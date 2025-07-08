#%%

import pandas as pd
from datetime import datetime
from utils.helpers import remove_keys_from_option_lists, extract_option_values, CALL_OPTION_KEYS, PUT_OPTION_KEYS, DEFAULT_CALL_OPTION_DICT, DEFAULT_PUT_OPTION_DICT
from utils.database import insert_in_database
from utils.logger import get_logger
logger = get_logger(__name__)


def process_option_chain_data(stock: str, oc_data: dict, snapshot_id: int) -> None:
    """
    Processes raw option chain data for a given stock and inserts the structured 
    call-put option matrix into the MySQL database.

    Args:
        stock (str): The stock symbol (e.g., 'RELIANCE').
        oc_data (dict): Option chain data with expiry dates as keys and nested 
                        'CE' and 'PE' lists representing call and put data.

    Raises:
        Exception: Logs detailed exception information if any part of the 
                   transformation or insertion fails.
    """
    final_df = pd.DataFrame()

    if not oc_data:
        logger.warning(f"[{stock}] No option chain data available to process.")
        return final_df

    for expiry_date, oc in oc_data.items():
        CE = list(oc.get('CE', []))
        PE = list(oc.get('PE', []))

        if len(CE) == 0 or len(PE) == 0:
            logger.warning(f"[{stock}] Missing CE or PE data for expiry {expiry_date}")
            continue

        if len(CE) != len(PE):
            logger.error(f"[{stock}] CE/PE length mismatch on {expiry_date}: CE={len(CE)}, PE={len(PE)}")
            continue

        keys_to_exclude = [
            'pchangeinOpenInterest', 'totalBuyQuantity', 'totalSellQuantity', 'identifier', 'pChange'
        ]

        try:
            CE, PE = remove_keys_from_option_lists(CE, PE, keys_to_exclude)

            l_OC = []
            for i in range(len(CE)):
                ce_data = CE[i] if CE[i] != '-' else DEFAULT_CALL_OPTION_DICT
                pe_data = PE[i] if PE[i] != '-' else DEFAULT_PUT_OPTION_DICT

                l_CE = extract_option_values(ce_data, CALL_OPTION_KEYS)
                l_PE = extract_option_values(pe_data, PUT_OPTION_KEYS)
                sp = [oc['strikePrice'][i]]

                l_OC.append(l_CE + sp + l_PE)

            OC_col = [
                'c_OI', 'c_CHNG_IN_OI', 'c_VOLUME', 'c_IV', 'c_LTP', 'c_CHNG',
                'c_BID_QTY', 'c_BID', 'c_ASK', 'c_ASK_QTY',
                'STRIKE',
                'p_BID_QTY', 'p_BID', 'p_ASK', 'p_ASK_QTY', 'p_CHNG',
                'p_LTP', 'p_IV', 'p_VOLUME', 'p_CHNG_IN_OI', 'p_OI'
            ]

            df = pd.DataFrame(l_OC, columns=OC_col)

            # Add stock column (Foreign Key)
            df.insert(0, 'TICKER', stock)

            # Add snapshot ID column
            df.insert(1, 'SNAPSHOT_ID', snapshot_id)

            # Add expiry date column
            df.insert(2, 'EXPIRY', expiry_date)
            df['EXPIRY'] = pd.to_datetime(df['EXPIRY'], format="%d-%b-%Y").dt.date

            final_df = pd.concat([final_df, df])

        except Exception as e:
            logger.exception(f"Exception while processing expiry {expiry_date} for stock {stock}: {e}")

    if final_df.empty:
        logger.warning(f"[{stock}] No valid option chain data found after processing.")

    return final_df

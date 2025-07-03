#%%

from utils.logger import get_logger
logger = get_logger(__name__)


def extract_option_chain_by_expiry(json_object: dict) -> dict:
    """
    Extracts and organizes option chain data by expiry dates from a JSON object.

    Args:
        json_object (dict): The raw JSON data containing 'records', 'data', and 'expiryDates'
                            as returned by the NSE option chain API.

    Returns:
        dict: A dictionary mapping each expiry date to a dictionary containing:
              - 'CE': List of Call option data
              - 'PE': List of Put option data
              - 'strikePrice': List of strike prices

    Example Output:
        {
            '2025-07-10': {
                'CE': [...], 
                'PE': [...], 
                'strikePrice': [15300, 15350, ...]
            },
            ...
        }

    Raises:
        Logs the exception and returns an empty dictionary if data extraction fails.
    """
    try:
        data = json_object['records']['data']
        expiry_dates = json_object['records']['expiryDates']
        oc_data = {}

        for ed in expiry_dates:
            oc_data[ed] = {'CE': [], 'PE': [], 'strikePrice': []}
            for item in data:
                if item.get('expiryDate') == ed:
                    oc_data[ed]['CE'].append(item.get('CE', '-'))
                    oc_data[ed]['PE'].append(item.get('PE', '-'))
                    oc_data[ed]['strikePrice'].append(item.get('strikePrice', 0))
        return oc_data

    except KeyError as e:
        logger.exception(f"Missing expected key in JSON while extracting option chain: {e}")
    except TypeError as e:
        logger.exception(f"Invalid JSON structure (TypeError) in input: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while extracting option chain data: {e}")
    
    return {}

def remove_keys_from_option_lists(CE, PE, keys_to_exclude=None):
    """
    Remove specified keys from dictionaries in CE and PE option lists.

    Args:
        CE (list): List of Call Option dictionaries (or '-' placeholders).
        PE (list): List of Put Option dictionaries (or '-' placeholders).
        keys_to_exclude (list, optional): List of keys to remove from each dictionary.
                                          Defaults to common option chain keys.
    Returns:
        tuple: The modified CE and PE lists, with specified keys removed from each dictionary.
    """

    if keys_to_exclude is None:
        keys_to_exclude = [
            'pchangeinOpenInterest', 'totalBuyQuantity', 'totalSellQuantity',
            'identifier', 'pChange'
        ]

    # Process CE list
    for i in range(len(CE)):
        if CE[i] != '-':
            if not isinstance(CE[i], dict):
                logger.error(f"Item at index {i} in CE is not a dict: {CE[i]}")
                continue
            for key in keys_to_exclude:
                try:
                    CE[i].pop(key, None)
                except Exception as e:
                    logger.error(f"Error removing key '{key}' from item at index {i} in CE: {e}")

    # Process PE list
    for i in range(len(PE)):
        if PE[i] != '-':
            if not isinstance(PE[i], dict):
                logger.error(f"Item at index {i} in PE is not a dict: {PE[i]}")
                continue
            for key in keys_to_exclude:
                try:
                    PE[i].pop(key, None)
                except Exception as e:
                    logger.error(f"Error removing key '{key}' from item at index {i} in PE: {e}")

    return CE, PE


CALL_OPTION_KEYS = [
    'openInterest', 'changeinOpenInterest', 'totalTradedVolume',
    'impliedVolatility', 'lastPrice', 'change',
    'bidQty', 'bidprice', 'askPrice', 'askQty'
]

PUT_OPTION_KEYS = [
    'bidQty', 'bidprice', 'askPrice',
    'askQty', 'change', 'lastPrice', 'impliedVolatility',
    'totalTradedVolume', 'changeinOpenInterest', 'openInterest'
]

DEFAULT_CALL_OPTION_DICT = {key: 0 for key in CALL_OPTION_KEYS}
DEFAULT_PUT_OPTION_DICT = {key: 0 for key in PUT_OPTION_KEYS}

def extract_option_values(option_data, option_keys):
    return [round(float(option_data.get(key, 0)), 2) for key in option_keys]



def compare_stock_dataframes(old_data: dict, new_data: dict) -> bool:
    """
    Compare old and new stock DataFrames.
    Returns True if there is any difference in any stock's data.
    Otherwise returns False if all match.
    """
    try:
        for stock, new_df in new_data.items():
            old_df = old_data.get(stock)
            if old_df is None:
                logger.info(f"{stock} not found in previous data — marked as changed.")
                return True  # new stock appeared

            if not new_df.equals(old_df):
                logger.info(f"Detected change in data for {stock}")
                return True  # data changed

        logger.info("No changes detected in any stock data.")
        return False  # all matched
    except Exception as e:
        logger.exception("Error comparing DataFrames")
        return True  # be safe and assume changes if comparison fails

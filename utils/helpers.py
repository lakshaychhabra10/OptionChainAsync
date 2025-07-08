#%%
from datetime import datetime
from utils.logger import get_logger
import os
import json
import pandas as pd


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
                CE[i].pop(key, None)

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



def extract_download_datetime_underlying(json_object):
    """
    Extracts download_date, download_time, and underlying from the JSON object's 'records' field.
    If the timestamp is missing or invalid, returns (None, None, None).

    Args:
        json_object (dict): The JSON object containing the timestamp and underlying.
        logger (logging.Logger, optional): Logger for error/warning messages.

    Returns:
        tuple: (download_date, download_time, underlying) as strings,
               or (None, None, None) if not available or invalid.
    """
    records = json_object.get('records', {})
    timestamp_str = records.get('timestamp', '')
    underlying = records.get('underlyingValue', None)

    if timestamp_str:

        timestamp = datetime.strptime(timestamp_str, "%d-%b-%Y %H:%M:%S")
        download_date = timestamp.date().strftime("%Y-%m-%d")
        download_time = timestamp.time().strftime("%H:%M:%S")
        return download_date, download_time, underlying

    else:
        logger.warning("No timestamp found for stock.")
        return None, None, underlying


def save_option_chain_snapshot(parent_dir, download_date, download_time, snapshot_id, stock, json_object):
    """
    Creates a directory structure: parent_dir/download_date/snapshot_id,
    and saves the JSON object as {stock}_{snapshot_id}_{download_date}{download_time}_istock_oc.json

    Args:
        parent_dir (str): The root directory for storing data.
        download_date (str): The date string (e.g., '20250704').
        download_time (str): The time string (e.g., '153600' for 15:36:00).
        snapshot_id (str or int): Unique identifier for the snapshot.
        stock (str): Stock name or symbol.
        json_object (dict): The JSON data to save.
    """
    # Build directory structure
    date_dir = os.path.join(parent_dir, download_date)
    snapshot_dir = os.path.join(date_dir, str(snapshot_id))
    os.makedirs(snapshot_dir, exist_ok=True)

    # Construct filename
    json_filename = f"{stock}_{snapshot_id}_{download_date}_{download_time}.json"
    json_path = os.path.join(snapshot_dir, json_filename)

    with open(json_path, 'w') as f:
        json.dump(json_object, f)
    logger.info(f"Saved raw JSON for {stock} at {json_path}")



def create_snapshot_df(snapshot_id, stock, download_date, download_time, underlying_val):
    """
    Creates a snapshot DataFrame for the option chain snapshot if final_df is not empty.
    Logs the result using the global logger.

    Args:
        final_df (pd.DataFrame): The processed option chain DataFrame.
        snapshot_id (str or int): The snapshot identifier.
        stock (str): The stock ticker.
        download_date (str): The download date.
        download_time (str): The download time.

    Returns:
        pd.DataFrame or None: The snapshot DataFrame if final_df is not empty, else None.
    """

    snapshot_df = pd.DataFrame([{
        'SNAPSHOT_ID': snapshot_id,
        'TICKER': stock,
        'DOWNLOAD_DATE': download_date,
        'DOWNLOAD_TIME': download_time,
        'UNDERLYING_VALUE' : underlying_val
    }])
    return snapshot_df
    




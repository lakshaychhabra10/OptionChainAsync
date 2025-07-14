#%%
from datetime import datetime
from utils.logger import get_logger
import os
import json
import pandas as pd
from google.cloud import storage
import os
from io import BytesIO
import aiofiles

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

async def save_option_chain_snapshot_local(temp_dir, download_date, download_time, snapshot_id, stock, json_object):
    """
    Asynchronously saves the JSON object to a local temporary directory.
    """
    date_dir = os.path.join(temp_dir, download_date, str(snapshot_id))
    os.makedirs(date_dir, exist_ok=True)

    json_filename = f"{stock}_{snapshot_id}_{download_date}_{download_time}.json"
    json_path = os.path.join(date_dir, json_filename)

    async with aiofiles.open(json_path, mode='w') as f:
        await f.write(json.dumps(json_object))

import os
from google.cloud import storage
from concurrent.futures import ThreadPoolExecutor, as_completed

def batch_upload_to_gcs(bucket_name, local_base_dir, max_workers=8):
    """
    Recursively uploads all files in local_base_dir to GCS bucket, preserving folder structure, using multi-threading.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Gather all files to upload
    files_to_upload = []
    for root, _, files in os.walk(local_base_dir):
        for file in files:
            local_path = os.path.join(root, file)
            rel_path = os.path.relpath(local_path, local_base_dir)
            files_to_upload.append((local_path, rel_path))

    def upload_file(local_path, rel_path):
        blob = bucket.blob(rel_path)
        blob.upload_from_filename(local_path, content_type='application/json')
        return rel_path

    # Use ThreadPoolExecutor for parallel uploads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(upload_file, local_path, rel_path)
            for local_path, rel_path in files_to_upload
        ]
        for future in as_completed(futures):
            try:
                uploaded = future.result()
                # Optional: log or print uploaded file path
                # print(f"Uploaded: {uploaded}")
            except Exception as e:
                logger.error(f"Upload to google cloud storage failed: {e}")


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
    




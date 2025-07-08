#%%


import requests
import json
import pandas as pd
from utils.database import insert_in_database
from utils.helpers import extract_option_chain_by_expiry, extract_download_datetime_underlying, save_option_chain_snapshot, create_snapshot_df
from utils.parser import process_option_chain_data
import time
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9"
}

stock = "RELIANCE"
url = f"https://www.nseindia.com/api/option-chain-equities?symbol={stock}"

# --- Create a session to persist cookies ---
session = requests.Session()
session.headers.update(headers)

# --- Step 1: Hit the main page to get cookies ---
main_page = session.get("https://www.nseindia.com")
if main_page.status_code == 200:
    print("Main page accessed successfully. Cookies set.")
else:
    print(f"Failed to access main page. Status code: {main_page.status_code}")
    exit(1)

# --- Step 2: Hit the option chain URL ---
response = session.get("https://www.nseindia.com/option-chain")
if response.status_code == 200:
    print("Option chain page accessed successfully.")
else:
    print(f"Failed to access option chain page. Status code: {response.status_code}")
    exit(1)

# --- Step 3: Fetch the option chain data ---
response = session.get(url)
if response.status_code == 200:
    data = response.json()
    print("Option chain data fetched successfully.")
    # Process the data as needed
    print(data)  # For demonstration, printing the fetched data
    with open(f"{stock}_option_chain.json", "w") as f:
        json.dump(data, f, indent=4)
else:
    print(f"Failed to fetch option chain data. Status code: {response.status_code}")
    exit(1)

# --- Step 4: Close the session ---
session.close()
print("Session closed.")

snapshot_id = 1  # Example snapshot ID, you can modify this as needed

download_date, download_time, underlying_val = extract_download_datetime_underlying(data)

save_option_chain_snapshot(
    parent_dir="option_chain_snapshots",
    download_date=download_date,
    download_time=download_time,
    snapshot_id=1,
    stock=stock,
    json_object=data
)

oc_data = extract_option_chain_by_expiry(data)
reliance_data = process_option_chain_data(stock, oc_data,snapshot_id)
insert_in_database(reliance_data, 'optionchain')

snapshot_df = create_snapshot_df(snapshot_id, stock, download_date, download_time, underlying_val)

insert_in_database(snapshot_df, 'optionchain_snapshots')

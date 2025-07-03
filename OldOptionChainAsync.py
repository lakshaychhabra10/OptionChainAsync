import asyncio
import aiohttp
import json
import random
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import time
import contextlib

# ----------------- Existing Functions (Synchronous) -----------------

def get_oc_data(json_object):
    data = json_object['records']['data']
    e_date = json_object['records']['expiryDates']
    oc_data = {}
    for ed in e_date:
        oc_data[ed] = {'CE':[], 'PE':[]}
        for di in range(len(data)):
            if data[di]['expiryDate'] == ed:
                if 'CE' in data[di].keys() and data[di]['CE']['expiryDate'] == ed:
                    oc_data[ed]['CE'].append(data[di]['CE'])
                else:
                    oc_data[ed]['CE'].append('-')
                if 'PE' in data[di].keys() and data[di]['PE']['expiryDate'] == ed:
                    oc_data[ed]['PE'].append(data[di]['PE'])
                else:
                    oc_data[ed]['PE'].append('-')
    return oc_data

def set_decimal(x):
    return round(float(x), 2)

def create_mysql_engine(username, password, host, port, database_name):
    connection_string = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database_name}"
    return create_engine(connection_string)

def insert_in_database(data, table_name):
    engine = create_mysql_engine(
        username="root",
        password="vL7#pD9r!xF2@tWz",  # Use your actual credentials
        host="localhost",
        port=3306,
        database_name="optionchaindata"
    )
    try:
        # Use context manager to ensure connection is closed
        with engine.connect() as connection:
            data.to_sql(table_name, con=connection, if_exists='append', index=False)
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")
    finally:
        # Explicitly dispose of the engine to close all connections
        engine.dispose()
        print("Database connection closed")

def get_strike_price(CE, PE, index):
    try:
        ce_strike = CE[index]['strikePrice']
        if ce_strike:
            return ce_strike
    except (IndexError, KeyError, TypeError):
        pass
    try:
        pe_strike = PE[index]['strikePrice']
        if pe_strike:
            return pe_strike
    except (IndexError, KeyError, TypeError):
        pass
    return 0

def OC_matrix(stock, oc_data, json_object, runtime_integer):
    final_df = pd.DataFrame()
    try:
        for expiry_date in oc_data.keys():
            oc_data_dt = oc_data[expiry_date]
            # Create CE and PE matrices
            CE = list(oc_data_dt['CE'])
            PE = list(oc_data_dt['PE'])
            # Remove unwanted keys
            keys_to_exclude = [
                'pchangeinOpenInterest',
                'totalBuyQuantity',
                'totalSellQuantity',
                'identifier',
                'pChange'
            ]
            for i in range(len(CE)):
                if CE[i] != '-':
                    for key in keys_to_exclude:
                        if key in CE[i]:
                            del CE[i][key]
            for i in range(len(PE)):
                if PE[i] != '-':
                    for key in keys_to_exclude:
                        if key in PE[i]:
                            del PE[i][key]
            l_OC = []
            for i in range(len(CE)):
                if CE[i] != '-':
                    l_CE = [
                        int(CE[i]['openInterest']),
                        int(CE[i]['changeinOpenInterest']),
                        int(CE[i]['totalTradedVolume']),
                        set_decimal(CE[i]['impliedVolatility']),
                        set_decimal(CE[i]['lastPrice']),
                        set_decimal(CE[i]['change']),
                        int(CE[i]['bidQty']),
                        set_decimal(CE[i]['bidprice']),
                        set_decimal(CE[i]['askPrice']),
                        int(CE[i]['askQty']),
                    ]
                else:
                    l_CE = [0]*10
                sp = get_strike_price(CE, PE, i)
                if PE[i] != '-':
                    l_PE = [
                        sp,
                        int(PE[i]['bidQty']),
                        set_decimal(PE[i]['bidprice']),
                        set_decimal(PE[i]['askPrice']),
                        int(PE[i]['askQty']),
                        set_decimal(PE[i]['change']),
                        set_decimal(PE[i]['lastPrice']),
                        set_decimal(PE[i]['impliedVolatility']),
                        int(PE[i]['totalTradedVolume']),
                        int(PE[i]['changeinOpenInterest']),
                        int(PE[i]['openInterest'])
                    ]
                else:
                    l_PE = [sp] + [0]*10
                l_OC_t = l_CE + l_PE
                l_OC.append(l_OC_t)
            OC_col = ['c_OI', 'c_CHNG_IN_OI', 'c_VOLUME', 'c_IV', 'c_LTP', 'c_CHNG', 'c_BID_QTY', 'c_BID', 'c_ASK', 'c_ASK_QTY',
                      'STRIKE', 'p_BID_QTY', 'p_BID', 'p_ASK', 'p_ASK_QTY', 'p_CHNG', 'p_LTP', 'p_IV', 'p_VOLUME', 'p_CHNG_IN_OI', 'p_OI']
            df = pd.DataFrame(l_OC, columns=OC_col)
            # Correct date format for SQL
            download_date = json_object['records']['timestamp'].split()[0]
            date_object = datetime.strptime(download_date, "%d-%b-%Y")
            formatted_date = date_object.strftime("%Y-%m-%d")
            download_time = json_object['records']['timestamp'].split()[1]
            underlying_val = json_object['records']["underlyingValue"]
            df.insert(0, 'SYMBOL', stock)
            df.insert(1, 'EXPIRY_DATE', expiry_date)
            df.insert(2, 'DOWNLOAD_DATE', formatted_date)
            df.insert(3, 'DOWNLOAD_TIME', download_time)
            df.insert(4, 'UNDERLYING_VALUE', underlying_val)
            df.insert(5, 'RUNTIME_INTEGER', runtime_integer)  # Insert the runtime integer

            # Insert data into the database
            print(f"Processed data for {stock} on expiry {expiry_date}")
            final_df = pd.concat([final_df, df])

        # Only insert if we have data
        if not final_df.empty:
            insert_in_database(final_df, 'oc_data')

    except Exception as e:
        print(f"An error occurred in OC_matrix: {e}")

# ----------------- Asynchronous Fetching -----------------

async def fetch_stock(stock, proxy):
    """
    Asynchronously fetch option chain data for a given stock using the provided proxy.
    The function first visits the main page and option chain page to establish cookies.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9"
    }
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={stock}"
    try:
        # Use a timeout for all requests to prevent hanging
        timeout = aiohttp.ClientTimeout(total=30)
        
        # Create a session per request with proper timeout and connection cleanup
        async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(ssl=False)) as session:
            # First hit the main page to get cookies
            async with session.get("https://www.nseindia.com", headers=headers, proxy=proxy) as response:
                await response.text()  # Ensure response is read and connection is properly closed
            
            # Then hit the option chain page
            async with session.get("https://www.nseindia.com/option-chain", headers=headers, proxy=proxy) as response:
                await response.text()  # Ensure response is read and connection is properly closed
            
            # Now request the API endpoint
            async with session.get(url, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    json_object = await response.json()
                    print(f"Fetched data for {stock} using proxy {proxy}")
                    return stock, json_object
                else:
                    print(f"Error {response.status} for {stock} using proxy {proxy}")
                    return stock, None
    except asyncio.TimeoutError:
        print(f"Timeout for {stock} using proxy {proxy}")
        return stock, None
    except aiohttp.ClientError as e:
        print(f"Client error for {stock} using proxy {proxy}: {e}")
        return stock, None
    except Exception as e:
        print(f"Exception for {stock} using proxy {proxy}: {e}")
        return stock, None

async def process_batch(batch, proxies):
    """
    Process a batch of stocks concurrently.
    Each stock in the batch is assigned a proxy from the provided list (rotated by index).
    """
    tasks = []
    for idx, stock in enumerate(batch):
        # Assign proxies in order; if batch size <= number of proxies, each gets a unique proxy.
        proxy = proxies[idx % len(proxies)]
        tasks.append(fetch_stock(stock, proxy))
    results = await asyncio.gather(*tasks)
    return results

async def main():
    runtime_integer = 1  # Start counting from 1

    try:
        while True:
            # List of stocks (replace these placeholders with your actual stock symbols)
            stocks = [
                "ABCAPITAL",  # Aditya Birla Capital
                "ACC",        # ACC
                "ADANIGREEN", # Adani Energy
                "HDFCBANK",   # HDFC Bank
                "RELIANCE",   # Reliance Industries
                "INFY",       # Infosys
                "TATAMOTORS", # Tata Motors
                "SBIN",       # State Bank of India
                "ICICIBANK",  # ICICI Bank
                "LT"          # Larsen & Toubro
            ]
            
            # List of your proxy URLs (replace with actual proxy URLs)
            proxies = [
                "http://171.237.93.79:1027",
                "http://aeizewrd:c7r90z945p6n@86.38.234.176:6630", 
                "http://aeizewrd:c7r90z945p6n@161.123.152.115:6360",
                "http://aeizewrd:c7r90z945p6n@185.199.229.156:7492",
                "http://aeizewrd:c7r90z945p6n@185.199.228.220:7300"
            ]

            all_results = []
            batch_size = 5  # Process 5 stocks per batch
            
            # Loop through stocks in batches, waiting 5 seconds between each batch
            for i in range(0, len(stocks), batch_size):
                batch = stocks[i:i + batch_size]
                print(f"Processing batch {i // batch_size + 1} with stocks: {batch}")
                
                # Process with proper error handling
                try:
                    results = await process_batch(batch, proxies)
                    all_results.extend(results)
                except Exception as e:
                    print(f"Error processing batch: {e}")
                
                # Wait between batches
                await asyncio.sleep(5)
            
            # Process fetched data: generate option chain matrices and insert into the database
            for stock, json_object in all_results:
                if json_object:
                    try:
                        oc_data = get_oc_data(json_object)
                        OC_matrix(stock, oc_data, json_object, runtime_integer)
                    except Exception as e:
                        print(f"Error processing data for {stock}: {e}")
                else:
                    print(f"No data for {stock}")

            print(f"Runtime: {runtime_integer}. Batch processing completed. Waiting for 200 seconds before restarting...")
            runtime_integer += 1  # Increment runtime counter
            await asyncio.sleep(200)  # Wait before restarting
    except KeyboardInterrupt:
        print("Process interrupted by user. Cleaning up...")
    except Exception as e:
        print(f"Unexpected error in main loop: {e}")
    finally:
        # Clean up any remaining resources
        # No explicit cleanup needed here as we're using context managers throughout
        print("Process terminated. All connections should be closed.")

if __name__ == "__main__":
    # Set up proper handling of asyncio tasks
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program terminated by user")
    except Exception as e:
        print(f"Fatal error: {e}")
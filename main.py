#%%

import sys
import asyncio
from config import STOCKS, PROXIES
from utils.fetcher import process_batch
from utils.helpers import extract_option_chain_by_expiry, extract_download_datetime, save_option_chain_snapshot, create_snapshot_df
from utils.parser import process_option_chain_data
from utils.database import insert_in_database, get_latest_snapshot_id
from utils.logger import get_logger
logger = get_logger(__name__)

async def main():
    """
    Periodically fetches, processes, and stores option chain data for multiple stocks in batches.

    - Iterates through STOCKS in batches, fetching option chain data asynchronously using process_batch.
    - Processes and inserts fetched data into the database.
    - Logs progress, errors, and warnings throughout the workflow.
    - Repeats the process after a configurable wait interval.

    This function runs indefinitely until externally interrupted.
    """
    
    logger.info("Starting main execution...")

    # Initialize snapshot ID
    try:
        last_snapshot_id = get_latest_snapshot_id()
        snapshot_id = last_snapshot_id + 1 if last_snapshot_id is not None else 1
        logger.info(f"Starting with snapshot ID {snapshot_id} (last was {last_snapshot_id})")
    except Exception as e:
        logger.error(f"Failed to determine next snapshot ID: {e}. Starting with snapshot_id=1")
        snapshot_id = 1

    
    while True:
        all_results = []
        batch_size = 1  # Adjust batch size as needed
        for i in range(0, len(STOCKS[0:3]), batch_size):
            batch = STOCKS[i:i+batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}: {batch}")
            results = await process_batch(batch, PROXIES)
            all_results.extend(results)
            await asyncio.sleep(2)

        for stock, json_object in all_results:
            if json_object:
                try:
                    download_date, download_time = extract_download_datetime(json_object)

                    save_option_chain_snapshot(
                        parent_dir="option_chain_snapshots",
                        download_date=download_date,
                        download_time=download_time,
                        snapshot_id=snapshot_id,
                        stock=stock,
                        json_object=json_object
                    )

                    oc_data = extract_option_chain_by_expiry(json_object)
                    
                    if oc_data:
                        stock_df = process_option_chain_data(stock, oc_data)
                    else:
                        logger.warning(f"No option chain data found for {stock}")
                        continue

                    if stock_df:
                        insert_in_database(stock_df, 'optionchain')
                        snapshot_df = create_snapshot_df(stock_df, snapshot_id, stock, download_date, download_time)
                        logger.info(f"Processed and inserted data for {stock} - snapshot ID {snapshot_id}")
                    else:
                        logger.warning(f"No valid data to insert for {stock}")

                    if snapshot_df:
                        insert_in_database(snapshot_df, 'optionchain_snapshots')

                except Exception as e:
                    logger.error(f"Error processing {stock}: {e}", exc_info=True)
            else:
                logger.warning(f"No data for {stock}")
        
        snapshot_id += 1
        wait_time = 150  # seconds
        logger.info(f"Sleeping for {wait_time} seconds...")
        await asyncio.sleep(wait_time)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("Unhandled exception in main execution")
        sys.exit(1)

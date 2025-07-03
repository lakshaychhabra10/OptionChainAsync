#%%

import sys
import asyncio
from config import STOCKS, PROXIES
from utils.fetcher import process_batch
from utils.helpers import extract_option_chain_by_expiry
from utils.parser import process_option_chain_data
from utils.database import insert_in_database
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
    while True:
        all_results = []
        batch_size = 1  # Adjust batch size as needed
        for i in range(0, len(STOCKS), batch_size):
            batch = STOCKS[i:i+batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}: {batch}")
            results = await process_batch(batch, PROXIES)
            all_results.extend(results)
            await asyncio.sleep(2)

        for stock, json_object in all_results:
            if json_object:
                try:
                    oc_data = extract_option_chain_by_expiry(json_object)
                    stock_df = process_option_chain_data(stock, oc_data)
                    print(stock_df)
                    insert_in_database(stock_df, 'optionchain')
                    logger.info(f"Processed and inserted data for {stock}")
                except Exception as e:
                    logger.error(f"Error processing {stock}: {e}", exc_info=True)
            else:
                logger.warning(f"No data for {stock}")
        
        wait_time = 150  # seconds
        logger.info(f"Sleeping for {wait_time} seconds...")
        await asyncio.sleep(wait_time)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("Unhandled exception in main execution")
        sys.exit(1)

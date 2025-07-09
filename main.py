import sys
import asyncio
from config import PROXY, SYMBOLS
from utils.fetcher import process_batch
from utils.helpers import (
    extract_option_chain_by_expiry,
    extract_download_datetime_underlying,
    save_option_chain_snapshot,
    create_snapshot_df
)
from utils.parser import process_option_chain_data
from utils.database import insert_in_database, get_latest_snapshot_id, engine, create_required_tables, get_previous_datetime
from utils.logger import get_logger
import time
from collections import defaultdict
import aiohttp

logger = get_logger(__name__)


async def process_result(stock, json_object, snapshot_id, symbol_type='equity'):
    status = "failed"  # default status
    error_message = None

    try:
        # Initial checks
        if not json_object:
            error_message = f"No data received for {stock}"
            raise Exception(error_message)

        # Extract download info
        download_date, download_time, underlying_val = await asyncio.to_thread(
            extract_download_datetime_underlying, json_object
        )

        # Check if snapshot exists
        last_date, last_time = await asyncio.to_thread(
            get_previous_datetime, stock
        )
        if download_date == last_date and download_time == last_time:
            status = "skipped"
            return stock, status, None

        # Save option chain snapshot
        await asyncio.to_thread(
            save_option_chain_snapshot,
            parent_dir="option_chain_snapshots",
            download_date=download_date,
            download_time=download_time,
            snapshot_id=snapshot_id,
            stock=stock,
            json_object=json_object
        )

        # Process option chain data
        oc_data = await asyncio.to_thread(extract_option_chain_by_expiry, json_object)
        stock_df = await asyncio.to_thread(process_option_chain_data, stock, oc_data, snapshot_id)

        if stock_df.empty:
            error_message = (f"No valid data to insert for {stock} ({symbol_type})")
            raise Exception(error_message)
        # Database operations
        await asyncio.to_thread(insert_in_database, stock_df, 'optionchain')
        
        snapshot_df = await asyncio.to_thread(
            create_snapshot_df,
            snapshot_id,
            stock,
            download_date,
            download_time,
            underlying_val
        )
        
        if not snapshot_df.empty:
            await asyncio.to_thread(insert_in_database, snapshot_df, 'optionchain_snapshots')
        else:
            raise Exception("Empty snapshot DataFrame")

        status = "success"
        return stock, status, None

    except Exception as e:
        error_message = f"Error processing {stock} ({symbol_type}): {str(e)}"
        return stock, status, error_message
    
async def main():
    logger.info("Starting main execution...")

    # Crash early if tables can't be created
    create_required_tables()

    # Crash early if DB is unreachable
    last_snapshot_id = get_latest_snapshot_id()
    snapshot_id = last_snapshot_id + 1 if last_snapshot_id is not None else 1
    logger.info(f"Starting with snapshot ID {snapshot_id} (last was {last_snapshot_id})")

    # Main loop
    while True:

        try:

            # Fetch data
            fetch_start_time = time.monotonic()  # Start timer for this cycle
            
            # Initialize status tracking
            status_counts = defaultdict(int)
            stock_status = defaultdict(list)
            process_failure_messages = defaultdict(list)  # New dict to store failure messages
            
            try:
                results = await process_batch(SYMBOLS, PROXY)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"Network error fetching symbols: {e}")
                results = []
            except Exception as e:
                logger.exception(f"Unexpected fetch error: {e}")
                raise  # Re-raise critical errors
            
            # Filter only successful fetches
            successful_results = []
            fetch_failed_stocks = []
            fetch_failure_messages = defaultdict(list)

            for (symbol, json_object, symbol_type) in results:
                if json_object is not None:
                    successful_results.append((symbol, json_object, symbol_type))
                else:
                    fetch_failed_stocks.append(symbol)

            fetch_end_time = time.monotonic()

            # Log failed fetches
            if fetch_failed_stocks:
                status_counts["fetch_failed"] = len(fetch_failed_stocks)
                stock_status["fetch_failed"] = fetch_failed_stocks
                for stock in fetch_failed_stocks:
                    fetch_failure_messages[stock].append("Fetch failed: Could not retrieve data")

            # Process data
            process_results = await asyncio.gather(
                *(process_result(stock, json_object, snapshot_id, symbol_type) for stock, json_object, symbol_type in successful_results)
            )

            # Update status tracking
            for result in process_results:
                if result is None:
                    continue  # In case process_result returns None for empty data
                stock, status, error_message = result
                status_counts[status] += 1
                stock_status[status].append(stock)
                if status == "failed" and error_message:
                    process_failure_messages[stock].append(error_message)
            
            # Enhanced logging with failure messages
            logger.info(f"{'='*50}")
            logger.info(f"PROCESSING SUMMARY FOR SNAPSHOT {snapshot_id}:")
            logger.info(f"TOTAL STOCKS: {len(SYMBOLS)} | TOTAL SUCCESS: {status_counts.get('success',0)} | TOTAL FAILED: {status_counts.get('failed',0) + status_counts.get('fetch_failed',0)} | TOTAL SKIPPED: {status_counts.get('skipped',0)}")
            logger.info(f"FETCH SUCCESS : {len(successful_results)} | FETCH FAILED: {status_counts.get('fetch_failed', 0)} | PROCESS FAILED: {status_counts.get('failed',0)}")
            
            # Fetch failure messages
            if fetch_failure_messages:
                logger.info("FETCH FAILURE DETAILS :")
                for stock, msg in fetch_failure_messages.items():
                    logger.error(f"• {stock}: {msg}")

            # Log skipped messages if any
            if status_counts.get('skipped'):
                logger.info(f"SKIPPED STOCKS: {', '.join(stock_status['skipped'])}")

            # Log process failure messages
            if process_failure_messages:
                logger.info("PROCESS FAILURE DETAILS:")
                for stock, messages in process_failure_messages.items():
                    for msg in messages:
                        logger.error(f"• {stock}: {msg}")

            process_end_time = time.monotonic()

            snapshot_id += 1

            fetch_time = fetch_end_time - fetch_start_time
            processing_time = process_end_time - fetch_end_time
            total_execution_time = fetch_time + processing_time

            wait_time = max(1, 60 - total_execution_time)  # Ensure minimum 1 second wait
            logger.info(f"TOTAL FETCH TIME : {fetch_time:.2f} SECONDS ,  TOTAL PROCESS TIME : {processing_time:.2f} SECONDS , TOTAL TIME : {fetch_time + processing_time:.2f} SECONDS")
            logger.info(f"SLEEPING FOR {wait_time:.2f} SECONDS")
            logger.info(f"{'='*50}")

            await asyncio.sleep(wait_time)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt. Shutting down gracefully...")
            break
        except Exception as e:
            logger.exception(f"Unexpected error in main loop: {e}")
            # Wait before retrying to prevent tight error loops
            await asyncio.sleep(60)
        
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
        sys.exit(0)

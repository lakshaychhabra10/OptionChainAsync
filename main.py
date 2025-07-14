
import sys
import asyncio
from config import PROXY, SYMBOLS
from utils.fetcher import process_batch
from utils.helpers import (
    extract_option_chain_by_expiry,
    extract_download_datetime_underlying,
    batch_upload_to_gcs,
    create_snapshot_df,
    save_option_chain_snapshot_local
)
from utils.parser import process_option_chain_data
from utils.database import insert_in_database, get_latest_snapshot_id, engine, create_required_tables, get_previous_datetime
from utils.logger import get_logger
import time
from collections import defaultdict
import shutil
import pandas as pd

logger = get_logger(__name__)


async def process_result(stock, json_object, snapshot_id, symbol_type='equity'):
    status = "failed"
    error_message = None

    try:
        if not json_object:
            error_message = f"No data received for {stock}"
            raise Exception(error_message)

        download_date, download_time, underlying_val = await asyncio.to_thread(
            extract_download_datetime_underlying, json_object
        )

        last_date, last_time = await asyncio.to_thread(
            get_previous_datetime, stock
        )
        if download_date == last_date and download_time == last_time:
            return stock, "skipped", None, None, None

        await save_option_chain_snapshot_local(
            temp_dir="temp_snapshots",
            download_date=download_date,
            download_time=download_time,
            snapshot_id=snapshot_id,
            stock=stock,
            json_object=json_object
        )

        oc_data = await asyncio.to_thread(extract_option_chain_by_expiry, json_object)
        stock_df = await asyncio.to_thread(process_option_chain_data, stock, oc_data, snapshot_id)

        if stock_df.empty:
            raise Exception(f"No valid data to insert for {stock} ({symbol_type})")

        snapshot_df = await asyncio.to_thread(
            create_snapshot_df,
            snapshot_id,
            stock,
            download_date,
            download_time,
            underlying_val
        )

        if snapshot_df.empty:
            raise Exception("Empty snapshot DataFrame")

        return stock, "success", None, stock_df, snapshot_df

    except Exception as e:
        return stock, status, f"Error processing {stock} ({symbol_type}): {str(e)}", None, None


async def main():
    logger.info("Starting main execution...")
    create_required_tables()
    last_snapshot_id = get_latest_snapshot_id()
    snapshot_id = last_snapshot_id + 1 if last_snapshot_id is not None else 1
    logger.info(f"Starting with snapshot ID {snapshot_id} (last was {last_snapshot_id})")

    while True:
        try:
            fetch_start_time = time.monotonic()
            status_counts = defaultdict(int)
            stock_status = defaultdict(list)
            process_failure_messages = defaultdict(list)
            all_stock_dfs = []
            all_snapshot_dfs = []

            try:
                results = await process_batch(SYMBOLS, PROXY)
            except asyncio.TimeoutError as e:
                logger.error(f"Network error fetching symbols: {e}")
                results = []
            except Exception as e:
                logger.exception(f"Unexpected fetch error: {e}")
                raise

            successful_results = []
            fetch_failed_stocks = []
            fetch_failure_messages = defaultdict(list)

            for (symbol, json_object, symbol_type) in results:
                if json_object is not None:
                    successful_results.append((symbol, json_object, symbol_type))
                else:
                    fetch_failed_stocks.append(symbol)

            fetch_end_time = time.monotonic()

            if fetch_failed_stocks:
                status_counts["fetch_failed"] = len(fetch_failed_stocks)
                stock_status["fetch_failed"] = fetch_failed_stocks
                for stock in fetch_failed_stocks:
                    fetch_failure_messages[stock].append("Fetch failed: Could not retrieve data")

            process_results = await asyncio.gather(
                *(process_result(stock, json_object, snapshot_id, symbol_type) for stock, json_object, symbol_type in successful_results)
            )

            for result in process_results:
                if result is None:
                    continue
                stock, status, error_message, stock_df, snapshot_df = result
                status_counts[status] += 1
                stock_status[status].append(stock)
                if status == "failed" and error_message:
                    process_failure_messages[stock].append(error_message)
                if stock_df is not None:
                    all_stock_dfs.append(stock_df)
                if snapshot_df is not None:
                    all_snapshot_dfs.append(snapshot_df)

            if all_stock_dfs:
                stock_df_combined = pd.concat(all_stock_dfs, ignore_index=True)
                await asyncio.to_thread(insert_in_database, stock_df_combined, 'optionchain')

            if all_snapshot_dfs:
                snapshot_df_combined = pd.concat(all_snapshot_dfs, ignore_index=True)
                await asyncio.to_thread(insert_in_database, snapshot_df_combined, 'optionchain_snapshots')

            await asyncio.to_thread(batch_upload_to_gcs, "my-option-chain-data", "temp_snapshots")
            shutil.rmtree("temp_snapshots", ignore_errors=True)

            logger.info(f"{'='*50}")
            logger.info(f"PROCESSING SUMMARY FOR SNAPSHOT {snapshot_id}:")
            logger.info(f"TOTAL STOCKS: {len(SYMBOLS)} | TOTAL SUCCESS: {status_counts.get('success',0)} | TOTAL FAILED: {status_counts.get('failed',0) + status_counts.get('fetch_failed',0)} | TOTAL SKIPPED: {status_counts.get('skipped',0)}")
            logger.info(f"FETCH SUCCESS : {len(successful_results)} | FETCH FAILED: {status_counts.get('fetch_failed', 0)} | PROCESS FAILED: {status_counts.get('failed',0)}")

            if fetch_failure_messages:
                logger.info("FETCH FAILURE DETAILS :")
                for stock, msg in fetch_failure_messages.items():
                    logger.error(f"• {stock}: {msg}")

            if status_counts.get('skipped'):
                logger.info(f"SKIPPED STOCKS: {', '.join(stock_status['skipped'])}")

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
            wait_time = max(1, 60 - total_execution_time)

            logger.info(f"TOTAL FETCH TIME : {fetch_time:.2f} SECONDS ,  TOTAL PROCESS TIME : {processing_time:.2f} SECONDS , TOTAL TIME : {fetch_time + processing_time:.2f} SECONDS")
            logger.info(f"SLEEPING FOR {wait_time:.2f} SECONDS")
            logger.info(f"{'='*50}")

            await asyncio.sleep(wait_time)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt. Shutting down gracefully...")
            break
        except Exception as e:
            logger.exception(f"Unexpected error in main loop: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
        sys.exit(0)

import sys
import asyncio
from config import STOCKS, PROXY
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

logger = get_logger(__name__)

async def process_result(stock, json_object, snapshot_id):
    if not json_object:
        logger.warning(f"No data for {stock}")
        return

    try:
        download_date, download_time, underlying_val = await asyncio.to_thread(
            extract_download_datetime_underlying, json_object
        )

        # 🆕 Get previous download timestamp for this stock
        last_date, last_time = await asyncio.to_thread(
            get_previous_datetime, stock
        )

        if download_date == last_date and download_time == last_time:
            logger.info(f"Skipping {stock}: same download timestamp ({download_date} {download_time}) as last run")
            return

        await asyncio.to_thread(
            save_option_chain_snapshot,
            parent_dir="option_chain_snapshots",
            download_date=download_date,
            download_time=download_time,
            snapshot_id=snapshot_id,
            stock=stock,
            json_object=json_object
        )

        oc_data = await asyncio.to_thread(extract_option_chain_by_expiry, json_object)

        if not oc_data:
            logger.warning(f"No option chain data found for {stock}")
            return

        stock_df = await asyncio.to_thread(process_option_chain_data, stock, oc_data, snapshot_id)

        if not stock_df.empty:
            await asyncio.to_thread(insert_in_database, stock_df, 'optionchain')
            snapshot_df = await asyncio.to_thread(
                create_snapshot_df,
                snapshot_id,
                stock,
                download_date,
                download_time,
                underlying_val
            )

        else:
            logger.warning(f"No valid data to insert for {stock}")
            return

        if not snapshot_df.empty:
            await asyncio.to_thread(insert_in_database, snapshot_df, 'optionchain_snapshots')
        else:
            logger.warning(f"No valid snapshot data to insert for {stock}")

    except Exception as e:
        logger.error(f"Error processing {stock}: {e}", exc_info=True)


async def main():
    logger.info("Starting main execution...")

    create_required_tables()

    try:
        last_snapshot_id = get_latest_snapshot_id()
        snapshot_id = last_snapshot_id + 1 if last_snapshot_id is not None else 1
        logger.info(f"Starting with snapshot ID {snapshot_id} (last was {last_snapshot_id})")
    except Exception as e:
        logger.error(f"Failed to determine next snapshot ID: {e}. Starting with snapshot_id=1")
        snapshot_id = 1

    while True:
        all_results = []
        batch_size = 224

        for i in range(0, len(STOCKS), batch_size):
            batch = STOCKS[i:i+batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}: len : {len(batch)} :{batch}")
            try:
                results = await process_batch(batch, PROXY)
            except Exception as e:
                logger.error(
                    f"Exception occurred while processing batch {i // batch_size + 1} ({batch}): {e}",
                    exc_info=True
                )
                results = []
            all_results.extend(results)
            await asyncio.sleep(2)

        await asyncio.gather(*(process_result(stock, json_object, snapshot_id) for stock, json_object in all_results))

        snapshot_id += 1
        wait_time = 15
        logger.info(f"Sleeping for {wait_time} seconds...")
        await asyncio.sleep(wait_time)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("Unhandled exception in main execution")
        sys.exit(1)
    finally:
        engine.dispose()
        logger.info("Database engine disposed cleanly on exit.")

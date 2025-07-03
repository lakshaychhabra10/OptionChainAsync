#%%

import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)

async def fetch_stock(stock, proxy):
    """
    Asynchronously fetch option chain data for a stock from NSE using a proxy.

    Args:
        stock (str): Stock symbol.
        proxy (str): HTTP proxy URL.

    Returns:
        tuple: (stock, data_dict or None)
    """
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9"
    }
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={stock}"

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(ssl=False)) as session:
            # Properly close connections for each request
            async with session.get("https://www.nseindia.com", headers=headers, proxy=proxy) as _:
                pass
            async with session.get("https://www.nseindia.com/option-chain", headers=headers, proxy=proxy) as _:
                pass
            async with session.get(url, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Fetched data for {stock}")
                    return stock, data
                else:
                    logger.warning(f"Bad response {response.status} for {stock}")
                    return stock, None
    except Exception as e:
        logger.exception(f"Fetch failed for {stock} with proxy {proxy}")
        return stock, None

async def process_batch(batch, proxies):
    """
    Asynchronously fetch option chain data for a batch of stocks using rotating proxies.

    Args:
        batch (list of str): Stock symbols.
        proxies (list of str): Proxy URLs.

    Returns:
        list of tuples: (stock, data_dict or None)
    """
    tasks = []
    for i, stock in enumerate(batch):
        proxy = proxies[i % len(proxies)]
        tasks.append(fetch_stock(stock, proxy))
    results = await asyncio.gather(*tasks)
    return results

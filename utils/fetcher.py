import aiohttp
import asyncio
from utils.logger import get_logger
import random

logger = get_logger(__name__)

HEADERS_LIST = [
    
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9"
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5"
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.7"
    }
    
]

def get_random_headers():
    return random.choice(HEADERS_LIST)

def allocate_proxies_to_stocks(stocks, proxies):
    """
    Assign proxies to stocks using a random round robin approach.
    Each run will produce a different mapping.
    Returns a list of (stock, proxy) tuples.
    """
    proxies_shuffled = proxies[:]  # Copy to avoid modifying original
    random.shuffle(proxies_shuffled)
    assignments = []
    for i, stock in enumerate(stocks):
        proxy = proxies_shuffled[i % len(proxies_shuffled)]
        assignments.append((stock, proxy))
    return assignments

async def fetch_stock(stock, proxy, headers):
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={stock}"
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get("https://www.nseindia.com", headers=headers, proxy=proxy) as _:
                pass
            await asyncio.sleep(random.uniform(1, 2))
            async with session.get("https://www.nseindia.com/option-chain", headers=headers, proxy=proxy) as _:
                pass
            await asyncio.sleep(random.uniform(1, 2))
            async with session.get(url, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Fetched data for {stock} via {proxy}")
                    return stock, data
                else:
                    logger.warning(f"Bad response {response.status} for {stock} via {proxy}")
                    return stock, None
    except Exception as e:
        logger.exception(f"Fetch failed for {stock} with proxy {proxy}")
        return stock, None

async def fetch_with_retries(stock, proxy, max_retries=3, backoff=2):
    """
    Try to fetch stock data with retry logic and rotating headers.
    """
    for attempt in range(1, max_retries + 1):
        await asyncio.sleep(random.uniform(1.5, 3.0)) # Stagger within the task
        headers = get_random_headers()  # New header every attempt
        logger.info(f"[{stock}] Attempt {attempt} with proxy {proxy} and headers: {headers['User-Agent']}")
        stock_data = await fetch_stock(stock, proxy, headers)

        if stock_data[1] is not None:
            return stock_data

        logger.warning(f"[{stock}] Retry {attempt} failed. Retrying in {backoff ** attempt:.1f} seconds...")
        await asyncio.sleep(backoff ** attempt)  # Exponential backoff

    logger.error(f"[{stock}] All {max_retries} retries failed using proxy {proxy}")
    return stock, None


async def process_batch(stocks, proxies):
    """
    Assign proxies to stocks in a random round robin way and fetch data.
    """
    assignments = allocate_proxies_to_stocks(stocks, proxies)
    tasks = []
    tasks = [asyncio.create_task(fetch_with_retries(stock, proxy)) for stock, proxy in assignments]
    results = await asyncio.gather(*tasks)
    return results

# Example usage:
if __name__ == "__main__":

    proxies = [
        "https://spdsnruo64:0Co0+qHdxIRrk8vrk2@in.decodo.com:10000"
    ]
    proxies *= 3
    stocks = ["RELIANCE", "TCS", "INFY"]  # Example batch
    asyncio.run(process_batch(stocks, proxies))

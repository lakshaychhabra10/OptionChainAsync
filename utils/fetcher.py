import aiohttp
import asyncio
import random
from urllib.parse import quote
from utils.logger import get_logger

logger = get_logger(__name__)

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
]

def get_random_headers():
    return random.choice(HEADERS_LIST).copy()

async def fetch_stock(stock, proxy, headers, session, symbol_type='equity'):
    await asyncio.sleep(random.uniform(0.5, 2))
    base_url = "https://www.nseindia.com"
    option_chain_url = "https://www.nseindia.com/option-chain"
    encoded_stock = quote(stock)
    api_url = (
        f"https://www.nseindia.com/api/option-chain-equities?symbol={encoded_stock}"
        if symbol_type == 'equity'
        else f"https://www.nseindia.com/api/option-chain-indices?symbol={encoded_stock}"
    )
    try:
        headers["Referer"] = "https://www.nseindia.com"
        async with session.get(base_url, headers=headers, proxy=proxy) as response:
            await asyncio.sleep(random.uniform(0.5, 2))
            if response.status != 200:
                logger.warning(f"Bad response {response.status} for {stock} (base_url) via {proxy}")
                return stock, None
        headers["Referer"] = base_url
        async with session.get(option_chain_url, headers=headers, proxy=proxy) as response:
            await asyncio.sleep(random.uniform(0.5, 2))
            if response.status != 200:
                logger.warning(f"Bad response {response.status} for {stock} (option_chain_url) via {proxy}")
                return stock, None
        headers["Referer"] = option_chain_url
        async with session.get(api_url, headers=headers, proxy=proxy) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"Fetched data for {stock} ({symbol_type}) via {proxy}")
                return stock, data
            else:
                logger.warning(f"Bad response {response.status} for {stock} ({symbol_type}) via {proxy}")
                return stock, None
    except Exception as e:
        logger.warning(f"Fetch failed for {stock} ({symbol_type}) with proxy {proxy}: {e}")
        return stock, None

async def fetch_with_retries(stock, proxy, session, max_retries=3, symbol_type='equity'):
    for attempt in range(max_retries):
        headers = get_random_headers()
        result = await fetch_stock(stock, proxy, headers, session, symbol_type)
        if result[1] is not None:
            return result
        logger.info(f"Retry {attempt + 1} for {stock} ({symbol_type}) via {proxy}")
        await asyncio.sleep(2 * (attempt + 1))
    return stock, None

async def process_batch(symbols_with_types, proxy):
    timeout = aiohttp.ClientTimeout(total=15)
    connector = aiohttp.TCPConnector(ssl=False, limit=250)
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        tasks = [
            fetch_with_retries(symbol, proxy, session, symbol_type=symbol_type)
            for symbol, symbol_type in symbols_with_types
        ]
        results = await asyncio.gather(*tasks)
        return [(symbol, json_object, symbol_type) for (symbol, json_object), (_, symbol_type) in zip(results, symbols_with_types)]
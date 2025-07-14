import asyncio
import random
import time
from urllib.parse import quote
from utils.logger import get_logger
from curl_cffi import requests as cureq

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


def sync_fetch_stock(stock, proxy, headers, symbol_type):
    time.sleep(random.uniform(0.5, 2))
    base_url = "https://www.nseindia.com"
    option_chain_url = "https://www.nseindia.com/option-chain"
    encoded_stock = quote(stock)
    api_url = (
        f"https://www.nseindia.com/api/option-chain-equities?symbol={encoded_stock}"
        if symbol_type == 'equity'
        else f"https://www.nseindia.com/api/option-chain-indices?symbol={encoded_stock}"
    )

    try:
        headers["Referer"] = base_url

        with cureq.Session(impersonate="chrome110") as session:
            session.get(base_url, headers=headers, proxies=proxy, timeout=15)
            time.sleep(random.uniform(0.5, 2))
            headers["Referer"] = base_url
            session.get(option_chain_url, headers=headers, proxies=proxy, timeout=15)
            time.sleep(random.uniform(0.5, 2))
            headers["Referer"] = option_chain_url
            response = session.get(api_url, headers=headers, proxies=proxy, timeout=15)

            if response.status_code == 200:
                return stock, response.json()
            else:
                logger.warning(f"Bad response {response.status_code} for {stock} ({symbol_type}) via {proxy}")
                return stock, None

    except Exception as e:
        logger.warning(f"Fetch failed for {stock} ({symbol_type}) with proxy {proxy}: {e}")
        return stock, None

async def fetch_stock(stock, proxy, headers, session, symbol_type='equity'):
    return await asyncio.to_thread(sync_fetch_stock, stock, proxy, headers, symbol_type)

async def fetch_with_retries(stock, assigned_proxy, proxies, session, max_retries=3, symbol_type='equity'):
    used_proxies = set()
    current_proxy = assigned_proxy

    for attempt in range(max_retries):
        headers = get_random_headers()
        result = await fetch_stock(stock, current_proxy, headers, session, symbol_type)
        if result[1] is not None:
            return result

        used_proxies.add(frozenset(current_proxy.items()))
        logger.info(f"Retry {attempt + 1} for {stock} ({symbol_type}) with new proxy")

        # Choose a new proxy not used before
        available_proxies = [p for p in proxies if frozenset(p.items()) not in used_proxies]
        if not available_proxies:
            logger.warning(f"No more unused proxies available for {stock} ({symbol_type})")
            break
        current_proxy = random.choice(available_proxies)
        await asyncio.sleep(2 * (attempt + 1))

    return stock, None

async def process_batch(symbols_with_types, proxies):
    session = None  # unused placeholder

    proxies = proxies.copy()  # Avoid modifying original
    random.shuffle(proxies)   # Shuffle proxies for randomness

    if len(proxies) < len(symbols_with_types):
        logger.warning("Not enough unique proxies for each stock. Proxies will be reused.")
    
    # Assign each stock a proxy (reusing if needed)
    assigned_proxies = [proxies[i % len(proxies)] for i in range(len(symbols_with_types))]

    tasks = [
        fetch_with_retries(symbol, assigned_proxy, proxies, session, symbol_type=symbol_type)
        for (symbol, symbol_type), assigned_proxy in zip(symbols_with_types, assigned_proxies)
    ]

    results = await asyncio.gather(*tasks)
    return [
        (symbol, json_object, symbol_type)
        for (symbol, json_object), (_, symbol_type) in zip(results, symbols_with_types)
    ]
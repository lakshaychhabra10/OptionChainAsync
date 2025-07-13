import aiohttp
import asyncio
import time
import random
import ssl
import traceback

PROXIES = [
    "http://iqoopiiq:x8z7nvi33uls@38.154.227.167:5868",
    "http://iqoopiiq:x8z7nvi33uls@92.113.242.158:6742",
    "http://iqoopiiq:x8z7nvi33uls@23.95.150.145:6114",
    "http://iqoopiiq:x8z7nvi33uls@198.23.239.134:6540",
    "http://iqoopiiq:x8z7nvi33uls@207.244.217.165:6712",
    "http://iqoopiiq:x8z7nvi33uls@107.172.163.27:6543",
    "http://iqoopiiq:x8z7nvi33uls@216.10.27.159:6837",
    "http://iqoopiiq:x8z7nvi33uls@136.0.207.84:6661",
    "http://iqoopiiq:x8z7nvi33uls@142.147.128.93:6593",
    "http://iqoopiiq:x8z7nvi33uls@206.41.172.74:6634"
]

# PROXIES *= 100  # Repeat the list to simulate a larger set of proxies

STOCK = "RELIANCE"
BASE_URL = "https://www.nseindia.com"
OPTION_CHAIN_PAGE = "https://www.nseindia.com/option-chain"
API_URL = f"https://www.nseindia.com/api/option-chain-equities?symbol={STOCK}"

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

async def check_proxy(proxy):
    start_time = time.time()
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            HEADERS = get_random_headers()
            await session.get(BASE_URL, headers=HEADERS, proxy=proxy)
            await asyncio.sleep(random.uniform(1, 3))
            await session.get(OPTION_CHAIN_PAGE, headers=HEADERS, proxy=proxy)
            await asyncio.sleep(random.uniform(1, 3))
            async with session.get(API_URL, headers=HEADERS, proxy=proxy) as response:
                elapsed_time = time.time() - start_time
                if response.status == 200:
                    return {"proxy": proxy, "status": "Working", "time": f"{elapsed_time:.2f} sec"}
                else:
                    body = await response.text()
                    print(f"Response body for {proxy}: {body[:200]}")
                    return {"proxy": proxy, "status": f"Failed (Code: {response.status})", "time": "N/A"}
    except Exception as e:
        print(f"Exception for {proxy}: {e}")
        traceback.print_exc()
        return {"proxy": proxy, "status": f"Failed ({str(e)})", "time": "N/A"}

async def main():
    print("Checking proxies for NSE option chain API...\n")
    results = await asyncio.gather(*(check_proxy(proxy) for proxy in PROXIES), return_exceptions=True)

    working_count = 0

    for result in results:
        if isinstance(result, dict):
            print(f"Proxy: {result['proxy']}")
            print(f"Status: {result['status']}")
            print(f"Time: {result['time']}\n")
            if result["status"] == "Working":
                working_count += 1
        else:
            print(f"Exception occurred: {result}")

    print(f"Summary: {working_count}/{len(PROXIES)} proxies working")

if __name__ == "__main__":
    asyncio.run(main())

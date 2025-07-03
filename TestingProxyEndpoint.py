#%%
import aiohttp
import asyncio
import time

# List of proxies to test
PROXIES = [
"http://192.168.18.4:31"
]

# Test stock symbol
STOCK = "RELIANCE"

# API endpoint and preliminary URLs
BASE_URL = "https://www.nseindia.com"
OPTION_CHAIN_PAGE = "https://www.nseindia.com/option-chain"
API_URL = f"https://www.nseindia.com/api/option-chain-equities?symbol={STOCK}"

# Headers from your snippet
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9"
}

async def check_proxy(proxy):
    start_time = time.time()
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout, connector=aiohttp.TCPConnector(ssl=False)) as session:
            # Preliminary requests to mimic your code
            await session.get(BASE_URL, headers=HEADERS, proxy=proxy)
            await session.get(OPTION_CHAIN_PAGE, headers=HEADERS, proxy=proxy)
            # API request
            async with session.get(API_URL, headers=HEADERS, proxy=proxy) as response:
                elapsed_time = time.time() - start_time
                if response.status == 200:
                    return {"proxy": proxy, "status": "Working", "time": f"{elapsed_time:.2f} sec"}
                return {"proxy": proxy, "status": f"Failed (Code: {response.status})", "time": "N/A"}
    except Exception as e:
        return {"proxy": proxy, "status": f"Failed ({str(e)})", "time": "N/A"}

async def main():
    print("Checking proxies for NSE option chain API...\n")
    # Run all proxy checks concurrently
    results = await asyncio.gather(*(check_proxy(proxy) for proxy in PROXIES), return_exceptions=True)

    working_count = 0
    for result in results:
        print(f"Proxy: {result['proxy']}")
        print(f"Status: {result['status']}")
        print(f"Time: {result['time']}\n")
        if result["status"] == "Working":
            working_count += 1

    print(f"Summary: {working_count}/{len(PROXIES)} proxies working")

if __name__ == "__main__":
    asyncio.run(main())
import aiohttp
import asyncio
import time
import random
import ssl
import traceback

PROXIES = [
"https://spdsnruo64:0Co0+qHdxIRrk8vrk2@gate.decodo.com:10001"
]

STOCK = "RELIANCE"
BASE_URL = "https://www.nseindia.com"
OPTION_CHAIN_PAGE = "https://www.nseindia.com/option-chain"
API_URL = f"https://www.nseindia.com/api/option-chain-equities?symbol={STOCK}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9"
}

async def check_proxy(proxy):
    start_time = time.time()
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            await session.get(BASE_URL, headers=HEADERS, proxy=proxy)
            await asyncio.sleep(random.uniform(1, 2))
            await session.get(OPTION_CHAIN_PAGE, headers=HEADERS, proxy=proxy)
            await asyncio.sleep(random.uniform(1, 2))
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

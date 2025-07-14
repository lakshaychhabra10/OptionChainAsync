#%%

import asyncio
import concurrent.futures
from curl_cffi import requests as cureq
import time

# Configuration
stock = "RELIANCE"
url = f"https://www.nseindia.com/api/option-chain-equities?symbol={stock}"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

from config import PROXY

# List of proxies to test (add more as needed)
PROXIES_LIST = PROXY

def test_proxy(proxy):
    """Test if a proxy works with the NSE India endpoint"""
    try:
        with cureq.Session(impersonate="chrome110") as session:
            # Set timeout for all requests (in seconds)
            timeout = 20
            
            # First request to set cookies
            session.get("https://www.nseindia.com", proxies=proxy, timeout=timeout)
            
            # Second request to maintain session
            session.get("https://www.nseindia.com/option-chain", proxies=proxy, timeout=timeout)
            
            # Final API request
            response = session.get(url, headers=headers, proxies=proxy, timeout=timeout)
            
            # Check for successful response
            if response.status_code == 200:
                response.json()  # Test if valid JSON
                return True
    except Exception as e:
        # Uncomment below for debugging
        print(f"Proxy failed ({proxy['http']}): {str(e)}")
        pass
    return False

async def test_proxies_concurrently(proxies_list, max_workers=300):
    """Test proxies concurrently using thread pool"""
    working_proxies = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_running_loop()
        futures = [
            loop.run_in_executor(executor, test_proxy, proxy)
            for proxy in proxies_list
        ]
        
        for future, proxy in zip(asyncio.as_completed(futures), proxies_list):
            result = await future
            if result:
                working_proxies.append(proxy)
                print(f"✅ Working proxy: {proxy['http']}")
            else:
                print(f"❌ Failed proxy: {proxy['http']}")
    
    return working_proxies

async def main():
    print(f"Starting proxy test with {len(PROXIES_LIST)} proxies...")
    start_time = time.time()
    
    working_proxies = await test_proxies_concurrently(PROXIES_LIST, max_workers=10)
    
    print("\n" + "="*50)
    print(f"Test completed in {time.time() - start_time:.2f} seconds")
    print(f"Total proxies tested: {len(PROXIES_LIST)}")
    print(f"Working proxies: {len(working_proxies)}")
    print("="*50)
    
    if working_proxies:
        print("\nWorking proxy list:")
        for i, proxy in enumerate(working_proxies, 1):
            print(f"{i}. {proxy['http']}")
    else:
        print("\nNo working proxies found")

if __name__ == "__main__":
    asyncio.run(main())
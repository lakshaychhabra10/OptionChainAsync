#%%


import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# List of proxies to test
proxies_list = [
    "https://spdsnruo64:0Co0+qHdxIRrk8vrk2@in.decodo.com:10000",
]

proxies_list *= 100  # Repeat the list to simulate a larger set of proxies

# Test URL to check proxy connectivity
TEST_URL = "http://httpbin.org/ip"

def check_proxy(proxy):
    """Check if a proxy is working by making a request to the test URL."""
    proxy_dict = {"http": proxy, "https": proxy}
    start_time = time.time()
    try:
        response = requests.get(TEST_URL, proxies=proxy_dict, timeout=10, verify=False)
        if response.status_code == 200:
            elapsed_time = time.time() - start_time
            return {"proxy": proxy, "status": "Working", "response_time": f"{elapsed_time:.2f} seconds"}
        else:
            return {"proxy": proxy, "status": f"Failed (Status Code: {response.status_code})", "response_time": None}
    except requests.exceptions.RequestException as e:
        return {"proxy": proxy, "status": f"Failed ({str(e)})", "response_time": None}

def main():
    print("Checking proxies...\n")
    results = []

    # Use ThreadPoolExecutor to check proxies concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies_list}
        for future in as_completed(future_to_proxy):
            results.append(future.result())

    # Sort results by proxy for consistent output
    results.sort(key=lambda x: x["proxy"])

    # Print results
    working_proxies = 0
    for result in results:
        status = result["status"]
        proxy = result["proxy"]
        response_time = result["response_time"] if result["response_time"] else "N/A"
        print(f"Proxy: {proxy}")
        print(f"Status: {status}")
        print(f"Response Time: {response_time}\n")
        if "Working" in status:
            working_proxies += 1

    print(f"Summary: {working_proxies}/{len(proxies_list)} proxies are working.")


if __name__ == "__main__":
    main()
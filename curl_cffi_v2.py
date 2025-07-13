#%%

from curl_cffi import requests as cureq

stock = "RELIANCE"
url = f"https://www.nseindia.com/api/option-chain-equities?symbol={stock}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

PROXY = {
    'http': 'http://iqoopiiq:x8z7nvi33uls@38.154.227.167:5868',
    'https': 'http://iqoopiiq:x8z7nvi33uls@38.154.227.167:5868'
}


with cureq.Session(impersonate="chrome110") as session:
    # First request (sets cookies)
    response1 = session.get("https://www.nseindia.com", proxies=PROXY)
    print(response1.cookies)

    # Second request (reuses cookies)
    response2 = session.get("https://www.nseindia.com/option-chain", proxies = PROXY)

    response3 = session.get(url, headers=headers, proxies = PROXY)
    print(response3.json())

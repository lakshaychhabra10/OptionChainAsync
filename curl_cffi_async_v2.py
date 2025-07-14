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

# List of proxies to test (add more as needed)
PROXIES_LIST = [
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.43.189.50:5721",
        "https": "http://aeizewrd:c7r90z945p6n@45.43.189.50:5721"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@46.203.202.120:6066",
        "https": "http://aeizewrd:c7r90z945p6n@46.203.202.120:6066"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@166.0.68.17:6477",
        "https": "http://aeizewrd:c7r90z945p6n@166.0.68.17:6477"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.38.122.43:6951",
        "https": "http://aeizewrd:c7r90z945p6n@45.38.122.43:6951"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@142.147.242.230:6209",
        "https": "http://aeizewrd:c7r90z945p6n@142.147.242.230:6209"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.43.186.43:6261",
        "https": "http://aeizewrd:c7r90z945p6n@45.43.186.43:6261"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@140.99.193.137:7515",
        "https": "http://aeizewrd:c7r90z945p6n@140.99.193.137:7515"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@184.174.25.184:6073",
        "https": "http://aeizewrd:c7r90z945p6n@184.174.25.184:6073"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@185.48.52.134:5726",
        "https": "http://aeizewrd:c7r90z945p6n@185.48.52.134:5726"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@191.96.69.25:5538",
        "https": "http://aeizewrd:c7r90z945p6n@191.96.69.25:5538"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.27.254.45:6404",
        "https": "http://aeizewrd:c7r90z945p6n@82.27.254.45:6404"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@107.174.194.159:5601",
        "https": "http://aeizewrd:c7r90z945p6n@107.174.194.159:5601"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@92.112.172.233:6505",
        "https": "http://aeizewrd:c7r90z945p6n@92.112.172.233:6505"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@192.198.126.226:7269",
        "https": "http://aeizewrd:c7r90z945p6n@192.198.126.226:7269"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.29.254.151:7011",
        "https": "http://aeizewrd:c7r90z945p6n@82.29.254.151:7011"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@92.112.238.216:7095",
        "https": "http://aeizewrd:c7r90z945p6n@92.112.238.216:7095"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.252.71.104:6032",
        "https": "http://aeizewrd:c7r90z945p6n@104.252.71.104:6032"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@185.39.8.61:5718",
        "https": "http://aeizewrd:c7r90z945p6n@185.39.8.61:5718"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@50.114.15.171:6156",
        "https": "http://aeizewrd:c7r90z945p6n@50.114.15.171:6156"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.25.247.117:6451",
        "https": "http://aeizewrd:c7r90z945p6n@82.25.247.117:6451"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@155.254.34.242:6222",
        "https": "http://aeizewrd:c7r90z945p6n@155.254.34.242:6222"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@107.175.56.96:6369",
        "https": "http://aeizewrd:c7r90z945p6n@107.175.56.96:6369"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@148.135.254.252:6299",
        "https": "http://aeizewrd:c7r90z945p6n@148.135.254.252:6299"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@84.33.224.189:6213",
        "https": "http://aeizewrd:c7r90z945p6n@84.33.224.189:6213"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@207.244.217.230:6777",
        "https": "http://aeizewrd:c7r90z945p6n@207.244.217.230:6777"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.238.9.128:6581",
        "https": "http://aeizewrd:c7r90z945p6n@104.238.9.128:6581"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@107.172.156.99:5747",
        "https": "http://aeizewrd:c7r90z945p6n@107.172.156.99:5747"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@155.254.34.83:6063",
        "https": "http://aeizewrd:c7r90z945p6n@155.254.34.83:6063"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@31.58.18.225:6494",
        "https": "http://aeizewrd:c7r90z945p6n@31.58.18.225:6494"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@199.180.9.112:6132",
        "https": "http://aeizewrd:c7r90z945p6n@199.180.9.112:6132"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.38.67.58:6990",
        "https": "http://aeizewrd:c7r90z945p6n@45.38.67.58:6990"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@23.95.250.15:6288",
        "https": "http://aeizewrd:c7r90z945p6n@23.95.250.15:6288"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@107.174.136.76:6018",
        "https": "http://aeizewrd:c7r90z945p6n@107.174.136.76:6018"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.39.18.155:6591",
        "https": "http://aeizewrd:c7r90z945p6n@45.39.18.155:6591"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@166.88.155.191:6350",
        "https": "http://aeizewrd:c7r90z945p6n@166.88.155.191:6350"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@154.30.250.163:5675",
        "https": "http://aeizewrd:c7r90z945p6n@154.30.250.163:5675"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@23.95.250.233:6506",
        "https": "http://aeizewrd:c7r90z945p6n@23.95.250.233:6506"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.24.224.66:5422",
        "https": "http://aeizewrd:c7r90z945p6n@82.24.224.66:5422"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@23.27.196.78:6447",
        "https": "http://aeizewrd:c7r90z945p6n@23.27.196.78:6447"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@38.170.176.234:5629",
        "https": "http://aeizewrd:c7r90z945p6n@38.170.176.234:5629"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@193.25.167.181:5712",
        "https": "http://aeizewrd:c7r90z945p6n@193.25.167.181:5712"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@217.69.127.242:6863",
        "https": "http://aeizewrd:c7r90z945p6n@217.69.127.242:6863"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@145.223.55.95:7142",
        "https": "http://aeizewrd:c7r90z945p6n@145.223.55.95:7142"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@198.46.137.58:6262",
        "https": "http://aeizewrd:c7r90z945p6n@198.46.137.58:6262"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.222.161.164:6296",
        "https": "http://aeizewrd:c7r90z945p6n@104.222.161.164:6296"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@107.173.105.13:5700",
        "https": "http://aeizewrd:c7r90z945p6n@107.173.105.13:5700"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.39.1.14:5453",
        "https": "http://aeizewrd:c7r90z945p6n@45.39.1.14:5453"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@91.124.253.142:6502",
        "https": "http://aeizewrd:c7r90z945p6n@91.124.253.142:6502"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.239.105.225:6755",
        "https": "http://aeizewrd:c7r90z945p6n@104.239.105.225:6755"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@154.73.250.86:5987",
        "https": "http://aeizewrd:c7r90z945p6n@154.73.250.86:5987"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@92.112.137.59:6002",
        "https": "http://aeizewrd:c7r90z945p6n@92.112.137.59:6002"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@64.137.31.235:6849",
        "https": "http://aeizewrd:c7r90z945p6n@64.137.31.235:6849"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@85.198.47.67:6335",
        "https": "http://aeizewrd:c7r90z945p6n@85.198.47.67:6335"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.238.8.203:6061",
        "https": "http://aeizewrd:c7r90z945p6n@104.238.8.203:6061"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@161.123.93.117:5847",
        "https": "http://aeizewrd:c7r90z945p6n@161.123.93.117:5847"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@161.123.154.14:6544",
        "https": "http://aeizewrd:c7r90z945p6n@161.123.154.14:6544"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@166.88.217.171:6504",
        "https": "http://aeizewrd:c7r90z945p6n@166.88.217.171:6504"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@31.59.13.193:6463",
        "https": "http://aeizewrd:c7r90z945p6n@31.59.13.193:6463"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@89.45.125.57:5783",
        "https": "http://aeizewrd:c7r90z945p6n@89.45.125.57:5783"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@185.171.254.102:6134",
        "https": "http://aeizewrd:c7r90z945p6n@185.171.254.102:6134"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@38.170.158.152:5428",
        "https": "http://aeizewrd:c7r90z945p6n@38.170.158.152:5428"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@38.170.189.207:9773",
        "https": "http://aeizewrd:c7r90z945p6n@38.170.189.207:9773"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.252.71.10:5938",
        "https": "http://aeizewrd:c7r90z945p6n@104.252.71.10:5938"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.251.61.5:6723",
        "https": "http://aeizewrd:c7r90z945p6n@45.251.61.5:6723"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.23.235.46:5370",
        "https": "http://aeizewrd:c7r90z945p6n@82.23.235.46:5370"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@172.98.169.3:6427",
        "https": "http://aeizewrd:c7r90z945p6n@172.98.169.3:6427"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@92.112.136.46:5990",
        "https": "http://aeizewrd:c7r90z945p6n@92.112.136.46:5990"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@142.147.240.171:6693",
        "https": "http://aeizewrd:c7r90z945p6n@142.147.240.171:6693"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@185.15.178.184:5868",
        "https": "http://aeizewrd:c7r90z945p6n@185.15.178.184:5868"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@198.105.122.19:6592",
        "https": "http://aeizewrd:c7r90z945p6n@198.105.122.19:6592"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@23.129.253.171:6789",
        "https": "http://aeizewrd:c7r90z945p6n@23.129.253.171:6789"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.41.169.50:6711",
        "https": "http://aeizewrd:c7r90z945p6n@45.41.169.50:6711"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.141.80.26:5752",
        "https": "http://aeizewrd:c7r90z945p6n@45.141.80.26:5752"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@67.227.1.30:6311",
        "https": "http://aeizewrd:c7r90z945p6n@67.227.1.30:6311"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.25.242.53:7372",
        "https": "http://aeizewrd:c7r90z945p6n@82.25.242.53:7372"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@209.127.191.157:5231",
        "https": "http://aeizewrd:c7r90z945p6n@209.127.191.157:5231"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.26.242.51:6870",
        "https": "http://aeizewrd:c7r90z945p6n@82.26.242.51:6870"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.22.247.218:8052",
        "https": "http://aeizewrd:c7r90z945p6n@82.22.247.218:8052"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.29.236.201:8014",
        "https": "http://aeizewrd:c7r90z945p6n@82.29.236.201:8014"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@166.88.217.52:6385",
        "https": "http://aeizewrd:c7r90z945p6n@166.88.217.52:6385"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@147.124.198.116:5975",
        "https": "http://aeizewrd:c7r90z945p6n@147.124.198.116:5975"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@216.173.122.190:5917",
        "https": "http://aeizewrd:c7r90z945p6n@216.173.122.190:5917"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.253.0.91:6530",
        "https": "http://aeizewrd:c7r90z945p6n@104.253.0.91:6530"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@181.214.13.16:5857",
        "https": "http://aeizewrd:c7r90z945p6n@181.214.13.16:5857"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@185.72.241.243:7535",
        "https": "http://aeizewrd:c7r90z945p6n@185.72.241.243:7535"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.38.86.158:6087",
        "https": "http://aeizewrd:c7r90z945p6n@45.38.86.158:6087"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@38.170.172.10:5011",
        "https": "http://aeizewrd:c7r90z945p6n@38.170.172.10:5011"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@173.244.41.144:6328",
        "https": "http://aeizewrd:c7r90z945p6n@173.244.41.144:6328"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.91.166.28:7087",
        "https": "http://aeizewrd:c7r90z945p6n@45.91.166.28:7087"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@89.43.32.84:5912",
        "https": "http://aeizewrd:c7r90z945p6n@89.43.32.84:5912"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@142.147.129.200:5809",
        "https": "http://aeizewrd:c7r90z945p6n@142.147.129.200:5809"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@204.217.245.17:6608",
        "https": "http://aeizewrd:c7r90z945p6n@204.217.245.17:6608"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.233.20.243:6259",
        "https": "http://aeizewrd:c7r90z945p6n@104.233.20.243:6259"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.253.82.2:6423",
        "https": "http://aeizewrd:c7r90z945p6n@104.253.82.2:6423"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@145.223.59.244:6278",
        "https": "http://aeizewrd:c7r90z945p6n@145.223.59.244:6278"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@38.170.161.206:9257",
        "https": "http://aeizewrd:c7r90z945p6n@38.170.161.206:9257"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@92.112.175.214:6487",
        "https": "http://aeizewrd:c7r90z945p6n@92.112.175.214:6487"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@166.88.58.77:5802",
        "https": "http://aeizewrd:c7r90z945p6n@166.88.58.77:5802"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.21.218.95:6447",
        "https": "http://aeizewrd:c7r90z945p6n@82.21.218.95:6447"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.23.215.129:7456",
        "https": "http://aeizewrd:c7r90z945p6n@82.23.215.129:7456"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.131.94.57:6044",
        "https": "http://aeizewrd:c7r90z945p6n@45.131.94.57:6044"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@64.64.110.109:6632",
        "https": "http://aeizewrd:c7r90z945p6n@64.64.110.109:6632"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@64.137.89.10:6083",
        "https": "http://aeizewrd:c7r90z945p6n@64.137.89.10:6083"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@206.206.73.243:6859",
        "https": "http://aeizewrd:c7r90z945p6n@206.206.73.243:6859"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.24.221.132:5983",
        "https": "http://aeizewrd:c7r90z945p6n@82.24.221.132:5983"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.222.185.252:5815",
        "https": "http://aeizewrd:c7r90z945p6n@104.222.185.252:5815"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@172.102.223.177:5688",
        "https": "http://aeizewrd:c7r90z945p6n@172.102.223.177:5688"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.26.235.105:7920",
        "https": "http://aeizewrd:c7r90z945p6n@82.26.235.105:7920"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@185.216.105.236:6813",
        "https": "http://aeizewrd:c7r90z945p6n@185.216.105.236:6813"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.23.239.150:6487",
        "https": "http://aeizewrd:c7r90z945p6n@82.23.239.150:6487"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.222.185.52:5615",
        "https": "http://aeizewrd:c7r90z945p6n@104.222.185.52:5615"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@206.41.168.73:6738",
        "https": "http://aeizewrd:c7r90z945p6n@206.41.168.73:6738"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@142.111.192.66:5662",
        "https": "http://aeizewrd:c7r90z945p6n@142.111.192.66:5662"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@142.111.131.39:6117",
        "https": "http://aeizewrd:c7r90z945p6n@142.111.131.39:6117"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@145.223.59.221:6255",
        "https": "http://aeizewrd:c7r90z945p6n@145.223.59.221:6255"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@154.29.233.119:5880",
        "https": "http://aeizewrd:c7r90z945p6n@154.29.233.119:5880"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.117.55.141:6787",
        "https": "http://aeizewrd:c7r90z945p6n@45.117.55.141:6787"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@166.88.238.3:5983",
        "https": "http://aeizewrd:c7r90z945p6n@166.88.238.3:5983"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@23.109.208.241:6765",
        "https": "http://aeizewrd:c7r90z945p6n@23.109.208.241:6765"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@184.174.44.241:6667",
        "https": "http://aeizewrd:c7r90z945p6n@184.174.44.241:6667"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.22.245.66:5890",
        "https": "http://aeizewrd:c7r90z945p6n@82.22.245.66:5890"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@92.112.236.33:6465",
        "https": "http://aeizewrd:c7r90z945p6n@92.112.236.33:6465"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@145.223.55.233:7280",
        "https": "http://aeizewrd:c7r90z945p6n@145.223.55.233:7280"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@109.196.161.252:6700",
        "https": "http://aeizewrd:c7r90z945p6n@109.196.161.252:6700"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@191.101.26.244:5983",
        "https": "http://aeizewrd:c7r90z945p6n@191.101.26.244:5983"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@64.137.60.53:5117",
        "https": "http://aeizewrd:c7r90z945p6n@64.137.60.53:5117"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@103.101.88.81:5805",
        "https": "http://aeizewrd:c7r90z945p6n@103.101.88.81:5805"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.91.167.99:6658",
        "https": "http://aeizewrd:c7r90z945p6n@45.91.167.99:6658"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@46.202.227.39:6033",
        "https": "http://aeizewrd:c7r90z945p6n@46.202.227.39:6033"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@107.181.148.205:6065",
        "https": "http://aeizewrd:c7r90z945p6n@107.181.148.205:6065"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@191.96.117.223:6978",
        "https": "http://aeizewrd:c7r90z945p6n@191.96.117.223:6978"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.41.177.39:5689",
        "https": "http://aeizewrd:c7r90z945p6n@45.41.177.39:5689"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@84.33.241.199:6556",
        "https": "http://aeizewrd:c7r90z945p6n@84.33.241.199:6556"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@64.137.88.220:6459",
        "https": "http://aeizewrd:c7r90z945p6n@64.137.88.220:6459"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.238.10.184:6130",
        "https": "http://aeizewrd:c7r90z945p6n@104.238.10.184:6130"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@198.37.98.199:5729",
        "https": "http://aeizewrd:c7r90z945p6n@198.37.98.199:5729"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@2.57.20.8:6000",
        "https": "http://aeizewrd:c7r90z945p6n@2.57.20.8:6000"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.91.167.121:6680",
        "https": "http://aeizewrd:c7r90z945p6n@45.91.167.121:6680"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.21.208.6:7323",
        "https": "http://aeizewrd:c7r90z945p6n@82.21.208.6:7323"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@23.229.19.142:8737",
        "https": "http://aeizewrd:c7r90z945p6n@23.229.19.142:8737"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.39.18.43:6479",
        "https": "http://aeizewrd:c7r90z945p6n@45.39.18.43:6479"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@89.249.193.161:5899",
        "https": "http://aeizewrd:c7r90z945p6n@89.249.193.161:5899"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@92.112.137.179:6122",
        "https": "http://aeizewrd:c7r90z945p6n@92.112.137.179:6122"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@23.27.210.108:6478",
        "https": "http://aeizewrd:c7r90z945p6n@23.27.210.108:6478"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@46.203.202.218:6164",
        "https": "http://aeizewrd:c7r90z945p6n@46.203.202.218:6164"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@136.0.117.155:6893",
        "https": "http://aeizewrd:c7r90z945p6n@136.0.117.155:6893"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@173.244.41.92:6276",
        "https": "http://aeizewrd:c7r90z945p6n@173.244.41.92:6276"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@193.42.225.131:6622",
        "https": "http://aeizewrd:c7r90z945p6n@193.42.225.131:6622"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@179.61.245.79:6858",
        "https": "http://aeizewrd:c7r90z945p6n@179.61.245.79:6858"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@184.174.56.76:5088",
        "https": "http://aeizewrd:c7r90z945p6n@184.174.56.76:5088"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@92.112.136.92:6036",
        "https": "http://aeizewrd:c7r90z945p6n@92.112.136.92:6036"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@38.153.135.55:5435",
        "https": "http://aeizewrd:c7r90z945p6n@38.153.135.55:5435"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.83.57.147:6664",
        "https": "http://aeizewrd:c7r90z945p6n@45.83.57.147:6664"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.222.167.14:6416",
        "https": "http://aeizewrd:c7r90z945p6n@104.222.167.14:6416"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.27.254.81:6440",
        "https": "http://aeizewrd:c7r90z945p6n@82.27.254.81:6440"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@184.174.56.238:5250",
        "https": "http://aeizewrd:c7r90z945p6n@184.174.56.238:5250"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@148.135.148.77:6070",
        "https": "http://aeizewrd:c7r90z945p6n@148.135.148.77:6070"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@185.135.10.188:5702",
        "https": "http://aeizewrd:c7r90z945p6n@185.135.10.188:5702"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@185.216.105.41:6618",
        "https": "http://aeizewrd:c7r90z945p6n@185.216.105.41:6618"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.67.0.144:6580",
        "https": "http://aeizewrd:c7r90z945p6n@45.67.0.144:6580"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@46.203.202.19:5965",
        "https": "http://aeizewrd:c7r90z945p6n@46.203.202.19:5965"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.23.223.86:7930",
        "https": "http://aeizewrd:c7r90z945p6n@82.23.223.86:7930"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.23.224.99:7414",
        "https": "http://aeizewrd:c7r90z945p6n@82.23.224.99:7414"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@154.36.85.46:6557",
        "https": "http://aeizewrd:c7r90z945p6n@154.36.85.46:6557"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@194.5.3.121:5633",
        "https": "http://aeizewrd:c7r90z945p6n@194.5.3.121:5633"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@199.180.9.166:6186",
        "https": "http://aeizewrd:c7r90z945p6n@199.180.9.166:6186"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.131.103.206:6192",
        "https": "http://aeizewrd:c7r90z945p6n@45.131.103.206:6192"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@23.26.94.81:6063",
        "https": "http://aeizewrd:c7r90z945p6n@23.26.94.81:6063"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.143.229.30:5958",
        "https": "http://aeizewrd:c7r90z945p6n@104.143.229.30:5958"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.239.104.107:6331",
        "https": "http://aeizewrd:c7r90z945p6n@104.239.104.107:6331"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@107.174.25.92:5546",
        "https": "http://aeizewrd:c7r90z945p6n@107.174.25.92:5546"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@38.153.132.236:5343",
        "https": "http://aeizewrd:c7r90z945p6n@38.153.132.236:5343"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@77.81.103.181:5698",
        "https": "http://aeizewrd:c7r90z945p6n@77.81.103.181:5698"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@198.23.239.197:6603",
        "https": "http://aeizewrd:c7r90z945p6n@198.23.239.197:6603"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@217.198.177.229:5745",
        "https": "http://aeizewrd:c7r90z945p6n@217.198.177.229:5745"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.39.1.224:5663",
        "https": "http://aeizewrd:c7r90z945p6n@45.39.1.224:5663"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@50.114.93.148:6132",
        "https": "http://aeizewrd:c7r90z945p6n@50.114.93.148:6132"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.252.71.77:6005",
        "https": "http://aeizewrd:c7r90z945p6n@104.252.71.77:6005"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@181.214.13.189:6030",
        "https": "http://aeizewrd:c7r90z945p6n@181.214.13.189:6030"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@149.57.17.244:5712",
        "https": "http://aeizewrd:c7r90z945p6n@149.57.17.244:5712"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@155.254.39.62:6020",
        "https": "http://aeizewrd:c7r90z945p6n@155.254.39.62:6020"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.29.249.246:8083",
        "https": "http://aeizewrd:c7r90z945p6n@82.29.249.246:8083"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@145.223.46.250:5800",
        "https": "http://aeizewrd:c7r90z945p6n@145.223.46.250:5800"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@173.244.41.94:6278",
        "https": "http://aeizewrd:c7r90z945p6n@173.244.41.94:6278"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.252.196.17:5925",
        "https": "http://aeizewrd:c7r90z945p6n@104.252.196.17:5925"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@38.225.2.141:5924",
        "https": "http://aeizewrd:c7r90z945p6n@38.225.2.141:5924"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.29.237.159:7968",
        "https": "http://aeizewrd:c7r90z945p6n@82.29.237.159:7968"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@146.103.4.187:6734",
        "https": "http://aeizewrd:c7r90z945p6n@146.103.4.187:6734"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.24.239.52:6909",
        "https": "http://aeizewrd:c7r90z945p6n@82.24.239.52:6909"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.143.251.36:6298",
        "https": "http://aeizewrd:c7r90z945p6n@104.143.251.36:6298"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@136.0.126.163:5924",
        "https": "http://aeizewrd:c7r90z945p6n@136.0.126.163:5924"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@38.154.195.250:9338",
        "https": "http://aeizewrd:c7r90z945p6n@38.154.195.250:9338"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@154.36.110.235:6889",
        "https": "http://aeizewrd:c7r90z945p6n@154.36.110.235:6889"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.252.28.143:6081",
        "https": "http://aeizewrd:c7r90z945p6n@104.252.28.143:6081"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.239.6.238:6372",
        "https": "http://aeizewrd:c7r90z945p6n@104.239.6.238:6372"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@172.245.157.102:6687",
        "https": "http://aeizewrd:c7r90z945p6n@172.245.157.102:6687"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@207.244.219.213:6469",
        "https": "http://aeizewrd:c7r90z945p6n@207.244.219.213:6469"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@84.33.214.148:6034",
        "https": "http://aeizewrd:c7r90z945p6n@84.33.214.148:6034"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@192.186.172.22:9022",
        "https": "http://aeizewrd:c7r90z945p6n@192.186.172.22:9022"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.43.189.250:5921",
        "https": "http://aeizewrd:c7r90z945p6n@45.43.189.250:5921"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@23.229.126.99:7628",
        "https": "http://aeizewrd:c7r90z945p6n@23.229.126.99:7628"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.67.3.173:6336",
        "https": "http://aeizewrd:c7r90z945p6n@45.67.3.173:6336"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@148.135.151.37:5530",
        "https": "http://aeizewrd:c7r90z945p6n@148.135.151.37:5530"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.43.184.149:5823",
        "https": "http://aeizewrd:c7r90z945p6n@45.43.184.149:5823"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.61.127.254:6193",
        "https": "http://aeizewrd:c7r90z945p6n@45.61.127.254:6193"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@46.203.206.152:5597",
        "https": "http://aeizewrd:c7r90z945p6n@46.203.206.152:5597"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@191.101.26.82:5821",
        "https": "http://aeizewrd:c7r90z945p6n@191.101.26.82:5821"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@206.41.164.214:6513",
        "https": "http://aeizewrd:c7r90z945p6n@206.41.164.214:6513"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@103.99.33.5:6000",
        "https": "http://aeizewrd:c7r90z945p6n@103.99.33.5:6000"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@142.111.48.173:6950",
        "https": "http://aeizewrd:c7r90z945p6n@142.111.48.173:6950"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.84.44.188:5666",
        "https": "http://aeizewrd:c7r90z945p6n@45.84.44.188:5666"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@191.96.254.246:6293",
        "https": "http://aeizewrd:c7r90z945p6n@191.96.254.246:6293"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.38.101.129:6062",
        "https": "http://aeizewrd:c7r90z945p6n@45.38.101.129:6062"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.23.243.199:7557",
        "https": "http://aeizewrd:c7r90z945p6n@82.23.243.199:7557"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@86.38.236.199:6483",
        "https": "http://aeizewrd:c7r90z945p6n@86.38.236.199:6483"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@107.174.25.89:5543",
        "https": "http://aeizewrd:c7r90z945p6n@107.174.25.89:5543"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@145.223.41.93:6364",
        "https": "http://aeizewrd:c7r90z945p6n@145.223.41.93:6364"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.25.247.83:6417",
        "https": "http://aeizewrd:c7r90z945p6n@82.25.247.83:6417"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@89.43.32.7:5835",
        "https": "http://aeizewrd:c7r90z945p6n@89.43.32.7:5835"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@107.175.56.253:6526",
        "https": "http://aeizewrd:c7r90z945p6n@107.175.56.253:6526"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@173.211.30.138:6572",
        "https": "http://aeizewrd:c7r90z945p6n@173.211.30.138:6572"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.29.226.99:7441",
        "https": "http://aeizewrd:c7r90z945p6n@82.29.226.99:7441"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@23.129.253.254:6872",
        "https": "http://aeizewrd:c7r90z945p6n@23.129.253.254:6872"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.238.36.1:6008",
        "https": "http://aeizewrd:c7r90z945p6n@104.238.36.1:6008"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.239.106.12:5657",
        "https": "http://aeizewrd:c7r90z945p6n@104.239.106.12:5657"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@107.173.105.27:5714",
        "https": "http://aeizewrd:c7r90z945p6n@107.173.105.27:5714"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.56.174.216:6469",
        "https": "http://aeizewrd:c7r90z945p6n@45.56.174.216:6469"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.21.238.26:7829",
        "https": "http://aeizewrd:c7r90z945p6n@82.21.238.26:7829"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.24.236.53:7863",
        "https": "http://aeizewrd:c7r90z945p6n@82.24.236.53:7863"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@104.252.41.52:6989",
        "https": "http://aeizewrd:c7r90z945p6n@104.252.41.52:6989"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@38.225.2.129:5912",
        "https": "http://aeizewrd:c7r90z945p6n@38.225.2.129:5912"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@64.137.48.53:6260",
        "https": "http://aeizewrd:c7r90z945p6n@64.137.48.53:6260"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@154.6.59.132:6600",
        "https": "http://aeizewrd:c7r90z945p6n@154.6.59.132:6600"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@207.244.219.166:6422",
        "https": "http://aeizewrd:c7r90z945p6n@207.244.219.166:6422"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@140.99.215.200:7575",
        "https": "http://aeizewrd:c7r90z945p6n@140.99.215.200:7575"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@154.6.121.9:5976",
        "https": "http://aeizewrd:c7r90z945p6n@154.6.121.9:5976"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@198.105.119.161:5410",
        "https": "http://aeizewrd:c7r90z945p6n@198.105.119.161:5410"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@45.43.189.134:5805",
        "https": "http://aeizewrd:c7r90z945p6n@45.43.189.134:5805"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@184.174.56.129:5141",
        "https": "http://aeizewrd:c7r90z945p6n@184.174.56.129:5141"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@46.202.79.66:7076",
        "https": "http://aeizewrd:c7r90z945p6n@46.202.79.66:7076"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@64.137.60.95:5159",
        "https": "http://aeizewrd:c7r90z945p6n@64.137.60.95:5159"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@2.57.20.14:6006",
        "https": "http://aeizewrd:c7r90z945p6n@2.57.20.14:6006"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@31.58.10.181:6149",
        "https": "http://aeizewrd:c7r90z945p6n@31.58.10.181:6149"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@89.213.141.129:7005",
        "https": "http://aeizewrd:c7r90z945p6n@89.213.141.129:7005"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@140.99.203.126:6003",
        "https": "http://aeizewrd:c7r90z945p6n@140.99.203.126:6003"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@161.123.131.244:5849",
        "https": "http://aeizewrd:c7r90z945p6n@161.123.131.244:5849"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.25.242.114:7433",
        "https": "http://aeizewrd:c7r90z945p6n@82.25.242.114:7433"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@206.41.164.242:6541",
        "https": "http://aeizewrd:c7r90z945p6n@206.41.164.242:6541"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@46.203.157.222:7165",
        "https": "http://aeizewrd:c7r90z945p6n@46.203.157.222:7165"
    },
    {
        "http": "http://aeizewrd:c7r90z945p6n@82.22.217.188:5530",
        "https": "http://aeizewrd:c7r90z945p6n@82.22.217.188:5530"
    }
]

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
import requests

# url = "http://www.jimbabbage.ca/cgi-sys/bxd.cgi?a=jim@jimbabbage.ca&id=ejpu5dcPaBojJm4lYrjjI-1741281817"
url = "http://www.digitalmoneytalk.com/cgi-sys/bxd.cgi?a=admin@digitalmoneytalk.com&id=bEfopuLViKymnTtpgX3WT-1741959710"

payload = {}
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

import requests

url = "http://www.gabrooksengineering.com/cgi-sys/bxd.cgi?a=greg@gabrooksengineering.com&id=dj7Ill3GQiehK9Eeqlkae-1741616116"
payload = {}
headers = {
    'sec-ch-ua-platform': '"macOS"',
    'Referer': 'https://juejin.cn/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'Content-Type': 'application/json',
    'sec-ch-ua-mobile': '?0'
}
response = requests.request("GET", url, headers=headers, data=payload)
text = response.text
print("click reply content", text)
if "Successful" in text:
    print("处理链接邮件成功")
else:
    print("处理链接邮件失败")
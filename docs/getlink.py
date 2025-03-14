import re

with open("link3.html", "r") as f:
    links = f.read()
    # 定义正则表达式来匹配URL
    url_pattern = r"https?://[^\s<>\"']+"
    # 使用正则表达式查找所有匹配的URL
    urls = re.search(url_pattern, links)
    # 打印提取的URL
    if urls:
        print(urls.group())

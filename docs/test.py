# 使用正则表达式提取链接

from bs4 import BeautifulSoup

with open("code2.html", "r", encoding="utf-8") as f:
    text = f.read()
    soup = BeautifulSoup(text, 'html.parser')
    # 查找包含“Deliver my email”文本的 <a> 标签
    a_tag = soup.find('a', string=lambda x: x and 'Deliver my email' in x.strip())
    # 提取链接地址
    if a_tag:
        link = a_tag.get('href')
        print("提取的链接地址get_deliver_link:", link)
    else:
        print("未找到包含'Deliver my email'的<a>标签")

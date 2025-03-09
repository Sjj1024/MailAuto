from requests_html import HTMLSession

# 创建会话
session = HTMLSession()

# 打开动态网页
url = 'https://antispam2.xefi.fr/invitation/?lang=en&id=8131d145-c9a0-44f5-9065-ec151584b6dd&utm_source=DA-en&utm_medium=email&utm_campaign=no-robot&utm_content=onpremise'

r = session.get('https://pythonclock.org')

r.html.render()

res = r.html.search('Python 2.7 will retire in...{}Enable Guido Mode')[0]

# 打印文字内容
print(res)
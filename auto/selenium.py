from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')  # 启用无头模式
chrome_options.add_argument('--disable-gpu')  # 禁用 GPU 加速
chrome_options.add_argument('--no-sandbox')  # 禁用沙盒模式

# 启动浏览器
driver = webdriver.Chrome(options=chrome_options)

# 打开 URL
url = 'https://antispam2.xefi.fr/invitation/?lang=en&id=8131d145-c9a0-44f5-9065-ec151584b6dd&utm_source=DA-en&utm_medium=email&utm_campaign=no-robot&utm_content=onpremise'
driver.get(url)

# 提取页面中的所有文字内容
text_content = driver.find_element('tag name', 'body').text

# 打印文字内容
print(text_content)

# 关闭浏览器
driver.quit()

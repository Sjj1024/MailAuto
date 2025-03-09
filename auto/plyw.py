from playwright.sync_api import sync_playwright

url = "https://antispam2.xefi.fr/invitation/?lang=en&id=8131d145-c9a0-44f5-9065-ec151584b6dd&utm_source=DA-en&utm_medium=email&utm_campaign=no-robot&utm_content=onpremise"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle")  # 等待页面加载完成
    text = page.content()  # 获取整个 HTML
    print(text)
    browser.close()

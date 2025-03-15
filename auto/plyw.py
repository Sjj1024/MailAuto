import time

from playwright.sync_api import sync_playwright

url = "https://antispam2.xefi.fr/invitation/?lang=en&id=8131d145-c9a0-44f5-9065-ec151584b6dd&utm_source=DA-en&utm_medium=email&utm_campaign=no-robot&utm_content=onpremise"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url, wait_until="networkidle")  # 等待页面加载完成
    text = page.content()  # 获取整个 HTML
    element = page.query_selector('div.msg-confirmation-container')
    if element:
        print("元素存在，说明已经发送过来")
        # 获取文本内容
        msg_container = page.locator('div.msg-container')
        text_content = msg_container.inner_text()
        print("文本内容:", text_content)
    else:
        print("元素不存在，说明需要验证码")
        # print(text)
        # 文本输入框输入success
        page.fill("input[name='word']", "success")
        # 点击提交按钮
        page.click("a[id='capcha-submit']")
        # 等待新内容加载完成
        page.wait_for_selector('div.msg-confirmation-container')
        # 获取变化后的网页内容
        content = page.content()
        print(content)

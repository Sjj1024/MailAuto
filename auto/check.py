import base64
import datetime
import json
import imaplib
import email
import os
import re
import time
from email.header import decode_header
import smtplib
from email.utils import make_msgid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import format_datetime
from email.header import Header
from openai import OpenAI
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


class MailCheck:
    def __init__(self):
        print("initializing mail control")
        self.config = None
        self.mail = None
        self.server = None
        self.link_count = 0
        self.code_count = 0
        self.aiclient = None
        self.current_email_id = 0
        self.init_env()
        self.init_mail()

    def init_mail(self):
        print("initializing mail")
        with open('config.json') as f:
            config = json.load(f)
            replay_ids = config.get("REPLAY_IDS", None)
            if replay_ids is None:
                config["REPLAY_IDS"] = []
            print("读取配置文件成功", config)
            # imap mail
            self.mail = imaplib.IMAP4_SSL(config.get("IMAP_SERVER"), 993)
            self.mail.login(config.get("EMAIL_ACCOUNT"), config.get("EMAIL_PASSWORD"))
            # smtp server
            self.server = smtplib.SMTP_SSL(config.get("SMTP_SERVER"), 465)  # 使用SSL加密
            self.server.login(config.get("EMAIL_ACCOUNT"), config.get("EMAIL_PASSWORD"))
            self.config = config
        print("mail initialized")
        # 移除代理
        proxies = {}
        self.aiclient = OpenAI(
            # 此为默认路径，您可根据业务所在地域进行配置
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
            api_key=config.get("AI_TOKEN", None),
        )

    def init_env(self):
        print("initializing env")
        # 检查是否存在imgs目录，不存在就创建
        if not os.path.exists("imgs"):
            os.makedirs("imgs")

    # 保存图片到imgs目录
    def save_img(self, filename, img):
        image_data = base64.b64decode(img)
        with open(f"imgs/{filename}.png", "wb") as f:
            f.write(image_data)
        print(f"{filename}.png存储完成")

    def send_email(self, email_id, to_email_str, subject, new_body, in_reply_to, is_text, new_references):
        print("sending mail to", to_email_str)
        # 创建邮件对象
        msg = MIMEText(new_body, "plain", "utf-8") if is_text else MIMEMultipart()
        # msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        # 设置发件人的显示名称和邮箱
        if self.config.get("EMAIL_NAME"):
            msg["From"] = f"""{self.config.get("EMAIL_NAME")} <{self.config.get("EMAIL_ACCOUNT")}>"""
        else:
            msg["From"] = self.config.get("EMAIL_ACCOUNT")
        # msg["To"] = to_email
        to_name, to_email = self.split_name_mail(to_email_str)
        print(f"Name: {to_name}")
        print(f"Email: {to_email}")
        receiver = f"{Header(to_name, 'utf-8').encode()} <{to_email}>" if to_name else to_email_str
        msg["To"] = receiver
        # 发件人名字
        msg["Subject"] = subject
        msg["Date"] = format_datetime(datetime.datetime.utcnow())
        msg["In-Reply-To"] = in_reply_to  # 关联原邮件
        # 9B4833CE-DF1B-495F-BB27-8C64B8508D0A@beidoufeng.com
        msg_id = make_msgid("", self.config.get("EMAIL_ACCOUNT").split("@")[1])
        # 去掉最后的点
        new_msg_id = re.sub(r'\.(?=[^@]*@)', '', msg_id)
        msg["Message-ID"] = new_msg_id
        msg["References"] = new_references  # 维护邮件线程
        # 添加邮件正文
        if not is_text:
            msg.attach(MIMEText(new_body, "plain" if is_text else "html", "utf-8"))
        # 连接 SMTP 服务器并发送邮件
        self.server.sendmail(self.config.get("EMAIL_ACCOUNT"), to_email_str, msg.as_string())
        # server.quit()
        # self.config.get("REPLAY_IDS", []).append(message_id)
        # 将邮件追加到已发送邮件
        self.mail.append('Sent', "\\Seen", None, msg.as_bytes())
        print(f"{email_id} 邮件回复成功！")

    def get_code(self, img):
        print("用豆包api识别图片中的文字")
        # 拼接data:image/png;base64,
        base64_img = "data:image/png;base64," + img
        response = self.aiclient.chat.completions.create(
            # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
            model="doubao-1-5-vision-pro-32k-250115",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text",
                         "text": "请返回这个图片中彩色的单词给我，不要返回其他的内容，如果有两个单词，用空格分开，如果没有，返回空字符串"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": base64_img
                            },
                        },
                    ],
                }
            ],
        )
        code = response.choices[0].message.content
        print(f"{self.current_email_id}图片验证码内容是: {code}")
        # 带有空格说明识别到两个单词，如果是空字符串，说明没有识别到单词
        if " " in code:
            return "retry"
        elif code == "":
            return "retry"
        else:
            return code

    def get_code_img(self, link):
        print("playwright网页中提取验证码图片...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # 等待页面加载完成
            page.goto(link, wait_until="networkidle")
            text = page.content()  # 获取整个 HTML
            # print("code html:", text)
            browser.close()
            pattern = r'<img[^>]*src="(data:image/[^;]+;base64,[^"]+)"[^>]*>'
            # 使用 re.search() 函数在文本中查找第一个匹配的链接地址
            match = re.search(pattern, text)
            if match:
                img = match.group(1)
                print("base64 img:", img)
                # 去掉base64的前缀
                img = img.split(",")[1]
                print("img data:", img)
                code = self.get_code(img)
                if code == "retry":
                    print("验证码识别失败，重试")
                    return False
                else:
                    print("验证码识别成功，回复邮件")
                    self.save_img(f"{self.current_email_id}_{code}", img)
                    return True
            else:
                print("未找到匹配的链接地址")
                return False

    def reply_code(self, code):
        print("回复识别到的文字内容")

    def click_reply(self, link):
        print("点击回复邮件链接", link)
        headers = {
            'sec-ch-ua-platform': '"macOS"',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            'Content-Type': 'application/json',
            'sec-ch-ua-mobile': '?0'
        }
        response = requests.request("GET", link, headers=headers)
        print("click reply response:", response)

    def get_click_link(self, html):
        # 定义正则表达式模式，用于匹配以 http 开头的链接地址
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        # 使用 re.search() 函数在文本中查找第一个匹配的链接地址
        match = re.search(pattern, html)
        # 如果找到匹配的链接地址，则返回该地址；否则返回 None
        if match:
            link = match.group(0)
            print("get_click_link:", link)
            return link
        return None

    def get_deliver_link(self, html):
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        # 查找包含“Deliver my email”文本的<a>标签
        a_tag = soup.find('a', class_='button_link')
        # 提取链接地址
        if a_tag:
            link = a_tag.get('href')
            print("提取的链接地址get_deliver_link:", link)
            return link
        else:
            print("未找到包含'Deliver my email'的<a>标签")
            return ""

    def check_reply(self, html_body):
        # print("检查并处理回复邮件", html_body)
        # 判断邮件类型
        if "button_link" in html_body:
            self.code_count += 1
            print("处理Deliver邮件", self.code_count)
            # 提取链接
            link = self.get_deliver_link(html_body)
            # 获取验证码
            if link:
                for i in range(3):
                    print(f"尝试第{i + 1}次获取验证码")
                    result = self.get_code_img(link)
                    if result:
                        break
                    else:
                        time.sleep(5)
            else:
                print("没有提取到按钮链接")
        else:
            self.link_count += 1
            print("处理链接", self.link_count)
            link = self.get_click_link(html_body)
            if link:
                self.click_reply(link)

    def rewrite_email(self, delivery_time, from_email, text_body, html_body: str):
        # print(f"Rewriting email body: {text_body}")
        print(f"Source text_body: {text_body}")
        print(f"Source html_body: {html_body}")
        if html_body and "<html" in html_body:
            print("处理html逻辑")
            # 获取邮件第一行内容
            # 使用正则表达式匹配 HTML 中的文本内容
            # 去掉 HTML 标签
            text_lines = [line for line in re.sub(r'<.*?>', '\r', html_body).split("\r") if line.strip()]
            first_line = text_lines[0] if text_lines else ""
            # 插入自定义内容
            first_html_line = f"<div>{first_line}</div><br>"
            custom_lines = self.config.get("CUSTOM_BODY", "").replace("\n", "<br>")
            custom_body = f"<div>{custom_lines}</div>"
            first_and_custom = first_html_line + custom_body + "<br>"
            body_tags = re.findall(r'<body[^>]*>', html_body, re.DOTALL)[0]
            body_header = re.split(r'</?body[^>]*>', html_body)[0]
            body_ender = re.split(r'</?body[^>]*>', html_body)[2]
            # 引用的开头要加上时间和收件人On Jan 19, 2025, at 19:17, Song <kent@beidoufeng.com> wrote:
            from_email = from_email.replace("<", "&lt;").replace("<", "&gt;")
            history_header = f"<div>{delivery_time}, {from_email} wrote:</div><br>"
            # 从html_body中提取body部分
            cite_html = re.split(r'</?body[^>]*>', html_body)[1]
            new_body = first_and_custom + f'<blockquote type="cite">{history_header + cite_html}</blockquote>'
            new_html = f"{body_header} {body_tags} {new_body} </body> {body_ender}"
        # 纯文本格式的
        else:
            print("处理纯文本逻辑")
            # 获取邮件第一行内容
            first_line = text_body.split('\n')[0].strip()
            print(f"First line: {first_line}")
            # 插入自定义内容
            first_line = f"{first_line}\r\n\r\n"
            custom_body = [f"{line.strip()}\n" for line in self.config.get("CUSTOM_BODY", "").split("\n")]
            first_and_custom = first_line + ''.join(custom_body) + "\r\n"
            # 引用的开头要加上时间和收件人On Jan 19, 2025, at 19:17, Song <kent@beidoufeng.com> wrote:
            history_header = f"> On {delivery_time}, {from_email} wrote: \n"
            text_body = "".join([f"> {line.lstrip()}\n" for line in text_body.split("\n") if line and line != "> "])
            cite_html = history_header + text_body
            # 重组html内容
            new_html = f"""{first_and_custom}{cite_html}"""
        print(f"Rewritten email body: {new_html}")
        return new_html

    def decode_header(self, header) -> str:
        """解析邮件头"""
        decoded_parts = decode_header(header)
        decoded_header = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_header += part.decode(encoding or "utf-8")
            else:
                decoded_header += part
        return decoded_header

    def split_name_mail(self, name_mail: str):
        if "<" in name_mail:
            name_str, mail_str = name_mail.split("<")
            return name_str.strip(), mail_str.replace(">", "").strip()
        else:
            return None, name_mail

    def sync_email(self):
        print(f"Syncing emails")
        # 选择收件箱（可选择其他文件夹，如 'Sent'）
        self.mail.select("INBOX")
        # self.mail.select("Sent")
        # 检索收件箱所有邮件
        status, messages = self.mail.search(None, "ALL")
        email_ids = messages[0].split()
        print(f"发现 {len(email_ids)} 封标记邮件")
        for (key, email_id) in enumerate(email_ids):
            # 获取邮件数据
            self.current_email_id = key
            print(f"正在处理邮件 {key} : {email_id}...")
            status, msg_data = self.mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])  # 解析邮件
                    # message_id = msg.get("Message-ID")
                    # if message_id in self.config.get("REPLAY_IDS", []):
                    #     continue
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    # 解析From
                    to_email_str = self.decode_header(msg['To'])
                    # to_email = "15670339118@163.com"
                    from_email = self.decode_header(msg['From'])
                    in_reply_to = msg.get("In-Reply-To")
                    original_message_id = msg.get("Message-ID", "").strip()
                    original_references = msg.get("References", "").replace("\r", "")
                    references_format = " ".join([ref.strip() for ref in original_references.split("\n")])
                    # 组装新的 References 字段
                    new_references = f"{references_format} {original_message_id}".strip()
                    delivery_time = msg['Date'].replace(" +0800", "") if msg[
                        'Date'] else datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S').replace("-0000", "")
                    # print(f"邮件主题: {subject}")
                    # print(f"MessageId: {original_message_id}")
                    # print(f"发件人: {from_email}")
                    # print("收件人:", to_email_str)
                    # # 收件时间
                    # print(f"收件时间: {delivery_time}")
                    # 解析邮件正文
                    text_body = None
                    html_body = None
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            # print(f"content_type: {content_type}")
                            if content_type == "text/plain":  # 仅获取纯文本部分
                                text_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                # print(f"邮件正文: {text_body}")
                            if content_type == "text/html":  # 仅获取纯文本部分
                                html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                # print(f"邮件正文: {html_body}")
                            # 检查是否是附件
                            if "attachment" in content_disposition or "inline" in content_disposition:
                                filename = part.get_filename()
                                if filename:
                                    print(f"Attachment: {filename}")
                                    # 你可以选择将附件保存到本地
                                    # with open(filename, 'wb') as f:
                                    #     f.write(part.get_payload(decode=True))
                    else:
                        # 纯文本邮件
                        text_body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        html_body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        # print(f"邮件正文: {html_body}")
                    # 检查邮件
                    try:
                        self.check_reply(html_body)
                    except Exception as e:
                        print(f"Error: {e}")
                    print(f"等待延时：{self.config.get('SLEEP_TIME', 60)} 秒...")
                    time.sleep(self.config.get("SLEEP_TIME", 60))
        # 退出

    def write_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f)

    def run(self):
        print("running mail check")
        try:
            self.sync_email()
            self.mail.logout()
            self.server.quit()
            print("邮件全部处理完成")
        except Exception as e:
            print(f"Error: {e}")
        self.write_config()


if __name__ == '__main__':
    mail = MailCheck()
    mail.run()

import datetime
import json
import imaplib
import email
import re
import time
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import format_datetime


class MailControl:
    def __init__(self):
        print("initializing mail control")
        self.config = None
        self.mail = None
        self.server = None
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

    def send_email(self, email_id, message_id, to_email, subject, new_body, in_reply_to, is_text, new_references):
        print("sending mail to", to_email)
        # 创建邮件对象
        msg = MIMEText(new_body, "plain", "utf-8") if is_text else MIMEMultipart()
        # msg['From'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        # 设置发件人的显示名称和邮箱
        if self.config.get("EMAIL_NAME"):
            msg["From"] = f"""{self.config.get("EMAIL_NAME")} <{self.config.get("EMAIL_ACCOUNT")}>"""
        else:
            msg["From"] = self.config.get("EMAIL_ACCOUNT")
        msg["To"] = to_email
        # 发件人名字
        msg["Subject"] = subject
        msg["Date"] = format_datetime(datetime.datetime.utcnow())
        msg["In-Reply-To"] = in_reply_to  # 关联原邮件
        msg["References"] = new_references  # 维护邮件线程
        # 添加邮件正文
        if not is_text:
            msg.attach(MIMEText(new_body, "plain" if is_text else "html", "utf-8"))
        # 连接 SMTP 服务器并发送邮件
        self.server.sendmail(self.config.get("EMAIL_ACCOUNT"), to_email, msg.as_string())
        # server.quit()
        # self.config.get("REPLAY_IDS", []).append(message_id)
        # 将邮件追加到已发送邮件
        self.mail.append('Sent', "\\Seen", None, msg.as_bytes())
        print(f"{email_id} 邮件回复成功！")

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

    def decode_header(self, header):
        """解析邮件头"""
        decoded_parts = decode_header(header)
        decoded_header = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_header += part.decode(encoding or "utf-8")
            else:
                decoded_header += part
        return decoded_header

    def sync_email(self):
        print(f"Syncing emails")
        # 选择收件箱（可选择其他文件夹，如 'Sent'）
        # mail.select("inbox")
        self.mail.select("Sent")
        # 搜索所有未读邮件
        # status, messages = mail.search(None, "UNSEEN")  # "ALL" 获取所有邮件, "UNSEEN" 获取未读邮件
        status, messages = self.mail.search(None, "FLAGGED")  # "ALL" 获取所有邮件, "UNSEEN" 获取未读邮件
        email_ids = messages[0].split()
        print(f"发现 {len(email_ids)} 封标记邮件")
        for email_id in email_ids:
            # 获取邮件数据
            print(f"正在处理邮件 {email_id}...")
            status, msg_data = self.mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])  # 解析邮件
                    message_id = msg.get("Message-ID")
                    # if message_id in self.config.get("REPLAY_IDS", []):
                    #     continue
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    # 解析From
                    to_email = self.decode_header(msg['To'])
                    # to_email = "15670339118@163.com"
                    from_email = self.decode_header(msg['From'])
                    in_reply_to = msg.get("In-Reply-To")
                    original_message_id = msg["Message-ID"]
                    original_references = msg.get("References", "")
                    # 组装新的 References 字段
                    new_references = f"{original_references}\r\n{original_message_id}".strip()
                    delivery_time = msg['Date'].replace(" +0800", "") if msg[
                        'Date'] else datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S').replace("-0000", "")
                    print(f"邮件主题: {subject}")
                    print(f"发件人: {from_email}")
                    print("收件人:", to_email)
                    # 收件时间
                    print(f"收件时间: {delivery_time}")
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
                    # 回复邮件
                    new_body = self.rewrite_email(delivery_time, from_email, text_body, html_body)
                    is_text = False if html_body and "<html" in html_body else True
                    self.send_email(email_id, message_id, to_email, subject, new_body, in_reply_to, is_text,
                                    new_references)
                    print(f"等待延时：{self.config.get('SLEEP_TIME', 60)} 秒...")
                    time.sleep(self.config.get("SLEEP_TIME", 60))
        # 退出

    def write_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f)

    def run(self):
        print("running mail control")
        try:
            self.sync_email()
            self.mail.logout()
            self.server.quit()
            print("邮件全部处理完成")
        except Exception as e:
            print(f"Error: {e}")
        self.write_config()


if __name__ == '__main__':
    mail = MailControl()
    mail.run()

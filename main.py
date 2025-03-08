import json
import imaplib
import email
import time
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 全局配置
global_config = {
    "IMAP_SERVER": "",
    "SMTP_SERVER": "",
    "EMAIL_ACCOUNT": "",
    "EMAIL_PASSWORD": "",
    "SLEEP_TIME": 60,
    "CUSTOM_BODY": ""
}


def read_config():
    with open('config.json') as f:
        global global_config
        global_config = json.load(f)
        replay_ids = global_config.get("REPLAY_IDS", None)
        if replay_ids is None:
            global_config["REPLAY_IDS"] = []
        print("读取配置文件成功", global_config)
        return global_config


def write_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)


def rewrite_email(text_body, html_body):
    print(f"Rewriting email body: {text_body}")
    print(f"Rewriting email body: {html_body}")
    # 获取邮件第一行内容
    first_line = text_body.split('\n')[0].strip()
    print(f"First line: {first_line}")
    # 插入自定义内容
    first_html_line = f"<div>{first_line}</div>"
    first_and_custom = first_html_line + global_config.get("CUSTOM_BODY", "")
    new_custom_body = f"<body>{first_and_custom}"
    html_body = html_body.replace("<body>", new_custom_body)
    return html_body


def sync_email():
    print(f"Syncing emails")
    try:
        # 连接到 IMAP 服务器
        mail = imaplib.IMAP4_SSL(global_config.get("IMAP_SERVER"), 993)
        mail.login(global_config.get("EMAIL_ACCOUNT"), global_config.get("EMAIL_PASSWORD"))
        # 选择收件箱（可选择其他文件夹，如 'Sent'）
        # mail.select("inbox")
        mail.select("Sent")
        # 搜索所有未读邮件
        # status, messages = mail.search(None, "UNSEEN")  # "ALL" 获取所有邮件, "UNSEEN" 获取未读邮件
        status, messages = mail.search(None, "FLAGGED")  # "ALL" 获取所有邮件, "UNSEEN" 获取未读邮件
        email_ids = messages[0].split()
        print(f"发现 {len(email_ids)} 封标记邮件")
        for email_id in email_ids:
            # 获取邮件数据
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])  # 解析邮件
                    message_id = msg.get("Message-ID")
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    to_email = msg.get("To")
                    in_reply_to = msg.get("In-Reply-To")
                    print(f"邮件主题: {subject}")
                    print(f"发件人: {msg['From']}")
                    print(f"收件人: {to_email}")
                    # 解析邮件正文
                    text_body = None
                    html_body = None
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            print(f"content_type: {content_type}")
                            if content_type == "text/plain":  # 仅获取纯文本部分
                                text_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                print(f"邮件正文: {text_body}")
                            if content_type == "text/html":  # 仅获取纯文本部分
                                html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                print(f"邮件正文: {html_body}")
                    else:
                        text_body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        html_body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        print(f"邮件正文: {html_body}")
                    # 回复邮件
                    new_body = rewrite_email(text_body, html_body)
                    send_email(message_id, to_email, subject, new_body, in_reply_to)
                    time.sleep(global_config.get("SLEEP_TIME", 60))
        # 退出
        mail.logout()
    except Exception as e:
        print("获取邮件失败:", e)


def send_email(message_id, to_email, subject, body, in_reply_to):
    print(f"Sending emails", message_id, to_email, subject, body)
    try:
        # 创建邮件对象
        msg = MIMEMultipart()
        msg["From"] = global_config.get("EMAIL_ACCOUNT")
        # msg["To"] = to_email
        msg["To"] = "15670339118@163.com"
        msg["Subject"] = subject
        msg["In-Reply-To"] = in_reply_to  # 关联原邮件
        # 添加邮件正文
        msg.attach(MIMEText(body, "html"))
        # 连接 SMTP 服务器并发送邮件
        server = smtplib.SMTP_SSL(global_config.get("SMTP_SERVER"), 465)  # 使用SSL加密
        server.login(global_config.get("EMAIL_ACCOUNT"), global_config.get("EMAIL_PASSWORD"))
        server.sendmail(global_config.get("EMAIL_ACCOUNT"), to_email, msg.as_string())
        server.quit()
        global_config.get("REPLAY_IDS", []).append(message_id)
        print("邮件发送成功！")
    except Exception as e:
        print("邮件发送失败:", e)


def save_sent_email(to_email, subject, body):
    """ 发送邮件后，将其存入已发送文件夹 """
    try:
        # 连接 IMAP 服务器
        mail = imaplib.IMAP4_SSL(global_config.get("IMAP_SERVER"), 993)
        mail.login(global_config.get("EMAIL_ACCOUNT"), global_config.get("EMAIL_PASSWORD"))
        mail.select("Sent")  # Gmail "已发送邮件" 文件夹

        # 构建邮件
        msg = MIMEText(body, "plain")
        msg["From"] = global_config.get("EMAIL_ACCOUNT")
        msg["To"] = to_email
        msg["Subject"] = subject

        # 将邮件追加到已发送邮件
        mail.append('Sent', None, None, msg.as_bytes())
        mail.logout()
        print("✅ 邮件已存入已发送文件夹")
    except Exception as e:
        print("❌ 存入已发送邮件失败:", e)


def main():
    print("运行主程序...")
    try:
        read_config()
        sync_email()
    except Exception as e:
        print(f"发生错误: {e}")
        global global_config
        global_config['last_error'] = str(e)
        write_config(global_config)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

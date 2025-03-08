import imaplib
import email
from email.header import decode_header

# 邮箱配置
IMAP_SERVER = "mail.privateemail.com"  # 你的IMAP服务器地址
EMAIL_ACCOUNT = "kent"  # 你的邮箱
EMAIL_PASSWORD = ""  # 你的邮箱密码


def fetch_emails():
    try:
        # 连接到 IMAP 服务器
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, 993)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)

        # 选择收件箱（可选择其他文件夹，如 'Sent'）
        # mail.select("inbox")
        mail.select("Sent")

        # 搜索所有未读邮件
        # status, messages = mail.search(None, "UNSEEN")  # "ALL" 获取所有邮件, "UNSEEN" 获取未读邮件
        status, messages = mail.search(None, "FLAGGED")  # "ALL" 获取所有邮件, "UNSEEN" 获取未读邮件
        email_ids = messages[0].split()

        print(f"发现 {len(email_ids)} 封未读邮件")

        for email_id in email_ids:
            # 获取邮件数据
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])  # 解析邮件
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    print(f"邮件主题: {subject}")
                    print(f"发件人: {msg['From']}")

                    # 解析邮件正文
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            print(f"content_type: {content_type}")
                            if content_type == "text/plain":  # 仅获取纯文本部分
                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                print(f"邮件正文: {body}")
                            if content_type == "text/html":  # 仅获取纯文本部分
                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                print(f"邮件正文: {body}")
                    else:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        print(f"邮件正文: {body}")

        # 退出
        mail.logout()
    except Exception as e:
        print("获取邮件失败:", e)


# 运行邮件接收
fetch_emails()

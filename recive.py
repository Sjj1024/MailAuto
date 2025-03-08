import poplib
import email
from email.parser import Parser

# 邮箱配置
POP3_SERVER = "mail.privateemail.com"  # 你的POP3服务器地址
EMAIL_ACCOUNT = "kent@.com"  # 你的邮箱
EMAIL_PASSWORD = ""  # 你的邮箱密码


def fetch_emails():
    try:
        # 连接到POP3服务器
        server = poplib.POP3_SSL(POP3_SERVER, 995)  # 使用SSL连接
        server.user(EMAIL_ACCOUNT)
        server.pass_(EMAIL_PASSWORD)

        # 获取邮件列表
        email_count, total_size = server.stat()
        print(f"邮箱中有 {email_count} 封邮件，总大小 {total_size} 字节")

        # 只获取最新的一封邮件
        if email_count > 0:
            response, lines, octets = server.retr(email_count)  # 获取最新一封邮件
            msg_content = b"\r\n".join(lines).decode("utf-8")  # 解析邮件内容
            msg = Parser().parsestr(msg_content)

            # 解析邮件内容
            print("From:", msg["From"])
            print("To:", msg["To"])
            print("Subject:", msg["Subject"])

            # 解析邮件正文
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":  # 只获取纯文本部分
                        print("Body:", part.get_payload(decode=True).decode("utf-8"))
            else:
                print("Body:", msg.get_payload(decode=True).decode("utf-8"))

        # 断开连接
        server.quit()
    except Exception as e:
        print("获取邮件失败:", e)


# 调用函数获取邮件
fetch_emails()

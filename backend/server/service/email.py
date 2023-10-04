import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, to_email):
    # Email settings
    SMTP_SERVER = 'smtp.qq.com'  # 如：'smtp.gmail.com'
    SMTP_PORT = 587  # 通常是587，但根据你的邮件提供商可能会不同
    SMTP_USERNAME = '513909280@qq.com'
    # 授权码
    SMTP_PASSWORD = 'zrgnnzrsypnycagb'
    FROM_EMAIL = 'victor.sl@foxmail.com'

    # 创建消息
    msg = MIMEText(body)
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    # 建立连接并发送邮件
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.close()
        print("Successfully sent email")
    except Exception as e:
        print(f"Failed to send email: {e}")
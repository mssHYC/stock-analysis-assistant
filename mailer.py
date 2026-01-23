import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import config
import datetime

def send_email(subject: str, content: str):
    """
    发送邮件
    
    Args:
        subject: 邮件主题
        content: 邮件正文
    """
    if config.SMTP_USER == "your_email@example.com":
        print("错误: 未配置邮箱。请在 config.py 中设置。")
        return

    # 获取接收者列表，兼容旧配置
    to_emails = getattr(config, 'TO_EMAILS', [config.TO_EMAIL])
    
    # 创建邮件对象
    message = MIMEMultipart()
    # 修正 From 头，使用 formataddr 并正确编码昵称
    nickname = "股票分析助手"
    message['From'] = formataddr((str(Header(nickname, 'utf-8')), config.SMTP_USER))
    
    # 设置 To 头 (多个收件人时，显示为逗号分隔的字符串)
    # 注意：直接使用 join，不要用 Header 包装整个列表，否则逗号可能被编码导致发送失败
    if len(to_emails) > 1:
        message['To'] = ",".join(to_emails)
    else:
        message['To'] = to_emails[0]
        
    message['Subject'] = Header(subject, 'utf-8')

    # 邮件正文
    # 如果 content 包含 HTML 标签（简单判断），则发送 HTML 邮件，否则发送纯文本
    if "<html>" in content or "</div>" in content or "<p>" in content:
        message.attach(MIMEText(content, 'html', 'utf-8'))
    else:
        message.attach(MIMEText(content, 'plain', 'utf-8'))

    try:
        # 根据端口选择连接方式
        if config.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT)
        else:
            server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
            server.starttls()  # 启用 TLS

        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        
        # 批量发送
        # 注意：sendmail 的第二个参数接受一个列表，表示所有接收者
        server.sendmail(config.SMTP_USER, to_emails, message.as_string())
        
        server.quit()
        print(f"[{datetime.datetime.now()}] 邮件已发送给: {to_emails}")
        
    except Exception as e:
        print(f"[{datetime.datetime.now()}] 邮件发送失败: {str(e)}")

if __name__ == "__main__":
    # 测试代码
    send_email("测试邮件", "这是一封来自股票分析助手的测试邮件。")

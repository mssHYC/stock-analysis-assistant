import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import config

def test_connection():
    print("=== 开始邮件连接测试 ===")
    print(f"服务器: {config.SMTP_SERVER}")
    print(f"端口: {config.SMTP_PORT}")
    print(f"用户: {config.SMTP_USER}")
    
    # 检查密码是否已设置
    if config.SMTP_PASSWORD == "your_qq_email_auth_code":
        print("\n[!] 警告: 检测到 SMTP_PASSWORD 仍然是默认值！")
        print("请打开 config.py 文件，将 SMTP_PASSWORD 修改为你的 QQ 邮箱授权码。")
        print("授权码获取方式: QQ邮箱网页版 -> 设置 -> 账户 -> POP3/IMAP/SMTP... -> 生成授权码")
        return

    try:
        if config.SMTP_PORT == 465:
            print("正在建立 SSL 连接...")
            server = smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, timeout=10)
        else:
            print("正在建立普通连接 (将升级为 TLS)...")
            server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT, timeout=10)
            server.set_debuglevel(1) # 开启调试输出
            server.starttls()

        print("连接建立成功，正在尝试登录...")
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        print("登录成功！")
        
        # 发送测试邮件
        msg = MIMEText('这是一封测试邮件，用于验证配置是否正确。', 'plain', 'utf-8')
        msg['Subject'] = Header('配置测试邮件', 'utf-8')
        # 修正 From 头
        nickname = "股票分析测试"
        msg['From'] = formataddr((str(Header(nickname, 'utf-8')), config.SMTP_USER))
        
        # 支持多个收件人
        to_emails = getattr(config, 'TO_EMAILS', [config.TO_EMAIL])
        msg['To'] = ",".join(to_emails)
        
        print(f"构造的 From 头: {msg['From']}")
        print(f"构造的 To 头: {msg['To']}")
        
        server.sendmail(config.SMTP_USER, to_emails, msg.as_string())
        print("测试邮件发送成功！")
        server.quit()
        
    except smtplib.SMTPAuthenticationError:
        print("\n[X] 认证失败！通常是以下原因：")
        print("1. 授权码错误（不要使用 QQ 登录密码）")
        print("2. 账户未开启 SMTP 服务")
    except Exception as e:
        print(f"\n[X] 发生错误: {str(e)}")
        # 建议尝试 587 端口
        if config.SMTP_PORT == 465:
            print("\n建议: 尝试在 config.py 中将端口改为 587 再次测试。")

if __name__ == "__main__":
    test_connection()

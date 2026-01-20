# DeepSeek API 配置
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 邮件配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465  # QQ邮箱使用 SSL
SMTP_USER = "your_email@qq.com"
SMTP_PASSWORD = "your_email_auth_code"  # 请注意：这里需要填入QQ邮箱的授权码，而不是QQ密码

# 接收邮箱列表，支持多个邮箱
TO_EMAILS = ["receive1@example.com", "receive2@example.com"] 
# 保持兼容性
TO_EMAIL = "receive1@example.com"

# 股票配置
# 示例：600519 (贵州茅台), 000001 (平安银行)
STOCK_SYMBOLS = ["600519", "000001"] 

# 大盘指数配置
# 000001: 上证指数, 399001: 深证成指, 000300: 沪深300, 399006: 创业板指
MARKET_INDEXES = ["000001", "399001", "000300", "399006"] 

# 定时任务配置
SCHEDULE_TIME = "18:00"

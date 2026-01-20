# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-f46f26e69688439886b245dcaf55026e"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"  # 或者是 DeepSeek 提供的具体 Base URL

# 邮件配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465  # QQ邮箱使用 SSL
SMTP_USER = "793010926@qq.com"
SMTP_PASSWORD = "zbkrtmfrmkswbeia"  # 请注意：这里需要填入QQ邮箱的授权码，而不是QQ密码
# 接收邮箱列表，支持多个邮箱
TO_EMAILS = ["793010926@qq.com", "1149224291@qq.com", "664137712@qq.com"] 
# 保持兼容性，虽然下面这个变量可能不再被主要逻辑使用，但为了防止报错暂时保留，建议后续清理
TO_EMAIL = "793010926@qq.com"

# 股票配置
# 示例：600519 (贵州茅台), 000001 (平安银行)
STOCK_SYMBOLS = ["600415", "600839"] 

# 大盘指数配置
# 000001: 上证指数, 399001: 深证成指, 000300: 沪深300, 399006: 创业板指
MARKET_INDEXES = ["000001", "399001", "000300", "399006"] 

# 定时任务配置
SCHEDULE_TIME = "18:00"

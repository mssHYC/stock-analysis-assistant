import schedule
import time
import datetime
import argparse
import sys
import markdown
import os

import config
from data_fetcher import fetch_stock_data, fetch_market_index_data, fetch_financial_news
from analyzer import analyze_stock, analyze_market, extract_stock_codes
from analyzer_gemini import analyze_stock as analyze_stock_gemini, analyze_market as analyze_market_gemini, extract_stock_codes as extract_stock_codes_gemini
from mailer import send_email

# 确保日志目录存在
LOG_DIR = "/app/logs"
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except:
        pass # 如果无法创建（例如非容器环境），则忽略

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    # 简单的文件日志记录
    try:
        with open(f"{LOG_DIR}/app.log", "a") as f:
            f.write(formatted_message + "\n")
    except:
        pass

def run_analysis_job(analyze_market_func, extract_stock_codes_func, analyze_stock_func, model_name):
    log(f"开始执行定时任务 ({model_name})...")
    
    # 初始化 Markdown 报告
    md_report = f"# 宏观市场与股票分析日报 ({datetime.date.today()})\n\n"
    md_report += "---\n\n"

    # --- 1. 宏观大盘分析 ---
    log("正在获取大盘数据和市场概况...")
    try:
        # 获取大盘指数数据
        market_data_map = fetch_market_index_data(config.MARKET_INDEXES)
        market_data_str = ""
        for symbol, data in market_data_map.items():
            market_data_str += f"{data}\n"
            
        # 获取市场概况/新闻
        news_str = fetch_financial_news()
        
        # 调用 AI 分析宏观
        log("正在进行宏观大盘分析...")
        macro_analysis = analyze_market_func(market_data_str, news_str)
        
        # 提取 AI 推荐的股票代码并添加到待分析列表
        recommended_stocks = extract_stock_codes_func(macro_analysis)
        if recommended_stocks:
            log(f"AI 推荐关注股票: {recommended_stocks}")
            for code in recommended_stocks:
                if code not in config.STOCK_SYMBOLS:
                    config.STOCK_SYMBOLS.append(code)
            log(f"当前待分析股票列表: {config.STOCK_SYMBOLS}")        
        md_report += "## 🌏 宏观策略报告\n\n"
        md_report += macro_analysis + "\n\n"
        md_report += "---\n\n"
        
    except Exception as e:
        log(f"宏观分析出错: {e}")
        md_report += f"## 宏观分析出错\n{str(e)}\n\n"

    # --- 2. 个股分析 ---
    log("正在获取个股数据...")
    stock_data_map = fetch_stock_data(config.STOCK_SYMBOLS)
    
    if stock_data_map:
        log("正在分析个股数据...")
        for symbol, data_str in stock_data_map.items():
            log(f"正在分析 {symbol} ...")
            
            # 如果数据获取出错，直接添加到报告
            if "错误" in data_str or "无法获取" in data_str:
                 analysis_result = data_str
            else:
                analysis_result = analyze_stock_func(data_str)
                
            md_report += f"## 📊 {symbol} 个股分析\n\n"
            if analysis_result:
                md_report += analysis_result + "\n\n"
            else:
                md_report += "分析失败: 未能获取分析结果。\n\n"
            md_report += "---\n\n"
    else:
        log("未配置个股或获取失败，跳过个股分析。")

    # 3. 转换为 HTML
    html_report = markdown.markdown(md_report, extensions=['tables', 'fenced_code'])
    
    # 添加简单的 CSS 样式，让邮件更好看
    html_style = """
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        h1 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        p { margin-bottom: 15px; }
        strong { color: #e74c3c; }
        ul { margin-bottom: 15px; }
        li { margin-bottom: 5px; }
    </style>
    """
    final_html = f"<html><head>{html_style}</head><body>{html_report}</body></html>"

    # 4. 发送邮件
    log("正在发送邮件...")
    subject = f"每日股票分析报告（{model_name}） - {datetime.date.today()}"
    send_email(subject, final_html)
    
    log("任务执行完毕！")

def job():
    run_analysis_job(analyze_market, extract_stock_codes, analyze_stock, "DeepSeek")

def job_gemini():
    run_analysis_job(analyze_market_gemini, extract_stock_codes_gemini, analyze_stock_gemini, "Gemini")

def main():
    parser = argparse.ArgumentParser(description="股票分析助手")
    parser.add_argument("--now", action="store_true", help="立即运行一次任务")
    args = parser.parse_args()

    if args.now:
        job()
        job_gemini()
        return

    # 设置定时任务
    log(f"股票分析助手已启动。将在每天 {config.SCHEDULE_TIME} 运行。")
    print("按 Ctrl+C 退出程序。")
    
    schedule.every().day.at(config.SCHEDULE_TIME).do(job)

    while True:
        try:
            schedule.run_pending()
            time.sleep(60) # 每分钟检查一次
        except KeyboardInterrupt:
            print("\n程序已退出。")
            sys.exit(0)
        except Exception as e:
            log(f"发生错误: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()


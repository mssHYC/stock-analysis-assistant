import schedule
import time
import datetime
import argparse
import sys
import markdown

import config
from data_fetcher import fetch_stock_data, fetch_market_index_data, fetch_financial_news
from analyzer import analyze_stock, analyze_market
from mailer import send_email

def job():
    print(f"[{datetime.datetime.now()}] 开始执行定时任务...")
    
    # 初始化 Markdown 报告
    md_report = f"# 宏观市场与股票分析日报 ({datetime.date.today()})\n\n"
    md_report += "---\n\n"

    # --- 1. 宏观大盘分析 ---
    print("正在获取大盘数据和市场概况...")
    try:
        # 获取大盘指数数据
        market_data_map = fetch_market_index_data(config.MARKET_INDEXES)
        market_data_str = ""
        for symbol, data in market_data_map.items():
            market_data_str += f"{data}\n"
            
        # 获取市场概况/新闻
        news_str = fetch_financial_news()
        
        # 调用 AI 分析宏观
        print("正在进行宏观大盘分析...")
        macro_analysis = analyze_market(market_data_str, news_str)
        
        md_report += "## 🌏 宏观策略报告\n\n"
        md_report += macro_analysis + "\n\n"
        md_report += "---\n\n"
        
    except Exception as e:
        print(f"宏观分析出错: {e}")
        md_report += f"## 宏观分析出错\n{str(e)}\n\n"

    # --- 2. 个股分析 ---
    print("正在获取个股数据...")
    stock_data_map = fetch_stock_data(config.STOCK_SYMBOLS)
    
    if stock_data_map:
        print("正在分析个股数据...")
        for symbol, data_str in stock_data_map.items():
            print(f"正在分析 {symbol} ...")
            
            # 如果数据获取出错，直接添加到报告
            if "错误" in data_str or "无法获取" in data_str:
                 analysis_result = data_str
            else:
                analysis_result = analyze_stock(data_str)
                
            md_report += f"## 📊 {symbol} 个股分析\n\n"
            md_report += analysis_result + "\n\n"
            md_report += "---\n\n"
    else:
        print("未配置个股或获取失败，跳过个股分析。")

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
    print("正在发送邮件...")
    subject = f"每日股票分析报告 - {datetime.date.today()}"
    send_email(subject, final_html)
    
    print(f"[{datetime.datetime.now()}] 任务执行完毕！")

def main():
    parser = argparse.ArgumentParser(description="股票分析助手")
    parser.add_argument("--now", action="store_true", help="立即运行一次任务")
    args = parser.parse_args()

    if args.now:
        job()
        return

    # 设置定时任务
    print(f"股票分析助手已启动。将在每天 {config.SCHEDULE_TIME} 运行。")
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
            print(f"发生错误: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()

import efinance as ef
import pandas as pd
from typing import Dict, Any, List

def fetch_stock_data(symbols: list) -> Dict[str, Any]:
    """
    获取股票数据 (使用 efinance 库获取东方财富数据)
    
    Args:
        symbols: 股票代码列表 (如 "600519", "000001")
        
    Returns:
        Dict: 包含每个股票的数据字典
    """
    stock_data = {}
    
    for symbol in symbols:
        try:
            # 获取历史 K 线数据
            # klt=101: 日线
            df = ef.stock.get_quote_history(symbol, klt=101)
            
            if df is not None and not df.empty:
                # 计算均线
                df['MA5'] = df['收盘'].rolling(window=5).mean()
                df['MA10'] = df['收盘'].rolling(window=10).mean()
                df['MA20'] = df['收盘'].rolling(window=20).mean()
                df['MA60'] = df['收盘'].rolling(window=60).mean()
                
                # 获取最近 5 天的数据
                hist = df.tail(5)
                
                # 获取基本信息
                stock_name = hist['股票名称'].iloc[0]
                
                # 构造详细的技术面数据字符串
                data_str = f"股票名称: {stock_name} ({symbol})\n"
                data_str += "【近期行情】 (Date, Open, High, Low, Close, Volume, MA5, MA20):\n"
                
                for _, row in hist.iterrows():
                    date_str = row['日期']
                    data_str += f"{date_str}: C={row['收盘']:.2f}, V={row['成交量']}, MA5={row['MA5']:.2f}, MA20={row['MA20']:.2f}\n"
                
                # 关键指标分析
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                
                # 涨跌幅
                change = latest['涨跌额']
                change_percent = latest['涨跌幅']
                
                # 均线位置
                ma_status = ""
                if latest['收盘'] > latest['MA5'] > latest['MA10'] > latest['MA20']:
                    ma_status = "均线多头排列 (强势)"
                elif latest['收盘'] < latest['MA5'] < latest['MA10'] < latest['MA20']:
                    ma_status = "均线空头排列 (弱势)"
                else:
                    ma_status = "均线纠缠 (震荡)"
                
                # 量能分析
                vol_ma5 = df['成交量'].rolling(window=5).mean().iloc[-1]
                vol_ratio = latest['成交量'] / vol_ma5
                vol_status = "放量" if vol_ratio > 1.2 else ("缩量" if vol_ratio < 0.8 else "平量")
                
                data_str += f"\n【当前状态】\n"
                data_str += f"- 收盘价: {latest['收盘']:.2f} (涨跌: {change_percent:.2f}%)\n"
                data_str += f"- 均线形态: {ma_status}\n"
                data_str += f"- 量能状态: {vol_status} (量比: {vol_ratio:.2f})\n"
                data_str += f"- MA位置: MA5={latest['MA5']:.2f}, MA20={latest['MA20']:.2f}, MA60={latest['MA60']:.2f}\n"
                
                stock_data[symbol] = data_str
            else:
                stock_data[symbol] = f"无法获取 {symbol} 的数据 (可能代码错误或停牌)"
                
        except Exception as e:
            stock_data[symbol] = f"获取 {symbol} 数据时出错: {str(e)}"
            
    return stock_data

def fetch_market_index_data(indexes: list) -> Dict[str, Any]:
    """
    获取大盘指数数据
    """
    return fetch_stock_data(indexes) # efinance 的 stock 接口通常也能获取指数

def fetch_financial_news() -> str:
    """
    获取最近的财经新闻
    """
    news_str = ""
    try:
        # 这里演示获取财经要闻，efinance 本身没有直接的新闻接口，我们暂时模拟或寻找替代
        # 实际项目中可以使用 tushare 或其他新闻 API
        # 这里我们使用 efinance 获取一些板块资金流向作为宏观参考
        
        # 1. 获取行业板块资金流向
        bk_flow = ef.stock.get_realtime_quotes('行业板块')
        if bk_flow is not None and not bk_flow.empty:
             # 按涨跌幅排序，取前5和后5
            top_bk = bk_flow.sort_values(by='涨跌幅', ascending=False).head(5)
            bottom_bk = bk_flow.sort_values(by='涨跌幅', ascending=True).head(5)
            
            news_str += "### 今日行业板块表现 (Top 5)\n"
            for _, row in top_bk.iterrows():
                news_str += f"- {row['股票名称']}: {row['涨跌幅']}%, 主力净流入: {row['主力净流入']}\n"
            
            news_str += "\n### 今日行业板块表现 (Bottom 5)\n"
            for _, row in bottom_bk.iterrows():
                news_str += f"- {row['股票名称']}: {row['涨跌幅']}%, 主力净流入: {row['主力净流入']}\n"
                
    except Exception as e:
        news_str += f"获取市场概况时出错: {str(e)}"
        
    return news_str

if __name__ == "__main__":
    # 测试代码
    print("--- 测试大盘指数 ---")
    indexes = ["000001", "399001"] # 上证, 深证
    index_data = fetch_market_index_data(indexes)
    for symbol, info in index_data.items():
        print(info)
        
    print("\n--- 测试市场概况 ---")
    print(fetch_financial_news())

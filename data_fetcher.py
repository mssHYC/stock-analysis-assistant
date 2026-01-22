import akshare as ak
import pandas as pd
import datetime
from typing import Dict, Any, List

def fetch_stock_data(symbols: list) -> Dict[str, Any]:
    """
    获取股票数据 (使用 akshare 库获取数据)
    
    Args:
        symbols: 股票代码列表 (如 "600519", "000001")
        
    Returns:
        Dict: 包含每个股票的数据字典
    """
    stock_data = {}
    
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y%m%d")
    end_date = datetime.datetime.now().strftime("%Y%m%d")

    for symbol in symbols:
        try:
            # 获取历史 K 线数据
            # akshare 接口: stock_zh_a_hist (日频)
            # adjust="qfq" 前复权
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")
            
            if df is not None and not df.empty:
                # 获取股票名称 (尝试获取实时数据以得到名称)
                stock_name = symbol
                try:
                    info = ak.stock_individual_info_em(symbol=symbol)
                    # info is a DF with columns item, value
                    name_row = info[info['item'] == "股票名称"]
                    if not name_row.empty:
                        stock_name = name_row['value'].values[0]
                except:
                    pass

                # 数据处理
                df['收盘'] = pd.to_numeric(df['收盘'])
                df['成交量'] = pd.to_numeric(df['成交量'])
                
                # 计算均线
                df['MA5'] = df['收盘'].rolling(window=5).mean()
                df['MA10'] = df['收盘'].rolling(window=10).mean()
                df['MA20'] = df['收盘'].rolling(window=20).mean()
                df['MA60'] = df['收盘'].rolling(window=60).mean()
                
                # 获取最近 5 天的数据
                hist = df.tail(5)
                
                # 构造详细的技术面数据字符串
                data_str = f"股票名称: {stock_name} ({symbol})\n"
                data_str += "【近期行情】 (Date, Open, High, Low, Close, Volume, MA5, MA20):\n"
                
                for _, row in hist.iterrows():
                    date_str = row['日期']
                    data_str += f"{date_str}: C={row['收盘']:.2f}, V={row['成交量']}, MA5={row['MA5']:.2f}, MA20={row['MA20']:.2f}\n"
                
                # 关键指标分析
                latest = df.iloc[-1]
                
                change_percent = latest['涨跌幅']
                
                # 均线位置
                ma_status = ""
                if not pd.isna(latest['MA5']) and not pd.isna(latest['MA10']) and not pd.isna(latest['MA20']):
                    if latest['收盘'] > latest['MA5'] > latest['MA10'] > latest['MA20']:
                        ma_status = "均线多头排列 (强势)"
                    elif latest['收盘'] < latest['MA5'] < latest['MA10'] < latest['MA20']:
                        ma_status = "均线空头排列 (弱势)"
                    else:
                        ma_status = "均线纠缠 (震荡)"
                else:
                    ma_status = "数据不足计算均线"
                
                # 量能分析
                vol_status = "未知"
                vol_ratio = 0.0
                if not pd.isna(latest['成交量']):
                    vol_ma5 = df['成交量'].rolling(window=5).mean().iloc[-1]
                    if vol_ma5 > 0:
                        vol_ratio = latest['成交量'] / vol_ma5
                        vol_status = "放量" if vol_ratio > 1.2 else ("缩量" if vol_ratio < 0.8 else "平量")
                
                data_str += f"\n【当前状态】\n"
                data_str += f"- 收盘价: {latest['收盘']:.2f} (涨跌: {change_percent:.2f}%)\n"
                data_str += f"- 均线形态: {ma_status}\n"
                data_str += f"- 量能状态: {vol_status} (量比: {vol_ratio:.2f})\n"
                
                # Handle potential NaN in MAs
                ma5_val = f"{latest['MA5']:.2f}" if not pd.isna(latest['MA5']) else "N/A"
                ma20_val = f"{latest['MA20']:.2f}" if not pd.isna(latest['MA20']) else "N/A"
                ma60_val = f"{latest['MA60']:.2f}" if not pd.isna(latest['MA60']) else "N/A"
                
                data_str += f"- MA位置: MA5={ma5_val}, MA20={ma20_val}, MA60={ma60_val}\n"
                
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
    # 映射指数代码到 akshare 格式
    mapped_indexes = []
    index_map = {} 
    
    for idx in indexes:
        if idx.startswith("0"):
            new_idx = "sh" + idx
        elif idx.startswith("3"):
            new_idx = "sz" + idx
        else:
            new_idx = idx
        mapped_indexes.append(new_idx)
        index_map[new_idx] = idx
        
    stock_data = {}
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y%m%d")
    end_date = datetime.datetime.now().strftime("%Y%m%d")
    
    for symbol in mapped_indexes:
        original_symbol = index_map.get(symbol, symbol)
        try:
            # akshare 指数接口: stock_zh_index_daily_em
            df = ak.stock_zh_index_daily_em(symbol=symbol, start_date=start_date, end_date=end_date)
            
            if df is not None and not df.empty:
                # Standardize columns: date, open, close, high, low, volume, amount
                df.rename(columns={'date': '日期', 'close': '收盘', 'volume': '成交量'}, inplace=True)
                
                df['收盘'] = pd.to_numeric(df['收盘'])
                df['成交量'] = pd.to_numeric(df['成交量'])
                
                hist = df.tail(5)
                
                data_str = f"指数代码: {original_symbol} ({symbol})\n"
                data_str += "【近期走势】:\n"
                
                for _, row in hist.iterrows():
                    data_str += f"{row['日期']}: C={row['收盘']:.2f}, V={row['成交量']}\n"
                    
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                change_percent = (latest['收盘'] - prev['收盘']) / prev['收盘'] * 100
                
                data_str += f"今日涨跌: {change_percent:.2f}%\n"
                
                stock_data[original_symbol] = data_str
            else:
                stock_data[original_symbol] = f"无法获取指数 {original_symbol} 数据"
        except Exception as e:
            stock_data[original_symbol] = f"获取指数 {original_symbol} 出错: {str(e)}"
            
    return stock_data

def fetch_financial_news() -> str:
    """
    获取最近的财经新闻 / 行业板块表现
    """
    news_str = ""
    try:
        # 获取行业板块数据
        # stock_board_industry_name_em: 东方财富-行业板块-实时
        bk_flow = ak.stock_board_industry_name_em()
        
        if bk_flow is not None and not bk_flow.empty:
            # 字段: 排名, 板块名称, 最新价, 涨跌幅, 涨跌额, ...
            top_bk = bk_flow.sort_values(by='涨跌幅', ascending=False).head(5)
            bottom_bk = bk_flow.sort_values(by='涨跌幅', ascending=True).head(5)
            
            news_str += "### 今日行业板块表现 (Top 5)\n"
            for _, row in top_bk.iterrows():
                news_str += f"- {row['板块名称']}: {row['涨跌幅']}%\n"
            
            news_str += "\n### 今日行业板块表现 (Bottom 5)\n"
            for _, row in bottom_bk.iterrows():
                news_str += f"- {row['板块名称']}: {row['涨跌幅']}%\n"
                
    except Exception as e:
        news_str += f"获取市场概况时出错: {str(e)}"
        
    return news_str

if __name__ == "__main__":
    print("--- 测试大盘指数 ---")
    indexes = ["000001", "399001"] 
    index_data = fetch_market_index_data(indexes)
    for symbol, info in index_data.items():
        print(info)
        
    print("\n--- 测试个股 ---")
    stock_data = fetch_stock_data(["600519"])
    for symbol, info in stock_data.items():
        print(info)

    print("\n--- 测试市场概况 ---")
    print(fetch_financial_news())

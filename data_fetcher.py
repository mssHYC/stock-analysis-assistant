import akshare as ak
import pandas as pd
import datetime
import os
from typing import Dict, Any, List

def get_sina_symbol(code: str) -> str:
    """
    为股票代码添加 sh/sz 前缀以适配 Sina 接口
    """
    if code.startswith(('60', '68')):
        return f"sh{code}"
    elif code.startswith(('00', '30')):
        return f"sz{code}"
    elif code.startswith(('4', '8')):
        return f"bj{code}"
    else:
        return code

def fetch_sector_map() -> Dict[str, float]:
    """
    获取行业板块涨跌幅数据，用于计算相对强弱
    Returns: {sector_name: change_percent}
    """
    sector_map = {}
    
    # 尝试 1: 新浪行业
    try:
        bk_flow = ak.stock_sector_spot(indicator="新浪行业")
        if bk_flow is not None and not bk_flow.empty:
            col_name = '涨跌幅' if '涨跌幅' in bk_flow.columns else None
            if col_name:
                for _, row in bk_flow.iterrows():
                    sector_map[row['板块']] = float(row[col_name])
    except:
        pass
        
    # 尝试 2: 同花顺行业 (总是尝试获取，以补充新浪数据的不足)
    try:
        bk_ths = ak.stock_board_industry_summary_ths()
        if bk_ths is not None and not bk_ths.empty:
             for _, row in bk_ths.iterrows():
                 # THS usually has '板块' and '涨跌幅'
                 name = row['板块']
                 val = float(row['涨跌幅'])
                 # 如果新浪没覆盖该板块，则添加
                 if name not in sector_map:
                     sector_map[name] = val
    except:
        pass
            
    return sector_map

def fetch_stock_data(symbols: list) -> Dict[str, Any]:
    """
    获取股票数据 (使用 akshare 库获取数据，切换为 Sina 接口)
    增加：行业、估值(PE/PB)、基本面(ROE)、同业相对强弱
    
    Args:
        symbols: 股票代码列表 (如 "600519", "000001")
        
    Returns:
        Dict: 包含每个股票的数据字典
    """
    stock_data = {}
    
    # 提前获取行业板块数据，用于后续查找
    sector_map = fetch_sector_map()
    
    now = datetime.datetime.now()
    # 如果是周末，使用周五的日期
    if now.weekday() == 5:  # 周六
        now = now - datetime.timedelta(days=1)
    elif now.weekday() == 6:  # 周日
        now = now - datetime.timedelta(days=2)

    start_date = (now - datetime.timedelta(days=365)).strftime("%Y%m%d")
    end_date = now.strftime("%Y%m%d")

    for symbol in symbols:
        try:
            # --- 1. 获取历史 K 线数据 (Sina) ---
            sina_symbol = get_sina_symbol(symbol)
            df = ak.stock_zh_a_daily(symbol=sina_symbol, start_date=start_date, end_date=end_date)
            
            if df is not None and not df.empty:
                # 基础信息变量
                stock_name = symbol
                industry = "未知"
                total_mv = "未知"
                pe_ttm = "未知"
                pb = "未知"
                roe = "未知"
                relative_strength_msg = "无法计算 (行业数据缺失)"
                
                # --- 2. 获取个股基本信息 (行业、市值) ---
                try:
                    info_df = ak.stock_individual_info_em(symbol=symbol)
                    if not info_df.empty:
                        # item, value
                        info_dict = dict(zip(info_df['item'], info_df['value']))
                        stock_name = info_dict.get('股票简称', symbol)
                        industry = info_dict.get('行业', '未知')
                        mv = info_dict.get('总市值', 0)
                        if isinstance(mv, (int, float)) and mv > 0:
                            total_mv = f"{mv / 100000000:.2f}亿"
                except:
                    pass

                # --- 3. 获取估值数据 (PE-TTM, PB) ---
                try:
                    # 使用百度估值接口 (返回历史序列，取最新)
                    # 注意：该接口可能稍慢
                    val_pe = ak.stock_zh_valuation_baidu(symbol=symbol, indicator="市盈率(TTM)")
                    if not val_pe.empty:
                        pe_ttm = val_pe.iloc[-1]['value']
                    
                    val_pb = ak.stock_zh_valuation_baidu(symbol=symbol, indicator="市净率")
                    if not val_pb.empty:
                        pb = val_pb.iloc[-1]['value']
                except:
                    pass
                
                # --- 4. 获取财务指标 (ROE) ---
                try:
                    fin_df = ak.stock_financial_abstract(symbol=symbol)
                    # 查找 ROE
                    if not fin_df.empty:
                        # 尝试找到 "净资产收益率" 相关行
                        roe_row = fin_df[fin_df['指标'].str.contains('净资产收益率', na=False)]
                        if not roe_row.empty:
                            # 取最近一期的数据 (列名通常是日期，且降序排列或第一列之后)
                            # 列结构: 选项, 指标, date1, date2...
                            # 假设第3列开始是最近的日期
                            if len(roe_row.columns) > 2:
                                # 取第一个日期列的值
                                val = roe_row.iloc[0, 2]
                                date_col = roe_row.columns[2]
                                roe = f"{val}% ({date_col})"
                except:
                    pass

                # 数据处理: Sina 返回 columns: date, open, high, low, close, volume...
                df.rename(columns={'date': '日期', 'close': '收盘', 'volume': '成交量'}, inplace=True)
                df['收盘'] = pd.to_numeric(df['收盘'])
                df['成交量'] = pd.to_numeric(df['成交量'])
                
                # 计算均线
                df['MA5'] = df['收盘'].rolling(window=5).mean()
                df['MA10'] = df['收盘'].rolling(window=10).mean()
                df['MA20'] = df['收盘'].rolling(window=20).mean()
                df['MA60'] = df['收盘'].rolling(window=60).mean()
                
                hist = df.tail(5)
                
                # 关键指标分析
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                change_percent = (latest['收盘'] - prev['收盘']) / prev['收盘'] * 100
                
                # --- 5. 计算同业相对强弱 ---
                matched_sector_name = None
                matched_sector_change = 0.0
                
                # 1. 精确匹配
                if industry in sector_map:
                    matched_sector_name = industry
                    matched_sector_change = sector_map[industry]
                
                # 2. 模糊匹配 (如果精确匹配失败)
                if matched_sector_name is None:
                    # 尝试去除 "行业" 后缀 (e.g., "酿酒行业" -> "酿酒")
                    simple_name = industry.replace("行业", "")
                    if simple_name in sector_map:
                         matched_sector_name = simple_name
                         matched_sector_change = sector_map[simple_name]
                    else:
                        # 尝试包含匹配
                        for s_name in sector_map:
                            # 避免过于宽泛的匹配 (如 "车" 匹配 "汽车")，要求至少2个字且包含
                            if len(s_name) >= 2 and len(industry) >= 2:
                                if industry in s_name or s_name in industry:
                                    matched_sector_name = s_name
                                    matched_sector_change = sector_map[s_name]
                                    break
                
                if matched_sector_name:
                    sector_change = matched_sector_change
                    rel_strength = change_percent - sector_change
                    status = "强于" if rel_strength > 0 else "弱于"
                    # 如果匹配的板块名与原名不同，显示在括号里
                    display_sector = industry
                    if matched_sector_name != industry:
                        display_sector = f"{industry}/{matched_sector_name}"
                        
                    relative_strength_msg = f"个股 {change_percent:.2f}% vs 行业({matched_sector_name}) {sector_change:.2f}% -> {status}板块 {abs(rel_strength):.2f}%"
                else:
                    relative_strength_msg = f"行业({industry}) 数据未找到，无法对比"

                # --- 构造输出 ---
                data_str = f"股票名称: {stock_name} ({symbol})\n"
                data_str += f"【基本面概况】\n"
                data_str += f"- 所属行业: {industry}\n"
                data_str += f"- 总市值: {total_mv}\n"
                data_str += f"- 估值水平: PE(TTM)={pe_ttm}, PB={pb}\n"
                data_str += f"- 财务质量: 最近ROE={roe}\n"
                data_str += f"- 同业相对强弱: {relative_strength_msg}\n\n"
                
                data_str += "【近期行情】 (Date, Open, High, Low, Close, Volume, MA5, MA20):\n"
                
                for _, row in hist.iterrows():
                    date_str = row['日期']
                    data_str += f"{date_str}: C={row['收盘']:.2f}, V={row['成交量']}, MA5={row['MA5']:.2f}, MA20={row['MA20']:.2f}\n"
                
                
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
    获取大盘指数数据 (切换为 Sina 接口)
    """
    # 映射指数代码到 Sina 格式
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
    
    now = datetime.datetime.now()
    # 如果是周末，使用周五的日期
    if now.weekday() == 5:  # 周六
        now = now - datetime.timedelta(days=1)
    elif now.weekday() == 6:  # 周日
        now = now - datetime.timedelta(days=2)

    start_date = (now - datetime.timedelta(days=365)).strftime("%Y%m%d")
    end_date = now.strftime("%Y%m%d")
    print(f"获取大盘指数数据，时间范围：{start_date} 至 {end_date}")
    for symbol in mapped_indexes:
        original_symbol = index_map.get(symbol, symbol)
        try:
            # akshare 指数接口: stock_zh_index_daily (Sina)
            # symbol like sh000001
            df = ak.stock_zh_index_daily(symbol=symbol)
            
            if df is not None and not df.empty:
                # Sina index returns: date, open, high, low, close, volume
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
    获取最近的财经新闻 / 行业板块表现 (切换为 Sina 接口，增加 THS 备选)
    """
    news_str = ""
    found_data = False
    
    # 尝试 1: 新浪行业
    try:
        bk_flow = ak.stock_sector_spot(indicator="新浪行业")
        if bk_flow is not None and not bk_flow.empty:
            col_name = '涨跌幅' if '涨跌幅' in bk_flow.columns else None
            if col_name:
                top_bk = bk_flow.sort_values(by=col_name, ascending=False).head(5)
                bottom_bk = bk_flow.sort_values(by=col_name, ascending=True).head(5)
                
                news_str += "### 今日行业板块表现 (Top 5)\n"
                for _, row in top_bk.iterrows():
                    val = row[col_name]
                    news_str += f"- {row['板块']}: {val}%\n"
                
                news_str += "\n### 今日行业板块表现 (Bottom 5)\n"
                for _, row in bottom_bk.iterrows():
                    val = row[col_name]
                    news_str += f"- {row['板块']}: {val}%\n"
                found_data = True
    except:
        pass
        
    # 尝试 2: 同花顺行业 (如果新浪失败)
    if not found_data:
        try:
            bk_ths = ak.stock_board_industry_summary_ths()
            if bk_ths is not None and not bk_ths.empty:
                # THS columns: 序号, 板块, 涨跌幅, ...
                top_bk = bk_ths.sort_values(by='涨跌幅', ascending=False).head(5)
                bottom_bk = bk_ths.sort_values(by='涨跌幅', ascending=True).head(5)
                
                news_str += "### 今日行业板块表现 (Top 5) [来源:同花顺]\n"
                for _, row in top_bk.iterrows():
                    news_str += f"- {row['板块']}: {row['涨跌幅']}%\n"
                
                news_str += "\n### 今日行业板块表现 (Bottom 5) [来源:同花顺]\n"
                for _, row in bottom_bk.iterrows():
                    news_str += f"- {row['板块']}: {row['涨跌幅']}%\n"
                found_data = True
        except Exception as e:
            news_str += f"获取市场概况备选源出错: {str(e)}"

    if not found_data and not news_str:
        news_str = "无法获取行业板块数据 (API 连接失败)"
        
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

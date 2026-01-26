
import akshare as ak
import pandas as pd
import os


def test_stock_info(symbol="600519"):
    print(f"Testing info for {symbol}...")
    
    # 1. Spot Data (Real-time price, PE, PB, Market Cap)
    print("\n--- Spot Data (stock_zh_a_spot_em) ---")
    try:
        # Note: stock_zh_a_spot_em returns ALL stocks if no symbol provided, 
        # but can filter? No, usually it returns all. 
        # Actually ak.stock_zh_a_spot_em() takes no arguments usually and returns all.
        # But wait, previous code used `ak.stock_zh_a_spot_em(symbol=symbol)`? 
        # Let's check if that works or if we need to filter.
        # The docs say it returns all. The previous code might be inefficient or relying on a parameter I don't see.
        # Let's try fetching all and filtering, or find a specific one.
        # Better: ak.stock_zh_a_spot_em() is for all. 
        # Maybe `ak.stock_individual_info_em` has some real time info? No.
        
        # Let's try `ak.stock_zh_a_spot_em()` (get all) and filter locally for test.
        # In production, fetching all 5000 stocks might be slow every time? 
        # Actually `ak.stock_zh_a_spot_em` is quite fast.
        
        # However, `fetch_stock_data` in `data_fetcher.py` currently uses:
        # info_df = ak.stock_zh_a_spot_em(symbol=symbol)
        # Does that validly filter? Let's test.
        
        spot_df = ak.stock_zh_a_spot_em()
        # Filter for the symbol
        row = spot_df[spot_df['代码'] == symbol]
        if not row.empty:
            print(row.iloc[0])
            # Check for PE, PB, Industry
            # Columns usually: 序号, 代码, 名称, 最新价, 涨跌幅, ..., 市盈率-动态, 市净率, ...
        else:
            print("Symbol not found in spot data.")
            
    except Exception as e:
        print(f"Error fetching spot data: {e}")

    # 2. Individual Info (Industry, Listing Date)
    print("\n--- Individual Info (stock_individual_info_em) ---")
    try:
        info_df = ak.stock_individual_info_em(symbol=symbol)
        print(info_df)
        # Expected: item, value rows.
    except Exception as e:
        print(f"Error fetching individual info: {e}")

    # 3. Financial Indicators (ROE, etc.)
    print("\n--- Financial Indicators (stock_financial_analysis_indicator) ---")
    try:
        # This might return a dataframe with years/quarters
        fin_df = ak.stock_financial_analysis_indicator(symbol=symbol)
        if not fin_df.empty:
            print(fin_df.head(1))
            # Check for ROE columns
        else:
            print("No financial data found.")
    except Exception as e:
        print(f"Error fetching financial indicators: {e}")

if __name__ == "__main__":
    test_stock_info("600519") # Moutai

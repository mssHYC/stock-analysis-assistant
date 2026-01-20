import efinance as ef
import pandas as pd

# 忽略警告
import warnings
warnings.filterwarnings("ignore")

def test_efinance():
    symbol = "600519"
    print(f"正在获取 {symbol} 的数据...")
    
    # 获取单只股票的历史K线
    # klt=101: 日K
    df = ef.stock.get_quote_history(symbol, klt=101)
    
    if df is None or df.empty:
        print("未获取到数据")
        return

    # 打印列名和最后几行
    print("列名:", df.columns.tolist())
    print("最后5行:")
    print(df.tail(5))

if __name__ == "__main__":
    test_efinance()

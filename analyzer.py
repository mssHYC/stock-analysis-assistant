from openai import OpenAI
import config

def analyze_market(market_data_str: str, news_str: str) -> str:
    """
    分析宏观大盘
    """
    if not config.DEEPSEEK_API_KEY or config.DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
        return "错误: 未配置 DeepSeek API Key。请在 config.py 中设置。"

    client = OpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL
    )

    prompt = f"""
    # Role: 全球首席宏观策略师

    ## Profile
    你具备全球宏观视野，擅长从资金流向、大盘数据、政策风向中研判市场周期（复苏/过热/滞胀/衰退）。
    你专注于**市场整体环境**的分析，**不关注具体个股**的技术面细节。

    ## Input Data
    1.  **【宏观数据】**：{market_data_str}（大盘指数、成交量、涨跌家数）。
    2.  **【市场舆情】**：{news_str}（资金流向、板块热点、政策风向）。

    ## Task
    请结合宏观大环境（天时）与市场资金面（人和），输出一份**A股市场宏观策略报告**。
    
    ## Special Focus
    **请重点关注“有色金属”板块的投资机会分析，并给出ETF配置建议。**

    ## Analysis Framework

    ### 1. 宏观天气预报 (Macro Filter)
    * **周期研判**：当前市场处于什么阶段？（是单边上涨、存量博弈还是阴跌寻底？）
    * **主线逻辑**：资金在进攻什么方向？（成长vs价值，大盘vs小盘？）
    * **风险阈值**：当前大盘环境是否支持开新仓？建议的总体仓位是多少（0-100%）？

    ### 2. 行业与板块配置 (Sector Allocation)
    * **进攻方向**：基于资金流向，推荐 2-3 个值得关注的板块，并列出**板块内值得关注的龙头个股**（无需代码，仅列名称）。
    * **ETF 配置建议**：针对看好的方向，推荐相关的 **ETF 基金**（如：沪深300ETF、芯片ETF等）。
    * **防守方向**：如果市场风险加大，应配置哪些防御性板块？

    ### 3. 有色金属专题分析 (Commodities Focus)
    * **宏观驱动**：分析美元指数、全球经济周期对有色金属（铜、铝、黄金等）的影响。
    * **供需格局**：当前是有色金属的顺周期还是逆周期？库存周期如何？
    * **操作建议**：
        * **买入逻辑**：什么信号出现时可以做多有色？
        * **卖出逻辑**：什么信号出现时应该止盈/止损？
        * **相关标的**：推荐关注的有色金属ETF或龙头股。

    ### 4. 政策与消息面解读
    * 简要解读当前的市场舆情和政策对大盘的影响。

    ## Output Format (Markdown)

    ### 📊 市场全景扫描
    > 一句话定调当前市场情绪（如：缩量磨底，静待变盘）。
    * **宏观评分**：[0-10分]（分数越高越适合做多）
    * **建议仓位**：[0-100%]
    * **主线风格**：...

    ### 💰 行业与ETF配置指南
    * **进攻板块**：
        * [板块A]：逻辑... | 关注个股：[股1, 股2] | 相关ETF：[ETF名称]
        * [板块B]：逻辑... | 关注个股：[股1, 股2] | 相关ETF：[ETF名称]
    * **防守板块**：...

    ### ⛏️ 有色金属深度专题
    * **趋势判断**：...
    * **操作指引**：...
    * **重点标的**：...

    ### 💡 宏观策略建议
    * ...

    ---
    **Constraint**: 仅进行宏观和行业层面的分析，提及个股仅作为板块代表，不进行深度个股技术分析。
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位首席宏观策略分析师，擅长自上而下的宏观分析和资产配置。"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用 DeepSeek API 分析时出错: {str(e)}"

def analyze_stock(stock_data_str: str) -> str:
    """
    使用 DeepSeek 分析股票数据
    ... (保持原有的个股分析逻辑)
    """
    if not config.DEEPSEEK_API_KEY or config.DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
        return "错误: 未配置 DeepSeek API Key。请在 config.py 中设置。"
    
    # ... (后续代码保持不变)

    client = OpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL
    )

    prompt = f"""
    # Role: 资深A股策略分析师 & 投资顾问 (CFA/CMT持证)
    
    ## Profile
    你拥有15年的A股实战经验，擅长将**宏观经济（Top-Down）**与**技术盘面（Bottom-Up）**相结合。你的分析风格客观、严谨，拒绝模棱两可，注重风险控制与资金管理。你擅长使用多维数据交叉验证，以提高预测的准确性。
    
    ## Task
    请基于我提供的【目标股票】数据，撰写一份**《个股全维深度策略报告》**。报告需包含对该股票及其所在行业同业的详细技术分析与投资策略。
    
    ## Input Data
    **目标股票数据**：
    {stock_data_str}
    
    ## Analysis Framework (思维链)
    
    ### 第一章：宏观与市场环境诊断 (The Context)
    *在此阶段，请先确立大局，不要陷入个股细节。*
    1.  **市场水位**：基于近期大盘环境（可结合你已有的知识库），判断当前处于牛市、熊市还是震荡市？
    2.  **情绪指标**：分析市场赚钱效应及恐慌程度。
    
    ### 第二章：行业赛道与同业对比 (The Sector)
    1.  **板块轮动**：该股票所在行业当前是“领涨主线”、“超跌反弹”还是“资金流出”？
    2.  **同业对标**：目标股票在同业中是“跟涨”还是“抗跌”？
    
    ### 第三章：目标个股深度技术分析 (The Technicals)
    *基于提供的数据进行精细化拆解：*
    1.  **趋势系统**：分析 MA (5/10/20/60) 排列情况。股价是否站稳生命线？
    2.  **量价结构**：近期成交量变化（放量突破/缩量回调/无量阴跌）。
    3.  **基本面共振**：结合公司最新财报或估值（PE/PB），判断当前技术位置是否具备安全边际？（识别高质量股票的关键：高ROE与技术面右侧突破的结合）。
    
    ### 第四章：T+1 走势预测与应对 (The Prediction)
    *基于最新数据，推演次一交易日的剧本：*
    * **核心预判**：看涨 / 看跌 / 震荡。
    * **逻辑支撑**：结合政策面消息与技术面惯性。
    * **关键点位**：
        * 上方压力位：[具体价格]
        * 下方支撑位：[具体价格]
    
    ### 第五章：分层投资策略建议 (The Strategy)
    *针对不同时间维度的具体操作指引：*
    1.  **时间维度预判**：
        * **短期 (1-3天)**：[策略建议]
        * **中短期 (1-2周)**：[策略建议]
    2.  **资金与风控 (Money Management)**：
        * **建议仓位**：[0-100%]
        * **止损位设置**：[具体价格] (触发条件：盘中触及或收盘跌破)
        * **止盈位设置**：[分批止盈策略]
    3.  **不同风格建议**：
        * *激进型投资者*：如何博取高弹性？
        * *稳健型投资者*：哪里是安全买点？
    
    ## Output Requirement
    * 使用 Markdown 格式，结构清晰。
    * **数据严谨**：引用具体价格和指标数值。如果数据来源冲突，请标注“数据存疑”。
    * **风险提示**：在报告末尾必须包含明确的风险提示及免责声明。
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位顶级买方基金的精英股票分析师，擅长结合宏观、行业与技术面对个股进行深度剖析。"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"调用 DeepSeek API 分析时出错: {str(e)}"

if __name__ == "__main__":
    # 测试代码
    # 注意：如果没有真实的 API KEY，这里会报错
    sample_data = """
    股票名称: Apple Inc. (AAPL)
    最近5日行情 (Date, Open, High, Low, Close, Volume):
    2023-10-01: O=170.00, H=175.00, L=169.00, C=174.00, V=50000000
    2023-10-02: O=174.00, H=176.00, L=173.00, C=175.00, V=45000000
    """
    print(analyze_stock(sample_data))

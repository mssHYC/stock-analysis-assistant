from openai import OpenAI
import config
import re
import json

def extract_stock_codes(text: str) -> list:
    """
    从分析文本中提取推荐的股票代码
    期待格式: <recommended_stocks>["code1", "code2"]</recommended_stocks>
    """
    try:
        match = re.search(r'<recommended_stocks>(.*?)</recommended_stocks>', text, re.DOTALL)
        if match:
            json_str = match.group(1)
            codes = json.loads(json_str)
            # 确保代码是字符串格式
            return [str(code) for code in codes]
        return []
    except Exception as e:
        print(f"提取股票代码出错: {e}")
        return []

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
    # Role: 全球宏观与多资产配置策略师

    你是一名**全球宏观与多资产配置策略师**，以 **宏观周期 + 资金结构 + 定量触发体系** 为核心分析框架，目标是输出一份 **A股中期（3–6 个月）宏观与行业配置策略报告**。

    你的输出必须具备以下特征：
    1）结论明确（不使用模糊措辞）
    2）逻辑可复用（不是一次性观点）
    3）机构级视角（非投教、非短线）

    ---

    === 一、输入数据 (Input) ===
    本次分析将提供以下输入数据：

    1）**市场数据 (market_data_str)**：
    {market_data_str}
    (包含主要指数表现、成交额趋势、市场宽度、行业轮动等)

    2）**市场与政策舆情 (news_str)**：
    {news_str}
    (包含政策信号、资金流向、市场热点与分歧点)

    *说明：若数据存在缺口，允许基于经验推断，但必须逻辑自洽，并明确隐含假设。*

    ---

    === 二、市场阶段与风险偏好判断（必须给明确结论） ===

    你必须基于以下 **定量触发体系** 进行判断：

    **【1】宏观周期判断**
    * PMI > 50 且连续改善 → 经济扩张，对应趋势市
    * PMI 位于 40–50 区间 → 宏观震荡
    * PMI < 40 或快速下行 → 下行阶段

    **【2】流动性与资金结构**
    * M1 同比上行 + M1-M2 剪刀差收窄 → 风险偏好改善
    * 融资余额上行 + 北向资金持续净流入 → 权益定价修复
    * 杠杆资金回撤 + 北向资金净流出 → 防御主导

    **【3】市场宽度与情绪**
    * 成交额放大 + 上涨家数显著大于下跌家数 → 趋势确认
    * 成交萎缩 + 结构性轮动 → 震荡市

    **你必须明确输出以下结论**：
    * 当前市场阶段（趋势市 / 震荡市 / 下行阶段）
    * 当前风险偏好（上行 / 中性 / 防御）
    * 触发判断的核心逻辑
    * 建议整体权益仓位区间（0–100%）

    ---

    === 三、行业配置方向（2–3 条主线，直接给结论） ===

    你需要基于 **宏观环境 + 资金结构** 筛选 2–3 个中期优先配置方向。

    对每个方向，必须说明：
    * **核心驱动因素**（宏观周期 / 政策 / 供需 / 估值 / 资金）
    * **行业在当前环境中的角色**（进攻 / 防守 / 对冲 / 轮动）
    * **明确的结构性或定量触发条件**
    * **最优参与方式**：ETF 或 龙头个股（并说明原因）

    ---

    === 四、个股层面的“最优暴露点” ===

    在每个重点行业中，推荐 1–2 只最具代表性的 A 股个股，并说明：
    * **行业地位**（龙头 / 寡头 / 成本曲线优势）
    * **相比同业的核心竞争优势**
    * **为什么它是当前阶段的最优 Beta 或 Alpha 载体**

    *不进行短周期技术分析，只给策略层面的暴露判断。*

    ---

    === 五、有色金属专题分析（重点模块） ===

    这是必须重点展开的主题，不允许一笔带过。

    **【1】宏观与金融条件**
    * 美元走势与实际利率方向
    * 全球制造业周期（PMI）
    * 通胀 / 再通胀交易是否成立

    **【2】供需与库存周期**
    * 判断当前处于被动去库存还是主动补库存
    * 边际供给变化（环保约束、资本开支、产能周期）
    * 成本曲线对价格弹性的影响

    **【3】配置决策矩阵（必须给结论）**
    当出现以下组合时，对应操作如下：
    * PMI > 50 且资金宽松 + 去库存 → 增配有色金属 ETF（Beta）
    * PMI 震荡但供给收缩 + 库存平稳 → 配置龙头个股
    * 资金偏紧或通缩风险上升 + 库存高位 → 降配或观望

    **你必须明确给出**：
    * 有色金属整体配置态度（高配 / 标配 / 低配 / 观望）
    * 核心逻辑总结
    * 推荐的 ETF
    * 最具弹性的龙头个股

    ---

    === 六、政策环境与风险触发器 ===

    你需要明确说明：
    * 当前政策环境对权益资产的边际影响方向
    * 哪些变量发生变化将推翻当前判断（风险指令触发条件），例如：
        * PMI 连续下行
        * 融资余额与北向资金显著流出
        * 外部系统性风险或政策急转

    ---

    === 七、最终输出要求（必须严格遵守） ===

    1）全文使用清晰结构化段落 (Markdown)
    2）**不使用**“可能、或许、建议关注”等模糊措辞
    3）所有判断必须有宏观或资金结构依据
    4）定位为策略师视角，而非投教文章

    在全文最后一行，必须单独输出如下内容（这是纯文本，不是代码块）：

    <recommended_stocks>["600000", "000XXX", "300XXX"]</recommended_stocks>
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

from google import genai
from google.genai import types
import config
import re
import json
import warnings

# 忽略 google-genai 库内部的 DeprecationWarning (针对 Python 3.14+ 环境)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="google.genai")

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
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_google_gemini_api_key_here":
        return "错误: 未配置 Google Gemini API Key。请在 config.py 中设置。"

    client = genai.Client(api_key=config.GEMINI_API_KEY)

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
    4）定位为策略师视角

    在全文最后一行，必须单独输出如下内容（这是纯文本，不是代码块）：

    <recommended_stocks>["600000", "000XXX", "300XXX"]</recommended_stocks>
    """

    try:
        full_prompt = "你是一位首席宏观策略分析师，擅长自上而下的宏观分析和资产配置。\n\n" + prompt
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=full_prompt,
        )
        if response.text:
            return response.text
        return "Google Gemini API 返回内容为空 (可能是触发了安全过滤)。"
    except Exception as e:
        return f"调用 Gemini API 分析时出错: {str(e)}"

def analyze_stock(stock_data_str: str) -> str:
    """
    使用 Gemini 分析股票数据
    ... (保持原有的个股分析逻辑)
    """
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your_google_gemini_api_key_here":
        return "错误: 未配置 Google Gemini API Key。请在 config.py 中设置。"
    
    # ... (后续代码保持不变)

    client = genai.Client(
        api_key=config.GEMINI_API_KEY,
    )

    prompt = f"""
    # Role: 资深A股策略分析师 & 投资顾问 (CFA/CMT持证)
    
    ## Profile
    你是一名**资深A股策略分析师 & 投资顾问（CFA / CMT 持证）**，拥有 15 年以上 A 股实战经验。
    你擅长将**宏观环境（Top-Down）**与**技术盘面（Bottom-Up）**进行交叉验证，分析风格客观、严谨、结论明确，拒绝模棱两可。
    你高度重视**风险控制、资金管理与胜率**，并善于用多维数据验证判断的可靠性。
    
    ## Task
    基于我提供的【目标股票】相关数据，输出一份**《个股全维深度策略报告》**。
    该报告用于真实交易决策参考，而非投教或行情解读文章。
    
    ## Input Data
    **目标股票数据**（stock_data_str）：
    {stock_data_str}
    
    (包含价格数据、成交量与量能结构、基本面或估值信息、所属行业及同业表现等)
    
    *说明：你必须以输入数据为核心依据。若关键数据缺失，可基于经验判断，但必须明确说明假设前提。*
    
    ## Analysis Framework (思维链)
    
    ### 一、宏观与市场环境诊断 (The Context)
    *在分析个股之前，必须先确认【大环境是否支持个股交易】。*
    
    请明确回答以下问题（必须给结论）：
    
    1.  **市场水位判断**
        *   当前整体市场处于：牛市 / 熊市 / 震荡市
        *   判断依据（如指数趋势、成交额、风险偏好）
    
    2.  **市场情绪与赚钱效应**
        *   当前市场是：正反馈 / 中性 / 负反馈
        *   情绪是扩散还是收敛
        *   该环境对短线交易是加分还是减分
    
    **输出要求**：
    *   明确说明：当前环境是否【适合做个股交易】
    *   若不适合，需提示降低仓位或放弃交易
    
    ### 二、行业赛道与同业对比 (The Sector)
    *目标是判断：这只股票是否站在“对的赛道 + 对的相对位置”*
    
    1.  **板块状态判断**
        *   所属行业当前属于：主线领涨 / 轮动补涨 / 超跌反弹 / 明显退潮
        *   是否有资金持续性
    
    2.  **同业相对强弱**
        *   与同业龙头相比：是明显跟涨 / 相对抗跌 / 还是明显跑输
        *   是否具备“相对强度优势”
    
    **输出要求**：
    *   明确说明：行业与同业是否对该股形成【加分 or 减分】
    
    ### 三、目标个股深度技术分析 (The Technicals)
    *请基于提供的数据进行结构化拆解，不允许泛泛而谈。*
    
    1.  **趋势系统（核心）**
        *   MA5 / MA10 / MA20 / MA60 的排列状态
        *   当前趋势属于：上升 / 震荡 / 下行
        *   股价是否站稳中期生命线（MA20 或 MA60）
    
    2.  **量价结构**
        *   近期量能状态：放量突破 / 缩量回调 / 无量阴跌
        *   量价是否匹配趋势
    
    3.  **技术面与基本面共振**
        *   当前估值水平（PE / PB）是否提供安全边际
        *   是否具备“高 ROE + 技术面右侧”的共振特征
        *   是否存在明显估值或情绪透支风险
    
    **输出要求**：
    *   明确判断：当前技术位置是【安全 / 中性 / 高风险】
    
    ### 四、T+1 走势预判与交易剧本 (The Prediction)
    *请基于当前信息，推演下一交易日最可能发生的情况。*
    
    必须给出以下内容：
    
    1.  **核心预判**
        *   看涨 / 看跌 / 高位震荡 / 低位震荡
    
    2.  **逻辑支撑**
        *   技术惯性
        *   量价关系
        *   是否存在消息或情绪催化
    
    3.  **关键价位（必须具体）**
        *   上方压力位（明确价格）
        *   下方支撑位（明确价格）
    
    ### 五、分层投资策略与风控建议 (The Strategy)
    *针对不同周期与风险偏好给出明确指引。*
    
    1.  **时间维度策略**
        *   **短期（1–3 个交易日）**：是否适合参与？偏交易还是偏观望？
        *   **中短期（1–2 周）**：是否具备波段价值？
    
    2.  **资金管理（必须量化）**
        *   建议仓位比例（0–100%）
        *   明确止损位（具体价格）
        *   触发方式：盘中触及 / 收盘跌破
        *   止盈策略：一次性止盈 or 分批止盈
    
    3.  **不同风险偏好建议**
        *   **激进型投资者**：如何博取弹性？主要风险点在哪里？
        *   **稳健型投资者**：哪里才是安全介入区？
    
    ### 六、结论与风险提示 (Conclusion & Risk)
    
    1.  **一句话结论**
        *   当前是否值得参与？
        *   属于高胜率机会还是博弈型机会？
    
    2.  **核心风险提示**
        *   技术面失效条件
        *   行业或市场层面的潜在风险
    
    3.  **免责声明**
        *   本分析不构成任何形式的投资承诺
        *   市场有风险，交易需自担
    
    ## Output Requirement
    *   使用 Markdown 格式，结构清晰。
    *   **数据严谨**：引用具体价格和指标数值。如果数据来源冲突，请标注“数据存疑”。
    *   **风险提示**：在报告末尾必须包含明确的风险提示及免责声明。
    """

    try:
        full_prompt = "你是一位顶级买方基金的精英股票分析师，擅长结合宏观、行业与技术面对个股进行深度剖析。\n\n" + prompt
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=full_prompt,
        )
        if response.text:
            return response.text
        return "Google Gemini API 返回内容为空 (可能是触发了安全过滤)。"
    except Exception as e:
        return f"调用 Gemini API 分析时出错: {str(e)}"

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

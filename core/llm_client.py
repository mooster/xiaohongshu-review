"""LLM 客户端 - Google Gemini"""
import os

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


def _load_api_key():
    """从 .env 读取 Google API Key"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key and os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GOOGLE_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
    return api_key


def get_model():
    """获取 Gemini 模型"""
    if not HAS_GEMINI:
        return None
    api_key = _load_api_key()
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.0-flash")


def rewrite_selling_point(sp_name, sp_ref, current_text, required_keywords, style="小红书爆文风格"):
    """用 AI 改写一个卖点的人话版本"""
    model = get_model()
    if not model:
        return None, "API 未配置（需要 GOOGLE_API_KEY）"

    kw_list = "、".join(required_keywords) if required_keywords else "无"

    prompt = f"""你是一个真实的小红书博主，不是AI。用你自己的语气改写这段卖点。

【卖点】{sp_name}
【参考话术】{sp_ref}
【当前文案】{current_text}

【要求】
1. 必须保留这些必提词（一字不差）：{kw_list}
2. 不要用违禁词：敏宝、过敏、新生儿、敏感、最、第一、预防、生长、发育、免疫
3. 像跟闺蜜聊天一样写，句子长短交错，可以用语气词
4. 不要用AI味的句式（"不仅...而且""值得一提""作为一个"）
5. 不要三段排比，不要空洞总结
6. 只输出改写后的文字"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip(), None
    except Exception as e:
        return None, str(e)


def rewrite_full_body(body, config, selling_points_config):
    """用 AI 改写整篇正文的人话感"""
    model = get_model()
    if not model:
        return None, "API 未配置（需要 GOOGLE_API_KEY）"

    # 收集所有必提词
    all_kw = []
    for para in selling_points_config:
        for sp in para.get("selling_points", []):
            all_kw.extend(sp.get("required_keywords", []))
    kw_str = "\n".join([f"- {kw}" for kw in all_kw if kw])

    # 从配置中读取违禁词列表
    forbidden = config.get("hard_rules", {}).get("forbidden_words", [])
    fw_list = "、".join([fw["word"] for fw in forbidden])

    # 构建替换规则提示
    replace_rules = []
    for fw in forbidden:
        if fw.get("replacement"):
            replace_rules.append(f"「{fw['word']}」→「{fw['replacement']}」")

    prompt = f"""你是一个真实的小红书博主，不是AI。请用你自己的语气改写以下文案。

【原文】
{body}

【硬性要求 - 必须100%遵守】
1. 字数严格控制在 820-880 字之间（中文字符数），绝对不能超过 900 字
2. 以下必提词必须原封不动保留（一字不差、不能省略、不能改写）：
{kw_str}
3. ⚠️ 绝对禁止出现以下违禁词：{fw_list}
   - 这些词连一个都不能出现！包括「过敏」「敏感」「新生儿」「免疫」「预防」「生长」「发育」等
   - 正确替换方式：{'; '.join(replace_rules)}
   - 「第一口奶」必须写成「第一口奶粉」
   - 「最」除了「最近、最后、最终、最初」外都不能用
   - 「第一」除了「第一口奶粉」外都不能用

【去AI痕迹 - 让文字像真人写的（基于Humanizer反AI检查清单）】
❌ 禁止使用AI典型句式：
- 不要用"值得一提的是""总而言之""综上所述""不仅...而且...""无论...还是..."
- 不要用"作为一个XX""说到XX""关于XX""众所周知"
- 不要每句话都用"的""了""呢"结尾
- 不要三段式排比（AI最爱凑三个并列）
- 不要空洞的总结句（如"选它准没错""值得每个妈妈拥有"）
- 不要用"重要的是""关键在于""核心是"这类伪深度表达

✅ 要像真人这样写：
- 句子长短交错，有时候一个词就是一句话。有时候拉长说
- 要有自己的态度和反应（"我当时真的吓到了""说实话一开始我也犹豫"）
- 可以有不确定感（"我也说不好""反正我家是这样"）
- 像在微信里跟闺蜜语音转文字，有口语的碎片感
- 适当用拼音缩写、网络用语（yyds、绝绝子、姐妹们）
- 中间可以插一句跟主题无关的感叹（"天气好热啊说远了"）让文章更真实
- 用具体的场景和细节，不要笼统概括

【结构要求】
- 保持原文的内容结构顺序
- 段落之间不要用生硬的过渡句，自然地聊下去就好

请直接输出改写后的完整正文，不要加任何解释或前言："""

    try:
        response = model.generate_content(prompt)
        return response.text.strip(), None
    except Exception as e:
        return None, str(e)

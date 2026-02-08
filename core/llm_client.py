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

    prompt = f"""你是小红书顶级爆文写手。请帮我把以下卖点内容改写成口语化、有感染力的小红书风格。

【卖点】{sp_name}
【参考话术】{sp_ref}
【当前文案中相关内容】{current_text}

【改写要求】
1. 必须保留以下必提词（一字不差）：{kw_list}
2. 风格：{style}，口语化、有代入感、像朋友聊天
3. 适当使用语气词（真的、绝了、太、超）
4. 不要用违禁词：敏宝、过敏、新生儿、敏感、最、第一、预防、生长、发育、免疫
5. 只输出改写后的文字，不要解释

【改写结果】"""

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

    prompt = f"""你是小红书顶级爆文写手。请改写以下文案，让它更口语化、有人话感。

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

【风格要求】
- 保持原文的内容结构（敏敏现状 → 防敏水解技术 → 自护力 → 基础营养）
- 像朋友聊天、有代入感、适当用语气词和emoji
- 小红书爆文风格

请直接输出改写后的完整正文，不要加任何解释："""

    try:
        response = model.generate_content(prompt)
        return response.text.strip(), None
    except Exception as e:
        return None, str(e)

import streamlit as st
import re
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import List
from docx import Document
import io
import anthropic

RULE_VERSION = "2026-02-04"
BRIEF_VERSION = "2026-02"

BRIEF_CONTENT = """
**核心卖点 (不可改动):**
- 多项科学实证的雀巢尖峰水解技术
- 防敏领域权威德国GINI研究认证
- 能长效防敏20年
- 相比于牛奶蛋白致敏性降低1000倍
- 全球创新的超倍自护科技
- 6种HMO加上明星双菌B.Infantis和Bb-12
- 协同作用释放高倍的原生保护力
- 短短28天就能调理好娃的肚肚菌菌环境
- 保护力能持续15个月
- 25种维生素和矿物质
- 全乳糖的配方口味清淡
"""

REVIEW_RULES = {
    "required_keywords": ["适度水解", "防敏", "能恩全护"],
    "forbidden_words": {
        "禁止词": ["敏宝", "奶瓶", "奶嘴", "新生儿", "过敏", "疾病"],
        "禁疗效": ["预防", "生长", "发育", "免疫"],
        "禁绝对化": ["最好", "最佳", "TOP1", "No.1"]
    },
    "allowed_exceptions": ["第一口奶粉", "第一口配方粉"],
    "selling_points": [
        "多项科学实证的雀巢尖峰水解技术",
        "防敏领域权威德国GINI研究认证",
        "能长效防敏20年",
        "相比于牛奶蛋白致敏性降低1000倍",
        "全球创新的超倍自护科技",
        "6种HMO加上明星双菌B.Infantis和Bb-12",
        "协同作用释放高倍的原生保护力",
        "短短28天就能调理好娃的肚肚菌菌环境",
        "保护力能持续15个月",
        "25种维生素和矿物质",
        "全乳糖的配方口味清淡"
    ],
    "required_tags": ["#能恩全护", "#能恩全护水奶", "#适度水解", "#适度水解奶粉", "#适度水解奶粉推荐", "#防敏奶粉", "#第一口奶粉", "#雀巢适度水解"],
    "max_words": 900,
    "min_tags": 10
}

SUGGESTIONS = {"敏宝": "敏感体质宝宝", "新生儿": "初生宝宝", "过敏": "敏敏", "预防": "远离", "生长": "成长", "发育": "成长", "免疫": "保护力"}

@dataclass
class CheckResult:
    name: str
    passed: bool
    found: int = 0
    total: int = 0
    issues: List[str] = field(default_factory=list)

def read_docx(file):
    doc = Document(io.BytesIO(file.read()))
    text = []
    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text)
    return "\n".join(text)

def parse_content(content):
    tags = re.findall(r'#[\w\u4e00-\u9fff]+', content)
    text = re.sub(r'#[\w\u4e00-\u9fff]+', '', content)
    word_count = len(re.findall(r'[\u4e00-\u9fff]', text))
    return {"text": content, "tags": tags, "word_count": word_count}

def run_review(content, kol, ver, reviewer):
    data = parse_content(content)
    results = {}
    
    kw_issues = []
    kw_found = 0
    for kw in REVIEW_RULES["required_keywords"]:
        if kw in data["text"]:
            kw_found += 1
        else:
            kw_issues.append(f"缺少: {kw}")
    results["keywords"] = CheckResult("必须关键词", len(kw_issues)==0, kw_found, len(REVIEW_RULES["required_keywords"]), kw_issues)
    
    fb_issues = []
    exceptions = REVIEW_RULES["allowed_exceptions"]
    for cat, words in REVIEW_RULES["forbidden_words"].items():
        for w in words:
            if w in data["text"]:
                ctx = data["text"][max(0,data["text"].find(w)-10):data["text"].find(w)+len(w)+10]
                if not any(e in ctx for e in exceptions):
                    sug = SUGGESTIONS.get(w, "删除")
                    fb_issues.append(f"{cat} [{w}] - {sug}")
    results["forbidden"] = CheckResult("禁词检查", len(fb_issues)==0, 0, 0, fb_issues)
    
    sp_issues = []
    sp_found = 0
    for sp in REVIEW_RULES["selling_points"]:
        if sp in data["text"]:
            sp_found += 1
        else:
            sp_issues.append(f"缺少: {sp[:20]}...")
    results["selling"] = CheckResult("不可改动卖点", sp_found==len(REVIEW_RULES["selling_points"]), sp_found, len(REVIEW_RULES["selling_points"]), sp_issues)
    
    st_issues = []
    if data["word_count"] > REVIEW_RULES["max_words"]:
        st_issues.append(f"字数超限: {data['word_count']}/{REVIEW_RULES['max_words']}")
    if len(data["tags"]) < REVIEW_RULES["min_tags"]:
        st_issues.append(f"标签不足: {len(data['tags'])}/{REVIEW_RULES['min_tags']}")
    results["structure"] = CheckResult("结构完整性", len(st_issues)==0, 0, 0, st_issues)
    
    tg_issues = []
    tg_found = 0
    for t in REVIEW_RULES["required_tags"]:
        if t in data["tags"]:
            tg_found += 1
        else:
            tg_issues.append(f"缺少: {t}")
    results["tags"] = CheckResult("必提Tag", len(tg_issues)==0, tg_found, len(REVIEW_RULES["required_tags"]), tg_issues)
    
    score = 0
    weights = [("keywords", 0.15), ("forbidden", 0.20), ("selling", 0.30), ("structure", 0.15), ("tags", 0.20)]
    for key, w in weights:
        r = results[key]
        if r.total > 0:
            score += (r.found / r.total) * w * 100
        else:
            score += (100 if r.passed else 0) * w
    
    return {"kol": kol, "ver": ver, "reviewer": reviewer, "results": results, "score": round(score, 1), "word_count": data["word_count"], "tag_count": len(data["tags"])}

def get_ai_suggestions(content, issues):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, None
    
    issues_text = "\n".join([f"- {issue}" for issue in issues])
    selling_points_text = "\n".join([f"- {sp}" for sp in REVIEW_RULES["selling_points"]])
    
    prompt = f"""你是小红书KOL稿件审核专家。请修改以下稿件。

原稿件:
{content}

发现的问题:
{issues_text}

必须包含的卖点(不可改动原文):
{selling_points_text}

禁词替换: 敏宝改为敏感体质宝宝, 新生儿改为初生宝宝, 过敏改为敏敏, 预防改为远离, 生长发育改为成长, 免疫改为保护力

任务1: 列出修改建议,格式为:
问题: xxx
原文: xxx  
改为: xxx

任务2: 输出修改后的完整稿件

请用以下格式回复:

SUGGESTIONS_START
(修改建议)
SUGGESTIONS_END

REVISED_START
(完整稿件)
REVISED_END
"""
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        response = message.content[0].text
        
        suggestions = ""
        revised = ""
        
        if "SUGGESTIONS_START" in response and "SUGGESTIONS_END" in response:
            start = response.find("SUGGESTIONS_START") + len("SUGGESTIONS_START")
            end = response.find("SUGGESTIONS_END")
            suggestions = response[start:end].strip()
        
        if "REVISED_START" in response and "REVISED_END" in response:
            start = response.find("REVISED_START") + len("REVISED_START")
            end = response.find("REVISED_END")
            revised = response[start:end].strip()
        
        return suggestions, revised
    except Exception as e:
        return f"AI error: {str(e)}", None

st.set_page_config(page_title="小红书KOL审稿系统", page_icon="🔍", layout="wide")
st.markdown("<h1 style='text-align:center;color:#ff6b6b;'>小红书KOL审稿系统 v2.1</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>能恩全护 - AI智能审核</p>", unsafe_allow_html=True)
st.markdown("---")

c1, c2 = st.columns(2)
c1.info(f"审核规则: {RULE_VERSION}")
c2.info(f"Brief: {BRIEF_VERSION}")

with st.expander("查看Brief内容"):
    st.markdown(BRIEF_CONTENT)

st.markdown("---")

c1, c2, c3 = st.columns(3)
kol = c1.text_input("KOL名称", placeholder="例如: 小红薯妈妈")
ver = c2.selectbox("版本", ["V1", "V2", "V3", "FINAL"])
reviewer = c3.selectbox("审核方", ["赞意", "客户"])

st.markdown("### 稿件内容")

tab1, tab2 = st.tabs(["上传文档", "粘贴文本"])

content = ""

with tab1:
    uploaded_file = st.file_uploader("上传Word文档", type=["docx"])
    if uploaded_file:
        content = read_docx(uploaded_file)
        st.success(f"已读取: {uploaded_file.name}")
        with st.expander("预览内容"):
            st.text(content[:500] + "..." if len(content) > 500 else content)

with tab2:
    pasted = st.text_area("粘贴稿件内容", height=250, placeholder="粘贴稿件...")
    if pasted:
        content = pasted

if st.button("开始审核", type="primary", use_container_width=True):
    if not kol:
        st.error("请填写KOL名称")
    elif not content.strip():
        st.error("请上传文档或粘贴内容")
    else:
        r = run_review(content, kol, ver, reviewer)
        
        st.markdown("---")
        st.markdown("## 审核报告")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("KOL", f"@{r['kol']}")
        c2.metric("版本", r['ver'])
        c3.metric("审核方", r['reviewer'])
        c4.metric("综合评分", f"{r['score']}%")
        
        st.markdown("---")
        st.markdown("## 一、客观检查")
        
        checks = [
            ("1.1 必须关键词", "keywords"),
            ("1.2 禁词检查", "forbidden"),
            ("1.3 不可改动卖点", "selling"),
            ("1.4 结构完整性", "structure"),
            ("1.5 必提Tag", "tags")
        ]
        
        all_issues = []
        for title, key in checks:
            res = r["results"][key]
            if res.total > 0:
                status = f"{res.found}/{res.total}"
            else:
                status = "通过" if res.passed else f"{len(res.issues)}项问题"
            
            with st.expander(f"{title} - {status}", expanded=not res.passed):
                if res.passed:
                    st.success("通过")
                else:
                    for issue in res.issues:
                        st.warning(issue)
                        all_issues.append(f"[{title}] {issue}")
        
        st.markdown("---")
        st.markdown("## 二、审核总结")
        
        if r["score"] >= 90:
            st.success("优秀!")
        elif r["score"] >= 70:
            st.info("良好")
        elif r["score"] >= 50:
            st.warning("需改进")
        else:
            st.error("需大改")
        
        st.caption(f"字数: {r['word_count']} | 标签: {r['tag_count']}个")
        
        if all_issues and r["score"] < 90:
            st.markdown("---")
            st.markdown("## 三、AI修改建议")
            
            with st.spinner("AI正在生成修改建议..."):
                suggestions, revised = get_ai_suggestions(content, all_issues)
            
            if suggestions:
                st.markdown("### 修改建议")
                st.markdown(suggestions)
                
                if revised:
                    st.markdown("---")
                    st.markdown("### 修改后的稿件")
                    st.text_area("可直接复制", revised, height=300)
                    
                    st.download_button(
                        label="下载修改稿件",
                        data=revised,
                        file_name=f"{kol}_{ver}_revised.txt",
                        mime="text/plain"
                    )
            else:
                st.warning("AI服务不可用,请检查API Key")

st.markdown("---")
st.caption(f"v2.1 | {RULE_VERSION}")

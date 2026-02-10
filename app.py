"""赞意AI · 小红书KOL审稿系统"""
import streamlit as st
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from core.config_loader import load_config, list_configs
from core.text_utils import count_chinese, read_docx
from core.hard_checks import run_all_checks
from core.auto_fix import auto_fix_all, highlight_original, highlight_revised, diff_highlight
from core.llm_client import rewrite_full_body
from core.doc_export import generate_diff_docx, generate_clean_docx
from ui.styles import MAIN_CSS

st.set_page_config(page_title="赞意AI - 审稿系统", page_icon="✦", layout="wide", initial_sidebar_state="expanded")
st.markdown(MAIN_CSS, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  工具函数
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def find_check(results, check_id):
    for r in results:
        if r["id"] == check_id:
            return r
    defaults = {
        "forbidden_words": {"id": check_id, "pass": True, "message": "未检查", "violations": [], "special_violations": [], "tag_violations": []},
        "selling_points": {"id": check_id, "pass": True, "message": "未检查", "total": 0, "passed": 0, "paragraphs": []},
        "title_keywords": {"id": check_id, "pass": True, "message": "未检查", "missing": []},
        "structure": {"id": check_id, "pass": True, "message": "未检查", "missing_sections": [], "order_correct": True, "expected_order": [], "actual_order": []},
    }
    return defaults.get(check_id, {"id": check_id, "pass": True, "message": "未检查"})


def build_full_text(titles, body, tags):
    parts = []
    for i, t in enumerate(titles):
        parts.append(f"标题{i+1}：{t}")
    parts.append("")
    parts.append(body)
    parts.append("")
    if tags:
        parts.append(tags)
    return "\n".join(parts)


def parse_input(text):
    lines = text.strip().split('\n')
    titles, body_lines, tags_line, section = [], [], "", None
    for line in lines:
        s = line.strip()
        if not s:
            if section == 'body' and body_lines and body_lines[-1] != "":
                body_lines.append("")
            continue
        if s.startswith(('一、', '二、', '三、', '四、')):
            section = 'title' if '标题' in s else ('body' if any(x in s for x in ['笔记', '内容']) else 'skip')
            continue
        if any(s.startswith(p) for p in ['达人昵称', '合作形式', '合作方向', '发布时间', '拍图', 'live图']):
            continue
        if s.startswith('标题') and '备选' in s:
            section = 'title'; continue
        if s.startswith('大纲'):
            section = 'body'
            rest = s.split('）')[-1].strip() if '）' in s else s.split(')')[-1].strip() if ')' in s else ""
            if rest and len(rest) > 5:
                body_lines.append(rest)
            continue
        if '话题标签' in s or s.count('#') >= 3:
            t = s.split('：')[-1].strip() if '话题标签' in s and '：' in s else s
            if t.count('#') >= 2:
                tags_line = t
            continue
        if section == 'title' and len(titles) < 5:
            titles.append(s)
            if len(titles) >= 3:
                section = 'body'
            continue
        if section in ('body', None):
            section = 'body'; body_lines.append(s)
    cleaned, prev = [], False
    for l in body_lines:
        if l == "":
            if not prev:
                cleaned.append("")
            prev = True
        else:
            cleaned.append(l); prev = False
    return titles[:3], '\n'.join(cleaned).strip(), tags_line


def render_sp_table(sp_result):
    html = '<table class="audit-table"><tr><th>卖点</th><th>必提词</th><th>状态</th></tr>'
    for para in sp_result["paragraphs"]:
        html += f'<tr><td colspan="3" class="sp-para-header">{para["paragraph_name"]}</td></tr>'
        for sp in para["selling_points"]:
            if sp.get("soft_only"):
                html += f'<tr><td>{sp["name"]}</td><td><span class="tag-warn">人话修改项（无必提词）</span></td><td>—</td></tr>'
                continue
            kws = ""
            for kw in sp.get("keywords", []):
                c = "tag-pass" if kw["found"] else "tag-fail"
                kws += f'<span class="{c}">{kw["keyword"]}</span> '
            icon = '<span class="status-pass">通过</span>' if sp["pass"] else '<span class="status-fail">未通过</span>'
            html += f'<tr><td>{sp["name"]}</td><td>{kws}</td><td>{icon}</td></tr>'
    html += '</table>'
    return html


def render_audit_table(results):
    html = '<table class="audit-table"><tr><th>检查项</th><th>状态</th><th>详情</th></tr>'
    for r in results:
        icon = '<span class="status-pass">通过</span>' if r["pass"] else '<span class="status-fail">未通过</span>'
        row_bg = "" if r["pass"] else ' style="background:var(--red-bg)"'
        html += f'<tr{row_bg}><td>{r["name"]}</td><td>{icon}</td><td>{r["message"]}</td></tr>'
    html += '</table>'
    return html


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  State
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INIT = {
    "results": None, "titles": [], "body": "", "tags": "",
    "fixed_titles": None, "fixed_body": None, "fixed_tags": None,
    "changes": [], "is_fixed": False,
    "ai_body": None, "ai_error": None, "ai_done": False,
    "ai_results": None,
    "final_titles": None, "final_body": None, "final_tags": None,
    "final_results": None,
}
for k, v in INIT.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  侧边栏
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">'
        '<span class="brand-icon">✦</span>'
        '<span class="brand-text">赞意AI</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption("小红书 KOL 审稿系统")
    st.markdown("---")

    configs = list_configs()
    labels = [c["label"] for c in configs]
    sel = st.selectbox("审核方向", range(len(configs)), format_func=lambda i: labels[i])
    config = load_config(configs[sel]["file"])
    m = config["meta"]
    st.caption(f"{m['brand']} · {m['direction']} · {m['platform']}")
    st.markdown("---")

    method = st.radio("输入方式", ["上传文件", "粘贴文本"], horizontal=True, label_visibility="collapsed")
    if "up_text" not in st.session_state:
        st.session_state.up_text = ""
    if method == "上传文件":
        f = st.file_uploader("上传 KOL 稿件", type=["docx"], help="支持 .docx 格式")
        if f:
            st.session_state.up_text = read_docx(f)
            st.success(f"已读取 {f.name}")
    else:
        st.session_state.up_text = st.text_area("粘贴内容", height=200, key="raw_in", placeholder="将稿件内容粘贴到这里...")

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    if st.button("开始审核", type="primary", use_container_width=True):
        raw = st.session_state.up_text
        if raw.strip():
            t, b, tg = parse_input(raw)
            st.session_state.titles = t
            st.session_state.body = b
            st.session_state.tags = tg
            st.session_state.results = run_all_checks(t, b, tg, config)
            for k in ["is_fixed", "fixed_titles", "fixed_body", "fixed_tags", "changes",
                       "ai_body", "ai_error", "ai_done", "ai_results",
                       "final_titles", "final_body", "final_tags", "final_results"]:
                st.session_state[k] = INIT[k]
        else:
            st.error("请先上传文件或粘贴稿件")

    if st.button("清空重置", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    # 流程进度
    if st.session_state.results:
        st.markdown("---")
        st.markdown('<div class="sidebar-section-title">流程进度</div>', unsafe_allow_html=True)
        steps = [
            ("基础审核", True),
            ("卖点审核", st.session_state.is_fixed),
            ("人话修改", st.session_state.ai_done),
            ("终检通过", st.session_state.final_results and all(r["pass"] for r in st.session_state.final_results)),
        ]
        for i, (name, done) in enumerate(steps):
            cls = "done" if done else "pending"
            num = i + 1
            st.markdown(
                f'<div class="progress-step {cls}">'
                f'<span class="step-num">{num}</span> {name}'
                f'</div>',
                unsafe_allow_html=True,
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  主区域
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown(
    '<div class="main-title">小红书KOL审稿系统</div>'
    '<div class="main-subtitle">智能内容审核 · 违禁词检测 · AI人话改写</div>',
    unsafe_allow_html=True,
)

if not st.session_state.results:
    st.markdown(
        '<div class="empty-state">'
        '<div class="empty-icon">✦</div>'
        '<h3>上传稿件，开始审核</h3>'
        '<p>在左侧选择审核方向，上传 .docx 或粘贴文本</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.stop()

results = st.session_state.results
titles = st.session_state.titles
body = st.session_state.body
tags = st.session_state.tags

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Tabs 布局
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

tab1, tab2, tab3, tab4 = st.tabs(["基础审核", "卖点审核", "人话修改", "终检"])


# ══════════════════════════════
#  Tab 1 — 基础审核
# ══════════════════════════════
with tab1:
    basic_ids = {"word_count", "title_count", "title_keywords", "hashtags", "forbidden_words"}
    basic_checks = [r for r in results if r["id"] in basic_ids]
    fw_r = find_check(results, "forbidden_words")
    fwc = len(fw_r.get("violations", []))
    basic_pass = sum(1 for r in basic_checks if r["pass"])
    basic_total = len(basic_checks)

    # 评分卡
    score_html = '<div class="score-bar">'
    for val, label, ok in [
        (f"{basic_pass}/{basic_total}", "基础通过", basic_pass == basic_total),
        (str(results[0]["value"]), "字数", results[0]["pass"]),
        (str(fwc), "违禁词", fwc == 0),
    ]:
        cls = "pass" if ok else "fail"
        vcls = "green" if ok else "red"
        score_html += (
            f'<div class="score-item {cls}">'
            f'<div class="label">{label}</div>'
            f'<div class="value {vcls}">{val}</div></div>'
        )
    score_html += '</div>'
    st.markdown(score_html, unsafe_allow_html=True)

    # 审核表
    st.markdown(render_audit_table(basic_checks), unsafe_allow_html=True)

    # 违禁词明细
    if fw_r["violations"]:
        st.markdown('<div class="section-label">违禁词明细</div>', unsafe_allow_html=True)
        by_word = {}
        for v in fw_r["violations"]:
            w = v["word"]
            if w not in by_word:
                by_word[w] = {"count": 0, "cat": v["category"], "repl": v["replacement"]}
            by_word[w]["count"] += 1
        d = '<table class="audit-table"><tr><th>违禁词</th><th>分类</th><th>次数</th><th>替换为</th></tr>'
        for w, info in by_word.items():
            repl = info["repl"] if info["repl"] else "删除"
            d += (
                f'<tr><td><span class="status-fail">{w}</span></td>'
                f'<td>{info["cat"]}</td><td>{info["count"]}</td>'
                f'<td><span class="tag-pass">{repl}</span></td></tr>'
            )
        d += '</table>'
        st.markdown(d, unsafe_allow_html=True)

    # 一键修复
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    if not st.session_state.is_fixed:
        st.caption("自动修复违禁词替换、标签补齐、特殊替换规则")
        if st.button("一键修复", type="primary", use_container_width=True, key="btn_fix"):
            ft, fb, ftg, changes = auto_fix_all(titles, body, tags, config)
            st.session_state.fixed_titles = ft
            st.session_state.fixed_body = fb
            st.session_state.fixed_tags = ftg
            st.session_state.changes = changes
            st.session_state.is_fixed = True
            st.session_state.results = run_all_checks(ft, fb, ftg, config)
            st.rerun()
    else:
        changes = st.session_state.changes
        fixed_body = st.session_state.fixed_body
        fixed_titles = st.session_state.fixed_titles
        fixed_tags = st.session_state.fixed_tags

        st.success(f"已修复 {len(changes)} 处问题")

        # 变更记录
        st.markdown('<div class="section-label">变更记录</div>', unsafe_allow_html=True)
        ch = '<table class="audit-table"><tr><th>类型</th><th>原文</th><th>修改为</th><th>次数</th></tr>'
        for c in changes:
            ch += (
                f'<tr><td><span class="tag-info">{c["type"]}</span></td>'
                f'<td><span class="hl-bad">{c["old"]}</span></td>'
                f'<td><span class="hl-good">{c["new"]}</span></td>'
                f'<td>{c.get("count", 1)}</td></tr>'
            )
        ch += '</table>'
        st.markdown(ch, unsafe_allow_html=True)

        # 对比
        st.markdown('<div class="section-label">正文对比</div>', unsafe_allow_html=True)
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown('<div class="diff-label orig">原稿</div>', unsafe_allow_html=True)
            orig_hl = highlight_original(body, changes)
            st.markdown(
                f'<div class="diff-panel original">{orig_hl.replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )
            with st.expander("复制原稿全文"):
                full_orig = build_full_text(titles, body, tags)
                st.text_area("Ctrl+A 全选复制", value=full_orig, height=200, key="copy_orig")

        with col_r:
            st.markdown('<div class="diff-label rev">修复后</div>', unsafe_allow_html=True)
            rev_hl = highlight_revised(fixed_body, changes)
            st.markdown(
                f'<div class="diff-panel revised">{rev_hl.replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )
            with st.expander("复制修复后全文"):
                full_fixed = build_full_text(fixed_titles, fixed_body, fixed_tags)
                st.text_area("Ctrl+A 全选复制", value=full_fixed, height=200, key="copy_fixed")

        # 标题编辑
        title_kw_r = find_check(st.session_state.results, "title_keywords")
        if not title_kw_r["pass"]:
            st.markdown("---")
            st.warning(f"标题关键词缺失：{'、'.join(title_kw_r['missing'])}，请编辑标题补充")
            edited_fix_titles = []
            for i, t in enumerate(fixed_titles):
                et = st.text_input(f"标题{i+1}", value=t, key=f"fix_title_{i}")
                edited_fix_titles.append(et)
            if st.button("保存标题", key="save_fix_titles"):
                st.session_state.fixed_titles = edited_fix_titles
                st.session_state.results = run_all_checks(
                    edited_fix_titles, st.session_state.fixed_body, st.session_state.fixed_tags, config,
                )
                st.rerun()


# ══════════════════════════════
#  Tab 2 — 卖点审核
# ══════════════════════════════
with tab2:
    if not st.session_state.is_fixed:
        st.markdown(
            '<div class="tab-locked">'
            '<div class="lock-icon">1</div>'
            '<p>请先完成「基础审核」中的一键修复</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        fixed_results = st.session_state.results
        sp_r = find_check(fixed_results, "selling_points")
        struct_r = find_check(fixed_results, "structure")

        # 评分卡
        sp_ok = sp_r["pass"]
        struct_ok = struct_r["pass"]
        score_html = '<div class="score-bar">'
        score_html += (
            f'<div class="score-item {"pass" if sp_ok else "fail"}">'
            f'<div class="label">卖点通过率</div>'
            f'<div class="value {"green" if sp_ok else "red"}">{sp_r["passed"]}/{sp_r["total"]}</div>'
            f'</div>'
        )
        score_html += (
            f'<div class="score-item {"pass" if struct_ok else "fail"}">'
            f'<div class="label">段落结构</div>'
            f'<div class="value {"green" if struct_ok else "red"}">{"通过" if struct_ok else "异常"}</div>'
            f'</div>'
        )
        score_html += '</div>'
        st.markdown(score_html, unsafe_allow_html=True)

        # 段落结构
        if not struct_r["pass"] and struct_r.get("missing_sections"):
            st.error(f"缺少内容：{'、'.join(struct_r['missing_sections'])}")
        if not struct_r.get("order_correct", True):
            st.warning(f"顺序不正确。期望：{'→'.join(struct_r['expected_order'])}，实际：{'→'.join(struct_r['actual_order'])}")

        # 卖点必提词
        st.markdown('<div class="section-label">卖点必提词检查</div>', unsafe_allow_html=True)
        st.markdown(render_sp_table(sp_r), unsafe_allow_html=True)

        if not sp_r["pass"]:
            missing_count = sp_r["total"] - sp_r["passed"]
            st.info(f"有 {missing_count} 个卖点必提词未通过，请在「人话修改」中补充")


# ══════════════════════════════
#  Tab 3 — 人话修改
# ══════════════════════════════
with tab3:
    if not st.session_state.is_fixed:
        st.markdown(
            '<div class="tab-locked">'
            '<div class="lock-icon">1</div>'
            '<p>请先完成「基础审核」中的一键修复</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        current_body = st.session_state.fixed_body
        paras_config = config["hard_rules"]["structure"]["paragraphs"]

        if not st.session_state.ai_done:
            col_ai1, col_ai2 = st.columns([1, 1])
            with col_ai1:
                if st.button("AI 一键人话改写", type="primary", use_container_width=True, key="btn_ai"):
                    with st.spinner("AI 正在改写中，请稍候..."):
                        result, error = rewrite_full_body(current_body, config, paras_config)
                        if result:
                            ai_t = list(st.session_state.fixed_titles)
                            ai_tg = st.session_state.fixed_tags
                            _, result, _, _ = auto_fix_all(ai_t, result, ai_tg, config)
                            st.session_state.ai_body = result
                            st.session_state.ai_done = True
                            st.session_state.ai_error = None
                            st.session_state.ai_results = run_all_checks(ai_t, result, ai_tg, config)
                        else:
                            st.session_state.ai_error = error
                        st.rerun()
            with col_ai2:
                if st.button("跳过，直接手动编辑", use_container_width=True, key="btn_skip_ai"):
                    st.session_state.ai_body = current_body
                    st.session_state.ai_done = True
                    ai_t = st.session_state.fixed_titles
                    ai_tg = st.session_state.fixed_tags
                    st.session_state.ai_results = run_all_checks(ai_t, current_body, ai_tg, config)
                    st.rerun()

            if st.session_state.ai_error:
                st.error(f"AI 调用失败: {st.session_state.ai_error}")
                st.info("你可以选择手动编辑，或检查 API key 后重试")
        else:
            ai_body = st.session_state.ai_body

            # 对比
            st.markdown('<div class="section-label">人话修改对比</div>', unsafe_allow_html=True)
            st.caption("红色=删除 · 黄色=被替换 · 绿色=新增")
            before_hl, after_hl = diff_highlight(st.session_state.fixed_body, ai_body)
            col_l, col_r = st.columns(2)
            with col_l:
                st.markdown('<div class="diff-label orig">修复后版本</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="diff-panel original">{before_hl}</div>', unsafe_allow_html=True)
                with st.expander("复制修复后全文"):
                    ft = build_full_text(st.session_state.fixed_titles, st.session_state.fixed_body, st.session_state.fixed_tags)
                    st.text_area("Ctrl+A 全选复制", value=ft, height=200, key="copy_fix2")

            with col_r:
                st.markdown('<div class="diff-label rev">人话修改版</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="diff-panel revised">{after_hl}</div>', unsafe_allow_html=True)
                with st.expander("复制人话版全文"):
                    fa = build_full_text(st.session_state.fixed_titles, ai_body, st.session_state.fixed_tags)
                    st.text_area("Ctrl+A 全选复制", value=fa, height=200, key="copy_ai")

            # 下载
            st.markdown('<div class="section-label">下载文档</div>', unsafe_allow_html=True)
            dl1, dl2 = st.columns(2)
            with dl1:
                diff_doc = generate_diff_docx(
                    st.session_state.fixed_titles,
                    st.session_state.fixed_body, ai_body,
                    st.session_state.fixed_tags,
                    title_label="人话修改 · 标注对比",
                )
                st.download_button(
                    "下载标注版 .docx", data=diff_doc,
                    file_name="人话修改_标注版.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            with dl2:
                clean_doc = generate_clean_docx(
                    st.session_state.fixed_titles, ai_body, st.session_state.fixed_tags,
                )
                st.download_button(
                    "下载纯净版 .docx", data=clean_doc,
                    file_name="人话修改_纯净版.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )

            # 在线微调
            with st.expander("在线微调"):
                edited_body = st.text_area("编辑正文", value=ai_body, height=400, key="edit_ai_body")
                st.caption(f"字数: {count_chinese(edited_body)}")
                edited_tags = st.text_area("编辑标签", value=st.session_state.fixed_tags, height=60, key="edit_ai_tags")
                edited_titles = []
                for i, t in enumerate(st.session_state.fixed_titles):
                    et = st.text_input(f"标题{i+1}", value=t, key=f"edit_ai_title_{i}")
                    edited_titles.append(et)
                if st.button("保存并重新审核", key="save_ai_edit"):
                    st.session_state.ai_body = edited_body
                    st.session_state.fixed_titles = edited_titles
                    st.session_state.fixed_tags = edited_tags
                    st.session_state.ai_results = run_all_checks(edited_titles, edited_body, edited_tags, config)
                    st.rerun()

            # 审核结果
            if st.session_state.ai_results:
                st.markdown('<div class="section-label">审核结果</div>', unsafe_allow_html=True)
                ai_r = st.session_state.ai_results
                all_ai_pass = all(r["pass"] for r in ai_r)
                ai_pass_count = sum(1 for r in ai_r if r["pass"])

                if all_ai_pass:
                    st.success(f"全部 {len(ai_r)} 项审核通过")
                else:
                    st.warning(f"审核 {ai_pass_count}/{len(ai_r)} 通过，{len(ai_r) - ai_pass_count} 项未通过")

                st.markdown(render_audit_table(ai_r), unsafe_allow_html=True)

                ai_sp = find_check(ai_r, "selling_points")
                with st.expander("查看卖点必提词明细"):
                    st.markdown(render_sp_table(ai_sp), unsafe_allow_html=True)

            # 进入终检
            st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
            if st.button("进入终检 →", type="primary", use_container_width=True, key="btn_final"):
                st.session_state.final_titles = list(st.session_state.fixed_titles)
                st.session_state.final_body = st.session_state.ai_body
                st.session_state.final_tags = st.session_state.fixed_tags
                st.session_state.final_results = run_all_checks(
                    st.session_state.fixed_titles, st.session_state.ai_body, st.session_state.fixed_tags, config,
                )
                st.rerun()


# ══════════════════════════════
#  Tab 4 — 终检
# ══════════════════════════════
with tab4:
    if not st.session_state.final_results:
        st.markdown(
            '<div class="tab-locked">'
            '<div class="lock-icon">3</div>'
            '<p>请先完成「人话修改」后点击进入终检</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        fr = st.session_state.final_results
        all_pass = all(r["pass"] for r in fr)
        final_body = st.session_state.final_body
        final_titles = st.session_state.final_titles
        final_tags = st.session_state.final_tags

        if all_pass:
            st.markdown(
                '<div class="final-pass-banner">'
                '<span class="pass-icon">✓</span>'
                '<div><strong>全部通过</strong><br><span>稿件可以提交了</span></div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            fp = sum(1 for r in fr if r["pass"])
            st.warning(f"终检 {fp}/{len(fr)} 通过，以下项目需要修改")

        # 审核表
        st.markdown(render_audit_table(fr), unsafe_allow_html=True)

        # 卖点逐条
        final_sp = find_check(fr, "selling_points")
        with st.expander("查看卖点必提词明细"):
            st.markdown(render_sp_table(final_sp), unsafe_allow_html=True)

        # 对比
        st.markdown('<div class="section-label">原稿 vs 终稿</div>', unsafe_allow_html=True)
        st.caption("红色=删除 · 黄色=被替换 · 绿色=新增")
        final_before_hl, final_after_hl = diff_highlight(body, final_body)
        col_fl, col_fr = st.columns(2)
        with col_fl:
            st.markdown('<div class="diff-label orig">原稿</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="diff-panel original">{final_before_hl}</div>', unsafe_allow_html=True)
        with col_fr:
            st.markdown('<div class="diff-label rev">终稿</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="diff-panel revised">{final_after_hl}</div>', unsafe_allow_html=True)

        # 元信息
        st.markdown('<div class="section-label">终稿信息</div>', unsafe_allow_html=True)
        info_cols = st.columns(3)
        with info_cols[0]:
            st.metric("字数", count_chinese(final_body))
        with info_cols[1]:
            st.metric("标题数", len(final_titles))
        with info_cols[2]:
            st.metric("标签数", final_tags.count("#"))

        for i, t in enumerate(final_titles):
            st.markdown(f"**标题{i+1}：** {t}")
        st.code(final_tags, language=None)

        # 下载
        st.markdown('<div class="section-label">下载文档</div>', unsafe_allow_html=True)
        dl_f1, dl_f2 = st.columns(2)
        with dl_f1:
            final_diff_doc = generate_diff_docx(
                final_titles, body, final_body, final_tags,
                title_label="终稿 · 原稿对比标注",
            )
            st.download_button(
                "下载标注版 .docx", data=final_diff_doc,
                file_name="终稿_标注版.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with dl_f2:
            final_clean_doc = generate_clean_docx(final_titles, final_body, final_tags)
            st.download_button(
                "下载终稿 .docx", data=final_clean_doc,
                file_name="终稿.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )

        # 复制
        with st.expander("复制终稿全文"):
            full_final = build_full_text(final_titles, final_body, final_tags)
            st.text_area("Ctrl+A 全选复制", value=full_final, height=300, key="copy_final")

        # 未通过 → 继续修改
        if not all_pass:
            with st.expander("继续修改"):
                ed_body = st.text_area("编辑正文", value=final_body, height=400, key="final_edit_body")
                st.caption(f"字数: {count_chinese(ed_body)}")
                ed_tags = st.text_area("编辑标签", value=final_tags, height=60, key="final_edit_tags")
                ed_titles = []
                for i, t in enumerate(final_titles):
                    et = st.text_input(f"标题{i+1}", value=t, key=f"final_edit_title_{i}")
                    ed_titles.append(et)
                if st.button("保存并重新终检", type="primary", key="btn_recheck"):
                    st.session_state.final_titles = ed_titles
                    st.session_state.final_body = ed_body
                    st.session_state.final_tags = ed_tags
                    st.session_state.final_results = run_all_checks(ed_titles, ed_body, ed_tags, config)
                    st.rerun()

"""UI 样式 - 基于 UI/UX Pro Max Bento Grid + Dimensional Layering 风格"""

MAIN_CSS = """
<style>
/* ====== 全局 ====== */
.block-container { max-width: 1400px; padding-top: 1rem; }

/* ====== Part 标题（圆角卡片+微阴影） ====== */
.part-header {
    padding: 18px 24px; border-radius: 16px; margin: 32px 0 18px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s;
}
.part-header:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.part-header h3 { margin: 0 0 4px 0; font-size: 1.2em; font-weight: 700; }
.part-sub { font-size: 0.82em; opacity: 0.65; }

.part-header.part1 {
    background: linear-gradient(135deg, #fce7f3, #dcfce7);
    border-left: 4px solid #ec4899;
}
.part-header.part2 {
    background: linear-gradient(135deg, #fef3c7, #ede9fe);
    border-left: 4px solid #8b5cf6;
}
.part-header.part3 {
    background: linear-gradient(135deg, #dbeafe, #e0e7ff);
    border-left: 4px solid #3b82f6;
}
.part-header.part4 {
    background: linear-gradient(135deg, #dcfce7, #f0fdf4);
    border-left: 4px solid #22c55e;
}

/* ====== 评分卡（Bento 卡片风格） ====== */
.score-bar {
    display: flex; gap: 12px; margin: 12px 0 22px 0; flex-wrap: wrap;
}
.score-item {
    flex: 1; min-width: 130px;
    background: #fff; border-radius: 16px;
    padding: 14px 18px; text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    border: 1px solid #f1f5f9;
    transition: transform 0.15s, box-shadow 0.15s;
}
.score-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.score-item.pass { border-left: 4px solid #22c55e; }
.score-item.fail { border-left: 4px solid #ef4444; }
.score-item .label { font-size: 0.78em; color: #64748b; margin-bottom: 4px; letter-spacing: 0.03em; }
.score-item .value { font-size: 1.35em; font-weight: 800; }
.score-item .value.green { color: #22c55e; }
.score-item .value.red { color: #ef4444; }

/* ====== 对比面板（层次阴影） ====== */
.diff-panel {
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px 24px;
    line-height: 1.9;
    font-size: 0.9em;
    min-height: 300px;
    background: #fff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.diff-panel.original { border-top: 3px solid #f87171; }
.diff-panel.revised  { border-top: 3px solid #4ade80; }

.diff-label {
    font-size: 0.8em; font-weight: 700; letter-spacing: 0.06em;
    margin-bottom: 12px; padding-bottom: 8px;
    border-bottom: 1px solid #f1f5f9;
}
.diff-label.orig { color: #ef4444; }
.diff-label.rev  { color: #22c55e; }

/* ====== 高亮标注 ====== */
.hl-bad {
    background: #fee2e2; color: #dc2626;
    padding: 1px 5px; border-radius: 4px;
    text-decoration: underline wavy #ef4444;
}
.hl-good {
    background: #dcfce7; color: #166534;
    padding: 1px 5px; border-radius: 4px;
}
.hl-change {
    background: #fef3c7; color: #92400e;
    padding: 1px 5px; border-radius: 4px;
    text-decoration: line-through;
}
.hl-note {
    font-size: 0.72em; color: #9ca3af;
    vertical-align: super;
}

/* ====== 审核表（圆角+阴影） ====== */
.audit-table {
    width: 100%; border-collapse: separate; border-spacing: 0;
    font-size: 0.85em; margin: 10px 0;
    border-radius: 12px; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    border: 1px solid #e2e8f0;
}
.audit-table th {
    background: #f8fafc; padding: 10px 14px; text-align: left;
    font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0;
}
.audit-table td {
    padding: 10px 14px; border-bottom: 1px solid #f1f5f9;
    background: #fff;
}
.audit-table tr:last-child td { border-bottom: none; }
.audit-table tr:hover td { background: #f8fafc; }

/* 卖点段落头 */
.sp-para-header {
    background: #fef3c7 !important; font-weight: 600; color: #7c3aed !important;
}

/* ====== 标签胶囊 ====== */
.tag-pass { display:inline-block; background:#dcfce7; color:#166534; padding:3px 10px; border-radius:20px; font-size:0.78em; margin:2px; font-weight:500; }
.tag-fail { display:inline-block; background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:20px; font-size:0.78em; margin:2px; font-weight:500; }
.tag-info { display:inline-block; background:#e0e7ff; color:#3730a3; padding:3px 10px; border-radius:20px; font-size:0.78em; margin:2px; font-weight:500; }
.tag-warn { display:inline-block; background:#fef3c7; color:#92400e; padding:3px 10px; border-radius:20px; font-size:0.78em; margin:2px; font-weight:500; }

/* ====== 下拉菜单不截断 ====== */
.stSelectbox [data-baseweb="select"] { min-width: 0; }
.stSelectbox [data-baseweb="select"] span { white-space: normal !important; overflow: visible !important; text-overflow: unset !important; }
.stSelectbox [role="listbox"] li { white-space: normal !important; }

/* ====== 侧边栏（浅色干净） ====== */
section[data-testid="stSidebar"] {
    background: #f8f9fb;
    border-right: 1px solid #e5e7eb;
}
section[data-testid="stSidebar"] .stMarkdown { color: #1f2937; }
section[data-testid="stSidebar"] .stCaption { color: #6b7280 !important; }
section[data-testid="stSidebar"] h3 { color: #7c3aed; }
section[data-testid="stSidebar"] hr { border-color: #e5e7eb; }
section[data-testid="stSidebar"] .stRadio label { color: #374151; }
section[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: #7c3aed; border: none; border-radius: 10px;
}
section[data-testid="stSidebar"] .stButton button[kind="secondary"] {
    background: #fff; color: #374151; border: 1px solid #d1d5db; border-radius: 10px;
}

/* ====== 全局按钮美化 ====== */
.stButton button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: transform 0.12s, box-shadow 0.12s !important;
}
.stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}
.stButton button[kind="primary"] {
    box-shadow: 0 2px 8px rgba(124,58,237,0.25) !important;
}
.stButton button[kind="primary"]:hover {
    box-shadow: 0 4px 16px rgba(124,58,237,0.35) !important;
}

/* ====== 下载按钮 ====== */
.stDownloadButton button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: transform 0.12s, box-shadow 0.12s !important;
}
.stDownloadButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}

/* ====== 输入框美化 ====== */
.stTextInput input, .stTextArea textarea {
    border-radius: 10px !important;
    border: 1px solid #d1d5db !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 2px rgba(124,58,237,0.15) !important;
}

/* ====== Expander 美化 ====== */
.streamlit-expanderHeader {
    border-radius: 12px !important;
    font-weight: 600 !important;
}
</style>
"""

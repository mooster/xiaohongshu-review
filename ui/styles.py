"""UI 样式 — Anthropic/Claude 设计语言 + Tabs 布局"""

MAIN_CSS = """
<style>
/* ====== 全局基础 ====== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');

:root {
    --bg-warm: #faf9f0;
    --bg-card: #ffffff;
    --bg-subtle: #f5f4eb;
    --accent: #d97757;
    --accent-light: #f4e0d6;
    --accent-hover: #c4633f;
    --text-primary: #1a1a1a;
    --text-secondary: #6b6560;
    --text-muted: #9c958e;
    --border: #e8e5dd;
    --border-light: #f0ede5;
    --green: #2d8a56;
    --green-bg: #e8f5ee;
    --red: #c53030;
    --red-bg: #fef2f2;
    --yellow-bg: #fdf6e3;
    --yellow-text: #8b6914;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 2px 8px rgba(0,0,0,0.06);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.08);
    --radius: 12px;
    --radius-lg: 16px;
}

/* 全局背景 */
.stApp, .stApp > header {
    background-color: var(--bg-warm) !important;
}
.block-container {
    max-width: 1200px;
    padding: 2rem 3rem 3rem 3rem !important;
}

/* 全局字体 */
html, body, .stApp, .stMarkdown, p, span, div, li, td, th, label, input, textarea, button, select {
    font-family: 'Inter', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ====== 页面标题 ====== */
.main-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin: 0 0 0.2rem 0;
    line-height: 1.3;
}
.main-subtitle {
    font-size: 0.85rem;
    color: var(--text-muted);
    font-weight: 400;
    margin-bottom: 1.5rem;
    letter-spacing: 0.02em;
}

/* ====== 空状态 ====== */
.empty-state {
    text-align: center;
    padding: 80px 40px;
    color: var(--text-muted);
}
.empty-state .empty-icon {
    font-size: 2.5rem;
    color: var(--accent);
    opacity: 0.4;
    margin-bottom: 16px;
}
.empty-state h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 6px;
}
.empty-state p {
    font-size: 0.85rem;
    color: var(--text-muted);
}

/* ====== Tabs 样式 ====== */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--bg-card);
    border-radius: var(--radius) var(--radius) 0 0;
    border: 1px solid var(--border);
    border-bottom: none;
    padding: 4px 4px 0 4px;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.85rem;
    color: var(--text-muted);
    padding: 12px 24px;
    border-radius: var(--radius) var(--radius) 0 0;
    border: none;
    background: transparent;
    transition: all 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary);
    background: var(--bg-subtle);
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    background: var(--bg-warm) !important;
    border-bottom: 2px solid var(--accent) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: var(--accent) !important;
}
.stTabs [data-baseweb="tab-border"] {
    display: none;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 24px 0 0 0;
}

/* ====== Tab 锁定状态 ====== */
.tab-locked {
    text-align: center;
    padding: 60px 40px;
    color: var(--text-muted);
    background: var(--bg-card);
    border-radius: var(--radius);
    border: 1px dashed var(--border);
    margin: 20px 0;
}
.tab-locked .lock-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--bg-subtle);
    color: var(--text-muted);
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 12px;
}
.tab-locked p {
    font-size: 0.88rem;
    color: var(--text-muted);
    margin: 0;
}

/* ====== 区块标签 ====== */
.section-label {
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--text-secondary);
    letter-spacing: 0.03em;
    text-transform: uppercase;
    margin: 28px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-light);
}

/* ====== 评分卡 ====== */
.score-bar {
    display: flex; gap: 14px; margin: 8px 0 24px 0; flex-wrap: wrap;
}
.score-item {
    flex: 1; min-width: 120px;
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 16px 20px;
    text-align: center;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s ease;
}
.score-item:hover { box-shadow: var(--shadow-md); }
.score-item.pass { border-bottom: 2px solid var(--green); }
.score-item.fail { border-bottom: 2px solid var(--red); }
.score-item .label {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 500;
}
.score-item .value {
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}
.score-item .value.green { color: var(--green); }
.score-item .value.red { color: var(--red); }

/* ====== 状态标签 ====== */
.status-pass {
    display: inline-block;
    background: var(--green-bg);
    color: var(--green);
    padding: 2px 10px;
    border-radius: 4px;
    font-size: 0.78rem;
    font-weight: 600;
}
.status-fail {
    display: inline-block;
    background: var(--red-bg);
    color: var(--red);
    padding: 2px 10px;
    border-radius: 4px;
    font-size: 0.78rem;
    font-weight: 600;
}

/* ====== 对比面板 ====== */
.diff-panel {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    line-height: 2;
    font-size: 0.88rem;
    min-height: 300px;
    background: var(--bg-card);
    box-shadow: var(--shadow-sm);
    color: var(--text-primary);
}
.diff-panel.original { border-top: 2px solid var(--red); }
.diff-panel.revised  { border-top: 2px solid var(--green); }

.diff-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    margin-bottom: 10px;
    text-transform: uppercase;
}
.diff-label.orig { color: var(--red); }
.diff-label.rev  { color: var(--green); }

/* ====== 高亮标注 ====== */
.hl-bad {
    background: var(--red-bg);
    color: var(--red);
    padding: 1px 4px;
    border-radius: 3px;
    text-decoration: line-through;
}
.hl-good {
    background: var(--green-bg);
    color: var(--green);
    padding: 1px 4px;
    border-radius: 3px;
}
.hl-change {
    background: var(--yellow-bg);
    color: var(--yellow-text);
    padding: 1px 4px;
    border-radius: 3px;
    text-decoration: line-through;
}

/* ====== 审核表 ====== */
.audit-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.85rem;
    margin: 8px 0 16px 0;
    border-radius: var(--radius);
    overflow: hidden;
    border: 1px solid var(--border);
    background: var(--bg-card);
}
.audit-table th {
    background: var(--bg-subtle);
    padding: 10px 16px;
    text-align: left;
    font-weight: 600;
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.audit-table td {
    padding: 10px 16px;
    border-bottom: 1px solid var(--border-light);
    color: var(--text-primary);
}
.audit-table tr:last-child td { border-bottom: none; }
.audit-table tr:hover td { background: var(--bg-subtle); }

.sp-para-header {
    background: var(--bg-subtle) !important;
    font-weight: 600;
    color: #8b6cc1 !important;
    font-size: 0.82rem;
}

/* ====== 标签胶囊 ====== */
.tag-pass {
    display: inline-block;
    background: var(--green-bg);
    color: var(--green);
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.76rem;
    margin: 2px;
    font-weight: 500;
}
.tag-fail {
    display: inline-block;
    background: var(--red-bg);
    color: var(--red);
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.76rem;
    margin: 2px;
    font-weight: 500;
}
.tag-info {
    display: inline-block;
    background: #eef2ff;
    color: #4338ca;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.76rem;
    margin: 2px;
    font-weight: 500;
}
.tag-warn {
    display: inline-block;
    background: var(--yellow-bg);
    color: var(--yellow-text);
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.76rem;
    margin: 2px;
    font-weight: 500;
}

/* ====== 侧边栏 ====== */
section[data-testid="stSidebar"] {
    background: #f7f6ee !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stMarkdown { color: var(--text-primary); }
section[data-testid="stSidebar"] .stCaption { color: var(--text-muted) !important; }

/* 侧边栏品牌 */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 4px;
    padding: 8px 0;
}
.brand-icon {
    font-size: 2rem;
    color: var(--accent);
    line-height: 1;
}
.brand-text {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}
.sidebar-section-title {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}

section[data-testid="stSidebar"] hr {
    border-color: var(--border) !important;
    margin: 12px 0;
}

/* ====== 下拉菜单 ====== */
.stSelectbox [data-baseweb="select"] { min-width: 0; }
.stSelectbox [data-baseweb="select"] span {
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
}
.stSelectbox [role="listbox"] li { white-space: normal !important; }

/* ====== 按钮 ====== */
.stButton button {
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.15s ease !important;
    border: 1px solid var(--border) !important;
}
.stButton button:hover {
    box-shadow: var(--shadow-md) !important;
}
.stButton button[kind="primary"] {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: #fff !important;
}
.stButton button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
    border-color: var(--accent-hover) !important;
    box-shadow: 0 2px 12px rgba(217,119,87,0.3) !important;
}

/* ====== 下载按钮 ====== */
.stDownloadButton button {
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border: 1px solid var(--border) !important;
    transition: all 0.15s ease !important;
}
.stDownloadButton button:hover {
    box-shadow: var(--shadow-md) !important;
}

/* ====== 输入框 ====== */
.stTextInput input, .stTextArea textarea {
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    background: var(--bg-card) !important;
    font-size: 0.88rem !important;
    transition: border-color 0.2s ease !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-light) !important;
}

/* ====== Expander ====== */
.streamlit-expanderHeader {
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    color: var(--text-secondary) !important;
}

/* ====== 分隔线 ====== */
hr {
    border-color: var(--border) !important;
    opacity: 0.6;
}

/* ====== 进度条 ====== */
.progress-step {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 3px 0;
    transition: background 0.15s ease;
}
.progress-step .step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    font-size: 0.68rem;
    font-weight: 700;
}
.progress-step.done {
    background: var(--green-bg);
    color: var(--green);
}
.progress-step.done .step-num {
    background: var(--green);
    color: #fff;
}
.progress-step.pending {
    background: transparent;
    color: var(--text-muted);
}
.progress-step.pending .step-num {
    background: var(--bg-subtle);
    color: var(--text-muted);
}

/* ====== 终检通过横幅 ====== */
.final-pass-banner {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px 28px;
    background: var(--green-bg);
    border: 1px solid #b7e4c7;
    border-radius: var(--radius);
    margin: 8px 0 20px 0;
}
.final-pass-banner .pass-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--green);
    color: #fff;
    font-size: 1.1rem;
    font-weight: 700;
    flex-shrink: 0;
}
.final-pass-banner strong {
    font-size: 1rem;
    color: var(--green);
}
.final-pass-banner span {
    font-size: 0.82rem;
    color: var(--text-secondary);
}

/* ====== Metric 美化 ====== */
[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    box-shadow: var(--shadow-sm);
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.3rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}

/* ====== 隐藏 Streamlit 默认元素 ====== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {
    background: transparent !important;
}
</style>
"""

"""UI 样式"""

MAIN_CSS = """
<style>
/* 全局 */
.block-container { max-width: 1400px; padding-top: 1rem; }

/* ====== Part 标题 ====== */
.part-header {
    padding: 14px 20px; border-radius: 10px; margin: 28px 0 16px 0;
}
.part-header h3 { margin: 0 0 2px 0; font-size: 1.15em; }
.part-sub { font-size: 0.82em; opacity: 0.7; }
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

/* ====== 评分卡 ====== */
.score-bar {
    display: flex; gap: 10px; margin: 10px 0 20px 0; flex-wrap: wrap;
}
.score-item {
    flex: 1; min-width: 120px;
    background: #fff; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 10px 14px; text-align: center;
}
.score-item.pass { border-left: 4px solid #22c55e; }
.score-item.fail { border-left: 4px solid #ef4444; }
.score-item .label { font-size: 0.78em; color: #64748b; margin-bottom: 2px; }
.score-item .value { font-size: 1.2em; font-weight: 700; }
.score-item .value.green { color: #22c55e; }
.score-item .value.red { color: #ef4444; }

/* ====== 对比面板 ====== */
.diff-panel {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px 20px;
    line-height: 1.9;
    font-size: 0.9em;
    min-height: 300px;
    background: #fff;
}
.diff-panel.original { border-top: 3px solid #f87171; }
.diff-panel.revised  { border-top: 3px solid #4ade80; }

.diff-label {
    font-size: 0.75em; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; margin-bottom: 10px; padding-bottom: 6px;
    border-bottom: 1px solid #f1f5f9;
}
.diff-label.orig { color: #ef4444; }
.diff-label.rev  { color: #22c55e; }

/* 高亮 */
.hl-bad {
    background: #fee2e2; color: #dc2626;
    padding: 1px 4px; border-radius: 3px;
    text-decoration: underline wavy #ef4444;
}
.hl-good {
    background: #dcfce7; color: #166534;
    padding: 1px 4px; border-radius: 3px;
}
.hl-note {
    font-size: 0.72em; color: #9ca3af;
    vertical-align: super;
}

/* ====== 审核表 ====== */
.audit-table {
    width: 100%; border-collapse: collapse;
    font-size: 0.85em; margin: 8px 0;
}
.audit-table th {
    background: #f8fafc; padding: 8px 12px; text-align: left;
    font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0;
}
.audit-table td {
    padding: 8px 12px; border-bottom: 1px solid #f1f5f9;
}
.audit-table tr:hover td { background: #fafbfc; }

/* 黄紫色卖点段落头 */
.sp-para-header {
    background: #fef3c7 !important; font-weight: 600; color: #7c3aed !important;
}

/* ====== 标签 ====== */
.tag-pass { display:inline-block; background:#dcfce7; color:#166534; padding:2px 8px; border-radius:12px; font-size:0.78em; margin:1px; }
.tag-fail { display:inline-block; background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:12px; font-size:0.78em; margin:1px; }
.tag-info { display:inline-block; background:#e0e7ff; color:#3730a3; padding:2px 8px; border-radius:12px; font-size:0.78em; margin:1px; }
.tag-warn { display:inline-block; background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:12px; font-size:0.78em; margin:1px; }

/* ====== 侧边栏 ====== */
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
    background: #7c3aed; border: none;
}
section[data-testid="stSidebar"] .stButton button[kind="secondary"] {
    background: #fff; color: #374151; border: 1px solid #d1d5db;
}
</style>
"""

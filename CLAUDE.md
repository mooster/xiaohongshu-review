# 小红书KOL审稿系统 - 项目记忆

## 项目概述
赞意AI内部审稿工具。公司是KOL投放广告公司，服务奶粉客户（雀巢能恩全护/ENCARE）。KOL写完小红书文稿后，员工用此工具按审核标准审稿。

## 当前进度（2026-02-10）
- **方向1（育婴师防敏科普）**：80% 完成，可正常使用
- **方向3（家族过敏史）**：已完成 JSON 配置，已上线
- **方向4（剖腹产）**：已完成 JSON 配置，已上线
- **方向2, 5-10**：待做，项目负责人填写模板后转 JSON 配置即可
- **模板文件**：`/Users/mac/Desktop/审稿规则填写模板.txt`（已给项目负责人）
- **完成方向10 = 应用全部完成**
- **GitHub 已推送**：v2.1 最新代码已在 main 分支
- **UI 大改版**：Tabs 标签页布局 + Claude/Anthropic 暖色设计语言

## 技术栈
- **框架**: Streamlit (Python 3.9 本地 / 3.12 服务器)
- **LLM**: Google Gemini 2.0 Flash (通过 google-generativeai SDK)
- **配置**: JSON 驱动审核规则（换品牌/方向只需换 JSON）
- **部署**: 阿里云 ECS 47.84.122.249:8200（nginx→8201）+ 本地 localhost:8501
- **Skills**: Humanizer（反AI痕迹）、UI/UX Pro Max（设计参考）

## 项目结构
```
xiaohongshu-review/
├── app.py                         # 主入口，Tabs 4步审核流程
├── .env                           # GOOGLE_API_KEY（不提交git）
├── .streamlit/config.toml         # Streamlit配置（本地8501，服务器8201）
├── configs/
│   ├── nengen_direction1.json     # 能恩方向1（育婴师防敏科普）
│   ├── nengen_direction3.json     # 能恩方向3（家族过敏史）
│   ├── nengen_direction4.json     # 能恩方向4（剖腹产）
│   └── _template.json             # 模板文件（_开头不显示在下拉菜单）
├── core/
│   ├── __init__.py
│   ├── config_loader.py           # JSON配置加载（_开头跳过, 标签显示"方向N · 名称"）
│   ├── text_utils.py              # 中文字数统计、标签提取、docx读取
│   ├── hard_checks.py             # 7项硬性审核检查引擎
│   ├── auto_fix.py                # 一键修复 + 高亮标注 + diff_highlight()字符级对比
│   ├── doc_export.py              # .docx导出（标注版红/黄/绿 + 纯净版）
│   └── llm_client.py              # Google Gemini API封装（含Humanizer反AI prompt）
├── ui/
│   ├── __init__.py
│   └── styles.py                  # CSS样式（Anthropic/Claude设计语言 + Tabs）
├── test_review.py                 # 测试脚本
└── review_compare.py              # 对比脚本
```

## 审核流程（Tabs 4步）
1. **基础审核** Tab：字数、标题、标签、违禁词 → 评分卡 → 一键修复 → 变更记录 → 左右对比
2. **卖点审核** Tab：段落结构 + 卖点通过率评分卡 → 必提词逐条检查表（锁定：需先完成基础审核）
3. **人话修改** Tab：AI改写 → diff对比 → 下载标注版/纯净版.docx → 在线微调 → 审核结果（锁定：需先完成基础审核）
4. **终检** Tab：全部通过绿色 banner → 审核表 → 原稿vs终稿对比 → 字数/标题/标签 metric → 下载（锁定：需先进入终检）

## UI 设计语言（2026-02-10 大改版）
- **参考**: Anthropic/Claude 官网设计
- **背景**: 暖奶油色 `#faf9f0`
- **强调色**: 陶土色 `#d97757`（按钮、选中态、品牌图标）
- **字体**: Inter + Noto Sans SC，抗锯齿渲染
- **布局**: Tabs 标签页切换，不再长页面滚动
- **卡片**: 白色背景 + 细边框 `#e8e5dd` + 微阴影
- **状态标签**: `通过`/`未通过` 文字胶囊替代 emoji ✅❌
- **进度条**: 数字圆圈 + 绿色完成状态
- **终检通过**: 绿色横幅 + 打勾圆圈
- **隐藏**: Streamlit 默认 header/footer/hamburger menu
- **无 emoji**: 全局去 emoji 化，更专业

## 关键设计决策
- **段落结构检测**: 不按 \n\n 严格分段，在全文搜索锚点关键词判断内容是否存在+顺序
- **AI后处理**: AI改写后自动跑 auto_fix_all 清理可能生成的违禁词
- **Humanizer反AI**: prompt融入24条反AI痕迹规则（中文适配版），禁止"不仅...而且"、三段排比、空洞总结等AI句式
- **AI提示词**: 字数目标820-880（留安全余量），违禁词+替换规则全部写入prompt
- **diff对比**: difflib.SequenceMatcher字符级对比，红色=删除、黄色=被替换、绿色=新增
- **docx导出**: 标注版（红色划线/黄底划线/绿色底色）+ 纯净版，用python-docx生成
- **特殊替换**: 通用逻辑支持 skip_if_followed_by 字段，避免双重替换
- **Tab锁定**: 未完成前置步骤的Tab显示锁定提示，引导用户按流程走

## 审核规则概要
### 方向1（育婴师防敏科普）
- 字数800-900, 标题3个(适度水解/防敏/科普), 标签8个, 违禁词15个
- 特殊替换: "第一口奶"→"第一口奶粉"、"雀巢的尖峰水解技术"→"多项科学实证的雀巢尖峰水解科技"
- 4段落(敏敏现状→防敏水解技术→自护力→基础营养), 12卖点

### 方向3（家族过敏史 - 反向经验分享）
- 字数800-900, 标题3个(家族敏敏/遗传敏敏/防敏), 标签9个, 违禁词15个
- 5段落(反向经验→敏敏现状→防敏水解技术→自护力→基础营养), 13卖点
- 独有锚点: 家族敏敏史, 大宝敏敏, 担心二胎敏敏

### 方向4（剖腹产 - 反向经验分享）
- 字数800-900, 标题3个(剖宝/防敏/自护力), 标签10个, 违禁词16个
- 5段落(反向经验→自护力→敏敏现状→防敏水解技术→基础营养)，段落顺序与其他方向不同
- 独有: 剖腹产→剖一刀, 产道挤压/剖宝体质弱

## 部署信息
- **阿里云ECS**: 47.84.122.249（密码见本地凭据）
- **端口**: nginx 8200 → streamlit 8201（systemd ExecStart 已指定 --server.port 8201）
- **服务**: systemd streamlit.service（自动启动、自动重启）
- **项目路径**: /opt/xiaohongshu-review/
- **访问地址**: http://47.84.122.249:8200
- **部署方式**: rsync（服务器无 git，需 sshpass 密码登录）
- **安全问题**: SSH root密码登录（高风险）、无防火墙（全ACCEPT）、.env已修600、端口8000暴露（未知服务）

## API配置
- .env 中设置 GOOGLE_API_KEY（见.env文件，不提交）
- 模型: gemini-2.0-flash

## GitHub
- **仓库**: github.com/mooster/xiaohongshu-review
- **用户**: mooster (mu.chen828@gmail.com)
- **推送方式**: HTTPS + Personal Access Token（见本地凭据，不提交）
- **remote**: https://github.com/mooster/xiaohongshu-review.git
- **最新commit**: v2.1 多方向支持 + diff高亮 + docx导出 + UI升级 + 反AI优化
- **SSH注意**: 本地 ~/.ssh/id_ed25519 已被其他 GitHub 帐号占用，用 HTTPS+token 推送
- **推送命令**: 先 `git remote set-url origin https://<TOKEN>@github.com/mooster/xiaohongshu-review.git`，推完后恢复无token URL

## Claude Code Skills
- **Humanizer** (blader/humanizer): ~/.claude/skills/humanizer/ — 24条反AI写作痕迹检查，已融入llm_client.py prompt
- **UI/UX Pro Max** (nextlevelbuilder): ~/.claude/skills/ui-ux-pro-max/ — 设计数据库，已用于styles.py升级

## 用户偏好
- 全程用中文沟通
- UI要简洁、专业、不要emoji
- 参考 Claude/Anthropic 官网设计风格
- Tabs 标签页布局（不要长页面滚动）
- 表格直接展开不折叠（卖点明细除外，用expander）
- 需要复制全文功能
- AI改写结果需要完整审核表
- diff对比需要红绿黄标注
- 下载.docx也要有颜色标注
- 定期保存 CLAUDE.md 项目记忆

## 待做事项
- 方向2, 5-10：待项目负责人填好模板 → 转JSON → 放configs/ → 自动出现在下拉菜单
- 服务器安全加固：禁用SSH密码登录、配置防火墙、排查端口8000
- 最新 Tabs UI 版本尚未 git commit+push（需下次推送）
- 业务流程可能调整：强制顺序通过、team lead管理权限（待确认）

# 小红书KOL审稿系统 - 项目记忆

## 项目概述
赞意AI内部审稿工具。公司是KOL投放广告公司，服务奶粉客户（雀巢能恩全护/ENCARE）。KOL写完小红书文稿后，员工用此工具按审核标准审稿。

## 当前进度（2026-02-09）
- **方向1**：80% 完成，用户满意，可正常使用
- **方向2-10**：待做，项目负责人填写模板后转 JSON 配置即可
- **模板文件**：`/Users/mac/Desktop/审稿规则填写模板.txt`（已给项目负责人）
- **完成方向10 = 应用全部完成**

## 技术栈
- **框架**: Streamlit (Python 3.9 本地 / 3.12 服务器)
- **LLM**: Google Gemini 2.0 Flash (通过 google-generativeai SDK)
- **配置**: JSON 驱动审核规则（换品牌/方向只需换 JSON）
- **部署**: 阿里云 ECS 47.84.122.249:8200（nginx→8201）+ 本地 localhost:8501
- **Skills**: Humanizer（反AI痕迹）、UI/UX Pro Max（设计参考）

## 项目结构
```
xiaohongshu-review/
├── app.py                         # 主入口，4步审核流程UI
├── .env                           # GOOGLE_API_KEY（不提交git）
├── .streamlit/config.toml         # Streamlit配置（本地8501，服务器8201）
├── configs/
│   ├── nengen_direction1.json     # 能恩方向1审核规则（已完成）
│   └── _template.json             # 模板文件（_开头不显示在下拉菜单）
├── core/
│   ├── __init__.py
│   ├── config_loader.py           # JSON配置加载（_开头文件自动跳过）
│   ├── text_utils.py              # 中文字数统计、标签提取、docx读取
│   ├── hard_checks.py             # 7项硬性审核检查引擎
│   ├── auto_fix.py                # 一键修复 + 高亮标注 + diff对比
│   ├── doc_export.py              # .docx导出（标注版+纯净版）
│   └── llm_client.py              # Google Gemini API封装（含Humanizer反AI prompt）
├── ui/
│   ├── __init__.py
│   └── styles.py                  # CSS样式（Bento Grid + Dimensional Layering风格）
├── test_review.py                 # 测试脚本
└── review_compare.py              # 对比脚本
```

## 审核流程（4步）
1. **① 基础审核**（粉绿色）：字数、标题、标签、违禁词 → 一键修复 → 左右红绿对比
2. **② 卖点审核**（黄紫色）：段落结构、必提词100%、人话卖点（修复后才显示）
3. **③ 人话修改**（蓝色）：AI改写 → 自动清理违禁词 → 红绿黄diff对比 → 下载标注版/纯净版.docx → 在线编辑 → 完整审核结果表
4. **④ 终检**（绿色）：全项检查、原稿vs终稿红绿黄对比、下载标注版/终稿.docx、卖点逐条验证

## 关键设计决策
- **段落结构检测**: 不按 \n\n 严格分段，而是在全文搜索锚点关键词判断内容是否存在+顺序
- **AI后处理**: AI改写后自动跑 auto_fix_all 清理可能生成的违禁词
- **Humanizer反AI**: prompt融入24条反AI痕迹规则（中文适配版），禁止"不仅...而且"、三段排比、空洞总结等AI句式
- **AI提示词**: 字数目标820-880（留安全余量），违禁词+替换规则全部写入prompt，角色设定为"真实博主不是AI"
- **diff对比**: difflib.SequenceMatcher字符级对比，红色=删除、黄色=被替换、绿色=新增
- **docx导出**: 标注版（红色划线/黄底划线/绿色底色）+ 纯净版，用python-docx生成
- **特殊替换**: 通用逻辑支持 skip_if_followed_by 字段，避免双重替换
- **UI风格**: 基于UI/UX Pro Max的Bento Grid（Apple风格圆角16px+阴影+hover上浮）

## 审核规则（能恩方向1）
- 字数: 800-900
- 标题: 3个，需含"适度水解""防敏""科普"
- 标签: 8个必须标签（#能恩全护 ×3, #能恩全护水奶 ×3, 等）
- 违禁词: 15个（敏宝、过敏→敏敏、新生儿→初生宝宝、免疫→自护力、等）
- 特殊替换: "第一口奶"→"第一口奶粉"、"雀巢的尖峰水解技术"→"多项科学实证的雀巢尖峰水解科技"
- 结构: 4个主题（敏敏现状→防敏水解技术→自护力→基础营养）
- 卖点: 12个卖点，10个有必提词

## 部署信息
- **阿里云ECS**: 47.84.122.249, root/Rootpwd123
- **端口**: nginx 8200 → streamlit 8201
- **服务**: systemd streamlit.service（自动启动、自动重启）
- **项目路径**: /opt/xiaohongshu-review/
- **访问地址**: http://47.84.122.249:8200

## API配置
- .env 中设置 GOOGLE_API_KEY=AIzaSyDxqTcDCVRHvbtGf-zlRqqNwRdIv1o83x8
- 模型: gemini-2.0-flash

## GitHub
- 仓库: github.com/mooster/xiaohongshu-review
- SSH公钥已生成: ~/.ssh/id_ed25519（待添加到GitHub）
- remote: https://github.com/mooster/xiaohongshu-review.git（待切SSH）

## Claude Code Skills
- **Humanizer** (blader/humanizer): ~/.claude/skills/humanizer/ — 24条反AI写作痕迹检查，已融入llm_client.py prompt
- **UI/UX Pro Max** (nextlevelbuilder): ~/.claude/skills/ui-ux-pro-max/ — 设计数据库，已用于styles.py升级

## 用户偏好
- 全程用中文沟通
- UI要简洁、不要过度复杂
- 侧边栏浅色背景
- 表格直接展开不折叠
- 需要复制全文功能
- AI改写结果需要完整审核表
- diff对比需要红绿黄标注
- 下载.docx也要有颜色标注

## 待做事项（方向2-10）
- 项目负责人填好模板 → 转成JSON配置 → 放入configs/文件夹 → 自动出现在下拉菜单
- 每个方向独立JSON，格式与nengen_direction1.json一致
- 业务流程未来可能调整：强制顺序通过、team lead管理权限（待确认）
- GitHub SSH push待完成

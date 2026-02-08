# 小红书KOL审稿系统 - 项目记忆

## 项目概述
赞意AI内部审稿工具。公司是KOL投放广告公司，服务奶粉客户（雀巢能恩全护/ENCARE）。KOL写完小红书文稿后，员工用此工具按审核标准审稿。

## 技术栈
- **框架**: Streamlit (Python 3.9)
- **LLM**: Google Gemini 2.0 Flash (通过 google-generativeai SDK)
- **配置**: JSON 驱动审核规则（换品牌/方向只需换 JSON）
- **部署**: localhost:8501

## 项目结构
```
xiaohongshu-review/
├── app.py                         # 主入口，4步审核流程UI
├── .env                           # GOOGLE_API_KEY（不提交git）
├── .streamlit/config.toml         # Streamlit配置（XSRF关闭、CORS关闭）
├── configs/
│   └── nengen_direction1.json     # 能恩方向1审核规则
├── core/
│   ├── __init__.py
│   ├── config_loader.py           # JSON配置加载
│   ├── text_utils.py              # 中文字数统计、标签提取、docx读取
│   ├── hard_checks.py             # 7项硬性审核检查引擎
│   ├── auto_fix.py                # 一键修复 + 高亮标注
│   └── llm_client.py              # Google Gemini API封装
├── ui/
│   ├── __init__.py
│   └── styles.py                  # CSS样式常量
├── test_review.py                 # 测试脚本
└── review_compare.py              # 对比脚本
```

## 审核流程（4步）
1. **① 基础审核**（粉绿色）：字数、标题、标签、违禁词 → 一键修复 → 左右对比
2. **② 卖点审核**（黄紫色）：段落结构、必提词100%、人话卖点（修复后才显示）
3. **③ 人话修改**（蓝色）：AI改写 → 自动清理违禁词 → 在线编辑 → 完整审核结果表
4. **④ 终检**（绿色）：全项检查、卖点逐条验证、终稿预览+复制

## 关键设计决策
- **段落结构检测**: 不按 \n\n 严格分段，而是在全文搜索锚点关键词判断内容是否存在+顺序
- **AI后处理**: AI改写后自动跑 auto_fix_all 清理可能生成的违禁词
- **AI提示词**: 字数目标设820-880（留安全余量避免超900），违禁词+替换规则全部写入prompt
- **复制全文**: 原稿和修复后都有"复制全文"功能（expander + text_area）
- **卖点表格**: 始终直接展开，不用折叠expander
- **标题编辑**: Part ① 修复后如标题关键词缺失，直接显示编辑框

## 审核规则（能恩方向1）
- 字数: 800-900
- 标题: 3个，需含"适度水解""防敏""科普"
- 标签: 8个必须标签（#能恩全护 ×3, #能恩全护水奶 ×3, 等）
- 违禁词: 15个（敏宝、过敏→敏敏、新生儿→初生宝宝、免疫→自护力、等）
- 结构: 4个主题（敏敏现状→防敏水解技术→自护力→基础营养）
- 卖点: 12个卖点，10个有必提词

## API配置
- .env 中设置 GOOGLE_API_KEY
- 模型: gemini-2.0-flash
- 之前尝试过 Anthropic 但用户的 key 格式不匹配（AQ.开头）

## 用户偏好
- 全程用中文沟通
- UI要简洁、不要过度复杂
- 侧边栏要浅色背景（不要深色）
- 表格直接展开，不要折叠
- 需要复制全文功能
- AI改写结果需要完整审核表

# CI环境AI翻译功能配置指南

## 🎯 问题现状
CI触发的报告缺少AI翻译和摘要能力，现在已修复此问题。

## ✅ 已完成的修复

### 1. CI工作流环境变量修复
已为所有CI工作流添加了翻译API密钥环境变量：

**修复的文件：**
- `.github/workflows/daily_papers.yml`
- `.github/workflows/weekly_papers.yml` 
- `.github/workflows/topic_papers.yml`

**添加的环境变量：**
```yaml
env:
  TZ: Asia/Shanghai
  DIDA_ACCESS_TOKEN: ${{ secrets.DIDA_ACCESS_TOKEN }}
  OPEN_ROUTE_API_KEY: ${{ secrets.OPEN_ROUTE_API_KEY }}  # ← 新增
```

### 2. 代码已支持双语翻译
所有报告生成脚本已支持AI翻译：

**配置状态：**
```python
# config.py
DIDA_API_CONFIG = {
    "enable_bilingual": True  # ✅ 已启用
}
```

**脚本支持状态：**
- ✅ `daily_papers.py` - 每日研究者动态监控，支持双语翻译滴答清单任务
- ✅ `weekly_papers.py` - 每周研究者动态汇总，支持双语翻译滴答清单任务
- ✅ `topic_papers.py` - 主题论文搜索，支持双语翻译滴答清单任务

## 🔧 需要完成的配置

### 步骤1：获取OpenRouter API密钥
1. 访问 [OpenRouter官网](https://openrouter.ai/)
2. 注册/登录账户
3. 进入 [API Keys页面](https://openrouter.ai/keys)
4. 创建新的API密钥
5. 复制密钥（格式：`sk-or-v1-xxxxxxxxxxxx...`）

### 步骤2：在GitHub Actions中设置密钥
1. 进入GitHub仓库页面
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 设置：
   - **Name:** `OPEN_ROUTE_API_KEY`
   - **Secret:** 你的OpenRouter API密钥
5. 点击 `Add secret`

### 步骤3：验证配置
设置完成后，下次CI运行时将自动启用AI翻译功能。

## 📊 功能效果对比

### 修复前（无AI翻译）
```
📄 每日研究者动态监控 - 2025-01-15
🎉 今日研究者发布 3 篇新论文！
📊 共发现 3 篇论文
...
```

### 修复后（包含AI翻译）
```
📄 每日研究者动态监控 - 2025-01-15 / 📄 Daily Researcher Activity Monitoring - 2025-01-15

中文版本 / Chinese Version:
🎉 今日研究者发布 3 篇新论文！
📊 共发现 3 篇论文
...

---

English Version:
🎉 Researchers published 3 new papers today!
📊 Total papers found: 3
...
```

## 🧪 本地测试

在设置GitHub Secrets之前，可以本地测试功能：

```bash
# 设置环境变量
export OPEN_ROUTE_API_KEY="your_api_key_here"
export DIDA_ACCESS_TOKEN="your_dida_token_here"

# 测试翻译服务
uv run python test_translation_service.py

# 测试滴答清单集成
uv run python test_dida_integration.py

# 测试完整功能
uv run python demo_bilingual_translation.py
```

## 💰 成本说明

**Gemini 2.0 Flash Lite 定价：**
- Input: $0.075/M tokens
- Output: $0.30/M tokens

**预估成本：**
- 单次翻译：~$0.0003 (约0.002人民币)
- 每月CI运行：~$0.036 (约0.25人民币)

## 🔍 故障排除

### 常见问题1: API密钥无效
```
❌ OpenRouter翻译服务连接失败: API调用失败: 401
```
**解决方案：**
- 检查GitHub Secrets中的 `OPEN_ROUTE_API_KEY` 是否正确
- 重新生成OpenRouter API密钥

### 常见问题2: CI中翻译功能未启用
**检查清单：**
- [ ] GitHub Secrets 已设置 `OPEN_ROUTE_API_KEY`
- [ ] GitHub Secrets 已设置 `DIDA_ACCESS_TOKEN`
- [ ] CI工作流使用最新版本（包含环境变量修复）

### 常见问题3: 翻译功能被禁用
```python
# 确保配置正确
DIDA_API_CONFIG = {
    "enable_bilingual": True  # 必须为True
}
```

## 🎉 配置完成后的效果

### CI运行时将显示：
```
✅ 翻译服务连接成功
🤖 使用模型: google/gemini-2.0-flash-lite-001
🌐 开始生成双语版本任务...
✅ 成功生成双语版本任务
✅ 滴答清单任务创建成功!
```

### 滴答清单中将收到：
- 包含中英双语内容的任务
- 智能翻译的论文摘要
- 保持格式和emoji的精美排版

现在您的ArXiv论文监控系统已具备完整的AI翻译能力！🚀 
# LLM翻译服务使用指南

## 🎯 功能概述

ArXiv Follow 系统现已集成LLM翻译服务，使用 OpenRouter 的 Gemini 2.0 Flash Lite 模型，可以将滴答清单任务信息自动翻译为中英双语版本。

### ✨ 主要特性
- 🌐 **中英双语翻译** - 自动生成任务的英文版本
- 🤖 **智能格式保持** - 保持emoji、时间格式和技术术语
- 📋 **双语任务创建** - 同时包含中英文内容的滴答清单任务
- 🔄 **降级处理** - 翻译失败时自动使用原始内容
- ⚙️ **灵活配置** - 可以启用/禁用翻译功能

## 🔑 获取 OpenRouter API 密钥

### 1. 注册 OpenRouter 账户
访问 [OpenRouter 官网](https://openrouter.ai/) 注册账户。

### 2. 获取 API 密钥
1. 登录后进入 [API Keys 页面](https://openrouter.ai/keys)
2. 点击 "Create Key" 创建新的API密钥
3. 复制生成的API密钥（格式类似：`sk-or-v1-xxxxxxxxxxxx...`）

### 3. 查看定价
- **Gemini 2.0 Flash Lite**: $0.075/M input tokens, $0.30/M output tokens
- 详细定价：https://openrouter.ai/google/gemini-2.0-flash-lite-001/api

## ⚙️ 配置翻译服务

### 本地开发环境

```bash
# macOS/Linux
export OPEN_ROUTE_API_KEY="your_openrouter_api_key_here"

# Windows (PowerShell)
$env:OPEN_ROUTE_API_KEY="your_openrouter_api_key_here"

# Windows (CMD)
set OPEN_ROUTE_API_KEY=your_openrouter_api_key_here
```

### GitHub Actions (CI/CD)

1. **添加 GitHub Secret**：
   - 进入你的GitHub仓库
   - 点击 `Settings` → `Secrets and variables` → `Actions`
   - 点击 `New repository secret`
   - Name: `OPEN_ROUTE_API_KEY`
   - Secret: 你的OpenRouter API密钥
   - 点击 `Add secret`

### 配置文件设置

编辑 `config.py` 文件中的翻译相关配置：

```python
# 滴答清单API配置
DIDA_API_CONFIG = {
    # ... 其他配置 ...
    
    # 是否启用双语翻译
    "enable_bilingual": True  # 设为 False 可禁用翻译
}

# LLM翻译服务配置
TRANSLATION_CONFIG = {
    # 是否启用翻译功能
    "enabled": True,
    
    # OpenRouter API配置
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "google/gemini-2.0-flash-lite-001",
        "max_tokens": 2000,
        "temperature": 0.3,
        "timeout": 60.0
    },
    
    # 默认翻译设置
    "default_settings": {
        "source_lang": "zh",       # 源语言
        "target_lang": "en",       # 目标语言
        "bilingual_format": True,  # 是否生成双语格式
        "preserve_emojis": True,   # 保持emoji表情
        "preserve_format": True    # 保持格式
    }
}
```

## 🧪 测试翻译功能

### 1. 测试翻译服务连接
```bash
# 测试OpenRouter API连接
uv run python translation_service.py
```

**预期输出**：
```
🧪 测试OpenRouter翻译服务连接...
✅ OpenRouter翻译服务连接成功
🤖 使用模型: google/gemini-2.0-flash-lite-001
🧪 测试翻译: Test Title

🧪 测试双语翻译功能...
✅ 双语翻译测试成功!
📋 双语标题: 📄 每日论文监控 - 2025-01-15 / Daily Paper Monitoring - 2025-01-15
📝 双语内容:
中文版本 / Chinese Version:
🎉 今日发现 3 篇新论文！...
```

### 2. 运行翻译服务完整测试
```bash
# 运行完整的翻译服务测试套件
uv run python test_translation_service.py
```

### 3. 测试集成功能
```bash
# 测试滴答清单集成（包含翻译功能）
uv run python test_dida_integration.py
```

## 🚀 使用方式

### 自动集成

所有主要脚本都已自动集成翻译功能：

```bash
# 每日监控 - 自动创建双语任务
uv run python daily_papers.py

# 周报生成 - 自动创建双语任务
uv run python weekly_papers.py

# 主题搜索 - 自动创建双语任务
uv run python topic_papers.py
```

### 手动调用翻译API

```python
from translation_service import translate_arxiv_task

# 生成双语版本
result = translate_arxiv_task(
    title="📄 每日论文监控 - 2025-01-15",
    content="今日发现 3 篇新论文！...",
    bilingual=True
)

if result.get("success"):
    print("中文标题:", result['chinese']['title'])
    print("英文标题:", result['english']['title'])
    print("双语标题:", result['bilingual']['title'])
```

## 📋 翻译效果示例

### 原始中文任务
```
📄 每日论文监控 - 2025-01-15

🎉 今日发现 3 篇新论文！

📊 共发现 3 篇论文

📝 详细信息:
监控了 5 位研究者

📊 论文分布:
• Zhang Wei: 2 篇
  1. Deep Learning Approaches for Cybersecurity...
  2. Federated Learning Privacy Protection...
• Li Ming: 1 篇
  1. AI-Powered Network Security Framework...

⏰ 生成时间: 2025-01-15 09:00:15
🤖 由 ArXiv Follow 系统自动生成
```

### 生成的双语任务
```
📄 每日论文监控 - 2025-01-15 / Daily Paper Monitoring - 2025-01-15

中文版本 / Chinese Version:
🎉 今日发现 3 篇新论文！

📊 共发现 3 篇论文

📝 详细信息:
监控了 5 位研究者

📊 论文分布:
• Zhang Wei: 2 篇
  1. Deep Learning Approaches for Cybersecurity...
  2. Federated Learning Privacy Protection...
• Li Ming: 1 篇
  1. AI-Powered Network Security Framework...

⏰ 生成时间: 2025-01-15 09:00:15
🤖 由 ArXiv Follow 系统自动生成

---

English Version:
🎉 Discovered 3 new papers today!

📊 Total papers found: 3

📝 Details:
Monitored 5 researchers

📊 Paper distribution:
• Zhang Wei: 2 papers
  1. Deep Learning Approaches for Cybersecurity...
  2. Federated Learning Privacy Protection...
• Li Ming: 1 paper
  1. AI-Powered Network Security Framework...

⏰ Generated at: 2025-01-15 09:00:15
🤖 Automatically generated by ArXiv Follow system
```

## 🛠️ 高级配置

### 自定义翻译模型

修改 `config.py` 中的模型配置：

```python
TRANSLATION_CONFIG = {
    "openrouter": {
        "model": "google/gemini-2.0-flash-lite-001",  # 可换其他模型
        "temperature": 0.3,   # 较低=更一致，较高=更创造性
        "max_tokens": 2000,   # 最大输出token数
    }
}
```

支持的其他模型：
- `anthropic/claude-3-haiku`
- `openai/gpt-4o-mini`
- `meta-llama/llama-3.1-8b-instruct`
- 更多模型请查看 [OpenRouter 模型列表](https://openrouter.ai/models)

### 禁用翻译功能

如果不想使用翻译功能：

#### 方法一：修改配置
```python
DIDA_API_CONFIG = {
    "enable_bilingual": False,  # 禁用双语翻译
}
```

#### 方法二：删除环境变量
```bash
unset OPEN_ROUTE_API_KEY
```

### 翻译语言设置

```python
TRANSLATION_CONFIG = {
    "default_settings": {
        "source_lang": "zh",       # 源语言：zh/en
        "target_lang": "en",       # 目标语言：en/zh
    }
}
```

## 🔧 故障排除

### 常见问题

#### 1. 翻译服务连接失败
```
❌ OpenRouter翻译服务连接失败: API调用失败: 401
```
**解决方案**：
- 检查 `OPEN_ROUTE_API_KEY` 环境变量是否正确设置
- 验证API密钥是否有效（重新生成新密钥）

#### 2. 翻译请求超时
```
❌ 翻译失败，使用原始内容: 网络错误: timeout
```
**解决方案**：
- 检查网络连接
- 增加超时时间：`TRANSLATION_CONFIG["openrouter"]["timeout"] = 120.0`

#### 3. 翻译结果解析失败
```
⚠️ 翻译结果JSON解析失败: Expecting value: line 1 column 1 (char 0)
```
**解决方案**：
- 这通常是临时问题，系统会自动使用降级处理
- 检查OpenRouter服务状态：https://status.openrouter.ai/

#### 4. 余额不足
```
❌ API调用失败: 402 - Insufficient credits
```
**解决方案**：
- 在 OpenRouter 后台充值账户余额
- 查看余额：https://openrouter.ai/activity

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 运行测试
from translation_service import test_translation_service
test_translation_service()
```

### 验证配置

```bash
# 检查所有环境变量
echo "DIDA_ACCESS_TOKEN: ${DIDA_ACCESS_TOKEN:0:10}..."
echo "OPEN_ROUTE_API_KEY: ${OPEN_ROUTE_API_KEY:0:20}..."

# 运行完整测试
uv run python test_dida_integration.py
```

## 💰 成本估算

### Gemini 2.0 Flash Lite 定价
- **输入**: $0.075/M tokens
- **输出**: $0.30/M tokens

### 典型使用成本
一个典型的ArXiv任务翻译：
- **输入**: ~800 tokens (中文任务内容)
- **输出**: ~800 tokens (英文翻译)
- **单次成本**: ~$0.0003 (约0.002人民币)

每日运行成本估算：
- **每日任务**: 1次翻译 × $0.0003 = $0.0003
- **周报任务**: 1次翻译 × $0.0005 = $0.0005  
- **主题搜索**: 1次翻译 × $0.0004 = $0.0004
- **月成本**: ~$0.036 (约0.25人民币)

## 📚 API 参考

### 核心函数

#### `translate_arxiv_task(title, content, bilingual=True)`
翻译ArXiv任务内容。

**参数**:
- `title` (str): 任务标题
- `content` (str): 任务内容
- `bilingual` (bool): 是否生成双语版本

**返回**:
```python
{
    "success": True,
    "chinese": {"title": "...", "content": "..."},
    "english": {"title": "...", "content": "..."},
    "bilingual": {"title": "...", "content": "..."},
    "model_used": "google/gemini-2.0-flash-lite-001"
}
```

#### `test_translation_service()`
测试翻译服务连接。

**返回**: `bool` - 连接是否成功

### 配置选项

完整的配置参数说明请参考 `config.py` 文件中的 `TRANSLATION_CONFIG` 部分。

## 🤝 贡献

如果您有改进建议或发现问题：

1. 提交 [Issue](https://github.com/your-repo/issues)
2. 创建 Pull Request
3. 改进翻译提示词或添加新的语言支持

## 📄 许可证

本翻译服务模块遵循项目的开源许可证。

---

**需要帮助？** 查看 [主要文档](../README.md) 或提交 [Issue](https://github.com/your-repo/issues)。 
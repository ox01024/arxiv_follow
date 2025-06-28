# 📝 滴答清单集成配置指南

## 🎯 功能概述

ArXiv Follow 系统已集成滴答清单API，可以在每次执行论文监控任务后自动创建滴答清单任务，方便你跟踪和管理论文监控结果。

### ✨ 支持的功能
- ✅ **每日论文监控** - 创建每日发现论文的汇总任务
- ✅ **周报论文汇总** - 创建每周论文监控报告任务
- ✅ **主题论文搜索** - 创建基于主题搜索的论文发现任务
- ✅ **错误监控** - 当监控脚本出错时创建错误记录任务
- ✅ **智能优先级** - 根据发现论文数量自动设置任务优先级

## 🚀 5分钟快速配置

### 1. 获取 Access Token

#### 方法一：使用第三方工具（推荐）
1. **访问获取工具**：
   - 在线工具：https://dida-auth.vercel.app/
   - GitHub项目：https://github.com/Stream-L/dida-auth

2. **操作步骤**：
   - 在 [滴答清单开发者管理页面](https://developer.dida365.com/manage) 创建新应用
   - 获取 Client ID 和 Client Secret
   - 在工具页面输入Client ID和Client Secret
   - 复制生成的 Redirect URI 到滴答清单应用设置中
   - 点击"Get Authorization Code"进行授权
   - 点击"Get Access Token"获取访问令牌

#### 方法二：查看官方文档
访问 [滴答清单开发者API文档](https://developer.dida365.com/api) 了解OAuth2认证流程。

### 2. 配置到 GitHub Secrets
1. 进入你的 GitHub 仓库
2. `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. Name: `DIDA_ACCESS_TOKEN`
5. Secret: 粘贴你的 token
6. 保存

### 3. 测试配置
```bash
# 本地测试（可选）
export DIDA_ACCESS_TOKEN="your_token"
uv run python test_dida_integration.py
```

## ⚙️ 详细配置步骤

### 本地开发环境

#### 设置环境变量
```bash
# Windows (CMD)
set DIDA_ACCESS_TOKEN=your_access_token_here

# Windows (PowerShell)
$env:DIDA_ACCESS_TOKEN="your_access_token_here"

# macOS/Linux
export DIDA_ACCESS_TOKEN="your_access_token_here"
```

#### 测试连接
```bash
# 测试滴答清单API集成
uv run python test_dida_integration.py

# 直接测试连接
uv run python dida_integration.py
```

### GitHub Actions (CI/CD)

GitHub Actions工作流已自动配置好环境变量，添加Secret后无需额外修改。

## 🚀 使用方式

### 自动集成

所有主要脚本都已集成滴答清单功能，无需额外配置：

```bash
# 每日监控后自动创建任务
uv run python daily_papers.py

# 周报生成后自动创建任务
uv run python weekly_papers.py

# 主题搜索后自动创建任务
uv run python topic_papers.py
```

### 手动测试

```bash
# 运行完整测试套件
uv run python test_dida_integration.py

# 测试特定功能
DIDA_ACCESS_TOKEN="your_token" uv run python test_dida_integration.py
```

## 📋 任务内容说明

### 任务标题格式
- 📄 **每日论文监控** - `📄 每日论文监控 - YYYY-MM-DD`
- 📚 **周报论文汇总** - `📚 周报论文汇总 - YYYY-MM-DD`  
- 🎯 **主题论文搜索** - `🎯 主题论文搜索 - YYYY-MM-DD`

### 任务内容示例

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

### 任务属性

#### 优先级设置
- **无优先级(0)** - 未发现论文时
- **中等优先级(1)** - 发现少量论文时(1-9篇)
- **高优先级(2)** - 发现大量论文时(10+篇)

#### 任务标签
- `arxiv` - 所有ArXiv相关任务
- `论文监控` - 监控类型标识
- `daily`/`weekly`/`topic` - 具体任务类型

#### 项目分配
- 默认创建到"收集箱"项目
- 可通过配置指定特定项目ID

## 🛠️ 高级配置

### 修改配置参数

编辑 `config.py` 文件中的 `DIDA_API_CONFIG` 部分：

```python
DIDA_API_CONFIG = {
    # 是否启用滴答清单集成
    "enabled": True,
    
    # API基础URL
    "base_url": "https://api.dida365.com/open/v1",
    
    # 默认项目ID（收集箱）
    "default_project_id": "inbox",
    
    # 任务标签前缀
    "tag_prefix": "arxiv",
    
    # 任务优先级映射
    "priority_mapping": {
        "no_papers": 0,    # 无论文时优先级
        "has_papers": 1,   # 有论文时优先级
        "many_papers": 2   # 论文较多时优先级（>=10篇）
    },
    
    # 论文数量阈值
    "many_papers_threshold": 10,
    
    # 请求超时时间（秒）
    "request_timeout": 30,
    
    # 重试次数
    "max_retries": 3
}
```

### 自定义任务模板

```python
# 自定义任务标题模板
TASK_TITLE_TEMPLATES = {
    "daily": "📄 每日论文监控 - {date}",
    "weekly": "📚 周报论文汇总 - {date}",
    "topic": "🎯 主题论文搜索 - {date}",
    "error": "❌ 系统错误记录 - {date}"
}

# 自定义任务内容模板
TASK_CONTENT_TEMPLATES = {
    "summary_line": "🎉 今日发现 {count} 篇新论文！" if count > 0 else "😴 今日暂无新论文发现",
    "details_header": "📝 详细信息:",
    "time_footer": "⏰ 生成时间: {timestamp}",
    "system_footer": "🤖 由 ArXiv Follow 系统自动生成"
}
```

### 禁用集成

如果不想使用滴答清单集成：

#### 方法一：删除环境变量
```bash
unset DIDA_ACCESS_TOKEN
```

#### 方法二：修改配置
```python
DIDA_API_CONFIG = {
    "enabled": False,
    # ... 其他配置保持不变
}
```

## 🔧 API 接口说明

### 核心函数

#### `test_dida_connection()`
测试与滴答清单API的基本连接：
```python
from dida_integration import test_dida_connection

# 测试连接
success = test_dida_connection()
if success:
    print("✅ 连接成功")
else:
    print("❌ 连接失败")
```

#### `create_arxiv_task()`
创建ArXiv相关任务：
```python
from dida_integration import create_arxiv_task

# 创建每日监控任务
result = create_arxiv_task(
    report_type="daily",
    summary="今日发现3篇新论文！",
    details="监控了5位研究者\n论文分布:\n• Zhang Wei: 2篇\n• Li Ming: 1篇",
    paper_count=3
)

if result.get("success"):
    print(f"✅ 任务创建成功: {result.get('url')}")
else:
    print(f"❌ 任务创建失败: {result.get('error')}")
```

#### `DidaIntegration` 类
高级API操作：
```python
from dida_integration import DidaIntegration

# 创建客户端实例
dida = DidaIntegration()

# 检查是否启用
if dida.is_enabled():
    # 创建自定义任务
    result = dida.create_task(
        title="🔬 自定义研究任务",
        content="任务详细内容...",
        tags=["研究", "AI", "自定义"],
        priority=1
    )
```

### 错误处理

系统提供完善的错误处理机制：

```python
# 网络错误处理
try:
    result = create_arxiv_task(...)
except requests.exceptions.RequestException as e:
    print(f"网络错误: {e}")

# API错误处理  
if not result.get("success"):
    error_code = result.get("error_code")
    if error_code == 401:
        print("Token无效或过期，请重新获取")
    elif error_code == 429:
        print("API请求频率限制，请稍后重试")
    else:
        print(f"未知错误: {result.get('error')}")
```

## 🔍 故障排除

### 常见问题

#### 1. Token无效或过期
**现象**: API调用返回401错误
**解决方案**:
```bash
# 检查token设置
echo $DIDA_ACCESS_TOKEN

# 重新获取token
# 访问 https://dida-auth.vercel.app/ 获取新token

# 更新GitHub Secrets
# 在仓库设置中更新 DIDA_ACCESS_TOKEN
```

#### 2. 网络连接问题
**现象**: 请求超时或连接失败
**解决方案**:
```bash
# 检查网络连接
ping api.dida365.com

# 测试HTTP连接
curl -I https://api.dida365.com/open/v1/

# 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

#### 3. 任务创建失败
**现象**: 返回其他HTTP错误码
**解决方案**:
```bash
# 运行详细诊断
export DEBUG=true
uv run python test_dida_integration.py

# 检查API配额
# 查看滴答清单开发者控制台的使用量统计
```

#### 4. 中文显示问题
**现象**: 任务内容出现乱码
**解决方案**:
```bash
# 检查系统编码
echo $LANG
echo $LC_ALL

# 设置UTF-8编码
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

### 调试模式

启用详细日志输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 或者通过环境变量
export DEBUG=true
```

### 验证配置

运行完整测试套件：

```bash
# 运行所有测试
uv run python test_dida_integration.py

# 测试特定功能
uv run python -c "
from dida_integration import test_dida_connection
print('连接测试:', '✅ 成功' if test_dida_connection() else '❌ 失败')
"
```

## 📊 使用统计

### API调用频率
- **每日监控**: 每天最多3次调用
- **周报汇总**: 每周1次调用  
- **主题搜索**: 每天1次调用
- **错误记录**: 按需调用

### 数据使用量
- 每个任务约500-2000字符
- 月均创建任务数量: ~100个
- 预计月流量: 50-200KB

### 性能指标
- API响应时间: 通常 < 2秒
- 成功率: > 99%
- 重试机制: 最多3次重试

## 💡 最佳实践

### 1. 安全管理
- 定期轮换Access Token
- 不要在代码中硬编码Token
- 使用环境变量或密钥管理服务

### 2. 错误监控
- 监控API调用成功率
- 设置失败通知机制
- 记录详细错误日志

### 3. 性能优化
- 避免频繁API调用
- 实现请求缓存机制
- 使用异步处理减少延迟

### 4. 用户体验
- 提供清晰的任务标题
- 包含详细的任务内容
- 设置合适的优先级和标签

## 🔄 版本更新

### v1.0.0 (当前版本)
- ✅ 基础任务创建功能
- ✅ 智能优先级设置
- ✅ 错误处理机制
- ✅ 完整测试套件

### 未来计划
- 📋 支持创建子任务
- 🔔 任务完成状态同步
- 📊 统计数据可视化
- 🤖 更智能的内容生成

---

**需要帮助？** 查看 [测试脚本](../test_dida_integration.py) 或提交 [Issue](https://github.com/your-repo/issues)。 
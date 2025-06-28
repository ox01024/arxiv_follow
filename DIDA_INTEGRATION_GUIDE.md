# 滴答清单API集成配置指南

## 🎯 功能概述

ArXiv Follow 系统已集成滴答清单API，可以在每次执行论文监控任务后自动创建滴答清单任务，方便你跟踪和管理论文监控结果。

### 支持的功能
- ✅ **每日论文监控** - 创建每日发现论文的汇总任务
- ✅ **周报论文汇总** - 创建每周论文监控报告任务
- ✅ **主题论文搜索** - 创建基于主题搜索的论文发现任务
- ✅ **错误监控** - 当监控脚本出错时创建错误记录任务
- ✅ **智能优先级** - 根据发现论文数量自动设置任务优先级

## 🔑 获取滴答清单 Access Token

### 方法一：使用第三方工具（推荐）

根据用户分享，可以使用第三方开发的获取工具：

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

### 方法二：查看滴答清单官方API文档

访问 [滴答清单开发者API文档](https://developer.dida365.com/api) 了解OAuth2认证流程。

## ⚙️ 配置 Access Token

### 本地开发环境

1. **设置环境变量**：
```bash
# Windows (CMD)
set DIDA_ACCESS_TOKEN=your_access_token_here

# Windows (PowerShell)
$env:DIDA_ACCESS_TOKEN="your_access_token_here"

# macOS/Linux
export DIDA_ACCESS_TOKEN="your_access_token_here"
```

2. **测试连接**：
```bash
# 测试滴答清单API集成
uv run python test_dida_integration.py

# 直接测试连接
uv run python dida_integration.py
```

### GitHub Actions (CI/CD)

1. **添加 GitHub Secret**：
   - 进入你的GitHub仓库
   - 点击 `Settings` → `Secrets and variables` → `Actions`
   - 点击 `New repository secret`
   - Name: `DIDA_ACCESS_TOKEN`
   - Secret: 你的滴答清单access token
   - 点击 `Add secret`

2. **GitHub Actions中的配置**：
GitHub Actions工作流已自动配置好环境变量，无需额外修改。

## 🚀 使用方式

### 自动集成

所有主要脚本都已集成滴答清单功能，无需额外配置：

- `daily_papers.py` - 每日监控后自动创建任务
- `weekly_papers.py` - 周报生成后自动创建任务  
- `topic_papers.py` - 主题搜索后自动创建任务

### 手动测试

```bash
# 测试API连接和任务创建
uv run python test_dida_integration.py

# 运行每日监控（会自动创建滴答清单任务）
uv run python daily_papers.py

# 运行周报生成（会自动创建滴答清单任务）
uv run python weekly_papers.py

# 运行主题搜索（会自动创建滴答清单任务）
uv run python topic_papers.py
```

## 📋 任务内容说明

### 任务标题格式
- 📄 每日论文监控 - YYYY-MM-DD
- 📚 周报论文汇总 - YYYY-MM-DD  
- 🎯 主题论文搜索 - YYYY-MM-DD

### 任务内容包含
- 📊 **统计信息** - 发现论文数量、监控研究者数量
- 📝 **详细信息** - 论文分布、研究者详情、论文标题摘要
- ⏰ **执行时间** - 任务执行的具体时间
- 🤖 **系统标识** - 标注为由ArXiv Follow系统自动生成

### 任务优先级
- **无优先级(0)** - 未发现论文时
- **中等优先级(1)** - 发现少量论文时(1-9篇)
- **高优先级(2)** - 发现大量论文时(10+篇)

### 任务标签
- `arxiv` - 所有ArXiv相关任务
- `论文监控` - 监控类型标识
- `daily`/`weekly`/`topic` - 具体任务类型

## 🛠️ 配置定制

### 修改配置

编辑 `config.py` 文件中的 `DIDA_API_CONFIG` 部分：

```python
DIDA_API_CONFIG = {
    # 是否启用滴答清单集成
    "enabled": True,
    
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
    "many_papers_threshold": 10
}
```

### 禁用集成

如果不想使用滴答清单集成，可以：

1. **删除环境变量**：
```bash
unset DIDA_ACCESS_TOKEN
```

2. **或修改配置**：
```python
DIDA_API_CONFIG = {
    "enabled": False,
    # ... 其他配置
}
```

## 🔧 故障排除

### 常见问题

1. **Token无效或过期**
   - 现象：API调用返回401错误
   - 解决：重新获取access token

2. **网络连接问题**
   - 现象：请求超时或连接失败
   - 解决：检查网络连接，确认滴答清单服务可访问

3. **任务创建失败**
   - 现象：返回其他HTTP错误码
   - 解决：检查token权限，查看错误详情

### 调试模式

启用详细日志输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 验证配置

运行完整测试套件：

```bash
# 运行所有测试
uv run python test_dida_integration.py

# 查看详细输出
DIDA_ACCESS_TOKEN="your_token" uv run python test_dida_integration.py
```

## 📚 API参考

### 主要函数

```python
from dida_integration import create_arxiv_task, test_dida_connection

# 测试连接
success = test_dida_connection()

# 创建任务
result = create_arxiv_task(
    report_type="daily",  # daily/weekly/topic
    summary="任务摘要",
    details="详细信息", 
    paper_count=5
)
```

### 返回值格式

```python
{
    "success": True,
    "task_id": "task_id_string",
    "title": "任务标题",
    "url": "https://dida365.com/webapp/#/task/task_id"
}
```

## 🔗 相关链接

- [滴答清单官网](https://dida365.com/)
- [滴答清单开发者文档](https://developer.dida365.com/api)
- [OAuth Token获取工具](https://dida-auth.vercel.app/)
- [ArXiv Follow 项目主页](https://github.com/your-username/arxiv_follow)

## 💡 提示

- Access Token建议定期更新以确保安全
- 可以在滴答清单Web版或App中查看和管理自动创建的任务
- 任务创建失败不会影响论文监控脚本的正常执行
- 建议在本地先测试API连接，确认无误后再配置到GitHub Actions中 
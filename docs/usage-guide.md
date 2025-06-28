# 📖 详细使用指南

## 🎯 系统概述

ArXiv Follow 是一个自动化论文监控系统，支持三种主要功能：
- **每日监控** - 跟踪特定研究者的最新论文
- **周报汇总** - 生成研究者论文发布趋势报告
- **主题搜索** - 基于研究领域的智能论文搜索

## 📋 功能详解

### 每日监控 (`daily_papers.py`)

#### 🎯 功能说明
- 监控配置的研究者在指定日期发布的论文
- 支持精确日期搜索和灵活日期范围
- 自动生成每日报告并保存

#### 🚀 使用方法
```bash
# 默认搜索当天论文
uv run python daily_papers.py

# 搜索指定日期论文
uv run python daily_papers.py --date 2025-01-15

# 搜索日期范围论文
uv run python daily_papers.py --date-from 2025-01-10 --date-to 2025-01-15
```

#### 📊 输出格式
```
🔍 每日论文监控 - 获取研究者当天发布的论文
时间: 2025-01-15 09:00:00

找到 3 个研究者:
==================================================
1. 姓名: Zhang Wei
2. 姓名: Li Ming
3. 姓名: Wang Hao

🔍 正在搜索 2025-01-15 当天发布的论文...

✅ 找到 2 篇新论文!
👨‍🔬 Zhang Wei (1 篇论文):
📄 Deep Learning Approaches for Cybersecurity
🔗 arXiv ID: 2501.12345
🌐 链接: https://arxiv.org/abs/2501.12345

👨‍🔬 Li Ming (1 篇论文):
📄 Federated Learning in Healthcare Applications
🔗 arXiv ID: 2501.12346
🌐 链接: https://arxiv.org/abs/2501.12346
```

### 周报汇总 (`weekly_papers.py`)

#### 🎯 功能说明
- 生成过去一周的论文发布统计
- 分析研究者活跃度和发布趋势
- 提供周度数据汇总

#### 🚀 使用方法
```bash
# 生成默认周报（过去7天）
uv run python weekly_papers.py

# 生成指定周数的报告
uv run python weekly_papers.py --weeks 2

# 生成自定义日期范围报告
uv run python weekly_papers.py --date-from 2025-01-01 --date-to 2025-01-07
```

#### 📊 输出内容
- 总论文数量统计
- 各研究者发布数量排名
- 日期分布分析
- 热门研究方向识别

### 研究者跟踪 (`follow_researchers.py`)

#### 🎯 功能说明
- 获取和管理研究者列表
- 验证研究者姓名格式
- 支持本地和远程数据源

#### 🚀 使用方法
```bash
# 查看研究者列表
uv run python follow_researchers.py --list

# 验证研究者格式
uv run python follow_researchers.py --validate

# 搜索特定研究者
uv run python follow_researchers.py --search "Zhang Wei"
```

## 🔧 配置管理

### 配置文件 (`config.py`)

系统配置集中在 `config.py` 文件中：

```python
# Google Sheets TSV 导出链接
RESEARCHERS_TSV_URL = "https://docs.google.com/..."

# 默认搜索主题
DEFAULT_TOPICS = ["cs.AI", "cs.CR"]

# HTTP请求超时时间（秒）
REQUEST_TIMEOUT = 30.0

# 滴答清单API配置
DIDA_API_CONFIG = {
    "enabled": True,
    "base_url": "https://api.dida365.com/open/v1",
    "default_project_id": "inbox",
    # ... 更多配置项
}
```

### 环境变量支持

系统支持通过环境变量覆盖配置：

```bash
# 滴答清单访问令牌
export DIDA_ACCESS_TOKEN="your_token_here"

# 请求超时时间
export REQUEST_TIMEOUT="60.0"

# 显示更多调试信息
export DEBUG="true"
```

### 研究者列表管理

#### 数据源配置
研究者列表存储在 Google Sheets 中：
- **格式**: TSV (制表符分隔)
- **结构**: 每行一个研究者姓名，无标题行
- **编码**: UTF-8
- **链接**: [配置链接](https://docs.google.com/spreadsheets/d/1itjnV2U-Eh0F1T0LIGuLjzIhgL9f_OD8tbkMUG-Onic)

#### 添加研究者
1. 打开 Google Sheets 链接
2. 在新行中输入研究者姓名
3. 确保姓名拼写与 arXiv 上一致
4. 保存后系统自动生效

#### 姓名格式要求
- 使用标准英文拼写
- 格式：`First Last` 或 `First Middle Last`
- 避免特殊字符和缩写
- 注意大小写准确性

## 📊 输出和报告

### 报告文件结构

所有报告保存在 `reports/` 目录下：

```
reports/
├── daily_papers_20250115_090000.json      # 每日监控结果
├── weekly_papers_20250115_090000.json     # 周报汇总结果
├── topic_papers_20250115_090000.json      # 主题搜索结果
└── researcher_stats_20250115.json         # 研究者统计数据
```

### JSON 格式说明

#### 每日监控报告
```json
{
    "report_type": "daily",
    "search_date": "2025-01-15",
    "execution_time": "2025-01-15T09:00:00",
    "researchers": [
        {
            "name": "Zhang Wei",
            "papers_found": 1,
            "papers": [
                {
                    "title": "Deep Learning Approaches...",
                    "arxiv_id": "2501.12345",
                    "authors": ["Zhang Wei", "Li Ming"],
                    "abstract": "This paper presents...",
                    "url": "https://arxiv.org/abs/2501.12345",
                    "submitted_date": "2025-01-15"
                }
            ]
        }
    ],
    "summary": {
        "total_papers": 2,
        "active_researchers": 2,
        "total_researchers": 10
    }
}
```

#### 主题搜索报告
```json
{
    "report_type": "topic",
    "search_topics": ["cs.AI", "cs.CR"],
    "search_strategy_used": "exact_date_range",
    "date_range": {
        "from": "2025-01-13",
        "to": "2025-01-15"
    },
    "papers": [
        {
            "title": "AI-Powered Cybersecurity...",
            "arxiv_id": "2501.12347",
            "authors": ["John Doe", "Jane Smith"],
            "categories": ["cs.AI", "cs.CR"],
            "abstract": "This research explores...",
            "url": "https://arxiv.org/abs/2501.12347"
        }
    ],
    "search_attempts": [
        {
            "strategy": "exact_date_range",
            "date_from": "2025-01-13", 
            "date_to": "2025-01-15",
            "result_count": 5,
            "success": true
        }
    ],
    "summary": {
        "total_papers": 5,
        "strategies_tried": 1,
        "final_strategy": "exact_date_range"
    }
}
```

## 🔍 搜索技巧

### 姓名搜索优化
1. **精确匹配**: 使用完整姓名获得最准确结果
2. **通用拼写**: 使用最常见的英文拼写形式
3. **避免缩写**: 尽量使用完整姓名而非缩写
4. **验证结果**: 检查返回的论文作者是否匹配

### 日期范围策略
1. **精确日期**: 搜索特定日期的论文
2. **灵活范围**: 使用日期范围增加结果
3. **回退策略**: 自动扩展搜索范围
4. **时区考虑**: 注意 arXiv 使用UTC时间

### 性能优化
1. **批量处理**: 避免过于频繁的API调用
2. **缓存结果**: 重复搜索时使用缓存
3. **并发控制**: 控制并发请求数量
4. **错误重试**: 网络错误时自动重试

## 🚨 常见问题

### 搜索无结果
**问题**: 搜索特定研究者但没有找到论文
**解决方案**:
1. 检查姓名拼写是否正确
2. 确认该研究者在指定日期是否有论文发布
3. 尝试扩大搜索日期范围
4. 验证研究者列表配置

### 网络连接问题
**问题**: 无法访问 arXiv 或 Google Sheets
**解决方案**:
1. 检查网络连接状态
2. 确认代理设置正确
3. 增加请求超时时间
4. 检查防火墙设置

### 数据格式错误
**问题**: JSON 报告格式异常或乱码
**解决方案**:
1. 确认文件编码为 UTF-8
2. 检查特殊字符处理
3. 验证 JSON 格式有效性
4. 检查磁盘空间是否充足

### 权限问题
**问题**: 无法创建报告文件或访问配置
**解决方案**:
1. 检查 `reports/` 目录权限
2. 确认运行用户有写入权限
3. 验证 Google Sheets 链接可访问
4. 检查环境变量设置

## 💡 最佳实践

### 定期监控
1. 设置每日定时运行
2. 配置异常情况通知
3. 定期检查研究者列表
4. 备份重要监控结果

### 数据管理
1. 定期清理旧报告文件
2. 建立报告归档策略
3. 监控磁盘空间使用
4. 备份配置文件

### 系统维护
1. 定期更新依赖包
2. 监控 API 限制情况
3. 检查错误日志
4. 测试备份恢复流程 
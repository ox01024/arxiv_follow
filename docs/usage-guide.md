# 📖 详细使用指南

## 🎯 系统概述

ArXiv Follow 是一个现代化的论文监控系统，基于CLI和Python API提供强大的搜索和监控功能：
- **智能搜索** - 支持关键词、作者、主题等多种搜索模式
- **异步架构** - 高性能并发处理，支持大规模数据采集
- **类型安全** - 基于Pydantic的数据模型和配置管理
- **AI增强** - 集成LLM进行智能论文分析和推荐
- **现代化CLI** - 基于Typer和Rich的美观命令行界面
- **可扩展集成** - 支持滴答清单、翻译服务等第三方集成

## 📋 核心功能详解

### 论文搜索 (`arxiv-follow search`)

#### 🎯 功能说明
- 支持多种搜索类型：关键词、研究者、主题、分类、混合搜索
- 灵活的过滤条件：时间范围、分类、作者等
- 智能结果排序和去重
- 支持结果导出为JSON格式

#### 🚀 使用方法
```bash
# 基础关键词搜索
arxiv-follow search "attention mechanism"

# 指定搜索类型和结果数量
arxiv-follow search "neural networks" --type keyword --max 50

# 限制搜索时间范围
arxiv-follow search "transformer" --days 7

# 按特定分类搜索
arxiv-follow search "deep learning" --categories "cs.AI,cs.LG"

# 混合搜索（结合多种条件）
arxiv-follow search "federated learning" \
  --type hybrid \
  --categories "cs.AI,cs.CR" \
  --authors "Li" \
  --days 30 \
  --output search_results.json
```

#### 📊 输出格式
```
🔍 正在搜索论文...

✅ 搜索完成
找到 15 篇论文（共 234 篇匹配）
搜索时间: 1250.5ms

                               搜索结果: attention mechanism                                
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID            标题                                                 作者                             分类       日期        ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2501.12345    Attention Mechanisms in Deep Learning                Li Wei, Zhang Ming 等3人            cs.AI      2025-01-15  │
│ 2501.12346    Self-Attention Networks for Computer Vision          Wang Hao, Liu Yang                   cs.CV      2025-01-14  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

显示前20篇，共找到15篇论文
```

### 研究者搜索 (`arxiv-follow authors`)

#### 🎯 功能说明
- 按作者姓名搜索其发表的论文
- 支持多个作者的组合搜索
- 智能作者姓名匹配

#### 🚀 使用方法
```bash
# 搜索单个作者
arxiv-follow authors "Geoffrey Hinton"

# 搜索多个作者（OR逻辑）
arxiv-follow authors "Yann LeCun,Geoffrey Hinton,Yoshua Bengio" --max 50

# 导出搜索结果
arxiv-follow authors "Zhang Wei" --output zhang_papers.json
```

### 主题搜索 (`arxiv-follow topics`)

#### 🎯 功能说明
- 按ArXiv分类主题搜索论文
- 支持跨领域搜索（AND逻辑）
- 时间范围过滤

#### 🚀 使用方法
```bash
# 搜索AI领域论文
arxiv-follow topics "cs.AI" --days 7

# 跨领域搜索（AI+安全）
arxiv-follow topics "cs.AI,cs.CR" --days 14 --max 100

# 计算机视觉最新论文
arxiv-follow topics "cs.CV" --days 3 --output cv_papers.json
```

### 最近论文 (`arxiv-follow recent`)

#### 🎯 功能说明
- 获取最近发布的论文
- 按默认主题或自定义主题过滤
- 快速了解最新研究动态

#### 🚀 使用方法
```bash
# 获取最近3天的论文（使用默认主题）
arxiv-follow recent

# 指定主题和时间范围
arxiv-follow recent --days 7 --topics "cs.AI,cs.LG"

# 大量数据获取
arxiv-follow recent --days 14 --max 200 --output recent_papers.json
```

## 🔧 配置管理

### 配置系统概述

系统使用现代化的Pydantic Settings配置管理，支持：
- **环境变量** - 使用 `ARXIV_FOLLOW_` 前缀
- **.env文件** - 本地开发环境配置
- **嵌套配置** - 分层配置结构
- **类型验证** - 自动类型检查和验证

### 查看当前配置

```bash
# 查看基本配置
arxiv-follow config

# 查看包含敏感信息的完整配置
arxiv-follow config --show-sensitive

# 测试配置有效性
arxiv-follow test
```

### 环境变量配置

#### API配置
```bash
# OpenRouter API（用于AI功能）
export ARXIV_FOLLOW_API__OPENROUTER_API_KEY="your_openrouter_key"

# 滴答清单API
export ARXIV_FOLLOW_API__DIDA_ACCESS_TOKEN="your_dida_token"

# HTTP设置
export ARXIV_FOLLOW_API__HTTP_TIMEOUT=30
export ARXIV_FOLLOW_API__HTTP_RETRIES=3
```

#### 功能开关
```bash
# AI分析功能
export ARXIV_FOLLOW_INTEGRATIONS__AI_ANALYSIS_ENABLED=true

# 滴答清单集成
export ARXIV_FOLLOW_INTEGRATIONS__DIDA_ENABLED=true

# 翻译服务
export ARXIV_FOLLOW_INTEGRATIONS__TRANSLATION_ENABLED=true
```

#### 监控配置
```bash
# 默认搜索主题
export ARXIV_FOLLOW_MONITORING__DEFAULT_SEARCH_TOPICS=["cs.AI","cs.CR"]

# 检查间隔
export ARXIV_FOLLOW_MONITORING__CHECK_INTERVAL_HOURS=6

# 每次检查最大论文数
export ARXIV_FOLLOW_MONITORING__MAX_PAPERS_PER_CHECK=100
```

#### 存储配置
```bash
# 数据目录
export ARXIV_FOLLOW_STORAGE__DATA_DIR="./data"
export ARXIV_FOLLOW_STORAGE__OUTPUT_DIR="./reports"

# 缓存设置
export ARXIV_FOLLOW_STORAGE__ENABLE_CACHE=true
export ARXIV_FOLLOW_STORAGE__CACHE_TTL_SECONDS=3600
```

### .env文件配置

创建 `.env` 文件进行本地配置：

```ini
# .env
# 基础设置
ARXIV_FOLLOW_DEBUG=false
ARXIV_FOLLOW_LOG_LEVEL=INFO

# API密钥
ARXIV_FOLLOW_API__OPENROUTER_API_KEY=your_openrouter_key
ARXIV_FOLLOW_API__DIDA_ACCESS_TOKEN=your_dida_token

# 功能开关
ARXIV_FOLLOW_INTEGRATIONS__AI_ANALYSIS_ENABLED=true
ARXIV_FOLLOW_INTEGRATIONS__DIDA_ENABLED=false
ARXIV_FOLLOW_INTEGRATIONS__TRANSLATION_ENABLED=true

# 存储配置
ARXIV_FOLLOW_STORAGE__DATA_DIR=./data
ARXIV_FOLLOW_STORAGE__OUTPUT_DIR=./reports
ARXIV_FOLLOW_STORAGE__ENABLE_CACHE=true

# 监控设置
ARXIV_FOLLOW_MONITORING__DEFAULT_SEARCH_TOPICS=["cs.AI","cs.CR","cs.LG"]
ARXIV_FOLLOW_MONITORING__CHECK_INTERVAL_HOURS=6
```

## 📊 输出和报告

### 报告文件结构

所有输出文件保存在配置的输出目录下（默认为 `reports/`）：

```
reports/
├── search_results_20250115_143020.json    # 搜索结果
├── recent_papers_20250115_120000.json     # 最近论文
├── author_search_20250115_150030.json     # 作者搜索结果
└── topic_analysis_20250115_160000.json    # 主题分析结果
```

### JSON 输出格式

#### 标准搜索结果格式
```json
{
    "query": {
        "query_id": "search_20250115_143020_a1b2c3d4",
        "search_type": "keyword",
        "query_text": "attention mechanism",
        "topics": ["cs.AI"],
        "filters": {
            "max_results": 20,
            "days_back": 7
        }
    },
    "papers": [
        {
            "arxiv_id": "2501.12345",
            "title": "Attention Mechanisms in Deep Learning",
            "authors": ["Li Wei", "Zhang Ming", "Wang Hao"],
            "abstract": "This paper presents a comprehensive...",
            "url": "https://arxiv.org/abs/2501.12345",
            "pdf_url": "https://arxiv.org/pdf/2501.12345.pdf",
            "submitted_date": "2025-01-15",
            "primary_category": "cs.AI",
            "categories": ["cs.AI", "cs.LG"],
            "comments": "18 pages, 5 figures",
            "journal_ref": null
        }
    ],
    "metrics": {
        "total_found": 234,
        "total_returned": 15,
        "search_time_ms": 1250.5,
        "success": true
    },
         "timestamp": "2025-01-15T14:30:20.123456",
     "success": true
 }
 ```

## 🎯 搜索技巧和最佳实践

### 搜索类型选择指南

- **keyword** - 适合概念性搜索（如 "attention mechanism"）
- **researcher** - 适合跟踪特定作者的工作
- **topic** - 适合按学科分类浏览（如 "cs.AI"）
- **hybrid** - 结合多种条件的复杂搜索

### 提高搜索效果的技巧

```bash
# 使用引号进行精确匹配
arxiv-follow search '"neural machine translation"'

# 组合多个关键词
arxiv-follow search "transformer attention" --type keyword

# 限制时间范围提高相关性
arxiv-follow search "federated learning" --days 30

# 使用分类过滤减少噪音
arxiv-follow search "privacy" --categories "cs.CR,cs.AI"
```

### 常用ArXiv分类

- **cs.AI** - 人工智能
- **cs.LG** - 机器学习  
- **cs.CV** - 计算机视觉
- **cs.CL** - 计算语言学
- **cs.CR** - 密码学与安全
- **cs.RO** - 机器人学
- **cs.DB** - 数据库
- **cs.DC** - 分布式计算

## ❓ 常见问题解答

### Q: 如何提高搜索速度？
A: 
- 减少搜索时间范围（使用 `--days` 参数）
- 限制结果数量（使用 `--max` 参数）
- 启用缓存功能（配置中设置）

### Q: 搜索结果为空怎么办？
A:
- 检查关键词拼写
- 扩大时间范围
- 尝试不同的搜索类型
- 使用更宽泛的关键词

### Q: 如何批量处理搜索结果？
A:
```bash
# 导出为JSON文件
arxiv-follow search "deep learning" --output results.json

# 使用Python API处理
python -c "
import json
import arxiv_follow

result = arxiv_follow.search('transformer', max_results=100)
with open('papers.json', 'w') as f:
    json.dump(result, f, indent=2)
"
```

### Q: 配置文件在哪里？
A: 系统使用环境变量和 `.env` 文件进行配置，不依赖固定的配置文件位置。可以通过 `arxiv-follow config` 查看当前配置。

## 🔗 相关文档

- [主题搜索专题](topic-search.md) - 深入了解主题搜索功能
- [智能监控指南](intelligent-monitoring-guide.md) - AI功能配置和使用
- [滴答清单集成](dida-integration.md) - 任务管理集成
- [翻译指南](translation-guide.md) - 双语翻译功能 
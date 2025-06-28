# ArXiv Follow - 现代化论文监控系统

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)

> 🔬 **全新重构** - 采用现代化Python架构，提供强大的ArXiv论文监控和分析功能

## ✨ 主要特性

- 🔍 **智能搜索引擎** - 支持关键词、作者、主题、跨领域等多种搜索模式
- 📊 **类型安全** - 基于Pydantic的数据模型，确保数据验证和类型安全
- ⚡ **异步架构** - 高性能并发处理，支持大规模数据采集
- 🎨 **现代化CLI** - 基于Typer和Rich的美观命令行界面
- 🧠 **AI增强分析** - 集成LLM进行智能论文分析和推荐
- 🔌 **可扩展设计** - 模块化架构，支持自定义扩展
- 📱 **多平台集成** - 支持滴答清单、翻译服务等第三方集成

## 🚀 快速开始

### 安装

```bash
# 使用 uv（推荐）
uv add arxiv-follow

# 或使用 pip
pip install arxiv-follow
```

### 基本使用

```bash
# 搜索最近3天的AI论文
arxiv-follow recent --days 3 --topics "cs.AI"

# 按关键词搜索
arxiv-follow search "machine learning"

# 按作者搜索
arxiv-follow authors "Yann LeCun,Geoffrey Hinton"

# 跨领域搜索
arxiv-follow topics "cs.AI,cs.CR" --days 7

# 显示系统配置
arxiv-follow config

# 测试系统连接
arxiv-follow test
```

### Python API

```python
import arxiv_follow

# 快速搜索
result = arxiv_follow.search("transformer", max_results=10)
print(f"找到 {result['count']} 篇论文")

# 获取最近论文
papers = arxiv_follow.recent(days=3, topics=["cs.AI", "cs.LG"])
for paper in papers['papers'][:5]:
    print(f"- {paper['title']}")

# 使用完整API
from arxiv_follow import SearchEngine, SearchQuery, SearchType
import asyncio

async def advanced_search():
    config = arxiv_follow.load_config()
    
    query = SearchQuery(
        query_id="my_search",
        search_type=SearchType.HYBRID,
        query_text="attention mechanism",
        topics=["cs.AI"],
        filters={"max_results": 20, "days_back": 7}
    )
    
    async with SearchEngine(config) as engine:
        result = await engine.search(query)
        return result.papers

papers = asyncio.run(advanced_search())
```

## 📖 详细文档

### 核心概念

#### 1. 搜索引擎 (SearchEngine)
统一的搜索接口，支持多种搜索策略：
- **关键词搜索** - 在标题、摘要中搜索特定词汇
- **作者搜索** - 按研究者姓名搜索论文
- **主题搜索** - 按ArXiv分类搜索
- **混合搜索** - 结合多种策略的智能搜索

#### 2. 数据模型
基于Pydantic的类型安全模型：
```python
from arxiv_follow.models import Paper, SearchQuery, SearchFilters

# 创建搜索查询
query = SearchQuery(
    query_id="search_001",
    search_type="keyword",
    query_text="neural networks",
    filters=SearchFilters(
        max_results=50,
        days_back=7,
        categories=["cs.AI", "cs.LG"]
    )
)
```

#### 3. 异步收集器 (ArxivCollector)
高性能的论文数据收集：
```python
from arxiv_follow import ArxivCollector
import asyncio

async def collect_papers():
    config = arxiv_follow.load_config()
    
    async with ArxivCollector(config) as collector:
        # 搜索最近论文
        result = await collector.search_recent_papers(
            days_back=3,
            categories=["cs.AI"],
            max_results=20
        )

        # 批量获取详情
        papers = await collector.collect_papers_batch(
            ["2501.01234", "2501.01235"],
            include_content=True
        )
        
        return papers

papers = asyncio.run(collect_papers())
```

### 配置系统

#### 环境变量配置
```bash
# API配置
export ARXIV_FOLLOW_API__OPENROUTER_API_KEY="your_key"
export ARXIV_FOLLOW_API__DIDA_ACCESS_TOKEN="your_token"

# 功能开关
export ARXIV_FOLLOW_INTEGRATIONS__AI_ANALYSIS_ENABLED=true
export ARXIV_FOLLOW_INTEGRATIONS__DIDA_ENABLED=true

# 监控配置
export ARXIV_FOLLOW_MONITORING__DEFAULT_SEARCH_TOPICS="cs.AI,cs.CR"
export ARXIV_FOLLOW_MONITORING__CHECK_INTERVAL_HOURS=6
```

#### .env 文件
```ini
# .env
ARXIV_FOLLOW_DEBUG=false
ARXIV_FOLLOW_API__OPENROUTER_API_KEY=your_openrouter_key
ARXIV_FOLLOW_API__DIDA_ACCESS_TOKEN=your_dida_token
ARXIV_FOLLOW_INTEGRATIONS__AI_ANALYSIS_ENABLED=true
ARXIV_FOLLOW_INTEGRATIONS__TRANSLATION_ENABLED=true
ARXIV_FOLLOW_STORAGE__DATA_DIR=./data
ARXIV_FOLLOW_STORAGE__OUTPUT_DIR=./reports
```

### CLI 命令详解

#### 搜索命令
```bash
# 基础搜索
arxiv-follow search "attention mechanism" --max 20

# 指定搜索类型
arxiv-follow search "neural networks" --type keyword --days 7

# 复杂过滤
arxiv-follow search "transformer" \
  --categories "cs.AI,cs.CL" \
  --authors "Vaswani" \
  --output results.json

# 按作者搜索
arxiv-follow authors "Geoffrey Hinton,Yann LeCun" --max 30

# 跨领域主题搜索
arxiv-follow topics "cs.AI,cs.CR" --days 14 --max 50
```

#### 监控命令
```bash
# 获取最近论文
arxiv-follow recent --days 3 --topics "cs.AI,cs.LG"

# 自定义主题监控
arxiv-follow recent --days 7 \
  --topics "cs.AI,cs.CR,cs.CV" \
  --output weekly_report.json
```

#### 系统管理
```bash
# 查看配置
arxiv-follow config

# 查看敏感配置
arxiv-follow config --show-sensitive

# 测试系统连接
arxiv-follow test
```

## 🏗️ 架构设计

### 项目结构
```
src/arxiv_follow/
├── models/           # 数据模型层
│   ├── paper.py     # 论文相关模型
│   ├── researcher.py # 研究者模型
│   ├── search.py    # 搜索模型
│   ├── task.py      # 任务模型
│   └── config.py    # 配置模型
├── core/            # 核心业务层
│   ├── collector.py # 数据收集器
│   ├── analyzer.py  # 分析器
│   ├── monitor.py   # 监控器
│   └── engine.py    # 搜索引擎
├── services/        # 服务层
│   ├── translation.py # 翻译服务
│   └── researcher.py  # 研究者服务
├── integrations/    # 集成层
│   └── dida.py     # 滴答清单集成
├── cli/             # 命令行接口
│   └── main.py     # 主CLI应用
└── config/          # 配置管理
    └── settings.py  # 设置管理
```

### 技术栈

- **数据验证**: Pydantic v2
- **异步编程**: AsyncIO + httpx
- **CLI框架**: Typer + Rich
- **配置管理**: Pydantic Settings
- **HTTP客户端**: httpx
- **包管理**: uv

## 🔧 开发指南

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/your-org/arxiv_follow.git
cd arxiv_follow

# 安装 uv (如果未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
uv sync --dev

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 运行测试
uv run pytest

# 运行类型检查
uv run mypy src/

# 运行代码格式化
uv run black src/
uv run isort src/
```

### 扩展开发

#### 自定义搜索策略
```python
from arxiv_follow.core.engine import SearchEngine
from arxiv_follow.models import SearchQuery, SearchResult

class CustomSearchEngine(SearchEngine):
    
    async def search_custom(self, query: SearchQuery) -> SearchResult:
        """自定义搜索逻辑"""
        # 实现你的搜索策略
        pass
```

#### 添加新的集成
```python
from arxiv_follow.models.config import AppConfig

class CustomIntegration:
    
    def __init__(self, config: AppConfig):
        self.config = config
    
    async def process_papers(self, papers: list) -> dict:
        """处理论文数据"""
        # 实现你的集成逻辑
        pass
```

## 📈 性能优化

### 并发控制
```python
# 配置文件中设置并发参数
ARXIV_FOLLOW_MAX_CONCURRENT_REQUESTS=10
ARXIV_FOLLOW_REQUEST_DELAY_SECONDS=1.0
```

### 缓存策略
```python
# 启用缓存
ARXIV_FOLLOW_STORAGE__ENABLE_CACHE=true
ARXIV_FOLLOW_STORAGE__CACHE_TTL_SECONDS=3600
ARXIV_FOLLOW_STORAGE__MAX_CACHE_SIZE_MB=500
```

### 大数据处理
```python
from arxiv_follow import ArxivCollector

async def stream_large_dataset():
    config = arxiv_follow.load_config()
    
    async with ArxivCollector(config) as collector:
        async for batch in collector.stream_search_results(
            query="cat:cs.AI",
            batch_size=100,
            max_total=10000
        ):
            # 处理批次数据
            process_batch(batch)
```

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_collector.py

# 运行覆盖率测试
uv run pytest --cov=src/arxiv_follow

# 运行性能测试
uv run pytest tests/test_performance.py -v
```

### 集成测试
```bash
# 测试真实API连接
uv run python -m arxiv_follow.cli.main test

# 烟雾测试
uv run pytest tests/ -k smoke
```

## 🚀 部署

### 生产环境配置
```bash
# 设置生产环境变量
export ARXIV_FOLLOW_DEBUG=false
export ARXIV_FOLLOW_LOG_LEVEL=INFO
export ARXIV_FOLLOW_STORAGE__BACKEND=postgresql
export ARXIV_FOLLOW_STORAGE__DATABASE_URL="postgresql://..."

# 启动应用
arxiv-follow config  # 验证配置
arxiv-follow test    # 测试连接
```

### Docker 部署
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync --no-dev

ENTRYPOINT ["uv", "run", "arxiv-follow"]
```

## 📋 路线图

### v1.1 计划功能
- [ ] 实时监控仪表板
- [ ] 论文推荐算法优化
- [ ] 更多第三方集成
- [ ] 分布式部署支持

### v1.2 计划功能
- [ ] 图形用户界面 (GUI)
- [ ] 论文引用网络分析
- [ ] 团队协作功能
- [ ] 高级AI分析模型

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 贡献类型
- 🐛 Bug 报告
- ✨ 新功能建议
- 📖 文档改进
- 🧪 测试用例
- 🔧 代码优化

### 开发流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

- 📧 邮箱: support@arxiv-follow.dev
- 💬 讨论: [GitHub Discussions](https://github.com/your-org/arxiv_follow/discussions)
- 🐛 问题: [GitHub Issues](https://github.com/your-org/arxiv_follow/issues)
- 📖 文档: [完整文档](https://arxiv-follow.dev/docs)

## 🙏 致谢

感谢以下项目和社区的支持：
- [ArXiv.org](https://arxiv.org/) - 提供优秀的学术论文平台
- [Pydantic](https://pydantic.dev/) - 强大的数据验证库
- [Typer](https://typer.tiangolo.com/) - 现代化CLI框架
- [Rich](https://rich.readthedocs.io/) - 美观的终端输出

---

<div align="center">

**ArXiv Follow** - 让学术研究更高效 🚀

[官网](https://arxiv-follow.dev) • [文档](https://docs.arxiv-follow.dev) • [社区](https://community.arxiv-follow.dev)

</div>
# ArXiv Follow - 智能论文监控系统

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)

> 🔬 **让学术研究更高效** - 自动追踪感兴趣的论文，永远不错过重要研究进展

## ✨ 核心功能

- 🔍 **多样化搜索** - 按关键词、作者、研究领域快速找到相关论文
- 📅 **自动监控** - 定期检查新发布的论文，第一时间获得通知
- 🧠 **AI智能分析** - 自动分析论文重要性，生成中文摘要和研究亮点
- 📱 **任务管理集成** - 直接推送到滴答清单，方便后续跟进和阅读安排
- 🌐 **双语支持** - 中英文对照，帮助理解和分享学术内容
- ⚡ **高效处理** - 快速处理大量论文数据，节省您的时间
- 🎨 **友好界面** - 清晰美观的命令行界面，使用简单直观

## 🎯 项目背景与挑战

> **💡 特殊挑战：零代码开发实验**

这个项目代表了一个独特的开发实验：**通过 Vibe Coding（AI 辅助编程）完全不写一行代码来构建完整的软件项目**。

### 🧠 挑战目标
- **改变开发习惯** - 摆脱"喜欢自己写代码"的传统思维模式
- **AI协作探索** - 探索人工智能在软件开发中的深度参与可能性
- **工程质量验证** - 验证AI生成代码在复杂项目中的可维护性和扩展性
- **开发效率革命** - 测试AI辅助开发是否能大幅提升开发效率

### 📈 实验成果
通过这个挑战，我们证明了：
- ✅ **AI可以构建复杂系统** - 包含CLI工具、异步架构、数据模型等完整功能
- ✅ **代码质量可控** - 生成的代码具有良好的结构和可维护性  
- ✅ **开发速度提升** - 显著减少传统编码时间，专注于需求和架构设计
- ✅ **学习效应明显** - 通过AI协作学习到新的编程模式和最佳实践

### 🔄 Vibe Coding 工作流
1. **需求对话** - 通过自然语言描述功能需求
2. **架构设计** - AI协助进行系统架构和模块设计
3. **代码生成** - AI生成完整的代码实现
4. **迭代优化** - 通过对话持续改进和扩展功能
5. **质量保证** - AI协助进行测试和文档编写

这个项目的每一行代码、每一个配置文件、每一份文档都是通过AI协作完成的，展示了AI辅助开发的巨大潜力。

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/your-repo/arxiv_follow.git
cd arxiv_follow

# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 基本使用

```bash
# 搜索最近3天的AI论文
arxiv-follow recent --days 3 --topics "cs.AI"

# 按关键词搜索
arxiv-follow search "machine learning" --max 20

# 按作者搜索
arxiv-follow authors "Yann LeCun,Geoffrey Hinton" --max 30

# 跨领域主题搜索
arxiv-follow topics "cs.AI,cs.CR" --days 7 --max 50

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
from arxiv_follow import SearchEngine, SearchQuery, SearchType, SearchFilters
import asyncio

async def advanced_search():
    config = arxiv_follow.load_config()
    
    query = SearchQuery(
        query_id="my_search",
        search_type=SearchType.HYBRID,
        query_text="attention mechanism",
        topics=["cs.AI"],
        filters=SearchFilters(max_results=20, days_back=7)
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
export ARXIV_FOLLOW_INTEGRATIONS__TRANSLATION_ENABLED=true

# 监控配置
export ARXIV_FOLLOW_MONITORING__DEFAULT_SEARCH_TOPICS=["cs.AI","cs.CR"]
export ARXIV_FOLLOW_MONITORING__CHECK_INTERVAL_HOURS=6

# 存储配置
export ARXIV_FOLLOW_STORAGE__DATA_DIR="./data"
export ARXIV_FOLLOW_STORAGE__OUTPUT_DIR="./reports"
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
# 基础关键词搜索
arxiv-follow search "attention mechanism" --max 20

# 指定搜索类型和时间范围
arxiv-follow search "neural networks" --type keyword --days 7

# 混合搜索（关键词+主题+作者）
arxiv-follow search "transformer" \
  --type hybrid \
  --categories "cs.AI,cs.CL" \
  --authors "Vaswani" \
  --output results.json

# 按作者搜索论文
arxiv-follow authors "Geoffrey Hinton,Yann LeCun" --max 30

# 跨领域主题搜索（支持AND逻辑）
arxiv-follow topics "cs.AI,cs.CR" --days 14 --max 50

# 获取最近论文
arxiv-follow recent --days 3 --topics "cs.AI,cs.LG" --max 25
```

#### 配置和测试命令
```bash
# 显示当前配置
arxiv-follow config

# 显示包含敏感信息的完整配置
arxiv-follow config --show-sensitive

# 测试系统连接
arxiv-follow test

# 自定义主题监控和输出
arxiv-follow recent --days 7 \
  --topics "cs.AI,cs.CR,cs.CV" \
  --output weekly_report.json
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

> **🤖 AI协作项目特别说明**
> 
> 本项目完全通过AI辅助开发构建，我们鼓励并欢迎使用AI工具进行贡献！无论是代码实现、文档编写还是测试用例，都可以通过AI协作完成。

我们欢迎所有形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

### 贡献类型
- 🐛 Bug 报告
- ✨ 新功能建议  
- 📖 文档改进
- 🧪 测试用例
- 🔧 代码优化
- 🤖 AI协作经验分享

### 推荐的AI辅助开发流程
1. **需求分析** - 使用AI协助分析和细化需求
2. **架构设计** - 通过AI对话设计技术方案
3. **代码实现** - AI生成代码实现
4. **质量保证** - AI协助代码review和测试
5. **文档编写** - AI辅助生成技术文档

### 传统开发流程
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

### 🤖 AI协作伙伴
特别感谢AI工具在项目开发中的核心贡献：
- **Claude (Anthropic)** - 项目的主要AI协作伙伴，负责架构设计、代码实现和文档编写
- **Cursor AI** - 代码编辑器中的智能助手，提供实时编程支持

> 📁 **完整协作记录**: 查看 [`vibe_coding/`](./vibe_coding/) 目录了解详细的AI协作开发历程

### 🛠️ 技术支持
感谢以下项目和社区的支持：
- [ArXiv.org](https://arxiv.org/) - 提供优秀的学术论文平台
- [Pydantic](https://pydantic.dev/) - 强大的数据验证库
- [Typer](https://typer.tiangolo.com/) - 现代化CLI框架  
- [Rich](https://rich.readthedocs.io/) - 美观的终端输出
- [OpenRouter](https://openrouter.ai/) - AI模型API服务
- [滴答清单](https://dida365.com/) - 任务管理平台集成

---

<div align="center">

**ArXiv Follow** - 让学术研究更高效 🚀

*🤖 由AI协作构建 • 零手写代码 • Vibe Coding实验项目*

[官网](https://arxiv-follow.dev) • [文档](https://docs.arxiv-follow.dev) • [AI协作记录](./vibe_coding/)

</div>
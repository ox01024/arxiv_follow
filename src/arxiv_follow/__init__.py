"""
ArXiv Follow - 现代化论文监控系统

这是一个全新重构的ArXiv论文监控系统，采用现代化Python架构：

- 🔍 强大的搜索引擎：支持多种搜索策略
- 📊 类型安全的数据模型：使用Pydantic进行数据验证
- ⚡ 异步编程：高性能的并发处理
- 🎨 现代化CLI：基于Typer和Rich的美观界面
- 🧠 AI增强分析：集成LLM进行智能分析
- 🔌 可扩展架构：模块化设计，易于扩展

主要功能：
- 按研究者、主题、关键词搜索论文
- 跨领域论文发现
- AI驱动的论文分析和推荐
- 自动化监控和通知
- 多种集成选项（滴答清单、翻译服务等）
"""

__version__ = "1.0.0"
__author__ = "ArXiv Follow Team"
__description__ = "现代化ArXiv论文监控系统 - 支持AI增强分析、研究者跟踪和智能推荐"

# 核心组件
# CLI应用
from .cli import app
from .core import ArxivCollector, PaperAnalyzer, PaperMonitor, SearchEngine
from .models import (
    AppConfig,
    Paper,
    PaperAnalysis,
    PaperContent,
    PaperMetadata,
    Researcher,
    ResearcherProfile,
    SearchFilters,
    SearchQuery,
    SearchResult,
    Task,
    TaskStatus,
    TaskType,
    load_config,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",
    # Core components
    "ArxivCollector",
    "PaperAnalyzer",
    "PaperMonitor",
    "SearchEngine",
    # Data models
    "Paper",
    "PaperMetadata",
    "PaperContent",
    "PaperAnalysis",
    "Researcher",
    "ResearcherProfile",
    "SearchQuery",
    "SearchResult",
    "SearchFilters",
    "Task",
    "TaskType",
    "TaskStatus",
    # Configuration
    "AppConfig",
    "load_config",
    # CLI
    "app",
]


def quick_search(query: str, max_results: int = 10) -> dict:
    """
    快速搜索接口

    Args:
        query: 搜索查询
        max_results: 最大结果数

    Returns:
        搜索结果字典
    """
    import asyncio

    from .core.engine import SearchEngine
    from .models import SearchFilters, SearchQuery, SearchType

    async def _search():
        config = load_config()
        search_query = SearchQuery(
            query_id=f"quick_search_{int(asyncio.get_event_loop().time())}",
            search_type=SearchType.KEYWORD,
            query_text=query,
            filters=SearchFilters(max_results=max_results),
        )

        async with SearchEngine(config) as engine:
            result = await engine.search(search_query)

        return {
            "success": result.success,
            "papers": result.papers,
            "count": len(result.papers),
            "query": query,
        }

    return asyncio.run(_search())


def get_recent_papers(days: int = 3, topics: list = None) -> dict:
    """
    获取最近论文接口

    Args:
        days: 回溯天数
        topics: 主题列表

    Returns:
        论文结果字典
    """
    import asyncio

    from .core.engine import SearchEngine

    async def _get_recent():
        config = load_config()
        if topics is None:
            topics_list = config.monitoring.default_search_topics
        else:
            topics_list = topics

        async with SearchEngine(config) as engine:
            result = await engine.search_recent_papers(
                days_back=days, topics=topics_list, max_results=50
            )

        return {
            "success": result.success,
            "papers": result.papers,
            "count": len(result.papers),
            "topics": topics_list,
            "days": days,
        }

    return asyncio.run(_get_recent())


# 便捷函数别名
search = quick_search
recent = get_recent_papers

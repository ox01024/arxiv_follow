"""
ArXiv Follow 数据模型

使用 Pydantic 定义的类型安全数据模型，支持自动验证、序列化和文档生成。
"""

from .config import APIConfig, AppConfig, IntegrationConfig, load_config
from .paper import Paper, PaperAnalysis, PaperContent, PaperMetadata
from .researcher import Researcher, ResearcherProfile, ResearchField
from .search import SearchFilters, SearchQuery, SearchResult, SearchType
from .task import Task, TaskPriority, TaskStatus, TaskType

__all__ = [
    # Paper models
    "Paper",
    "PaperMetadata",
    "PaperContent",
    "PaperAnalysis",
    # Researcher models
    "Researcher",
    "ResearcherProfile",
    "ResearchField",
    # Search models
    "SearchQuery",
    "SearchResult",
    "SearchFilters",
    "SearchType",
    # Task models
    "Task",
    "TaskType",
    "TaskStatus",
    "TaskPriority",
    # Configuration
    "AppConfig",
    "APIConfig",
    "IntegrationConfig",
    "load_config",
]

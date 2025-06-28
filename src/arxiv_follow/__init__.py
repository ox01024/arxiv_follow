"""
ArXiv 研究者动态监控系统

这是一个自动化监控特定研究者在 arXiv 上发布论文的系统，
支持每日研究者动态监控和周报汇总，以及基于交叉学科主题的智能搜索。
"""

__version__ = "0.1.0"
__author__ = "ArXiv Follow Team"
__description__ = "ArXiv论文监控系统 - 支持研究者跟踪、主题订阅和定期报告"

# 主要组件导出
from .core.collector import PaperCollector
from .core.analyzer import PaperAnalyzer
from .core.monitor import IntelligentPaperMonitor
from .services.translation import TranslationService
from .services.researcher import ResearcherService
from .integrations.dida import DidaIntegration

__all__ = [
    "PaperCollector",
    "PaperAnalyzer", 
    "IntelligentPaperMonitor",
    "TranslationService",
    "ResearcherService",
    "DidaIntegration",
] 
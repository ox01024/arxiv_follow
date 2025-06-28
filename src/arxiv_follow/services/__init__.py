"""
服务层模块

包含翻译服务、研究者服务等业务服务。
"""

from .translation import TranslationService
from .researcher import ResearcherService

__all__ = [
    "TranslationService",
    "ResearcherService",
] 
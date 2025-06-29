#!/usr/bin/env python3
"""
现代化论文监控模块

提供智能的论文监控、分析和报告生成功能。
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from ..models import (
    SearchFilters,
    SearchQuery,
    SearchResult,
    SearchType,
    Task,
    TaskStatus,
    TaskType,
)
from ..models.config import AppConfig
from .analyzer import PaperAnalyzer
from .collector import ArxivCollector
from .engine import SearchEngine

logger = logging.getLogger(__name__)


class PaperMonitor:
    """现代化论文监控器"""

    def __init__(self, config: AppConfig):
        """初始化监控器"""
        self.config = config
        self.collector = ArxivCollector(config)
        self.analyzer = (
            PaperAnalyzer(config) if config.is_feature_enabled("ai_analysis") else None
        )
        self.engine = SearchEngine(config)

        logger.info("论文监控器初始化完成")
        logger.info(f"AI分析: {'启用' if self.analyzer else '禁用'}")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.collector.__aenter__()
        await self.engine.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.collector.__aexit__(exc_type, exc_val, exc_tb)
        await self.engine.__aexit__(exc_type, exc_val, exc_tb)

    async def monitor_researchers(
        self, researchers: list[str], days_back: int = 1
    ) -> SearchResult:
        """监控研究者的新论文"""
        query = SearchQuery(
            query_id=f"researchers_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            search_type=SearchType.RESEARCHER,
            query_text=f"监控 {len(researchers)} 位研究者",
            researchers=researchers,
            filters=SearchFilters(days_back=days_back, max_results=100),
        )

        result = await self.engine.search(query)

        if result.success and self.analyzer:
            # 对结果进行AI分析
            analyzed_papers = []
            for paper_data in result.papers:
                try:
                    analysis = await self.analyzer.analyze_paper_significance(
                        paper_data
                    )
                    paper_data["ai_analysis"] = analysis
                    analyzed_papers.append(paper_data)
                except Exception as e:
                    logger.warning(f"分析论文失败: {e}")
                    analyzed_papers.append(paper_data)

            result.papers = analyzed_papers

        return result

    async def monitor_topics(
        self, topics: list[str], days_back: int = 1
    ) -> SearchResult:
        """监控主题的新论文"""
        query = SearchQuery(
            query_id=f"topics_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            search_type=SearchType.TOPIC,
            query_text=f"监控主题: {', '.join(topics)}",
            topics=topics,
            filters=SearchFilters(days_back=days_back, max_results=100),
        )

        result = await self.engine.search(query)

        if result.success and self.analyzer:
            # 按重要性排序
            scored_papers = []
            for paper_data in result.papers:
                try:
                    analysis = await self.analyzer.analyze_paper_significance(
                        paper_data
                    )
                    paper_data["ai_analysis"] = analysis
                    paper_data["importance_score"] = analysis.get(
                        "importance_score", 5.0
                    )
                    scored_papers.append(paper_data)
                except Exception as e:
                    logger.warning(f"分析论文失败: {e}")
                    paper_data["importance_score"] = 5.0
                    scored_papers.append(paper_data)

            # 按重要性评分排序
            scored_papers.sort(
                key=lambda x: x.get("importance_score", 5.0), reverse=True
            )
            result.papers = scored_papers

        return result

    async def daily_monitor(
        self,
        researchers: list[str] | None = None,
        topics: list[str] | None = None,
    ) -> dict[str, Any]:
        """每日监控"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "researcher_results": None,
            "topic_results": None,
            "summary": {},
            "success": True,
        }

        try:
            # 监控研究者
            if researchers:
                logger.info(f"开始监控 {len(researchers)} 位研究者")
                results["researcher_results"] = await self.monitor_researchers(
                    researchers, days_back=1
                )

            # 监控主题
            if topics:
                logger.info(f"开始监控主题: {', '.join(topics)}")
                results["topic_results"] = await self.monitor_topics(
                    topics, days_back=1
                )

            # 生成摘要
            results["summary"] = self._generate_daily_summary(results)

            logger.info("每日监控完成")

        except Exception as e:
            logger.error(f"每日监控失败: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    async def weekly_monitor(
        self,
        researchers: list[str] | None = None,
        topics: list[str] | None = None,
    ) -> dict[str, Any]:
        """每周监控"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "week_start": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "week_end": datetime.now().strftime("%Y-%m-%d"),
            "researcher_results": None,
            "topic_results": None,
            "summary": {},
            "success": True,
        }

        try:
            # 监控研究者（过去7天）
            if researchers:
                logger.info(f"开始每周监控 {len(researchers)} 位研究者")
                results["researcher_results"] = await self.monitor_researchers(
                    researchers, days_back=7
                )

            # 监控主题（过去7天）
            if topics:
                logger.info(f"开始每周监控主题: {', '.join(topics)}")
                results["topic_results"] = await self.monitor_topics(
                    topics, days_back=7
                )

            # 生成摘要
            results["summary"] = self._generate_weekly_summary(results)

            logger.info("每周监控完成")

        except Exception as e:
            logger.error(f"每周监控失败: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def _generate_daily_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """生成每日摘要"""
        summary = {
            "total_papers": 0,
            "researcher_papers": 0,
            "topic_papers": 0,
            "top_papers": [],
            "ai_insights": None,
        }

        # 统计研究者论文
        if results["researcher_results"] and results["researcher_results"].success:
            summary["researcher_papers"] = len(results["researcher_results"].papers)
            summary["total_papers"] += summary["researcher_papers"]

        # 统计主题论文
        if results["topic_results"] and results["topic_results"].success:
            summary["topic_papers"] = len(results["topic_results"].papers)
            summary["total_papers"] += summary["topic_papers"]

        # 收集所有论文并按重要性排序
        all_papers = []

        if results["researcher_results"] and results["researcher_results"].success:
            all_papers.extend(results["researcher_results"].papers)

        if results["topic_results"] and results["topic_results"].success:
            all_papers.extend(results["topic_results"].papers)

        # 去重并按重要性排序
        unique_papers = {
            p.get("arxiv_id"): p for p in all_papers if p.get("arxiv_id")
        }.values()
        sorted_papers = sorted(
            unique_papers, key=lambda x: x.get("importance_score", 5.0), reverse=True
        )

        # 选取前5篇论文
        summary["top_papers"] = list(sorted_papers)[:5]

        # 生成AI洞察（如果启用）
        if self.analyzer and summary["top_papers"]:
            try:
                summary["ai_insights"] = self._generate_ai_insights(
                    summary["top_papers"]
                )
            except Exception as e:
                logger.warning(f"生成AI洞察失败: {e}")

        return summary

    def _generate_weekly_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """生成每周摘要"""
        summary = self._generate_daily_summary(results)  # 复用每日摘要逻辑

        # 添加周报特有的统计
        summary["weekly_trends"] = self._analyze_weekly_trends(results)

        return summary

    def _analyze_weekly_trends(self, results: dict[str, Any]) -> dict[str, Any]:
        """分析每周趋势"""
        trends = {
            "hot_topics": [],
            "productive_researchers": [],
            "research_directions": [],
        }

        # 分析热门主题
        all_papers = []
        if results["topic_results"] and results["topic_results"].success:
            all_papers.extend(results["topic_results"].papers)

        if all_papers:
            # 统计分类频次
            category_counts = {}
            for paper in all_papers:
                categories = paper.get("categories", [])
                for cat in categories:
                    category_counts[cat] = category_counts.get(cat, 0) + 1

            # 获取前5个热门分类
            hot_categories = sorted(
                category_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
            trends["hot_topics"] = [
                {"category": cat, "count": count} for cat, count in hot_categories
            ]

        # 分析高产研究者
        if results["researcher_results"] and results["researcher_results"].success:
            author_counts = {}
            for paper in results["researcher_results"].papers:
                authors = paper.get("authors", [])
                for author in authors:
                    author_counts[author] = author_counts.get(author, 0) + 1

            productive_authors = sorted(
                author_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
            trends["productive_researchers"] = [
                {"name": name, "papers": count} for name, count in productive_authors
            ]

        return trends

    def _generate_ai_insights(self, papers: list[dict[str, Any]]) -> dict[str, Any]:
        """生成AI洞察"""
        insights = {
            "summary": "",
            "key_trends": [],
            "recommendations": [],
            "innovation_level": 0.0,
        }

        if not papers:
            return insights

        # 分析创新水平
        scores = [
            p.get("importance_score", 5.0) for p in papers if p.get("importance_score")
        ]
        if scores:
            insights["innovation_level"] = sum(scores) / len(scores)

        # 提取关键趋势
        all_categories = []
        for paper in papers:
            all_categories.extend(paper.get("categories", []))

        category_freq = {}
        for cat in all_categories:
            category_freq[cat] = category_freq.get(cat, 0) + 1

        insights["key_trends"] = [
            cat
            for cat, _ in sorted(
                category_freq.items(), key=lambda x: x[1], reverse=True
            )[:3]
        ]

        # 生成摘要
        insights["summary"] = (
            f"发现 {len(papers)} 篇高质量论文，平均重要性评分 {insights['innovation_level']:.1f}/10"
        )

        # 生成建议
        if insights["innovation_level"] > 7.0:
            insights["recommendations"].append("发现多篇高影响力论文，建议深入研读")
        if len(insights["key_trends"]) > 1:
            insights["recommendations"].append("注意跨领域研究趋势")

        return insights

    async def create_monitoring_task(
        self, task_type: TaskType, parameters: dict[str, Any]
    ) -> Task:
        """创建监控任务"""
        from ..models import Task, TaskPriority

        task = Task(
            task_id=f"{task_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            task_type=task_type,
            title=f"论文监控任务 - {task_type.value}",
            description=f"自动监控任务，参数: {parameters}",
            status=TaskStatus.PENDING,
            priority=TaskPriority.NORMAL,
            parameters=parameters,
        )

        return task


def create_paper_monitor(config: AppConfig) -> PaperMonitor:
    """
    创建论文监控器实例

    Args:
        config: 应用程序配置

    Returns:
        论文监控器实例
    """
    return PaperMonitor(config)


if __name__ == "__main__":
    # 测试代码
    print("🧪 测试论文监控功能")

    # 示例论文数据
    test_papers = [
        {
            "arxiv_id": "2501.12345",
            "title": "Deep Learning for Cybersecurity Applications",
            "authors": ["Zhang Wei", "Li Ming"],
            "abstract": "This paper presents novel deep learning approaches for cybersecurity...",
            "url": "https://arxiv.org/abs/2501.12345",
        }
    ]

    monitor = create_paper_monitor(AppConfig())

    print(f"AI分析: {'启用' if monitor.analyzer else '禁用'}")

    # 测试每日监控
    result = monitor.daily_monitor(researchers=["Zhang Wei"], topics=["Deep Learning"])

    print(f"\n✅ 测试完成，每日监控结果: {result}")

    # 测试每周监控
    result = monitor.weekly_monitor(researchers=["Zhang Wei"], topics=["Deep Learning"])

    print(f"\n✅ 测试完成，每周监控结果: {result}")

    # 测试任务创建
    task = monitor.create_monitoring_task(
        TaskType.DAILY_MONITOR,
        {"researchers": ["Zhang Wei"], "topics": ["Deep Learning"]},
    )

    print(f"\n✅ 测试完成，任务创建: {task}")

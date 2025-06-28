"""
搜索引擎模块

提供统一的搜索接口，支持多种搜索策略和智能优化。
"""

import logging
import uuid
from datetime import date, datetime, timedelta

from ..models import SearchFilters, SearchQuery, SearchResult, SearchType
from ..models.config import AppConfig
from .collector import ArxivCollector

logger = logging.getLogger(__name__)


class SearchEngine:
    """统一搜索引擎"""

    def __init__(self, config: AppConfig):
        """初始化搜索引擎"""
        self.config = config
        self.collector = ArxivCollector(config)

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.collector.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.collector.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        """关闭搜索引擎"""
        await self.collector.close()

    def _create_query_id(self) -> str:
        """创建查询ID"""
        return (
            f"search_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        )

    def _apply_date_filters(self, query: SearchQuery) -> tuple | None:
        """应用日期过滤器"""
        filters = query.filters

        # 优先使用日期范围
        if filters.date_from or filters.date_to:
            return (filters.date_from, filters.date_to)

        # 使用回溯天数
        if filters.days_back:
            date_from = date.today() - timedelta(days=filters.days_back)
            return (date_from, None)

        return None

    def _build_category_filter(self, query: SearchQuery) -> list[str] | None:
        """构建分类过滤器"""
        categories = []

        # 添加查询中的主题（作为分类）
        categories.extend(query.topics)

        # 添加过滤器中的分类
        categories.extend(query.filters.categories)

        # 去重
        categories = list(set(categories))

        # 排除指定分类
        if query.filters.exclude_categories:
            categories = [
                cat for cat in categories if cat not in query.filters.exclude_categories
            ]

        return categories if categories else None

    async def search_by_researchers(self, query: SearchQuery) -> SearchResult:
        """按研究者搜索"""
        try:
            start_time = datetime.now()

            # 构建作者列表
            authors = query.researchers.copy()

            # 执行搜索
            result = await self.collector.search_by_authors(
                authors=authors, max_results=query.filters.max_results
            )

            # 更新查询信息
            result.query = query
            result.execution_time = start_time

            # 应用额外过滤
            result = await self._apply_post_filters(result, query)

            # 计算搜索时间
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            result.metrics.search_time_ms = search_time

            return result

        except Exception as e:
            logger.error(f"Error in researcher search: {e}")
            return self._create_error_result(query, str(e))

    async def search_by_topics(self, query: SearchQuery) -> SearchResult:
        """按主题搜索"""
        try:
            start_time = datetime.now()

            # 获取分类过滤器
            categories = self._build_category_filter(query)
            if not categories:
                categories = self.config.monitoring.default_search_topics

            # 获取日期过滤器
            date_range = self._apply_date_filters(query)

            # 执行搜索
            if date_range:
                result = await self.collector.search_by_date_range(
                    date_from=date_range[0],
                    date_to=date_range[1],
                    categories=categories,
                    max_results=query.filters.max_results,
                )
            else:
                result = await self.collector.search_by_categories(
                    categories=categories, max_results=query.filters.max_results
                )

            # 更新查询信息
            result.query = query
            result.execution_time = start_time

            # 应用额外过滤
            result = await self._apply_post_filters(result, query)

            # 计算搜索时间
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            result.metrics.search_time_ms = search_time

            return result

        except Exception as e:
            logger.error(f"Error in topic search: {e}")
            return self._create_error_result(query, str(e))

    async def search_by_keywords(self, query: SearchQuery) -> SearchResult:
        """按关键词搜索"""
        try:
            start_time = datetime.now()

            # 构建搜索查询字符串
            search_terms = []

            # 添加查询文本
            if query.query_text:
                search_terms.append(f'all:"{query.query_text}"')

            # 添加关键词
            for keyword in query.keywords:
                search_terms.append(f'all:"{keyword}"')

            # 组合查询
            if not search_terms:
                raise ValueError("No search terms provided")

            search_string = " OR ".join(search_terms)

            # 添加分类过滤
            categories = self._build_category_filter(query)
            if categories:
                cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
                search_string = f"({search_string}) AND ({cat_query})"

            # 执行搜索
            result = await self.collector.search_by_query(
                query=search_string, max_results=query.filters.max_results
            )

            # 更新查询信息
            result.query = query
            result.execution_time = start_time

            # 应用额外过滤
            result = await self._apply_post_filters(result, query)

            # 计算搜索时间
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            result.metrics.search_time_ms = search_time

            return result

        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return self._create_error_result(query, str(e))

    async def search_hybrid(self, query: SearchQuery) -> SearchResult:
        """混合搜索（结合多种策略）"""
        try:
            start_time = datetime.now()

            # 创建智能查询
            smart_query = self.collector.create_smart_query(
                topics=query.topics,
                authors=query.researchers,
                date_from=(
                    self._apply_date_filters(query)[0]
                    if self._apply_date_filters(query)
                    else None
                ),
                exclude_categories=query.filters.exclude_categories,
            )

            # 执行搜索
            result = await self.collector.search_by_query(
                query=smart_query, max_results=query.filters.max_results
            )

            # 更新查询信息
            result.query = query
            result.execution_time = start_time

            # 应用额外过滤
            result = await self._apply_post_filters(result, query)

            # 计算搜索时间
            search_time = (datetime.now() - start_time).total_seconds() * 1000
            result.metrics.search_time_ms = search_time

            return result

        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return self._create_error_result(query, str(e))

    async def search(self, query: SearchQuery) -> SearchResult:
        """统一搜索接口"""
        logger.info(f"Executing search: {query.search_type} - {query.query_text}")

        # 根据搜索类型分发
        if query.search_type == SearchType.RESEARCHER:
            return await self.search_by_researchers(query)
        elif query.search_type == SearchType.TOPIC:
            return await self.search_by_topics(query)
        elif query.search_type == SearchType.KEYWORD:
            return await self.search_by_keywords(query)
        elif query.search_type == SearchType.HYBRID:
            return await self.search_hybrid(query)
        else:
            # 默认使用混合搜索
            query.search_type = SearchType.HYBRID
            return await self.search_hybrid(query)

    async def _apply_post_filters(
        self, result: SearchResult, query: SearchQuery
    ) -> SearchResult:
        """应用后处理过滤器"""
        papers = result.papers.copy()

        # 按评分过滤
        if query.filters.min_score is not None:
            papers = [p for p in papers if p.get("score", 0) >= query.filters.min_score]

        # 按作者过滤
        if query.filters.authors:

            def matches_author(
                paper_authors: list[str], filter_authors: list[str]
            ) -> bool:
                for filter_author in filter_authors:
                    for paper_author in paper_authors:
                        if filter_author.lower() in paper_author.lower():
                            return True
                return False

            papers = [
                p
                for p in papers
                if matches_author(p.get("authors", []), query.filters.authors)
            ]

        # 排除作者
        if query.filters.exclude_authors:

            def excludes_author(
                paper_authors: list[str], exclude_authors: list[str]
            ) -> bool:
                for exclude_author in exclude_authors:
                    for paper_author in paper_authors:
                        if exclude_author.lower() in paper_author.lower():
                            return True
                return False

            papers = [
                p
                for p in papers
                if not excludes_author(
                    p.get("authors", []), query.filters.exclude_authors
                )
            ]

        # 按日期过滤（如果ArXiv搜索没有处理）
        date_range = self._apply_date_filters(query)
        if date_range and date_range[0]:
            papers = [
                p
                for p in papers
                if p.get("submitted_date")
                and (
                    isinstance(p["submitted_date"], datetime)
                    and p["submitted_date"].date() >= date_range[0]
                )
            ]

        # 创建新结果
        filtered_result = SearchResult(
            query=result.query,
            papers=papers,
            execution_time=result.execution_time,
            success=result.success,
        )

        # 更新指标
        filtered_result.metrics = result.metrics.copy()
        filtered_result.metrics.total_returned = len(papers)
        filtered_result.update_metrics()

        return filtered_result

    def _create_error_result(
        self, query: SearchQuery, error_message: str
    ) -> SearchResult:
        """创建错误结果"""
        return SearchResult(
            query=query, papers=[], success=False, error_message=error_message
        )

    async def search_recent_papers(
        self,
        days_back: int = 3,
        topics: list[str] | None = None,
        max_results: int = 50,
    ) -> SearchResult:
        """搜索最近的论文（便捷方法）"""
        query = SearchQuery(
            query_id=self._create_query_id(),
            search_type=SearchType.TOPIC,
            query_text=f"Recent papers from last {days_back} days",
            topics=topics or self.config.monitoring.default_search_topics,
            filters=SearchFilters(days_back=days_back, max_results=max_results),
        )

        return await self.search(query)

    async def search_by_author_names(
        self, author_names: list[str], max_results: int = 50
    ) -> SearchResult:
        """按作者姓名搜索（便捷方法）"""
        query = SearchQuery(
            query_id=self._create_query_id(),
            search_type=SearchType.RESEARCHER,
            query_text=f"Papers by: {', '.join(author_names)}",
            researchers=author_names,
            filters=SearchFilters(max_results=max_results),
        )

        return await self.search(query)

    async def search_cross_domain(
        self, primary_topics: list[str], days_back: int = 7, max_results: int = 50
    ) -> SearchResult:
        """跨领域搜索（便捷方法）"""
        query = SearchQuery(
            query_id=self._create_query_id(),
            search_type=SearchType.TOPIC,
            query_text=f"Cross-domain search: {' AND '.join(primary_topics)}",
            topics=primary_topics,
            filters=SearchFilters(days_back=days_back, max_results=max_results),
        )

        return await self.search(query)

    def create_search_query(
        self, search_type: SearchType, query_text: str, **kwargs
    ) -> SearchQuery:
        """创建搜索查询对象（便捷方法）"""
        return SearchQuery(
            query_id=self._create_query_id(),
            search_type=search_type,
            query_text=query_text,
            **kwargs,
        )

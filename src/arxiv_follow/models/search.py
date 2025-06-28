"""
搜索相关的数据模型

定义搜索查询、结果和过滤器的数据结构。
"""

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class SearchType(str, Enum):
    """搜索类型"""

    RESEARCHER = "researcher"  # 按研究者搜索
    TOPIC = "topic"  # 按主题搜索
    KEYWORD = "keyword"  # 按关键词搜索
    CATEGORY = "category"  # 按分类搜索
    HYBRID = "hybrid"  # 混合搜索


class SortOrder(str, Enum):
    """排序方式"""

    RELEVANCE = "relevance"  # 按相关性
    DATE_DESC = "date_desc"  # 按日期降序
    DATE_ASC = "date_asc"  # 按日期升序
    CITATIONS = "citations"  # 按引用数
    SCORE = "score"  # 按评分


class SearchFilters(BaseModel):
    """搜索过滤器"""

    # 时间过滤
    date_from: date | None = Field(None, description="开始日期")
    date_to: date | None = Field(None, description="结束日期")
    days_back: int | None = Field(None, ge=1, le=365, description="回溯天数")

    # 分类过滤
    categories: list[str] = Field(default_factory=list, description="分类过滤")
    exclude_categories: list[str] = Field(default_factory=list, description="排除分类")

    # 作者过滤
    authors: list[str] = Field(default_factory=list, description="作者过滤")
    exclude_authors: list[str] = Field(default_factory=list, description="排除作者")

    # 机构过滤
    institutions: list[str] = Field(default_factory=list, description="机构过滤")

    # 质量过滤
    min_score: float | None = Field(None, ge=0, le=10, description="最低评分")
    has_code: bool | None = Field(None, description="是否包含代码")
    has_data: bool | None = Field(None, description="是否包含数据")

    # 语言过滤
    languages: list[str] = Field(default_factory=list, description="语言过滤")

    # 数量限制
    max_results: int = Field(default=50, ge=1, le=1000, description="最大结果数")

    @validator("date_to")
    def validate_date_range(
        cls, v: date | None, values: dict[str, Any]
    ) -> date | None:
        """验证日期范围"""
        if v and "date_from" in values and values["date_from"]:
            if v < values["date_from"]:
                raise ValueError("date_to must be after date_from")
        return v


class SearchQuery(BaseModel):
    """搜索查询"""

    # 基础信息
    query_id: str = Field(..., description="查询ID")
    search_type: SearchType = Field(..., description="搜索类型")

    # 查询内容
    query_text: str = Field(..., description="查询文本")
    keywords: list[str] = Field(default_factory=list, description="关键词列表")
    researchers: list[str] = Field(default_factory=list, description="研究者列表")
    topics: list[str] = Field(default_factory=list, description="主题列表")

    # 搜索配置
    filters: SearchFilters = Field(
        default_factory=SearchFilters, description="搜索过滤器"
    )
    sort_order: SortOrder = Field(default=SortOrder.RELEVANCE, description="排序方式")

    # 高级配置
    use_ai_enhancement: bool = Field(default=True, description="是否使用AI增强")
    include_content: bool = Field(default=False, description="是否包含论文内容")
    enable_translation: bool = Field(default=False, description="是否启用翻译")

    # 元信息
    created_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    created_by: str | None = Field(None, description="创建者")
    description: str | None = Field(None, description="查询描述")
    tags: list[str] = Field(default_factory=list, description="标签")

    @validator("query_text")
    def validate_query_text(cls, v: str) -> str:
        """验证查询文本"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Query text cannot be empty")
        return v.strip()

    @validator("keywords")
    def validate_keywords(cls, v: list[str]) -> list[str]:
        """验证关键词"""
        return [kw.strip() for kw in v if kw.strip()]

    def get_search_terms(self) -> list[str]:
        """获取所有搜索术语"""
        terms = []

        # 添加查询文本中的词汇
        terms.extend(self.query_text.split())

        # 添加关键词
        terms.extend(self.keywords)

        # 添加主题
        terms.extend(self.topics)

        # 去重并返回
        return list(set(term.strip().lower() for term in terms if term.strip()))

    def is_researcher_search(self) -> bool:
        """是否为研究者搜索"""
        return self.search_type == SearchType.RESEARCHER or bool(self.researchers)

    def is_topic_search(self) -> bool:
        """是否为主题搜索"""
        return self.search_type == SearchType.TOPIC or bool(self.topics)


class SearchMetrics(BaseModel):
    """搜索指标"""

    total_found: int = Field(default=0, description="找到的总数")
    total_returned: int = Field(default=0, description="返回的数量")
    search_time_ms: float = Field(default=0, description="搜索时间(毫秒)")

    # 质量指标
    avg_relevance_score: float | None = Field(None, description="平均相关性评分")
    high_quality_count: int = Field(default=0, description="高质量论文数量")

    # 分类统计
    category_distribution: dict[str, int] = Field(
        default_factory=dict, description="分类分布"
    )
    author_distribution: dict[str, int] = Field(
        default_factory=dict, description="作者分布"
    )

    # 时间分布
    date_distribution: dict[str, int] = Field(
        default_factory=dict, description="日期分布"
    )


class SearchResult(BaseModel):
    """搜索结果"""

    # 基础信息
    query: SearchQuery = Field(..., description="搜索查询")

    # 结果数据
    papers: list[dict[str, Any]] = Field(default_factory=list, description="论文列表")

    # 统计信息
    metrics: SearchMetrics = Field(
        default_factory=SearchMetrics, description="搜索指标"
    )

    # 执行信息
    execution_time: datetime = Field(
        default_factory=datetime.now, description="执行时间"
    )
    success: bool = Field(default=True, description="是否成功")
    error_message: str | None = Field(None, description="错误信息")

    # 分页信息
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=50, ge=1, le=1000, description="每页数量")
    has_next_page: bool = Field(default=False, description="是否有下一页")

    # 增强信息
    ai_summary: str | None = Field(None, description="AI生成的结果摘要")
    recommendations: list[str] = Field(default_factory=list, description="推荐相关搜索")

    @property
    def paper_count(self) -> int:
        """获取论文数量"""
        return len(self.papers)

    @property
    def has_results(self) -> bool:
        """是否有结果"""
        return self.paper_count > 0

    def get_arxiv_ids(self) -> list[str]:
        """获取ArXiv ID列表"""
        return [
            paper.get("arxiv_id", "") for paper in self.papers if paper.get("arxiv_id")
        ]

    def get_authors(self) -> list[str]:
        """获取所有作者"""
        authors = []
        for paper in self.papers:
            paper_authors = paper.get("authors", [])
            if isinstance(paper_authors, list):
                authors.extend(paper_authors)
        return list(set(authors))

    def get_categories(self) -> list[str]:
        """获取所有分类"""
        categories = []
        for paper in self.papers:
            paper_categories = paper.get("categories", [])
            if isinstance(paper_categories, list):
                categories.extend(paper_categories)
            elif isinstance(paper_categories, str):
                categories.append(paper_categories)
        return list(set(categories))

    def filter_by_score(self, min_score: float) -> "SearchResult":
        """按评分过滤"""
        filtered_papers = [
            paper for paper in self.papers if paper.get("score", 0) >= min_score
        ]

        # 创建新的搜索结果
        new_result = self.copy()
        new_result.papers = filtered_papers
        new_result.metrics.total_returned = len(filtered_papers)

        return new_result

    def sort_by_date(self, descending: bool = True) -> "SearchResult":
        """按日期排序"""
        sorted_papers = sorted(
            self.papers, key=lambda p: p.get("submitted_date", ""), reverse=descending
        )

        new_result = self.copy()
        new_result.papers = sorted_papers

        return new_result

    def update_metrics(self) -> None:
        """更新统计指标"""
        self.metrics.total_returned = len(self.papers)

        # 计算分类分布
        category_counts: dict[str, int] = {}
        for paper in self.papers:
            categories = paper.get("categories", [])
            if isinstance(categories, list):
                for cat in categories:
                    category_counts[cat] = category_counts.get(cat, 0) + 1
        self.metrics.category_distribution = category_counts

        # 计算作者分布
        author_counts: dict[str, int] = {}
        for paper in self.papers:
            authors = paper.get("authors", [])
            if isinstance(authors, list):
                for author in authors:
                    author_counts[author] = author_counts.get(author, 0) + 1
        self.metrics.author_distribution = dict(
            list(author_counts.items())[:10]
        )  # 只保留前10

        # 计算高质量论文数量
        self.metrics.high_quality_count = sum(
            1 for paper in self.papers if paper.get("score", 0) >= 7.0
        )

        # 计算平均相关性评分
        scores = [paper.get("score", 0) for paper in self.papers if paper.get("score")]
        if scores:
            self.metrics.avg_relevance_score = sum(scores) / len(scores)

    class Config:
        """Pydantic配置"""

        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = True

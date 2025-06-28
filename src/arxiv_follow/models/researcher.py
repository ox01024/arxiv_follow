"""
研究者相关的数据模型

定义研究者、研究领域和个人资料的数据结构。
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl, validator


class ResearchField(str, Enum):
    """研究领域"""

    # 计算机科学
    ARTIFICIAL_INTELLIGENCE = "artificial_intelligence"
    MACHINE_LEARNING = "machine_learning"
    COMPUTER_VISION = "computer_vision"
    NATURAL_LANGUAGE_PROCESSING = "natural_language_processing"
    ROBOTICS = "robotics"
    CRYPTOGRAPHY = "cryptography"
    HUMAN_COMPUTER_INTERACTION = "human_computer_interaction"

    # 数学与统计
    STATISTICS = "statistics"
    OPTIMIZATION = "optimization"
    PROBABILITY = "probability"

    # 物理学
    PHYSICS = "physics"
    ASTROPHYSICS = "astrophysics"

    # 生物学
    COMPUTATIONAL_BIOLOGY = "computational_biology"
    BIOINFORMATICS = "bioinformatics"

    # 经济学
    ECONOMICS = "economics"
    ECONOMETRICS = "econometrics"

    # 其他
    OTHER = "other"


class ResearcherStatus(str, Enum):
    """研究者状态"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"


class ResearcherProfile(BaseModel):
    """研究者个人资料"""

    full_name: str = Field(..., description="全名")
    email: str | None = Field(None, description="邮箱")

    # 机构信息
    institution: str | None = Field(None, description="所属机构")
    department: str | None = Field(None, description="部门")
    position: str | None = Field(None, description="职位")

    # 联系方式
    homepage: HttpUrl | None = Field(None, description="个人主页")
    google_scholar: HttpUrl | None = Field(None, description="Google Scholar链接")
    orcid: str | None = Field(None, description="ORCID ID")

    # 研究信息
    research_fields: list[ResearchField] = Field(
        default_factory=list, description="研究领域"
    )
    research_interests: list[str] = Field(default_factory=list, description="研究兴趣")
    bio: str | None = Field(None, description="个人简介")

    # 统计信息
    h_index: int | None = Field(None, description="H指数")
    citation_count: int | None = Field(None, description="引用数")
    paper_count: int | None = Field(None, description="论文数量")

    # 最近活动
    last_paper_date: datetime | None = Field(None, description="最新论文日期")

    @validator("orcid")
    def validate_orcid(cls, v: str | None) -> str | None:
        """验证ORCID格式"""
        if v is None:
            return v
        import re

        if not re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", v):
            raise ValueError(f"Invalid ORCID format: {v}")
        return v


class Researcher(BaseModel):
    """研究者模型"""

    # 基础标识
    researcher_id: str = Field(..., description="研究者唯一ID")
    arxiv_name: str = Field(..., description="在ArXiv上的姓名")
    name_variants: list[str] = Field(default_factory=list, description="姓名变体")

    # 个人资料
    profile: ResearcherProfile = Field(..., description="个人资料")

    # 状态信息
    status: ResearcherStatus = Field(
        default=ResearcherStatus.UNKNOWN, description="研究者状态"
    )
    is_monitored: bool = Field(default=True, description="是否监控")
    priority: int = Field(default=5, ge=1, le=10, description="监控优先级 (1-10)")

    # 论文统计
    recent_papers: list[str] = Field(
        default_factory=list, description="最近论文ArXiv ID列表"
    )
    all_papers: list[str] = Field(
        default_factory=list, description="所有论文ArXiv ID列表"
    )

    # 监控配置
    notification_enabled: bool = Field(default=True, description="是否启用通知")
    monitor_frequency: str = Field(default="daily", description="监控频率")

    # 系统信息
    created_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    last_checked: datetime | None = Field(None, description="最后检查时间")
    last_updated: datetime = Field(
        default_factory=datetime.now, description="最后更新时间"
    )

    # 标签和分类
    tags: list[str] = Field(default_factory=list, description="自定义标签")
    notes: str | None = Field(None, description="备注")

    @validator("researcher_id")
    def validate_researcher_id(cls, v: str) -> str:
        """验证研究者ID格式"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Researcher ID cannot be empty")
        return v.strip()

    @validator("monitor_frequency")
    def validate_monitor_frequency(cls, v: str) -> str:
        """验证监控频率"""
        valid_frequencies = ["hourly", "daily", "weekly", "monthly"]
        if v not in valid_frequencies:
            raise ValueError(
                f"Invalid monitor frequency: {v}. Must be one of {valid_frequencies}"
            )
        return v

    @property
    def display_name(self) -> str:
        """获取显示名称"""
        return self.profile.full_name or self.arxiv_name

    @property
    def institution_display(self) -> str:
        """获取机构显示信息"""
        parts = []
        if self.profile.institution:
            parts.append(self.profile.institution)
        if self.profile.department:
            parts.append(self.profile.department)
        return " - ".join(parts) if parts else "Unknown"

    def get_research_fields_display(self) -> str:
        """获取研究领域显示字符串"""
        if not self.profile.research_fields:
            return "Unknown"
        return ", ".join(
            [
                field.value.replace("_", " ").title()
                for field in self.profile.research_fields
            ]
        )

    def update_paper_stats(self, paper_ids: list[str]) -> None:
        """更新论文统计信息"""
        self.all_papers = list(set(self.all_papers + paper_ids))
        self.profile.paper_count = len(self.all_papers)
        self.last_updated = datetime.now()

    def add_recent_paper(self, paper_id: str) -> None:
        """添加最近论文"""
        if paper_id not in self.recent_papers:
            self.recent_papers.insert(0, paper_id)
            # 保持最近论文列表在合理大小
            self.recent_papers = self.recent_papers[:20]

        # 同时添加到所有论文列表
        if paper_id not in self.all_papers:
            self.all_papers.append(paper_id)
            self.profile.paper_count = len(self.all_papers)

        self.last_updated = datetime.now()

    def is_active_recently(self, days: int = 180) -> bool:
        """检查最近是否活跃"""
        if not self.profile.last_paper_date:
            return False

        from datetime import timedelta

        threshold = datetime.now() - timedelta(days=days)
        return self.profile.last_paper_date >= threshold

    def matches_name(self, name: str) -> bool:
        """检查姓名是否匹配"""
        name_lower = name.lower()

        # 检查主要姓名
        if name_lower == self.arxiv_name.lower():
            return True
        if name_lower == self.profile.full_name.lower():
            return True

        # 检查姓名变体
        for variant in self.name_variants:
            if name_lower == variant.lower():
                return True

        return False

    class Config:
        """Pydantic配置"""

        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = True

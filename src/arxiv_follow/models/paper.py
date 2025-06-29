"""
论文相关的数据模型

定义论文、元数据、内容和分析结果的数据结构。
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, validator


class PaperStatus(str, Enum):
    """论文状态"""

    SUBMITTED = "submitted"
    REVISED = "revised"
    PUBLISHED = "published"
    WITHDRAWN = "withdrawn"


class PaperCategory(str, Enum):
    """ArXiv 主要分类"""

    # Computer Science
    CS_AI = "cs.AI"  # Artificial Intelligence
    CS_CL = "cs.CL"  # Computation and Language
    CS_CV = "cs.CV"  # Computer Vision and Pattern Recognition
    CS_LG = "cs.LG"  # Machine Learning
    CS_CR = "cs.CR"  # Cryptography and Security
    CS_RO = "cs.RO"  # Robotics
    CS_SI = "cs.SI"  # Social and Information Networks
    CS_HC = "cs.HC"  # Human-Computer Interaction

    # Physics
    PHYSICS_GEN_PH = "physics.gen-ph"  # General Physics
    ASTRO_PH = "astro-ph"  # Astrophysics

    # Mathematics
    MATH_OC = "math.OC"  # Optimization and Control
    MATH_ST = "math.ST"  # Statistics Theory

    # Quantitative Biology
    Q_BIO = "q-bio"  # Quantitative Biology

    # Economics
    ECON = "econ"  # Economics


class PaperMetadata(BaseModel):
    """论文元数据"""

    arxiv_id: str = Field(..., description="ArXiv ID，如 2501.12345")
    title: str = Field(..., description="论文标题")
    authors: list[str] = Field(default_factory=list, description="作者列表")
    abstract: str = Field(default="", description="摘要")

    # 分类信息
    primary_category: str | None = Field(None, description="主要分类")
    categories: list[str] = Field(default_factory=list, description="所有分类")

    # 时间信息
    submitted_date: datetime | None = Field(None, description="提交日期")
    updated_date: datetime | None = Field(None, description="更新日期")
    published_date: datetime | None = Field(None, description="发布日期")

    # 状态和版本
    status: PaperStatus = Field(default=PaperStatus.SUBMITTED, description="论文状态")
    version: str = Field(default="v1", description="版本号")

    # 元信息
    doi: str | None = Field(None, description="DOI")
    journal_ref: str | None = Field(None, description="期刊引用")
    comments: str | None = Field(None, description="备注信息")

    # URLs
    arxiv_url: HttpUrl | None = Field(None, description="ArXiv链接")
    pdf_url: HttpUrl | None = Field(None, description="PDF链接")
    html_url: HttpUrl | None = Field(None, description="HTML链接")

    @validator("arxiv_id")
    def validate_arxiv_id(cls, v: str) -> str:
        """验证ArXiv ID格式"""
        import re

        if not re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", v):
            raise ValueError(f"Invalid ArXiv ID format: {v}")
        return v

    @validator("arxiv_url", pre=True, always=True)
    def generate_arxiv_url(cls, v: str | None, values: dict[str, Any]) -> str | None:
        """自动生成ArXiv URL"""
        if v is None and "arxiv_id" in values:
            return f"https://arxiv.org/abs/{values['arxiv_id']}"
        return v

    @validator("pdf_url", pre=True, always=True)
    def generate_pdf_url(cls, v: str | None, values: dict[str, Any]) -> str | None:
        """自动生成PDF URL"""
        if v is None and "arxiv_id" in values:
            return f"https://arxiv.org/pdf/{values['arxiv_id']}.pdf"
        return v


class PaperContent(BaseModel):
    """论文内容"""

    arxiv_id: str = Field(..., description="ArXiv ID")

    # 原始内容
    raw_text: str | None = Field(None, description="原始文本内容")
    html_content: str | None = Field(None, description="HTML格式内容")

    # 结构化内容
    sections: dict[str, str] = Field(default_factory=dict, description="章节内容")
    references: list[str] = Field(default_factory=list, description="参考文献")
    figures: list[dict[str, Any]] = Field(default_factory=list, description="图表信息")
    tables: list[dict[str, Any]] = Field(default_factory=list, description="表格信息")

    # 提取元信息
    extraction_method: str = Field(default="auto", description="内容提取方法")
    extraction_time: datetime = Field(
        default_factory=datetime.now, description="提取时间"
    )
    extraction_success: bool = Field(default=False, description="提取是否成功")

    # 语言和格式
    language: str = Field(default="en", description="语言")
    has_latex: bool = Field(default=False, description="是否包含LaTeX")
    has_code: bool = Field(default=False, description="是否包含代码")


class AnalysisType(str, Enum):
    """分析类型"""

    IMPORTANCE = "importance"
    TECHNICAL = "technical"
    NOVELTY = "novelty"
    IMPACT = "impact"
    SUMMARY = "summary"
    TRANSLATION = "translation"


class PaperAnalysis(BaseModel):
    """论文AI分析结果"""

    arxiv_id: str = Field(..., description="ArXiv ID")
    analysis_type: AnalysisType = Field(..., description="分析类型")

    # 分析结果
    score: float | None = Field(None, ge=0, le=10, description="评分 (0-10)")
    summary: str = Field(default="", description="分析摘要")
    key_points: list[str] = Field(default_factory=list, description="关键要点")
    strengths: list[str] = Field(default_factory=list, description="优势")
    weaknesses: list[str] = Field(default_factory=list, description="不足")

    # 技术细节
    methodology: str | None = Field(None, description="方法论分析")
    contributions: list[str] = Field(default_factory=list, description="主要贡献")
    limitations: list[str] = Field(default_factory=list, description="局限性")

    # 分析元信息
    model_used: str = Field(..., description="使用的AI模型")
    analysis_time: datetime = Field(
        default_factory=datetime.now, description="分析时间"
    )
    confidence: float | None = Field(None, ge=0, le=1, description="置信度")

    # 翻译内容（如果是翻译分析）
    translated_title: str | None = Field(None, description="翻译标题")
    translated_abstract: str | None = Field(None, description="翻译摘要")
    translated_summary: str | None = Field(None, description="翻译总结")


class Paper(BaseModel):
    """完整的论文模型"""

    # 基础信息
    metadata: PaperMetadata = Field(..., description="论文元数据")
    content: PaperContent | None = Field(None, description="论文内容")

    # 分析结果
    analyses: list[PaperAnalysis] = Field(
        default_factory=list, description="AI分析结果"
    )

    # 系统信息
    discovered_time: datetime = Field(
        default_factory=datetime.now, description="发现时间"
    )
    last_updated: datetime = Field(
        default_factory=datetime.now, description="最后更新时间"
    )

    # 标签和分类
    tags: list[str] = Field(default_factory=list, description="自定义标签")
    priority: int = Field(default=0, description="优先级 (0-10)")

    # 关联信息
    related_papers: list[str] = Field(default_factory=list, description="相关论文ID")
    citing_papers: list[str] = Field(default_factory=list, description="引用此论文的ID")
    cited_papers: list[str] = Field(default_factory=list, description="此论文引用的ID")

    @property
    def arxiv_id(self) -> str:
        """获取ArXiv ID"""
        return self.metadata.arxiv_id

    @property
    def title(self) -> str:
        """获取标题"""
        return self.metadata.title

    @property
    def authors(self) -> list[str]:
        """获取作者列表"""
        return self.metadata.authors

    def get_analysis_by_type(self, analysis_type: AnalysisType) -> PaperAnalysis | None:
        """根据类型获取分析结果"""
        for analysis in self.analyses:
            if analysis.analysis_type == analysis_type:
                return analysis
        return None

    def add_analysis(self, analysis: PaperAnalysis) -> None:
        """添加分析结果"""
        # 如果已存在相同类型的分析，则替换
        self.analyses = [
            a for a in self.analyses if a.analysis_type != analysis.analysis_type
        ]
        self.analyses.append(analysis)
        self.last_updated = datetime.now()

    def has_content(self) -> bool:
        """检查是否有内容"""
        return self.content is not None and (
            self.content.raw_text
            or self.content.html_content
            or bool(self.content.sections)
        )

    def is_analyzed(self, analysis_type: AnalysisType) -> bool:
        """检查是否已进行指定类型的分析"""
        return self.get_analysis_by_type(analysis_type) is not None

    class Config:
        """Pydantic配置"""

        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = True

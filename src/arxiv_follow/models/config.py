"""
配置相关的数据模型

定义应用配置、API配置和集成配置的数据结构。
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings

from ..config.models import get_default_model


class LogLevel(str, Enum):
    """日志级别"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StorageBackend(str, Enum):
    """存储后端"""

    LOCAL = "local"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"


class APIConfig(BaseModel):
    """API配置"""

    # OpenRouter API (用于AI功能)
    openrouter_api_key: str | None = Field(None, description="OpenRouter API密钥")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1", description="OpenRouter API基础URL"
    )

    # 别名属性用于analyzer
    @property
    def api_base_url(self) -> str:
        return self.openrouter_base_url

    @property
    def default_model(self) -> str:
        return get_default_model()

    # ArXiv API配置
    arxiv_base_url: str = Field(
        default="http://export.arxiv.org/api/query", description="ArXiv API基础URL"
    )
    arxiv_delay_seconds: float = Field(
        default=3.0, ge=0, description="ArXiv API请求延迟(秒)"
    )
    arxiv_timeout_seconds: int = Field(
        default=30, ge=1, description="ArXiv API超时时间(秒)"
    )

    # 滴答清单API配置
    dida_access_token: str | None = Field(None, description="滴答清单访问令牌")
    dida_base_url: str = Field(
        default="https://api.dida365.com/api/v2", description="滴答清单API基础URL"
    )

    # 通用HTTP配置
    http_timeout: int = Field(default=30, ge=1, description="HTTP请求超时时间(秒)")
    http_retries: int = Field(default=3, ge=0, description="HTTP请求重试次数")
    user_agent: str = Field(
        default="ArXiv-Follow/1.0.0 (Academic Research Tool)",
        description="User-Agent字符串",
    )


class IntegrationConfig(BaseModel):
    """集成配置"""

    # 滴答清单集成
    dida_enabled: bool = Field(default=False, description="是否启用滴答清单集成")
    dida_project_name: str = Field(default="ArXiv 论文", description="滴答清单项目名称")
    dida_auto_create_tasks: bool = Field(default=True, description="是否自动创建任务")

    # 翻译服务
    translation_enabled: bool = Field(default=False, description="是否启用翻译服务")
    default_source_language: str = Field(default="en", description="默认源语言")
    default_target_language: str = Field(default="zh", description="默认目标语言")

    # AI分析 - 使用动态获取的默认模型
    ai_analysis_enabled: bool = Field(default=False, description="是否启用AI分析")
    ai_temperature: float = Field(default=0.3, ge=0, le=2, description="AI温度参数")
    ai_max_tokens: int = Field(default=2048, ge=1, description="AI最大令牌数")

    @property
    def ai_model(self) -> str:
        """获取AI模型名称"""
        return get_default_model()

    # 通知配置
    notifications_enabled: bool = Field(default=True, description="是否启用通知")
    notification_methods: list[str] = Field(
        default_factory=lambda: ["console"], description="通知方式"
    )


class StorageConfig(BaseModel):
    """存储配置"""

    backend: StorageBackend = Field(
        default=StorageBackend.LOCAL, description="存储后端"
    )

    # 本地文件存储
    data_dir: str = Field(default="./data", description="数据目录")
    cache_dir: str = Field(default="./cache", description="缓存目录")
    output_dir: str = Field(default="./reports", description="输出目录")

    # 数据库配置
    database_url: str | None = Field(None, description="数据库连接URL")

    # 缓存配置
    enable_cache: bool = Field(default=True, description="是否启用缓存")
    cache_ttl_seconds: int = Field(default=3600, ge=0, description="缓存生存时间(秒)")
    max_cache_size_mb: int = Field(default=500, ge=1, description="最大缓存大小(MB)")


class MonitoringConfig(BaseModel):
    """监控配置"""

    # 研究者监控
    daily_check_enabled: bool = Field(default=True, description="是否启用每日检查")
    weekly_summary_enabled: bool = Field(default=True, description="是否启用周报")

    # 主题监控
    topic_search_enabled: bool = Field(default=True, description="是否启用主题搜索")
    default_search_topics: list[str] = Field(
        default_factory=lambda: ["cs.AI", "cs.CR"], description="默认搜索主题"
    )

    # 监控频率
    check_interval_hours: int = Field(
        default=6, ge=1, le=24, description="检查间隔(小时)"
    )
    max_papers_per_check: int = Field(
        default=100, ge=1, description="每次检查最大论文数"
    )

    # 过滤配置
    min_paper_score: float = Field(default=5.0, ge=0, le=10, description="最低论文评分")
    exclude_categories: list[str] = Field(
        default_factory=list, description="排除的分类"
    )


class AppConfig(BaseSettings):
    """应用配置"""

    # 基础信息
    app_name: str = Field(default="ArXiv Follow", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="是否为调试模式")

    # 日志配置
    log_level: LogLevel = Field(default=LogLevel.INFO, description="日志级别")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式",
    )
    log_file: str | None = Field(None, description="日志文件路径")

    # 子配置
    api: APIConfig = Field(default_factory=APIConfig, description="API配置")
    integrations: IntegrationConfig = Field(
        default_factory=IntegrationConfig, description="集成配置"
    )
    storage: StorageConfig = Field(
        default_factory=StorageConfig, description="存储配置"
    )
    monitoring: MonitoringConfig = Field(
        default_factory=MonitoringConfig, description="监控配置"
    )

    # 性能配置
    max_concurrent_requests: int = Field(default=10, ge=1, description="最大并发请求数")
    request_delay_seconds: float = Field(default=1.0, ge=0, description="请求延迟(秒)")

    # 安全配置
    enable_rate_limiting: bool = Field(default=True, description="是否启用速率限制")
    max_requests_per_minute: int = Field(
        default=60, ge=1, description="每分钟最大请求数"
    )

    class Config:
        """Pydantic设置配置"""

        env_file = ".env"
        env_nested_delimiter = "__"
        case_sensitive = False

        # 环境变量前缀
        env_prefix = "ARXIV_FOLLOW_"

        # 字段映射
        fields = {
            "api.openrouter_api_key": {"env": "OPEN_ROUTE_API_KEY"},
            "api.dida_access_token": {"env": "DIDA_ACCESS_TOKEN"},
        }

    @validator("storage")
    def validate_storage_config(
        cls, v: StorageConfig, values: dict[str, Any]
    ) -> StorageConfig:
        """验证存储配置"""
        if v.backend == StorageBackend.POSTGRESQL and not v.database_url:
            raise ValueError("PostgreSQL backend requires database_url")
        if v.backend == StorageBackend.MONGODB and not v.database_url:
            raise ValueError("MongoDB backend requires database_url")
        return v

    @validator("integrations")
    def validate_integration_config(
        cls, v: IntegrationConfig, values: dict[str, Any]
    ) -> IntegrationConfig:
        """验证集成配置"""
        # 检查API配置
        api_config = values.get("api")
        if api_config:
            if v.dida_enabled and not api_config.dida_access_token:
                raise ValueError(
                    "Dida integration enabled but no access token provided"
                )
            if v.ai_analysis_enabled and not api_config.openrouter_api_key:
                raise ValueError(
                    "AI analysis enabled but no OpenRouter API key provided"
                )

        return v

    def get_effective_log_level(self) -> str:
        """获取有效的日志级别"""
        if self.debug:
            return LogLevel.DEBUG.value
        return self.log_level.value

    def is_feature_enabled(self, feature: str) -> bool:
        """检查功能是否启用"""
        feature_map = {
            "dida": self.integrations.dida_enabled,
            "translation": self.integrations.translation_enabled,
            "ai_analysis": self.integrations.ai_analysis_enabled,
            "notifications": self.integrations.notifications_enabled,
            "daily_check": self.monitoring.daily_check_enabled,
            "weekly_summary": self.monitoring.weekly_summary_enabled,
            "topic_search": self.monitoring.topic_search_enabled,
        }

        return feature_map.get(feature, False)

    def get_llm_api_key(self) -> str | None:
        """获取LLM API密钥"""
        return self.api.openrouter_api_key

    @property
    def llm(self) -> APIConfig:
        """LLM配置别名"""
        return self.api

    def get_api_headers(self) -> dict[str, str]:
        """获取API请求头"""
        return {
            "User-Agent": self.api.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def to_dict(self) -> dict[str, Any]:
        """转换为字典（隐藏敏感信息）"""
        config_dict = self.dict()

        # 隐藏敏感信息
        if config_dict.get("api", {}).get("openrouter_api_key"):
            config_dict["api"]["openrouter_api_key"] = "***"
        if config_dict.get("api", {}).get("dida_access_token"):
            config_dict["api"]["dida_access_token"] = "***"
        if config_dict.get("storage", {}).get("database_url"):
            config_dict["storage"]["database_url"] = "***"

        return config_dict


def load_config() -> AppConfig:
    """加载应用配置"""
    return AppConfig()

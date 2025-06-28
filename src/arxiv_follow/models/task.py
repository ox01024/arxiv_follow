"""
任务相关的数据模型

定义任务、任务类型、状态和优先级的数据结构。
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class TaskType(str, Enum):
    """任务类型"""

    DAILY_MONITOR = "daily_monitor"  # 每日监控任务
    WEEKLY_SUMMARY = "weekly_summary"  # 每周汇总任务
    TOPIC_SEARCH = "topic_search"  # 主题搜索任务
    PAPER_ANALYSIS = "paper_analysis"  # 论文分析任务
    TRANSLATION = "translation"  # 翻译任务
    NOTIFICATION = "notification"  # 通知任务
    DATA_EXPORT = "data_export"  # 数据导出任务
    MAINTENANCE = "maintenance"  # 维护任务


class TaskStatus(str, Enum):
    """任务状态"""

    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 执行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消
    PAUSED = "paused"  # 暂停


class TaskPriority(str, Enum):
    """任务优先级"""

    LOW = "low"  # 低优先级
    NORMAL = "normal"  # 普通优先级
    HIGH = "high"  # 高优先级
    URGENT = "urgent"  # 紧急


class TaskResult(BaseModel):
    """任务执行结果"""

    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="结果消息")

    # 统计信息
    items_processed: int = Field(default=0, description="处理项目数")
    items_successful: int = Field(default=0, description="成功项目数")
    items_failed: int = Field(default=0, description="失败项目数")

    # 详细数据
    data: dict[str, Any] = Field(default_factory=dict, description="详细结果数据")
    errors: list[str] = Field(default_factory=list, description="错误列表")
    warnings: list[str] = Field(default_factory=list, description="警告列表")

    # 性能指标
    execution_time_seconds: float = Field(default=0, description="执行时间(秒)")
    memory_usage_mb: float | None = Field(None, description="内存使用量(MB)")

    # 输出文件
    output_files: list[str] = Field(default_factory=list, description="输出文件路径")

    @property
    def success_rate(self) -> float:
        """计算成功率"""
        if self.items_processed == 0:
            return 0.0
        return self.items_successful / self.items_processed


class TaskSchedule(BaseModel):
    """任务调度配置"""

    # 调度类型
    is_recurring: bool = Field(default=False, description="是否循环任务")
    cron_expression: str | None = Field(None, description="Cron表达式")

    # 时间配置
    scheduled_time: datetime | None = Field(None, description="预定执行时间")
    next_run_time: datetime | None = Field(None, description="下次执行时间")

    # 重试配置
    max_retries: int = Field(default=3, ge=0, description="最大重试次数")
    retry_delay_seconds: int = Field(default=60, ge=0, description="重试延迟(秒)")

    # 超时配置
    timeout_seconds: int | None = Field(None, ge=1, description="超时时间(秒)")

    @validator("cron_expression")
    def validate_cron_expression(cls, v: str | None) -> str | None:
        """验证Cron表达式格式"""
        if v is None:
            return v

        # 简单的Cron表达式验证（5或6个字段）
        parts = v.strip().split()
        if len(parts) not in [5, 6]:
            raise ValueError("Cron expression must have 5 or 6 fields")

        return v


class Task(BaseModel):
    """任务模型"""

    # 基础信息
    task_id: str = Field(..., description="任务唯一ID")
    task_type: TaskType = Field(..., description="任务类型")
    title: str = Field(..., description="任务标题")
    description: str | None = Field(None, description="任务描述")

    # 状态信息
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    priority: TaskPriority = Field(
        default=TaskPriority.NORMAL, description="任务优先级"
    )
    progress: float = Field(default=0.0, ge=0, le=100, description="完成进度(%)")

    # 任务配置
    parameters: dict[str, Any] = Field(default_factory=dict, description="任务参数")
    schedule: TaskSchedule | None = Field(None, description="调度配置")

    # 执行信息
    created_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    started_time: datetime | None = Field(None, description="开始时间")
    completed_time: datetime | None = Field(None, description="完成时间")
    last_updated: datetime = Field(
        default_factory=datetime.now, description="最后更新时间"
    )

    # 执行结果
    result: TaskResult | None = Field(None, description="执行结果")

    # 重试信息
    retry_count: int = Field(default=0, ge=0, description="重试次数")
    last_error: str | None = Field(None, description="最后错误信息")

    # 依赖关系
    depends_on: list[str] = Field(default_factory=list, description="依赖的任务ID")
    blocks: list[str] = Field(default_factory=list, description="阻塞的任务ID")

    # 元信息
    created_by: str | None = Field(None, description="创建者")
    assigned_to: str | None = Field(None, description="分配给")
    tags: list[str] = Field(default_factory=list, description="标签")

    @validator("task_id")
    def validate_task_id(cls, v: str) -> str:
        """验证任务ID格式"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Task ID cannot be empty")
        return v.strip()

    @validator("title")
    def validate_title(cls, v: str) -> str:
        """验证任务标题"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        return v.strip()

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self.status == TaskStatus.RUNNING

    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status == TaskStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """是否失败"""
        return self.status == TaskStatus.FAILED

    @property
    def can_run(self) -> bool:
        """是否可以运行"""
        return self.status in [TaskStatus.PENDING, TaskStatus.PAUSED]

    @property
    def duration_seconds(self) -> float | None:
        """获取执行时长(秒)"""
        if not self.started_time:
            return None

        end_time = self.completed_time or datetime.now()
        return (end_time - self.started_time).total_seconds()

    def start(self) -> None:
        """开始任务"""
        if not self.can_run:
            raise ValueError(
                f"Task {self.task_id} cannot be started (status: {self.status})"
            )

        self.status = TaskStatus.RUNNING
        self.started_time = datetime.now()
        self.last_updated = datetime.now()
        self.progress = 0.0

    def complete(self, result: TaskResult) -> None:
        """完成任务"""
        self.status = TaskStatus.COMPLETED
        self.completed_time = datetime.now()
        self.last_updated = datetime.now()
        self.progress = 100.0
        self.result = result

    def fail(self, error_message: str) -> None:
        """任务失败"""
        self.status = TaskStatus.FAILED
        self.completed_time = datetime.now()
        self.last_updated = datetime.now()
        self.last_error = error_message

        # 创建失败结果
        self.result = TaskResult(
            success=False, message=error_message, errors=[error_message]
        )

    def cancel(self) -> None:
        """取消任务"""
        if self.status == TaskStatus.RUNNING:
            self.status = TaskStatus.CANCELLED
            self.completed_time = datetime.now()
            self.last_updated = datetime.now()

    def pause(self) -> None:
        """暂停任务"""
        if self.status == TaskStatus.RUNNING:
            self.status = TaskStatus.PAUSED
            self.last_updated = datetime.now()

    def resume(self) -> None:
        """恢复任务"""
        if self.status == TaskStatus.PAUSED:
            self.status = TaskStatus.RUNNING
            self.last_updated = datetime.now()

    def update_progress(self, progress: float, message: str | None = None) -> None:
        """更新进度"""
        self.progress = max(0.0, min(100.0, progress))
        self.last_updated = datetime.now()

        if message and self.result:
            self.result.message = message

    def can_retry(self) -> bool:
        """是否可以重试"""
        if not self.schedule:
            return False

        return (
            self.status == TaskStatus.FAILED
            and self.retry_count < self.schedule.max_retries
        )

    def increment_retry(self) -> None:
        """增加重试次数"""
        self.retry_count += 1
        self.status = TaskStatus.PENDING
        self.last_updated = datetime.now()

        # 清除之前的执行信息
        self.started_time = None
        self.completed_time = None
        self.progress = 0.0

    def get_estimated_completion_time(self) -> datetime | None:
        """获取预计完成时间"""
        if not self.started_time or self.progress <= 0:
            return None

        elapsed = (datetime.now() - self.started_time).total_seconds()
        estimated_total = elapsed * (100.0 / self.progress)

        return self.started_time + datetime.timedelta(seconds=estimated_total)

    def to_summary(self) -> dict[str, Any]:
        """转换为摘要信息"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "title": self.title,
            "status": self.status,
            "priority": self.priority,
            "progress": self.progress,
            "created_time": self.created_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "success": self.result.success if self.result else None,
        }

    class Config:
        """Pydantic配置"""

        json_encoders = {datetime: lambda v: v.isoformat()}
        use_enum_values = True

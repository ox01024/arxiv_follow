"""
配置文件 - 存储系统配置参数
"""

from .models import get_translation_config, get_analysis_config

# Google Sheets TSV 导出链接
RESEARCHERS_TSV_URL = "https://docs.google.com/spreadsheets/d/1itjnV2U-Eh0F1T0LIGuLjzIhgL9f_OD8tbkMUG-Onic/export?format=tsv&id=1itjnV2U-Eh0F1T0LIGuLjzIhgL9f_OD8tbkMUG-Onic&gid=0"

# 默认搜索主题
DEFAULT_TOPICS = ["cs.AI", "cs.CR"]

# HTTP请求超时时间（秒）
REQUEST_TIMEOUT = 30.0

# 论文显示限制
DISPLAY_LIMIT = 10

# 日期回退默认天数
DEFAULT_DAYS_BACK = 3

# 搜索结果保存目录
REPORTS_DIR = "reports"

# 滴答清单API配置
DIDA_API_CONFIG = {
    # 是否启用滴答清单集成
    "enabled": True,
    # API基础URL
    "base_url": "https://api.dida365.com/open/v1",
    # 默认项目ID（收集箱）
    "default_project_id": "inbox",
    # 任务标签前缀
    "tag_prefix": "arxiv",
    # 任务优先级映射
    "priority_mapping": {
        "no_papers": 0,  # 无论文时优先级
        "has_papers": 1,  # 有论文时优先级
        "many_papers": 2,  # 论文较多时优先级（>=10篇）
    },
    # 论文数量阈值
    "many_papers_threshold": 10,
    # 是否启用双语翻译
    "enable_bilingual": True,
}

# LLM翻译服务配置 - 使用统一的模型配置
TRANSLATION_CONFIG = get_translation_config()

# 论文分析配置 - 使用统一的模型配置
PAPER_ANALYSIS_CONFIG = get_analysis_config()

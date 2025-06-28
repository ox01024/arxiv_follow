"""
配置文件 - 存储系统配置参数
"""

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
        "no_papers": 0,    # 无论文时优先级
        "has_papers": 1,   # 有论文时优先级
        "many_papers": 2   # 论文较多时优先级（>=10篇）
    },
    
    # 论文数量阈值
    "many_papers_threshold": 10,
    
    # 是否启用双语翻译
    "enable_bilingual": True
}

# LLM翻译服务配置
TRANSLATION_CONFIG = {
    # 是否启用翻译功能
    "enabled": True,
    
    # OpenRouter API配置
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "google/gemini-2.0-flash-lite-001",
        "max_tokens": 2000,
        "temperature": 0.3,
        "timeout": 60.0
    },
    
    # 默认翻译设置
    "default_settings": {
        "source_lang": "zh",       # 源语言
        "target_lang": "en",       # 目标语言
        "bilingual_format": True,  # 是否生成双语格式
        "preserve_emojis": True,   # 保持emoji表情
        "preserve_format": True    # 保持格式
    },
    
    # 降级策略
    "fallback": {
        "on_error": "original",    # 错误时返回原始内容
        "retry_attempts": 2,       # 重试次数
        "timeout_handling": "skip" # 超时处理：skip/retry/original
    }
}

# 论文分析配置
PAPER_ANALYSIS_CONFIG = {
    # 功能开关
    "enable_analysis": False,      # 是否启用论文分析功能
    "enable_content_collection": False,  # 是否启用内容采集
    
    # 分析模式
    "analysis_mode": "comprehensive",  # 分析模式: significance, technical, comprehensive
    "max_papers_per_batch": 5,        # 每批最多分析的论文数量
    "collection_delay": 1.0,          # 采集请求间隔(秒)
    
    # LLM分析配置
    "llm_config": {
        "model": "google/gemini-2.0-flash-lite-001",
        "temperature": 0.3,
        "max_tokens": 2000,
        "timeout": 60,
    },
    
    # 内容采集配置  
    "collection_config": {
        "try_html_version": True,      # 尝试获取HTML版本
        "include_sections": True,      # 包含章节信息
        "max_content_length": 10000,   # 最大内容长度
        "user_agent": "ArXiv-Follow-Collector/1.0"
    },
    
    # 报告生成配置
    "report_config": {
        "include_technical_analysis": True,   # 包含技术分析
        "include_significance_analysis": True, # 包含重要性分析
        "generate_daily_summary": True,       # 生成每日总结
        "max_summary_papers": 10,             # 总结中包含的最大论文数
    }
} 
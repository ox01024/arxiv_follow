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
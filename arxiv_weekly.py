#!/usr/bin/env python3
"""
每周研究者动态汇总脚本 - 兼容性包装器
这个脚本保持向后兼容，同时使用新的项目结构
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from arxiv_follow.cli.weekly import main

if __name__ == "__main__":
    main() 
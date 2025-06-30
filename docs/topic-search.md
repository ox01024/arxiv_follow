# 🎯 主题搜索专题指南

## 🚀 功能概述

主题搜索功能允许基于 arXiv 研究领域分类搜索最新论文，支持多主题组合搜索和智能日期回退策略，完美解决了传统搜索中日期范围过严导致无结果的问题。

## 🔧 核心特性

### 🧠 智能日期回退策略
系统会自动尝试多种搜索策略，确保总能找到相关论文：

1. **精确日期范围** - 例如：2025-01-13 到 2025-01-15 (3天)
2. **扩展到7天** - 例如：2025-01-08 到 2025-01-15 (7天)
3. **扩展到30天** - 例如：2024-12-16 到 2025-01-15 (30天)
4. **不限日期** - 获取最新50篇论文

### 🎨 多主题组合搜索
支持多个研究领域的组合搜索：
- **AND 逻辑** - 论文必须同时属于所有指定主题
- **智能解析** - 自动处理主题格式和验证
- **结果优化** - 过滤和排序搜索结果

## 🚀 使用方法

### 基础搜索

```bash
# 默认搜索 (使用配置的默认主题)
arxiv-follow topics "cs.AI,cs.CR"

# 查看最近AI论文
arxiv-follow topics "cs.AI" --days 3
```

### 自定义主题搜索

```bash
# AI + 机器学习
arxiv-follow topics "cs.AI,cs.LG"

# 安全 + 网络
arxiv-follow topics "cs.CR,cs.NI"

# AI + 计算机视觉
arxiv-follow topics "cs.AI,cs.CV"

# 数据库 + 信息检索
arxiv-follow topics "cs.DB,cs.IR"
```

### 高级参数

```bash
# 指定搜索天数和结果数量
arxiv-follow topics "cs.AI,cs.LG" --days 7 --max 50

# 导出搜索结果
arxiv-follow topics "cs.AI,cs.LG" --days 14 --output ai_ml_papers.json

# 大规模数据获取
arxiv-follow topics "cs.AI,cs.CR" --days 30 --max 200
```

## 🎨 热门主题组合

### 人工智能相关

| 组合 | 描述 | 应用场景 |
|------|------|----------|
| `cs.AI,cs.LG` | AI + 机器学习 | 基础AI研究、算法创新 |
| `cs.AI,cs.CV` | AI + 计算机视觉 | 图像识别、视觉AI |
| `cs.AI,cs.CL` | AI + 计算语言学 | 自然语言处理、LLM |
| `cs.AI,cs.RO` | AI + 机器人学 | 智能机器人、自动化 |
| `cs.AI,cs.HC` | AI + 人机交互 | AI界面、用户体验 |

### 网络安全相关

| 组合 | 描述 | 应用场景 |
|------|------|----------|
| `cs.CR,cs.NI` | 安全 + 网络 | 网络安全、通信协议 |
| `cs.CR,cs.AI` | 安全 + AI | AI安全、对抗攻击 |
| `cs.CR,cs.SY` | 安全 + 系统 | 系统安全、漏洞分析 |
| `cs.CR,cs.DC` | 安全 + 分布式 | 区块链、分布式安全 |

### 系统与架构

| 组合 | 描述 | 应用场景 |
|------|------|----------|
| `cs.DC,cs.OS` | 分布式 + 操作系统 | 云计算、容器技术 |
| `cs.DB,cs.IR` | 数据库 + 信息检索 | 搜索引擎、数据挖掘 |
| `cs.SE,cs.PL` | 软件工程 + 编程语言 | 开发工具、语言设计 |
| `cs.DS,cs.GT` | 数据结构 + 博弈论 | 算法优化、理论分析 |

### 跨学科组合

| 组合 | 描述 | 应用场景 |
|------|------|----------|
| `cs.LG,stat.ML` | 机器学习 + 统计ML | 统计学习理论 |
| `cs.AI,q-bio.NC` | AI + 神经计算 | 神经科学、脑机接口 |
| `cs.CV,eess.IV` | 计算机视觉 + 图像处理 | 医学影像、信号处理 |

## 📊 输出格式说明

### 控制台输出

```
🔍 主题搜索结果
🏷️  搜索主题: cs.AI AND cs.CR  
⏰ 搜索时间: 2025-01-15 13:29:09

📋 搜索策略尝试记录:
  1. ✅ 精确日期范围 (2025-01-13 到 2025-01-15): 6 篇论文

🎯 使用策略: 精确日期范围 (2025-01-13 到 2025-01-15)
📊 显示前 6 篇论文 (总计 6 篇)

------------------------------------------------------------
📄 1. AI-Powered Cybersecurity Framework for Zero-Trust Architecture
🆔 arXiv ID: 2501.12345
👥 作者: John Smith, Jane Doe, Bob Wilson 等 5 位作者
🌐 链接: https://arxiv.org/abs/2501.12345

📄 2. Deep Learning Approaches for Malware Detection in IoT Environments  
🆔 arXiv ID: 2501.12346
👥 作者: Alice Chen, David Kim 等 3 位作者
🌐 链接: https://arxiv.org/abs/2501.12346
```

### CI模式输出 (GitHub Actions)

```
🔍 主题搜索 - cs.AI AND cs.CR
📊 找到 6 篇论文 (使用策略: 精确日期范围)
📅 日期范围: 2025-01-13 到 2025-01-15
⏰ 执行时间: 2025-01-15 13:29:09
```

### JSON报告格式

```json
{
    "report_type": "topic",
    "search_topics": ["cs.AI", "cs.CR"],
    "search_query": "cat:cs.AI AND cat:cs.CR",
    "execution_time": "2025-01-15T13:29:09",
    "search_strategy_used": "exact_date_range",
    "date_range": {
        "from": "2025-01-13",
        "to": "2025-01-15"
    },
    "papers": [
        {
            "title": "AI-Powered Cybersecurity Framework...",
            "arxiv_id": "2501.12345",
            "authors": ["John Smith", "Jane Doe", "Bob Wilson"],
            "categories": ["cs.AI", "cs.CR", "cs.LG"],
            "abstract": "This paper presents a novel framework...",
            "url": "https://arxiv.org/abs/2501.12345",
            "submitted_date": "2025-01-15T10:30:00Z"
        }
    ],
    "search_attempts": [
        {
            "strategy": "exact_date_range",
            "date_from": "2025-01-13",
            "date_to": "2025-01-15", 
            "result_count": 6,
            "success": true,
            "query_used": "cat:cs.AI AND cat:cs.CR AND submittedDate:[20250113 TO 20250115]"
        }
    ],
    "summary": {
        "total_papers": 6,
        "strategies_tried": 1,
        "final_strategy": "exact_date_range",
        "average_authors_per_paper": 3.2,
        "categories_distribution": {
            "cs.AI": 6,
            "cs.CR": 6,
            "cs.LG": 2
        }
    }
}
```

## 🔍 arXiv 分类系统

### 计算机科学 (cs)

#### 核心领域
- `cs.AI` - Artificial Intelligence (人工智能)
- `cs.LG` - Machine Learning (机器学习)
- `cs.CV` - Computer Vision and Pattern Recognition (计算机视觉)
- `cs.CL` - Computation and Language (计算语言学)
- `cs.CR` - Cryptography and Security (密码学与安全)

#### 系统与架构
- `cs.DC` - Distributed, Parallel, and Cluster Computing (分布式计算)
- `cs.OS` - Operating Systems (操作系统)
- `cs.NI` - Networking and Internet Architecture (网络架构)
- `cs.SE` - Software Engineering (软件工程)
- `cs.SY` - Systems and Control (系统与控制)

#### 理论与算法
- `cs.DS` - Data Structures and Algorithms (数据结构与算法)
- `cs.CC` - Computational Complexity (计算复杂性)
- `cs.GT` - Computer Science and Game Theory (博弈论)
- `cs.FL` - Formal Languages and Automata Theory (形式语言)

#### 应用领域
- `cs.DB` - Databases (数据库)
- `cs.IR` - Information Retrieval (信息检索)
- `cs.HC` - Human-Computer Interaction (人机交互)
- `cs.RO` - Robotics (机器人学)
- `cs.GR` - Graphics (图形学)

### 相关交叉领域

#### 统计与数学
- `stat.ML` - Machine Learning (Statistics)
- `math.OC` - Optimization and Control
- `math.ST` - Statistics Theory

#### 电子工程
- `eess.IV` - Image and Video Processing
- `eess.SP` - Signal Processing
- `eess.SY` - Systems and Control

#### 生物信息
- `q-bio.NC` - Neurons and Cognition
- `q-bio.QM` - Quantitative Methods

## 🧠 搜索策略详解

### 智能回退逻辑

```python
# 搜索策略优先级
strategies = [
    {
        "name": "exact_date_range",
        "days": 3,
        "description": "精确日期范围"
    },
    {
        "name": "week_range", 
        "days": 7,
        "description": "一周范围"
    },
    {
        "name": "month_range",
        "days": 30, 
        "description": "一月范围"
    },
    {
        "name": "no_date_filter",
        "days": None,
        "description": "不限日期"
    }
]
```

### 查询构建

系统会根据输入自动构建 arXiv 查询：

```python
# 单主题
"cat:cs.AI"

# 多主题组合
"cat:cs.AI AND cat:cs.CR" 

# 带日期范围
"cat:cs.AI AND cat:cs.CR AND submittedDate:[20250113 TO 20250115]"

# 不限日期但限制数量
"cat:cs.AI AND cat:cs.CR"  # 最多返回50篇
```

### 结果处理

1. **去重** - 基于 arXiv ID 去除重复论文
2. **排序** - 按提交日期降序排列
3. **过滤** - 确保论文包含所有指定主题
4. **格式化** - 统一输出格式

## 🎯 实际应用场景

### 学术研究
```bash
# 跟踪AI安全研究进展
uv run python topic_papers.py "cs.AI,cs.CR"

# 关注联邦学习最新论文  
uv run python topic_papers.py "cs.LG,cs.DC"

# 监控计算机视觉突破
uv run python topic_papers.py "cs.CV,cs.AI"
```

### 技术调研
```bash
# 区块链技术研究
uv run python topic_papers.py "cs.CR,cs.DC" 

# 自然语言处理进展
uv run python topic_papers.py "cs.CL,cs.AI"

# 量子计算发展
uv run python topic_papers.py "quant-ph,cs.CC"
```

### 会议准备
```bash
# NeurIPS 相关论文
uv run python topic_papers.py "cs.LG,cs.AI,stat.ML" --days 30

# USENIX Security 相关
uv run python topic_papers.py "cs.CR,cs.SY,cs.OS" --days 14

# SIGMOD 数据库会议
uv run python topic_papers.py "cs.DB,cs.IR" --days 21
```

## 🔧 高级配置

### 自定义搜索参数

在 `config.py` 中配置：

```python
# 主题搜索配置
TOPIC_SEARCH_CONFIG = {
    # 默认搜索主题
    "default_topics": ["cs.AI", "cs.CR"],
    
    # 日期回退策略
    "fallback_strategies": [
        {"name": "exact_date_range", "days": 3},
        {"name": "week_range", "days": 7}, 
        {"name": "month_range", "days": 30},
        {"name": "no_date_filter", "days": None}
    ],
    
    # 最大论文数量
    "max_papers": 50,
    
    # 搜索超时时间
    "search_timeout": 30,
    
    # 重试次数
    "max_retries": 3
}
```

### 输出定制

```python
# 输出格式配置
OUTPUT_CONFIG = {
    # 控制台显示论文数量
    "console_display_limit": 10,
    
    # 是否显示摘要
    "show_abstracts": False,
    
    # 是否显示搜索策略
    "show_search_strategy": True,
    
    # CI模式简化输出
    "ci_mode_minimal": True
}
```

## 💡 使用技巧

### 1. 主题选择策略
- **宽泛搜索** - 使用核心主题如 `cs.AI`
- **精确定位** - 组合相关主题如 `cs.AI,cs.CR`
- **交叉领域** - 探索跨学科组合

### 2. 时间范围优化
- **实时监控** - 使用默认日期范围
- **全面调研** - 增加搜索天数
- **定期追踪** - 设置定时执行

### 3. 结果分析
- **趋势识别** - 关注论文数量变化
- **热点发现** - 分析高频关键词
- **作者网络** - 跟踪活跃研究者

### 4. 组合策略
- **基础+应用** - 如 `cs.LG,cs.CV` (理论+应用)
- **方法+领域** - 如 `cs.AI,cs.HC` (方法+应用场景)
- **多角度** - 如 `cs.CR,cs.AI,cs.SY` (多维度分析)

## 🚨 故障排除

### 常见问题

**Q: 为什么搜索结果为空？**
A: 系统会自动使用智能回退策略。如果所有策略都无结果，可能是主题组合过于具体，建议使用更通用的主题。

**Q: 如何获得更多结果？**  
A: 
1. 减少主题组合数量
2. 增加搜索时间范围
3. 使用更通用的主题分类

**Q: 搜索速度慢怎么办？**
A:
1. 检查网络连接
2. 减少并发请求
3. 增加超时时间设置

**Q: JSON报告格式异常？**
A:
1. 检查磁盘空间
2. 确认文件权限
3. 验证UTF-8编码

### 调试模式

启用调试输出：

```bash
# 设置调试环境变量
export DEBUG=true

# 运行搜索并查看详细日志
uv run python topic_papers.py "cs.AI,cs.CR"
```

### 性能监控

```bash
# 测试网络连接
uv run python test_ci.py

# 验证配置有效性
uv run python -c "from config import *; print('配置加载成功')"

# 检查依赖包
uv list
``` 
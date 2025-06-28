# ArXiv 研究者论文监控系统

这是一个自动化监控研究者在 arXiv 上发布论文的系统，支持每日和周报两种监控模式，以及基于主题的智能搜索。

## 🚀 特别挑战

> **"不写一行代码，构建一个项目，改掉喜欢自己写代码的坏毛病"**

这个项目是一个有趣的实验——完全通过与 AI 助手对话的方式构建，作者没有亲自编写任何代码。完整的开发对话记录保存在 `vibe_coding/` 文件夹中，对想了解 AI 协作开发流程的开发者可能很有价值。

## ✨ 功能特性

- 📄 **每日监控** - 自动检测研究者当天发布的新论文
- 📚 **周报汇总** - 生成最近一周的论文报告  
- 🎯 **主题搜索** - 基于研究领域的智能论文搜索
- 🧠 **智能日期回退** - 自动处理日期范围搜索无结果的情况
- 🤖 **GitHub Actions自动化** - 定时执行，中国时区适配
- 📝 **滴答清单集成** - 自动创建任务到你的滴答清单

## 🚀 快速开始

### 环境准备
```bash
# 安装 UV 包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

### 立即体验
```bash
# 每日论文监控
uv run python daily_papers.py

# 周报汇总
uv run python weekly_papers.py

# 主题搜索（AI + 安全）
uv run python topic_papers.py

# 自定义主题搜索
uv run python topic_papers.py "cs.AI,cs.LG"  # AI + 机器学习

# 查看演示
uv run python demo_search.py
```

## 📋 输出示例

```
🔍 每日论文监控 - 获取研究者当天发布的论文
时间: 2025-06-28 09:00:00

✅ 找到 1 篇新论文!
👨‍🔬 Minghao Shao (1 篇论文):
📄 QHackBench: Benchmarking Large Language Models...
🔗 arXiv ID: 2506.20008
🌐 链接: https://arxiv.org/abs/2506.20008
```

## 🤖 自动化运行

系统已配置 GitHub Actions 自动化工作流：

- **每日监控** - 每天 09:00/12:00/22:00 (中国时间)
- **周报汇总** - 每周一 09:00 (中国时间)  
- **主题搜索** - 每天 09:00 (中国时间)

支持手动触发，可自定义搜索主题和时间范围。

## 📚 完整文档中心

### 🎯 按用户类型导航

#### 🆕 新用户入门
```
1️⃣ 开始使用 → 上面的"🚀 快速开始"
2️⃣ 深入了解 → 📖 详细使用指南
3️⃣ 高级功能 → 🎯 主题搜索专题
```

#### 👨‍💻 开发者部署
```
1️⃣ 本地测试 → 📖 详细使用指南
2️⃣ 自动化部署 → 🚀 部署指南
3️⃣ 任务管理 → 📝 滴答清单集成
```

#### 🔬 研究者定制
```
1️⃣ 配置研究者 → 📖 详细使用指南 > 配置管理
2️⃣ 主题订阅 → 🎯 主题搜索专题
3️⃣ 自动化监控 → 🚀 部署指南
```

### 📖 核心文档

| 文档 | 内容概要 | 适合人群 | 预计阅读时间 |
|------|----------|----------|--------------|
| [📖 详细使用指南](docs/usage-guide.md) | 完整功能说明、配置管理、搜索技巧、故障排除 | 所有用户 | 15-20分钟 |
| [🎯 主题搜索专题](docs/topic-search.md) | arXiv分类、智能搜索、热门组合、高级技巧 | 研究者/高级用户 | 10-15分钟 |
| [📝 滴答清单集成](docs/dida-integration.md) | 5分钟快速配置、API详解、故障排除 | 想要任务管理的用户 | 8-12分钟 |
| [🚀 部署指南](docs/deployment.md) | GitHub Actions配置、自动化部署、监控维护 | 开发者/运维人员 | 12-18分钟 |

### 🔍 快速查找

#### 📋 常见任务指南
- **配置研究者监控** → [使用指南 > 研究者列表管理](docs/usage-guide.md#研究者列表管理)
- **设置主题订阅** → [主题搜索专题 > 使用方法](docs/topic-search.md#🚀-使用方法)
- **启用自动化** → [部署指南 > 配置步骤](docs/deployment.md#🔧-配置步骤)
- **集成滴答清单** → [滴答清单集成 > 快速配置](docs/dida-integration.md#🚀-5分钟快速配置)
- **自定义时间** → [部署指南 > 时间配置](docs/deployment.md#📅-时间配置详解)

#### 🆘 问题求解
- **搜索无结果** → [使用指南 > 常见问题](docs/usage-guide.md#🚨-常见问题)
- **网络连接问题** → [使用指南 > 网络连接问题](docs/usage-guide.md#网络连接问题)
- **滴答清单配置** → [滴答清单集成 > 故障排除](docs/dida-integration.md#🔍-故障排除)
- **GitHub Actions失败** → [部署指南 > 监控调试](docs/deployment.md#🔍-监控和调试)

### 📚 完整文档索引
> 📁 **[查看所有文档](docs/README.md)** - 包含完整的文档目录和遗留版本

## 🔧 配置说明

### 研究者列表
研究者列表存储在 [Google Sheets](https://docs.google.com/spreadsheets/d/1itjnV2U-Eh0F1T0LIGuLjzIhgL9f_OD8tbkMUG-Onic) 中，TSV格式，每行一个研究者姓名。

### 滴答清单集成
1. 获取 Access Token：使用 [在线工具](https://dida-auth.vercel.app/) 
2. 配置 GitHub Secrets：`DIDA_ACCESS_TOKEN`
3. 测试连接：`uv run python test_dida_integration.py`

## 🛠️ 项目结构

```
arxiv_follow/
├── daily_papers.py          # 每日监控脚本
├── weekly_papers.py         # 周报生成脚本  
├── topic_papers.py          # 主题搜索脚本
├── follow_researchers.py    # 研究者跟踪脚本
├── dida_integration.py      # 滴答清单集成
├── demo_search.py           # 演示脚本
├── config.py                # 配置文件
├── test_*.py                # 测试脚本
├── docs/                    # 详细文档
└── .github/workflows/       # GitHub Actions配置
```

## 📊 监控范围

- **研究领域** - 计算机科学 + 物理学各分支
- **搜索平台** - arXiv.org  
- **时间筛选** - 基于论文提交日期
- **智能特性** - 自动日期回退，确保搜索结果

## 🎯 适用场景

- 科研人员跟踪同行最新研究
- 研究团队定期论文调研
- 特定领域的论文监控订阅
- 学术会议前的论文收集

---

**⭐ 如果这个项目对你有帮助，请给个Star支持！**
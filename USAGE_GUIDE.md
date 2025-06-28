# 🎯 主题论文搜索使用指南

## 🚀 快速开始

### 本地使用

```bash
# 基础搜索 - 默认 cs.AI + cs.CR
uv run python topic_papers.py

# 自定义主题搜索
uv run python topic_papers.py "cs.AI,cs.LG"     # AI + 机器学习
uv run python topic_papers.py "cs.CR,cs.NI"     # 安全 + 网络  
uv run python topic_papers.py "cs.AI,cs.CV"     # AI + 计算机视觉
uv run python topic_papers.py "cs.DB,cs.IR"     # 数据库 + 信息检索

# 查看完整演示
uv run python demo_search.py
```

### GitHub Actions 自动化

#### 📅 每日自动订阅
- **时间**: 每天中国时间 09:00 自动运行
- **主题**: cs.AI AND cs.CR (人工智能 + 计算机安全)
- **结果**: 自动保存为 GitHub Actions artifacts

#### 🎯 手动触发（支持自定义）
1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "🎯 主题论文监控 - AI & Security"
3. 点击 "Run workflow" 
4. 自定义参数：
   - **搜索主题**: `cs.AI,cs.LG` 或 `cs.CR,cs.NI` 等
   - **搜索天数**: `3` 或 `7` 等

## 🎨 热门主题组合

| 组合 | 描述 | 命令 |
|------|------|------|
| `cs.AI,cs.CR` | AI + 网络安全 | `python topic_papers.py "cs.AI,cs.CR"` |
| `cs.AI,cs.LG` | AI + 机器学习 | `python topic_papers.py "cs.AI,cs.LG"` |
| `cs.AI,cs.CV` | AI + 计算机视觉 | `python topic_papers.py "cs.AI,cs.CV"` |
| `cs.AI,cs.CL` | AI + 计算语言学 | `python topic_papers.py "cs.AI,cs.CL"` |
| `cs.CR,cs.NI` | 安全 + 网络 | `python topic_papers.py "cs.CR,cs.NI"` |
| `cs.DB,cs.IR` | 数据库 + 信息检索 | `python topic_papers.py "cs.DB,cs.IR"` |
| `cs.DC,cs.DS` | 分布式计算 + 数据结构 | `python topic_papers.py "cs.DC,cs.DS"` |

## 🧠 智能特性

### 📅 智能日期回退
系统会自动尝试多种搜索策略：
1. **精确日期范围** (如 2025-06-27 到 2025-06-28)
2. **扩展到7天** (如 2025-06-21 到 2025-06-28) 
3. **扩展到30天** (如 2025-05-29 到 2025-06-28)
4. **不限日期** (获取最新50篇)

### 🔍 解决arXiv搜索痛点
- ✅ **问题**: 严格日期范围搜索经常返回"no results"
- ✅ **解决**: 智能回退到更宽松的日期范围
- ✅ **效果**: 确保总能找到相关论文

### 💾 结果保存
- **格式**: JSON格式，包含完整论文信息
- **位置**: `reports/topic_papers_YYYYMMDD_HHMMSS.json`
- **内容**: 标题、作者、摘要、arXiv ID、搜索策略等

## 📊 输出示例

```
🔍 主题搜索结果
🏷️  搜索主题: cs.AI AND cs.CR
⏰ 搜索时间: 2025-06-28 13:29:09

📋 搜索策略尝试记录:
  1. ✅ 精确日期范围 (2025-06-26 到 2025-06-28): 6 篇论文

🎯 使用策略: 精确日期范围 (2025-06-26 到 2025-06-28)
📊 显示前 6 篇论文 (总计 6 篇)

------------------------------------------------------------
📄 1. PhishKey: A Novel Centroid-Based Approach for Enhanced Phishing Detection...
🆔 arXiv ID: 2506.21106
👥 作者: Felipe Castaño, Eduardo Fidalgo, Enrique Alegre 等 6 位作者
🌐 链接: https://arxiv.org/abs/2506.21106
```

## 🔧 CI环境特性

当在GitHub Actions中运行时，脚本会自动：
- 🎯 切换到CI优化模式（减少不必要输出）
- 📊 显示简洁的搜索总结
- 💾 自动保存结果为artifacts
- ⏱️ 优化执行时间

## 💡 使用技巧

1. **定期监控**: 设置GitHub Actions每日自动运行
2. **主题组合**: 尝试不同的研究领域组合
3. **结果跟踪**: 下载artifacts查看历史搜索结果
4. **手动触发**: 在重要会议前手动触发获取最新论文
5. **时间调整**: 根据需要修改cron表达式调整运行时间

## 🆘 常见问题

**Q: 为什么有时候搜索没有结果？**
A: 系统会自动使用智能日期回退，通常都能找到结果。如果完全没有结果，可能是主题组合过于具体。

**Q: 如何修改搜索时间？**
A: 编辑 `.github/workflows/topic_papers.yml` 中的 cron 表达式。

**Q: 能搜索物理学论文吗？**
A: 当前主要针对计算机科学，但可以修改脚本支持物理学分类。

**Q: 结果保存在哪里？**
A: 本地运行保存在 `reports/` 目录，CI运行保存为GitHub Actions artifacts。 
# 滴答清单集成 - 快速开始

## 🚀 5分钟快速配置

### 1. 获取 Access Token
使用第三方工具（最简单）：
1. 访问 https://dida-auth.vercel.app/
2. 在滴答清单开发者页面创建应用
3. 按工具指示获取 Access Token

### 2. 配置到 GitHub Secrets
1. 进入你的 GitHub 仓库
2. `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. Name: `DIDA_ACCESS_TOKEN`
5. Secret: 粘贴你的 token
6. 保存

### 3. 测试配置
```bash
# 本地测试（可选）
export DIDA_ACCESS_TOKEN="your_token"
uv run python test_dida_integration.py
```

## ✅ 完成！

现在每次 GitHub Actions 运行时，都会自动在你的滴答清单中创建任务：

- 📄 **每日监控** → 每日论文发现汇总任务
- 📚 **周报汇总** → 每周论文统计任务  
- 🎯 **主题搜索** → 主题论文搜索结果任务

## 📋 任务内容示例

```
📄 每日论文监控 - 2025-01-15

🎉 今日发现 3 篇新论文！

📊 共发现 3 篇论文

📝 详细信息:
监控了 5 位研究者

📊 论文分布:
• 张三: 2 篇
  1. GPT-4在网络安全中的应用研究...
  2. 基于深度学习的恶意软件检测...
• 李四: 1 篇
  1. 联邦学习中的隐私保护机制...

⏰ 生成时间: 2025-01-15 09:00:15
🤖 由 ArXiv Follow 系统自动生成
```

## 🛠️ 自定义配置

编辑 `config.py` 中的 `DIDA_API_CONFIG` 来自定义：
- 任务优先级规则
- 标签前缀
- 论文数量阈值

## 🔧 故障排除

**问题**: 任务创建失败  
**解决**: 检查 token 是否正确，重新获取新的 token

**问题**: 没有看到任务  
**解决**: 确认 GitHub Secrets 配置正确，token 名称为 `DIDA_ACCESS_TOKEN`

## 📚 详细文档

完整配置指南：[DIDA_INTEGRATION_GUIDE.md](./DIDA_INTEGRATION_GUIDE.md) 
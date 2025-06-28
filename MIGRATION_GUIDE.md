# 项目结构重构迁移指南

## 🏗️ 新项目结构

为了更好地遵循Python项目最佳实践，我们重新组织了项目结构。

### 📁 新的目录结构

```
arxiv_follow/
├── src/arxiv_follow/          # 主包源代码
│   ├── core/                  # 核心业务逻辑
│   ├── services/              # 服务层
│   ├── integrations/          # 第三方集成
│   ├── cli/                   # 命令行工具
│   └── config/                # 配置模块
├── tests/                     # 测试文件
├── examples/                  # 示例代码
├── docs/                      # 文档
└── pyproject.toml            # 项目配置
```

## 🔄 主要变更

1. **源代码移到 src/ 布局**
2. **模块化设计**：按功能分组
3. **标准化项目配置**
4. **改进的测试结构**

## ✅ 向后兼容

- 根目录保留兼容性脚本 (arxiv_daily.py, arxiv_weekly.py, arxiv_topic.py)
- 原有使用方式继续有效
- 新增作为Python包的使用方式

## 🆕 新功能

- 支持 `pip install -e .` 安装
- 命令行工具：`arxiv-daily`, `arxiv-weekly`, `arxiv-topic`
- 可导入的模块组件
- 改进的测试和开发工具配置 
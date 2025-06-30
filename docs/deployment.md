# 🚀 部署指南

## 🎯 概述

本指南详细说明如何配置和部署 ArXiv Follow 系统的 GitHub Actions 自动化工作流，包括每日监控、周报汇总和主题搜索功能。

## 🏗️ GitHub Actions 工作流

### 工作流概览

系统包含三个主要的自动化工作流：

| 工作流 | 文件路径 | 执行时间 | 功能 |
|--------|----------|----------|------|
| 每日监控 | `.github/workflows/daily_papers.yml` | 每天 09:00/12:00/22:00 (中国时间) | 监控研究者论文发布 |
| 周报汇总 | `.github/workflows/weekly_papers.yml` | 每周一 09:00 (中国时间) | 生成周度论文报告 |
| 主题搜索 | `.github/workflows/topic_papers.yml` | 每天 09:00 (中国时间) | 基于主题搜索论文 |

### 每日监控工作流

#### 配置文件: `.github/workflows/daily_papers.yml`

```yaml
name: 📄 每日论文监控

on:
  schedule:
    # 每天 01:00, 04:00, 14:00 UTC (中国时间 09:00, 12:00, 22:00)
    - cron: '0 1 * * *'   # 09:00 中国时间
    - cron: '0 4 * * *'   # 12:00 中国时间  
    - cron: '0 14 * * *'  # 22:00 中国时间
  workflow_dispatch:  # 支持手动触发

jobs:
  daily-monitoring:
    runs-on: ubuntu-latest
    
    steps:
    - name: 检出代码
      uses: actions/checkout@v4
      
    - name: 设置 Python 环境
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        
    - name: 安装 UV
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
        
    - name: 安装依赖
      run: uv sync
      
    - name: 运行 CI 环境测试
      run: uv run python test_ci.py
      
    - name: 执行每日监控
      env:
        DIDA_ACCESS_TOKEN: ${{ secrets.DIDA_ACCESS_TOKEN }}
      run: uv run python daily_papers.py
      
    - name: 上传报告文件
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: daily-reports-${{ github.run_number }}
        path: reports/
        retention-days: 30
```

#### 特性说明
- **多时段执行**: 一天三次执行，确保及时发现新论文
- **中国时区**: 自动转换为中国时间执行
- **错误容错**: 即使部分步骤失败也会上传报告
- **报告保存**: 自动保存为 GitHub Actions artifacts

### 周报汇总工作流

#### 配置文件: `.github/workflows/weekly_papers.yml`

```yaml
name: 📚 周报论文汇总

on:
  schedule:
    # 每周一 01:00 UTC (中国时间 09:00)
    - cron: '0 1 * * 1'
  workflow_dispatch:

jobs:
  weekly-summary:
    runs-on: ubuntu-latest
    
    steps:
    - name: 检出代码
      uses: actions/checkout@v4
      
    - name: 设置 Python 环境
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        
    - name: 安装 UV
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
        
    - name: 安装依赖
      run: uv sync
      
    - name: 运行 CI 环境测试
      run: uv run python test_ci.py
      
    - name: 生成周报
      env:
        DIDA_ACCESS_TOKEN: ${{ secrets.DIDA_ACCESS_TOKEN }}
      run: uv run python weekly_papers.py
      
    - name: 上传报告文件
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: weekly-reports-${{ github.run_number }}
        path: reports/
        retention-days: 90
```

#### 特性说明
- **周度执行**: 每周一早上自动生成周报
- **长期保存**: 报告保存90天，便于历史分析
- **趋势分析**: 提供研究者活跃度和论文发布趋势

### 主题搜索工作流

#### 配置文件: `.github/workflows/topic_papers.yml`

```yaml
name: 🎯 主题论文监控 - AI & Security

on:
  schedule:
    # 每天 01:00 UTC (中国时间 09:00)
    - cron: '0 1 * * *'
  workflow_dispatch:
    inputs:
      topics:
        description: '搜索主题 (用逗号分隔，如: cs.AI,cs.LG)'
        required: false
        default: 'cs.AI,cs.CR'
        type: string
      days:
        description: '搜索天数 (如: 3, 7, 30)'
        required: false
        default: '3'
        type: string

jobs:
  topic-search:
    runs-on: ubuntu-latest
    
    steps:
    - name: 检出代码
      uses: actions/checkout@v4
      
    - name: 设置 Python 环境
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        
    - name: 安装 UV
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
        
    - name: 安装依赖
      run: uv sync
      
    - name: 运行 CI 环境测试
      run: uv run python test_ci.py
      
    - name: 执行主题搜索
      env:
        DIDA_ACCESS_TOKEN: ${{ secrets.DIDA_ACCESS_TOKEN }}
      run: |
        if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
          # 手动触发，使用自定义参数
          if [ -n "${{ github.event.inputs.days }}" ]; then
            uv run python topic_papers.py "${{ github.event.inputs.topics }}" --days ${{ github.event.inputs.days }} --ci-mode
          else
            uv run python topic_papers.py "${{ github.event.inputs.topics }}" --ci-mode
          fi
        else
          # 定时触发，使用默认参数
          uv run python topic_papers.py --ci-mode
        fi
        
    - name: 上传搜索结果
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: topic-search-results-${{ github.run_number }}
        path: reports/
        retention-days: 60
```

#### 特性说明
- **自定义参数**: 支持手动触发时自定义搜索主题和天数
- **CI模式**: 优化的输出格式，适合自动化环境
- **智能回退**: 自动使用日期回退策略确保搜索结果
- **灵活配置**: 可以通过 GitHub UI 自定义搜索参数

## 🔧 配置步骤

### 1. Fork 仓库

1. 访问项目 GitHub 页面
2. 点击右上角 "Fork" 按钮
3. 选择你的账户作为目标

### 2. 配置 Secrets

#### 必需的 Secrets

| Secret 名称 | 描述 | 是否必需 |
|------------|------|----------|
| `DIDA_ACCESS_TOKEN` | 滴答清单API访问令牌 | 可选 |

#### 配置步骤
1. 进入你的 Fork 仓库
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 添加相应的 Secret

### 3. 启用 GitHub Actions

1. 进入 `Actions` 标签页
2. 如果 Actions 被禁用，点击启用
3. 选择需要的工作流
4. 点击 "Enable workflow"

### 4. 验证部署

#### 检查工作流状态
```bash
# 克隆你的 Fork 仓库
git clone https://github.com/YOUR_USERNAME/arxiv_follow.git
cd arxiv_follow

# 检查工作流文件
ls -la .github/workflows/

# 验证配置文件语法
# 可以使用 GitHub Actions 的验证工具
```

#### 手动触发测试
1. 进入 `Actions` 标签页
2. 选择任一工作流
3. 点击 `Run workflow`
4. 观察执行结果

## 📅 时间配置详解

### Cron 表达式格式

```
# ┌───────────── 分钟 (0-59)
# │ ┌─────────── 小时 (0-23)
# │ │ ┌───────── 日 (1-31)
# │ │ │ ┌─────── 月 (1-12)
# │ │ │ │ ┌───── 星期 (0-6, 0=周日)
# │ │ │ │ │
# * * * * *
```

### 时区转换对照表

| UTC 时间 | 中国时间 (UTC+8) | 说明 |
|----------|------------------|------|
| 01:00 | 09:00 | 上班时间 |
| 04:00 | 12:00 | 午休时间 |
| 14:00 | 22:00 | 晚间时间 |

### 自定义时间配置

修改 `.github/workflows/*.yml` 文件中的 cron 表达式：

```yaml
# 例子：修改为每天早上6点和晚上6点执行
schedule:
  - cron: '0 22 * * *'  # 06:00 中国时间
  - cron: '0 10 * * *'  # 18:00 中国时间
```

### 常用时间配置模板

```yaml
# 每小时执行
- cron: '0 * * * *'

# 每天特定时间
- cron: '30 2 * * *'  # 每天 10:30 中国时间

# 工作日执行
- cron: '0 1 * * 1-5'  # 周一至周五 09:00 中国时间

# 每月第一天
- cron: '0 1 1 * *'  # 每月1号 09:00 中国时间
```

## 🔍 监控和调试

### 工作流状态监控

#### 通过 GitHub UI
1. 进入 `Actions` 标签页
2. 查看最近执行记录
3. 点击具体运行查看详细日志

#### 通过 GitHub CLI
```bash
# 安装 GitHub CLI
# https://cli.github.com/

# 查看工作流运行状态
gh run list

# 查看特定运行的日志
gh run view RUN_ID --log
```

### 常见问题诊断

#### 1. 工作流不执行
**可能原因**:
- 仓库非活跃状态（60天无活动）
- Cron 表达式错误
- Actions 被禁用

**解决方案**:
```bash
# 检查仓库活跃度
git log --oneline -10

# 验证 cron 表达式
# 使用在线工具: https://crontab.guru/

# 手动触发工作流验证
```

#### 2. 脚本执行失败
**可能原因**:
- 依赖安装失败
- 网络连接问题
- 环境变量配置错误

**解决方案**:
```bash
# 本地测试脚本
uv run python test_ci.py
uv run python daily_papers.py

# 检查依赖
uv list

# 验证网络连接
curl -I https://export.arxiv.org/
```

#### 3. Artifacts 上传失败
**可能原因**:
- 文件路径错误
- 权限问题
- 文件大小超限

**解决方案**:
```yaml
# 调试文件路径
- name: 列出文件
  run: |
    ls -la reports/
    find . -name "*.json" -type f

# 修复权限问题
- name: 修复权限
  run: chmod -R 755 reports/
```

### 性能监控

#### 执行时间统计
```bash
# 查看最近执行的平均时间
gh run list --limit 10 --json status,conclusion,createdAt,updatedAt
```

#### 资源使用监控
```yaml
# 在工作流中添加资源监控
- name: 系统资源监控
  run: |
    echo "磁盘使用:"
    df -h
    echo "内存使用:"
    free -h
    echo "CPU信息:"
    nproc
```

## 🔄 更新和维护

### 定期维护任务

#### 1. 更新依赖包
```bash
# 本地更新
uv lock --upgrade

# 提交更新
git add uv.lock
git commit -m "更新依赖包"
git push
```

#### 2. 清理旧的 Artifacts
- GitHub 自动清理超期的 artifacts
- 可在 Settings → Actions → General 中配置保留期

#### 3. 监控 API 限制
- arXiv API: 无严格限制，建议控制频率
- 滴答清单 API: 查看开发者控制台的使用量

### 版本升级

#### 升级工作流版本
```yaml
# 更新 Actions 版本
- uses: actions/checkout@v4      # 保持最新
- uses: actions/setup-python@v5  # 保持最新
- uses: actions/upload-artifact@v4  # 保持最新
```

#### 升级 Python 版本
```yaml
# 修改 Python 版本
- name: 设置 Python 环境
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'  # 升级到新版本
```

### 备份和恢复

#### 配置备份
```bash
# 备份工作流配置
cp -r .github/workflows/ backup/workflows/

# 备份项目配置
cp config.py backup/
cp pyproject.toml backup/
```

#### 快速恢复
```bash
# 恢复配置
cp backup/workflows/* .github/workflows/
cp backup/config.py .
cp backup/pyproject.toml .

# 提交恢复
git add .
git commit -m "恢复配置"
git push
```

## 💡 最佳实践

### 1. 安全配置
- 使用 Secrets 存储敏感信息
- 定期轮换访问令牌
- 限制工作流权限

### 2. 性能优化
- 合理设置执行频率
- 使用缓存加速构建
- 控制并发执行数量

### 3. 可靠性保障
- 添加错误重试机制
- 设置超时限制
- 实现优雅降级

### 4. 监控告警
- 关注执行失败通知
- 定期检查执行日志
- 监控资源使用情况

## 🧪 开发和测试工作流

### 测试工作流 (`.github/workflows/tests.yml`)

**触发条件**：
- 推送到 `main` 或 `develop` 分支
- 针对 `main` 分支的Pull Request

**包含的任务**：

1. **代码质量检查** (`quality`)
   - Black 代码格式化检查
   - Ruff 代码质量检查
   - MyPy 类型检查（允许失败）

2. **基础测试** (`test-basic`)
   - 环境验证测试
   - 包导入测试
   - CLI命令测试
   - 系统连接测试

3. **单元测试** (`test-unit`)
   - 支持Python 3.11和3.12
   - 运行非集成测试
   - 生成覆盖率报告
   - 上传到Codecov

4. **集成测试** (`test-integration`)
   - 仅在PR时运行
   - 使用GitHub Secrets中的API密钥
   - 测试真实API连接

### 安全工作流 (`.github/workflows/security.yml`)

**包含的检查**：
- **依赖安全扫描** - Safety检查已知漏洞，Bandit安全代码分析
- **代码复杂度分析** - Radon复杂度检查，可维护性指数计算
- **覆盖率检查** - 要求最低70%覆盖率
- **许可证检查** - 扫描依赖许可证兼容性
- **SAST分析** - GitHub CodeQL安全扫描

## 🔧 本地开发设置

### 安装开发环境

```bash
# 安装开发依赖
uv sync --dev

# 安装pre-commit hooks
uv run pre-commit install

# 手动运行所有检查
uv run pre-commit run --all-files
```

### 本地测试

```bash
# 运行所有测试
uv run pytest

# 运行单元测试
uv run pytest -m "not integration and not slow"

# 运行集成测试（需要API密钥）
uv run pytest -m "integration"

# 生成覆盖率报告
uv run pytest --cov=src/arxiv_follow --cov-report=html
```

### 代码质量检查

```bash
# 格式化代码
uv run black src tests

# 检查代码质量
uv run ruff check src tests

# 类型检查
uv run mypy src

# 安全检查
uv run bandit -r src/
```

### 环境变量配置

在GitHub仓库的Settings → Secrets and variables → Actions中配置：

| 变量名 | 描述 | 用途 |
|--------|------|------|
| `OPEN_ROUTE_API_KEY` | OpenRouter API密钥 | AI分析功能测试 |
| `DIDA_ACCESS_TOKEN` | 滴答清单API令牌 | 滴答清单集成测试 |

### 分支策略

- **`main`**: 生产分支，每次推送触发完整测试
- **`develop`**: 开发分支，用于集成新功能
- **Feature分支**: 从`develop`分出，通过PR合并

### 发布流程

1. 确保所有测试通过
2. 更新版本号（`pyproject.toml`中的`version`）
3. 创建并推送版本标签：
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```
4. 在GitHub上创建Release
5. 自动触发发布工作流

---

**需要帮助？** 查看 [GitHub Actions 文档](https://docs.github.com/en/actions) 或提交 [Issue](https://github.com/your-repo/issues)。 
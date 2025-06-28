# CI/CD 系统说明

本项目使用现代化的GitHub Actions工作流进行持续集成和部署。

## 工作流概览

### 🧪 测试工作流 (`.github/workflows/tests.yml`)

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

5. **端到端测试** (`test-e2e`)
   - CLI功能完整测试
   - Python包接口测试

6. **性能测试** (`test-performance`)
   - 仅在主分支运行
   - 测试搜索性能和包导入时间

### 🔒 安全工作流 (`.github/workflows/security.yml`)

**触发条件**：
- 推送到 `main` 或 `develop` 分支
- 针对 `main` 分支的Pull Request
- 每周一次定时扫描

**包含的检查**：

1. **依赖安全扫描**
   - Safety检查已知漏洞
   - Bandit安全代码分析

2. **代码复杂度分析**
   - Radon复杂度检查
   - 可维护性指数计算

3. **覆盖率检查**
   - 要求最低70%覆盖率

4. **许可证检查**
   - 扫描依赖许可证兼容性

5. **SAST分析**
   - GitHub CodeQL安全扫描

6. **漏洞扫描**
   - Trivy容器和文件系统扫描

### 🚀 发布工作流 (`.github/workflows/release.yml`)

**触发条件**：
- 推送版本标签 (`v*`)
- 发布Release

**包含的步骤**：

1. **构建分发包**
   - 构建wheel和源码包
   - 验证包完整性

2. **跨平台测试**
   - Windows、macOS、Linux
   - Python 3.11和3.12

3. **发布到PyPI**
   - 使用可信发布者功能
   - 自动上传到PyPI

4. **GitHub Release**
   - 上传构建产物
   - 创建Release页面

5. **文档部署**
   - 构建并部署到GitHub Pages

## 本地开发设置

### 安装Pre-commit

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

## 环境变量配置

在GitHub仓库的Settings → Secrets and variables → Actions中配置：

| 变量名 | 描述 | 用途 |
|--------|------|------|
| `OPEN_ROUTE_API_KEY` | OpenRouter API密钥 | AI分析功能测试 |
| `DIDA_ACCESS_TOKEN` | 滴答清单API令牌 | 滴答清单集成测试 |

## 分支策略

- **`main`**: 生产分支，每次推送触发完整测试
- **`develop`**: 开发分支，用于集成新功能
- **Feature分支**: 从`develop`分出，通过PR合并

## 发布流程

1. 确保所有测试通过
2. 更新版本号（`pyproject.toml`中的`version`）
3. 创建并推送版本标签：
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```
4. 在GitHub上创建Release
5. 自动触发发布工作流

## 故障排除

### 测试失败
- 检查代码格式：`uv run black --check src tests`
- 运行本地测试：`uv run pytest tests/`
- 查看详细错误日志

### Pre-commit失败
```bash
# 跳过特定hook
SKIP=mypy git commit -m "your message"

# 更新hooks版本
uv run pre-commit autoupdate
```

### 依赖更新
```bash
# 更新lockfile
uv lock --upgrade

# 更新pre-commit hooks
uv run pre-commit autoupdate
```

## 监控和报告

- **测试覆盖率**: [Codecov Dashboard](https://codecov.io/gh/YOUR_USERNAME/arxiv_follow)
- **安全报告**: GitHub Security标签页
- **性能监控**: GitHub Actions执行时间
- **依赖更新**: Dependabot自动PR

## 最佳实践

1. **提交前检查**：确保pre-commit hooks通过
2. **小步提交**：每个PR专注于单一功能
3. **测试驱动**：新功能必须包含测试
4. **安全优先**：定期查看安全扫描报告
5. **文档同步**：代码变更时更新相关文档 
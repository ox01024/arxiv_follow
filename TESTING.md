# ArXiv Follow 测试指南

本项目包含完整的测试套件，确保代码质量和功能正确性。

## 测试结构

```
tests/
├── conftest.py                    # pytest配置和夹具
├── test_ci.py                     # CI/CD测试
├── test_config/                   # 配置模块测试
│   ├── __init__.py
│   └── test_settings.py
├── test_core/                     # 核心模块测试
│   ├── __init__.py
│   ├── test_analyzer.py          # 论文分析器测试
│   ├── test_collector.py         # 论文收集器测试
│   └── test_intelligent_monitor.py # 智能监控测试
├── test_integrations/             # 第三方集成测试
│   ├── __init__.py
│   └── test_dida_integration.py  # 滴答清单集成测试
└── test_services/                 # 服务层测试
    ├── __init__.py
    ├── test_researcher_service.py # 研究者服务测试
    └── test_translation_service.py # 翻译服务测试
```

## 快速开始

### 1. 安装测试依赖

```bash
uv add --dev pytest pytest-cov
```

### 2. 运行测试

使用我们的测试运行器：

```bash
# 运行所有单元测试
python run_tests.py --mode unit

# 运行冒烟测试（快速验证）
python run_tests.py --mode smoke

# 运行所有测试（包括集成测试）
python run_tests.py --mode all

# 生成覆盖率报告
python run_tests.py --mode unit --coverage
```

### 3. 使用pytest直接运行

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_core/test_collector.py

# 运行特定测试类或方法
pytest tests/test_core/test_collector.py::TestPaperCollector::test_collector_initialization

# 详细输出
pytest tests/ -v

# 生成覆盖率报告
pytest tests/ --cov=src/arxiv_follow --cov-report=html
```

## 测试类型

### 单元测试
- **目标**: 测试独立的函数和类
- **特点**: 不需要外部依赖，运行快速
- **命令**: `python run_tests.py --mode unit`

### 集成测试
- **目标**: 测试与外部API的集成
- **前提**: 需要设置API密钥
- **命令**: `python run_tests.py --mode integration`

### 冒烟测试
- **目标**: 快速验证基本功能
- **特点**: 测试模块导入和基础初始化
- **命令**: `python run_tests.py --mode smoke`

## API密钥设置

某些测试需要API密钥：

```bash
# 翻译服务测试
export OPEN_ROUTE_API_KEY="your-openrouter-api-key"

# 滴答清单集成测试
export DIDA_ACCESS_TOKEN="your-dida-access-token"
```

## 测试标记

我们使用pytest标记来分类测试：

- `@pytest.mark.api`: 需要API密钥的测试
- `@pytest.mark.network`: 需要网络连接的测试
- `@pytest.mark.slow`: 运行较慢的测试
- `@pytest.mark.integration`: 集成测试

### 运行特定标记的测试

```bash
# 只运行不需要API的测试
pytest tests/ -m "not api and not network"

# 只运行集成测试
pytest tests/ -m "api or integration"

# 排除慢速测试
pytest tests/ -m "not slow"
```

## 测试运行器选项

我们的测试运行器（`run_tests.py`）提供多种选项：

```bash
# 基本选项
python run_tests.py --mode {unit,integration,smoke,all,report}
python run_tests.py --module {core,services,integrations}
python run_tests.py --verbose
python run_tests.py --coverage
python run_tests.py --no-deps-check

# 示例
python run_tests.py --mode unit --verbose --coverage
python run_tests.py --module core --verbose
python run_tests.py --mode all --coverage
```

## 覆盖率报告

生成覆盖率报告：

```bash
# HTML报告
python run_tests.py --mode report
# 查看报告：打开 htmlcov/index.html

# 命令行报告
pytest tests/ --cov=src/arxiv_follow --cov-report=term-missing
```

## 持续集成

项目配置了GitHub Actions自动化测试：

- **推送到main/develop分支**: 运行完整测试套件
- **Pull Request**: 运行单元测试和集成测试
- **多Python版本**: 3.9, 3.10, 3.11, 3.12

查看`.github/workflows/tests.yml`了解详细配置。

## 编写新测试

### 1. 测试文件命名

- 测试文件以`test_`开头
- 测试类以`Test`开头
- 测试方法以`test_`开头

### 2. 使用夹具（Fixtures）

```python
def test_my_function(sample_paper_data):
    """使用conftest.py中定义的夹具"""
    result = my_function(sample_paper_data)
    assert result is not None
```

### 3. 模拟（Mocking）

```python
@patch('httpx.Client.get')
def test_api_call(mock_get):
    """模拟HTTP请求"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    # 测试代码...
```

### 4. 跳过测试

```python
@pytest.mark.skipif(not os.getenv('API_KEY'), reason="需要API密钥")
def test_api_function():
    """需要API密钥的测试"""
    pass
```

## 故障排除

### 常见问题

1. **导入错误**: 确保安装了项目包 `uv pip install -e .`
2. **API测试失败**: 检查API密钥设置
3. **网络测试失败**: 检查网络连接
4. **依赖问题**: 运行 `uv sync --dev`

### 调试测试

```bash
# 详细输出
pytest tests/ -v -s

# 只运行失败的测试
pytest tests/ --lf

# 在第一个失败时停止
pytest tests/ -x

# 进入调试器
pytest tests/ --pdb
```

## 性能考虑

- 单元测试应该快速（<1秒）
- 使用mock避免实际的网络调用
- 集成测试可以较慢但应限制在合理范围内
- 定期清理临时文件和测试数据

## 报告问题

如果发现测试问题：

1. 确认问题是可重现的
2. 收集错误日志和环境信息
3. 创建minimal reproduction case
4. 在GitHub Issues中报告

## 最佳实践

1. **测试应该独立**: 每个测试不应依赖其他测试的状态
2. **使用有意义的断言**: 使用具体的断言而不是简单的`assert True`
3. **测试边界条件**: 包括异常情况和错误处理
4. **保持测试简单**: 每个测试应该只验证一个行为
5. **及时更新测试**: 修改代码时同时更新相关测试

---

有关更多信息，请参阅项目的[主要README](README.md)和[开发指南](DEVELOPMENT.md)。 
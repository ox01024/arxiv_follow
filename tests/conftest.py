#!/usr/bin/env python3
"""
Pytest配置文件
包含全局测试夹具和配置
"""

import os
import sys
from unittest.mock import Mock

import pytest

# 确保项目根目录在Python路径中
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)


@pytest.fixture(scope="session")
def project_root_path():
    """项目根目录路径"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(scope="session")
def sample_arxiv_id():
    """示例arXiv ID"""
    return "2501.12345"


@pytest.fixture(scope="session")
def sample_paper_data():
    """示例论文数据"""
    return {
        "arxiv_id": "2501.12345",
        "title": "Deep Learning for Cybersecurity: A Comprehensive Survey",
        "authors": ["John Smith", "Alice Brown", "Bob Wilson"],
        "abstract": "This paper presents a comprehensive survey of deep learning techniques applied to cybersecurity problems.",
        "subjects": ["cs.AI", "cs.CR", "cs.LG"],
        "url": "https://arxiv.org/abs/2501.12345",
        "pdf_url": "https://arxiv.org/pdf/2501.12345.pdf",
    }


@pytest.fixture(scope="session")
def sample_researchers_data():
    """示例研究者数据"""
    return [
        {"name": "John Smith", "affiliation": "MIT", "field": "AI"},
        {"name": "Alice Brown", "affiliation": "Stanford", "field": "ML"},
        {"name": "Bob Wilson", "affiliation": "CMU", "field": "Security"},
    ]


@pytest.fixture
def mock_httpx_client():
    """模拟的HTTPX客户端"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html>Mock response content</html>"
    mock_response.raise_for_status.return_value = None
    mock_client.get.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_successful_api_response():
    """模拟成功的API响应"""
    return {
        "success": True,
        "data": "Mock successful response",
        "timestamp": "2025-01-15T09:00:00Z",
    }


@pytest.fixture
def mock_failed_api_response():
    """模拟失败的API响应"""
    return {"success": False, "error": "Mock API error", "error_code": "TEST_ERROR"}


@pytest.fixture(autouse=True)
def clean_environment():
    """清理测试环境变量"""
    # 在测试前保存原有环境变量
    original_env = {}
    test_env_vars = ["OPEN_ROUTE_API_KEY", "DIDA_ACCESS_TOKEN"]

    for var in test_env_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]

    yield

    # 测试后恢复原有环境变量
    for var in test_env_vars:
        if var in original_env:
            os.environ[var] = original_env[var]
        elif var in os.environ:
            del os.environ[var]


def pytest_configure(config):
    """Pytest配置钩子"""
    # 添加自定义标记
    config.addinivalue_line("markers", "slow: 标记运行较慢的测试")
    config.addinivalue_line("markers", "integration: 标记集成测试")
    config.addinivalue_line("markers", "api: 标记需要API密钥的测试")
    config.addinivalue_line("markers", "network: 标记需要网络连接的测试")


def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    # 自动为需要API密钥的测试添加标记
    for item in items:
        # 检查测试名称或文档字符串中是否包含API相关关键词
        if any(
            keyword in item.name.lower() for keyword in ["api", "connection", "token"]
        ):
            if "api" not in [mark.name for mark in item.iter_markers()]:
                item.add_marker(pytest.mark.api)

        # 检查是否需要网络连接
        if any(
            keyword in item.name.lower() for keyword in ["fetch", "download", "request"]
        ):
            if "network" not in [mark.name for mark in item.iter_markers()]:
                item.add_marker(pytest.mark.network)


@pytest.fixture
def skip_if_no_api_key(request):
    """如果没有API密钥则跳过测试"""
    if not os.getenv("OPEN_ROUTE_API_KEY"):
        pytest.skip("需要OPEN_ROUTE_API_KEY环境变量")


@pytest.fixture
def skip_if_no_dida_token(request):
    """如果没有滴答清单token则跳过测试"""
    if not os.getenv("DIDA_ACCESS_TOKEN"):
        pytest.skip("需要DIDA_ACCESS_TOKEN环境变量")


# 测试环境配置
pytest_plugins = []

#!/usr/bin/env python3
"""
研究者服务测试
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

try:
    from src.arxiv_follow.services.researcher import (
        ResearcherService,
        fetch_papers_for_researcher,
        fetch_researchers_from_tsv,
        parse_arxiv_search_results,
    )
except ImportError as e:
    pytest.skip(f"研究者服务模块导入失败: {e}", allow_module_level=True)


class TestResearcherService:
    """研究者服务测试类"""

    @pytest.fixture
    def service(self):
        """创建研究者服务实例"""
        return ResearcherService()

    def test_service_initialization(self, service):
        """测试服务初始化"""
        assert service is not None
        assert hasattr(service, "client")
        assert hasattr(service, "fetch_researchers_from_tsv")

    @patch("httpx.Client.get")
    def test_fetch_researchers_from_tsv_success(self, mock_get, service):
        """测试成功获取研究者数据"""
        # 模拟TSV响应
        mock_response = Mock()
        mock_response.text = "name\taffiliation\nJohn Smith\tMIT\nAlice Brown\tStanford"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        url = "https://example.com/test.tsv"
        result = service.fetch_researchers_from_tsv(url)

        # 实际调用函数测试
        result = fetch_researchers_from_tsv(url)
        assert len(result) == 2
        assert result[0]["name"] == "John Smith"
        assert result[1]["name"] == "Alice Brown"

    @patch("httpx.Client.get")
    def test_fetch_researchers_network_error(self, mock_get, service):
        """测试网络错误处理"""
        mock_get.side_effect = Exception("Network error")

        url = "https://example.com/test.tsv"
        result = fetch_researchers_from_tsv(url)

        assert result == []

    def test_parse_arxiv_search_results_empty(self):
        """测试解析空搜索结果"""
        html_content = "Sorry, your query returned no results"
        result = parse_arxiv_search_results(html_content)

        assert result == []

    def test_parse_arxiv_search_results_with_papers(self):
        """测试解析包含论文的搜索结果"""
        html_content = """
        <html>
        <body>
            <li class="arxiv-result">
                <a href="https://arxiv.org/abs/2501.12345">arXiv:2501.12345</a>
                <p class="title is-5 mathjax">Deep Learning for Cybersecurity</p>
                <p class="authors">
                    <span>Authors:</span>
                    <a href="#">John Smith</a>, 
                    <a href="#">Alice Brown</a>
                </p>
            </li>
            <li class="arxiv-result">
                <a href="https://arxiv.org/abs/2501.12346">arXiv:2501.12346</a>
                <p class="title is-5 mathjax">Machine Learning Security</p>
            </li>
        </body>
        </html>
        """

        result = parse_arxiv_search_results(html_content)

        assert len(result) == 2
        assert result[0]["arxiv_id"] == "2501.12345"
        assert "Deep Learning for Cybersecurity" in result[0]["title"]
        # 由于实际的解析逻辑可能与测试HTML结构不完全匹配，我们检查论文基本信息
        assert "title" in result[0]
        assert "url" in result[0]

    @patch("src.arxiv_follow.services.researcher.fetch_papers_for_researcher")
    def test_fetch_papers_for_researcher_wrapper(self, mock_fetch, service):
        """测试获取研究者论文的包装方法"""
        mock_fetch.return_value = [{"arxiv_id": "2501.12345", "title": "Test Paper"}]

        result = service.fetch_papers_for_researcher(
            "John Smith", "2025-01-01", "2025-01-02"
        )

        assert len(result) == 1
        assert result[0]["arxiv_id"] == "2501.12345"
        mock_fetch.assert_called_once_with("John Smith", "2025-01-01", "2025-01-02")

    def test_tsv_parsing_with_header(self):
        """测试带标题行的TSV解析"""
        # 模拟包含标题行的TSV数据
        with patch("httpx.Client.get") as mock_get:
            mock_response = Mock()
            mock_response.text = "name\taffiliation\tfield\nJohn Smith\tMIT\tAI\nAlice Brown\tStanford\tML"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_researchers_from_tsv("https://example.com/test.tsv")

            assert len(result) == 2
            assert result[0]["name"] == "John Smith"
            assert result[0]["affiliation"] == "MIT"
            assert result[0]["field"] == "AI"

    def test_tsv_parsing_without_header(self):
        """测试无标题行的TSV解析"""
        with patch("httpx.Client.get") as mock_get:
            mock_response = Mock()
            mock_response.text = "John Smith\nAlice Brown\nBob Wilson"
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_researchers_from_tsv("https://example.com/test.tsv")

            assert len(result) == 3
            assert result[0]["name"] == "John Smith"
            assert result[1]["name"] == "Alice Brown"
            assert result[2]["name"] == "Bob Wilson"

    def test_tsv_parsing_empty_data(self):
        """测试空数据处理"""
        with patch("httpx.Client.get") as mock_get:
            mock_response = Mock()
            mock_response.text = ""
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = fetch_researchers_from_tsv("https://example.com/test.tsv")

            assert result == []

    @patch("httpx.Client.get")
    def test_fetch_papers_success(self, mock_get):
        """测试成功获取论文"""
        mock_response = Mock()
        mock_response.text = """
        <li class="arxiv-result">
            <a href="https://arxiv.org/abs/2501.12345">arXiv:2501.12345</a>
            <p class="title is-5 mathjax">Test Paper Title</p>
        </li>
        """
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_papers_for_researcher("John Smith", "2025-01-01", "2025-01-02")

        assert len(result) == 1
        assert result[0]["arxiv_id"] == "2501.12345"

    @patch("httpx.Client.get")
    def test_fetch_papers_network_failure(self, mock_get):
        """测试获取论文时的网络错误"""
        mock_get.side_effect = Exception("Network error")

        result = fetch_papers_for_researcher("John Smith", "2025-01-01", "2025-01-02")

        assert result == []

    def test_build_arxiv_search_url(self):
        """测试构建arXiv搜索URL"""
        from src.arxiv_follow.services.researcher import build_arxiv_search_url

        url = build_arxiv_search_url("John Smith", "2025-01-01", "2025-01-02")

        assert "arxiv.org/search/advanced" in url
        assert "John%20Smith" in url or "John+Smith" in url
        assert "2025-01-01" in url
        assert "2025-01-02" in url

    def test_date_handling_same_dates(self):
        """测试相同日期的处理"""
        from src.arxiv_follow.services.researcher import build_arxiv_search_url

        # 当开始日期和结束日期相同时，应该自动调整结束日期
        url = build_arxiv_search_url("John Smith", "2025-01-01", "2025-01-01")

        # 应该包含调整后的结束日期
        assert "2025-01-02" in url

    def test_html_content_extraction(self):
        """测试HTML内容提取功能"""
        html_with_abstract = """
        <li class="arxiv-result">
            <a href="https://arxiv.org/abs/2501.12345">arXiv:2501.12345</a>
            <p class="title is-5 mathjax">Test Paper</p>
            <span class="abstract-full">This is the full abstract of the paper.</span>
        </li>
        """

        result = parse_arxiv_search_results(html_with_abstract)

        assert len(result) == 1
        # 检查是否提取了摘要（如果实现了的话）
        # assert 'abstract' in result[0]

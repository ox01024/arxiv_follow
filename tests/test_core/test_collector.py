#!/usr/bin/env python3
"""
论文收集器测试
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

try:
    from src.arxiv_follow.core.collector import PaperCollector
except ImportError as e:
    pytest.skip(f"论文收集器模块导入失败: {e}", allow_module_level=True)


class TestPaperCollector:
    """论文收集器测试类"""

    @pytest.fixture
    def collector(self):
        """创建论文收集器实例"""
        return PaperCollector()

    def test_collector_initialization(self, collector):
        """测试收集器初始化"""
        assert collector is not None
        assert hasattr(collector, "session")
        assert hasattr(collector, "get_paper_abstract_page")

    def test_extract_paper_metadata(self, collector):
        """测试论文元数据提取"""
        # 模拟HTML内容
        sample_html = """
        <h1 class="title mathjax">
            <span class="descriptor">Title:</span>
            <span>Deep Learning for Cybersecurity: A Survey</span>
        </h1>
        <div class="authors">
            <a href="#">John Smith</a>, 
            <a href="#">Alice Brown</a>
        </div>
        <blockquote class="abstract mathjax">
            <span class="descriptor">Abstract:</span>
            This paper presents a comprehensive survey of deep learning techniques
        </blockquote>
        """

        arxiv_id = "2501.12345"
        metadata = collector.extract_paper_metadata(sample_html, arxiv_id)

        assert metadata["arxiv_id"] == arxiv_id
        assert "title" in metadata
        assert "url" in metadata
        assert "pdf_url" in metadata
        assert "collection_time" in metadata

    def test_extract_text_from_html(self, collector):
        """测试HTML文本提取"""
        sample_html = """
        <html>
        <body>
            <h1>Introduction</h1>
            <p>This is the introduction section.</p>
            <h2>Methods</h2>
            <p>This describes our methods.</p>
        </body>
        </html>
        """

        result = collector.extract_text_from_html(sample_html)

        assert "has_html_version" in result
        assert result["has_html_version"] is True
        assert "extraction_time" in result

    @patch("httpx.Client.get")
    def test_get_paper_abstract_page_success(self, mock_get, collector):
        """测试成功获取论文摘要页面"""
        # 模拟成功的HTTP响应
        mock_response = Mock()
        mock_response.text = "<html>Mock HTML content</html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        arxiv_id = "2501.12345"
        result = collector.get_paper_abstract_page(arxiv_id)

        assert result == "<html>Mock HTML content</html>"
        mock_get.assert_called_once()

    @patch("httpx.Client.get")
    def test_get_paper_abstract_page_failure(self, mock_get, collector):
        """测试获取论文摘要页面失败"""
        # 模拟HTTP错误
        mock_get.side_effect = Exception("Network error")

        arxiv_id = "2501.12345"
        result = collector.get_paper_abstract_page(arxiv_id)

        assert result is None

    @patch("httpx.Client.get")
    def test_get_paper_html_content_success(self, mock_get, collector):
        """测试成功获取HTML版本内容"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>HTML version content</html>"
        mock_get.return_value = mock_response

        arxiv_id = "2501.12345"
        result = collector.get_paper_html_content(arxiv_id)

        assert result == "<html>HTML version content</html>"

    @patch("httpx.Client.get")
    def test_get_paper_html_content_not_available(self, mock_get, collector):
        """测试HTML版本不可用"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        arxiv_id = "2501.12345"
        result = collector.get_paper_html_content(arxiv_id)

        assert result is None

    def test_collect_multiple_papers(self, collector):
        """测试批量收集论文"""
        arxiv_ids = ["2501.12345", "2501.12346"]

        with patch.object(collector, "collect_paper_content") as mock_collect:
            mock_collect.side_effect = [
                {"arxiv_id": "2501.12345", "title": "Paper 1"},
                {"arxiv_id": "2501.12346", "title": "Paper 2"},
            ]

            results = collector.collect_multiple_papers(arxiv_ids, delay=0.1)

            assert len(results) == 2
            assert "2501.12345" in results
            assert "2501.12346" in results
            assert mock_collect.call_count == 2

    def test_invalid_arxiv_id_handling(self, collector):
        """测试无效arXiv ID处理"""
        # 测试空ID
        result = collector.extract_paper_metadata("", "")
        assert "arxiv_id" in result

        # 测试无效格式ID
        result = collector.extract_paper_metadata("<html></html>", "invalid_id")
        assert result["arxiv_id"] == "invalid_id"

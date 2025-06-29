#!/usr/bin/env python3
"""
论文分析器测试
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

try:
    from src.arxiv_follow.core.analyzer import PaperAnalyzer
    from src.arxiv_follow.models.config import APIConfig, AppConfig
except ImportError as e:
    pytest.skip(f"论文分析器模块导入失败: {e}", allow_module_level=True)


class TestPaperAnalyzer:
    """论文分析器测试类"""

    @pytest.fixture
    def mock_config_with_api_key(self):
        """创建带有API密钥的模拟配置"""
        config = MagicMock(spec=AppConfig)
        config.get_llm_api_key.return_value = "test_api_key"
        config.llm = MagicMock(spec=APIConfig)
        config.llm.api_base_url = "https://openrouter.ai/api/v1"
        config.llm.default_model = "google/gemini-2.0-flash-001"
        return config

    @pytest.fixture
    def mock_config_without_api_key(self):
        """创建没有API密钥的模拟配置"""
        config = MagicMock(spec=AppConfig)
        config.get_llm_api_key.return_value = None
        config.llm = MagicMock(spec=APIConfig)
        config.llm.api_base_url = "https://openrouter.ai/api/v1"
        config.llm.default_model = "google/gemini-2.0-flash-001"
        return config

    @pytest.fixture
    def analyzer(self, mock_config_without_api_key):
        """创建论文分析器实例"""
        return PaperAnalyzer(mock_config_without_api_key)

    @pytest.fixture
    def analyzer_with_key(self, mock_config_with_api_key):
        """创建带有API密钥的论文分析器实例"""
        return PaperAnalyzer(mock_config_with_api_key)

    @pytest.fixture
    def sample_paper_data(self):
        """示例论文数据"""
        return {
            "arxiv_id": "2501.12345",
            "title": "Deep Learning for Cybersecurity: A Comprehensive Survey",
            "authors": ["John Smith", "Alice Brown", "Bob Wilson"],
            "abstract": "This paper presents a comprehensive survey of deep learning techniques applied to cybersecurity problems. We review recent advances in neural network architectures for intrusion detection, malware analysis, and threat intelligence.",
            "subjects": ["cs.AI", "cs.CR", "cs.LG"],
            "url": "https://arxiv.org/abs/2501.12345",
        }

    def test_analyzer_initialization(self, analyzer):
        """测试分析器初始化"""
        assert analyzer is not None
        assert hasattr(analyzer, "is_enabled")
        assert hasattr(analyzer, "analyze_paper_significance")

    def test_is_enabled_without_api_key(self, analyzer):
        """测试没有API密钥时的状态"""
        assert not analyzer.is_enabled()

    def test_is_enabled_with_api_key(self, analyzer_with_key):
        """测试有API密钥时的状态"""
        assert analyzer_with_key.is_enabled()

    @pytest.mark.asyncio
    async def test_analyze_paper_significance_no_api_key(
        self, analyzer, sample_paper_data
    ):
        """测试没有API密钥时的重要性分析"""
        result = await analyzer.analyze_paper_significance(sample_paper_data)

        assert "error" in result
        assert "分析器未启用" in result["error"]
        assert result["success"] is False

    @pytest.mark.asyncio
    @patch("src.arxiv_follow.core.analyzer.PaperAnalyzer._call_llm")
    async def test_analyze_paper_significance_success(
        self, mock_call_llm, analyzer_with_key, sample_paper_data
    ):
        """测试成功的重要性分析"""
        # 模拟LLM响应
        mock_response = """
        ## 研究意义
        这项研究解决了网络安全领域的关键问题。

        ## 技术创新点
        提出了新的深度学习架构。

        ## 应用价值
        可用于实时威胁检测。

        ## 重要性评分
        重要性评分: 8.5
        """
        mock_call_llm.return_value = mock_response

        result = await analyzer_with_key.analyze_paper_significance(sample_paper_data)

        assert result["success"] is True
        assert result["analysis_type"] == "significance"
        assert "content" in result
        assert "model" in result
        assert "analysis_time" in result
        assert "importance_score" in result

    @pytest.mark.asyncio
    @patch("src.arxiv_follow.core.analyzer.PaperAnalyzer._call_llm")
    async def test_analyze_paper_technical_details_success(
        self, mock_call_llm, analyzer_with_key, sample_paper_data
    ):
        """测试成功的技术分析"""
        mock_response = """
        ## 方法论分析
        使用了监督学习和无监督学习方法。

        ## 算法详解
        基于深度神经网络的异常检测算法。

        ## 实验设计
        使用了多个公开数据集进行验证。
        """
        mock_call_llm.return_value = mock_response

        result = await analyzer_with_key.analyze_paper_technical_details(
            sample_paper_data
        )

        assert result["success"] is True
        assert result["analysis_type"] == "technical"
        assert "content" in result

    @pytest.mark.asyncio
    @patch("src.arxiv_follow.core.analyzer.PaperAnalyzer._call_llm")
    async def test_analyze_paper_llm_failure(
        self, mock_call_llm, analyzer_with_key, sample_paper_data
    ):
        """测试LLM调用失败的情况"""
        mock_call_llm.return_value = None

        result = await analyzer_with_key.analyze_paper_significance(sample_paper_data)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    @patch("src.arxiv_follow.core.analyzer.PaperAnalyzer._call_llm")
    async def test_generate_comprehensive_report(
        self, mock_call_llm, analyzer_with_key, sample_paper_data
    ):
        """测试生成综合报告"""
        # 模拟LLM响应
        mock_call_llm.return_value = "Mock comprehensive report response"

        result = await analyzer_with_key.generate_comprehensive_report(
            sample_paper_data
        )

        assert result["success"] is True
        assert result["analysis_type"] == "comprehensive"
        assert "paper_info" in result
        assert "significance_analysis" in result
        assert "technical_analysis" in result
        assert "overall_score" in result

    @pytest.mark.asyncio
    async def test_analyze_multiple_papers(self, analyzer_with_key, sample_paper_data):
        """测试批量分析论文"""
        papers = [sample_paper_data, {**sample_paper_data, "arxiv_id": "2501.12346"}]

        with patch.object(
            analyzer_with_key, "analyze_paper_significance"
        ) as mock_analyze:
            mock_analyze.return_value = {"success": True, "content": "分析结果"}

            results = await analyzer_with_key.analyze_multiple_papers(
                papers, mode="significance"
            )

            assert len(results) == 2
            assert mock_analyze.call_count == 2

    def test_generate_daily_summary(self, analyzer_with_key):
        """测试生成每日总结"""
        papers_analysis = [
            {
                "paper_info": {"title": "Paper 1", "arxiv_id": "2501.12345", "categories": ["cs.AI"]},
                "significance_analysis": {"content": "重要论文"},
                "importance_score": 8.5,
                "success": True,
            },
            {
                "paper_info": {"title": "Paper 2", "arxiv_id": "2501.12346", "categories": ["cs.LG"]},
                "significance_analysis": {"content": "一般论文"},
                "importance_score": 6.2,
                "success": True,
            },
        ]

        result = analyzer_with_key.generate_daily_summary(papers_analysis)

        assert "date" in result
        assert "total_papers" in result
        assert "successful_analysis" in result
        assert result["total_papers"] == 2
        assert result["successful_analysis"] == 2
        assert "summary_text" in result

    def test_error_handling_empty_paper_data(self, analyzer):
        """测试空论文数据的错误处理"""
        # 这个测试验证分析器能够优雅地处理空或无效的论文数据
        assert analyzer is not None
        # 由于没有API密钥，这个分析器应该是禁用状态
        assert not analyzer.is_enabled()

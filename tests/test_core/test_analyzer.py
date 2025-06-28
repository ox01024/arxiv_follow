#!/usr/bin/env python3
"""
论文分析器测试
"""

import os
import sys
from unittest.mock import patch

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

try:
    from src.arxiv_follow.core.analyzer import PaperAnalyzer
except ImportError as e:
    pytest.skip(f"论文分析器模块导入失败: {e}", allow_module_level=True)


class TestPaperAnalyzer:
    """论文分析器测试类"""

    @pytest.fixture
    def analyzer(self):
        """创建论文分析器实例"""
        return PaperAnalyzer()

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
        # 不设置API密钥的情况下
        analyzer_no_key = PaperAnalyzer(api_key=None)
        assert not analyzer_no_key.is_enabled()

    def test_is_enabled_with_api_key(self):
        """测试有API密钥时的状态"""
        analyzer_with_key = PaperAnalyzer(api_key="test_key")
        assert analyzer_with_key.is_enabled()

    def test_analyze_paper_significance_no_api_key(self, analyzer, sample_paper_data):
        """测试没有API密钥时的重要性分析"""
        analyzer_no_key = PaperAnalyzer(api_key=None)
        result = analyzer_no_key.analyze_paper_significance(sample_paper_data)

        assert "error" in result
        assert "分析器未启用" in result["error"]

    @patch("src.arxiv_follow.core.analyzer.PaperAnalyzer._call_llm")
    def test_analyze_paper_significance_success(self, mock_call_llm, sample_paper_data):
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
        8.5/10
        """
        mock_call_llm.return_value = mock_response

        analyzer = PaperAnalyzer(api_key="test_key")
        result = analyzer.analyze_paper_significance(sample_paper_data)

        assert result["success"] is True
        assert result["analysis_type"] == "significance"
        assert "content" in result
        assert "model" in result
        assert "analysis_time" in result

    @patch("src.arxiv_follow.core.analyzer.PaperAnalyzer._call_llm")
    def test_analyze_paper_technical_details_success(
        self, mock_call_llm, sample_paper_data
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

        analyzer = PaperAnalyzer(api_key="test_key")
        result = analyzer.analyze_paper_technical_details(sample_paper_data)

        assert result["success"] is True
        assert result["analysis_type"] == "technical"
        assert "content" in result

    @patch("src.arxiv_follow.core.analyzer.PaperAnalyzer._call_llm")
    def test_analyze_paper_llm_failure(self, mock_call_llm, sample_paper_data):
        """测试LLM调用失败的情况"""
        mock_call_llm.return_value = None

        analyzer = PaperAnalyzer(api_key="test_key")
        result = analyzer.analyze_paper_significance(sample_paper_data)

        assert result["success"] is False
        assert "error" in result

    @patch("src.arxiv_follow.core.analyzer.PaperAnalyzer.analyze_paper_significance")
    @patch(
        "src.arxiv_follow.core.analyzer.PaperAnalyzer.analyze_paper_technical_details"
    )
    def test_generate_comprehensive_report(
        self, mock_technical, mock_significance, sample_paper_data
    ):
        """测试生成综合报告"""
        # 模拟分析结果
        mock_significance.return_value = {
            "success": True,
            "content": "重要性分析结果",
            "analysis_type": "significance",
        }
        mock_technical.return_value = {
            "success": True,
            "content": "技术分析结果",
            "analysis_type": "technical",
        }

        analyzer = PaperAnalyzer(api_key="test_key")

        # 使用patch装饰器确保不会调用实际的LLM
        with patch.object(analyzer, "_call_llm") as mock_llm:
            mock_llm.return_value = "Mock response"
            result = analyzer.generate_comprehensive_report(sample_paper_data)

        assert result["success"] is True
        assert result["report_type"] == "comprehensive"
        assert "report_content" in result
        assert "analysis_components" in result
        assert result["analysis_components"]["significance"] is True
        assert result["analysis_components"]["technical"] is True

    def test_analyze_multiple_papers(self, sample_paper_data):
        """测试批量分析论文"""
        papers = [sample_paper_data, {**sample_paper_data, "arxiv_id": "2501.12346"}]

        with patch.object(PaperAnalyzer, "analyze_paper_significance") as mock_analyze:
            mock_analyze.return_value = {"success": True, "content": "分析结果"}

            analyzer = PaperAnalyzer(api_key="test_key")
            results = analyzer.analyze_multiple_papers(papers, mode="significance")

            assert len(results) == 2
            assert mock_analyze.call_count == 2

    @patch("src.arxiv_follow.core.analyzer.PaperAnalyzer._call_llm")
    def test_generate_daily_summary(self, mock_call_llm):
        """测试生成每日总结"""
        papers_analysis = [
            {
                "paper_data": {"title": "Paper 1", "arxiv_id": "2501.12345"},
                "significance_analysis": {"content": "重要论文"},
                "success": True,
            },
            {
                "paper_data": {"title": "Paper 2", "arxiv_id": "2501.12346"},
                "significance_analysis": {"content": "一般论文"},
                "success": True,
            },
        ]

        mock_call_llm.return_value = "今日论文总结：发现2篇重要论文..."

        analyzer = PaperAnalyzer(api_key="test_key")
        result = analyzer.generate_daily_summary(papers_analysis)

        assert result["success"] is True
        assert "summary_content" in result
        assert "papers_count" in result
        assert result["papers_count"] == 2

    def test_error_handling_empty_paper_data(self, analyzer):
        """测试空论文数据的错误处理"""
        empty_data = {}

        if analyzer.is_enabled():
            with patch.object(analyzer, "_call_llm") as mock_call:
                mock_call.return_value = "分析结果"
                result = analyzer.analyze_paper_significance(empty_data)
                assert result is not None
        else:
            result = analyzer.analyze_paper_significance(empty_data)
            assert "error" in result

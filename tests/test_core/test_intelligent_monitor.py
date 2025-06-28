#!/usr/bin/env python3
"""
智能论文监控测试套件 - 测试论文采集、分析和集成功能
"""

import os
import sys
import unittest
from unittest.mock import patch

# 导入模块
try:
    from config import PAPER_ANALYSIS_CONFIG
    from intelligent_monitor import IntelligentPaperMonitor, create_intelligent_monitor
    from paper_analyzer import PaperAnalyzer, analyze_paper
    from paper_collector import PaperCollector, collect_paper_content
except ImportError as e:
    print(f"❌ 导入测试模块失败: {e}")
    sys.exit(1)


class TestPaperCollector(unittest.TestCase):
    """测试论文采集功能"""

    def setUp(self):
        """设置测试环境"""
        self.collector = PaperCollector()
        self.test_arxiv_id = "2312.11805"

    def test_collector_initialization(self):
        """测试采集器初始化"""
        self.assertIsNotNone(self.collector)
        self.assertIsNotNone(self.collector.session)

    def test_get_paper_abstract_page(self):
        """测试获取论文摘要页面"""
        # 使用一个简单的测试ID
        result = self.collector.get_paper_abstract_page("1234.5678")
        # 这个ID不存在，但应该返回一个响应（可能是404页面）
        self.assertIsInstance(result, (str, type(None)))

    def test_extract_paper_metadata(self):
        """测试元数据提取"""
        # 模拟HTML内容
        mock_html = """
        <h1 class="title mathjax"><span>Test Paper Title</span></h1>
        <div class="authors"><a>Test Author</a></div>
        <blockquote class="abstract mathjax">
            <span>Abstract:</span> This is a test abstract.
        </blockquote>
        """

        result = self.collector.extract_paper_metadata(mock_html, "1234.5678")

        self.assertEqual(result["arxiv_id"], "1234.5678")
        self.assertIn("title", result)
        self.assertIn("url", result)
        self.assertIn("pdf_url", result)


class TestPaperAnalyzer(unittest.TestCase):
    """测试论文分析功能"""

    def setUp(self):
        """设置测试环境"""
        self.analyzer = PaperAnalyzer()
        self.test_paper = {
            "arxiv_id": "2501.12345",
            "title": "Test Paper: Deep Learning for Testing",
            "authors": ["Test Author 1", "Test Author 2"],
            "abstract": "This is a test abstract for demonstration purposes. It contains enough text to test the analysis functionality.",
            "subjects": ["cs.AI", "cs.LG"],
        }

    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        self.assertIsNotNone(self.analyzer)
        # is_enabled 取决于环境变量
        enabled = self.analyzer.is_enabled()
        self.assertIsInstance(enabled, bool)

    def test_analyze_paper_disabled(self):
        """测试分析器禁用时的行为"""
        # 临时禁用分析器
        with patch.object(self.analyzer, "is_enabled", return_value=False):
            result = self.analyzer.analyze_paper_significance(self.test_paper)
            self.assertIn("error", result)

    @unittest.skipUnless(os.getenv("OPEN_ROUTE_API_KEY"), "需要API密钥")
    def test_analyze_paper_significance(self):
        """测试重要性分析（需要API密钥）"""
        if self.analyzer.is_enabled():
            result = self.analyzer.analyze_paper_significance(self.test_paper)
            self.assertIn("success", result)
            if result.get("success"):
                self.assertIn("content", result)
                self.assertIn("analysis_time", result)


class TestIntelligentMonitor(unittest.TestCase):
    """测试智能监控集成"""

    def setUp(self):
        """设置测试环境"""
        self.monitor = create_intelligent_monitor()
        self.test_papers = [
            {
                "arxiv_id": "2501.12345",
                "title": "Test Paper 1",
                "authors": ["Author 1"],
                "abstract": "Test abstract 1",
                "url": "https://arxiv.org/abs/2501.12345",
            },
            {
                "arxiv_id": "2501.12346",
                "title": "Test Paper 2",
                "authors": ["Author 2"],
                "abstract": "Test abstract 2",
                "url": "https://arxiv.org/abs/2501.12346",
            },
        ]

    def test_monitor_initialization(self):
        """测试监控器初始化"""
        self.assertIsNotNone(self.monitor)
        self.assertIsNotNone(self.monitor.config)

    def test_feature_status_check(self):
        """测试功能状态检查"""
        collection_enabled = self.monitor.is_collection_enabled()
        analysis_enabled = self.monitor.is_analysis_enabled()

        self.assertIsInstance(collection_enabled, bool)
        self.assertIsInstance(analysis_enabled, bool)

    def test_generate_enhanced_content(self):
        """测试增强内容生成"""
        content = self.monitor.generate_enhanced_content(self.test_papers)

        self.assertIsInstance(content, str)
        self.assertIn("论文详情", content)
        self.assertIn("Test Paper 1", content)
        self.assertIn("Test Paper 2", content)
        self.assertIn("统计信息", content)

    @patch("intelligent_monitor.create_arxiv_task")
    def test_create_intelligent_dida_task(self, mock_create_task):
        """测试智能任务创建"""
        # 模拟成功的任务创建
        mock_create_task.return_value = {
            "success": True,
            "task_id": "test_task_id",
            "task_url": "https://test.url",
        }

        result = self.monitor.create_intelligent_dida_task(
            report_type="test", title="测试任务", papers=self.test_papers
        )

        self.assertTrue(result.get("success"))
        self.assertIn("intelligent_features", result)
        mock_create_task.assert_called_once()


def run_integration_tests():
    """运行集成测试"""
    print("🧪 运行智能监控集成测试")
    print("=" * 50)

    # 检查环境配置
    api_key = os.getenv("OPEN_ROUTE_API_KEY")
    dida_token = os.getenv("DIDA_ACCESS_TOKEN")

    print(f"API密钥: {'✅ 已配置' if api_key else '❌ 未配置'}")
    print(f"滴答Token: {'✅ 已配置' if dida_token else '❌ 未配置'}")

    # 测试配置读取
    print("\n📋 配置检查:")
    print(f"   启用分析: {PAPER_ANALYSIS_CONFIG.get('enable_analysis')}")
    print(f"   启用采集: {PAPER_ANALYSIS_CONFIG.get('enable_content_collection')}")
    print(f"   分析模式: {PAPER_ANALYSIS_CONFIG.get('analysis_mode')}")

    # 创建监控器测试
    try:
        monitor = create_intelligent_monitor()
        print("\n🚀 监控器创建: ✅ 成功")
        print(f"   内容采集: {'启用' if monitor.is_collection_enabled() else '禁用'}")
        print(f"   LLM分析: {'启用' if monitor.is_analysis_enabled() else '禁用'}")
    except Exception as e:
        print(f"\n🚀 监控器创建: ❌ 失败 - {e}")

    # 基础功能测试
    test_papers = [
        {
            "arxiv_id": "test.12345",
            "title": "集成测试论文",
            "authors": ["测试作者"],
            "abstract": "这是一个用于集成测试的模拟论文摘要。",
            "url": "https://arxiv.org/abs/test.12345",
        }
    ]

    try:
        enhanced_content = monitor.generate_enhanced_content(test_papers)
        print(f"\n📝 内容生成: ✅ 成功 (长度: {len(enhanced_content)})")
    except Exception as e:
        print(f"\n📝 内容生成: ❌ 失败 - {e}")


def main():
    """主测试函数"""
    print("🎯 ArXiv Follow 智能监控测试套件")
    print("============================================================")

    # 运行单元测试
    print("📋 运行单元测试...")

    # 创建测试套件
    test_suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [TestPaperCollector, TestPaperAnalyzer, TestIntelligentMonitor]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 运行集成测试
    print("\n" + "=" * 60)
    run_integration_tests()

    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    print(f"   运行测试: {result.testsRun}")
    print(f"   失败数: {len(result.failures)}")
    print(f"   错误数: {len(result.errors)}")

    if result.failures:
        print("\n❌ 失败的测试:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split(chr(10))[-2]}")

    if result.errors:
        print("\n⚠️ 错误的测试:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split(chr(10))[-2]}")

    success_rate = (
        (result.testsRun - len(result.failures) - len(result.errors))
        / result.testsRun
        * 100
    )
    print(f"\n🎯 成功率: {success_rate:.1f}%")

    if success_rate == 100:
        print("🎉 所有测试通过!")
    elif success_rate >= 80:
        print("✅ 大部分测试通过，系统基本可用")
    else:
        print("⚠️ 多个测试失败，请检查配置和环境")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        import traceback

        traceback.print_exc()

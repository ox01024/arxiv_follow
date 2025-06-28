#!/usr/bin/env python3
"""
LLM翻译服务测试脚本
用于测试OpenRouter API连接和翻译功能
"""

import os
import sys

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

try:
    from src.arxiv_follow.services.translation import (
        TranslationService,
        test_translation_service,
        translate_arxiv_task,
    )
except ImportError as e:
    print(f"❌ 导入翻译服务模块失败: {e}")
    pytest.skip(f"翻译服务模块导入失败: {e}", allow_module_level=True)


class TestTranslationService:
    """翻译服务测试类"""

    @pytest.fixture
    def translator(self):
        """翻译服务实例"""
        return TranslationService()

    def test_service_initialization(self, translator):
        """测试服务初始化"""
        assert translator is not None
        assert hasattr(translator, "is_enabled")

    def test_basic_connection(self):
        """测试基本API连接"""
        if not os.getenv("OPEN_ROUTE_API_KEY"):
            pytest.skip("需要OPEN_ROUTE_API_KEY环境变量")

        success = test_translation_service()
        assert success, "API连接应该成功"

    def test_simple_translation(self, translator):
        """测试简单翻译功能"""
        if not translator.is_enabled():
            pytest.skip("翻译服务未启用，请设置OPEN_ROUTE_API_KEY环境变量")

        result = translator.translate_task_content(
            title="📄 每日论文监控",
            content="今日发现 2 篇新论文，请查看详细信息。",
            source_lang="zh",
            target_lang="en",
        )

        assert result.get("success"), f"翻译应该成功: {result.get('error')}"
        assert "translated_title" in result
        assert "translated_content" in result
        assert result["translated_title"] is not None
        assert result["translated_content"] is not None

    def test_bilingual_translation(self):
        """测试双语翻译功能"""
        if not os.getenv("OPEN_ROUTE_API_KEY"):
            pytest.skip("需要OPEN_ROUTE_API_KEY环境变量")

        test_title = "📄 每日论文监控 - 2025-01-15"
        test_content = """🎉 今日发现 3 篇新论文！

📊 共发现 3 篇论文

📝 详细信息:
监控了 5 位研究者"""

        result = translate_arxiv_task(test_title, test_content, bilingual=True)

        assert result.get("success"), f"双语翻译应该成功: {result.get('error')}"
        assert "bilingual" in result or ("chinese" in result and "english" in result)

    def test_error_handling(self, translator):
        """测试错误处理"""
        # 测试空内容
        result = translator.translate_task_content("", "")
        assert result is not None

        # 测试不支持的语言（应该优雅处理）
        result = translator.translate_task_content(
            title="Test",
            content="Test content",
            source_lang="invalid",
            target_lang="invalid",
        )
        assert result is not None


def test_smart_bilingual_translation():
    """测试智能双语翻译功能（包含英文论文信息）"""
    print("\n🧪 测试4: 智能双语翻译测试")
    print("-" * 40)

    test_title = "📄 每日论文监控 - 2025-01-15"
    test_content = """🎉 今日发现 2 篇新论文！

📊 共发现 2 篇论文

📝 详细信息:
监控了 3 位研究者

📊 论文分布:
• Zhang Wei: 1 篇
  1. **Transformer-based Anomaly Detection in Network Traffic**
     📄 **arXiv:** 2501.12345
     👥 **作者:** Zhang Wei, John Smith, Alice Brown
     📝 **摘要:** This paper presents a novel transformer-based approach for detecting network anomalies in real-time cybersecurity systems. Our method achieves superior performance compared to traditional machine learning approaches.
     
• Li Ming: 1 篇
  1. **Federated Learning with Differential Privacy for Healthcare Data**
     📄 **arXiv:** 2501.12346  
     👥 **作者:** Li Ming, Sarah Johnson, Michael Chen
     📝 **摘要:** We propose a federated learning framework that incorporates differential privacy mechanisms to protect sensitive healthcare data while maintaining model performance.

⏰ 生成时间: 2025-01-15 09:00:15
🤖 由 ArXiv Follow 系统自动生成"""

    # 测试智能翻译模式
    smart_result = translate_arxiv_task(
        test_title, test_content, bilingual=True, smart_mode=True
    )

    if smart_result.get("success"):
        print("✅ 智能双语翻译测试成功")
        print(f"🔧 翻译模式: {smart_result.get('translation_mode', 'unknown')}")

        print("\n📋 中文标题:")
        print(f"   {smart_result['chinese']['title']}")

        print("\n📝 中文内容预览:")
        chinese_content = smart_result["chinese"]["content"]
        print(f"   {chinese_content[:300]}...")

        print("\n📝 英文内容预览:")
        english_content = smart_result["english"]["content"]
        print(f"   {english_content[:300]}...")

        print(f"\n🤖 使用模型: {smart_result.get('model_used')}")

        # 检查中文版本是否正确翻译了论文标题
        if (
            "基于" in chinese_content
            or "变换器" in chinese_content
            or "异常检测" in chinese_content
        ):
            print("✅ 论文标题翻译正确")
        else:
            print("⚠️ 论文标题可能未正确翻译")

        # 检查研究者名字是否保持英文
        if "Zhang Wei" in chinese_content and "Li Ming" in chinese_content:
            print("✅ 研究者名字保持英文")
        else:
            print("⚠️ 研究者名字可能被翻译了")

        return True
    else:
        print(f"❌ 智能双语翻译测试失败: {smart_result.get('error')}")
        return False


def test_complex_content_translation():
    """测试复杂内容翻译"""
    print("\n🧪 测试4: 复杂内容翻译测试")
    print("-" * 40)

    complex_title = "🎯 主题论文搜索 - Machine Learning & Security"
    complex_content = """🔍 搜索结果总览

📊 搜索统计:
• 搜索主题: ["cs.AI", "cs.CR", "machine learning", "cybersecurity"]
• 时间范围: 2025-01-10 至 2025-01-15
• 总计发现: 8 篇相关论文

📝 热门论文:
1. "Adversarial Machine Learning in Cybersecurity: A Comprehensive Survey"
   - 作者: Smith, J. et al.
   - arXiv ID: 2501.12345
   - 发布时间: 2025-01-14
   
2. "Zero-Shot Learning for Network Intrusion Detection"
   - 作者: Zhang, L. & Wang, M.
   - arXiv ID: 2501.12346
   - 发布时间: 2025-01-13

📈 趋势分析:
• 深度学习安全: ↗️ 增长趋势
• 联邦学习隐私: ↗️ 热点领域
• 量子机器学习: ➡️ 稳定关注

🎯 搜索策略:
采用了智能日期回退策略，从当前日期向前搜索至找到相关结果。

⏰ 执行时间: 2025-01-15 14:30:22
🤖 由 ArXiv Follow 自动生成 (版本 v1.2.0)"""

    result = translate_arxiv_task(complex_title, complex_content, bilingual=True)

    if result.get("success"):
        print("✅ 复杂内容翻译测试成功")

        print("\n📋 原始中文标题:")
        print(f"   {complex_title}")

        print("\n📋 英文翻译标题:")
        print(f"   {result['english']['title']}")

        print("\n📝 英文内容节选:")
        english_content = result["english"]["content"]
        lines = english_content.split("\n")[:8]  # 显示前8行
        for line in lines:
            print(f"   {line}")
        print("   ...")

        return True
    else:
        print(f"❌ 复杂内容翻译测试失败: {result.get('error')}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("🎯 OpenRouter翻译服务完整测试套件")
    print("=" * 50)

    tests = [
        test_basic_connection,
        test_simple_translation,
        test_bilingual_translation,
        test_smart_bilingual_translation,
        test_complex_content_translation,
        test_error_handling,
    ]

    passed = 0
    total = len(tests)

    for i, test_func in enumerate(tests, 1):
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️ 测试 {i} 未通过")
        except Exception as e:
            print(f"❌ 测试 {i} 执行时出错: {e}")

    print("\n📊 测试结果总结:")
    print("=" * 50)
    print(f"总测试数: {total}")
    print(f"通过数量: {passed}")
    print(f"成功率: {passed/total*100:.1f}%")

    if passed == total:
        print("🎉 所有测试通过!")
        return True
    else:
        print(f"⚠️ {total - passed} 个测试未通过")
        return False


def check_prerequisites():
    """检查环境变量和依赖"""
    print("🔍 检查运行环境...")

    # 检查环境变量
    api_key = os.getenv("OPEN_ROUTE_API_KEY")
    if not api_key:
        print("❌ 未设置 OPEN_ROUTE_API_KEY 环境变量")
        print("💡 请设置环境变量:")
        print('   export OPEN_ROUTE_API_KEY="your_api_key_here"')
        return False
    else:
        print(f"✅ 找到 OPEN_ROUTE_API_KEY (长度: {len(api_key)})")

    # 检查依赖
    try:
        import httpx

        print("✅ httpx 库可用")
    except ImportError:
        print("❌ httpx 库未安装")
        return False

    return True


if __name__ == "__main__":
    print("🚀 启动OpenRouter翻译服务测试")
    print("=" * 50)

    # 检查前置条件
    if not check_prerequisites():
        print("\n❌ 环境检查失败，无法继续测试")
        sys.exit(1)

    print("\n" + "=" * 50)

    # 运行测试
    success = run_all_tests()

    print("\n" + "=" * 50)

    if success:
        print("🎉 翻译服务测试完成！所有功能正常")
        print("\n💡 接下来可以:")
        print("   1. 将翻译功能集成到滴答清单任务创建中")
        print("   2. 在GitHub Actions中设置 OPEN_ROUTE_API_KEY")
        print("   3. 运行实际的论文监控任务")
        sys.exit(0)
    else:
        print("❌ 部分测试未通过，请检查配置")
        sys.exit(1)

#!/usr/bin/env python3
"""
滴答清单API集成测试脚本
用于测试滴答清单API连接和任务创建功能
"""

import os
import sys
import pytest
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

try:
    from src.arxiv_follow.integrations.dida import (
        DidaIntegration, 
        create_arxiv_task, 
        test_dida_connection
    )
    from src.arxiv_follow.services.translation import test_translation_service
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    pytest.skip(f"模块导入失败: {e}", allow_module_level=True)


class TestDidaIntegration:
    """滴答清单集成测试类"""
    
    @pytest.fixture
    def dida(self):
        """滴答清单集成实例"""
        return DidaIntegration()
    
    def test_service_initialization(self, dida):
        """测试服务初始化"""
        assert dida is not None
        assert hasattr(dida, 'is_enabled')
    
    def test_basic_connection(self):
        """测试基本API连接"""
        if not os.getenv('DIDA_ACCESS_TOKEN'):
            pytest.skip("需要DIDA_ACCESS_TOKEN环境变量")
        
        success = test_dida_connection()
        assert success, "API连接应该成功"
    
    def test_simple_task_creation(self, dida):
        """测试简单任务创建"""
        if not dida.is_enabled():
            pytest.skip("滴答清单API未启用，请设置DIDA_ACCESS_TOKEN环境变量")
        
        result = dida.create_task(
            title="🧪 ArXiv Follow 测试任务",
            content=f"这是一个测试任务，用于验证滴答清单API集成功能。\n\n创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            tags=["测试", "arxiv", "api"]
        )
        
        assert result.get("success"), f"任务创建应该成功: {result.get('error')}"
        assert "task_id" in result or "url" in result
    
    def test_arxiv_task_creation(self):
        """测试ArXiv论文监控任务创建"""
        if not os.getenv('DIDA_ACCESS_TOKEN'):
            pytest.skip("需要DIDA_ACCESS_TOKEN环境变量")
        
        # 测试每日研究者动态监控任务
        result1 = create_arxiv_task(
            report_type="daily",
            summary="今日研究者发布3篇新论文！",
            details="监控了5位研究者\n论文分布:\n• 张三: 2篇\n• 李四: 1篇",
            paper_count=3
        )
        assert result1.get("success"), f"每日任务创建失败: {result1.get('error')}"
        
        # 测试每周研究者动态汇总任务
        result2 = create_arxiv_task(
            report_type="weekly", 
            summary="本周研究者无新论文发布",
            details="监控了5位研究者\n监控周期: 2025-01-01 至 2025-01-07",
            paper_count=0
        )
        assert result2.get("success"), f"每周任务创建失败: {result2.get('error')}"
        
        # 测试主题搜索任务
        result3 = create_arxiv_task(
            report_type="topic",
            summary="主题论文搜索发现10篇论文！\n主题: cs.AI AND cs.CR",
            details="搜索主题: cs.AI AND cs.CR\n使用策略: 智能日期回退",
            paper_count=10
        )
        assert result3.get("success"), f"主题任务创建失败: {result3.get('error')}"
    
    def test_bilingual_task_creation(self):
        """测试双语翻译任务创建"""
        if not os.getenv('DIDA_ACCESS_TOKEN'):
            pytest.skip("需要DIDA_ACCESS_TOKEN环境变量")
        
        # 检查是否有翻译服务API密钥
        try:
            translation_available = test_translation_service()
        except:
            pytest.skip("翻译服务模块不可用")
        
        if not translation_available:
            pytest.skip("翻译服务API密钥未配置")
        
        result = create_arxiv_task(
            report_type="daily",
            summary="今日研究者发布2篇新论文！",
            details="""监控了3位研究者

📊 论文分布:
• Zhang Wei: 1篇
  1. **Deep Learning Approaches for Network Intrusion Detection**
     📄 **arXiv:** 2501.12345

⏰ 执行时间: 2025-01-15 09:00:15""",
            paper_count=2,
            bilingual=True
        )
        
        assert result.get("success"), f"双语任务创建失败: {result.get('error')}"
    
    def test_error_handling(self):
        """测试错误处理"""
        invalid_dida = DidaIntegration(access_token="invalid_token_12345")
        
        result = invalid_dida.create_task(
            title="应该失败的任务",
            content="这个任务应该因为无效token而失败"
        )
        
        assert not result.get("success"), "无效token应该导致失败"


def main():
    """主测试函数"""
    print("🧪 滴答清单API集成测试套件")
    print("=" * 60)
    
    # 检查环境变量
    access_token = os.getenv('DIDA_ACCESS_TOKEN')
    if not access_token:
        print("⚠️  警告: 未设置 DIDA_ACCESS_TOKEN 环境变量")
        print("   部分测试将被跳过或失败")
        print("   请参考README.md获取access token配置方法")
    else:
        print(f"✅ 检测到access token (长度: {len(access_token)})")
    
    print()
    
    # 运行测试
    test_results = []
    
    # 测试1: 基本连接
    test_results.append(test_basic_connection())
    
    # 测试2: 简单任务创建（需要有效token）
    if access_token:
        test_results.append(test_simple_task_creation())
        test_results.append(test_arxiv_task_creation())
        test_results.append(test_bilingual_task_creation())
    else:
        print("\n⏭️  跳过任务创建测试（需要access token）")
        test_results.extend([False, False, False])
    
    # 测试5: 错误处理
    test_results.append(test_error_handling())
    
    # 测试结果汇总
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    test_names = [
        "基本API连接测试",
        "简单任务创建测试", 
        "ArXiv任务创建测试",
        "双语翻译任务创建测试",
        "错误处理测试"
    ]
    
    passed = 0
    for i, (name, result) in enumerate(zip(test_names, test_results), 1):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{i}. {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{len(test_results)} 个测试通过")
    
    if passed == len(test_results):
        print("🎉 所有测试通过！滴答清单API集成正常工作")
        return 0
    elif passed > len(test_results) // 2:
        print("⚠️  部分测试通过，请检查失败的测试项")
        return 1
    else:
        print("❌ 大部分测试失败，请检查配置和网络连接")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
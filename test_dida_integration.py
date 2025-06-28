#!/usr/bin/env python3
"""
滴答清单API集成测试脚本
用于测试滴答清单API连接和任务创建功能
"""

import os
import sys
from datetime import datetime

# 确保能够导入项目模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from dida_integration import (
        DidaIntegration, 
        create_arxiv_task, 
        test_dida_connection
    )
    from translation_service import test_translation_service
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)


def test_basic_connection():
    """测试基本API连接"""
    print("🧪 测试1: 基本API连接测试")
    print("-" * 40)
    
    success = test_dida_connection()
    
    if success:
        print("✅ API连接测试成功")
        return True
    else:
        print("❌ API连接测试失败")
        return False


def test_simple_task_creation():
    """测试简单任务创建"""
    print("\n🧪 测试2: 简单任务创建测试")
    print("-" * 40)
    
    dida = DidaIntegration()
    
    if not dida.is_enabled():
        print("❌ 滴答清单API未启用，请设置DIDA_ACCESS_TOKEN环境变量")
        return False
    
    # 创建测试任务
    result = dida.create_task(
        title="🧪 ArXiv Follow 测试任务",
        content=f"这是一个测试任务，用于验证滴答清单API集成功能。\n\n创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        tags=["测试", "arxiv", "api"]
    )
    
    if result.get("success"):
        print("✅ 简单任务创建成功")
        print(f"   任务ID: {result.get('task_id')}")
        print(f"   任务链接: {result.get('url')}")
        return True
    else:
        print(f"❌ 简单任务创建失败: {result.get('error')}")
        return False


def test_arxiv_task_creation():
    """测试ArXiv论文监控任务创建"""
    print("\n🧪 测试3: ArXiv论文监控任务创建测试")
    print("-" * 40)
    
    # 测试每日研究者动态监控任务
    print("📄 测试每日研究者动态监控任务...")
    result1 = create_arxiv_task(
        report_type="daily",
        summary="今日研究者发布3篇新论文！",
        details="监控了5位研究者\n论文分布:\n• 张三: 2篇\n• 李四: 1篇",
        paper_count=3
    )
    
    if result1.get("success"):
        print("✅ 每日研究者动态监控任务创建成功")
    else:
        print(f"❌ 每日研究者动态监控任务创建失败: {result1.get('error')}")
    
    # 测试每周研究者动态汇总任务
    print("\n📚 测试每周研究者动态汇总任务...")
    result2 = create_arxiv_task(
        report_type="weekly", 
        summary="本周研究者无新论文发布",
        details="监控了5位研究者\n监控周期: 2025-01-01 至 2025-01-07",
        paper_count=0
    )
    
    if result2.get("success"):
        print("✅ 每周研究者动态汇总任务创建成功")
    else:
        print(f"❌ 每周研究者动态汇总任务创建失败: {result2.get('error')}")
    
    # 测试主题搜索任务
    print("\n🎯 测试主题搜索任务...")
    result3 = create_arxiv_task(
        report_type="topic",
        summary="主题论文搜索发现10篇论文！\n主题: cs.AI AND cs.CR",
        details="搜索主题: cs.AI AND cs.CR\n使用策略: 智能日期回退\n发现论文:\n1. GPT-4 在网络安全中的应用\n2. 基于深度学习的恶意软件检测",
        paper_count=10
    )
    
    if result3.get("success"):
        print("✅ 主题搜索任务创建成功")
    else:
        print(f"❌ 主题搜索任务创建失败: {result3.get('error')}")
    
    # 统计成功数量
    success_count = sum([
        result1.get("success", False),
        result2.get("success", False), 
        result3.get("success", False)
    ])
    
    print(f"\n📊 ArXiv任务创建测试结果: {success_count}/3 成功")
    return success_count == 3


def test_bilingual_task_creation():
    """测试双语翻译任务创建"""
    print("\n🧪 测试4: 双语翻译任务创建测试")
    print("-" * 40)
    
    # 检查是否有翻译服务API密钥
    try:
        translation_available = test_translation_service()
    except:
        print("⚠️ 翻译服务模块不可用，跳过双语测试")
        return True
    
    if not translation_available:
        print("⚠️ 翻译服务API密钥未配置，跳过双语测试")
        print("💡 设置 OPEN_ROUTE_API_KEY 环境变量以启用双语翻译测试")
        return True
    
    # 测试智能双语任务创建（包含英文论文信息）
    print("🌐 测试智能双语任务创建...")
    result = create_arxiv_task(
        report_type="daily",
        summary="今日研究者发布2篇新论文！",
        details="""监控了3位研究者

📊 论文分布:
• Zhang Wei: 1篇
  1. **Deep Learning Approaches for Network Intrusion Detection**
     📄 **arXiv:** 2501.12345
     👥 **作者:** Zhang Wei, John Smith, Alice Brown
     📝 **摘要:** This paper presents a comprehensive survey of deep learning techniques for network intrusion detection systems.
     
• Li Ming: 1篇  
  1. **Federated Learning with Privacy Protection Mechanisms**
     📄 **arXiv:** 2501.12346
     👥 **作者:** Li Ming, Sarah Johnson
     📝 **摘要:** We propose a novel federated learning framework that incorporates advanced privacy protection mechanisms for distributed machine learning.

⏰ 执行时间: 2025-01-15 09:00:15""",
        paper_count=2,
        bilingual=True
    )
    
    if result.get("success"):
        print("✅ 双语任务创建成功")
        if result.get("translation_success"):
            print(f"✅ 翻译成功，使用模型: {result.get('model_used')}")
        else:
            print(f"⚠️ 翻译失败，但任务创建成功: {result.get('translation_error')}")
        
        if result.get("task_id"):
            print(f"   任务ID: {result['task_id']}")
        if result.get("url"):
            print(f"   任务链接: {result['url']}")
        return True
    else:
        print(f"❌ 双语任务创建失败: {result.get('error')}")
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n🧪 测试4: 错误处理测试")
    print("-" * 40)
    
    # 创建一个使用无效token的客户端
    invalid_dida = DidaIntegration(access_token="invalid_token_12345")
    
    result = invalid_dida.create_task(
        title="应该失败的任务",
        content="这个任务应该因为无效token而失败"
    )
    
    if not result.get("success"):
        print("✅ 错误处理测试成功 - 无效token正确返回失败")
        return True
    else:
        print("❌ 错误处理测试失败 - 无效token应该返回失败")
        return False


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
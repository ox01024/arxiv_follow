#!/usr/bin/env python3
"""
LLM翻译服务演示脚本
展示OpenRouter API翻译功能和滴答清单双语任务创建
"""

import os
import sys
from datetime import datetime

# 确保能够导入项目模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    print("=" * 50)
    
    # 检查必要的环境变量
    env_vars = {
        "OPEN_ROUTE_API_KEY": os.getenv('OPEN_ROUTE_API_KEY'),
        "DIDA_ACCESS_TOKEN": os.getenv('DIDA_ACCESS_TOKEN')
    }
    
    all_configured = True
    
    for var_name, value in env_vars.items():
        if value:
            masked_value = value[:8] + "..." if len(value) > 8 else value  # 测试展示截断
            print(f"✅ {var_name}: {masked_value}")
        else:
            print(f"❌ {var_name}: 未设置")
            all_configured = False
    
    if not all_configured:
        print("\n💡 配置说明:")
        print("   export OPEN_ROUTE_API_KEY=\"your_openrouter_api_key\"")
        print("   export DIDA_ACCESS_TOKEN=\"your_dida_access_token\"")
        print("\n📚 详细配置指南请查看: docs/translation-guide.md")
    
    return all_configured


def demo_translation_service():
    """演示翻译服务功能"""
    print("\n🌐 翻译服务功能演示")
    print("=" * 50)
    
    try:
        from translation_service import (
            TranslationService, 
            translate_arxiv_task, 
            test_translation_service
        )
    except ImportError as e:
        print(f"❌ 无法导入翻译服务: {e}")
        return False
    
    # 1. 测试API连接
    print("🧪 1. 测试OpenRouter API连接...")
    if not test_translation_service():
        print("❌ 翻译服务连接失败，请检查API密钥")
        return False
    
    # 2. 演示简单翻译
    print("\n🧪 2. 演示简单翻译功能...")
    translator = TranslationService()
    
    simple_result = translator.translate_task_content(
        title="📄 研究者动态日报",
        content="今日研究者发布了2篇高质量的机器学习论文，值得深入研究。",
        source_lang="zh",
        target_lang="en"
    )
    
    if simple_result.get("success"):
        print("✅ 简单翻译成功:")
        print(f"   原标题: 📄 论文监控日报")
        print(f"   译标题: {simple_result['translated_title']}")
        print(f"   原内容: 今日研究者发布了2篇高质量的机器学习论文，值得深入研究。")
        print(f"   译内容: {simple_result['translated_content']}")
    else:
        print(f"❌ 简单翻译失败: {simple_result.get('error')}")
        return False
    
    # 3. 演示双语翻译
    print("\n🧪 3. 演示双语翻译功能...")
    
    demo_title = "📄 每日论文监控 - 2025-01-15"
    demo_content = """🎉 今日研究者发布 2 篇新论文！

📊 共发现 2 篇论文

📝 详细信息:
监控了 3 位研究者

📊 论文分布:
• Zhang Wei: 1 篇
  1. Transformer-based Anomaly Detection in Network Traffic
• Li Ming: 1 篇
  1. Federated Learning with Differential Privacy

⏰ 生成时间: 2025-01-15 14:30:22
🤖 由 ArXiv Follow 系统自动生成"""

    bilingual_result = translate_arxiv_task(demo_title, demo_content, bilingual=True)
    
    if bilingual_result.get("success"):
        print("✅ 双语翻译成功:")
        print(f"\n📋 双语标题:")
        print(f"{bilingual_result['bilingual']['title']}")
        
        print(f"\n📝 双语内容预览 (前300字符):")
        content_preview = bilingual_result['bilingual']['content'][:300]
        print(f"{content_preview}...")
        
        print(f"\n🤖 使用模型: {bilingual_result.get('model_used')}")
        return bilingual_result
    else:
        print(f"❌ 双语翻译失败: {bilingual_result.get('error')}")
        return False


def demo_dida_integration(translation_result=None):
    """演示滴答清单集成功能"""
    print("\n📝 滴答清单集成演示")
    print("=" * 50)
    
    try:
        from dida_integration import (
            DidaIntegration,
            create_arxiv_task,
            test_dida_connection
        )
    except ImportError as e:
        print(f"❌ 无法导入滴答清单集成: {e}")
        return False
    
    # 1. 测试滴答清单连接
    print("🧪 1. 测试滴答清单API连接...")
    if not test_dida_connection():
        print("❌ 滴答清单连接失败，请检查Access Token")
        return False
    
    # 2. 创建普通任务
    print("\n🧪 2. 创建普通中文任务...")
    normal_result = create_arxiv_task(
        report_type="daily",
        summary="演示任务：今日研究者发布1篇新论文",
        details="这是一个演示任务，用于展示基本的任务创建功能。",
        paper_count=1,
        bilingual=False
    )
    
    if normal_result.get("success"):
        print("✅ 普通任务创建成功")
        print(f"   任务ID: {normal_result.get('task_id')}")
        if normal_result.get('url'):
            print(f"   任务链接: {normal_result['url']}")
    else:
        print(f"❌ 普通任务创建失败: {normal_result.get('error')}")
    
    # 3. 创建双语任务
    print("\n🧪 3. 创建双语翻译任务...")
    bilingual_task_result = create_arxiv_task(
        report_type="daily",
        summary="演示任务：今日研究者发布2篇高质量论文！",
        details="""监控了3位顶级研究者

📊 论文分布:
• 张三教授: 1篇 - 深度学习在网络安全中的应用
• 李四博士: 1篇 - 联邦学习隐私保护机制研究

这些论文都来自顶级会议，具有重要的学术价值和实际应用前景。""",
        paper_count=2,
        bilingual=True
    )
    
    if bilingual_task_result.get("success"):
        print("✅ 双语任务创建成功")
        print(f"   任务ID: {bilingual_task_result.get('task_id')}")
        if bilingual_task_result.get('url'):
            print(f"   任务链接: {bilingual_task_result['url']}")
        
        if bilingual_task_result.get("translation_success"):
            print(f"✅ 翻译成功，使用模型: {bilingual_task_result.get('model_used')}")
        else:
            print(f"⚠️ 翻译失败，但任务创建成功: {bilingual_task_result.get('translation_error')}")
    else:
        print(f"❌ 双语任务创建失败: {bilingual_task_result.get('error')}")
    
    return normal_result.get("success") and bilingual_task_result.get("success")


def demo_full_workflow():
    """演示完整的工作流程"""
    print("\n🚀 完整工作流程演示")
    print("=" * 50)
    
    # 模拟论文监控结果
    mock_papers = {
        "Zhang Wei": [
            {
                "title": "Adversarial Machine Learning: A Comprehensive Survey",
                "arxiv_id": "2501.12345",
                "url": "https://arxiv.org/abs/2501.12345",
                "authors": ["Zhang Wei", "Li Ming", "Wang Lei"],
                "abstract": "This paper provides a comprehensive survey of adversarial machine learning techniques...",
                "subjects": ["cs.AI", "cs.CR", "cs.LG"]
            }
        ],
        "Li Ming": [
            {
                "title": "Privacy-Preserving Federated Learning with Differential Privacy",
                "arxiv_id": "2501.12346", 
                "url": "https://arxiv.org/abs/2501.12346",
                "authors": ["Li Ming", "Chen Hua"],
                "abstract": "We propose a novel approach for privacy-preserving federated learning...",
                "subjects": ["cs.LG", "cs.CR"]
            }
        ]
    }
    
    # 构建详细的任务内容
    summary = "🎉 每日监控发现 2 篇高质量论文！"
    
    details_lines = [
        "👥 监控研究者: 5 位",
        "📅 监控日期: 2025-01-15",
        "",
        "## 📊 发现论文详情",
        ""
    ]
    
    paper_count = 0
    for author, papers in mock_papers.items():
        details_lines.append(f"### 👨‍🔬 {author} ({len(papers)} 篇)")
        
        for i, paper in enumerate(papers, 1):
            paper_count += 1
            title = paper['title']
            arxiv_id = paper['arxiv_id']
            url = paper['url']
            authors = ", ".join(paper['authors'])
            subjects = ", ".join([f"`{s}`" for s in paper['subjects']])
            
            details_lines.extend([
                f"",
                f"**{i}. [{title}]({url})**",
                f"📄 **arXiv:** `{arxiv_id}`",
                f"👥 **作者:** {authors}",
                f"🏷️ **领域:** {subjects}",
                f"📝 **摘要:** {paper['abstract'][:100]}...",  # 测试展示截断
                "---"
            ])
    
    details_lines.extend([
        "",
        f"⏰ **执行时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ])
    
    details = "\n".join(details_lines)
    
    # 创建双语任务
    print("📝 模拟完整的论文监控工作流程...")
    print("   1. 论文搜索与解析 ✅")
    print("   2. 内容格式化 ✅")
    print("   3. LLM翻译处理 ⏳")
    print("   4. 滴答清单任务创建 ⏳")
    
    try:
        from dida_integration import create_arxiv_task
        
        result = create_arxiv_task(
            report_type="daily",
            summary=summary,
            details=details,
            paper_count=paper_count,
            bilingual=True
        )
        
        if result.get("success"):
            print("\n✅ 完整工作流程演示成功！")
            print(f"   📋 任务ID: {result.get('task_id')}")
            if result.get('url'):
                print(f"   🔗 任务链接: {result['url']}")
            
            if result.get("translation_success"):
                print(f"   🌐 翻译成功: {result.get('model_used')}")
            else:
                print(f"   ⚠️ 翻译失败: {result.get('translation_error')}")
            
            return True
        else:
            print(f"\n❌ 工作流程失败: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ 工作流程执行错误: {e}")
        return False


def main():
    """主函数"""
    print("🎯 ArXiv Follow LLM翻译服务演示")
    print("=" * 60)
    print(f"⏰ 演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查环境配置
    if not check_environment():
        print("\n❌ 环境配置不完整，部分演示将被跳过")
        print("📚 请查看 docs/translation-guide.md 了解配置方法")
    
    results = {}
    
    # 演示翻译服务
    translation_result = demo_translation_service()
    results['translation'] = bool(translation_result)
    
    # 演示滴答清单集成
    dida_result = demo_dida_integration(translation_result)
    results['dida'] = dida_result
    
    # 演示完整工作流程
    workflow_result = demo_full_workflow()
    results['workflow'] = workflow_result
    
    # 总结
    print("\n📊 演示结果总结")
    print("=" * 60)
    
    demo_items = [
        ("翻译服务功能", results['translation']),
        ("滴答清单集成", results['dida']),
        ("完整工作流程", results['workflow'])
    ]
    
    passed = 0
    for item_name, success in demo_items:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"• {item_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 演示结果: {passed}/{len(demo_items)} 项成功")
    
    if passed == len(demo_items):
        print("🎉 所有功能演示成功！系统集成完整且正常工作")
        print("\n💡 接下来您可以:")
        print("   1. 运行 daily_papers.py 进行每日论文监控")
        print("   2. 运行 weekly_papers.py 生成周报")
        print("   3. 运行 topic_papers.py 进行主题搜索")
        print("   4. 在 GitHub Actions 中设置定时任务自动运行")
        return 0
    elif passed > 0:
        print("⚠️ 部分功能正常，请检查失败的项目")
        return 1
    else:
        print("❌ 演示未成功，请检查配置和网络连接")
        return 2


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ 演示被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 演示执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 
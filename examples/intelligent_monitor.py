#!/usr/bin/env python3
"""
智能论文监控演示脚本 - 展示完整的论文采集、分析和报告生成功能
"""

import os
import sys
from datetime import datetime

# 导入模块
try:
    from paper_collector import collect_paper_content
    from paper_analyzer import analyze_paper, PaperAnalyzer
    from intelligent_monitor import create_intelligent_monitor
    from config import PAPER_ANALYSIS_CONFIG
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)


def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查环境变量
    env_vars = {
        "OPEN_ROUTE_API_KEY": os.getenv('OPEN_ROUTE_API_KEY'),
        "DIDA_ACCESS_TOKEN": os.getenv('DIDA_ACCESS_TOKEN')
    }
    
    all_configured = True
    for var_name, var_value in env_vars.items():
        if var_value:
            print(f"✅ {var_name}: {'*' * 10}...{var_value[-4:]}")  # 测试展示截断
        else:
            print(f"❌ {var_name}: 未设置")
            all_configured = False
    
    if not all_configured:
        print("\n💡 配置说明:")
        print("   export OPEN_ROUTE_API_KEY=\"your_openrouter_api_key\"")
        print("   export DIDA_ACCESS_TOKEN=\"your_dida_access_token\"")
        print("\n📚 详细配置指南请查看: docs/translation-guide.md")
        return False
    
    return True


def demo_paper_collection():
    """演示论文内容采集功能"""
    print("\n📄 演示论文内容采集功能")
    print("="*50)
    
    # 使用一个真实的arXiv ID进行测试
    test_arxiv_id = "2312.11805"  # 一个关于Transformer的论文
    
    print(f"🧪 采集论文: {test_arxiv_id}")
    
    try:
        result = collect_paper_content(test_arxiv_id)
        
        if 'error' in result:
            print(f"❌ 采集失败: {result['error']}")
            return None
        
        print("✅ 采集成功!")
        print(f"📋 标题: {result.get('title', 'N/A')}")
        print(f"👥 作者数: {len(result.get('authors', []))}")
        print(f"📖 摘要长度: {len(result.get('abstract', ''))}")
        print(f"🌐 HTML版本: {'是' if result.get('has_html_version') else '否'}")
        print(f"📊 内容源: {result.get('content_sources', [])}")
        
        if result.get('sections'):
            print(f"📑 发现章节数: {len(result['sections'])}")
            print("   前3个章节:")
            for i, section in enumerate(result['sections'][:3]):
                print(f"     {i+1}. {section['title']} (级别 {section['level']})")
        
        return result
        
    except Exception as e:
        print(f"❌ 采集异常: {e}")
        return None


def demo_paper_analysis(paper_data):
    """演示论文分析功能"""
    print("\n🧠 演示论文分析功能")
    print("="*50)
    
    if not paper_data:
        print("⚠️ 没有论文数据可供分析")
        return None
    
    analyzer = PaperAnalyzer()
    
    if not analyzer.is_enabled():
        print("❌ 分析器未启用，请检查 OPEN_ROUTE_API_KEY 环境变量")
        return None
    
    print("🤖 使用LLM分析论文...")
    
    try:
        # 1. 重要性分析
        print("\n📊 1. 重要性分析...")
        sig_result = analyzer.analyze_paper_significance(paper_data)
        
        if sig_result.get('success'):
            print("✅ 重要性分析完成")
            print("内容预览:")
            print(sig_result.get('content', '')[:300] + "...")  # 测试展示截断
        else:
            print(f"❌ 重要性分析失败: {sig_result.get('error')}")
        
        # 2. 技术分析
        print("\n🔧 2. 技术分析...")
        tech_result = analyzer.analyze_paper_technical_details(paper_data)
        
        if tech_result.get('success'):
            print("✅ 技术分析完成")
            print("内容预览:")
            print(tech_result.get('content', '')[:300] + "...")  # 测试展示截断
        else:
            print(f"❌ 技术分析失败: {tech_result.get('error')}")
        
        # 3. 综合报告
        print("\n📋 3. 综合报告生成...")
        report_result = analyzer.generate_comprehensive_report(paper_data)
        
        if report_result.get('success'):
            print("✅ 综合报告生成成功")
            print("\n📝 完整报告:")
            print("-" * 60)
            print(report_result.get('report_content', ''))
            print("-" * 60)
        else:
            print(f"❌ 综合报告生成失败: {report_result.get('error')}")
        
        return report_result
        
    except Exception as e:
        print(f"❌ 分析异常: {e}")
        return None


def demo_intelligent_integration():
    """演示智能集成功能"""
    print("\n🚀 演示智能集成功能")
    print("="*50)
    
    # 创建智能监控器
    monitor = create_intelligent_monitor()
    
    print(f"内容采集: {'启用' if monitor.is_collection_enabled() else '禁用'}")
    print(f"LLM分析: {'启用' if monitor.is_analysis_enabled() else '禁用'}")
    
    # 准备测试数据
    test_papers = [
        {
            "arxiv_id": "2312.11805",
            "title": "Transformer-based Network Traffic Anomaly Detection",
            "authors": ["Zhang Wei", "Li Ming", "Wang Qiang"],
            "abstract": "This paper presents a novel approach for detecting anomalies in network traffic using transformer architectures...",
            "url": "https://arxiv.org/abs/2312.11805"
        },
        {
            "arxiv_id": "2312.11806", 
            "title": "Federated Learning with Privacy Protection",
            "authors": ["Liu Yang", "Chen Jun"],
            "abstract": "We propose a federated learning framework that provides strong privacy guarantees...",
            "url": "https://arxiv.org/abs/2312.11806"
        }
    ]
    
    print(f"\n🧪 测试智能处理 {len(test_papers)} 篇论文...")
    
    try:
        # 测试智能任务创建
        result = monitor.create_intelligent_dida_task(
            report_type="demo",
            title="智能监控演示",
            papers=test_papers
        )
        
        if result.get('success'):
            print("✅ 智能任务创建成功!")
            print(f"📋 任务ID: {result.get('task_id')}")
            print(f"🔗 任务链接: {result.get('task_url')}")
            
            intelligent_features = result.get('intelligent_features', {})
            print("\n🤖 智能功能状态:")
            print(f"   内容采集: {'✅' if intelligent_features.get('content_collection') else '❌'}")
            print(f"   LLM分析: {'✅' if intelligent_features.get('llm_analysis') else '❌'}")
            
            if result.get('translation_info'):
                print(f"   双语翻译: {'✅' if result['translation_info'].get('success') else '❌'}")
        
        else:
            print(f"❌ 智能任务创建失败: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ 智能集成异常: {e}")
        return None


def demo_configuration_guide():
    """演示配置指南"""
    print("\n⚙️ 配置指南")
    print("="*50)
    
    print("📝 论文分析功能配置:")
    print(f"   enable_analysis: {PAPER_ANALYSIS_CONFIG.get('enable_analysis')}")
    print(f"   enable_content_collection: {PAPER_ANALYSIS_CONFIG.get('enable_content_collection')}")
    print(f"   analysis_mode: {PAPER_ANALYSIS_CONFIG.get('analysis_mode')}")
    print(f"   max_papers_per_batch: {PAPER_ANALYSIS_CONFIG.get('max_papers_per_batch')}")
    
    print("\n💡 启用智能功能:")
    print("1. 设置环境变量 OPEN_ROUTE_API_KEY")
    print("2. 在 config.py 中设置:")
    print("   PAPER_ANALYSIS_CONFIG['enable_analysis'] = True")
    print("   PAPER_ANALYSIS_CONFIG['enable_content_collection'] = True")
    
    print("\n🎯 分析模式说明:")
    print("   - significance: 重要性分析")
    print("   - technical: 技术分析")
    print("   - comprehensive: 综合分析（推荐）")


def main():
    """主演示流程"""
    print("🎯 ArXiv Follow 智能论文监控演示")
    print("============================================================")
    print(f"⏰ 演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境配置不完整，部分功能将无法演示")
        print("继续演示基础功能...")
    
    # 演示配置指南
    demo_configuration_guide()
    
    # 演示论文采集
    paper_data = demo_paper_collection()
    
    # 演示论文分析（如果有数据且API密钥可用）
    if paper_data and os.getenv('OPEN_ROUTE_API_KEY'):
        demo_paper_analysis(paper_data)
    else:
        print("\n⚠️ 跳过论文分析演示（缺少论文数据或API密钥）")
    
    # 演示智能集成
    if os.getenv('DIDA_ACCESS_TOKEN'):
        demo_intelligent_integration()
    else:
        print("\n⚠️ 跳过智能集成演示（缺少滴答清单token）")
    
    print("\n🎉 演示完成!")
    print("="*60)
    print("💡 接下来可以:")
    print("   1. 启用配置文件中的智能功能")
    print("   2. 运行 daily_papers.py 进行每日监控")
    print("   3. 运行 topic_papers.py 进行主题搜索")
    print("   4. 查看文档 docs/translation-guide.md 了解更多")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出现异常: {e}")
        import traceback
        traceback.print_exc() 
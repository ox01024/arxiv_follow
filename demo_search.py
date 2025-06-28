#!/usr/bin/env python3
"""
演示脚本 - 展示主题搜索功能的使用方法
"""

from topic_papers import fetch_papers_by_topic, display_search_results

def main():
    """演示主要功能"""
    print("🎯 arXiv主题搜索演示")
    print("="*50)
    
    # 演示cs.AI + cs.CR搜索
    print("📚 演示搜索: cs.AI AND cs.CR (人工智能 + 计算机安全)")
    results = fetch_papers_by_topic(["cs.AI", "cs.CR"], date_from=None, date_to=None)
    
    if results['papers']:
        print(f"✅ 成功找到 {len(results['papers'])} 篇论文")
        print(f"🎯 使用策略: {results['search_strategy_used']}")
        
        # 显示前5篇论文的详细信息
        for i, paper in enumerate(results['papers'][:5], 1):
            title = paper.get('title', paper['arxiv_id'])
            print(f"  {i}. {title}")
            
            # 显示作者
            if paper.get('authors'):
                authors_str = ", ".join(paper['authors'][:2])
                if len(paper['authors']) > 2:
                    authors_str += f" 等{len(paper['authors'])}位作者"
                print(f"     👥 作者: {authors_str}")
            
            # 显示ArXiv链接
            if paper.get('url'):
                print(f"     🔗 链接: {paper['url']}")
        
        if len(results['papers']) > 5:
            print(f"  ... 还有 {len(results['papers'])-5} 篇论文（运行完整脚本查看全部）")
    else:
        print("❌ 未找到相关论文")
    
    print(f"\n💡 使用方法:")
    print(f"  uv run python topic_papers.py")
    print(f"  uv run python topic_papers.py 'cs.AI,cs.LG'")

if __name__ == "__main__":
    main() 
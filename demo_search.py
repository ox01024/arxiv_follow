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
        
        # 显示前3篇
        for i, paper in enumerate(results['papers'][:3], 1):
            title = paper.get('title', paper['arxiv_id'])
            if len(title) > 60:
                title = title[:60] + "..."
            print(f"  {i}. {title}")
    else:
        print("❌ 未找到相关论文")
    
    print(f"\n💡 使用方法:")
    print(f"  uv run python topic_papers.py")
    print(f"  uv run python topic_papers.py 'cs.AI,cs.LG'")

if __name__ == "__main__":
    main() 
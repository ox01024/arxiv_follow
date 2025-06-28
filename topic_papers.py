#!/usr/bin/env python3
"""
基于主题的论文监控脚本 - 搜索特定主题领域的最新论文
支持智能日期回退和多种搜索模式
"""

import httpx
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from urllib.parse import urlencode
import json


def build_topic_search_url(
    topics: List[str], 
    date_from: Optional[str] = None, 
    date_to: Optional[str] = None,
    classification: str = "computer_science",
    field: str = "all",
    size: int = 50
) -> str:
    """
    构建基于主题的 arXiv 高级搜索 URL
    
    Args:
        topics: 主题列表 (如 ["cs.AI", "cs.CR"])
        date_from: 开始日期 (YYYY-MM-DD), None 表示不限制
        date_to: 结束日期 (YYYY-MM-DD), None 表示不限制
        classification: 分类领域
        field: 搜索字段
        size: 结果数量
        
    Returns:
        arXiv 搜索 URL
    """
    base_url = "https://arxiv.org/search/advanced"
    
    params = {
        'advanced': '',
        'abstracts': 'show',
        'size': str(size),
        'order': '-announced_date_first'
    }
    
    # 添加主题搜索条件
    for i, topic in enumerate(topics):
        params[f'terms-{i}-operator'] = 'AND'
        params[f'terms-{i}-term'] = topic
        params[f'terms-{i}-field'] = field
    
    # 添加分类
    if classification == "computer_science":
        params['classification-computer_science'] = 'y'
    elif classification == "physics":
        params['classification-physics_archives'] = 'all'
    
    params['classification-include_cross_list'] = 'include'
    
    # 添加日期条件
    if date_from and date_to:
        params['date-filter_by'] = 'date_range'
        params['date-from_date'] = date_from
        params['date-to_date'] = date_to
        params['date-date_type'] = 'submitted_date'
    else:
        params['date-filter_by'] = 'all_dates'
    
    params['date-year'] = ''
    
    return f"{base_url}?{urlencode(params)}"


def parse_arxiv_search_results(html_content: str) -> List[Dict[str, Any]]:
    """
    解析 arXiv 搜索结果页面
    
    Args:
        html_content: HTML 内容
        
    Returns:
        论文列表
    """
    papers = []
    
    # 检查是否有结果
    if "Sorry, your query returned no results" in html_content:
        return papers
    
    # 提取结果总数
    total_pattern = r'Showing 1–\d+ of ([\d,]+) results'
    total_match = re.search(total_pattern, html_content)
    total_count = 0
    if total_match:
        total_count = int(total_match.group(1).replace(',', ''))
    
    # 更精确的解析策略 - 基于实际HTML结构
    # 查找论文列表的容器，通常是 <ol> 或类似的结构
    
    # 模式1: 寻找论文条目 - 匹配arXiv ID开头的论文
    # 基于用户提供的搜索结果格式：1. arXiv:2506.21106 [pdf, ps, other] cs.CR cs.AI
    paper_pattern = r'(\d+)\.\s*arXiv:(\d{4}\.\d{4,5})\s*\[([^\]]+)\]\s*((?:cs\.\w+\s*)+)(.*?)(?=\d+\.\s*arXiv:|\n\n|\Z)'
    paper_matches = re.findall(paper_pattern, html_content, re.DOTALL)
    
    if not paper_matches:
        # 模式2: 更宽泛的匹配模式
        paper_pattern = r'arXiv:(\d{4}\.\d{4,5})\s*\[([^\]]+)\]\s*(.*?)(?=arXiv:|\Z)'
        alt_matches = re.findall(paper_pattern, html_content, re.DOTALL)
        
        for arxiv_id, file_types, content in alt_matches:
            paper = {
                'arxiv_id': arxiv_id,
                'url': f"https://arxiv.org/abs/{arxiv_id}",
                'file_types': [t.strip() for t in file_types.split(',')],
                'total_results': total_count
            }
            
            # 解析内容
            _parse_paper_content(paper, content)
            
            if paper.get('title'):
                papers.append(paper)
    else:
        # 使用模式1的结果
        for seq_num, arxiv_id, file_types, subjects, content in paper_matches:
            paper = {
                'arxiv_id': arxiv_id,
                'url': f"https://arxiv.org/abs/{arxiv_id}",
                'subjects': [s.strip() for s in subjects.split() if s.strip()],
                'file_types': [t.strip() for t in file_types.split(',')],
                'sequence_number': int(seq_num),
                'total_results': total_count
            }
            
            # 解析内容
            _parse_paper_content(paper, content)
            
            if paper.get('title'):
                papers.append(paper)
    
    # 如果以上都没找到，尝试基于HTML标签的解析
    if not papers:
        papers = _parse_html_structure(html_content, total_count)
    
    return papers


def _parse_paper_content(paper: Dict[str, Any], content: str) -> None:
    """
    解析论文内容，提取标题、作者、摘要等信息
    
    Args:
        paper: 论文字典（会被修改）
        content: 内容字符串
    """
    # 提取标题 - 通常在最开始
    title_patterns = [
        r'^\s*([^\n]+?)(?:\s*Authors?:|\s*Abstract:|\n\s*\n)',
        r'^\s*([^\n]{10,200}?)(?:\s*Authors?:)',
        r'^\s*([^\n]+)',
    ]
    
    for pattern in title_patterns:
        title_match = re.search(pattern, content.strip(), re.MULTILINE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # 清理标题
            title = re.sub(r'▽\s*More|△\s*Less', '', title)
            title = re.sub(r'\s+', ' ', title).strip()
            if len(title) > 10 and not title.lower().startswith('authors'):
                paper['title'] = title
                break
    
    # 提取作者
    authors_patterns = [
        r'Authors?:\s*([^\n]+?)(?:\s*Abstract:|\s*Submitted|\n\s*\n)',
        r'Authors?:\s*([^\n]+)',
    ]
    
    for pattern in authors_patterns:
        authors_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if authors_match:
            authors_text = authors_match.group(1).strip()
            # 清理并分割作者
            authors_text = re.sub(r'▽\s*More|△\s*Less', '', authors_text)
            authors = [author.strip() for author in re.split(r',|;', authors_text) if author.strip()]
            paper['authors'] = authors
            break
    
    # 提取摘要
    abstract_patterns = [
        r'Abstract:\s*(.*?)(?:\s*Submitted|\s*Comments|\n\s*\n|\Z)',
        r'Abstract:\s*(.*?)(?=△\s*Less|\Z)',
    ]
    
    for pattern in abstract_patterns:
        abstract_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if abstract_match:
            abstract = abstract_match.group(1).strip()
            # 清理摘要
            abstract = re.sub(r'▽\s*More|△\s*Less', '', abstract)
            abstract = re.sub(r'\s+', ' ', abstract).strip()
            if len(abstract) > 20:
                paper['abstract'] = abstract
            break
    
    # 提取提交日期
    submitted_patterns = [
        r'Submitted\s+(\d{1,2}\s+\w+,?\s+\d{4})',
        r'originally announced\s+(\w+\s+\d{4})',
    ]
    
    for pattern in submitted_patterns:
        submitted_match = re.search(pattern, content, re.IGNORECASE)
        if submitted_match:
            paper['submitted_date'] = submitted_match.group(1)
            break


def _parse_html_structure(html_content: str, total_count: int) -> List[Dict[str, Any]]:
    """
    基于HTML结构解析论文信息
    
    Args:
        html_content: HTML 内容
        total_count: 总结果数
        
    Returns:
        论文列表
    """
    papers = []
    
    # 寻找论文列表容器
    list_patterns = [
        r'<ol[^>]*class="[^"]*breathe[^"]*"[^>]*>(.*?)</ol>',
        r'<ol[^>]*>(.*?)</ol>',
        r'<div[^>]*class="[^"]*results[^"]*"[^>]*>(.*?)</div>',
    ]
    
    list_content = None
    for pattern in list_patterns:
        list_match = re.search(pattern, html_content, re.DOTALL)
        if list_match:
            list_content = list_match.group(1)
            break
    
    if list_content:
        # 在列表中查找论文项
        item_pattern = r'<li[^>]*>(.*?)</li>'
        item_matches = re.findall(item_pattern, list_content, re.DOTALL)
        
        for item_content in item_matches:
            # 提取 arXiv ID
            id_match = re.search(r'arXiv:(\d{4}\.\d{4,5})', item_content)
            if id_match:
                arxiv_id = id_match.group(1)
                paper = {
                    'arxiv_id': arxiv_id,
                    'url': f"https://arxiv.org/abs/{arxiv_id}",
                    'total_results': total_count
                }
                
                # 提取标题
                title_patterns = [
                    r'<p[^>]*class="[^"]*title[^"]*"[^>]*>.*?<a[^>]*>(.*?)</a>',
                    r'<a[^>]*href="/abs/[^"]*"[^>]*>(.*?)</a>',
                ]
                
                for pattern in title_patterns:
                    title_match = re.search(pattern, item_content, re.DOTALL)
                    if title_match:
                        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                        paper['title'] = title
                        break
                
                # 提取作者
                authors_pattern = r'<p[^>]*class="[^"]*authors[^"]*"[^>]*>(.*?)</p>'
                authors_match = re.search(authors_pattern, item_content, re.DOTALL)
                if authors_match:
                    authors_html = authors_match.group(1)
                    authors = re.findall(r'<a[^>]*>(.*?)</a>', authors_html)
                    if authors:
                        paper['authors'] = [re.sub(r'<[^>]+>', '', author).strip() for author in authors]
                
                if paper.get('title'):
                    papers.append(paper)
    
    return papers


def fetch_papers_by_topic(
    topics: List[str], 
    date_from: Optional[str] = None, 
    date_to: Optional[str] = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    根据主题搜索论文，支持智能日期回退
    
    Args:
        topics: 主题列表
        date_from: 开始日期
        date_to: 结束日期  
        max_retries: 最大重试次数
        
    Returns:
        包含论文列表和搜索信息的字典
    """
    
    # 定义搜索策略
    search_strategies = []
    
    if date_from and date_to:
        # 策略1: 精确日期范围
        search_strategies.append({
            'name': f'精确日期范围 ({date_from} 到 {date_to})',
            'date_from': date_from,
            'date_to': date_to
        })
        
        # 策略2: 扩展到最近7天
        try:
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
            start_date = end_date - timedelta(days=7)
            search_strategies.append({
                'name': f'最近7天 ({start_date.strftime("%Y-%m-%d")} 到 {date_to})',
                'date_from': start_date.strftime('%Y-%m-%d'),
                'date_to': date_to
            })
        except:
            pass
        
        # 策略3: 扩展到最近30天
        try:
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
            start_date = end_date - timedelta(days=30)
            search_strategies.append({
                'name': f'最近30天 ({start_date.strftime("%Y-%m-%d")} 到 {date_to})',
                'date_from': start_date.strftime('%Y-%m-%d'),
                'date_to': date_to
            })
        except:
            pass
    
    # 策略4: 不限日期
    search_strategies.append({
        'name': '不限日期',
        'date_from': None,
        'date_to': None
    })
    
    results = {
        'topics': topics,
        'papers': [],
        'search_strategy_used': None,
        'total_results': 0,
        'search_url': None,
        'attempted_strategies': []
    }
    
    # 尝试各种搜索策略
    for strategy in search_strategies:
        try:
            print(f"🔍 尝试搜索策略: {strategy['name']}")
            
            url = build_topic_search_url(
                topics=topics,
                date_from=strategy['date_from'],
                date_to=strategy['date_to']
            )
            
            print(f"🌐 搜索URL: {url}")
            
            with httpx.Client(follow_redirects=True, timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()
                
            papers = parse_arxiv_search_results(response.text)
            
            strategy_result = {
                'name': strategy['name'],
                'papers_found': len(papers),
                'total_available': papers[0].get('total_results', 0) if papers else 0,
                'url': url
            }
            results['attempted_strategies'].append(strategy_result)
            
            print(f"📊 找到 {len(papers)} 篇论文")
            
            if papers:
                results['papers'] = papers
                results['search_strategy_used'] = strategy['name']
                results['total_results'] = papers[0].get('total_results', len(papers))
                results['search_url'] = url
                break
            else:
                print(f"❌ 该策略未找到结果，尝试下一个策略...")
                
        except Exception as e:
            print(f"❌ 搜索策略 '{strategy['name']}' 失败: {e}")
            results['attempted_strategies'].append({
                'name': strategy['name'],
                'error': str(e),
                'url': url if 'url' in locals() else None
            })
            continue
    
    return results


def display_search_results(results: Dict[str, Any], limit: int = 10) -> None:
    """
    显示搜索结果
    
    Args:
        results: 搜索结果字典
        limit: 显示论文数量限制
    """
    print("\n" + "="*80)
    print(f"🔍 主题搜索结果")
    print(f"🏷️  搜索主题: {' AND '.join(results['topics'])}")
    print(f"⏰ 搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 显示尝试的搜索策略
    print(f"\n📋 搜索策略尝试记录:")
    for i, strategy in enumerate(results['attempted_strategies'], 1):
        if 'error' in strategy:
            print(f"  {i}. ❌ {strategy['name']}: {strategy['error']}")
        else:
            print(f"  {i}. {'✅' if strategy['papers_found'] > 0 else '❌'} {strategy['name']}: {strategy['papers_found']} 篇论文 (总计 {strategy['total_available']} 篇)")
    
    if not results['papers']:
        print(f"\n❌ 所有搜索策略都未找到结果")
        return
    
    print(f"\n🎯 使用策略: {results['search_strategy_used']}")
    print(f"📊 显示前 {min(limit, len(results['papers']))} 篇论文 (总计 {results['total_results']} 篇)")
    print(f"🔗 搜索链接: {results['search_url']}")
    
    # 显示论文列表
    for i, paper in enumerate(results['papers'][:limit], 1):
        print(f"\n{'-'*60}")
        print(f"📄 {i}. {paper.get('title', '无标题')}")
        print(f"🆔 arXiv ID: {paper['arxiv_id']}")
        print(f"🏷️  学科分类: {', '.join(paper.get('subjects', []))}")
        
        if paper.get('authors'):
            authors_display = ', '.join(paper['authors'][:3])
            if len(paper['authors']) > 3:
                authors_display += f" 等 {len(paper['authors'])} 位作者"
            print(f"👥 作者: {authors_display}")
        
        if paper.get('submitted_date'):
            print(f"📅 提交日期: {paper['submitted_date']}")
            
        print(f"🌐 链接: {paper['url']}")
        
        if paper.get('abstract'):
            abstract = paper['abstract']
            if len(abstract) > 200:
                abstract = abstract[:200] + "..."
            print(f"📝 摘要: {abstract}")
    
    if len(results['papers']) > limit:
        print(f"\n💡 还有 {len(results['papers']) - limit} 篇论文未显示，可调整 limit 参数查看更多")


def get_topic_papers_with_smart_dates(
    topics: List[str], 
    target_date: Optional[str] = None,
    days_back: int = 1
) -> Dict[str, Any]:
    """
    智能获取主题论文，支持日期回退
    
    Args:
        topics: 主题列表
        target_date: 目标日期 (YYYY-MM-DD)，None 表示今天
        days_back: 回退天数
        
    Returns:
        搜索结果字典
    """
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    # 计算日期范围
    try:
        end_date = datetime.strptime(target_date, '%Y-%m-%d')
        start_date = end_date - timedelta(days=days_back-1)
        date_from = start_date.strftime('%Y-%m-%d')
        date_to = end_date.strftime('%Y-%m-%d')
    except:
        date_from = None
        date_to = None
    
    return fetch_papers_by_topic(topics, date_from, date_to)


def main():
    """主函数"""
    print("🔍 基于主题的论文搜索系统")
    print("="*50)
    
    # 默认搜索 AI + 安全/密码学 交叉领域
    topics = ["cs.AI", "cs.CR"]
    
    # 可以通过命令行参数或者直接修改来自定义
    import sys
    if len(sys.argv) > 1:
        # 支持命令行输入主题
        topics = sys.argv[1].split(',')
        topics = [topic.strip() for topic in topics]  # 清理空格
    
    print(f"📚 搜索主题: {' AND '.join(topics)}")
    
    # 检测是否在CI环境中运行
    is_ci = os.getenv('GITHUB_ACTIONS') == 'true'
    
    if is_ci:
        # CI环境：运行单一的智能搜索，减少输出
        print("\n🔍 CI模式: 智能搜索最新论文")
        results = get_topic_papers_with_smart_dates(topics, days_back=3)
        display_search_results(results, limit=10)
    else:
        # 本地环境：运行完整的测试模式
        print("\n🔍 测试1: 智能搜索最近3天的论文")
        results1 = get_topic_papers_with_smart_dates(topics, days_back=3)
        display_search_results(results1, limit=5)
        
        print("\n\n🔍 测试2: 不限日期搜索（获取最新50篇）")
        results2 = fetch_papers_by_topic(topics, date_from=None, date_to=None)
        display_search_results(results2, limit=10)
        
        results = results2 if results2['papers'] else results1
    
    # 保存最新的结果到文件
    output_file = f"reports/topic_papers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        os.makedirs("reports", exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到: {output_file}")
        
        # CI环境中显示总结信息
        if is_ci:
            papers_count = len(results.get('papers', []))
            strategy_used = results.get('search_strategy_used', 'N/A')
            print(f"📊 本次搜索总结:")
            print(f"   🎯 策略: {strategy_used}")
            print(f"   📄 论文数量: {papers_count}")
            print(f"   🏷️  主题: {' AND '.join(topics)}")
            
    except Exception as e:
        print(f"\n❌ 保存结果失败: {e}")


if __name__ == "__main__":
    main() 
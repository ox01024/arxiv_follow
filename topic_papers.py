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

# 导入滴答清单集成
try:
    from dida_integration import create_arxiv_task
except ImportError:
    print("⚠️ 无法导入滴答清单集成模块，相关功能将被禁用")
    def create_arxiv_task(*args, **kwargs):
        return {"success": False, "error": "模块未导入"}


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
    
    # 查找论文条目 - 使用实际的HTML结构
    paper_pattern = r'<li class="arxiv-result">(.*?)</li>'
    paper_matches = re.findall(paper_pattern, html_content, re.DOTALL)
    
    for match in paper_matches:
        paper = {
            'total_results': total_count
        }
        
        # 提取arXiv ID和URL
        id_pattern = r'<a href="https://arxiv\.org/abs/(\d{4}\.\d{4,5})">arXiv:(\d{4}\.\d{4,5})</a>'
        id_match = re.search(id_pattern, match)
        if id_match:
            paper['arxiv_id'] = id_match.group(1)
            paper['url'] = f"https://arxiv.org/abs/{paper['arxiv_id']}"
        
        # 提取标题
        title_pattern = r'<p class="title is-5 mathjax"[^>]*>\s*(.*?)\s*</p>'
        title_match = re.search(title_pattern, match, re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # 清理HTML标签
            title = re.sub(r'<[^>]+>', '', title)
            title = re.sub(r'\s+', ' ', title).strip()
            if title:
                paper['title'] = title
        
        # 提取作者
        authors_pattern = r'<p class="authors"[^>]*>.*?<span[^>]+>Authors:</span>(.*?)</p>'
        authors_match = re.search(authors_pattern, match, re.DOTALL)
        if authors_match:
            authors_html = authors_match.group(1)
            # 提取所有作者链接
            author_links = re.findall(r'<a[^>]+>(.*?)</a>', authors_html)
            if author_links:
                authors = [re.sub(r'<[^>]+>', '', author).strip() for author in author_links]
                authors = [author for author in authors if author]  # 过滤空字符串
                if authors:
                    paper['authors'] = authors
        
        # 提取学科分类
        subjects = []
        subject_pattern = r'<span class="tag[^"]*"[^>]*data-tooltip="([^"]+)"[^>]*>([^<]+)</span>'
        subject_matches = re.findall(subject_pattern, match)
        for tooltip, subject_code in subject_matches:
            subjects.append(subject_code.strip())
        if subjects:
            paper['subjects'] = subjects
        
        # 提取摘要 - 优先获取完整摘要
        abstract_patterns = [
            # 优先提取完整摘要
            r'<span[^>]*class="[^"]*abstract-full[^"]*"[^>]*[^>]*>(.*?)</span>',
            # 备选：普通摘要段落
            r'<p[^>]*class="[^"]*abstract[^"]*"[^>]*>.*?<span[^>]+>Abstract[^<]*</span>:\s*(.*?)</p>',
            # 备选：abstract-short（如果没有full版本）
            r'<span[^>]*class="[^"]*abstract-short[^"]*"[^>]*[^>]*>(.*?)</span>',
        ]
        
        for pattern in abstract_patterns:
            abstract_match = re.search(pattern, match, re.DOTALL | re.IGNORECASE)
            if abstract_match:
                abstract = abstract_match.group(1).strip()
                # 清理HTML标签、链接和多余空白
                abstract = re.sub(r'<a[^>]*>.*?</a>', '', abstract)  # 移除More/Less链接
                abstract = re.sub(r'<[^>]+>', '', abstract)
                abstract = re.sub(r'&hellip;.*', '', abstract)  # 移除省略号及后续内容
                abstract = re.sub(r'\s+', ' ', abstract).strip()
                if len(abstract) > 20:  # 确保不是空的或太短的内容
                    paper['abstract'] = abstract
                    break
        
        # 提取提交日期
        submitted_pattern = r'<span[^>]+>Submitted</span>\s+([^;]+);'
        submitted_match = re.search(submitted_pattern, match)
        if submitted_match:
            paper['submitted_date'] = submitted_match.group(1).strip()
        
        # 提取评论信息
        comments_pattern = r'<p class="comments[^"]*"[^>]*>.*?<span[^>]+>Comments:</span>\s*<span[^>]*>(.*?)</span>'
        comments_match = re.search(comments_pattern, match, re.DOTALL)
        if comments_match:
            comments = re.sub(r'<[^>]+>', '', comments_match.group(1)).strip()
            if comments:
                paper['comments'] = comments
        
        # 只添加至少有标题或arXiv ID的论文
        if paper.get('title') or paper.get('arxiv_id'):
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


def create_topic_dida_task(topics: List[str], 
                          results: Dict[str, Any],
                          error: str = None) -> None:
    """
    创建主题论文搜索的滴答清单任务
    
    Args:
        topics: 搜索主题列表
        results: 搜索结果字典
        error: 错误信息（如果有的话）
    """
    print("\n📝 创建滴答清单任务...")
    
    try:
        # 计算统计信息
        papers = results.get('papers', []) if results else []
        paper_count = len(papers)
        
        # 构建任务摘要
        topics_str = ' AND '.join(topics)
        if error:
            summary = f"❌ 主题论文搜索执行失败\n主题: {topics_str}\n错误信息: {error}"
            details = f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elif paper_count == 0:
            summary = f"🎯 主题论文搜索未发现新论文\n主题: {topics_str}"
            details = f"搜索主题: {topics_str}\n"
            if results:
                strategy_info = []
                for strategy in results.get('attempted_strategies', []):
                    if 'error' in strategy:
                        strategy_info.append(f"❌ {strategy['name']}: {strategy['error']}")
                    else:
                        strategy_info.append(f"• {strategy['name']}: {strategy['papers_found']} 篇")
                details += f"尝试策略:\n" + "\n".join(strategy_info)
            details += f"\n\n⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            summary = f"🎉 主题论文搜索发现 {paper_count} 篇论文！\n主题: {topics_str}"
            # 构建详细信息
            details_lines = [f"搜索主题: {topics_str}"]
            
            if results:
                details_lines.append(f"使用策略: {results.get('search_strategy_used', '未知')}")
                details_lines.append(f"总可用论文: {results.get('total_results', paper_count)} 篇")
                
                # 添加前3篇论文标题
                if papers:
                    details_lines.append("\n📊 发现论文:")
                    for i, paper in enumerate(papers[:3], 1):
                        title = paper.get('title', '未知标题')
                        if len(title) > 60:
                            title = title[:60] + "..."
                        arxiv_id = paper.get('arxiv_id', '')
                        details_lines.append(f"{i}. {title} (arXiv:{arxiv_id})")
                    
                    if len(papers) > 3:
                        details_lines.append(f"... 还有 {len(papers)-3} 篇")
            
            details_lines.append(f"\n⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            details = "\n".join(details_lines)
        
        # 创建任务
        result = create_arxiv_task(
            report_type="topic",
            summary=summary,
            details=details,
            paper_count=paper_count
        )
        
        if result.get("success"):
            print(f"✅ 滴答清单任务创建成功!")
            if result.get("task_id"):
                print(f"   任务ID: {result['task_id']}")
            if result.get("url"):
                print(f"   任务链接: {result['url']}")
        else:
            print(f"❌ 滴答清单任务创建失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 创建滴答清单任务时出错: {e}")


def main():
    """主函数"""
    # 默认搜索 AI + 安全/密码学 交叉领域
    topics = ["cs.AI", "cs.CR"]
    results = None
    
    try:
        print("🔍 基于主题的论文搜索系统")
        print("="*50)
        
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
        
        # 创建滴答清单任务
        create_topic_dida_task(topics, results)
        
        # 保存最新的结果到文件
        output_file = f"reports/topic_papers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            os.makedirs("reports", exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 结果已保存到: {output_file}")
            
            # CI环境中显示总结信息
            if os.getenv('GITHUB_ACTIONS') == 'true':
                papers_count = len(results.get('papers', []))
                strategy_used = results.get('search_strategy_used', 'N/A')
                print(f"📊 本次搜索总结:")
                print(f"   🎯 策略: {strategy_used}")
                print(f"   📄 论文数量: {papers_count}")
                print(f"   🏷️  主题: {' AND '.join(topics)}")
                
        except Exception as e:
            print(f"\n❌ 保存结果失败: {e}")
            
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()
        # 创建错误记录任务
        create_topic_dida_task(topics, results, error=str(e))


if __name__ == "__main__":
    main() 
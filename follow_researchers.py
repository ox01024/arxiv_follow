#!/usr/bin/env python3
"""
从 Google Sheets TSV 链接获取研究者列表并检索他们当天发布的论文
"""

import httpx
import csv
import io
from typing import List, Dict, Any
from datetime import datetime, timedelta
import re
from urllib.parse import urlencode, quote


def fetch_researchers_from_tsv(url: str) -> List[Dict[str, Any]]:
    """
    从 TSV URL 获取研究者数据
    
    Args:
        url: Google Sheets TSV 导出链接
        
    Returns:
        研究者数据列表
    """
    try:
        # 使用 httpx 获取 TSV 数据，允许重定向
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            
        # 解析 TSV 数据
        tsv_content = response.text
        print(f"获取到的原始数据:\n{tsv_content}\n")
        
        # 使用 csv 模块解析 TSV
        csv_reader = csv.reader(io.StringIO(tsv_content), delimiter='\t')
        
        # 读取所有行
        rows = list(csv_reader)
        
        if not rows:
            print("未找到任何数据")
            return []
            
        # 检查是否有标题行（通过检查第一行是否包含明显的标题词汇）
        has_header = False
        if rows and len(rows) > 1:
            first_row = [cell.strip().lower() for cell in rows[0]]
            header_indicators = ['name', 'author', 'researcher', '姓名', '作者', '研究者']
            has_header = any(indicator in cell for cell in first_row for indicator in header_indicators)
        
        if has_header:
            headers = rows[0]
            data_rows = rows[1:]
            print(f"检测到标题行: {headers}")
        else:
            headers = []
            data_rows = rows
            print(f"未检测到标题行，所有行都视为数据")
        
        print(f"数据行数: {len(data_rows)}")
        
        # 转换为字典列表
        researchers = []
        for i, row in enumerate(data_rows):
            if any(cell.strip() for cell in row):  # 跳过空行
                if headers and len(headers) > 1:
                    # 如果有多个列，创建字典
                    researcher = {}
                    for j, header in enumerate(headers):
                        value = row[j] if j < len(row) else ""
                        researcher[header] = value.strip()
                    researchers.append(researcher)
                else:
                    # 如果只有一列或没有标题，将每行作为研究者姓名
                    name = " ".join(cell.strip() for cell in row if cell.strip())
                    if name:
                        researchers.append({"name": name, "row_index": i})
                        
        return researchers
        
    except httpx.RequestError as e:
        print(f"网络请求错误: {e}")
        return []
    except Exception as e:
        print(f"解析数据时出错: {e}")
        return []


def build_arxiv_search_url(author_name: str, date_from: str, date_to: str) -> str:
    """
    构建 arXiv 高级搜索 URL
    
    Args:
        author_name: 作者姓名
        date_from: 开始日期 (YYYY-MM-DD)
        date_to: 结束日期 (YYYY-MM-DD)
        
    Returns:
        arXiv 搜索 URL
    """
    # 修正arXiv日期范围问题：如果开始日期和结束日期相同，将结束日期设置为第二天
    # 因为arXiv要求 "End date must be later than start date"
    if date_from == date_to:
        from datetime import datetime, timedelta
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
            date_to = end_date.strftime('%Y-%m-%d')
        except ValueError:
            # 如果日期解析失败，保持原样
            pass
    
    base_url = "https://arxiv.org/search/advanced"
    
    params = {
        'advanced': '',
        'terms-0-operator': 'AND',
        'terms-0-term': f'"{author_name}"',
        'terms-0-field': 'author',
        'classification-computer_science': 'y',
        'classification-physics_archives': 'all',
        'classification-include_cross_list': 'include',
        'date-year': '',
        'date-filter_by': 'date_range',
        'date-from_date': date_from,
        'date-to_date': date_to,
        'date-date_type': 'submitted_date',
        'abstracts': 'show',
        'size': '50',
        'order': '-announced_date_first'
    }
    
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


def fetch_papers_for_researcher(author_name: str, date_from: str, date_to: str) -> List[Dict[str, Any]]:
    """
    获取特定研究者在指定日期范围内的论文
    
    Args:
        author_name: 研究者姓名
        date_from: 开始日期
        date_to: 结束日期
        
    Returns:
        论文列表
    """
    try:
        # 构建搜索URL
        search_url = build_arxiv_search_url(author_name, date_from, date_to)
        print(f"搜索 {author_name} 的论文: {search_url}")
        
        # 获取搜索结果页面
        with httpx.Client(follow_redirects=True, timeout=30.0) as client:
            response = client.get(search_url)
            response.raise_for_status()
        
        # 解析搜索结果
        papers = parse_arxiv_search_results(response.text)
        
        # 为每篇论文添加查询的作者信息
        for paper in papers:
            paper['queried_author'] = author_name
            
        return papers
        
    except Exception as e:
        print(f"获取 {author_name} 的论文时出错: {e}")
        return []


def get_today_papers_for_all_researchers(researchers: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    获取所有研究者今天发布的论文
    
    Args:
        researchers: 研究者列表
        
    Returns:
        按研究者分组的论文字典
    """
    # 获取今天的日期
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    
    print(f"\n正在搜索 {date_str} 当天发布的论文...")
    print("=" * 60)
    
    all_papers = {}
    
    for researcher in researchers:
        # 获取研究者姓名
        if isinstance(researcher, dict):
            if "name" in researcher:
                author_name = researcher["name"]
            else:
                # 取第一个非空值作为姓名
                author_name = next((v for v in researcher.values() if v.strip()), "")
        else:
            author_name = str(researcher)
        
        if not author_name or author_name.lower() in ['aaa', 'test']:  # 跳过测试数据
            continue
            
        print(f"\n正在搜索 {author_name} 的论文...")
        
        # 获取该研究者的论文
        papers = fetch_papers_for_researcher(author_name, date_str, date_str)
        
        if papers:
            all_papers[author_name] = papers
            print(f"  找到 {len(papers)} 篇论文")
        else:
            print(f"  未找到论文")
    
    return all_papers


def display_papers(all_papers: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    显示所有论文
    
    Args:
        all_papers: 按研究者分组的论文字典
    """
    if not all_papers:
        print("\n没有找到符合条件的论文。")
        return
    
    total_papers = sum(len(papers) for papers in all_papers.values())
    print(f"\n🎉 共找到 {total_papers} 篇论文:")
    print("=" * 80)
    
    for author, papers in all_papers.items():
        print(f"\n👨‍🔬 {author} ({len(papers)} 篇论文):")
        print("-" * 40)
        
        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. 📄 {paper.get('title', '未知标题')}")
            
            if 'arxiv_id' in paper:
                print(f"   🔗 arXiv ID: {paper['arxiv_id']}")
                print(f"   🌐 链接: {paper.get('url', '')}")
            
            if 'authors' in paper and paper['authors']:
                authors_str = ", ".join(paper['authors'][:3])  # 只显示前3个作者
                if len(paper['authors']) > 3:
                    authors_str += f" (等 {len(paper['authors'])} 位作者)"
                print(f"   👥 作者: {authors_str}")
            
            if 'submitted_date' in paper:
                print(f"   📅 提交日期: {paper['submitted_date']}")
            
            if 'abstract' in paper and paper['abstract']:
                abstract = paper['abstract']
                print(f"   📝 摘要: {abstract}")


def display_researchers(researchers: List[Dict[str, Any]]) -> None:
    """
    显示研究者列表
    
    Args:
        researchers: 研究者数据列表
    """
    if not researchers:
        print("没有找到研究者数据")
        return
        
    print(f"\n找到 {len(researchers)} 个研究者:")
    print("=" * 50)
    
    for i, researcher in enumerate(researchers, 1):
        print(f"{i}. ", end="")
        
        if isinstance(researcher, dict):
            if "name" in researcher:
                print(f"姓名: {researcher['name']}")
                # 显示其他字段
                for key, value in researcher.items():
                    if key != "name" and key != "row_index" and value:
                        print(f"   {key}: {value}")
            else:
                # 显示所有字段
                for key, value in researcher.items():
                    if value:
                        print(f"{key}: {value}")
        else:
            print(researcher)
        print()


def get_recent_papers_for_researchers(researchers: List[Dict[str, Any]], days: int = 7) -> Dict[str, List[Dict[str, Any]]]:
    """
    获取所有研究者最近几天发布的论文
    
    Args:
        researchers: 研究者列表
        days: 搜索最近几天
        
    Returns:
        按研究者分组的论文字典
    """
    # 获取日期范围
    today = datetime.now()
    start_date = today - timedelta(days=days)
    end_date = today
    
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    print(f"\n正在搜索 {start_date_str} 到 {end_date_str} 期间发布的论文...")
    print("=" * 60)
    
    all_papers = {}
    
    for researcher in researchers:
        # 获取研究者姓名
        if isinstance(researcher, dict):
            if "name" in researcher:
                author_name = researcher["name"]
            else:
                # 取第一个非空值作为姓名
                author_name = next((v for v in researcher.values() if v.strip()), "")
        else:
            author_name = str(researcher)
        
        if not author_name or author_name.lower() in ['aaa', 'test']:  # 跳过测试数据
            continue
            
        print(f"\n正在搜索 {author_name} 的论文...")
        
        # 获取该研究者的论文
        papers = fetch_papers_for_researcher(author_name, start_date_str, end_date_str)
        
        if papers:
            all_papers[author_name] = papers
            print(f"  找到 {len(papers)} 篇论文")
        else:
            print(f"  未找到论文")
    
    return all_papers


def main():
    """主函数"""
    # Google Sheets TSV 导出链接
    tsv_url = "https://docs.google.com/spreadsheets/d/1itjnV2U-Eh0F1T0LIGuLjzIhgL9f_OD8tbkMUG-Onic/export?format=tsv&id=1itjnV2U-Eh0F1T0LIGuLjzIhgL9f_OD8tbkMUG-Onic&gid=0"
    
    print("🔍 正在从 Google Sheets 获取研究者列表...")
    print(f"URL: {tsv_url}\n")
    
    # 获取研究者数据
    researchers = fetch_researchers_from_tsv(tsv_url)
    
    # 显示研究者列表
    display_researchers(researchers)
    
    if researchers:
        # 获取所有研究者今天发布的论文
        all_papers = get_today_papers_for_all_researchers(researchers)
        
        # 显示论文结果
        display_papers(all_papers)
        
        # 如果今天没有找到论文，搜索最近一周的论文
        if not all_papers:
            print("\n💡 今天没有新论文，让我们搜索最近一周的论文...")
            recent_papers = get_recent_papers_for_researchers(researchers, days=7)
            if recent_papers:
                print(f"\n📚 最近一周的论文 (注意：这些不是今天发布的):")
                display_papers(recent_papers)
            else:
                print("\n📝 最近一周也没有找到论文。可能原因：")
                print("   1. 研究者姓名需要核实")
                print("   2. 该研究者最近没有在 arXiv 上发布论文") 
                print("   3. 可以尝试更长的时间范围")
        
        return researchers, all_papers
    else:
        return [], {}


if __name__ == "__main__":
    researchers_data, papers_data = main()

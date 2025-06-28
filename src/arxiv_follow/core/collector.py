#!/usr/bin/env python3
"""
论文内容采集模块 - 从arXiv获取论文完整内容
支持多种内容获取方式和智能内容提取
"""

import httpx
import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import json
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaperCollector:
    """论文内容采集器"""
    
    def __init__(self):
        self.session = httpx.Client(
            timeout=30.0,
            headers={
                "User-Agent": "ArXiv-Follow-Collector/1.0 (Academic Research Tool)"
            },
            follow_redirects=True
        )
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, 'session'):
            self.session.close()
    
    def get_paper_abstract_page(self, arxiv_id: str) -> Optional[str]:
        """
        获取论文摘要页面内容
        
        Args:
            arxiv_id: arXiv论文ID (如: 2501.12345)
            
        Returns:
            摘要页面HTML内容
        """
        try:
            url = f"https://arxiv.org/abs/{arxiv_id}"
            logger.info(f"获取论文摘要页面: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"获取摘要页面失败 {arxiv_id}: {e}")
            return None
    
    def extract_paper_metadata(self, html_content: str, arxiv_id: str) -> Dict[str, Any]:
        """
        从摘要页面提取详细元数据
        
        Args:
            html_content: HTML内容
            arxiv_id: arXiv ID
            
        Returns:
            详细的论文元数据
        """
        metadata = {
            'arxiv_id': arxiv_id,
            'url': f"https://arxiv.org/abs/{arxiv_id}",
            'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            'collection_time': datetime.now().isoformat()
        }
        
        try:
            # 提取标题
            title_pattern = r'<h1 class="title mathjax"[^>]*>\s*<span[^>]*>\s*(.*?)\s*</span>\s*</h1>'
            title_match = re.search(title_pattern, html_content, re.DOTALL)
            if title_match:
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                metadata['title'] = title
            
            # 提取作者信息（更详细）
            authors_pattern = r'<div class="authors"[^>]*>(.*?)</div>'
            authors_match = re.search(authors_pattern, html_content, re.DOTALL)
            if authors_match:
                authors_html = authors_match.group(1)
                # 提取作者链接和姓名
                author_links = re.findall(r'<a[^>]+>([^<]+)</a>', authors_html)
                if author_links:
                    metadata['authors'] = [author.strip() for author in author_links]
                else:
                    # 备选方案：提取纯文本作者
                    authors_text = re.sub(r'<[^>]+>', '', authors_html)
                    authors = [author.strip() for author in authors_text.split(',')]
                    metadata['authors'] = [author for author in authors if author]
            
            # 提取完整摘要
            abstract_pattern = r'<blockquote class="abstract mathjax"[^>]*>\s*<span[^>]*>Abstract:</span>\s*(.*?)\s*</blockquote>'
            abstract_match = re.search(abstract_pattern, html_content, re.DOTALL)
            if abstract_match:
                abstract = re.sub(r'<[^>]+>', '', abstract_match.group(1)).strip()
                abstract = re.sub(r'\s+', ' ', abstract)
                metadata['abstract'] = abstract
            
            # 提取学科分类
            subjects_pattern = r'<span class="primary-subject">([^<]+)</span>'
            subjects_match = re.search(subjects_pattern, html_content)
            if subjects_match:
                metadata['primary_subject'] = subjects_match.group(1).strip()
            
            # 提取所有分类
            all_subjects = re.findall(r'<td class="tablecell subjects">([^<]+)</td>', html_content)
            if all_subjects:
                subjects = [subj.strip() for subj in all_subjects[0].split(';') if subj.strip()]
                metadata['subjects'] = subjects
            
            # 提取提交日期
            submitted_pattern = r'<td class="tablecell"[^>]*>\[Submitted[^<]*on\s+([^\]]+)\]</td>'
            submitted_match = re.search(submitted_pattern, html_content)
            if submitted_match:
                metadata['submitted_date'] = submitted_match.group(1).strip()
            
            # 提取评论信息
            comments_pattern = r'<td class="tablecell comments mathjax">([^<]+)</td>'
            comments_match = re.search(comments_pattern, html_content)
            if comments_match:
                metadata['comments'] = comments_match.group(1).strip()
            
            # 提取期刊引用信息
            journal_pattern = r'<td class="tablecell jref">([^<]+)</td>'
            journal_match = re.search(journal_pattern, html_content)
            if journal_match:
                metadata['journal_ref'] = journal_match.group(1).strip()
            
            # 提取DOI
            doi_pattern = r'<td class="tablecell doi"[^>]*><a[^>]+>([^<]+)</a></td>'
            doi_match = re.search(doi_pattern, html_content)
            if doi_match:
                metadata['doi'] = doi_match.group(1).strip()
            
            # 检查是否有HTML版本
            html_version_pattern = r'<a[^>]+href="([^"]*html[^"]*)"[^>]*>HTML</a>'
            html_version_match = re.search(html_version_pattern, html_content)
            if html_version_match:
                metadata['html_url'] = urljoin("https://arxiv.org", html_version_match.group(1))
            
        except Exception as e:
            logger.error(f"提取元数据时出错: {e}")
        
        return metadata
    
    def get_paper_html_content(self, arxiv_id: str) -> Optional[str]:
        """
        尝试获取论文的HTML版本内容
        
        Args:
            arxiv_id: arXiv论文ID
            
        Returns:
            HTML格式的论文内容，如果不可用则返回None
        """
        try:
            # 检查HTML版本是否可用
            html_url = f"https://arxiv.org/html/{arxiv_id}"
            logger.info(f"尝试获取HTML版本: {html_url}")
            
            response = self.session.get(html_url)
            
            if response.status_code == 200:
                logger.info(f"成功获取HTML版本: {arxiv_id}")
                return response.text
            else:
                logger.info(f"HTML版本不可用: {arxiv_id} (状态码: {response.status_code})")
                return None
                
        except Exception as e:
            logger.warning(f"获取HTML版本失败 {arxiv_id}: {e}")
            return None
    
    def extract_text_from_html(self, html_content: str) -> Dict[str, Any]:
        """
        从HTML内容中提取结构化文本
        
        Args:
            html_content: HTML内容
            
        Returns:
            提取的结构化文本信息
        """
        extracted = {
            'has_html_version': True,
            'extraction_time': datetime.now().isoformat()
        }
        
        try:
            # 提取标题
            title_patterns = [
                r'<h1[^>]*class="[^"]*title[^"]*"[^>]*>([^<]+)</h1>',
                r'<title>([^<]+)</title>',
                r'<h1[^>]*>([^<]+)</h1>'
            ]
            
            for pattern in title_patterns:
                title_match = re.search(pattern, html_content, re.IGNORECASE)
                if title_match:
                    extracted['title'] = title_match.group(1).strip()
                    break
            
            # 提取章节内容
            sections = []
            
            # 查找所有标题和内容
            section_pattern = r'<h([1-6])[^>]*>([^<]+)</h\1>(.*?)(?=<h[1-6]|$)'
            section_matches = re.findall(section_pattern, html_content, re.DOTALL | re.IGNORECASE)
            
            for level, title, content in section_matches:
                # 清理内容
                clean_content = re.sub(r'<[^>]+>', ' ', content)
                clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                
                if clean_content and len(clean_content) > 20:  # 过滤太短的内容
                    sections.append({
                        'level': int(level),
                        'title': title.strip(),
                        'content': clean_content[:2000]  # 限制长度
                    })
            
            if sections:
                extracted['sections'] = sections
            
            # 提取摘要
            abstract_patterns = [
                r'<div[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</div>',
                r'<section[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</section>',
                r'<p[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</p>'
            ]
            
            for pattern in abstract_patterns:
                abstract_match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
                if abstract_match:
                    abstract = re.sub(r'<[^>]+>', ' ', abstract_match.group(1))
                    abstract = re.sub(r'\s+', ' ', abstract).strip()
                    if len(abstract) > 50:
                        extracted['html_abstract'] = abstract
                        break
            
            # 提取参考文献数量
            ref_patterns = [
                r'<div[^>]*class="[^"]*reference[^"]*"',
                r'<li[^>]*class="[^"]*reference[^"]*"',
                r'\[(\d+)\].*?</li>'
            ]
            
            ref_count = 0
            for pattern in ref_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                ref_count = max(ref_count, len(matches))
            
            if ref_count > 0:
                extracted['reference_count'] = ref_count
            
            # 估算文本长度
            all_text = re.sub(r'<[^>]+>', ' ', html_content)
            all_text = re.sub(r'\s+', ' ', all_text)
            extracted['estimated_word_count'] = len(all_text.split())
            
        except Exception as e:
            logger.error(f"从HTML提取文本时出错: {e}")
        
        return extracted
    
    def collect_paper_content(self, arxiv_id: str) -> Dict[str, Any]:
        """
        采集论文完整内容
        
        Args:
            arxiv_id: arXiv论文ID
            
        Returns:
            完整的论文内容信息
        """
        logger.info(f"开始采集论文内容: {arxiv_id}")
        
        # 获取基础元数据
        abstract_html = self.get_paper_abstract_page(arxiv_id)
        if not abstract_html:
            return {'error': f'无法获取论文 {arxiv_id} 的摘要页面'}
        
        # 提取元数据
        metadata = self.extract_paper_metadata(abstract_html, arxiv_id)
        
        # 尝试获取HTML版本
        html_content = self.get_paper_html_content(arxiv_id)
        
        if html_content:
            # 提取HTML版本的详细内容
            html_extracted = self.extract_text_from_html(html_content)
            metadata.update(html_extracted)
        else:
            metadata['has_html_version'] = False
        
        # 添加采集统计
        metadata['content_sources'] = []
        if abstract_html:
            metadata['content_sources'].append('abstract_page')
        if html_content:
            metadata['content_sources'].append('html_version')
        
        logger.info(f"论文内容采集完成: {arxiv_id}, 数据源: {metadata.get('content_sources', [])}")
        
        return metadata
    
    def collect_multiple_papers(self, arxiv_ids: List[str], delay: float = 1.0) -> Dict[str, Dict[str, Any]]:
        """
        批量采集多篇论文内容
        
        Args:
            arxiv_ids: arXiv ID列表
            delay: 请求间隔延迟(秒)
            
        Returns:
            论文ID到内容的映射
        """
        results = {}
        
        logger.info(f"开始批量采集 {len(arxiv_ids)} 篇论文")
        
        for i, arxiv_id in enumerate(arxiv_ids):
            try:
                results[arxiv_id] = self.collect_paper_content(arxiv_id)
                
                # 进度显示
                if i % 5 == 0 or i == len(arxiv_ids) - 1:
                    logger.info(f"采集进度: {i + 1}/{len(arxiv_ids)}")
                
                # 添加延迟避免过于频繁的请求
                if i < len(arxiv_ids) - 1:
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"采集论文 {arxiv_id} 时出错: {e}")
                results[arxiv_id] = {'error': str(e)}
        
        logger.info(f"批量采集完成，成功: {len([r for r in results.values() if 'error' not in r])}/{len(arxiv_ids)}")
        
        return results


def collect_paper_content(arxiv_id: str) -> Dict[str, Any]:
    """
    便捷函数：采集单篇论文内容
    
    Args:
        arxiv_id: arXiv论文ID
        
    Returns:
        论文内容信息
    """
    collector = PaperCollector()
    try:
        return collector.collect_paper_content(arxiv_id)
    finally:
        collector.session.close()


def collect_multiple_papers(arxiv_ids: List[str], delay: float = 1.0) -> Dict[str, Dict[str, Any]]:
    """
    便捷函数：批量采集论文内容
    
    Args:
        arxiv_ids: arXiv ID列表
        delay: 请求间隔延迟(秒)
        
    Returns:
        论文ID到内容的映射
    """
    collector = PaperCollector()
    try:
        return collector.collect_multiple_papers(arxiv_ids, delay)
    finally:
        collector.session.close()


if __name__ == "__main__":
    # 测试代码
    test_arxiv_id = "2501.12345"  # 示例ID，实际使用时需要替换
    
    print(f"🧪 测试论文内容采集: {test_arxiv_id}")
    
    try:
        result = collect_paper_content(test_arxiv_id)
        print("\n📄 采集结果:")
        print(f"标题: {result.get('title', 'N/A')}")
        print(f"作者: {result.get('authors', 'N/A')}")
        print(f"摘要长度: {len(result.get('abstract', ''))}")
        print(f"HTML版本: {'是' if result.get('has_html_version') else '否'}")
        print(f"内容源: {result.get('content_sources', [])}")
        
        if result.get('sections'):
            print(f"发现章节数: {len(result['sections'])}")
            for section in result['sections'][:3]:  # 显示前3个章节
                print(f"  - {section['title']} (级别 {section['level']})")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}") 
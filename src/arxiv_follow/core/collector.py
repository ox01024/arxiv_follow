#!/usr/bin/env python3
"""
论文内容采集模块 - 从arXiv获取论文完整内容
支持多种内容获取方式和智能内容提取
"""

import asyncio
import logging
import re
from typing import Dict, Any, Optional, List, AsyncIterator
from datetime import datetime, date, timedelta
import time
import json
from urllib.parse import urljoin, urlencode

import httpx
import xml.etree.ElementTree as ET
from pydantic import ValidationError

from ..models import Paper, PaperMetadata, PaperContent, SearchQuery, SearchResult
from ..models.config import AppConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArxivCollector:
    """ArXiv 论文收集器"""
    
    def __init__(self, config: AppConfig):
        """初始化收集器"""
        self.config = config
        self.base_url = config.api.arxiv_base_url
        self.delay = config.api.arxiv_delay_seconds
        self.timeout = config.api.arxiv_timeout_seconds
        
        # HTTP客户端配置
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=config.get_api_headers(),
            follow_redirects=True
        )
    
        # 命名空间映射（用于XML解析）
        self.namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom',
            'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()
    
    def _build_query_url(self, **params) -> str:
        """构建查询URL"""
        # 处理搜索查询
        search_query = params.get('search_query', '')
        if not search_query:
            raise ValueError("search_query is required")
        
        # 构建查询参数
        query_params = {
            'search_query': search_query,
            'start': params.get('start', 0),
            'max_results': params.get('max_results', 50),
            'sortBy': params.get('sortBy', 'submittedDate'),
            'sortOrder': params.get('sortOrder', 'descending')
        }
        
        return f"{self.base_url}?{urlencode(query_params)}"
    
    def _parse_arxiv_response(self, xml_content: str) -> Dict[str, Any]:
        """解析ArXiv API响应"""
        try:
            root = ET.fromstring(xml_content)
            
            # 获取总数
            total_results = root.find('.//opensearch:totalResults', self.namespaces)
            total = int(total_results.text) if total_results is not None else 0
            
            # 获取论文条目
            entries = root.findall('.//atom:entry', self.namespaces)
            papers = []
            
            for entry in entries:
                try:
                    paper_data = self._parse_entry(entry)
                    if paper_data:
                        papers.append(paper_data)
                except Exception as e:
                    logger.warning(f"Failed to parse entry: {e}")
                    continue
            
            return {
                'total_results': total,
                'papers': papers,
                'count': len(papers)
            }
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML response: {e}")
            raise ValueError(f"Invalid XML response: {e}")
    
    def _parse_entry(self, entry: ET.Element) -> Optional[Dict[str, Any]]:
        """解析单个论文条目"""
        try:
            # 基础信息
            title_elem = entry.find('.//atom:title', self.namespaces)
            title = title_elem.text.strip() if title_elem is not None else ""
            
            summary_elem = entry.find('.//atom:summary', self.namespaces)
            abstract = summary_elem.text.strip() if summary_elem is not None else ""
            
            # ArXiv ID
            id_elem = entry.find('.//atom:id', self.namespaces)
            if id_elem is None:
                return None
            
            arxiv_url = id_elem.text.strip()
            arxiv_id = arxiv_url.split('/')[-1]  # 提取ID部分
            
            # 作者
            authors = []
            author_elems = entry.findall('.//atom:author', self.namespaces)
            for author_elem in author_elems:
                name_elem = author_elem.find('.//atom:name', self.namespaces)
                if name_elem is not None:
                    authors.append(name_elem.text.strip())
            
            # 日期
            published_elem = entry.find('.//atom:published', self.namespaces)
            submitted_date = None
            if published_elem is not None:
                try:
                    submitted_date = datetime.fromisoformat(
                        published_elem.text.replace('Z', '+00:00')
                    )
                except ValueError:
                    pass
            
            updated_elem = entry.find('.//atom:updated', self.namespaces)
            updated_date = None
            if updated_elem is not None:
                try:
                    updated_date = datetime.fromisoformat(
                        updated_elem.text.replace('Z', '+00:00')
                    )
                except ValueError:
                    pass
            
            # 分类
            categories = []
            category_elems = entry.findall('.//atom:category', self.namespaces)
            for cat_elem in category_elems:
                term = cat_elem.get('term')
                if term:
                    categories.append(term)
            
            primary_category = categories[0] if categories else None
            
            # DOI和期刊引用
            doi = None
            journal_ref = None
            
            arxiv_elems = entry.findall('.//arxiv:doi', self.namespaces)
            if arxiv_elems:
                doi = arxiv_elems[0].text.strip()
            
            journal_elems = entry.findall('.//arxiv:journal_ref', self.namespaces)
            if journal_elems:
                journal_ref = journal_elems[0].text.strip()
            
            # 构建链接
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            
            return {
                'arxiv_id': arxiv_id,
                'title': title,
                'authors': authors,
                'abstract': abstract,
                'primary_category': primary_category,
                'categories': categories,
                'submitted_date': submitted_date,
                'updated_date': updated_date,
                'doi': doi,
                'journal_ref': journal_ref,
                'arxiv_url': arxiv_url,
                'pdf_url': pdf_url,
            }
                
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None
    
    async def search_by_query(self, query: str, max_results: int = 50, start: int = 0) -> SearchResult:
        """通过查询字符串搜索论文"""
        try:
            url = self._build_query_url(
                search_query=query,
                max_results=max_results,
                start=start
            )
            
            logger.info(f"Searching ArXiv: {query}")
            response = await self.client.get(url)
            response.raise_for_status()
            
            # 解析响应
            result_data = self._parse_arxiv_response(response.text)
            
            # 构建搜索结果
            search_query = SearchQuery(
                query_id=f"arxiv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                search_type="keyword",
                query_text=query
            )
            
            search_result = SearchResult(
                query=search_query,
                papers=result_data['papers']
            )
            
            search_result.metrics.total_found = result_data['total_results']
            search_result.metrics.total_returned = result_data['count']
            search_result.update_metrics()
            
            return search_result
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during search: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise
    
    async def search_by_authors(self, authors: List[str], max_results: int = 50) -> SearchResult:
        """按作者搜索论文"""
        # 构建作者查询
        author_queries = [f'au:"{author}"' for author in authors]
        query = ' OR '.join(author_queries)
        
        return await self.search_by_query(query, max_results)
    
    async def search_by_categories(self, categories: List[str], max_results: int = 50) -> SearchResult:
        """按分类搜索论文"""
        # 构建分类查询
        cat_queries = [f'cat:{cat}' for cat in categories]
        query = ' AND '.join(cat_queries)
        
        return await self.search_by_query(query, max_results)
    
    async def search_by_date_range(
        self, 
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        categories: Optional[List[str]] = None,
        max_results: int = 50
    ) -> SearchResult:
        """按日期范围搜索论文"""
        query_parts = []
        
        # 添加分类条件
        if categories:
            cat_queries = [f'cat:{cat}' for cat in categories]
            query_parts.append(f"({' OR '.join(cat_queries)})")
        else:
            query_parts.append("all:*")  # 搜索所有分类
        
        # 添加日期条件
        if date_from or date_to:
            date_query = "submittedDate:["
            
            if date_from:
                date_query += date_from.strftime("%Y%m%d")
            else:
                date_query += "*"
            
            date_query += " TO "
            
            if date_to:
                date_query += date_to.strftime("%Y%m%d")
            else:
                date_query += "*"
            
            date_query += "]"
            query_parts.append(date_query)
        
        query = " AND ".join(query_parts)
        return await self.search_by_query(query, max_results)
    
    async def search_recent_papers(
        self, 
        days_back: int = 7,
        categories: Optional[List[str]] = None,
        max_results: int = 50
    ) -> SearchResult:
        """搜索最近的论文"""
        date_from = date.today() - timedelta(days=days_back)
        return await self.search_by_date_range(
            date_from=date_from,
            categories=categories,
            max_results=max_results
        )
    
    async def get_paper_details(self, arxiv_id: str) -> Optional[Paper]:
        """获取单篇论文的详细信息"""
        try:
            # 通过ID搜索
            result = await self.search_by_query(f"id:{arxiv_id}", max_results=1)
            
            if not result.papers:
                logger.warning(f"Paper {arxiv_id} not found")
                return None
            
            paper_data = result.papers[0]
            
            # 创建论文元数据
            metadata = PaperMetadata(**paper_data)
            
            # 创建完整论文对象
            paper = Paper(metadata=metadata)
            
            return paper
            
        except ValidationError as e:
            logger.error(f"Validation error for paper {arxiv_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting paper details for {arxiv_id}: {e}")
            return None
    
    async def get_paper_content(self, arxiv_id: str) -> Optional[PaperContent]:
        """获取论文内容（如果有HTML版本）"""
        try:
            # 尝试获取HTML版本
            html_url = f"https://arxiv.org/html/{arxiv_id}"
            
            response = await self.client.get(html_url)
            
            if response.status_code == 200:
                # 成功获取HTML内容
                content = PaperContent(
                    arxiv_id=arxiv_id,
                    html_content=response.text,
                    extraction_method="html",
                    extraction_success=True,
                    language="en"
                )
                
                # 简单的内容提取
                if "latex" in response.text.lower():
                    content.has_latex = True
                
                if any(keyword in response.text.lower() for keyword in ["code", "github", "implementation"]):
                    content.has_code = True
                
                return content
            else:
                logger.info(f"HTML version not available for {arxiv_id}")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to get content for {arxiv_id}: {e}")
            return None
    
    async def collect_papers_batch(
        self, 
        arxiv_ids: List[str], 
        include_content: bool = False
    ) -> List[Paper]:
        """批量收集论文"""
        papers = []
        
        for arxiv_id in arxiv_ids:
            try:
                # 获取论文详情
                paper = await self.get_paper_details(arxiv_id)
                if not paper:
                    continue
                
                # 获取内容（如果需要）
                if include_content:
                    content = await self.get_paper_content(arxiv_id)
                    if content:
                        paper.content = content
                
                papers.append(paper)
                
                # 延迟以避免过度请求
                if self.delay > 0:
                    await asyncio.sleep(self.delay)
                    
            except Exception as e:
                logger.error(f"Failed to collect paper {arxiv_id}: {e}")
                continue
        
        logger.info(f"Successfully collected {len(papers)} papers out of {len(arxiv_ids)}")
        return papers
    
    async def stream_search_results(
        self, 
        query: str, 
        batch_size: int = 50,
        max_total: Optional[int] = None
    ) -> AsyncIterator[List[Dict[str, Any]]]:
        """流式搜索结果（用于大量数据）"""
        start = 0
        total_retrieved = 0
        
        while True:
            try:
                # 计算本次获取数量
                current_batch_size = batch_size
                if max_total and (total_retrieved + batch_size) > max_total:
                    current_batch_size = max_total - total_retrieved
                
                if current_batch_size <= 0:
                    break
                
                # 执行搜索
                result = await self.search_by_query(query, current_batch_size, start)
                
                if not result.papers:
                    break
                
                yield result.papers
                
                total_retrieved += len(result.papers)
                start += len(result.papers)
                
                # 检查是否已达到最大数量
                if max_total and total_retrieved >= max_total:
                    break
                
                # 检查是否还有更多结果
                if len(result.papers) < batch_size:
                    break
                
                # 延迟
                if self.delay > 0:
                    await asyncio.sleep(self.delay)
                    
            except Exception as e:
                logger.error(f"Error in stream search: {e}")
                break
    
    def create_smart_query(
        self, 
        topics: List[str], 
        authors: Optional[List[str]] = None,
        date_from: Optional[date] = None,
        exclude_categories: Optional[List[str]] = None
    ) -> str:
        """创建智能查询字符串"""
        query_parts = []
        
        # 主题查询（AND逻辑）
        if topics:
            topic_queries = [f'cat:{topic}' for topic in topics]
            query_parts.append(f"({' AND '.join(topic_queries)})")
        
        # 作者查询
        if authors:
            author_queries = [f'au:"{author}"' for author in authors]
            query_parts.append(f"({' OR '.join(author_queries)})")
        
        # 排除分类
        if exclude_categories:
            for cat in exclude_categories:
                query_parts.append(f"-cat:{cat}")
        
        # 日期过滤
        if date_from:
            date_query = f"submittedDate:[{date_from.strftime('%Y%m%d')} TO *]"
            query_parts.append(date_query)
        
        return " AND ".join(query_parts) if query_parts else "all:*"

 
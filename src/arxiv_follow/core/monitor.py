#!/usr/bin/env python3
"""
智能论文监控模块 - 集成论文采集、LLM分析和报告生成
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

# 导入各个模块
try:
    from .collector import PaperCollector
    from .analyzer import PaperAnalyzer
    from ..integrations.dida import create_arxiv_task
    from ..config.settings import PAPER_ANALYSIS_CONFIG, DIDA_API_CONFIG
except ImportError as e:
    print(f"⚠️ 无法导入必要模块: {e}")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentPaperMonitor:
    """智能论文监控器 - 集成采集、分析和报告功能"""
    
    def __init__(self):
        """初始化智能监控器"""
        self.config = PAPER_ANALYSIS_CONFIG
        self.collector = PaperCollector() if self.config.get('enable_content_collection') else None
        self.analyzer = PaperAnalyzer() if self.config.get('enable_analysis') else None
        
        logger.info(f"智能监控器初始化完成")
        logger.info(f"内容采集: {'启用' if self.collector else '禁用'}")
        logger.info(f"LLM分析: {'启用' if self.analyzer and self.analyzer.is_enabled() else '禁用'}")
    
    def is_analysis_enabled(self) -> bool:
        """检查分析功能是否启用"""
        return (self.config.get('enable_analysis', False) and 
                self.analyzer and 
                self.analyzer.is_enabled())
    
    def is_collection_enabled(self) -> bool:
        """检查采集功能是否启用"""
        return self.config.get('enable_content_collection', False) and self.collector
    
    def create_intelligent_dida_task(self, 
                                   report_type: str,
                                   title: str, 
                                   papers: List[Dict[str, Any]],
                                   error: str = None) -> Dict[str, Any]:
        """
        创建增强的滴答清单任务
        
        Args:
            report_type: 报告类型
            title: 任务标题
            papers: 论文列表
            error: 错误信息
            
        Returns:
            任务创建结果
        """
        if error or not papers:
            # 如果有错误或没有论文，使用原始的任务创建方式
            return create_arxiv_task(report_type, "无论文发现", "", 0)
        
        logger.info(f"开始智能处理 {len(papers)} 篇论文")
        
        # 生成增强的报告内容
        enhanced_content = self.generate_enhanced_content(papers)
        
        # 更新标题（如果启用了分析）
        enhanced_title = title
        if self.is_analysis_enabled():
            enhanced_title = f"🧠 {title} (AI增强版)"
        
        # 创建任务
        bilingual = DIDA_API_CONFIG.get('enable_bilingual', False)
        
        result = create_arxiv_task(
            report_type=report_type,
            summary=enhanced_title,
            details=enhanced_content,
            paper_count=len(papers),
            bilingual=bilingual
        )
        
        # 添加智能处理信息
        if result.get('success'):
            result['intelligent_features'] = {
                'content_collection': self.is_collection_enabled(),
                'llm_analysis': self.is_analysis_enabled()
            }
        
        return result
    
    def generate_enhanced_content(self, papers: List[Dict[str, Any]]) -> str:
        """
        生成增强的报告内容
        
        Args:
            papers: 论文列表
            
        Returns:
            增强的报告内容
        """
        content_parts = []
        
        # 基础论文信息
        content_parts.append("## 📄 论文详情")
        
        for i, paper in enumerate(papers, 1):
            title = paper.get('title', '未知标题')
            authors = paper.get('authors', [])
            arxiv_id = paper.get('arxiv_id', '')
            abstract = paper.get('abstract', '')
            
            content_parts.append(f"\n### {i}. {title}")
            
            if authors:
                content_parts.append(f"**作者**: {', '.join(authors[:3])}")
                if len(authors) > 3:
                    content_parts.append(f" 等 {len(authors)} 人")
            
            if arxiv_id:
                content_parts.append(f"**arXiv ID**: {arxiv_id}")
                content_parts.append(f"**链接**: https://arxiv.org/abs/{arxiv_id}")
            
            if abstract:
                content_parts.append(f"**摘要**: {abstract}")
            
            content_parts.append("\n" + "-"*30)
        
        # 统计信息
        content_parts.append(f"\n## 📊 统计信息")
        content_parts.append(f"- 发现论文数: {len(papers)}")
        content_parts.append(f"- 生成时间: {datetime.now().isoformat()}")
        content_parts.append(f"\n🤖 *由 ArXiv Follow 智能监控系统生成*")
        
        return '\n'.join(content_parts)


def create_intelligent_monitor() -> IntelligentPaperMonitor:
    """
    创建智能监控器实例
    
    Returns:
        智能监控器实例
    """
    return IntelligentPaperMonitor()


if __name__ == "__main__":
    # 测试代码
    print("🧪 测试智能论文监控功能")
    
    # 示例论文数据
    test_papers = [
        {
            "arxiv_id": "2501.12345",
            "title": "Deep Learning for Cybersecurity Applications",
            "authors": ["Zhang Wei", "Li Ming"],
            "abstract": "This paper presents novel deep learning approaches for cybersecurity...",
            "url": "https://arxiv.org/abs/2501.12345"
        }
    ]
    
    monitor = create_intelligent_monitor()
    
    print(f"内容采集: {'启用' if monitor.is_collection_enabled() else '禁用'}")
    print(f"LLM分析: {'启用' if monitor.is_analysis_enabled() else '禁用'}")
    
    # 测试任务创建
    result = monitor.create_intelligent_dida_task(
        report_type="daily",
        title="每日论文监控",
        papers=test_papers
    )
    
    print(f"\n✅ 测试完成，任务创建: {'成功' if result.get('success') else '失败'}")
    print(f"智能功能: {result.get('intelligent_features', {})}") 
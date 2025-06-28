#!/usr/bin/env python3
"""
论文分析模块 - 使用LLM对论文进行深度分析和报告生成
"""

import os
import httpx
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# 导入翻译服务的基础设施
try:
    from translation_service import TranslationService
except ImportError:
    print("⚠️ 无法导入翻译服务，将使用简化版本")
    TranslationService = None

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaperAnalyzer:
    """论文分析器 - 使用LLM分析论文内容"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化论文分析器
        
        Args:
            api_key: OpenRouter API密钥，如果不提供会从环境变量读取
        """
        self.api_key = api_key or os.getenv('OPEN_ROUTE_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "google/gemini-2.0-flash-lite-001"
        
        if not self.api_key:
            logger.warning("未找到OpenRouter API密钥，分析功能将被禁用")
            logger.info("请设置环境变量: OPEN_ROUTE_API_KEY")
    
    def is_enabled(self) -> bool:
        """检查分析器是否可用"""
        return bool(self.api_key)
    
    def _call_llm(self, prompt: str, max_tokens: int = 2000) -> Optional[str]:
        """
        调用LLM API
        
        Args:
            prompt: 提示词
            max_tokens: 最大token数
            
        Returns:
            LLM响应内容
        """
        if not self.is_enabled():
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/arxiv-follow",
                "X-Title": "ArXiv Follow Paper Analysis Service"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": 0.3,  # 降低随机性，提高分析的一致性
                "top_p": 0.9
            }
            
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                logger.info(f"LLM分析完成，响应长度: {len(content)}")
                return content
                
        except Exception as e:
            logger.error(f"LLM API调用失败: {e}")
            return None
    
    def analyze_paper_significance(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析论文的重要性和意义
        
        Args:
            paper_data: 论文数据
            
        Returns:
            重要性分析结果
        """
        if not self.is_enabled():
            return {"error": "分析器未启用"}
        
        # 构建分析提示词
        title = paper_data.get('title', '未知标题')
        abstract = paper_data.get('abstract', '无摘要')
        authors = paper_data.get('authors', [])
        subjects = paper_data.get('subjects', [])
        
        prompt = f"""请分析以下学术论文的重要性和意义：

论文标题：{title}

作者：{', '.join(authors) if authors else '未知'}

学科分类：{', '.join(subjects) if subjects else '未知'}

摘要：
{abstract}

请从以下角度进行分析（用中文回答）：

1. **研究意义**：这个研究解决了什么问题？为什么重要？
2. **技术创新点**：有哪些新的方法、技术或理论贡献？
3. **应用价值**：可能的实际应用场景和影响？
4. **研究质量评估**：基于摘要判断研究的严谨性和完整性
5. **重要性评分**：给出1-10分的重要性评分（10分最高）
6. **关键词提取**：提取5-8个关键技术词汇

请用结构化的方式回答，每个部分用简洁但有见地的语言总结。
"""
        
        response = self._call_llm(prompt, max_tokens=1500)
        
        if response:
            return {
                "analysis_type": "significance",
                "content": response,
                "model": self.model,
                "analysis_time": datetime.now().isoformat(),
                "success": True
            }
        else:
            return {
                "error": "LLM分析失败",
                "success": False
            }
    
    def analyze_paper_technical_details(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析论文的技术细节
        
        Args:
            paper_data: 论文数据
            
        Returns:
            技术分析结果
        """
        if not self.is_enabled():
            return {"error": "分析器未启用"}
        
        title = paper_data.get('title', '未知标题')
        abstract = paper_data.get('abstract', '无摘要')
        sections = paper_data.get('sections', [])
        
        # 如果有章节信息，包含在分析中
        sections_text = ""
        if sections:
            sections_text = "\n\n章节信息：\n"
            for section in sections[:5]:  # 只取前5个章节
                sections_text += f"- {section['title']}: {section['content']}\n"
        
        prompt = f"""请对以下学术论文进行技术深度分析：

论文标题：{title}

摘要：
{abstract}
{sections_text}

请从技术角度进行详细分析（用中文回答）：

1. **方法论分析**：使用了哪些研究方法和技术手段？
2. **算法/模型详解**：核心算法或模型的工作原理是什么？
3. **实验设计**：实验是如何设计的？使用了什么数据集？
4. **技术难点**：解决了哪些技术挑战？
5. **与现有工作的关系**：如何在现有研究基础上改进？
6. **可重现性评估**：实验的可重现性如何？
7. **技术局限性**：存在哪些技术限制或不足？

请用专业但易懂的语言进行分析，重点突出技术贡献。
"""
        
        response = self._call_llm(prompt, max_tokens=2000)
        
        if response:
            return {
                "analysis_type": "technical",
                "content": response,
                "model": self.model,
                "analysis_time": datetime.now().isoformat(),
                "success": True
            }
        else:
            return {
                "error": "LLM技术分析失败",
                "success": False
            }
    
    def generate_comprehensive_report(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成综合分析报告
        
        Args:
            paper_data: 论文数据
            
        Returns:
            综合报告
        """
        if not self.is_enabled():
            return {"error": "分析器未启用"}
        
        logger.info(f"开始生成综合报告: {paper_data.get('title', 'unknown')}")
        
        # 获取多个维度的分析
        significance_analysis = self.analyze_paper_significance(paper_data)
        technical_analysis = self.analyze_paper_technical_details(paper_data)
        
        # 生成最终综合报告
        title = paper_data.get('title', '未知标题')
        arxiv_id = paper_data.get('arxiv_id', '未知ID')
        authors = paper_data.get('authors', [])
        
        prompt = f"""基于以下论文的多维度分析，生成一份简洁但全面的分析报告：

论文：{title} (arXiv:{arxiv_id})
作者：{', '.join(authors[:5]) if authors else '未知'}

重要性分析：
{significance_analysis.get('content', '分析失败')}

技术分析：
{technical_analysis.get('content', '分析失败')}

请生成一份结构化的综合报告，包含：

📊 **论文概览**
- 基本信息和研究背景

🔬 **核心贡献**
- 主要技术创新（3-4个要点）

⚡ **重点亮点** 
- 最值得关注的创新点（2-3个）

🎯 **应用前景**
- 实际应用价值和潜在影响

📈 **推荐指数**
- 综合评分（1-10分）和推荐理由

请用markdown格式，语言简洁专业，适合作为研究简报。
"""
        
        response = self._call_llm(prompt, max_tokens=1800)
        
        if response:
            return {
                "report_type": "comprehensive",
                "paper_id": arxiv_id,
                "paper_title": title,
                "report_content": response,
                "model": self.model,
                "generation_time": datetime.now().isoformat(),
                "success": True,
                "analysis_components": {
                    "significance": significance_analysis.get('success', False),
                    "technical": technical_analysis.get('success', False)
                }
            }
        else:
            return {
                "error": "综合报告生成失败",
                "success": False
            }
    
    def analyze_multiple_papers(self, papers_data: List[Dict[str, Any]], mode: str = "significance") -> List[Dict[str, Any]]:
        """
        批量分析多篇论文
        
        Args:
            papers_data: 论文数据列表
            mode: 分析模式 ("significance", "technical", "comprehensive")
            
        Returns:
            分析结果列表
        """
        if not self.is_enabled():
            return [{"error": "分析器未启用"} for _ in papers_data]
        
        logger.info(f"开始批量分析 {len(papers_data)} 篇论文，模式: {mode}")
        
        results = []
        
        for i, paper_data in enumerate(papers_data):
            try:
                if mode == "significance":
                    result = self.analyze_paper_significance(paper_data)
                elif mode == "technical":
                    result = self.analyze_paper_technical_details(paper_data)
                elif mode == "comprehensive":
                    result = self.generate_comprehensive_report(paper_data)
                else:
                    result = {"error": f"未知分析模式: {mode}"}
                
                result['paper_index'] = i
                result['paper_id'] = paper_data.get('arxiv_id', f'paper_{i}')
                results.append(result)
                
                # 进度显示
                if i % 3 == 0 or i == len(papers_data) - 1:
                    logger.info(f"分析进度: {i + 1}/{len(papers_data)}")
                
            except Exception as e:
                logger.error(f"分析论文 {i} 时出错: {e}")
                results.append({
                    "error": str(e),
                    "paper_index": i,
                    "paper_id": paper_data.get('arxiv_id', f'paper_{i}')
                })
        
        success_count = len([r for r in results if r.get('success')])
        logger.info(f"批量分析完成，成功: {success_count}/{len(papers_data)}")
        
        return results
    
    def generate_daily_summary(self, papers_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成每日论文总结报告
        
        Args:
            papers_analysis: 论文分析结果列表
            
        Returns:
            每日总结报告
        """
        if not self.is_enabled():
            return {"error": "分析器未启用"}
        
        # 过滤成功的分析
        successful_analyses = [a for a in papers_analysis if a.get('success')]
        
        if not successful_analyses:
            return {"error": "没有成功的论文分析结果"}
        
        # 构建总结提示词
        papers_summary = "\n\n".join([
                            f"论文 {i+1}: {analysis.get('paper_id', 'unknown')}\n内容摘要:\n{analysis.get('report_content', analysis.get('content', ''))}"
            for i, analysis in enumerate(successful_analyses[:10])  # 最多总结10篇
        ])
        
        prompt = f"""基于今日收集的 {len(successful_analyses)} 篇论文分析，生成每日研究简报：

{papers_summary}

请生成一份每日简报，包含：

📅 **今日概览**
- 论文数量和主要研究领域分布

🔥 **热点趋势** 
- 识别出的研究热点和趋势（3-4个）

💎 **精选推荐**
- 最值得关注的2-3篇论文（说明理由）

🧠 **技术洞察**
- 新兴技术方向和重要进展

📊 **影响评估**
- 对相关研究领域可能产生的影响

请用markdown格式，简洁专业，适合作为研究动态简报。
"""
        
        response = self._call_llm(prompt, max_tokens=2000)
        
        if response:
            return {
                "summary_type": "daily",
                "papers_count": len(successful_analyses),
                "total_papers": len(papers_analysis),
                "summary_content": response,
                "model": self.model,
                "generation_time": datetime.now().isoformat(),
                "success": True
            }
        else:
            return {
                "error": "每日简报生成失败",
                "success": False
            }


def analyze_paper(paper_data: Dict[str, Any], mode: str = "comprehensive") -> Dict[str, Any]:
    """
    便捷函数：分析单篇论文
    
    Args:
        paper_data: 论文数据
        mode: 分析模式
        
    Returns:
        分析结果
    """
    analyzer = PaperAnalyzer()
    
    if mode == "significance":
        return analyzer.analyze_paper_significance(paper_data)
    elif mode == "technical":
        return analyzer.analyze_paper_technical_details(paper_data)
    else:
        return analyzer.generate_comprehensive_report(paper_data)


def analyze_multiple_papers(papers_data: List[Dict[str, Any]], mode: str = "comprehensive") -> List[Dict[str, Any]]:
    """
    便捷函数：批量分析论文
    
    Args:
        papers_data: 论文数据列表
        mode: 分析模式
        
    Returns:
        分析结果列表
    """
    analyzer = PaperAnalyzer()
    return analyzer.analyze_multiple_papers(papers_data, mode)


if __name__ == "__main__":
    # 测试代码
    print("🧪 测试论文分析功能")
    
    # 示例论文数据
    test_paper = {
        "arxiv_id": "2501.12345",
        "title": "Transformer-based Anomaly Detection in Network Traffic",
        "authors": ["Zhang Wei", "Li Ming"],
        "abstract": "This paper presents a novel approach for detecting anomalies in network traffic using transformer architectures. We propose a self-supervised learning framework that can identify unusual patterns without requiring labeled data...",
        "subjects": ["cs.AI", "cs.CR"]
    }
    
    analyzer = PaperAnalyzer()
    
    if analyzer.is_enabled():
        print("✅ 分析器已启用，开始测试...")
        
        # 测试重要性分析
        print("\n📊 测试重要性分析...")
        sig_result = analyzer.analyze_paper_significance(test_paper)
        if sig_result.get('success'):
            print("✅ 重要性分析成功")
            print(f"内容长度: {len(sig_result.get('content', ''))}")
        else:
            print(f"❌ 重要性分析失败: {sig_result.get('error')}")
        
        # 测试综合报告
        print("\n📋 测试综合报告生成...")
        report_result = analyzer.generate_comprehensive_report(test_paper)
        if report_result.get('success'):
            print("✅ 综合报告生成成功")
            print("\n报告内容预览:")
            print(report_result.get('report_content', '')[:300] + "...")
        else:
            print(f"❌ 综合报告生成失败: {report_result.get('error')}")
    
    else:
        print("❌ 分析器未启用，请设置 OPEN_ROUTE_API_KEY 环境变量") 
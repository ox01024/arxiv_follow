#!/usr/bin/env python3
"""
现代化论文分析模块

使用AI技术对论文进行深度分析、理解和报告生成。
"""

import logging
from datetime import datetime
from typing import Any

# 第三方库
import httpx

# 内部模块
from ..models.config import AppConfig

logger = logging.getLogger(__name__)


class PaperAnalyzer:
    """现代化论文分析器 - 使用AI进行深度分析"""

    def __init__(self, config: AppConfig):
        """
        初始化论文分析器

        Args:
            config: 应用程序配置
        """
        self.config = config
        self.api_key = config.get_llm_api_key()
        self.base_url = config.llm.api_base_url
        self.model = config.llm.default_model

        if not self.api_key:
            logger.warning("未找到LLM API密钥，分析功能将被禁用")
            logger.info("请在配置中设置LLM API密钥")

    def is_enabled(self) -> bool:
        """检查分析器是否可用"""
        return bool(self.api_key)

    async def _call_llm(self, prompt: str, max_tokens: int = 2000) -> str | None:
        """
        异步调用LLM API

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
                "X-Title": "ArXiv Follow Paper Analysis Service",
            }

            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.3,
                "top_p": 0.9,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions", headers=headers, json=data
                )
                response.raise_for_status()

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                logger.info(f"LLM分析完成，响应长度: {len(content)}")
                return content

        except Exception as e:
            logger.error(f"LLM API调用失败: {e}")
            return None

    async def analyze_paper_significance(
        self, paper_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        分析论文的重要性和意义

        Args:
            paper_data: 论文数据

        Returns:
            重要性分析结果
        """
        if not self.is_enabled():
            return {
                "error": "分析器未启用",
                "success": False,
                "importance_score": 5.0,  # 默认中等重要性
            }

        # 构建分析提示词
        title = paper_data.get("title", "未知标题")
        abstract = paper_data.get("summary", paper_data.get("abstract", "无摘要"))
        authors = paper_data.get("authors", [])
        categories = paper_data.get("categories", [])

        prompt = f"""请分析以下学术论文的重要性和意义：

论文标题：{title}

作者：{', '.join(authors) if authors else '未知'}

分类：{', '.join(categories) if categories else '未知'}

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
最后请在最后一行单独输出重要性评分，格式为"重要性评分: X.X"
"""

        response = await self._call_llm(prompt, max_tokens=1500)

        if response:
            # 尝试提取重要性评分
            importance_score = 5.0  # 默认评分
            try:
                # 查找评分模式
                lines = response.split("\n")
                for line in lines:
                    if "重要性评分" in line or "评分" in line:
                        import re

                        score_match = re.search(r"(\d+\.?\d*)", line)
                        if score_match:
                            importance_score = float(score_match.group(1))
                            break
            except (ValueError, AttributeError):
                pass

            return {
                "analysis_type": "significance",
                "content": response,
                "model": self.model,
                "analysis_time": datetime.now().isoformat(),
                "importance_score": importance_score,
                "success": True,
            }
        else:
            return {"error": "LLM分析失败", "success": False, "importance_score": 5.0}

    async def analyze_paper_technical_details(
        self, paper_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        分析论文的技术细节

        Args:
            paper_data: 论文数据

        Returns:
            技术分析结果
        """
        if not self.is_enabled():
            return {"error": "分析器未启用", "success": False}

        title = paper_data.get("title", "未知标题")
        abstract = paper_data.get("summary", paper_data.get("abstract", "无摘要"))

        prompt = f"""请对以下学术论文进行技术深度分析：

论文标题：{title}

摘要：
{abstract}

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

        response = await self._call_llm(prompt, max_tokens=2000)

        if response:
            return {
                "analysis_type": "technical",
                "content": response,
                "model": self.model,
                "analysis_time": datetime.now().isoformat(),
                "success": True,
            }
        else:
            return {"error": "LLM分析失败", "success": False}

    async def generate_comprehensive_report(
        self, paper_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        生成综合分析报告

        Args:
            paper_data: 论文数据

        Returns:
            综合分析报告
        """
        if not self.is_enabled():
            return {"error": "分析器未启用", "success": False}

        # 并行执行多种分析
        significance_task = self.analyze_paper_significance(paper_data)
        technical_task = self.analyze_paper_technical_details(paper_data)

        try:
            significance_result = await significance_task
            technical_result = await technical_task

            return {
                "analysis_type": "comprehensive",
                "paper_info": {
                    "title": paper_data.get("title", "未知标题"),
                    "authors": paper_data.get("authors", []),
                    "arxiv_id": paper_data.get("arxiv_id", paper_data.get("id", "")),
                    "categories": paper_data.get("categories", []),
                },
                "significance_analysis": significance_result,
                "technical_analysis": technical_result,
                "overall_score": significance_result.get("importance_score", 5.0),
                "analysis_time": datetime.now().isoformat(),
                "success": True,
            }

        except Exception as e:
            logger.error(f"综合分析失败: {e}")
            return {"error": f"综合分析失败: {str(e)}", "success": False}

    async def analyze_multiple_papers(
        self, papers_data: list[dict[str, Any]], mode: str = "significance"
    ) -> list[dict[str, Any]]:
        """
        批量分析多篇论文

        Args:
            papers_data: 论文数据列表
            mode: 分析模式 ("significance", "technical", "comprehensive")

        Returns:
            分析结果列表
        """
        if not self.is_enabled():
            return [{"error": "分析器未启用", "success": False} for _ in papers_data]

        if not papers_data:
            return []

        logger.info(f"开始批量分析 {len(papers_data)} 篇论文，模式: {mode}")

        results = []

        # 根据模式选择分析方法
        if mode == "significance":
            analyze_func = self.analyze_paper_significance
        elif mode == "technical":
            analyze_func = self.analyze_paper_technical_details
        elif mode == "comprehensive":
            analyze_func = self.generate_comprehensive_report
        else:
            raise ValueError(f"不支持的分析模式: {mode}")

        # 批量处理（这里可以根据需要调整并发度）
        import asyncio

        semaphore = asyncio.Semaphore(3)  # 限制并发数

        async def analyze_with_semaphore(paper_data):
            async with semaphore:
                return await analyze_func(paper_data)

        tasks = [analyze_with_semaphore(paper) for paper in papers_data]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"论文 {i} 分析失败: {result}")
                processed_results.append({"error": str(result), "success": False})
            else:
                processed_results.append(result)

        logger.info(
            f"批量分析完成，成功: {sum(1 for r in processed_results if r.get('success'))}/{len(processed_results)}"
        )

        return processed_results

    def generate_daily_summary(
        self, papers_analysis: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        生成每日分析摘要

        Args:
            papers_analysis: 论文分析结果列表

        Returns:
            每日摘要
        """
        summary = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_papers": len(papers_analysis),
            "successful_analysis": sum(1 for p in papers_analysis if p.get("success")),
            "failed_analysis": sum(1 for p in papers_analysis if not p.get("success")),
            "average_importance": 0.0,
            "high_importance_papers": [],
            "top_categories": {},
            "summary_text": "",
        }

        # 统计成功分析的论文
        successful_papers = [p for p in papers_analysis if p.get("success")]

        if successful_papers:
            # 计算平均重要性
            scores = [
                p.get("importance_score", 5.0)
                for p in successful_papers
                if p.get("importance_score")
            ]
            if scores:
                summary["average_importance"] = sum(scores) / len(scores)

            # 筛选高重要性论文（> 7.0分）
            high_importance = [
                p for p in successful_papers if p.get("importance_score", 0) > 7.0
            ]
            summary["high_importance_papers"] = high_importance[:5]  # 最多5篇

            # 统计分类分布
            categories = {}
            for paper in successful_papers:
                paper_categories = paper.get("paper_info", {}).get("categories", [])
                for cat in paper_categories:
                    categories[cat] = categories.get(cat, 0) + 1

            # 取前5个分类
            summary["top_categories"] = dict(
                sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
            )

            # 生成摘要文本
            summary["summary_text"] = self._generate_summary_text(summary)

        return summary

    def _generate_summary_text(self, summary: dict[str, Any]) -> str:
        """生成可读的摘要文本"""
        parts = []

        parts.append(f"📊 今日共分析 {summary['total_papers']} 篇论文")
        parts.append(f"✅ 成功分析 {summary['successful_analysis']} 篇")

        if summary["failed_analysis"] > 0:
            parts.append(f"❌ 分析失败 {summary['failed_analysis']} 篇")

        if summary["average_importance"] > 0:
            parts.append(f"📈 平均重要性评分 {summary['average_importance']:.1f}/10")

        if summary["high_importance_papers"]:
            parts.append(
                f"⭐ 发现 {len(summary['high_importance_papers'])} 篇高重要性论文"
            )

        if summary["top_categories"]:
            top_cat = list(summary["top_categories"].keys())[0]
            parts.append(f"🔥 热门分类: {top_cat}")

        return "\n".join(parts)


# 便捷函数
async def analyze_paper(
    paper_data: dict[str, Any], config: AppConfig, mode: str = "comprehensive"
) -> dict[str, Any]:
    """
    分析单篇论文的便捷函数

    Args:
        paper_data: 论文数据
        config: 应用配置
        mode: 分析模式

    Returns:
        分析结果
    """
    analyzer = PaperAnalyzer(config)

    if mode == "significance":
        return await analyzer.analyze_paper_significance(paper_data)
    elif mode == "technical":
        return await analyzer.analyze_paper_technical_details(paper_data)
    elif mode == "comprehensive":
        return await analyzer.generate_comprehensive_report(paper_data)
    else:
        raise ValueError(f"不支持的分析模式: {mode}")


async def analyze_multiple_papers(
    papers_data: list[dict[str, Any]], config: AppConfig, mode: str = "comprehensive"
) -> list[dict[str, Any]]:
    """
    批量分析论文的便捷函数

    Args:
        papers_data: 论文数据列表
        config: 应用配置
        mode: 分析模式

    Returns:
        分析结果列表
    """
    analyzer = PaperAnalyzer(config)
    return await analyzer.analyze_multiple_papers(papers_data, mode)


if __name__ == "__main__":
    # 测试代码
    import asyncio

    from ..models.config import AppConfig

    async def test_analyzer():
        print("🧪 测试论文分析功能")

        config = AppConfig()
        analyzer = PaperAnalyzer(config)

        print(f"分析器状态: {'启用' if analyzer.is_enabled() else '禁用'}")

        if analyzer.is_enabled():
            # 测试论文数据
            test_paper = {
                "title": "Deep Learning for Cybersecurity Applications",
                "authors": ["Zhang Wei", "Li Ming"],
                "abstract": "This paper presents novel deep learning approaches for cybersecurity...",
                "categories": ["cs.CR", "cs.LG"],
            }

            result = await analyzer.analyze_paper_significance(test_paper)
            print(f"分析结果: {result.get('success', False)}")
            print(f"重要性评分: {result.get('importance_score', 'N/A')}")

    asyncio.run(test_analyzer())

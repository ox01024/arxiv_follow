#!/usr/bin/env python3
"""
每周研究者动态汇总脚本 - 搜索特定研究者最近一周发布的论文
"""

from datetime import datetime, timedelta
from typing import Any

import httpx

# 导入滴答清单集成和配置
try:
    from ..config.settings import DIDA_API_CONFIG
    from ..integrations.dida import create_arxiv_task
    from ..services.researcher import (
        build_arxiv_search_url,
        fetch_researchers_from_tsv,
        parse_arxiv_search_results,
    )
except ImportError:
    print("⚠️ 无法导入集成模块，相关功能将被禁用")

    def create_arxiv_task(*_args, **_kwargs):
        return {"success": False, "error": "模块未导入"}

    def fetch_researchers_from_tsv(*_args, **_kwargs):
        return []

    def build_arxiv_search_url(*_args, **_kwargs):
        return ""

    def parse_arxiv_search_results(*_args, **_kwargs):
        return []

    DIDA_API_CONFIG = {"enable_bilingual": True}


def fetch_papers_for_researcher(
    author_name: str, date_from: str, date_to: str
) -> list[dict[str, Any]]:
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
            paper["queried_author"] = author_name

        return papers

    except Exception as e:
        print(f"获取 {author_name} 的论文时出错: {e}")
        return []


def get_weekly_papers_for_all_researchers(
    researchers: list[dict[str, Any]], days: int = 7
) -> dict[str, list[dict[str, Any]]]:
    """
    获取所有研究者最近一周发布的论文

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

    print(f"\n📚 正在搜索 {start_date_str} 到 {end_date_str} 期间发布的论文...")
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

        if not author_name or author_name.lower() in ["aaa", "test"]:  # 跳过测试数据
            continue

        print(f"\n正在搜索 {author_name} 的论文...")

        # 获取该研究者的论文
        papers = fetch_papers_for_researcher(author_name, start_date_str, end_date_str)

        if papers:
            all_papers[author_name] = papers
            print(f"  ✅ 找到 {len(papers)} 篇论文")
        else:
            print("  ❌ 未找到论文")

    return all_papers


def display_papers(
    all_papers: dict[str, list[dict[str, Any]]], period: str = "最近一周"
) -> None:
    """
    显示所有论文

    Args:
        all_papers: 按研究者分组的论文字典
        period: 时间段描述
    """
    if not all_papers:
        print(f"\n📝 {period}没有找到论文")
        return

    total_papers = sum(len(papers) for papers in all_papers.values())
    print(f"\n🎉 {period}共找到 {total_papers} 篇论文!")
    print("=" * 80)

    for author, papers in all_papers.items():
        print(f"\n👨‍🔬 {author} ({len(papers)} 篇论文):")
        print("-" * 40)

        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. 📄 {paper.get('title', '未知标题')}")

            if "arxiv_id" in paper:
                print(f"   🔗 arXiv ID: {paper['arxiv_id']}")
                print(f"   🌐 链接: {paper.get('url', '')}")

            if "authors" in paper and paper["authors"]:
                # 显示所有作者
                authors_str = ", ".join(paper["authors"])
                print(f"   👥 作者: {authors_str}")

            if "submitted_date" in paper:
                print(f"   📅 提交日期: {paper['submitted_date']}")

            if "abstract" in paper and paper["abstract"]:
                abstract = paper["abstract"]
                print(f"   📝 摘要: {abstract}")

            # 显示学科分类
            if "subjects" in paper and paper["subjects"]:
                subjects_str = ", ".join(paper["subjects"])
                print(f"   🏷️ 领域: {subjects_str}")

            # 显示评论信息
            if "comments" in paper and paper["comments"]:
                print(f"   💬 评论: {paper['comments']}")


def display_researchers(researchers: list[dict[str, Any]]) -> None:
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


def create_weekly_dida_task(
    researchers: list[dict[str, Any]],
    all_papers: dict[str, list[dict[str, Any]]],
    error: str = None,
) -> None:
    """
    创建周报论文监控的滴答清单任务

    Args:
        researchers: 研究者列表
        all_papers: 论文数据
        error: 错误信息（如果有的话）
    """
    print("\n📝 创建滴答清单任务...")

    try:
        # 计算统计信息
        total_papers = (
            sum(len(papers) for papers in all_papers.values()) if all_papers else 0
        )
        researcher_count = len(researchers)

        # 构建任务摘要（Markdown格式）
        if error:
            summary = f"❌ **每周研究者动态汇总执行失败**\n\n**错误信息:** {error}"
            details = f"⏰ **执行时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elif total_papers == 0:
            summary = "📚 **本周研究者无新论文发布**"
            details = f"👥 **监控研究者:** {researcher_count} 位\n📅 **监控周期:** {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} 至 {datetime.now().strftime('%Y-%m-%d')}\n⏰ **执行时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            summary = f"🎉 **本周研究者发布 {total_papers} 篇新论文！**"
            # 构建详细信息（Markdown格式）
            details_lines = [f"👥 **监控研究者:** {researcher_count} 位"]
            details_lines.append(
                f"📅 **监控周期:** {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} 至 {datetime.now().strftime('%Y-%m-%d')}"
            )

            # 添加发现论文的研究者详情（Markdown格式）
            if all_papers:
                details_lines.append("\n## 📊 论文分布")
                for author, papers in all_papers.items():
                    details_lines.append(f"\n### 👨‍🔬 {author} ({len(papers)} 篇)")

                    # 显示论文详细信息（前3篇显示详情，其余只显示标题）
                    for i, paper in enumerate(papers, 1):
                        title = paper.get("title", "未知标题")
                        arxiv_id = paper.get("arxiv_id", "")
                        url = paper.get("url", "")

                        if i <= 3:  # 前3篇显示详细信息
                            # 使用Markdown链接格式
                            if url and arxiv_id:
                                details_lines.append(f"\n**{i}. [{title}]({url})**")
                                details_lines.append(f"📄 **arXiv:** `{arxiv_id}`")
                            else:
                                details_lines.append(f"\n**{i}. {title}**")

                            # 作者信息（显示所有作者）
                            if paper.get("authors"):
                                authors_str = ", ".join(paper["authors"])
                                details_lines.append(f"👥 **作者:** {authors_str}")

                            # 摘要信息（前250字符）
                            if paper.get("abstract"):
                                abstract = paper["abstract"]

                                details_lines.append(f"📝 **摘要:** {abstract}")

                            # 提交日期
                            if paper.get("submitted_date"):
                                details_lines.append(
                                    f"📅 **提交日期:** {paper['submitted_date']}"
                                )

                            # 学科分类（显示所有分类）
                            if paper.get("subjects"):
                                subjects_str = ", ".join(
                                    [f"`{s}`" for s in paper["subjects"]]
                                )
                                details_lines.append(f"🏷️ **领域:** {subjects_str}")

                            # 评论信息
                            if paper.get("comments"):
                                comments = paper["comments"]

                                details_lines.append(f"💬 **评论:** {comments}")

                            details_lines.append("---")  # 分隔线
                        else:  # 其余论文显示标题和基本信息
                            # 使用Markdown链接格式
                            if url and arxiv_id:
                                details_lines.append(
                                    f"\n**{i}.** [{title}]({url}) `arXiv:{arxiv_id}`"
                                )
                            else:
                                details_lines.append(f"\n**{i}.** {title}")

                            # 简化的作者信息
                            if paper.get("authors"):
                                main_authors = ", ".join(paper["authors"][:2])
                                if len(paper["authors"]) > 2:
                                    main_authors += (
                                        f" *等{len(paper['authors'])}位作者*"
                                    )
                                details_lines.append(f"   👥 {main_authors}")

                    # 如果有超过3篇论文，添加提示
                    if len(papers) > 3:
                        details_lines.append(
                            f"\n*📝 以上仅显示前3篇详细信息，总计**{len(papers)}**篇论文*"
                        )
                        details_lines.append("")

            details_lines.append(
                f"\n⏰ **执行时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            details = "\n".join(details_lines)

        # 创建任务（支持双语翻译）
        bilingual_enabled = DIDA_API_CONFIG.get("enable_bilingual", False)
        result = create_arxiv_task(
            report_type="weekly",
            summary=summary,
            details=details,
            paper_count=total_papers,
            bilingual=bilingual_enabled,
        )

        if result.get("success"):
            print("✅ 滴答清单任务创建成功!")
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
    try:
        # Google Sheets TSV 导出链接
        tsv_url = "https://docs.google.com/spreadsheets/d/1itjnV2U-Eh0F1T0LIGuLjzIhgL9f_OD8tbkMUG-Onic/export?format=tsv&id=1itjnV2U-Eh0F1T0LIGuLjzIhgL9f_OD8tbkMUG-Onic&gid=0"

        print("📚 每周研究者动态汇总 - 获取特定研究者最近一周发布的论文")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"URL: {tsv_url}\n")

        # 获取研究者数据
        researchers = fetch_researchers_from_tsv(tsv_url)

        # 显示研究者列表
        display_researchers(researchers)

        if researchers:
            # 获取所有研究者最近一周发布的论文
            all_papers = get_weekly_papers_for_all_researchers(researchers, days=7)

            # 显示论文结果
            display_papers(all_papers, "最近一周")

            print(
                f"\n✅ 研究者动态汇总完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # 创建滴答清单任务
            create_weekly_dida_task(researchers, all_papers)

            return researchers, all_papers
        else:
            print("⚠️ 未找到研究者数据，请检查数据源")
            # 即使没有数据也创建一个记录任务
            create_weekly_dida_task([], {})
            return [], {}

    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        import traceback

        traceback.print_exc()
        # 创建错误记录任务
        create_weekly_dida_task([], {}, error=str(e))
        return [], {}


if __name__ == "__main__":
    researchers_data, papers_data = main()

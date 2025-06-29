#!/usr/bin/env python3
"""
基于主题的论文监控脚本 - 搜索特定主题领域的最新论文
支持智能日期回退和多种搜索模式
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx

# 导入滴答清单集成和配置
try:
    from ..config.settings import DIDA_API_CONFIG
    from ..integrations.dida import create_arxiv_task
    from ..services.researcher import parse_arxiv_search_results
except ImportError:
    print("⚠️ 无法导入集成模块，相关功能将被禁用")

    def create_arxiv_task(*_args, **_kwargs):
        return {"success": False, "error": "模块未导入"}

    def parse_arxiv_search_results(*_args, **_kwargs):
        return []

    DIDA_API_CONFIG = {"enable_bilingual": True}


def build_topic_search_url(
    topics: list[str],
    date_from: str | None = None,
    date_to: str | None = None,
    classification: str = "computer_science",
    field: str = "all",
    size: int = 50,
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
        "advanced": "",
        "abstracts": "show",
        "size": str(size),
        "order": "-announced_date_first",
    }

    # 添加主题搜索条件
    for i, topic in enumerate(topics):
        params[f"terms-{i}-operator"] = "AND"
        params[f"terms-{i}-term"] = topic
        params[f"terms-{i}-field"] = field

    # 添加分类
    if classification == "computer_science":
        params["classification-computer_science"] = "y"
    elif classification == "physics":
        params["classification-physics_archives"] = "all"

    params["classification-include_cross_list"] = "include"

    # 添加日期条件
    if date_from and date_to:
        params["date-filter_by"] = "date_range"
        params["date-from_date"] = date_from
        params["date-to_date"] = date_to
        params["date-date_type"] = "submitted_date"
    else:
        params["date-filter_by"] = "all_dates"

    params["date-year"] = ""

    return f"{base_url}?{urlencode(params)}"





def fetch_papers_by_topic(
    topics: list[str],
    date_from: str | None = None,
    date_to: str | None = None,
    max_retries: int = 3,
) -> dict[str, Any]:
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
        search_strategies.append(
            {
                "name": f"精确日期范围 ({date_from} 到 {date_to})",
                "date_from": date_from,
                "date_to": date_to,
            }
        )

        # 策略2: 扩展到最近7天
        try:
            end_date = datetime.strptime(date_to, "%Y-%m-%d")
            start_date = end_date - timedelta(days=7)
            search_strategies.append(
                {
                    "name": f'最近7天 ({start_date.strftime("%Y-%m-%d")} 到 {date_to})',
                    "date_from": start_date.strftime("%Y-%m-%d"),
                    "date_to": date_to,
                }
            )
        except (ValueError, TypeError):
            pass

        # 策略3: 扩展到最近30天
        try:
            end_date = datetime.strptime(date_to, "%Y-%m-%d")
            start_date = end_date - timedelta(days=30)
            search_strategies.append(
                {
                    "name": f'最近30天 ({start_date.strftime("%Y-%m-%d")} 到 {date_to})',
                    "date_from": start_date.strftime("%Y-%m-%d"),
                    "date_to": date_to,
                }
            )
        except (ValueError, TypeError):
            pass

    # 策略4: 不限日期
    search_strategies.append({"name": "不限日期", "date_from": None, "date_to": None})

    results = {
        "topics": topics,
        "papers": [],
        "search_strategy_used": None,
        "total_results": 0,
        "search_url": None,
        "attempted_strategies": [],
    }

    # 尝试各种搜索策略
    for strategy in search_strategies:
        try:
            print(f"🔍 尝试搜索策略: {strategy['name']}")

            url = build_topic_search_url(
                topics=topics,
                date_from=strategy["date_from"],
                date_to=strategy["date_to"],
            )

            print(f"🌐 搜索URL: {url}")

            with httpx.Client(follow_redirects=True, timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()

            papers = parse_arxiv_search_results(response.text)

            strategy_result = {
                "name": strategy["name"],
                "papers_found": len(papers),
                "total_available": papers[0].get("total_results", 0) if papers else 0,
                "url": url,
            }
            results["attempted_strategies"].append(strategy_result)

            print(f"📊 找到 {len(papers)} 篇论文")

            if papers:
                results["papers"] = papers
                results["search_strategy_used"] = strategy["name"]
                results["total_results"] = papers[0].get("total_results", len(papers))
                results["search_url"] = url
                break
            else:
                print("❌ 该策略未找到结果，尝试下一个策略...")

        except Exception as e:
            print(f"❌ 搜索策略 '{strategy['name']}' 失败: {e}")
            results["attempted_strategies"].append(
                {
                    "name": strategy["name"],
                    "error": str(e),
                    "url": url if "url" in locals() else None,
                }
            )
            continue

    return results


def display_search_results(results: dict[str, Any], limit: int = 10) -> None:
    """
    显示搜索结果

    Args:
        results: 搜索结果字典
        limit: 显示论文数量限制
    """
    print("\n" + "=" * 80)
    print("🔍 主题搜索结果")
    print(f"🏷️  搜索主题: {' AND '.join(results['topics'])}")
    print(f"⏰ 搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 显示尝试的搜索策略
    print("\n📋 搜索策略尝试记录:")
    for i, strategy in enumerate(results["attempted_strategies"], 1):
        if "error" in strategy:
            print(f"  {i}. ❌ {strategy['name']}: {strategy['error']}")
        else:
            print(
                f"  {i}. {'✅' if strategy['papers_found'] > 0 else '❌'} {strategy['name']}: {strategy['papers_found']} 篇论文 (总计 {strategy['total_available']} 篇)"
            )

    if not results["papers"]:
        print("\n❌ 所有搜索策略都未找到结果")
        return

    print(f"\n🎯 使用策略: {results['search_strategy_used']}")
    print(
        f"📊 显示前 {min(limit, len(results['papers']))} 篇论文 (总计 {results['total_results']} 篇)"
    )
    print(f"🔗 搜索链接: {results['search_url']}")

    # 显示论文列表
    for i, paper in enumerate(results["papers"][:limit], 1):
        print(f"\n{'-'*60}")
        print(f"📄 {i}. {paper.get('title', '无标题')}")
        print(f"🆔 arXiv ID: {paper['arxiv_id']}")
        print(f"🏷️  学科分类: {', '.join(paper.get('subjects', []))}")

        if paper.get("authors"):
            # 显示所有作者
            authors_display = ", ".join(paper["authors"])
            print(f"👥 作者: {authors_display}")

        if paper.get("submitted_date"):
            print(f"📅 提交日期: {paper['submitted_date']}")

        print(f"🌐 链接: {paper['url']}")

        if paper.get("abstract"):
            abstract = paper["abstract"]
            print(f"📝 摘要: {abstract}")

        # 显示评论信息
        if paper.get("comments"):
            print(f"💬 评论: {paper['comments']}")

    if len(results["papers"]) > limit:
        print(
            f"\n💡 还有 {len(results['papers']) - limit} 篇论文未显示，可调整 limit 参数查看更多"
        )


def get_topic_papers_with_smart_dates(
    topics: list[str], target_date: str | None = None, days_back: int = 1
) -> dict[str, Any]:
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
        target_date = datetime.now().strftime("%Y-%m-%d")

    # 计算日期范围
    try:
        end_date = datetime.strptime(target_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=days_back - 1)
        date_from = start_date.strftime("%Y-%m-%d")
        date_to = end_date.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        date_from = None
        date_to = None

    return fetch_papers_by_topic(topics, date_from, date_to)


def create_topic_dida_task(
    topics: list[str], results: dict[str, Any], error: str = None
) -> None:
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
        papers = results.get("papers", []) if results else []
        paper_count = len(papers)

        # 构建任务摘要（Markdown格式）
        topics_str = " AND ".join([f"`{topic}`" for topic in topics])
        " AND ".join(topics)
        if error:
            summary = f"❌ **主题论文搜索执行失败**\n\n**主题:** {topics_str}\n**错误信息:** {error}"
            details = f"⏰ **执行时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elif paper_count == 0:
            summary = f"🎯 **主题论文搜索未发现新论文**\n\n**主题:** {topics_str}"
            details = f"🔍 **搜索主题:** {topics_str}\n"
            if results:
                details += "\n### 📋 尝试策略\n"
                strategy_info = []
                for strategy in results.get("attempted_strategies", []):
                    if "error" in strategy:
                        strategy_info.append(
                            f"❌ **{strategy['name']}:** {strategy['error']}"
                        )
                    else:
                        strategy_info.append(
                            f"✅ **{strategy['name']}:** {strategy['papers_found']} 篇"
                        )
                details += "\n".join(strategy_info)
            details += (
                f"\n\n⏰ **执行时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        else:
            summary = f"🎉 **主题论文搜索发现 {paper_count} 篇论文！**\n\n**主题:** {topics_str}"
            # 构建详细信息（Markdown格式）
            details_lines = [f"🔍 **搜索主题:** {topics_str}"]

            if results:
                details_lines.append(
                    f"🎯 **使用策略:** {results.get('search_strategy_used', '未知')}"
                )
                details_lines.append(
                    f"📊 **总可用论文:** {results.get('total_results', paper_count)} 篇"
                )

                # 显示所有论文的详细信息（Markdown格式）
                if papers:
                    details_lines.append("\n## 📊 发现论文")
                    for i, paper in enumerate(papers, 1):
                        title = paper.get("title", "未知标题")
                        arxiv_id = paper.get("arxiv_id", "")
                        url = paper.get("url", "")

                        # 使用Markdown链接格式
                        if url and arxiv_id:
                            details_lines.append(f"\n**{i}. [{title}]({url})**")
                            details_lines.append(f"📄 **arXiv:** `{arxiv_id}`")
                        else:
                            details_lines.append(f"\n**{i}. {title}**")
                            if arxiv_id:
                                details_lines.append(f"📄 **arXiv:** `{arxiv_id}`")

                        # 作者信息（显示所有作者）
                        if paper.get("authors"):
                            authors_str = ", ".join(paper["authors"])
                            details_lines.append(f"👥 **作者:** {authors_str}")

                        # 摘要信息（前200字符）
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

            details_lines.append(
                f"\n⏰ **执行时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            details = "\n".join(details_lines)

        # 创建任务（支持双语翻译）
        bilingual_enabled = DIDA_API_CONFIG.get("enable_bilingual", False)
        result = create_arxiv_task(
            report_type="topic",
            summary=summary,
            details=details,
            paper_count=paper_count,
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
    # 默认搜索 AI + 安全/密码学 交叉领域
    topics = ["cs.AI", "cs.CR"]
    results = None

    try:
        print("🔍 基于主题的论文搜索系统")
        print("=" * 50)

        # 可以通过命令行参数或者直接修改来自定义
        import sys

        if len(sys.argv) > 1:
            # 支持命令行输入主题
            topics = sys.argv[1].split(",")
            topics = [topic.strip() for topic in topics]  # 清理空格

        print(f"📚 搜索主题: {' AND '.join(topics)}")

        # 检测是否在CI环境中运行
        is_ci = os.getenv("GITHUB_ACTIONS") == "true"

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

            results = results2 if results2["papers"] else results1

        # 创建滴答清单任务
        create_topic_dida_task(topics, results)

        # 保存最新的结果到文件
        output_file = (
            f"reports/topic_papers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        try:
            os.makedirs("reports", exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 结果已保存到: {output_file}")

            # CI环境中显示总结信息
            if os.getenv("GITHUB_ACTIONS") == "true":
                papers_count = len(results.get("papers", []))
                strategy_used = results.get("search_strategy_used", "N/A")
                print("📊 本次搜索总结:")
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

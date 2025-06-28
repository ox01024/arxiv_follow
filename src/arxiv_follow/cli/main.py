"""
ArXiv Follow 主命令行界面

使用 Typer 构建的现代化CLI工具。
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..core.collector import ArxivCollector
from ..core.engine import SearchEngine
from ..models import SearchFilters, SearchQuery, SearchType
from ..models.config import AppConfig, load_config

# 创建应用实例
app = typer.Typer(
    name="arxiv-follow",
    help="现代化ArXiv论文监控系统 - 支持AI增强分析、研究者跟踪和智能推荐",
    add_completion=False,
    rich_markup_mode="rich",
)

# 控制台输出
console = Console()

# 全局配置
_config: AppConfig | None = None


def get_config() -> AppConfig:
    """获取全局配置"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def setup_logging(debug: bool = False) -> None:
    """设置日志"""
    config = get_config()
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format=config.log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def display_papers_table(papers: list[dict], title: str = "论文列表") -> None:
    """显示论文表格"""
    if not papers:
        console.print("[yellow]没有找到论文[/yellow]")
        return

    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=12)
    table.add_column("标题", style="green", width=50)
    table.add_column("作者", style="blue", width=30)
    table.add_column("分类", style="yellow", width=15)
    table.add_column("日期", style="red", width=10)

    for paper in papers[:20]:  # 限制显示数量
        arxiv_id = paper.get("arxiv_id", "N/A")
        title = (
            paper.get("title", "N/A")[:50] + "..."
            if len(paper.get("title", "")) > 50
            else paper.get("title", "N/A")
        )
        authors = ", ".join(paper.get("authors", [])[:2])  # 显示前两个作者
        if len(paper.get("authors", [])) > 2:
            authors += f" 等{len(paper.get('authors', [])) - 2}人"
        categories = paper.get("primary_category", "N/A")
        submitted_date = paper.get("submitted_date", "N/A")
        if isinstance(submitted_date, datetime):
            submitted_date = submitted_date.strftime("%Y-%m-%d")

        table.add_row(arxiv_id, title, authors, categories, str(submitted_date))

    console.print(table)

    if len(papers) > 20:
        console.print(f"[dim]显示前20篇，共找到{len(papers)}篇论文[/dim]")


@app.callback()
def main(
    debug: Annotated[bool, typer.Option("--debug", help="启用调试模式")] = False,
    config_file: Annotated[
        str | None, typer.Option("--config", help="配置文件路径")
    ] = None,
):
    """
    ArXiv Follow - 现代化论文监控系统

    支持研究者跟踪、主题搜索、AI分析等功能。
    """
    setup_logging(debug)

    if config_file:
        # TODO: 支持自定义配置文件
        pass


@app.command("search")
def search_papers(
    query: Annotated[str, typer.Argument(help="搜索查询")],
    type: Annotated[
        SearchType, typer.Option("--type", "-t", help="搜索类型")
    ] = SearchType.KEYWORD,
    max_results: Annotated[int, typer.Option("--max", "-m", help="最大结果数")] = 20,
    days_back: Annotated[
        int | None, typer.Option("--days", "-d", help="回溯天数")
    ] = None,
    categories: Annotated[
        str | None, typer.Option("--categories", "-c", help="分类过滤（逗号分隔）")
    ] = None,
    authors: Annotated[
        str | None, typer.Option("--authors", "-a", help="作者过滤（逗号分隔）")
    ] = None,
    output: Annotated[
        str | None, typer.Option("--output", "-o", help="输出文件路径")
    ] = None,
):
    """
    搜索ArXiv论文

    支持关键词搜索、作者搜索、主题搜索等多种模式。
    """

    async def run_search():
        config = get_config()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("正在搜索论文...", total=None)

            try:
                # 构建搜索查询
                search_query = SearchQuery(
                    query_id=f"cli_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    search_type=type,
                    query_text=query,
                    topics=categories.split(",") if categories else [],
                    researchers=authors.split(",") if authors else [],
                    filters=SearchFilters(
                        max_results=max_results,
                        days_back=days_back,
                    ),
                )

                # 执行搜索
                async with SearchEngine(config) as engine:
                    result = await engine.search(search_query)

                progress.update(task, completed=True)

                # 显示结果
                if result.success:
                    console.print("\n[green]✅ 搜索完成[/green]")
                    console.print(
                        f"找到 {result.metrics.total_returned} 篇论文（共 {result.metrics.total_found} 篇匹配）"
                    )
                    console.print(f"搜索时间: {result.metrics.search_time_ms:.1f}ms\n")

                    display_papers_table(result.papers, f"搜索结果: {query}")

                    # 保存结果
                    if output:
                        import json

                        output_path = Path(output)
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        with open(output_path, "w", encoding="utf-8") as f:
                            json.dump(
                                {
                                    "query": result.query.dict(),
                                    "papers": result.papers,
                                    "metrics": result.metrics.dict(),
                                    "timestamp": datetime.now().isoformat(),
                                },
                                f,
                                ensure_ascii=False,
                                indent=2,
                            )

                        console.print(f"\n[blue]💾 结果已保存到: {output_path}[/blue]")
                else:
                    console.print(f"[red]❌ 搜索失败: {result.error_message}[/red]")

            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]❌ 搜索出错: {e}[/red]")
                raise typer.Exit(1)

    asyncio.run(run_search())


@app.command("recent")
def recent_papers(
    days: Annotated[int, typer.Option("--days", "-d", help="回溯天数")] = 3,
    topics: Annotated[
        str | None, typer.Option("--topics", "-t", help="主题过滤（逗号分隔）")
    ] = None,
    max_results: Annotated[int, typer.Option("--max", "-m", help="最大结果数")] = 20,
    output: Annotated[
        str | None, typer.Option("--output", "-o", help="输出文件路径")
    ] = None,
):
    """
    获取最近发布的论文

    默认获取最近3天的AI和安全领域论文。
    """

    async def run_recent():
        config = get_config()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"正在获取最近 {days} 天的论文...", total=None)

            try:
                topic_list = (
                    topics.split(",")
                    if topics
                    else config.monitoring.default_search_topics
                )

                async with SearchEngine(config) as engine:
                    result = await engine.search_recent_papers(
                        days_back=days, topics=topic_list, max_results=max_results
                    )

                progress.update(task, completed=True)

                if result.success:
                    console.print("\n[green]✅ 获取完成[/green]")
                    console.print(f"找到 {result.metrics.total_returned} 篇论文")
                    console.print(f"主题: {', '.join(topic_list)}")
                    console.print(f"时间范围: {days} 天内\n")

                    display_papers_table(result.papers, f"最近 {days} 天的论文")

                    if output:
                        import json

                        output_path = Path(output)
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        with open(output_path, "w", encoding="utf-8") as f:
                            json.dump(
                                {
                                    "query": result.query.dict(),
                                    "papers": result.papers,
                                    "metrics": result.metrics.dict(),
                                    "timestamp": datetime.now().isoformat(),
                                },
                                f,
                                ensure_ascii=False,
                                indent=2,
                            )

                        console.print(f"\n[blue]💾 结果已保存到: {output_path}[/blue]")
                else:
                    console.print(f"[red]❌ 获取失败: {result.error_message}[/red]")

            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]❌ 获取出错: {e}[/red]")
                raise typer.Exit(1)

    asyncio.run(run_recent())


@app.command("authors")
def search_by_authors(
    authors: Annotated[str, typer.Argument(help="作者姓名（逗号分隔）")],
    max_results: Annotated[int, typer.Option("--max", "-m", help="最大结果数")] = 20,
    output: Annotated[
        str | None, typer.Option("--output", "-o", help="输出文件路径")
    ] = None,
):
    """
    按作者搜索论文

    搜索指定作者发表的论文。
    """

    async def run_author_search():
        config = get_config()
        author_list = [name.strip() for name in authors.split(",")]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("正在搜索作者论文...", total=None)

            try:
                async with SearchEngine(config) as engine:
                    result = await engine.search_by_author_names(
                        author_names=author_list, max_results=max_results
                    )

                progress.update(task, completed=True)

                if result.success:
                    console.print("\n[green]✅ 搜索完成[/green]")
                    console.print(f"找到 {result.metrics.total_returned} 篇论文")
                    console.print(f"作者: {', '.join(author_list)}\n")

                    display_papers_table(
                        result.papers, f"作者论文: {', '.join(author_list[:2])}"
                    )

                    if output:
                        import json

                        output_path = Path(output)
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        with open(output_path, "w", encoding="utf-8") as f:
                            json.dump(
                                {
                                    "query": result.query.dict(),
                                    "papers": result.papers,
                                    "metrics": result.metrics.dict(),
                                    "timestamp": datetime.now().isoformat(),
                                },
                                f,
                                ensure_ascii=False,
                                indent=2,
                            )

                        console.print(f"\n[blue]💾 结果已保存到: {output_path}[/blue]")
                else:
                    console.print(f"[red]❌ 搜索失败: {result.error_message}[/red]")

            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]❌ 搜索出错: {e}[/red]")
                raise typer.Exit(1)

    asyncio.run(run_author_search())


@app.command("topics")
def search_by_topics(
    topics: Annotated[
        str, typer.Argument(help="主题分类（逗号分隔，如: cs.AI,cs.CR）")
    ],
    days: Annotated[int | None, typer.Option("--days", "-d", help="回溯天数")] = 7,
    max_results: Annotated[int, typer.Option("--max", "-m", help="最大结果数")] = 20,
    output: Annotated[
        str | None, typer.Option("--output", "-o", help="输出文件路径")
    ] = None,
):
    """
    按主题搜索论文（跨领域）

    搜索指定主题交叉的论文，支持AND逻辑。
    """

    async def run_topic_search():
        config = get_config()
        topic_list = [topic.strip() for topic in topics.split(",")]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("正在搜索跨领域论文...", total=None)

            try:
                async with SearchEngine(config) as engine:
                    result = await engine.search_cross_domain(
                        primary_topics=topic_list,
                        days_back=days,
                        max_results=max_results,
                    )

                progress.update(task, completed=True)

                if result.success:
                    console.print("\n[green]✅ 搜索完成[/green]")
                    console.print(f"找到 {result.metrics.total_returned} 篇论文")
                    console.print(f"主题: {' AND '.join(topic_list)}")
                    console.print(f"时间范围: 最近 {days} 天\n")

                    display_papers_table(
                        result.papers, f"跨领域论文: {' ∩ '.join(topic_list)}"
                    )

                    if output:
                        import json

                        output_path = Path(output)
                        output_path.parent.mkdir(parents=True, exist_ok=True)

                        with open(output_path, "w", encoding="utf-8") as f:
                            json.dump(
                                {
                                    "query": result.query.dict(),
                                    "papers": result.papers,
                                    "metrics": result.metrics.dict(),
                                    "timestamp": datetime.now().isoformat(),
                                },
                                f,
                                ensure_ascii=False,
                                indent=2,
                            )

                        console.print(f"\n[blue]💾 结果已保存到: {output_path}[/blue]")
                else:
                    console.print(f"[red]❌ 搜索失败: {result.error_message}[/red]")

            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"[red]❌ 搜索出错: {e}[/red]")
                raise typer.Exit(1)

    asyncio.run(run_topic_search())


@app.command("config")
def show_config(
    show_sensitive: Annotated[
        bool, typer.Option("--show-sensitive", help="显示敏感信息")
    ] = False,
):
    """
    显示当前配置
    """
    config = get_config()

    console.print(
        Panel.fit(
            f"[bold cyan]ArXiv Follow 配置[/bold cyan]\n"
            f"版本: {config.app_version}\n"
            f"调试模式: {config.debug}\n"
            f"日志级别: {config.get_effective_log_level()}\n"
            f"存储后端: {config.storage.backend.value}\n"
            f"数据目录: {config.storage.data_dir}\n"
            f"输出目录: {config.storage.output_dir}",
            title="基础配置",
        )
    )

    # 功能状态
    features = [
        ("AI分析", config.is_feature_enabled("ai_analysis")),
        ("翻译服务", config.is_feature_enabled("translation")),
        ("滴答清单", config.is_feature_enabled("dida")),
        ("通知", config.is_feature_enabled("notifications")),
        ("每日检查", config.is_feature_enabled("daily_check")),
        ("周报", config.is_feature_enabled("weekly_summary")),
        ("主题搜索", config.is_feature_enabled("topic_search")),
    ]

    feature_table = Table(title="功能状态", show_header=True)
    feature_table.add_column("功能", style="cyan")
    feature_table.add_column("状态", style="green")

    for feature_name, enabled in features:
        status = "[green]✅ 启用[/green]" if enabled else "[red]❌ 禁用[/red]"
        feature_table.add_row(feature_name, status)

    console.print(feature_table)

    # API配置
    api_info = f"ArXiv API: {config.api.arxiv_base_url}\n"
    api_info += f"请求延迟: {config.api.arxiv_delay_seconds}秒\n"

    if show_sensitive:
        api_info += f"OpenRouter API: {'已配置' if config.api.openrouter_api_key else '未配置'}\n"
        api_info += (
            f"滴答清单: {'已配置' if config.api.dida_access_token else '未配置'}\n"
        )
    else:
        api_info += "使用 --show-sensitive 显示API配置状态"

    console.print(Panel.fit(api_info, title="API配置"))


@app.command("test")
def test_connection():
    """
    测试系统连接
    """

    async def run_test():
        config = get_config()

        console.print("[bold cyan]🧪 测试系统连接[/bold cyan]\n")

        tests = [
            ("ArXiv API连接", test_arxiv_connection),
            ("配置验证", test_config_validation),
        ]

        if config.is_feature_enabled("ai_analysis"):
            tests.append(("AI服务连接", test_ai_connection))

        if config.is_feature_enabled("dida"):
            tests.append(("滴答清单连接", test_dida_connection))

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[progress.description]正在测试: {test_name}"),
                console=console,
            ) as progress:
                task = progress.add_task("", total=None)

                try:
                    await test_func(config)
                    progress.update(task, completed=True)
                    console.print(f"[green]✅ {test_name}: 通过[/green]")
                    passed += 1
                except Exception as e:
                    progress.update(task, completed=True)
                    console.print(f"[red]❌ {test_name}: 失败 - {e}[/red]")

        console.print(f"\n[bold]测试结果: {passed}/{total} 通过[/bold]")

        if passed == total:
            console.print("[green]🎉 所有测试通过，系统状态良好！[/green]")
        else:
            console.print("[yellow]⚠️ 部分测试失败，请检查配置[/yellow]")
            raise typer.Exit(1)

    asyncio.run(run_test())


# 测试函数
async def test_arxiv_connection(config: AppConfig):
    """测试ArXiv连接"""
    async with ArxivCollector(config) as collector:
        result = await collector.search_by_query("cat:cs.AI", max_results=1)
        if not result.papers:
            raise Exception("无法获取测试论文")


async def test_config_validation(config: AppConfig):
    """测试配置验证"""
    if not config.storage.data_dir:
        raise Exception("数据目录未配置")

    # 尝试创建目录
    data_path = Path(config.storage.data_dir)
    data_path.mkdir(parents=True, exist_ok=True)


async def test_ai_connection(config: AppConfig):
    """测试AI服务连接"""
    if not config.api.openrouter_api_key:
        raise Exception("OpenRouter API密钥未配置")
    # TODO: 实际测试API连接


async def test_dida_connection(config: AppConfig):
    """测试滴答清单连接"""
    if not config.api.dida_access_token:
        raise Exception("滴答清单访问令牌未配置")
    # TODO: 实际测试API连接


if __name__ == "__main__":
    app()

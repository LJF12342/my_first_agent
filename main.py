#!/usr/bin/env python3
import os
import sys

# 确保 src 目录可导入
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

"""Deep Research Agent CLI — 基于 LangGraph 的自我反思研究助手。"""

import sys
import json
import time

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich import box

from src.my_first_agent.config import settings
from src.my_first_agent.graph.graph import app

console = Console()


# ─── 辅助函数 ─────────────────────────────────────────────

def print_banner():
    """打印启动横幅。"""
    banner = """
╔══════════════════════════════════════════════╗
║       🧠  Deep Research Agent  🧠            ║
║    基于 LangGraph · DeepSeek · DuckDuckGo    ║
╚══════════════════════════════════════════════╝
"""
    console.print(banner, style="bold cyan")
    console.print(f"模型: {settings.deepseek_model}", style="dim")
    console.print(f"最大修订次数: {settings.deepseek_model}", style="dim")
    console.print("")


def stream_graph_progress(state: dict):
    """运行 LangGraph 并实时显示进度。"""
    steps_display = {
        "plan": ("📋 制定研究计划...", "正在将问题拆解为可执行的子问题和搜索策略"),
        "search": ("🔍 执行网络搜索...", "正在对各个子问题进行 DuckDuckGo 搜索"),
        "analyze": ("📊 分析搜索结果...", "正在让 DeepSeek 从搜索结果中提炼信息"),
        "draft": ("✍️ 撰写报告初稿...", "正在基于收集的信息撰写研究报告"),
        "reflect": ("🧐 自我评审中...", "正在从完整性、准确性等维度评价报告质量"),
        "revise": ("🔄 修订报告中...", "正在根据评审意见改进报告"),
    }

    """运行 LangGraph 并实时显示进度，返回最终状态。"""
    config = {"recursion_limit": 50}
    current_state = dict(state)  # 拷贝一份，逐步累积

    for event in app.stream(state, config=config):
        for node_name, output in event.items():
            if not output:
                continue
            # 更新累积状态
            current_state.update(output)
            if node_name in steps_display:
                title, desc = steps_display[node_name]
                with console.status(f"[bold cyan]{title}[/]", spinner="dots"):
                    console.print(f"  └─ {desc}", style="dim")

    return current_state


def format_reflection_result(reflection_str: str | None) -> str:
    """将评审结果格式化为可读文本。"""
    if not reflection_str:
        return "未进行自我评审"
    try:
        ref = json.loads(reflection_str)
        scores = ref.get("scores", {})
        parts = [
            f"完整性: {scores.get('completeness', '?')}/10",
            f"准确性: {scores.get('accuracy', '?')}/10",
            f"结构性: {scores.get('structure', '?')}/10",
            f"客观性: {scores.get('objectivity', '?')}/10",
        ]
        return " · ".join(parts)
    except json.JSONDecodeError:
        return "评审结果解析失败"


def run_single_query(question: str):
    """对单条查询执行完整的研究流程。"""
    initial_state = {
        "question": question,
        "plan": None,
        "search_results": [],
        "findings": None,
        "draft": None,
        "reflection": None,
        "revision_count": 0,
        "max_revisions": 2,
        "final_report": None,
        "messages": [],
    }

    console.print(Panel(f"[bold]研究问题[/]\n{question}", border_style="cyan"))

    result = stream_graph_progress(initial_state)

    # 提取最终结果
    draft = result.get("draft")
    reflection = result.get("reflection")
    revision_count = result.get("revision_count", 0)

    if draft:
        console.print("\n")
        console.print(Panel(
            Markdown(draft),
            title=f"[bold green]📄 研究报告[/] (修订 {revision_count} 次)",
            border_style="green",
        ))

    if reflection:
        score_text = format_reflection_result(reflection)
        console.print(f"\n[dim]自我评审: {score_text}[/]")

    return draft


# ─── 主入口 ──────────────────────────────────────────────

def main():
    print_banner()

    if not settings.deepseek_api_key:
        console.print("[bold red]❌ 未配置 DeepSeek API Key![/]")
        console.print("请创建 .env 文件并添加:")
        console.print("  DEEPSEEK_API_KEY=sk-your-key-here", style="yellow")
        console.print("参考 .env.example 文件\n")
        sys.exit(1)

    # 判断是交互模式还是单次查询模式
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        run_single_query(question)
    else:
        console.print("[dim]输入研究问题（或输入 quit 退出）[/]\n")
        while True:
            try:
                question = console.input("[bold cyan]🧠 研究问题 > [/]").strip()
                if question.lower() in ("quit", "exit", "q"):
                    console.print("\n[bold]👋 再见！[/]")
                    break
                if not question:
                    continue
                run_single_query(question)
                console.print("\n" + "─" * 60 + "\n")
            except KeyboardInterrupt:
                console.print("\n\n[bold]👋 再见！[/]")
                break


if __name__ == "__main__":
    main()

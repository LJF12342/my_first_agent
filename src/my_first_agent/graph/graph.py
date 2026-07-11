"""LangGraph 图构建与编译。"""

from langgraph.graph import StateGraph, END

from .state import ResearchState
from .nodes import (
    plan_research,
    execute_search,
    analyze_results,
    draft_report,
    reflect_on_report,
    revise_report,
    router,
)


def build_research_graph() -> StateGraph:
    """构建并编译研究 Agent 的 LangGraph。

    图结构:

        ┌──────┐
        │ plan │——制定研究计划
        └──┬───┘
           ▼
        ┌────────┐
        │ search │——执行网络搜索
        └───┬────┘
            ▼
        ┌─────────┐
        │ analyze │——分析搜索结果
        └───┬─────┘
            ▼
        ┌────────┐
        │ draft  │——撰写报告初稿
        └───┬────┘
            ▼
        ┌──────────┐
        │ reflect  │——自我评审
        └───┬──────┘
            │
       ┌────┼────┬────────┐
       │    │    │        │
       ▼    ▼    ▼        ▼
    结束  revise search  结束
           │
           ▼
        reflect (循环)
    """
    workflow = StateGraph(ResearchState)

    # ── 注册节点 ──
    workflow.add_node("plan", plan_research)
    workflow.add_node("search", execute_search)
    workflow.add_node("analyze", analyze_results)
    workflow.add_node("draft", draft_report)
    workflow.add_node("reflect", reflect_on_report)
    workflow.add_node("revise", revise_report)

    # ── 入口 ──
    workflow.set_entry_point("plan")

    # ── 顺序边 ──
    workflow.add_edge("plan", "search")
    workflow.add_edge("search", "analyze")
    workflow.add_edge("analyze", "draft")
    workflow.add_edge("draft", "reflect")

    # ── 条件边（自我反思循环的核心） ──
    workflow.add_conditional_edges(
        "reflect",
        router,
        {
            "end": END,
            "revise": "revise",
            "search": "search",
        },
    )

    # revise 后回到 reflect 再次检查
    workflow.add_edge("revise", "reflect")

    return workflow.compile()


# 方便直接 import
app = build_research_graph()

__all__ = ["build_research_graph", "app"]

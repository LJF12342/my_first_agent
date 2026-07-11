"""LangGraph 状态定义。"""

from typing import Any, Optional
from typing_extensions import TypedDict


class ResearchState(TypedDict):
    """Agent 的状态图定义。

    字段：
    - question:         用户输入的原始问题
    - plan:             JSON 格式的研究计划
    - search_results:   每次搜索的原始结果列表
    - findings:         分析后的结构化发现
    - draft:            报告初稿
    - reflection:       JSON 格式的自我评审
    - revision_count:   已修订次数
    - final_report:     最终输出报告
    - messages:         LangChain 内部消息
    """

    question: str
    plan: Optional[str]
    search_results: list[dict]
    findings: Optional[str]
    draft: Optional[str]
    reflection: Optional[str]
    revision_count: int
    max_revisions: int
    final_report: Optional[str]
    messages: list[Any]

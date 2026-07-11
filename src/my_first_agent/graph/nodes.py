"""LangGraph 各阶段节点函数。"""

import json
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..llm import get_llm
from ..prompts.prompts import (
    PLAN_PROMPT,
    ANALYZE_PROMPT,
    DRAFT_PROMPT,
    REFLECT_PROMPT,
    REVISE_PROMPT,
)
from ..tools import search_web, fetch_web_content

from .state import ResearchState


# ─── helpers ──────────────────────────────────────────────

def extract_json(text: str) -> dict:
    """从 LLM 输出中提取 JSON，兼容 markdown 代码块包裹的情况。"""
    # 尝试 ```json ... ```
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if m:
        text = m.group(1)
    text = text.strip()
    return json.loads(text)


def _prompt_chain(template: str):
    """快捷创建 prompt -> llm -> parser 链。"""
    prompt = ChatPromptTemplate.from_messages([("system", template)])
    return prompt | get_llm() | StrOutputParser()


# ─── 节点逻辑 ─────────────────────────────────────────────

def plan_research(state: ResearchState) -> dict:
    """制定研究计划——将用户问题拆解为子问题和搜索关键词。"""
    chain = _prompt_chain(PLAN_PROMPT)
    result = chain.invoke({"question": state["question"]})
    plan = extract_json(result)
    return {"plan": json.dumps(plan, ensure_ascii=False)}


def execute_search(state: ResearchState) -> dict:
    """执行搜索——对每个子问题逐一搜索。"""
    plan = json.loads(state["plan"])
    sub_questions = plan.get("sub_questions", [])

    existing = state.get("search_results") or []
    already_urls = {r["link"] for r in existing if r.get("link")}

    all_results = list(existing)

    for idx, sq in enumerate(sub_questions):
        keywords = sq.get("search_keywords") or [sq["question"]]
        for kw in keywords:
            results = search_web(kw)
            for r in results:
                r["sub_question_index"] = idx
                if r.get("link") and r["link"] not in already_urls:
                    all_results.append(r)
                    already_urls.add(r["link"])

    return {"search_results": all_results}


def analyze_results(state: ResearchState) -> dict:
    """分析搜索结果——让 LLM 从搜索结果中提炼结构化发现。"""
    plan = json.loads(state["plan"])
    sub_questions = plan.get("sub_questions", [])

    chain = _prompt_chain(ANALYZE_PROMPT)
    findings = []

    search_results = state.get("search_results") or []

    for sq in sub_questions:
        idx = sub_questions.index(sq)
        relevant = [r for r in search_results if r.get("sub_question_index") == idx]
        if not relevant:
            continue

        results_text = "\n\n".join(
            f"[{j + 1}] {r['title']}\n    链接: {r['link']}\n    摘要: {r['snippet']}"
            for j, r in enumerate(relevant)
        )

        raw = chain.invoke({
            "question": state["question"],
            "sub_question": sq["question"],
            "search_results": results_text,
        })

        try:
            parsed = extract_json(raw)
        except json.JSONDecodeError:
            parsed = {"findings": [{"claim": raw, "source_index": 0, "confidence": "medium"}], "info_gaps": [], "summary": ""}

        parsed["sub_question"] = sq["question"]
        findings.append(parsed)

    return {"findings": json.dumps(findings, ensure_ascii=False)}


def draft_report(state: ResearchState) -> dict:
    """撰写初稿——基于信息分析和发现生成结构化报告。"""
    chain = _prompt_chain(DRAFT_PROMPT)
    result = chain.invoke({
        "question": state["question"],
        "plan": state["plan"],
        "findings": state["findings"],
    })
    return {"draft": result}


def reflect_on_report(state: ResearchState) -> dict:
    """自我评审——LLM 从完整性、准确性等维度批判自己的输出。"""
    chain = _prompt_chain(REFLECT_PROMPT)
    result = chain.invoke({
        "question": state["question"],
        "plan": state["plan"],
        "draft": state["draft"],
    })
    reflection = extract_json(result)
    return {"reflection": json.dumps(reflection, ensure_ascii=False)}


def revise_report(state: ResearchState) -> dict:
    """修订报告——根据评审意见改进报告。"""
    chain = _prompt_chain(REVISE_PROMPT)
    result = chain.invoke({
        "question": state["question"],
        "draft": state["draft"],
        "reflection": state["reflection"],
    })
    return {
        "draft": result,
        "revision_count": (state.get("revision_count") or 0) + 1,
    }


def router(state: ResearchState) -> str:
    """条件路由——根据评审结果决定下一步。"""
    reflection_raw = state.get("reflection")
    if not reflection_raw:
        return "end"

    try:
        reflection = json.loads(reflection_raw)
    except (json.JSONDecodeError, TypeError):
        return "end"

    revision_count = state.get("revision_count") or 0
    max_revisions = state.get("max_revisions") or 2

    if revision_count >= max_revisions:
        return "end"
    if reflection.get("needs_more_research"):
        return "search"
    if reflection.get("needs_revision"):
        return "revise"
    return "end"

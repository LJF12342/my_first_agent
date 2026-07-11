"""输出格式化工具。"""

import json


def format_search_results(results: list[dict], indent: str = "") -> str:
    """将搜索结果格式化为可读文本。"""
    if not results:
        return f"{indent}(无结果)"
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{indent}[{i}] {r.get('title', '(无标题)')}")
        lines.append(f"{indent}    链接: {r.get('link', '')}")
        lines.append(f"{indent}    摘要: {r.get('snippet', '')[:200]}")
    return "\n".join(lines)


def format_report(report: str | None) -> str:
    """格式化最终报告的标题分隔线。"""
    if not report:
        return "(报告为空)"
    return report


def format_status(step: str, detail: str = "") -> str:
    """格式化 Agent 状态消息。"""
    emoji_map = {
        "plan": "📋",
        "search": "🔍",
        "analyze": "📊",
        "draft": "✍️",
        "reflect": "🧐",
        "revise": "🔄",
        "final": "✅",
        "error": "❌",
    }
    emoji = emoji_map.get(step, "🤖")
    msg = f"{emoji} {detail}" if detail else f"{emoji}"
    return msg


def pretty_json(obj) -> str:
    """将对象格式化为漂亮的 JSON 字符串。"""
    return json.dumps(obj, ensure_ascii=False, indent=2)

from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class ToolResult:
    success: bool
    output: str
    error: str | None = None


class Tool:
    """一个可被 Agent 调用的工具。"""

    def __init__(
        self,
        name: str,
        description: str,
        fn: Callable[..., ToolResult],
    ):
        self.name = name
        self.description = description
        self.fn = fn

    def run(self, **kwargs) -> ToolResult:
        try:
            return self.fn(**kwargs)
        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))

    def to_openai_tool(self) -> dict:
        """转换为 OpenAI function calling 格式。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {"type": "object", "properties": {}},
            },
        }

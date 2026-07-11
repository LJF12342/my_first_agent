"""Agent 核心：一个基于 ReAct 模式的简单智能体。"""

from typing import Callable

from .tools import Tool, ToolResult


class Agent:
    """一个简单的智能体，使用 ReAct（推理-行动）模式工作。"""

    def __init__(self, name: str = "Agent"):
        self.name = name
        self.tools: dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        """注册一个工具供 Agent 使用。"""
        self.tools[tool.name] = tool

    def get_tool_list(self) -> list[dict]:
        """返回 OpenAI 格式的工具列表。"""
        return [t.to_openai_tool() for t in self.tools.values()]

    async def run(self, user_input: str, llm_call: Callable) -> str:
        """运行 Agent：接收输入，调用 LLM，执行工具，返回结果。"""
        messages = [
            {"role": "system", "content": f"你是 {self.name}，一个有用的 AI 助手。"},
            {"role": "user", "content": user_input},
        ]

        for step in range(10):
            response = await llm_call(messages, self.get_tool_list())

            choice = response.choices[0]
            msg = choice.message

            if not msg.tool_calls:
                return msg.content or ""

            messages.append(msg)

            for tc in msg.tool_calls:
                tool = self.tools.get(tc.function.name)
                if tool is None:
                    result = ToolResult(
                        success=False,
                        output="",
                        error=f"未知工具: {tc.function.name}",
                    )
                else:
                    result = tool.run()

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result.output,
                    }
                )

        return "已达最大步骤数。"

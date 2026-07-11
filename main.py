"""My First Agent — 入口点。"""

import asyncio

from my_first_agent import Agent, Tool, ToolResult


def get_current_time() -> ToolResult:
    """获取当前时间的工具。"""
    from datetime import datetime

    now = datetime.now()
    return ToolResult(
        success=True,
        output=f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}",
    )


def greet_user() -> ToolResult:
    """打招呼的工具。"""
    return ToolResult(success=True, output="你好！我是你的第一个 AI Agent 🤖")


async def main():
    agent = Agent(name="我的第一个 Agent")

    # 注册工具
    agent.register_tool(
        Tool(
            name="get_current_time",
            description="获取当前的日期和时间",
            fn=get_current_time,
        )
    )
    agent.register_tool(
        Tool(
            name="greet_user",
            description="向用户打招呼",
            fn=greet_user,
        )
    )

    print(f"🤖 {agent.name} 已启动！")
    print("=" * 40)

    print("\n可用命令: time, greet, hello, quit")
    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            print("👋 再见！")
            break
        elif user_input.lower() in ("time", "现在几点"):
            result = get_current_time()
            print(f"🤖 {result.output}")
        elif user_input.lower() in ("greet", "hello", "你好"):
            result = greet_user()
            print(f"🤖 {result.output}")
        else:
            print(f"🤖 你说: 「{user_input}」— 我还不知道如何回答，但我正在学习！")


if __name__ == "__main__":
    asyncio.run(main())

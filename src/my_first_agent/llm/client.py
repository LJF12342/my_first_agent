"""DeepSeek LLM 客户端封装。"""

from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from ..config import settings


def get_llm(**kwargs: dict) -> BaseChatModel:
    """获取非流式的 DeepSeek Chat 实例。

    用法:
        llm = get_llm()
        response = llm.invoke([HumanMessage(content="你好")])
    """
    merged = {**settings.llm_kwargs, **kwargs}
    return ChatOpenAI(**merged, streaming=False)


def get_llm_streaming(**kwargs: dict) -> BaseChatModel:
    """获取流式的 DeepSeek Chat 实例（用于实时输出）。"""
    merged = {**settings.llm_kwargs, **kwargs}
    return ChatOpenAI(**merged, streaming=True)

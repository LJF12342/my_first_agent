"""DuckDuckGo 搜索封装。"""

from ..config import settings


def search_web(query: str, max_results: int | None = None) -> list[dict]:
    """通过网络搜索指定查询，返回结果列表。

    每个结果包含:
    - title: 页面标题
    - link: 页面链接
    - snippet: 页面摘要
    """
    k = max_results or settings.search_max_results
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=k))

        results = []
        for item in raw:
            results.append(
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", item.get("href", "")),
                    "snippet": item.get("body", item.get("snippet", "")),
                }
            )
        return results

    except ImportError:
        return [
            {
                "title": f"搜索结果: {query}",
                "link": "",
                "snippet": f"需要安装 duckduckgo-search: pip install duckduckgo-search",
            }
        ]
    except Exception as e:
        return [{"title": "搜索失败", "link": "", "snippet": f"错误: {e!s}"}]

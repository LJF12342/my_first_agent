"""网页内容抓取工具。"""

import httpx
from bs4 import BeautifulSoup


def fetch_web_content(url: str, timeout: float = 15.0) -> str | None:
    """抓取指定网页的正文内容。

    返回纯文本内容（去除 HTML 标签），失败时返回 None。
    """
    if not url:
        return None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        # 移除无关元素
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        lines = [ln for ln in text.splitlines() if ln.strip()]

        # 限制长度避免 token 超限
        content = "\n".join(lines[:200])
        return content

    except Exception as e:
        return f"[抓取失败: {e!s}]"

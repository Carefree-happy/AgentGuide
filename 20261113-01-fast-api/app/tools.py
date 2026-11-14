import urllib.request
import urllib.error

from langchain.tools import tool


@tool
def add(a: int, b: int) -> int:
    """计算两个整数的和。"""
    return a + b


@tool
def fetch_text_from_url(url: str) -> str:
    """
    Download a complete plain-text document from a URL.
    Return the original text without modifying its contents.
    """
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
            return raw.decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        return f"Fetch failed: {e}"
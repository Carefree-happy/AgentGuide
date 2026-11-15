import urllib.request
import urllib.error
import ssl
import certifi
import os

from langchain.tools import tool


@tool
def add(a: int, b: int) -> int:
    """计算两个整数的和。"""
    return a + b


@tool
def fetch_text_from_url(url: str) -> str:
    """
    Fetch webpage text, then use LLM to summarize the content.
    Returns both raw text and summary as markdown.
    """

    # 打印当前环境代理，用来排查是不是LangGraph thread上下文注入了代理
    http_proxy = os.environ.get("HTTP_PROXY")
    https_proxy = os.environ.get("HTTPS_PROXY")
    no_proxy = os.environ.get("NO_PROXY")
    print(f"[fetch debug] HTTP_PROXY={http_proxy}")
    print(f"[fetch debug] HTTPS_PROXY={https_proxy}")
    print(f"[fetch debug] NO_PROXY={no_proxy}")

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )

    context = ssl.create_default_context(cafile=certifi.where())

    try:
        with urllib.request.urlopen(req, timeout=120, context=context) as resp:
            raw = resp.read()
            return raw.decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        # 细分类型，方便区分证书报错 / reset / 超时
        if isinstance(e.reason, ssl.SSLCertVerificationError):
            return f"[SSL Cert Error] Fetch failed: {e}"
        elif isinstance(e.reason, OSError) and "Connection reset" in str(e.reason):
            return f"[TLS Reset] Fetch failed: {e}"
        elif isinstance(e.reason, TimeoutError):
            return f"[Timeout] Fetch failed: {e}"
        else:
            return f"[URLError] Fetch failed: {e}"


@tool
def calc_text_stats(text: str) -> str:
    """
    Calculate text statistics from raw text.
    Stats: total lines, lines with "Gatsby", count "Gatsby", first line of "Daisy", lines with "Daisy", count "Daisy".
    Case-sensitive.
    """
    lines = text.splitlines()
    total_lines = len(lines)
    gatsby_lines = [i+1 for i, l in enumerate(lines) if "Gatsby" in l]
    gatsby_count = text.count("Gatsby")
    daisy_lines = [i+1 for i, l in enumerate(lines) if "Daisy" in l]
    daisy_count = text.count("Daisy")
    first_daisy_line = daisy_lines[0] if daisy_lines else None

    out = (
        f"total_lines={total_lines}\n"
        f"gatsby_matching_lines={len(gatsby_lines)}\n"
        f"gatsby_occurrences={gatsby_count}\n"
        f"first_daisy_line={first_daisy_line}\n"
        f"daisy_matching_lines={len(daisy_lines)}\n"
        f"daisy_occurrences={daisy_count}"
    )
    return out
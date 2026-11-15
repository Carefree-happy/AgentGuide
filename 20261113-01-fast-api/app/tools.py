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
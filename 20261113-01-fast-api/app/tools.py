from langchain.tools import tool


@tool
def add(a: int, b: int) -> int:
    """计算两个整数的和。"""
    return a + b

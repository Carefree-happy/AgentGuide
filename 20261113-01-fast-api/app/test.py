
from config import model
from tools import add
from utils import invoke_until_complete, timed_call


TOOLS = [add]
PROMPT = "请使用 add 工具计算 123 + 456，不要直接计算。"


def test_model_connection():
    return test_tool_calling()


def test_tool_calling():
    return invoke_until_complete(
        model,
        PROMPT,
        tools=TOOLS,
    )


if __name__ == "__main__":
    result = timed_call(
        "模型工具测试",
        test_tool_calling
    )

    print(result.content)

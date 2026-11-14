
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain_core.messages import ToolMessage

from model import model
from tools import fetch_text_from_url
from utils import timed_call


GUTENBERG_URL = "https://www.gutenberg.org/files/64317/64317-0.txt"

def test_tool_calling():
    return invoke_until_complete(
        model,
        PROMPT,
        tools=TOOLS,
    )

def test_agent_fetch_text():
    agent = create_agent(
        model=model,
        tools=[fetch_text_from_url],
        system_prompt=(
            "Call fetch_text_from_url exactly once to retrieve the requested "
            "document. After receiving the text, report its character length. "
            "Do not call any other tool."
        ),
        middleware=[
            ToolCallLimitMiddleware(
                tool_name="fetch_text_from_url",
                run_limit=1,
                exit_behavior="error",
            )
        ],
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Fetch this document and tell me the text length: "
                        f"{GUTENBERG_URL}"
                    ),
                }
            ]
        }
    )

    tool_results = [
        message
        for message in result["messages"]
        if isinstance(message, ToolMessage)
        and message.name == "fetch_text_from_url"
    ]
    if len(tool_results) != 1:
        raise RuntimeError(
            "Agent must call fetch_text_from_url exactly once; "
            f"observed {len(tool_results)} calls"
        )

    text = tool_results[0].content
    if not isinstance(text, str):
        raise TypeError("fetch_text_from_url did not return text")
    if text.startswith("Fetch failed:"):
        raise RuntimeError(text)

    print(f"文本长度（字符数）: {len(text)}")
    final_message = result["messages"][-1]
    print(final_message.content)
    return len(text)


if __name__ == "__main__":
    result = timed_call(
        "Agent fetch 文本",
        test_agent_fetch_text,
    )

    print(f"最终文本长度: {result}")

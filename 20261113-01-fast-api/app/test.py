from utils import invoke_until_complete
from utils import timed_call
from agent import agent


GUTENBERG_URL = "https://www.gutenberg.org/files/64317/64317-0.txt"

# 拿到文本，获取长度
def test_agent_fetch_text():
    result = invoke_until_complete(
        agent,
        prompt = (
            f"Fetch this document and tell me the text length: {GUTENBERG_URL}. "
            "Only output the numeric length value, no other words. "
            "Append <END_OF_ANSWER> right after the number. "
        )
    )
    return result

if __name__ == "__main__":
    result = timed_call(
        "Agent fetch 文本",
        test_agent_fetch_text,
    )

    print(f"最终文本长度: {result.content}")

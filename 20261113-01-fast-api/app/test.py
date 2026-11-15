from utils import invoke_until_complete
from utils import timed_call
from agent import agent


GUTENBERG_URL = "https://www.gutenberg.org/files/64317/64317-0.txt"

user_content = f"""
# Project: The Great Gatsby Literary Research
Source: {GUTENBERG_URL}
Analyze the complete Gutenberg text.

Tasks:
1. Use fetch_text_from_url to download the complete text.
2. Use calc_text_stats to compute exact statistics.
3. Character analysis of Jay Gatsby, Daisy Buchanan, Nick Carraway, Tom Buchanan, Jordan Baker.
4. Chapter structure and summary.
5. Final Markdown report with stats, character analysis, chapter summaries, synopsis, limitations.
No shell, no filesystem. Use the provided tools only.
"""

user_config = {"configurable": {"thread_id": "gatsby-plain-agent"}}

# 拿到文本，获取长度
def test_agent_fetch_text():
    result = invoke_until_complete(
        agent,
        prompt = user_content,
        max_rounds = 5,
        max_attempts_per_call = 8,
        agent_config = user_config
    )
    return result

if __name__ == "__main__":
    result = timed_call(
        "Agent fetch 文本",
        test_agent_fetch_text,
    )

    print(f"最终文本长度: {result.content}")

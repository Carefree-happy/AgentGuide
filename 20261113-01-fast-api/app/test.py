from utils import run_agent_or_llm
from utils import timed_call
from agent import deep_agent
from prompts import DEEP_USER_CONTENT

user_config = {"configurable": {"thread_id": "gatsby-deep-agent-1"}}

# 拿到文本，获取长度
def test_agent_fetch_text():
    result = deep_agent.invoke(
        {"messages": [{"role": "user", "content": DEEP_USER_CONTENT}]},
        config=user_config
    )
    return result

if __name__ == "__main__":
    result = timed_call(
        "Agent fetch 文本",
        test_agent_fetch_text,
    )

    print(f"最终文本长度: {result.content}")

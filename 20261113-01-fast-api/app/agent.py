from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import ToolCallLimitMiddleware


from model import model
from tools import fetch_text_from_url, calc_text_stats

SYSTEM_PROMPT = """
You are a literary research assistant.
Rules:
1. Never fabricate statistics, line numbers, or quotations.
2. Distinguish verified facts from literary interpretations.
3. Use tools to obtain evidence.
4. For exact text statistics, use deterministic computation.
5. When evidence is unavailable, explicitly report the limitation.
6. Produce a structured and concise research report.
"""

TOOLS = [fetch_text_from_url, calc_text_stats]

agent_checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=agent_checkpointer,
    middleware=[
        ToolCallLimitMiddleware(
            tool_name="fetch_text_from_url",
            run_limit=10,
            exit_behavior="error",
        )
    ],
)
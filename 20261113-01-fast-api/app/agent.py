from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import ToolCallLimitMiddleware


from model import model
from tools import fetch_text_from_url, calc_text_stats

SYSTEM_PROMPT = """
Call fetch_text_from_url exactly once to retrieve the requested 
document. After receiving the text, report its character length. 
Do not call any other tool. 
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
            run_limit=1,
            exit_behavior="error",
        )
    ],
)
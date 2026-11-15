from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import ToolCallLimitMiddleware, TodoListMiddleware

from deepagents import create_deep_agent
from bashkit.deepagents import BashkitBackend

from model import model
from prompts import SYSTEM_PROMPT, SUBAGENTS
from tools import fetch_text_from_url, calc_text_stats


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

deep_checkpointer = InMemorySaver()

backend = BashkitBackend(timeout_seconds=60)

fetch_limit_mw = ToolCallLimitMiddleware(
    tool_name="fetch_text_from_url",
    run_limit=5,
    exit_behavior="error",
)

todolist_mw = TodoListMiddleware(
    # system_prompt="使用 write_todos 维护任务清单"
)

deep_agent = create_deep_agent(
    model=model,
    tools=TOOLS,
    backend=backend,
    system_prompt=SYSTEM_PROMPT,
    middleware=[
        fetch_limit_mw
    ],
    subagents=SUBAGENTS
)
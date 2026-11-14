import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain.chat_models import init_chat_model
from langchain.tools import tool

from deepagents import create_deep_agent
from bashkit.deepagents import BashkitBackend

from langgraph.checkpoint.memory import InMemorySaver

from app.tools import add


load_dotenv()


# ============================================================
# 1. Configuration
# ============================================================

GUTENBERG_URL = (
    "https://www.gutenberg.org/files/64317/64317-0.txt"
)

MODEL_NAME = os.getenv("QINIU")

MODEL_URL = os.getenv("QINIU_URL")

AGENT_KEY = os.getenv("QINIU_API_KEY")

SYSTEM_PROMPT = """
You are a literary research assistant.

Your task is to analyze complete literary documents.

Rules:

1. Never fabricate statistics, line numbers, or quotations.
2. Distinguish verified facts from literary interpretations.
3. Use tools to obtain evidence.
4. For exact text statistics, use deterministic computation.
5. When evidence is unavailable, explicitly report the limitation.
6. Produce a structured and concise research report.
"""


# ============================================================
# 2. Model
# ============================================================

model = init_chat_model(
    MODEL_NAME,
    model_provider="openai",
    temperature=0,
    timeout=600,
    max_tokens=8192,
    base_url=MODEL_URL,
    api_key=AGENT_KEY,
)


# ============================================================
# 3. Shared tool
# ============================================================

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
        with urllib.request.urlopen(
            req,
            timeout=120
        ) as resp:
            raw = resp.read()

        return raw.decode(
            "utf-8",
            errors="replace"
        )

    except urllib.error.URLError as e:
        return f"Fetch failed: {e}"


shared_tools = [
    fetch_text_from_url,
    add,
]


# ============================================================
# 4. Ordinary Agent
# ============================================================

agent_checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=shared_tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=agent_checkpointer,
)


# ============================================================
# 5. Deep Agent
# ============================================================

deep_checkpointer = InMemorySaver()

# A real execution environment.
backend = BashkitBackend(
    timeout_seconds=60
)

deep_agent = create_deep_agent(
    model=model,
    tools=shared_tools,
    backend=backend,
    system_prompt=SYSTEM_PROMPT,

    # Explicitly enable planning.
    # Newer DeepAgents versions no longer include
    # TodoListMiddleware by default.
    middleware=[
        TodoListMiddleware()
    ],

    # Specialized subagents.
    subagents=[
        {
            "name": "character_analyst",
            "description": (
                "Analyze the main characters, "
                "their relationships and motivations."
            ),
            "system_prompt": """
            You are a literary character analyst.

            Analyze the characters in The Great Gatsby.
            Identify their relationships, motivations,
            conflicts and narrative roles.

            Support interpretations with evidence.
            Do not invent quotations.
            """,
        },
        {
            "name": "chapter_analyst",
            "description": (
                "Analyze the chapters and summarize "
                "the major events of the novel."
            ),
            "system_prompt": """
            You are a literary chapter analyst.

            Identify chapter boundaries and summarize
            the major events of each chapter.

            Use the source document as evidence.
            Do not invent chapter information.
            """,
        },
    ],
)


# ============================================================
# 6. Research task
# ============================================================

content = f"""
# Project: The Great Gatsby Literary Research

Source:
{GUTENBERG_URL}

Analyze the complete Gutenberg text.

Your tasks:

## Task 1: Acquire the source

Use fetch_text_from_url to download the complete text.

Do not assume that the document has been successfully
downloaded until you have verified the tool result.

## Task 2: Preserve the source

Save the original document into your virtual filesystem:

/home/user/gatsby.txt

Do not modify the original document.

## Task 3: Exact text statistics

Use shell execution or deterministic text-processing
commands to calculate:

1. Total number of lines in the source.
2. Number of lines containing the case-sensitive
   substring "Gatsby".
3. Number of occurrences of "Gatsby".
4. The first 1-based line number containing "Daisy".
5. Number of lines containing "Daisy".
6. Number of occurrences of "Daisy".

For line counts, count matching lines rather than
occurrences.

Use the actual saved source file.

Do not estimate or calculate these values from memory.

## Task 4: Character analysis

Delegate character analysis to character_analyst.

Analyze at least:

- Jay Gatsby
- Daisy Buchanan
- Nick Carraway
- Tom Buchanan
- Jordan Baker

Explain their relationships and roles.

## Task 5: Chapter analysis

Delegate chapter analysis to chapter_analyst.

Identify the chapter structure and summarize
the major events.

## Task 6: Final report

Produce a Markdown report containing:

1. Source information
2. Verified text statistics
3. Main character analysis
4. Chapter summaries
5. A two-sentence neutral synopsis
6. Limitations and verification notes

All exact statistics must be supported by
actual execution results.

If you cannot verify a number, use null.

Never fabricate data.
"""


# ============================================================
# 7. Run experiments independently
# ============================================================

agent_result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": content,
            }
        ]
    },
    config={
        "configurable": {
            "thread_id": "gatsby-agent"
        }
    },
)

deep_agent_result = deep_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": content,
            }
        ]
    },
    config={
        "configurable": {
            "thread_id": "gatsby-deep-agent"
        }
    },
)


# ============================================================
# 8. Print results
# ============================================================

def print_trace(name, result):
    print(f"\n{'=' * 25} {name} {'=' * 25}")

    for index, message in enumerate(result["messages"]):
        print(f"\n--- Message {index} ---")
        print("Type:", message.type)

        if getattr(message, "name", None):
            print("Name:", message.name)

        if getattr(message, "tool_calls", None):
            print("Tool calls:", message.tool_calls)

        print("Content:", message.content)


print_trace("ORDINARY AGENT", agent_result)
print_trace("DEEP AGENT", deep_agent_result)

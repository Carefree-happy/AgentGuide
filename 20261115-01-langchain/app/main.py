import os
from langchain.agents import create_agent
from langchain.tools import tool


from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

def check_config(items: list):
    """
    批量校验配置项
    items 格式：[(变量值, 环境变量名, 展示名称), ...]
    """
    for value, env_name, display_name in items:
        if not value:
            raise RuntimeError(f"{display_name} 未配置")
        else:
            print(f"✅ {display_name} 已配置")

# 大模型
LLMS = "DEEPSEEK"

MODEL_ID = os.getenv(f"{LLMS}")
BASE_URL = os.getenv(f"{LLMS}_URL")
API_KEY = os.getenv(f"{LLMS}_API_KEY")

check_config([
    (API_KEY, f"{LLMS}_API_KEY", f"{LLMS}_API_KEY"),
    (BASE_URL, f"{LLMS}_URL", f"{LLMS}_URL"),
    (MODEL_ID, "MODEL_ID", LLMS)
])

model = init_chat_model(
    MODEL_ID,
    model_provider="openai",
    temperature=0,
    timeout=120,
    max_tokens=2048,
    base_url=BASE_URL,
    api_key=API_KEY,
)

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

tools = [search]

agent = create_agent(
    model, 
    tools,
    system_prompt="You are a helpful assistant. Be concise and accurate."
)

result = agent.invoke({"messages": [{"role": "user", "content": "Summarize AI trends"}]})

print(result)

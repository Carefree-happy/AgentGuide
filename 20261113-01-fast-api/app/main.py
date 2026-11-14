import os
from dotenv import load_dotenv
from fastapi import FastAPI

# 加载环境变量
load_dotenv()

# 遍历所有环境变量
import os
from dotenv import load_dotenv

load_dotenv()

# 定义需要读取的配置
api_keys = {
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "fireworks": "FIREWORKS_API_KEY",
    "baseten": "BASETEN_API_KEY",
    "ollama": "OLLAMA_API_KEY",
    "azure": "AZURE_OPENAI_API_KEY",
    "huggingface": "HUGGINGFACEHUB_API_TOKEN",
}

# 遍历
for provider, env_name in api_keys.items():
    api_key = os.getenv(env_name)

    if api_key:
        print(f"{provider}: {env_name}已配置")
    else:
        print(f"{provider}: {env_name}未配置")

app = FastAPI()


@app.get("/")
def hello():
    return {"msg": "ok"}
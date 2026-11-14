import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

API_KEY = os.getenv("QINIU_API_KEY")

BASE_URL = os.getenv("QINIU_URL")

MODEL_NAME = os.getenv("QINIU")

if not API_KEY:
    raise RuntimeError("QINIU_API_KEY 未配置")
else:
    print(f"✅ QINIU_API_KEY 已配置")

if not BASE_URL:
    raise RuntimeError("QINIU_URL 未配置")
else:
    print(f"✅ QINIU_URL 已配置")

if not MODEL_NAME:
    raise RuntimeError("QINIU 未配置")
else:
    print(f"✅ QINIU 已配置")

model = init_chat_model(
    MODEL_NAME,
    model_provider="openai",
    temperature=0,
    timeout=120,
    max_tokens=2048,
    base_url=BASE_URL,
    api_key=API_KEY,
)

# 添加重试机制
# model = model.with_retry(
#     retry_if_exception_type=(Exception),
#     stop_after_attempt=5,
#     wait_exponential_jitter=True,
# )

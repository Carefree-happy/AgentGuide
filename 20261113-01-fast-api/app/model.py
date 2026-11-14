import os

from utils import check_config
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# 大模型
LLMS = "QINIU"

API_KEY = os.getenv(f"{LLMS}_API_KEY")

BASE_URL = os.getenv(f"{LLMS}_URL")

MODEL_ID = os.getenv(f"{LLMS}")

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

# 添加重试机制
# model = model.with_retry(
#     retry_if_exception_type=(Exception),
#     stop_after_attempt=5,
#     wait_exponential_jitter=True,
# )

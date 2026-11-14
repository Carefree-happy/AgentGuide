
import os
import time

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

API_KEY = os.getenv("QINIU_API_KEY")

BASE_URL = os.getenv("QINIU_URL")

MODEL_NAME = os.getenv("QINIU")

if not API_KEY:
    raise RuntimeError("QINIU_API_KEY 未配置")
else:
    print(f"QINIU_API_KEY 已配置: {API_KEY}")

if not BASE_URL:
    raise RuntimeError("QINIU_URL 未配置")
else:
    print(f"QINIU_URL 已配置: {BASE_URL}")

if not MODEL_NAME:
    raise RuntimeError("QINIU 未配置")
else:
    print(f"QINIU 已配置: {MODEL_NAME}")

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
model = model.with_retry(
    retry_if_exception_type=(Exception,),
    stop_after_attempt=3,
    wait_exponential_jitter=True,
)


def timed_call(name, func):
    start = time.perf_counter()

    print(f"\n开始执行：{name}")

    try:
        result = func()
        elapsed = time.perf_counter() - start

        print(f"执行成功：{name}")
        print(f"耗时：{elapsed:.2f} 秒")

        return result

    except Exception as e:
        elapsed = time.perf_counter() - start

        print(f"执行失败：{name}")
        print(f"耗时：{elapsed:.2f} 秒")
        print(f"错误：{type(e).__name__}: {e}")

        raise


if __name__ == "__main__":
    result = timed_call(
        "模型连接测试",
        lambda: model.invoke("hello, my name is John! do you know the whether today is sunny or rainy?")
    )

    print(result.content)

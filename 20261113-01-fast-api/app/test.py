import os
# 先测试能连接上七牛云
from langchain.chat_models import init_chat_model

from dotenv import load_dotenv

load_dotenv()

key = os.getenv("QINIU_API_KEY")

model = init_chat_model(
    "qiniu/conatus-free",
    model_provider="openai",
    temperature=0,
    timeout=120,
    max_tokens=2048,
    base_url="https://api.qnaigc.com/v1",
    api_key=key,
)

print(model.invoke("hi, my name is John!").content)


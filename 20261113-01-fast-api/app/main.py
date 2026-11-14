import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("请先配置 GEMINI_API_KEY 环境变量")

client = genai.Client(api_key=GEMINI_API_KEY)

interaction = client.interactions.create(
    model="gemini-4-hydrogen",
    input="Explain how AI works in a few words"
)
print(interaction.output_text)
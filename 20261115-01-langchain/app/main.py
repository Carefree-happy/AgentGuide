import asyncio
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.zhipuai import ZhipuAIEmbedding

from llm import llm, API_KEY, ZHIPU_EMBEDDING

embed_model = ZhipuAIEmbedding(
    model="embedding-3",   # 推荐 embedding-3；老版本 embedding-2
    api_key=ZHIPU_EMBEDDING,
    dimensions=1024,       # embedding-3支持，embedding-2固定1024，不用传
    timeout=60
)

Settings.embed_model = embed_model

Settings.llm = llm


def multiply(a: float, b: float) -> float:
    """Useful for multiplying two numbers."""
    return a * b


async def search_documents(query: str) -> str:
    """Useful for answering natural language questions about an personal essay written by Paul Graham."""
    response = await query_engine.aquery(query)
    return str(response)


# Create a RAG tool using LlamaIndex
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

agent = FunctionAgent(
    tools=[multiply, search_documents],
    llm=llm,
    system_prompt="""You are a helpful assistant that can perform calculations and search through documents to answer questions.""",
)

async def main():
    response = await agent.run("What did the author do in college? Also, what's 7 * 8?")

    print(response)

asyncio.run(main())

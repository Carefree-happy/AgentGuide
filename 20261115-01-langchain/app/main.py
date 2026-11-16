import asyncio
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import Context
from llama_index.core.memory import Memory


from llm import llm


agent = FunctionAgent(
    tools=[],
    llm=llm,
    system_prompt="You are a helpful assistant.",
)

memory = Memory.from_defaults(session_id="test-session", token_limit=4000)

ctx = Context(agent)

async def main():
    response1 = await agent.run("My name is SUNJING", ctx=ctx, memory=memory)
    print(response1)
    print("Waiting for 2 seconds before asking the next question...")
    await asyncio.sleep(10) # 等待一秒，确保上下文保存到内存中
    response2 = await agent.run("What is my name?", ctx=ctx, memory=memory)
    print(response2)

asyncio.run(main())

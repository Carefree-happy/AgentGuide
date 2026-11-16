import asyncio
from llama_index.core.agent.workflow import FunctionAgent

from llm import llm

def multiply(nums: list[float]) -> float:
    """Useful for multiplying a batch of numbers.
    Args:
        nums: An array containing all numbers you want to multiply, e.g. [10,20,20,20,20]
    You MUST call this tool, do NOT compute manually.
    """
    res = 1.0
    for n in nums:
        res *= n
    return res


agent = FunctionAgent(
    tools=[multiply],
    llm=llm,
    system_prompt="You are a helpful assistant that can multiply any number of numbers.",
)

async def main():
    result = await agent.run("计算 10 * 20 * 20 * 20 * 20")
    print(result)

asyncio.run(main())

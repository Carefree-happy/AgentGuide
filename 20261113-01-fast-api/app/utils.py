import time
import random

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def invoke_model_with_tools(
    model,
    messages,
    tools,
    max_tool_rounds=10,
    max_attempts=5,
):
    """
    执行模型调用。
    如果模型请求工具，则执行工具并继续调用模型。
    直到模型返回普通回答。
    """

    tools_by_name = {tool.name: tool for tool in tools}

    for tool_round in range(max_tool_rounds):

        result = invoke_with_retry(
            model,
            messages,
            max_attempts=max_attempts,
        )

        # 保存 AIMessage，包括 tool_calls
        messages.append(result)

        # 没有工具调用，说明模型已经返回普通回答
        if not result.tool_calls:
            return result

        print(f"执行第 {tool_round + 1} 轮工具调用")

        # 执行工具并将结果转换为模型可继续处理的 ToolMessage
        tool_messages = []
        for tool_call in result.tool_calls:
            tool = tools_by_name.get(tool_call["name"])
            if tool is None:
                raise ValueError(
                    f"模型请求了未注册的工具：{tool_call['name']}"
                )
            tool_messages.append(tool.invoke(tool_call))

        # 将工具执行结果添加到上下文
        messages.extend(tool_messages)

    raise RuntimeError("超过最大工具调用轮数")

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


def invoke_with_retry(
    model,
    messages,
    max_attempts=5,
    base_delay=2,
    max_delay=30,
):
    """
    模型请求容错：
    429、超时、网络异常、服务器错误自动重试。
    """

    for attempt in range(1, max_attempts + 1):
        try:
            result = model.invoke(messages)

            # 工具调用响应通常没有文本内容，但仍是有效的模型响应。
            if not result.content and not result.tool_calls:
                raise RuntimeError("模型返回了空内容")

            return result

        except Exception as e:

            status_code = getattr(e, "status_code", None)

            response = getattr(e, "response", None)
            if status_code is None and response is not None:
                status_code = getattr(response, "status_code", None)

            error_name = type(e).__name__.lower()

            retryable = (
                status_code in (408, 409, 425, 429)
                or (status_code is not None and 500 <= status_code < 600)
                or "timeout" in error_name
                or "connection" in error_name
                or "temporarily" in str(e).lower()
                or "空内容" in str(e)
            )

            if not retryable:
                print(f"不可重试错误：{type(e).__name__}: {e}")
                raise

            if attempt >= max_attempts:
                print(f"请求失败，已达到最大重试次数：{e}")
                raise RuntimeError(
                    f"模型请求失败，已重试 {max_attempts} 次"
                ) from e

            # 指数退避 + 随机抖动
            delay = min(
                base_delay * (2 ** (attempt - 1)),
                max_delay,
            )

            delay += random.uniform(0, 1)

            # 如果服务商返回 Retry-After，优先参考
            headers = getattr(response, "headers", {}) if response else {}
            retry_after = headers.get("Retry-After") if headers else None

            if retry_after:
                try:
                    delay = min(float(retry_after), max_delay)
                except (ValueError, TypeError):
                    pass

            print(
                f"请求失败：{type(e).__name__}，"
                f"第 {attempt} 次尝试，"
                f"{delay:.1f} 秒后重试"
            )

            time.sleep(delay)

    raise RuntimeError("模型请求失败，未获得响应")


def invoke_until_complete(
    model,
    prompt: str,
    max_rounds: int = 5,
    max_attempts: int = 5,
    tools=None,
    max_tool_rounds: int = 10,
):
    """
    自动检测回答完整性。
    请求失败自动重试，回答截断自动续写。
    """

    messages = [
        SystemMessage(
            content=(
                "请完整回答用户的问题。"
                "只有在整个回答完成后，"
                "才在最后单独输出 <END_OF_ANSWER>。"
            )
        ),
        HumanMessage(content=prompt),
    ]
    tool_enabled_model = model.bind_tools(tools) if tools else model

    full_content = ""
    last_metadata = {}
    completed = False

    for round_num in range(1, max_rounds + 1):

        print(f"\n========== 第 {round_num} 轮生成 ==========")

        if tools:
            result = invoke_model_with_tools(
                tool_enabled_model,
                messages,
                tools,
                max_tool_rounds=max_tool_rounds,
                max_attempts=max_attempts,
            )
        else:
            result = invoke_with_retry(
                tool_enabled_model,
                messages,
                max_attempts=max_attempts,
            )

        content = result.content
        last_metadata = result.response_metadata or {}

        finish_reason = last_metadata.get("finish_reason")

        print(f"结束原因：{finish_reason}")
        print(f"本轮输出长度：{len(content)}")

        full_content += content

        # 检查结束标记
        if "<END_OF_ANSWER>" in full_content:
            full_content = full_content.replace(
                "<END_OF_ANSWER>", ""
            ).rstrip()

            completed = True
            print("回答完整，任务结束！")
            break

        # 已经达到最大轮数
        if round_num == max_rounds:
            print("达到最大续写轮数。")
            break

        # invoke_model_with_tools 已保存模型最终回答。
        if not tools:
            messages.append(AIMessage(content=content))

        # 请求模型继续
        messages.append(
            HumanMessage(
                content=(
                    "请从上一轮回答结束的位置继续，"
                    "不要重复已有内容。"
                    "请完成剩余内容，"
                    "全部完成后输出 <END_OF_ANSWER>。"
                )
            )
        )

    return AIMessage(
        content=full_content,
        response_metadata={
            **last_metadata,
            "complete": completed,
        },
    )

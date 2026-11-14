import time
import random

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

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

            # 空内容视为本次请求未成功
            if not result.content:
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
                return None

            if attempt >= max_attempts:
                print(f"请求失败，已达到最大重试次数：{e}")
                return None

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

    return None


def invoke_until_complete(
    model,
    prompt: str,
    max_rounds: int = 5,
    max_attempts: int = 5,
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

    full_content = ""
    last_metadata = {}
    completed = False

    for round_num in range(1, max_rounds + 1):

        print(f"\n========== 第 {round_num} 轮生成 ==========")

        result = invoke_with_retry(
            model,
            messages,
            max_attempts=max_attempts,
        )

        # 多次重试仍然失败，不让程序直接崩溃
        if result is None:
            print("本轮请求最终失败，保留已有回答。")
            break

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

        # 保存本轮回答
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

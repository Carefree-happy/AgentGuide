import time
import random

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def check_config(items: list):
    """
    批量校验配置项
    items 格式：[(变量值, 环境变量名, 展示名称), ...]
    """
    for value, env_name, display_name in items:
        if not value:
            raise RuntimeError(f"{display_name} 未配置")
        else:
            print(f"✅ {display_name} 已配置")


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
    runner_callable,
    max_attempts=5,
    base_delay=2,
    max_delay=30,
):
    """
    ========== 【底层网络&异常重试层，只负责通信容错，不关心续写、不关心工具】 ==========
    职责：
      1. 捕获网络类异常：连接失败、超时、服务商限流429、5xx服务错误
      2. 指数退避 + jitter，优先遵从响应头 Retry-After
      3. 区分【可重试错误】和【不可重试错误】，不可重试直接向上抛
      4. 只返回 AIMessage，校验返回体合法性（不能完全空）
    适用对象：
      - lambda: model.invoke(messages)
      - lambda: agent.invoke({"messages": messages})
    ！！重要：工具逻辑完全不在这一层，Agent内部闭环
    """

    for attempt in range(1, max_attempts + 1):
        try:
            # 执行业务调用（model / agent）
            result = runner_callable()

            # 合法性校验：返回不能既无内容也无tool_calls
            # Agent场景下，中间tool轮次的AIMessage会带tool_calls、空content，是合法的
            has_content = bool(result.content)
            has_tool_calls = bool(getattr(result, "tool_calls", None))
            if not has_content and not has_tool_calls:
                raise RuntimeError("返回消息非法：无content，也无tool_calls")

            return result

        except Exception as e:
            # 提取状态码：优先从异常本身，其次从e.response
            status_code = getattr(e, "status_code", None)

            response = getattr(e, "response", None)
            if status_code is None and response is not None:
                status_code = getattr(response, "status_code", None)

            error_class_name = type(e).__name__.lower()
            err_msg = str(e).lower()

            # ====================== 可重试规则定义 ======================
            # 408 请求超时 / 429 限流 / 500~599 服务端错误 / 连接类异常 / timeout异常
            is_retryable = (
                status_code in (408, 425, 429)
                or (status_code is not None and 500 <= status_code < 600)
                or "timeout" in error_class_name
                or "connection" in error_class_name
                or "connect" in err_msg
                or "temporarily" in err_msg
            )

            if not is_retryable:
                print(f"[retry] 不可重试错误，直接抛出：{type(e).__name__}: {e}")
                raise

            if attempt >= max_attempts:
                print(f"[retry] 请求失败，已达到最大重试次数：{e}")
                raise RuntimeError(
                    f"模型请求失败，已重试 {max_attempts} 次"
                ) from e

            # 如果服务商返回 Retry-After 响应头，优先使用服务商指定等待时间
            headers = getattr(response, "headers", {}) if response else {}
            retry_after = headers.get("Retry-After") if headers else None
            delay = None

            if retry_after:
                try:
                    delay = min(float(retry_after), max_delay)
                except (ValueError, TypeError):
                    delay = None

            # 没有合法Retry-After，才走指数退避+抖动
            if delay is None:
                raw_delay = base_delay * (2 ** (attempt - 1))
                raw_delay = min(raw_delay, max_delay)
                # Full Jitter 推荐写法，替换原来固定+0~1
                delay = random.uniform(0, raw_delay)

            print(
                f"[retry] 第 {attempt}/{max_attempts} 次失败，"
                f"{delay:.1f}s 后重试 | 异常：{type(e).__name__}"
            )

            time.sleep(delay)

    # 理论不会走到这里，for循环内部attempt>=max_attempts已经raise
    raise RuntimeError("重试循环异常退出")


def invoke_until_complete(
    runner,
    prompt: str,
    max_rounds: int = 5,
    max_attempts_per_call: int = 5,
    agent_config = None,
):
    """
    ========== 【长文本续写层，只负责截断、<END_OF_ANSWER>标记，不处理网络重试细节、不碰工具】 ==========
    职责边界：
      1. 组装初始对话 messages
      2. 循环调用底层 invoke_with_retry，拿到一轮输出
      3. 检测：<END_OF_ANSWER> 标记完成，或者 finish_reason=length 截断
      4. 截断时自动追加续写提示，继续请求
      5. 上限：max_continue_rounds 轮续写，防止无限循环
    【Runner 两种形态】
      - 原生 ChatModel：拥有 bind_tools 方法，调用 runner.invoke(messages)
      - LangGraph Agent（create_agent返回）：调用 runner.invoke({"messages": messages})，内部自动跑工具闭环
    【重要约定】
      Agent内部全权处理工具调用、ToolMessage、多轮tool循环；
      本层看到的永远是Agent跑完工具链之后，产出的最终 AIMessage。
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

        print(f"\n========== 第 {round_num}/{max_rounds} 轮生成 ==========")

        # 构造无参回调，交给重试层执行
        def run_once() -> AIMessage:
            # 分支1：原生LLM model（ChatModel）
            if hasattr(runner, "bind_tools"):
                return runner.invoke(messages)
            # 分支2：LangGraph Agent（create_agent）
            else:
                invoke_payload = {"messages": messages}
                if agent_config is not None:
                    # 带 thread_id 等配置调用
                    agent_out = runner.invoke(invoke_payload, config=agent_config)
                else:
                    agent_out = runner.invoke(invoke_payload)
                # 从Agent返回的消息列表里，取最后一条 AIMessage
                for msg in reversed(agent_out["messages"]):
                    if isinstance(msg, AIMessage):
                        has_content = bool(msg.content)
                        has_tool_calls = bool(getattr(msg, "tool_calls", None))
                        if has_content or has_tool_calls:
                            return msg
                        else:
                            # 是AIMessage，但它是空消息，跳过并打日志
                            print("[debug] skip empty AIMessage")
                    else:
                        # 非AI消息，仅打印调试，继续循环
                        print(f"[debug] skip non-AIMessage: {type(msg).__name__}")
                raise RuntimeError("Agent返回结果中没有找到有效的 AIMessage（全部是空消息）")

        # 调用【重试层】，自动处理429、超时、连接异常
        result = invoke_with_retry(
            runner_callable=run_once,
            max_attempts=max_attempts_per_call,
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

        # 没有结束，准备下一轮续写：
        # 1. 把本轮模型输出（AIMessage）加入上下文
        # 2. 追加续写 HumanMessage 提示，让模型接着写
        messages.append(result)
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
            "max_rounds": max_rounds,
        },
    )

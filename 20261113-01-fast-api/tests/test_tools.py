from langchain_core.messages import AIMessage

from app.tools import add
from app.utils import invoke_model_with_tools, invoke_until_complete, invoke_with_retry


def test_add_tool_sums_two_integers():
    assert add.invoke({"a": 123, "b": 456}) == 579


def test_model_runner_executes_tool_and_returns_final_answer():
    class FakeModel:
        def __init__(self):
            self.calls = 0

        def bind_tools(self, tools):
            assert tools == [add]
            return self

        def invoke(self, messages):
            self.calls += 1
            if self.calls == 1:
                return AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "add",
                            "args": {"a": 123, "b": 456},
                            "id": "add-123-456",
                            "type": "tool_call",
                        }
                    ],
                )

            assert messages[-1].content == "579"
            return AIMessage(content="123 + 456 = 579 <END_OF_ANSWER>")

    response = invoke_until_complete(
        FakeModel(),
        "请使用 add 工具计算 123 + 456。",
        tools=[add],
    )

    assert response.content == "123 + 456 = 579"
    assert response.response_metadata["complete"] is True


def test_retry_handles_rate_limit_and_empty_tool_call_response(monkeypatch):
    class RateLimitError(Exception):
        status_code = 429

    class FakeModel:
        def __init__(self):
            self.calls = 0

        def invoke(self, messages):
            self.calls += 1
            if self.calls == 1:
                raise RateLimitError("Too many requests")
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "add",
                        "args": {"a": 123, "b": 456},
                        "id": "add-123-456",
                        "type": "tool_call",
                    }
                ],
            )

    monkeypatch.setattr("app.utils.time.sleep", lambda _: None)
    model = FakeModel()

    response = invoke_with_retry(
        model,
        [],
        max_attempts=2,
        base_delay=0,
    )

    assert model.calls == 2
    assert response.tool_calls[0]["name"] == "add"


import os
from utils import timed_call, invoke_until_complete
from config import model


def test_model_connection():
    return invoke_until_complete(
            model,
            "我的妈妈已经卵巢癌晚期了，请详细介绍 卵巢癌晚期的症状、诊断方法和治疗方案，并且给我提供护理病人的注意事项。"
        )


if __name__ == "__main__":
    result = timed_call(
        "模型连接测试",
        test_model_connection
    )

    print(result.content)

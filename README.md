# 项目简介

学习AgentGuide

# 项目脚手架
project
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── conftest.py        ← 共享 fixture（TestClient）
│   └── test_main.py       ← 示例测试
├── pyproject.toml         ← 新增 dev 依赖组 + pytest 配置
└── .gitignore

第一版

`uv sync` 默认会安装 dev 组；上线时可用 `uv sync --no-dev` 去掉测试依赖

`uv run uvicorn app.main:app --reload               # 跑主程序`
`uv run pytest                                      # 跑全部`
`uv run pytest tests/test_main.py::test_read_root   # 只跑一个`
`uv run pytest --cov=app --cov-report=term-missing  # 带覆盖率`

第二版

`uv run fastapi dev`

# 项目简介

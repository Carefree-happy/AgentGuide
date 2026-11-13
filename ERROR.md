
# 2026-11-13 14:48:27 Using `httpx` with `starlette.testclient` is deprecated
.venv/lib/python3.11/site-packages/fastapi/testclient.py:1
/Users/blackode/workspace/learning/AgentGuide/20261113-01-fast-api/.venv/lib/python3.11/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
from starlette.testclient import TestClient as TestClient  # noqa

脚手架中直接修改
- dev = ["pytest>=8", "httpx>=0.27", "pytest-cov>=5"]
+ dev = ["pytest>=8", "httpx2", "pytest-cov>=5"]
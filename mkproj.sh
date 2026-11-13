#!/usr/bin/env bash
set -euo pipefail

slug="${1:?用法: ./mkproj.sh <项目简称，如 fast-api>}"
today="$(date +%Y%m%d)"
n="$(find . -maxdepth 1 -mindepth 1 -type d -name "${today}-[0-9][0-9]-*" | wc -l | tr -d ' ')"
dir="$(printf '%s-%02d-%s' "$today" "$((n + 1))" "$slug")"

mkdir -p "$dir/app" "$dir/tests"
: > "$dir/app/__init__.py"

cat > "$dir/pyproject.toml" <<EOF
[project]
name = "${slug}-${today}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["fastapi", "uvicorn[standard]"]

[dependency-groups]
dev = ["pytest>=8", "httpx2", "pytest-cov>=5"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "-q"
EOF

cat > "$dir/app/main.py" <<'EOF'
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"hello": "world"}
EOF

cat > "$dir/tests/conftest.py" <<'EOF'
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
EOF

cat > "$dir/tests/test_main.py" <<'EOF'
def test_read_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"hello": "world"}


def test_openapi_available(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "/" in resp.json()["paths"]
EOF

# printf '.venv/\n__pycache__/\n*.pyc\n.pytest_cache/\n.coverage\nhtmlcov/\n' > "$dir/.gitignore"

echo "已创建 $dir"
echo "运行: cd $dir && uv sync && uv run uvicorn app.main:app --reload"
echo "测试: cd $dir && uv sync && uv run pytest"

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

[agent-demo 项目地址](https://agent-demo.fastapicloud.dev/)

单独运行 python 程序

`uv run python app/main.py`

# 项目简介

## LangChain 当前 API 中跑通模型/消息调用与 create_agent，理解工具、状态和 middleware

[免费的LLM API](https://openapi.felo.ai/zh-CN/free-llm-api)
[free-llm-api-resources 指南](https://my.oschina.net/u/9487999/blog/19721096)


[LangChain Quickstart](https://docs.langchain.com/oss/python/langchain/quickstart)
[Google AI Studio example](https://aistudio.google.com/docs/get-started)
[Google AI Studio api keys](https://aistudio.google.com/api-keys)

[七牛云](https://portal.qiniu.com/)

# 问题一：返回的信息会出现卡断

# 问题二：指数退避，随机抖动
- 指数退避让请求间隔越来越长
- 随机抖动可以避免大量客户端在同一时间发生错误后，又在同一时间重新请求服务器，造成第二次流量拥堵。
- 指数退避解决的是请求频率问题，随机抖动解决的是请求同步问题

agent 如何解决 fetch 尝试因 SSL 证书验证失败而未能获取文本
- `https://www.gutenberg.org/files/64317/64317-0.txt`：老路径，经常 SSL EOF、断连
- `https://www.gutenberg.org/cache/epub/64317/pg64317.txt`：缓存镜像，稳定性强很多

===== GATSBY TEXT STATS (正文，剔除Gutenberg版权头尾) =====
1:33 总行数： 6408
1:34 总字符(含换行空格)： 270822
1:35 总字符(不含空白)： 220109
1:36 单词总数： 49979
1:37 Gatsby 出现次数： 264
1:38 Daisy 出现次数： 186
1:39 第一行包含 Daisy： Buchanans. Daisy was my second cousin once removed, and I’d known Tom

## 生成目录树

`chmod +x tree.sh && ./tree.sh`
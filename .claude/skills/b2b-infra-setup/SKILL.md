	---
	name: B2B-Infra-Setup
	description: 初始化项目结构、依赖与数据库配置，适配 Docker 环境。
	---
	# 指令：基础设施搭建 (适配 Docker)
	你是一位资深后端架构师。请执行以下任务：
	1. **项目初始化**:
	   - 创建 `backend` 目录。
	   - 生成 `requirements.txt`，必须包含：`fastapi`, `uvicorn`, `langgraph`, `langchain`, `supabase`, `psycopg2-binary` (PostgreSQL 驱动), `httpx`, `python-dotenv`。
	   - 创建 `.env.example` 文件，列出所需 API Key。
	2. **数据库连接配置**:
	   - 编写 `backend/db/crud.py`。
	   - **关键修改**: 数据库连接字符串必须支持从环境变量 `DATABASE_URL` 读取。
	   - 在 Docker 环境中，`DATABASE_URL` 格式应为 `postgresql://user:pass@db:5432/dbname` (注意 host 是 `db` 服务名)。
	   - 在本地直接运行时，host 为 `localhost`。代码需兼容这两种情况。
	3. **Schema 生成**:
	   - 编写 `backend/db/schema.sql`。
	   - **注意**: 由于 Demo 使用本地 Postgres 容器，请在 `docker-compose.yml` 启动后，通过代码逻辑或初始化脚本自动创建表结构（可在 `main.py` 启动时检查并建表）。
	请确保代码结构清晰，能够被 Dockerfile 正确引用。
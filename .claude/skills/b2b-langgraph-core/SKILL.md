	---
	name: B2B-LangGraph-Core
	description: 使用 LangGraph 编排工作流并暴露 API 接口，适配容器化运行。
	---
	# 指令：构建 LangGraph 工作流与 API
	请在 `backend/workflows/main_graph.py` 和 `backend/main.py` 中实现：
	1. **工作流编排**:
	   - 定义 LangGraph 状态机，节点包括：`Scout` -> `Miner` -> `Writer` -> `HumanReview` -> `Outreach` -> `SDR`。
	   - 在 `HumanReview` 节点实现阻塞逻辑，等待前端回调或人工确认。
	2. **API 服务封装** (`backend/main.py`):
	   - 使用 FastAPI 创建应用实例。
	   - 暴露接口 `POST /run_workflow`，接收 `product_keyword` 触发流程。
	   - 暴露接口 `POST /approve_draft`，用于人工审核通过文案。
	   - **关键修改**: 启动命令必须绑定 `0.0.0.0`，不能绑定 `127.0.0.1`，否则 Docker 容器外部无法访问服务。
	   - 示例启动代码:
	     ```python
	     if __name__ == "__main__":
	         import uvicorn
	         # host="0.0.0.0" 是 Docker 部署的关键
	         uvicorn.run(app, host="0.0.0.0", port=8000)
	     ```
	3. **异步处理**:
	   - 考虑到 Agent 执行时间较长，建议使用 `BackgroundTasks` 或 `AsyncIOScheduler` 处理请求，避免 HTTP 请求超时。
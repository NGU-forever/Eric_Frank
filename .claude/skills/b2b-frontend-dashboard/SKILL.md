	---
	name: B2B-Frontend-Dashboard
	description: 构建 React (Vite) 前端项目，用于输入关键词、查看线索列表及人工审核批准。
	---
	# 指令：构建前端控制面板
	请在项目根目录创建 `frontend` 文件夹，并实现以下功能：
	1.  **技术栈初始化**:
	    - 使用 `npm create vite@latest frontend -- --template react` 初始化项目。
	    - 安装依赖: `axios` (API 调用), `tailwindcss` (样式), `lucide-react` (图标)。
	2.  **核心页面与组件**:
	    - **CampaignPage (首页)**:
	        - 输入框: 接收 `Product Keyword` (如 "LED Lights")。
	        - 按钮: "Start AI Prospecting"，点击后调用后端 `/run_workflow` 接口。
	        - 展示当前运行状态。
	    - **LeadsTable (线索列表)**:
	        - 表格展示字段: Company Name, Website, Decision Maker, Status, Actions。
	        - 状态徽章: 不同颜色区分。
	    - **ApprovalModal (人工审核弹窗)**:
	        - 触发条件: 当线索状态为 `Drafted` 时，Actions 列显示 "Review" 按钮。
	        - 弹窗内容: 显示 AI 生成的 `icebreaker_text` (邮件内容)。
	        - 操作按钮: "Approve & Send" (调用 `/approve_draft`) 和 "Reject"。
	3.  **API 集成**:
	    - 创建 `src/api.js`，配置 Axios BaseURL。
	    - **关键配置**: 在 Vite 中使用环境变量 `VITE_API_URL` 指向后端地址。
	    - 开发环境代理配置 (`vite.config.js`): 代理 `/api` 到 `http://localhost:8000`。
	4.  **代码规范**:
	    - 使用函数组件与 Hooks (useState, useEffect)。
	    - 样式使用 Tailwind CSS 实现响应式布局。
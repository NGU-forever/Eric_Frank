	---
	name: B2B-Miner-Agent
	description: 实现 Agent 2 深度挖掘员，负责官网解析与决策人查找。
	---
	# 指令：开发深度挖掘员 Agent
	请参考 PRD 中的 Agent 2 定义，在 `backend/agents/miner.py` 中实现：
	1. **输入**: `website_url` (目标官网)。
	2. **工具集成**:
	   - 实现 `Firecrawl` 或 `ScrapeGraphAI` 的调用封装（模拟或实际调用 API），抓取首页和 About Us 页面内容。
	   - 实现 `Apollo/Proxycurl` API 调用封装，根据域名查询决策人。
	   - 实现 `NeverBounce` API 调用封装，验证邮箱有效性。
	3. **处理流程**:
	   - 解析官网文本，生成 `company_context` (业务简介摘要)。
	   - 查询 Apollo API 获取 CEO/Procurement Director 的姓名和邮箱。
	   - 验证邮箱格式与有效性。
	4. **数据库更新**:
	   - 更新 `b2b_leads` 表中的 `decision_maker_name`, `verified_email`, `company_context`。
	   - 状态流转为 `Mined`。
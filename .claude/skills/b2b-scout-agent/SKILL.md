	---
	name: B2B-Scout-Agent
	description: 实现 Agent 1 市场侦察员逻辑，负责从 Google 搜索并清洗线索。
	---
	# 指令：开发市场侦察员 Agent
	请参考 PRD 中的 Agent 1 定义，在 `backend/agents/scout.py` 中实现该模块：
	1. **输入**: `product_keyword` (产品词), `competitor_domain` (可选竞对域名)。
	2. **核心逻辑**:
	   - 使用 `httpx` 调用 Serper API 进行 Google 搜索。
	   - 构建 Prompt: "Find B2B distributors for {keyword}, exclude Alibaba, Made-in-China platforms."
	   - 对返回的搜索结果进行清洗：
	     - 过滤掉包含 `alibaba.com`, `made-in-china.com`, `yellowpages.com` 的域名。
	     - 提取清洗后的公司名和官网链接。
	3. **输出**:
	   - 返回一个字典列表: `[{'company_name': x, 'website_url': y}]`。
	   - 将结果通过 `crud.py` 写入数据库，状态标记为 `Scouted`。
	**代码规范**: 使用 `Pydantic` 定义输入输出模型，确保类型安全。
	---
	name: B2B-SDR-Agent
	description: 实现 Agent 5 SDR 客服，负责意向分类与自动约访。
	---
	# 指令：开发 SDR 客服 Agent
	请参考 PRD Agent 5，在 `backend/agents/sdr.py` 中实现：
	1. **输入**: `incoming_message` (客户回复内容)。
	2. **NLP 分类**:
	   - 使用 LLM 对回复进行意图识别。
	   - 分类逻辑:
	     - A类 (积极问询): 关键词 "quote", "price", "meeting"。
	     - B类 (稍后联系): 关键词 "later", "expensive", "not now"。
	     - C类 (拒绝): 关键词 "unsubscribe", "not interested"。
	3. **自动动作**:
	   - A类: 调用 Calendly API 生成链接并回复，更新状态为 `Meeting_Booked`，触发飞书/钉钉 Webhook 通知。
	   - B类: 打标签 `Nurture`。
	   - C类: 加入黑名单。
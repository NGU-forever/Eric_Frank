	---
	name: B2B-Outreach-Agent
	description: 实现 Agent 4 触达引擎，包含人工审核阻断与自动化发送逻辑。
	---
	# 指令：开发触达引擎 Agent
	请参考 PRD Agent 4，在 `backend/agents/outreach.py` 中实现：
	1. **人工干预检查**:
	   - 函数入口首先检查数据库中 `is_approved` 是否为 `True`。
	   - 若为 `False`，抛出异常或返回 "Pending Approval"。
	2. **发送逻辑**:
	   - 封装 `Instantly` API 发送邮件。
	   - 封装 `Wati` API 发送 WhatsApp 消息。
	   - 支持从数据库读取 `icebreaker_text` 作为内容。
	3. **防封号逻辑**:
	   - 在发送函数中加入 `time.sleep(random.randint(45, 120))` 实现随机延迟。
	   - 记录发送日志，每日发送计数器（防止单账号超 50 封）。
	4. **状态更新**:
	   - 发送成功后更新状态为 `Emailed` 或 `WhatsApped`，记录 `last_contact_date`。
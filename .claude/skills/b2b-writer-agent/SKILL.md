	---
	name: B2B-Writer-Agent
	description: 实现 Agent 3 文案大师，生成个性化破冰邮件和 WhatsApp 文案。
	---
	# 指令：开发文案生成 Agent
	请参考 PRD Agent 3，在 `backend/agents/writer.py` 中实现：
	1. **输入**: 从数据库读取 `company_context`, `decision_maker_name`, `company_name`。
	2. **LLM 调用**:
	   - 使用 LangChain 或原生 SDK 调用 Claude 3.5 Sonnet。
	   - Prompt 模板要求:
	     - 结合 `company_context` (如最近的新闻、痛点)。
	     - 结合我方产品优势。
	     - 生成 1:1 定制的破冰邮件 (Subject + Body) 和 WhatsApp 短信。
	3. **风控机制**:
	   - 生成内容后，将 `is_approved` 字段置为 `False`。
	   - 将生成的文案存入 `icebreaker_text` 字段。
	   - 状态流转为 `Drafted`。
	   - **注意**: 必须包含日志打印，提示“文案已生成，等待人工审核”。
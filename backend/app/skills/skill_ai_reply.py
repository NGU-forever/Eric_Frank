"""
Skill 6: AI智能询盘回复

功能：
- 自动识别客户意图
- 多轮对话
- 知识库检索
- 意向分级
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import json

from app.core.skill_base import BaseSkill, register_skill
from app.core.context import ExecutionContext, MessageContext
from app.config import settings


@register_skill
class AIReplySkill(BaseSkill):
    """
    AI回复Skill

    自动识别客户意图并生成智能回复
    """
    name = "ai_reply"
    display_name = "AI Reply"
    description = "自动识别客户意图并生成智能回复"
    category = "ai"
    version = "1.0.0"

    config_schema = {
        "type": "object",
        "properties": {
            "enable_intent_detection": {
                "type": "boolean",
                "default": True
            },
            "enable_kb_search": {
                "type": "boolean",
                "default": True
            },
            "max_context_messages": {
                "type": "integer",
                "default": 10
            },
            "confidence_threshold": {
                "type": "number",
                "default": 0.7
            }
        }
    }

    default_config = {
        "enable_intent_detection": True,
        "enable_kb_search": True,
        "max_context_messages": 10,
        "confidence_threshold": 0.7
    }

    input_schema = {
        "type": "object",
        "required": ["conversation_id", "message"],
        "properties": {
            "conversation_id": {
                "type": "string"
            },
            "customer_id": {
                "type": "integer"
            },
            "platform": {
                "type": "string",
                "enum": ["email", "whatsapp", "instagram_dm", "tiktok_dm"]
            },
            "message": {
                "type": "string",
                "description": "新收到的消息"
            },
            "history": {
                "type": "array",
                "items": {"type": "object"},
                "description": "对话历史"
            },
            "customer": {
                "type": "object",
                "description": "客户信息"
            },
            "product_info": {
                "type": "object",
                "description": "产品信息（上下文）"
            }
        }
    }

    output_schema = {
        "type": "object",
        "required": ["reply", "intent"],
        "properties": {
            "reply": {
                "type": "string",
                "description": "生成的回复"
            },
            "intent": {
                "type": "string",
                "description": "识别的意图"
            },
            "intent_level": {
                "type": "string",
                "enum": ["low", "medium", "high", "very_high"]
            },
            "intent_confidence": {
                "type": "number"
            },
            "suggested_actions": {
                "type": "array",
                "items": {"type": "string"}
            },
            "kb_sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "使用的知识库来源"
            },
            "should_takeover": {
                "type": "boolean",
                "description": "是否需要人工接管"
            },
            "takeover_reason": {
                "type": "string"
            }
        }
    }

    # 意图定义
    INTENTS = {
        "price_inquiry": {
            "keywords": ["price", "cost", "how much", "pricing", "rate", "quote", "费用", "价格", "多少钱", "报价"],
            "level": "medium",
            "actions": ["send_price_list", "offer_discount", "schedule_call"]
        },
        "product_inquiry": {
            "keywords": ["product", "item", "catalog", "brochure", "spec", "产品", "目录", "手册", "规格"],
            "level": "medium",
            "actions": ["send_catalog", "send_samples", "schedule_demo"]
        },
        "sample_request": {
            "keywords": ["sample", "try", "test", "demo", "样品", "试用", "测试"],
            "level": "high",
            "actions": ["request_shipping", "approve_sample", "send_sample_form"]
        },
        "moq_inquiry": {
            "keywords": ["moq", "minimum order", "minimum quantity", "起订量", "最小起订", "最低订购"],
            "level": "medium",
            "actions": ["explain_moq", "offer_flexibility", "discuss_options"]
        },
        "collaboration_inquiry": {
            "keywords": ["collaborate", "partner", "cooperation", "affiliate", "合作", "合伙", "联盟"],
            "level": "high",
            "actions": ["schedule_call", "send_partnership_info", "escalate_to_sales"]
        },
        "shipping_inquiry": {
            "keywords": ["shipping", "delivery", "logistics", "freight", "shipping cost", "发货", "运输", "物流", "运费"],
            "level": "low",
            "actions": ["provide_shipping_quote", "explain_shipping_options"]
        },
        "payment_inquiry": {
            "keywords": ["payment", "terms", "pay", "deposit", "method", "支付", "付款", "定金", "方式"],
            "level": "medium",
            "actions": ["explain_payment_terms", "send_invoice", "discuss_options"]
        },
        "lead_time_inquiry": {
            "keywords": ["lead time", "delivery time", "production time", "when ready", "交期", "生产周期", "什么时候好"],
            "level": "medium",
            "actions": ["provide_lead_time", "check_production_schedule"]
        },
        "complaint": {
            "keywords": ["problem", "issue", "wrong", "defect", "bad", "not work", "问题", "错误", "缺陷", "不好用"],
            "level": "high",
            "actions": ["escalate_to_support", "request_details", "apologize"]
        },
        "greeting": {
            "keywords": ["hello", "hi", "hey", "good morning", "good afternoon", "你好", "嗨", "早上好", "下午好"],
            "level": "low",
            "actions": ["greet_back", "ask_how_help"]
        },
        "goodbye": {
            "keywords": ["bye", "goodbye", "thank you", "thanks", "再见", "谢谢"],
            "level": "low",
            "actions": ["close_conversation", "follow_up_later"]
        },
        "urgent": {
            "keywords": ["urgent", "asap", "immediately", "emergency", "紧急", "马上", "立即", "急"],
            "level": "very_high",
            "actions": ["escalate_urgently", "takeover_required"]
        },
        "complex_negotiation": {
            "keywords": ["negotiate", "discount", "deal", "offer", "谈判", "折扣", "交易"],
            "level": "high",
            "actions": ["escalate_to_sales", "takeover_required"]
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute AI reply

        Args:
            context: Execution context

        Returns:
            Dict containing reply and intent analysis
        """
        input_data = context.input_data
        message = input_data.get("message", "")
        conversation_id = input_data.get("conversation_id", "")
        history = input_data.get("history", [])
        customer = input_data.get("customer", {})
        product_info = input_data.get("product_info", {})

        # Track metrics
        context.increment_metric("messages_processed")

        # Detect intent
        if self.config.get("enable_intent_detection", True):
            intent, confidence, level, actions = self._detect_intent(message, customer, history)
        else:
            intent = "general"
            confidence = 0.5
            level = "low"
            actions = []

        # Check if takeover is needed
        should_takeover, takeover_reason = self._check_takeover_needed(intent, confidence, level)

        # Search knowledge base if enabled
        kb_context = ""
        kb_sources = []
        if self.config.get("enable_kb_search", True) and not should_takeover:
            kb_context, kb_sources = await self._search_knowledge_base(message, intent, customer, product_info)

        # Generate reply
        if should_takeover:
            reply = self._generate_takeover_message(intent, customer)
        else:
            reply = await self._generate_reply(message, intent, level, kb_context, customer, history)

        # Update context
        context.set_state("detected_intent", intent)
        context.set_state("intent_level", level)
        context.set_state("confidence", confidence)

        return {
            "reply": reply,
            "intent": intent,
            "intent_level": level,
            "intent_confidence": confidence,
            "suggested_actions": actions,
            "kb_sources": kb_sources,
            "should_takeover": should_takeover,
            "takeover_reason": takeover_reason if should_takeover else None
        }

    def _detect_intent(
        self,
        message: str,
        customer: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> tuple[str, float, str, List[str]]:
        """
        Detect customer intent

        Returns:
            Tuple of (intent, confidence, level, actions)
        """
        message_lower = message.lower()

        # Score each intent
        scores = {}
        for intent_name, intent_data in self.INTENTS.items():
            score = 0
            for keyword in intent_data["keywords"]:
                if keyword.lower() in message_lower:
                    score += 1
            scores[intent_name] = score

        # Get best match
        if not scores or max(scores.values()) == 0:
            # No clear intent detected
            return "general", 0.3, "low", []

        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        # Calculate confidence
        confidence = min(best_score / 3, 1.0)  # Normalize

        # Get level and actions
        intent_data = self.INTENTS[best_intent]
        level = intent_data["level"]
        actions = intent_data["actions"].copy()

        # Adjust level based on customer data
        if customer.get("intent_level") == "very_high":
            level = "very_high"
        elif level == "low" and customer.get("follower_count", 0) > 100000:
            level = "medium"

        # Adjust based on conversation length
        if len(history) > 5:
            # Deeper conversation - increase intent level
            level_map = {"low": "medium", "medium": "high"}
            level = level_map.get(level, level)

        return best_intent, confidence, level, actions

    def _check_takeover_needed(
        self,
        intent: str,
        confidence: float,
        level: str,
    ) -> tuple[bool, str]:
        """
        Check if human takeover is needed

        Returns:
            Tuple of (should_takeover, reason)
        """
        threshold = self.config.get("confidence_threshold", 0.7)

        # Low confidence - need human
        if confidence < threshold:
            return True, "low_confidence"

        # Urgent or complex - need human
        if intent in ["urgent", "complaint", "complex_negotiation"]:
            return True, f"complex_intent_{intent}"

        # Very high intent but low confidence - escalate
        if level == "very_high" and confidence < 0.9:
            return True, "high_value_low_confidence"

        return False, ""

    async def _search_knowledge_base(
        self,
        query: str,
        intent: str,
        customer: Dict[str, Any],
        product_info: Dict[str, Any],
    ) -> tuple[str, List[str]]:
        """
        Search knowledge base for relevant information
        
        Returns:
            Tuple of (context_text, sources)
        """
        # Try RAG search first
        try:
            from app.skills.skill_rag import RagSkill
            rag_skill = RagSkill()
            
            # Use query (message) for search
            result = await rag_skill.execute(
                ExecutionContext(input_data={}), 
                action="query", 
                text=query, 
                top_k=3
            )
            
            if result.get("success") and result.get("documents"):
                documents = result["documents"]
                
                # Format context
                context_parts = []
                sources = []
                
                for i, doc in enumerate(documents):
                    content = doc.get("content", "")
                    metadata = doc.get("metadata", {})
                    source = metadata.get("source", f"doc_{i+1}")
                    
                    context_parts.append(f"Source: {source}\nContent: {content}")
                    if source not in sources:
                        sources.append(source)
                
                context_text = "\n\n".join(context_parts)
                return context_text, sources
                
        except Exception as e:
            # Log error but continue to fallback
            print(f"RAG search failed: {e}")
        
        # Fallback to mock data based on intent
        kb_entries = {
            "price_inquiry": {
                "context": "Our standard pricing starts at $X for small quantities, with volume discounts available for orders over 100 units.",
                "sources": ["pricing_policy_v1", "price_list_2024"]
            },
            "product_inquiry": {
                "context": "We offer a wide range of products including standard catalog items and custom solutions.",
                "sources": ["product_catalog_2024", "custom_solutions_guide"]
            },
            "sample_request": {
                "context": "Samples are available for qualified customers. Standard processing time is 3-5 business days.",
                "sources": ["sample_policy_v2"]
            },
            "moq_inquiry": {
                "context": "Our standard MOQ is 100 units for first orders, with flexibility for repeat customers.",
                "sources": ["moq_policy_v1"]
            },
            "collaboration_inquiry": {
                "context": "We offer various partnership models including dropshipping, wholesale, and affiliate programs.",
                "sources": ["partnership_guide_2024"]
            },
            "shipping_inquiry": {
                "context": "We ship worldwide via DHL, FedEx, and UPS. Shipping costs depend on destination and order size.",
                "sources": ["shipping_policy_v3"]
            },
            "payment_inquiry": {
                "context": "We accept wire transfer, PayPal, and credit card payments. Standard terms are 30% deposit, 70% before shipping.",
                "sources": ["payment_policy_v2"]
            },
            "lead_time_inquiry": {
                "context": "Standard lead time is 10-15 business days for stock items, 20-30 days for custom orders.",
                "sources": ["production_schedule_2024"]
            }
        }

        entry = kb_entries.get(intent)
        if entry:
            return entry["context"], entry["sources"]

        return "", []

    async def _generate_reply(
        self,
        message: str,
        intent: str,
        level: str,
        kb_context: str,
        customer: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> str:
        """Generate AI reply"""
        # Import AI provider
        from app.integrations.ai_provider import get_ai_provider

        ai_provider = get_ai_provider()

        # Build conversation history for context
        context_messages = []
        if history:
            # Take last N messages
            recent_history = history[-self.config.get("max_context_messages", 10):]
            for msg in recent_history:
                role = "user" if msg.get("role") == "user" else "assistant"
                context_messages.append({
                    "role": role,
                    "content": msg.get("content", "")
                })

        # Build system prompt
        system_prompt = f"""You are a helpful and professional customer service assistant for a trading/export company.

Your role:
- Respond to customer inquiries about products, pricing, and services
- Be friendly, professional, and concise
- Ask clarifying questions when needed
- Escalate to human agents for complex issues

Current customer intent: {intent}
Intent level: {level} (low=general inquiry, medium=showing interest, high=serious buyer, very_high=ready to purchase)

Relevant knowledge base information:
{kb_context if kb_context else "Use general knowledge for the company's products and services."}

Guidelines:
- For low intent: Be helpful but brief, don't over-promise
- For medium intent: Provide more details, encourage next steps
- For high intent: Be more detailed, push for action (call, meeting, sample)
- For very high intent: Be urgent, focus on closing or scheduling"""

        # Build user prompt
        user_prompt = f"""Customer message: {message}

Generate a helpful response."""

        # Add customer context if available
        if customer:
            user_prompt += f"\n\nCustomer info: {json.dumps(customer, ensure_ascii=False)}"

        # Build messages
        messages = [
            {"role": "system", "content": system_prompt},
            *context_messages,
            {"role": "user", "content": user_prompt}
        ]

        # Generate reply
        response = await ai_provider.chat_completion(messages)

        return response

    def _generate_takeover_message(self, intent: str, customer: Dict[str, Any]) -> str:
        """Generate message when human takeover is needed"""
        name = customer.get("name") or customer.get("username", "")

        if intent == "urgent":
            return f"Thank you for your message. I understand this is urgent. Let me connect you with our team right away."
        elif intent == "complaint":
            return f"I'm sorry to hear about this issue. I want to make sure we resolve this properly. Let me connect you with our customer service team."
        else:
            return f"Thank you for your interest. I'd like to have one of our specialists reach out to you to discuss your needs in detail. Is there a good time for a call?"


@register_skill
class IntentAnalysisSkill(BaseSkill):
    """
    意图分析Skill

    仅分析意图，不生成回复
    """
    name = "intent_analysis"
    display_name = "Intent Analysis"
    description = "分析客户消息意图"
    category = "ai"
    version = "1.0.0"

    input_schema = {
        "type": "object",
        "required": ["message"],
        "properties": {
            "message": {"type": "string"},
            "customer": {"type": "object"},
            "history": {"type": "array"}
        }
    }

    output_schema = {
        "type": "object",
        "required": ["intent", "confidence"],
        "properties": {
            "intent": {"type": "string"},
            "confidence": {"type": "number"},
            "intent_level": {"type": "string"},
            "all_scores": {"type": "object"}
        }
    }

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute intent analysis"""
        # Create AIReply skill to reuse intent detection
        ai_reply = AIReplySkill(self.config)

        input_data = context.input_data
        message = input_data.get("message", "")
        customer = input_data.get("customer", {})
        history = input_data.get("history", [])

        intent, confidence, level, _ = ai_reply._detect_intent(message, customer, history)

        # Get all scores for debugging
        message_lower = message.lower()
        all_scores = {}
        for intent_name, intent_data in AIReplySkill.INTENTS.items():
            score = 0
            for keyword in intent_data["keywords"]:
                if keyword.lower() in message_lower:
                    score += 1
            all_scores[intent_name] = score

        return {
            "intent": intent,
            "confidence": confidence,
            "intent_level": level,
            "all_scores": all_scores
        }

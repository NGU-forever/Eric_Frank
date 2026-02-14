"""
Skill 4: AI智能话术生成

功能：
- 根据客户信息生成个性化话术
- 支持邮件和WhatsApp两种格式
- 多语言支持
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.core.skill_base import BaseSkill, register_skill
from app.core.context import ExecutionContext
from app.config import settings


@register_skill
class MessageGeneratorSkill(BaseSkill):
    """
    AI话术生成Skill

    根据客户信息生成个性化话术
    """
    name = "message_generator"
    display_name = "Message Generator"
    description = "根据客户信息生成个性化话术，支持邮件和WhatsApp"
    category = "outreach"
    version = "1.0.0"

    config_schema = {
        "type": "object",
        "properties": {
            "default_language": {
                "type": "string",
                "default": "en"
            },
            "tone": {
                "type": "string",
                "enum": ["professional", "friendly", "casual", "formal"],
                "default": "professional"
            },
            "max_length": {
                "type": "integer",
                "default": 500
            },
            "use_templates": {
                "type": "boolean",
                "default": True
            }
        }
    }

    default_config = {
        "default_language": "en",
        "tone": "professional",
        "max_length": 500,
        "use_templates": True
    }

    input_schema = {
        "type": "object",
        "required": ["customer"],
        "properties": {
            "customer": {
                "type": "object",
                "description": "客户信息"
            },
            "channel": {
                "type": "string",
                "enum": ["email", "whatsapp"],
                "default": "email"
            },
            "language": {
                "type": "string",
                "default": "en"
            },
            "template_id": {
                "type": "string",
                "description": "使用指定模板"
            },
            "custom_prompt": {
                "type": "string",
                "description": "自定义Prompt"
            },
            "product_info": {
                "type": "object",
                "description": "产品信息"
            }
        }
    }

    output_schema = {
        "type": "object",
        "required": ["subject", "body"],
        "properties": {
            "subject": {
                "type": "string",
                "description": "邮件主题"
            },
            "body": {
                "type": "string",
                "description": "消息正文"
            },
            "whatsapp_message": {
                "type": "string",
                "description": "WhatsApp消息"
            },
            "variables_used": {
                "type": "array",
                "items": {"type": "string"},
                "description": "使用的变量"
            }
        }
    }

    # 话术模板库
    TEMPLATES = {
        "email": {
            "en": {
                "introduction": {
                    "subject": "Quick Question About {company_name}'s Social Media",
                    "body": """Hi {name},

I noticed {company_name} is doing great work on {platform} - especially your content about {category}!

I work with brands like yours to help scale their supplier partnerships and improve product sourcing.

Would you be open to a brief chat about how we might collaborate?

Best regards,
{sender_name}
{company}"""
                },
                "followup": {
                    "subject": "Following Up - Partnership Opportunity",
                    "body": """Hi {name},

I wanted to follow up on my previous message about potential collaboration.

I understand you're likely busy, but I think there could be real value in connecting.

Would 15 minutes this week work for a quick call?

Best,
{sender_name}"""
                },
                "collaboration": {
                    "subject": "Collaboration Opportunity with {company_name}",
                    "body": """Hi {name},

I've been following {company_name} on {platform} for a while and love your content around {category}.

We're a {your_business} specializing in high-quality {product_category}. I think our products could be a great fit for your audience.

Would you be interested in seeing our catalog?

Looking forward to hearing from you!

{sender_name}
{company}"""
                },
                "sample": {
                    "subject": "Free Sample Request - {product_name}",
                    "body": """Hi {name},

I'd love to send you some samples of our {product_name}.

We believe these could be perfect for your content, and we'd appreciate your feedback.

If you're interested, just let me know your shipping details and I'll get them sent out right away.

Best regards,
{sender_name}"""
                }
            },
            "zh": {
                "introduction": {
                    "subject": "关于{company_name}社媒合作的机会",
                    "body": """您好 {name}，

我关注了{company_name}在{platform}上的账号，特别喜欢您关于{category}的内容！

我们公司专注于为品牌提供优质的{product_category}产品，相信能为您的粉丝带来价值。

是否有时间聊聊合作的可能性？

祝好，
{sender_name}
{company}"""
                },
                "followup": {
                    "subject": "跟进：合作机会",
                    "body": """您好 {name}，

想跟进一下之前的合作建议。

我知道您很忙，但我认为我们的合作能带来双赢。

这周方便安排15分钟的通话吗？

祝好，
{sender_name}"""
                }
            }
        },
        "whatsapp": {
            "en": {
                "introduction": """Hi {name}! 👋

I've been following {company_name} on {platform} and love your content about {category}!

We're a {your_business} and I think we could collaborate. Would you be open to a quick chat?""",
                "followup": """Hi {name}! Just following up on my previous message about potential collaboration. Would 15 minutes this week work?""",
                "collaboration": """Hi {name}! Love your {platform} content! We're looking for partners in the {category} space. Would you be interested in seeing our catalog? 📦"""
            },
            "zh": {
                "introduction": """您好 {name}！👋

关注了您的{platform}账号，很喜欢您的{category}内容！

我们是做{product_category}的，有兴趣合作吗？""",
                "followup": """您好 {name}，想跟进一下之前的合作建议，这周方便聊15分钟吗？"""
            }
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute message generation

        Args:
            context: Execution context

        Returns:
            Dict containing generated message
        """
        input_data = context.input_data
        customer = input_data.get("customer", {})
        channel = input_data.get("channel", "email")
        language = input_data.get("language", self.config.get("default_language", "en"))
        template_id = input_data.get("template_id", "introduction")
        custom_prompt = input_data.get("custom_prompt")
        product_info = input_data.get("product_info", {})

        # Extract customer info
        customer_name = customer.get("name") or customer.get("username", "").lstrip("@")
        company_name = customer.get("company_name") or customer.get("company") or customer.get("username", "")
        platform = customer.get("platform", "social media")
        category = customer.get("category") or "your industry"

        # Generate variables
        variables = {
            "name": self._format_name(customer_name),
            "company_name": company_name,
            "platform": platform,
            "category": category,
            "product_category": product_info.get("category", "products"),
            "product_name": product_info.get("name", "our products"),
            "sender_name": settings.APP_NAME if not custom_prompt else "Your Name",
            "company": settings.APP_NAME,
            "your_business": product_info.get("business_type", "supplier business"),
        }

        # Generate message
        if custom_prompt:
            # Use custom prompt with AI
            message = await self._generate_with_ai(custom_prompt, variables, channel, language)
        else:
            # Use template
            message = self._generate_from_template(channel, language, template_id, variables)

        # Update context
        context.set_state("generated_variables", variables)
        context.increment_metric("messages_generated")

        return {
            **message,
            "variables_used": list(variables.keys())
        }

    def _generate_from_template(
        self,
        channel: str,
        language: str,
        template_id: str,
        variables: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate message from template"""
        try:
            templates = self.TEMPLATES.get(channel, {}).get(language, {})
            template = templates.get(template_id, templates.get("introduction", {}))

            # Handle both string templates (for WhatsApp) and dict templates (for email)
            if isinstance(template, str):
                # WhatsApp template
                message = self._replace_variables(template, variables)
                return {
                    "whatsapp_message": message,
                    "body": message
                }
            else:
                # Email template
                subject = template.get("subject", "Collaboration Opportunity")
                body = template.get("body", "")

                return {
                    "subject": self._replace_variables(subject, variables),
                    "body": self._replace_variables(body, variables)
                }

        except Exception:
            # Fallback to simple message
            return self._generate_fallback(variables)

    def _replace_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """Replace variables in template"""
        result = text
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))
        return result

    def _format_name(self, name: str) -> str:
        """Format customer name"""
        if not name:
            return "there"
        return name.strip().title()

    def _generate_fallback(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback message"""
        name = variables.get("name", "there")
        company = variables.get("company_name", "your company")

        return {
            "subject": f"Partnership Opportunity with {company}",
            "body": f"""Hi {name},

I hope this message finds you well. I'd like to discuss a potential partnership opportunity between our companies.

Would you be available for a brief call this week?

Best regards,
{variables.get('sender_name', 'Your Name')}""",
            "whatsapp_message": f"Hi {name}! Would you be interested in a quick chat about a potential collaboration?"
        }

    async def _generate_with_ai(
        self,
        prompt: str,
        variables: Dict[str, Any],
        channel: str,
        language: str,
    ) -> Dict[str, Any]:
        """Generate message using AI"""
        # Import AI provider
        from app.integrations.ai_provider import get_ai_provider

        ai_provider = get_ai_provider()

        # Build system prompt
        system_prompt = f"""You are a professional business development specialist. Your task is to write a {channel} message in {language}.

Requirements:
1. Keep it {self.config.get('tone', 'professional')} and engaging
2. Avoid sounding like spam or a generic template
3. Keep it concise (under {self.config.get('max_length', 500)} words)
4. End with a clear call to action
5. Be respectful of the recipient's time

Use the following variables to personalize the message:
{', '.join([f'{k}={v}' for k, v in variables.items()])}"""

        # Build user prompt
        user_prompt = f"{prompt}\n\nGenerate a {channel} message."

        # Call AI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        response = await ai_provider.chat_completion(messages)

        # Parse response
        if channel == "email":
            # Try to extract subject and body
            lines = response.split("\n")
            subject = None
            body_lines = []

            for line in lines:
                if line.lower().startswith("subject:"):
                    subject = line.split(":", 1)[1].strip()
                elif line.lower().startswith("body:"):
                    continue
                else:
                    body_lines.append(line)

            body = "\n".join(body_lines).strip()

            return {
                "subject": subject or "Partnership Opportunity",
                "body": body
            }
        else:
            return {
                "whatsapp_message": response,
                "body": response
            }


@register_skill
class BulkMessageGeneratorSkill(BaseSkill):
    """
    批量话术生成Skill

    为多个客户生成话术
    """
    name = "bulk_message_generator"
    display_name = "Bulk Message Generator"
    description = "批量生成个性化话术"
    category = "outreach"
    version = "1.0.0"

    input_schema = {
        "type": "object",
        "required": ["customers"],
        "properties": {
            "customers": {
                "type": "array",
                "items": {"type": "object"},
                "description": "客户列表"
            },
            "channel": {
                "type": "string",
                "enum": ["email", "whatsapp"],
                "default": "email"
            },
            "language": {
                "type": "string",
                "default": "en"
            },
            "template_id": {
                "type": "string",
                "default": "introduction"
            },
            "product_info": {
                "type": "object"
            }
        }
    }

    output_schema = {
        "type": "object",
        "required": ["messages"],
        "properties": {
            "messages": {
                "type": "array",
                "description": "生成的消息列表"
            },
            "total": {
                "type": "integer"
            }
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute bulk message generation"""
        input_data = context.input_data
        customers = input_data.get("customers", [])
        channel = input_data.get("channel", "email")
        language = input_data.get("language", "en")
        template_id = input_data.get("template_id", "introduction")
        product_info = input_data.get("product_info", {})

        # Create generator skill
        generator = MessageGeneratorSkill(self.config)

        messages = []
        for customer in customers:
            try:
                # Create input for single generation
                gen_input = {
                    "customer": customer,
                    "channel": channel,
                    "language": language,
                    "template_id": template_id,
                    "product_info": product_info
                }

                # Create execution context
                gen_context = ExecutionContext(
                    workflow_id=context.workflow_id,
                    execution_id=context.execution_id,
                )
                gen_context.input_data = gen_input

                # Generate message
                result = await generator.run(gen_context)
                result["customer_id"] = customer.get("id")
                result["customer_username"] = customer.get("username")
                messages.append(result)

            except Exception:
                context.increment_metric("errors")
                continue

        return {
            "messages": messages,
            "total": len(messages)
        }

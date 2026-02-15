"""
Skill 5: 自动化触达发送

功能：
- 按时区定时发送
- 随机间隔防封
- 多账号轮换
- 状态回传
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import smtplib
from email.message import EmailMessage
import httpx

from app.core.skill_base import BaseSkill, register_skill
from app.core.context import ExecutionContext
from app.config import settings


@register_skill
class AutoSenderSkill(BaseSkill):
    """
    自动发送Skill

    自动发送邮件或WhatsApp消息
    """
    name = "auto_sender"
    display_name = "Auto Sender"
    description = "自动化触达发送，支持邮件和WhatsApp"
    category = "outreach"
    version = "1.0.0"

    config_schema = {
        "type": "object",
        "properties": {
            "dry_run": {
                "type": "boolean",
                "default": False,
                "description": "是否只模拟发送，不实际发送"
            },
            "batch_size": {
                "type": "integer",
                "default": 50,
                "description": "每批发送数量"
            },
            "default_timezone": {
                "type": "string",
                "default": "UTC"
            },
            "enable_account_rotation": {
                "type": "boolean",
                "default": True,
                "description": "是否启用账号轮换"
            }
        }
    }

    default_config = {
        "dry_run": False,
        "batch_size": 50,
        "default_timezone": "UTC",
        "enable_account_rotation": True
    }

    input_schema = {
        "type": "object",
        "required": ["customers", "messages"],
        "properties": {
            "customers": {
                "type": "array",
                "items": {"type": "object"},
                "description": "客户列表"
            },
            "messages": {
                "type": "object",
                "description": "消息内容（可以是单个消息或批量消息）"
            },
            "channel": {
                "type": "string",
                "enum": ["email", "whatsapp"],
                "default": "email"
            },
            "schedule": {
                "type": "object",
                "description": "发送计划"
            },
            "accounts": {
                "type": "array",
                "items": {"type": "object"},
                "description": "可用的账号列表"
            },
            "send_immediately": {
                "type": "boolean",
                "default": False
            }
        }
    }

    output_schema = {
        "type": "object",
        "required": ["results", "success_count", "failed_count"],
        "properties": {
            "results": {
                "type": "array",
                "description": "发送结果列表"
            },
            "success_count": {
                "type": "integer"
            },
            "failed_count": {
                "type": "integer"
            },
            "scheduled_count": {
                "type": "integer"
            }
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._account_pool: List[Dict[str, Any]] = []
        self._current_account_index = 0

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute auto sending

        Args:
            context: Execution context

        Returns:
            Dict containing send results
        """
        input_data = context.input_data
        customers = input_data.get("customers", [])
        messages = input_data.get("messages", {})
        channel = input_data.get("channel", "email")
        schedule = input_data.get("schedule", {})
        accounts = input_data.get("accounts", [])
        send_immediately = input_data.get("send_immediately", False)

        dry_run = self.config.get("dry_run", False)
        enable_rotation = self.config.get("enable_account_rotation", True)

        # Initialize account pool
        if enable_rotation and accounts:
            self._account_pool = accounts.copy()
            random.shuffle(self._account_pool)

        results = []
        success_count = 0
        failed_count = 0
        scheduled_count = 0

        # Process messages
        if isinstance(messages, list) and len(messages) == len(customers):
            # Bulk messages - one per customer
            for i, (customer, message) in enumerate(zip(customers, messages)):
                result = await self._send_single(
                    customer,
                    message,
                    channel,
                    schedule,
                    send_immediately,
                    dry_run,
                )
                results.append(result)

                if result["status"] == "sent":
                    success_count += 1
                elif result["status"] == "scheduled":
                    scheduled_count += 1
                else:
                    failed_count += 1

                # Random delay between sends
                if not dry_run and i < len(customers) - 1:
                    await self._random_delay(schedule)

        else:
            # Single message for all customers
            for i, customer in enumerate(customers):
                result = await self._send_single(
                    customer,
                    messages,
                    channel,
                    schedule,
                    send_immediately,
                    dry_run,
                )
                results.append(result)

                if result["status"] == "sent":
                    success_count += 1
                elif result["status"] == "scheduled":
                    scheduled_count += 1
                else:
                    failed_count += 1

                # Random delay between sends
                if not dry_run and i < len(customers) - 1:
                    await self._random_delay(schedule)

        # Update metrics
        context.set_state("send_stats", {
            "success": success_count,
            "failed": failed_count,
            "scheduled": scheduled_count
        })
        context.increment_metric("messages_sent", success_count)
        context.increment_metric("messages_failed", failed_count)

        return {
            "results": results,
            "success_count": success_count,
            "failed_count": failed_count,
            "scheduled_count": scheduled_count
        }

    async def _send_single(
        self,
        customer: Dict[str, Any],
        message: Dict[str, Any],
        channel: str,
        schedule: Optional[Dict[str, Any]],
        send_immediately: bool,
        dry_run: bool,
    ) -> Dict[str, Any]:
        """Send a single message"""
        result = {
            "customer_id": customer.get("id"),
            "customer_username": customer.get("username"),
            "status": "pending",
            "message_id": None,
            "sent_at": None,
            "error": None
        }

        try:
            # Check if should schedule instead of immediate send
            if not send_immediately and schedule:
                send_time = self._calculate_send_time(customer, schedule)
                if send_time > datetime.utcnow():
                    result["status"] = "scheduled"
                    result["scheduled_at"] = send_time.isoformat()
                    return result

            # Get account
            account = self._get_next_account(channel, customer)

            # Send based on channel
            if channel == "email":
                await self._send_email(customer, message, account, dry_run)
            elif channel == "whatsapp":
                await self._send_whatsapp(customer, message, account, dry_run)
            else:
                raise ValueError(f"Unsupported channel: {channel}")

            result["status"] = "sent"
            result["sent_at"] = datetime.utcnow().isoformat()
            result["account_id"] = account.get("id") if account else None

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)

        return result

    async def _send_email(
        self,
        customer: Dict[str, Any],
        message: Dict[str, Any],
        account: Optional[Dict[str, Any]],
        dry_run: bool,
    ):
        """Send email"""
        email = customer.get("email")
        if not email:
            raise ValueError("Customer has no email")

        if dry_run:
            # Simulate sending
            await asyncio.sleep(0.1)
            return

        # Get SMTP settings from account or config
        smtp_host = account.get("smtp_host") if account else settings.SMTP_HOST
        smtp_port = account.get("smtp_port", settings.SMTP_PORT) if account else settings.SMTP_PORT
        smtp_user = account.get("smtp_user") if account else settings.SMTP_USER
        smtp_password = account.get("smtp_password") if account else settings.SMTP_PASSWORD

        # Create message
        msg = EmailMessage()
        msg["From"] = smtp_user
        msg["To"] = email
        msg["Subject"] = message.get("subject", "")
        msg.set_content(message.get("body", ""))

        # Send
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

    async def _send_whatsapp(
        self,
        customer: Dict[str, Any],
        message: Dict[str, Any],
        account: Optional[Dict[str, Any]],
        dry_run: bool,
    ):
        """Send WhatsApp message"""
        phone = customer.get("whatsapp")
        if not phone:
            raise ValueError("Customer has no WhatsApp number")

        if dry_run:
            # Simulate sending
            await asyncio.sleep(0.1)
            return

        # Get WhatsApp API settings
        phone_number_id = account.get("phone_number_id") if account else settings.WHATSAPP_PHONE_NUMBER_ID
        access_token = account.get("access_token") if account else settings.WHATSAPP_ACCESS_TOKEN

        # WhatsApp Business API
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {
                "body": message.get("whatsapp_message") or message.get("body", "")
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

    def _get_next_account(self, channel: str, customer: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get next account from rotation pool"""
        if not self._account_pool:
            return None

        # Filter accounts by channel
        channel_accounts = [
            acc for acc in self._account_pool
            if acc.get("account_type") == channel or acc.get("type") == channel
        ]

        if not channel_accounts:
            return self._account_pool[0]

        # Get next account
        account = channel_accounts[self._current_account_index % len(channel_accounts)]
        self._current_account_index += 1

        return account

    def _calculate_send_time(
        self,
        customer: Dict[str, Any],
        schedule: Dict[str, Any],
    ) -> datetime:
        """Calculate optimal send time based on schedule"""
        # Get timezone (default to UTC)
        timezone = schedule.get("timezone", "UTC")
        country = customer.get("country", "US")

        # Map country to timezone (simplified)
        tz_map = {
            "US": "America/New_York",
            "UK": "Europe/London",
            "DE": "Europe/Berlin",
            "FR": "Europe/Paris",
            "IT": "Europe/Rome",
            "ES": "Europe/Madrid",
            "JP": "Asia/Tokyo",
            "KR": "Asia/Seoul",
            "CN": "Asia/Shanghai",
            "SG": "Asia/Singapore",
            "AU": "Australia/Sydney",
            "BR": "America/Sao_Paulo",
            "IN": "Asia/Kolkata",
        }

        target_tz = tz_map.get(country, timezone)

        # Get allowed hours
        send_hours = schedule.get("send_hours", [9, 10, 11, 14, 15, 16])

        # Calculate random delay
        interval_min = schedule.get("interval_min", 30)
        interval_max = schedule.get("interval_max", 120)
        delay_minutes = random.randint(interval_min, interval_max)

        # Calculate send time
        now = datetime.utcnow() + timedelta(minutes=delay_minutes)

        # Simple implementation - just return delayed time
        # In production, would convert to target timezone and adjust to business hours
        return now

    async def _random_delay(self, schedule: Optional[Dict[str, Any]] = None):
        """Random delay between sends"""
        interval_min = schedule.get("interval_min", 30) if schedule else 30
        interval_max = schedule.get("interval_max", 120) if schedule else 120

        delay = random.randint(interval_min, interval_max)
        await asyncio.sleep(delay)


@register_skill
class ScheduleOutreachSkill(BaseSkill):
    """
    定时触达Skill

    为触达任务创建定时任务
    """
    name = "schedule_outreach"
    display_name = "Schedule Outreach"
    description = "创建定时触达任务"
    category = "outreach"
    version = "1.0.0"

    input_schema = {
        "type": "object",
        "required": ["customers", "channel"],
        "properties": {
            "customers": {
                "type": "array",
                "items": {"type": "object"}
            },
            "channel": {
                "type": "string",
                "enum": ["email", "whatsapp"]
            },
            "schedule": {
                "type": "object"
            },
            "template_id": {
                "type": "string"
            }
        }
    }

    output_schema = {
        "type": "object",
        "required": ["task_id", "scheduled_count"],
        "properties": {
            "task_id": {"type": "string"},
            "scheduled_count": {"type": "integer"}
        }
    }

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute scheduled outreach"""
        # Import task scheduling (would use Celery in production)
        from app.tasks.task_functions import schedule_outreach_task

        input_data = context.input_data
        customers = input_data.get("customers", [])
        channel = input_data.get("channel", "email")
        schedule = input_data.get("schedule", {})

        # Schedule task
        task_id = str(hash(str(customers) + channel + str(schedule)))

        # In production, this would create Celery tasks
        context.set_state("scheduled_outreach", {
            "task_id": task_id,
            "channel": channel,
            "count": len(customers)
        })

        return {
            "task_id": task_id,
            "scheduled_count": len(customers)
        }

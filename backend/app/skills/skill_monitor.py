"""
Skill 7: 老板监控与接管

功能：
- 实时任务状态监控
- 对话查看
- 一键接管
- 权限控制
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.core.skill_base import BaseSkill, register_skill
from app.core.context import ExecutionContext
from app.config import settings


@register_skill
class MonitorSkill(BaseSkill):
    """
    监控Skill

    实时监控工作流执行状态和对话
    """
    name = "monitor"
    display_name = "Monitor"
    description = "实时监控工作流执行状态和对话"
    category = "monitoring"
    version = "1.0.0"

    config_schema = {
        "type": "object",
        "properties": {
            "refresh_interval": {
                "type": "integer",
                "default": 30,
                "description": "刷新间隔（秒）"
            },
            "alert_thresholds": {
                "type": "object",
                "properties": {
                    "error_rate": {"type": "number", "default": 0.1},
                    "failure_time": {"type": "integer", "default": 300}
                }
            }
        }
    }

    default_config = {
        "refresh_interval": 30,
        "alert_thresholds": {
            "error_rate": 0.1,
            "failure_time": 300
        }
    }

    input_schema = {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "enum": ["workflow_status", "conversation_list", "customer_list", "dashboard"],
                "default": "dashboard"
            },
            "filters": {
                "type": "object",
                "description": "筛选条件"
            },
            "limit": {
                "type": "integer",
                "default": 50
            },
            "time_range": {
                "type": "string",
                "enum": ["today", "week", "month", "all"],
                "default": "today"
            }
        }
    }

    output_schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object"
            },
            "alerts": {
                "type": "array"
            }
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute monitoring

        Args:
            context: Execution context

        Returns:
            Dict containing monitoring data and alerts
        """
        input_data = context.input_data
        monitor_type = input_data.get("type", "dashboard")
        filters = input_data.get("filters", {})
        limit = input_data.get("limit", 50)
        time_range = input_data.get("time_range", "today")

        alerts = []

        # Get data based on type
        if monitor_type == "workflow_status":
            data = await self._get_workflow_status(context, filters, limit, time_range)
            alerts = self._check_workflow_alerts(data)

        elif monitor_type == "conversation_list":
            data = await self._get_conversation_list(context, filters, limit, time_range)
            alerts = self._check_conversation_alerts(data)

        elif monitor_type == "customer_list":
            data = await self._get_customer_list(context, filters, limit, time_range)

        else:  # dashboard
            data = await self._get_dashboard(context, time_range)
            alerts = self._check_dashboard_alerts(data)

        return {
            "data": data,
            "alerts": alerts,
            "refresh_interval": self.config.get("refresh_interval", 30)
        }

    async def _get_workflow_status(
        self,
        context: ExecutionContext,
        filters: Dict[str, Any],
        limit: int,
        time_range: str,
    ) -> Dict[str, Any]:
        """Get workflow execution status"""
        # In production, this would query the database
        return {
            "total": 10,
            "running": 2,
            "completed": 6,
            "failed": 1,
            "paused": 1,
            "executions": [
                {
                    "id": "exec_001",
                    "workflow_name": "outreach_workflow",
                    "status": "running",
                    "current_step": "send_messages",
                    "started_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                    "progress": 60
                },
                {
                    "id": "exec_002",
                    "workflow_name": "lead_generation",
                    "status": "failed",
                    "error": "Rate limit exceeded",
                    "started_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                    "finished_at": (datetime.utcnow() - timedelta(minutes=25)).isoformat()
                }
            ]
        }

    async def _get_conversation_list(
        self,
        context: ExecutionContext,
        filters: Dict[str, Any],
        limit: int,
        time_range: str,
    ) -> Dict[str, Any]:
        """Get conversation list"""
        # In production, this would query the database
        return {
            "total": 25,
            "active": 18,
            "awaiting_reply": 7,
            "high_intent": 5,
            "conversations": [
                {
                    "id": "conv_001",
                    "customer_id": 1,
                    "customer_name": "@brand123",
                    "platform": "email",
                    "status": "active",
                    "last_message": "What's your pricing for bulk orders?",
                    "last_message_at": (datetime.utcnow() - timedelta(minutes=2)).isoformat(),
                    "intent_level": "high",
                    "ai_handled": True
                },
                {
                    "id": "conv_002",
                    "customer_id": 2,
                    "customer_name": "@retailer456",
                    "platform": "whatsapp",
                    "status": "active",
                    "last_message": "I need samples asap",
                    "last_message_at": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                    "intent_level": "very_high",
                    "ai_handled": False,
                    "should_takeover": True
                }
            ]
        }

    async def _get_customer_list(
        self,
        context: ExecutionContext,
        filters: Dict[str, Any],
        limit: int,
        time_range: str,
    ) -> Dict[str, Any]:
        """Get customer list"""
        # In production, this would query the database
        return {
            "total": 150,
            "new": 30,
            "contacted": 80,
            "engaged": 25,
            "converted": 10,
            "lost": 5,
            "customers": [
                {
                    "id": 1,
                    "username": "@brand123",
                    "platform": "tiktok",
                    "email": "contact@brand.com",
                    "country": "US",
                    "follower_count": 50000,
                    "status": "engaged",
                    "intent_level": "high",
                    "last_contacted": (datetime.utcnow() - timedelta(hours=1)).isoformat()
                }
            ]
        }

    async def _get_dashboard(
        self,
        context: ExecutionContext,
        time_range: str,
    ) -> Dict[str, Any]:
        """Get dashboard summary"""
        # In production, this would aggregate data
        return {
            "summary": {
                "customers_found": 100,
                "messages_sent": 80,
                "emails_opened": 45,
                "replies_received": 15,
                "conversions": 3
            },
            "conversion_rate": 0.03,
            "avg_response_time": 2.5,  # hours
            "active_conversations": 18,
            "high_intent_leads": 5,
            "recent_activity": [
                {
                    "type": "message_sent",
                    "description": "Email sent to @brand123",
                    "time": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
                },
                {
                    "type": "reply_received",
                    "description": "Reply from @retailer456: 'What's your MOQ?'",
                    "time": (datetime.utcnow() - timedelta(minutes=15)).isoformat()
                }
            ]
        }

    def _check_workflow_alerts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for workflow-related alerts"""
        alerts = []

        if data.get("failed", 0) > 0:
            alerts.append({
                "type": "workflow_failed",
                "severity": "high",
                "message": f"{data['failed']} workflow(s) failed",
                "count": data["failed"]
            })

        return alerts

    def _check_conversation_alerts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for conversation-related alerts"""
        alerts = []

        conversations = data.get("conversations", [])
        for conv in conversations:
            if conv.get("should_takeover"):
                alerts.append({
                    "type": "takeover_needed",
                    "severity": "high",
                    "message": f"High intent conversation requires attention: {conv.get('customer_name')}",
                    "conversation_id": conv["id"]
                })

        return alerts

    def _check_dashboard_alerts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for dashboard alerts"""
        alerts = []
        thresholds = self.config.get("alert_thresholds", {})

        summary = data.get("summary", {})
        sent = summary.get("messages_sent", 0)
        opened = summary.get("emails_opened", 0)

        if sent > 0:
            open_rate = opened / sent
            if open_rate < (1 - thresholds.get("error_rate", 0.1)):
                alerts.append({
                    "type": "low_open_rate",
                    "severity": "medium",
                    "message": f"Email open rate is low: {open_rate:.1%}"
                })

        high_intent = data.get("high_intent_leads", 0)
        if high_intent > 0:
            alerts.append({
                "type": "high_intent_leads",
                "severity": "medium",
                "message": f"{high_intent} high intent leads need attention",
                "count": high_intent
            })

        return alerts


@register_skill
class TakeoverSkill(BaseSkill):
    """
    接管Skill

    支持人工接管对话或工作流
    """
    name = "takeover"
    display_name = "Takeover"
    description = "人工接管对话或工作流"
    category = "monitoring"
    version = "1.0.0"

    input_schema = {
        "type": "object",
        "required": ["target_type", "target_id"],
        "properties": {
            "target_type": {
                "type": "string",
                "enum": ["conversation", "execution", "workflow"]
            },
            "target_id": {
                "type": "string",
                "description": "对话ID或执行ID"
            },
            "action": {
                "type": "string",
                "enum": ["pause", "resume", "cancel", "takeover", "update_state"],
                "default": "takeover"
            },
            "reason": {
                "type": "string",
                "description": "接管原因"
            },
            "data": {
                "type": "object",
                "description": "附加数据（用于update_state）"
            }
        }
    }

    output_schema = {
        "type": "object",
        "required": ["success", "status"],
        "properties": {
            "success": {"type": "boolean"},
            "status": {"type": "string"},
            "message": {"type": "string"},
            "context": {"type": "object"}
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute takeover action

        Args:
            context: Execution context

        Returns:
            Dict containing action result
        """
        input_data = context.input_data
        target_type = input_data.get("target_type")
        target_id = input_data.get("target_id")
        action = input_data.get("action", "takeover")
        reason = input_data.get("reason", "manual_takeover")
        data = input_data.get("data", {})

        # Get agent orchestrator
        from app.core.agent import get_agent
        agent = get_agent()

        # Perform action based on target type
        if target_type == "execution" or target_type == "workflow":
            result = await self._handle_execution_takeover(
                agent, target_id, action, reason, data
            )
        elif target_type == "conversation":
            result = await self._handle_conversation_takeover(
                target_id, action, reason, data
            )
        else:
            result = {
                "success": False,
                "status": "error",
                "message": f"Unknown target type: {target_type}"
            }

        return result

    async def _handle_execution_takeover(
        self,
        agent,
        execution_id: str,
        action: str,
        reason: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle workflow execution takeover"""
        try:
            if action == "pause":
                agent.pause_execution(execution_id)
                status = "paused"
                message = f"Execution {execution_id} paused"
            elif action == "resume":
                agent.resume_execution(execution_id)
                status = "resumed"
                message = f"Execution {execution_id} resumed"
            elif action == "cancel":
                agent.cancel_execution(execution_id)
                status = "cancelled"
                message = f"Execution {execution_id} cancelled"
            elif action == "takeover":
                await agent.handle_interrupt(execution_id, "takeover", {"reason": reason})
                status = "paused_for_takeover"
                message = f"Execution {execution_id} paused for manual takeover"
            elif action == "update_state":
                await agent.handle_interrupt(execution_id, "update_state", data)
                status = "state_updated"
                message = f"Execution {execution_id} state updated"
            else:
                return {
                    "success": False,
                    "status": "error",
                    "message": f"Unknown action: {action}"
                }

            # Get execution status
            execution = agent.get_execution_status(execution_id)

            return {
                "success": True,
                "status": status,
                "message": message,
                "context": execution
            }

        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "message": str(e)
            }

    async def _handle_conversation_takeover(
        self,
        conversation_id: str,
        action: str,
        reason: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Handle conversation takeover"""
        # In production, this would update the database
        # For now, return mock response

        if action == "takeover":
            return {
                "success": True,
                "status": "taken_over",
                "message": f"Conversation {conversation_id} taken over manually",
                "context": {
                    "conversation_id": conversation_id,
                    "manual_takeover": True,
                    "takeover_reason": reason,
                    "taken_over_at": datetime.utcnow().isoformat()
                }
            }

        return {
            "success": False,
            "status": "error",
            "message": f"Unknown action: {action}"
        }


@register_skill
class AlertSkill(BaseSkill):
    """
    告警Skill

    管理告警通知
    """
    name = "alert"
    display_name = "Alert Manager"
    description = "管理告警通知和提醒"
    category = "monitoring"
    version = "1.0.0"

    config_schema = {
        "type": "object",
        "properties": {
            "channels": {
                "type": "array",
                "items": {"type": "string"},
                "enum": ["email", "webhook", "in_app"],
                "default": ["in_app"]
            },
            "webhook_url": {
                "type": "string"
            }
        }
    }

    default_config = {
        "channels": ["in_app"]
    }

    input_schema = {
        "type": "object",
        "required": ["alert"],
        "properties": {
            "alert": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "severity": {"type": "string"},
                    "message": {"type": "string"}
                }
            },
            "recipients": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "用户ID列表"
            }
        }
    }

    output_schema = {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "channels_used": {"type": "array"}
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute alert sending"""
        input_data = context.input_data
        alert = input_data.get("alert", {})
        recipients = input_data.get("recipients", [])

        channels = self.config.get("channels", ["in_app"])
        channels_used = []

        # Send through each configured channel
        if "in_app" in channels:
            await self._send_in_app_alert(alert, recipients)
            channels_used.append("in_app")

        if "webhook" in channels:
            await self._send_webhook_alert(alert)
            channels_used.append("webhook")

        if "email" in channels and recipients:
            await self._send_email_alert(alert, recipients)
            channels_used.append("email")

        return {
            "success": True,
            "channels_used": channels_used
        }

    async def _send_in_app_alert(self, alert: Dict[str, Any], recipients: List[int]):
        """Send in-app alert"""
        # In production, this would store in database for real-time display
        context.set_state("alert_sent", alert)

    async def _send_webhook_alert(self, alert: Dict[str, Any]):
        """Send webhook alert"""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return

        import httpx
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json=alert)

    async def _send_email_alert(self, alert: Dict[str, Any], recipients: List[int]):
        """Send email alert"""
        # In production, this would send emails to recipients
        pass

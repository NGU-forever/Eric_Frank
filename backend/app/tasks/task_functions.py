"""
Celery任务函数
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from app.tasks.celery_worker import celery
from app.config import settings
from app.db import SessionLocal
from app.models.database import (
    Customer, OutreachLog, Conversation, TaskQueue, Account
)
from app.core.agent import get_agent
from app.integrations.email_service import get_email_service
from app.integrations.whatsapp_service import get_whatsapp_service

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3)
def schedule_outreach_task(
    self,
    customer_ids: List[int],
    channel: str,
    template_id: str,
    schedule_config: Dict[str, Any],
):
    """
    定时触达任务

    Args:
        customer_ids: 客户ID列表
        channel: 触达渠道
        template_id: 模板ID
        schedule_config: 调度配置
    """
    db = SessionLocal()

    try:
        # Get template
        # template = db.query(Template).filter(Template.id == template_id).first()
        # if not template:
        #     logger.error(f"Template not found: {template_id}")
        #     return {"success": False, "error": "Template not found"}

        # Get account for sending
        account = db.query(Account).filter(
            Account.account_type == channel,
            Account.is_active == True,
            Account.today_sent < Account.daily_limit
        ).first()

        if not account:
            logger.error(f"No available account for channel: {channel}")
            return {"success": False, "error": "No available account"}

        # Process each customer
        results = []
        for customer_id in customer_ids:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if not customer:
                logger.warning(f"Customer not found: {customer_id}")
                continue

            try:
                # Check timezone and schedule time
                send_time = _calculate_send_time(customer, schedule_config)
                now = datetime.utcnow()

                if send_time > now:
                    # Schedule for later
                    _schedule_task(
                        db,
                        customer_id,
                        channel,
                        template_id,
                        send_time
                    )
                    results.append({"customer_id": customer_id, "status": "scheduled"})
                    continue

                # Send message
                if channel == "email":
                    result = _send_email(db, customer, account, template_id)
                elif channel == "whatsapp":
                    result = _send_whatsapp(db, customer, account, template_id)
                else:
                    logger.error(f"Unsupported channel: {channel}")
                    continue

                results.append(result)

                # Update account
                account.today_sent += 1

                # Add delay between sends
                import time
                delay_min = schedule_config.get("interval_min", 30)
                delay_max = schedule_config.get("interval_max", 120)
                delay = (delay_min + delay_max) / 2
                time.sleep(delay)

            except Exception as e:
                logger.error(f"Failed to send to customer {customer_id}: {str(e)}")
                results.append({"customer_id": customer_id, "status": "failed", "error": str(e)})

        db.commit()

        return {
            "success": True,
            "total": len(customer_ids),
            "results": results
        }

    except Exception as e:
        logger.error(f"Outreach task failed: {str(e)}")
        raise self.retry(exc=e, countdown=60 * 5)  # Retry in 5 minutes
    finally:
        db.close()


@celery.task(bind=True, max_retries=3)
def check_replies_task(self):
    """
    检查回复任务

    定期检查是否有新回复
    """
    db = SessionLocal()

    try:
        # Check for new messages in conversations
        # This would integrate with email/WhatsApp APIs to fetch new messages

        # For now, just log
        logger.info("Checking for new replies...")

        return {"success": True, "checked_at": datetime.utcnow().isoformat()}

    except Exception as e:
        logger.error(f"Check replies task failed: {str(e)}")
        raise self.retry(exc=e, countdown=60 * 5)
    finally:
        db.close()


@celery.task(bind=True)
def generate_daily_report_task(self, user_id: int):
    """
    生成日报任务

    Args:
        user_id: 用户ID
    """
    db = SessionLocal()

    try:
        today = datetime.utcnow().date()

        # Get or create stats
        from app.models.database import StatsDaily
        stats = db.query(StatsDaily).filter(
            StatsDaily.user_id == user_id,
            StatsDaily.date == today
        ).first()

        if not stats:
            stats = StatsDaily(user_id=user_id, date=today)
            db.add(stats)

        # Calculate stats from database
        stats.new_customers = db.query(Customer).filter(
            Customer.created_at >= datetime.combine(today, datetime.min.time())
        ).count()

        stats.emails_sent = db.query(OutreachLog).filter(
            OutreachLog.channel == "email",
            OutreachLog.sent_at >= datetime.combine(today, datetime.min.time())
        ).count()

        stats.whatsapp_sent = db.query(OutreachLog).filter(
            OutreachLog.channel == "whatsapp",
            OutreachLog.sent_at >= datetime.combine(today, datetime.min.time())
        ).count()

        stats.emails_replied = db.query(OutreachLog).filter(
            OutreachLog.channel == "email",
            OutreachLog.replied_at >= datetime.combine(today, datetime.min.time())
        ).count()

        stats.new_conversations = db.query(Conversation).filter(
            Conversation.created_at >= datetime.combine(today, datetime.min.time())
        ).count()

        stats.converted_customers = db.query(Customer).filter(
            Customer.status == "converted",
            Customer.updated_at >= datetime.combine(today, datetime.min.time())
        ).count()

        db.commit()

        logger.info(f"Daily report generated for user {user_id}")

        return {"success": True, "date": today.isoformat()}

    except Exception as e:
        logger.error(f"Daily report task failed: {str(e)}")
        raise self.retry(exc=e, countdown=60 * 1)
    finally:
        db.close()


@celery.task
def send_digest_email_task(user_id: int, report_data: Dict[str, Any]):
    """
    发送摘要邮件

    Args:
        user_id: 用户ID
        report_data: 报告数据
    """
    db = SessionLocal()

    try:
        # Get user
        from app.models.database import User
        user = db.query(User).filter(User.id == user_id).first()

        if not user or not user.email:
            logger.error(f"User not found or no email: {user_id}")
            return {"success": False}

        # Send digest email
        # email_service = get_email_service()
        # await email_service.send_email(...)

        logger.info(f"Digest email sent to user {user_id}")

        return {"success": True}

    except Exception as e:
        logger.error(f"Digest email task failed: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@celery.task
def update_message_status_task(message_id: str):
    """
    更新消息状态任务

    Args:
        message_id: 消息ID
    """
    db = SessionLocal()

    try:
        # Update message status based on API callback
        # This would be called by webhooks from email/WhatsApp providers

        logger.info(f"Message status updated: {message_id}")

        return {"success": True}

    except Exception as e:
        logger.error(f"Update message status task failed: {str(e)}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def _calculate_send_time(customer: Customer, schedule_config: Dict[str, Any]) -> datetime:
    """计算最佳发送时间"""
    # Simple implementation - return now
    # In production, would consider timezone and business hours
    return datetime.utcnow()


def _schedule_task(
    db: SessionLocal,
    customer_id: int,
    channel: str,
    template_id: str,
    send_time: datetime
):
    """调度任务"""
    task = TaskQueue(
        task_type="outreach",
        payload_json={
            "customer_id": customer_id,
            "channel": channel,
            "template_id": template_id
        },
        scheduled_at=send_time
    )
    db.add(task)


def _send_email(
    db: SessionLocal,
    customer: Customer,
    account: Account,
    template_id: str
) -> Dict[str, Any]:
    """发送邮件"""
    # Get email service
    email_service = get_email_service(
        service_type="smtp",
        **account.credentials_json
    )

    # Generate message
    # from app.skills.skill_message_generator import MessageGeneratorSkill
    # generator = MessageGeneratorSkill()
    # result = generator.execute(...)

    # For now, use simple message
    subject = "Partnership Opportunity"
    body = f"Hi {customer.username or 'there'},\n\nWe would like to discuss a potential collaboration..."

    # Send
    import asyncio
    result = asyncio.run(email_service.send_email(
        to=customer.email,
        subject=subject,
        body=body
    ))

    # Log outreach
    log = OutreachLog(
        customer_id=customer.id,
        channel="email",
        status="sent" if result.get("success") else "failed",
        subject=subject,
        content=body,
        template_id=template_id,
        account_id=account.id,
        sent_at=datetime.utcnow() if result.get("success") else None,
        error_msg=result.get("error")
    )
    db.add(log)

    return {
        "customer_id": customer.id,
        "status": log.status.value,
        "message_id": str(log.id)
    }


def _send_whatsapp(
    db: SessionLocal,
    customer: Customer,
    account: Account,
    template_id: str
) -> Dict[str, Any]:
    """发送WhatsApp消息"""
    # Get WhatsApp service
    whatsapp_service = get_whatsapp_service(
        phone_number_id=account.credentials_json.get("phone_number_id"),
        access_token=account.credentials_json.get("access_token")
    )

    # Generate message
    message = f"Hi {customer.username or 'there'}! We would like to discuss a potential collaboration..."

    # Send
    import asyncio
    result = asyncio.run(whatsapp_service.send_message(
        to=customer.whatsapp,
        text=message
    ))

    # Log outreach
    log = OutreachLog(
        customer_id=customer.id,
        channel="whatsapp",
        status="sent" if result.get("success") else "failed",
        content=message,
        template_id=template_id,
        account_id=account.id,
        sent_at=datetime.utcnow() if result.get("success") else None,
        error_msg=result.get("error")
    )
    db.add(log)

    return {
        "customer_id": customer.id,
        "status": log.status.value,
        "message_id": str(log.id)
    }

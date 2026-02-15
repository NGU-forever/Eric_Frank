"""
对话管理相关API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.database import User, Conversation, Message
from app.models.schemas import (
    ConversationCreate, ConversationResponse, ConversationWithMessagesResponse,
    MessageCreate, MessageResponse
)
from app.core.agent import get_agent
from app.api.v1.auth import get_current_active_user

router = APIRouter()


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    customer_id: Optional[int] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """列出对话"""
    query = db.query(Conversation)

    if customer_id:
        query = query.filter(Conversation.customer_id == customer_id)
    if platform:
        query = query.filter(Conversation.platform == platform)
    if status:
        query = query.filter(Conversation.status == status)

    conversations = query.order_by(
        Conversation.last_message_at.desc().nulls_last()
    ).limit(limit).all()

    return conversations


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建对话"""
    # Check for existing conversation
    existing = db.query(Conversation).filter(
        Conversation.customer_id == conversation.customer_id,
        Conversation.platform == conversation.platform
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Conversation already exists")

    db_conversation = Conversation(**conversation.model_dump())
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return db_conversation


@router.get("/{conversation_id}", response_model=ConversationWithMessagesResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取对话详情及消息"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.sent_at).all()

    return ConversationWithMessagesResponse(
        **conversation.__dict__,
        messages=messages
    )


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取对话消息"""
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.sent_at.desc()).limit(limit).all()

    return list(reversed(messages))


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def create_message(
    conversation_id: str,
    message: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """创建消息"""
    # Get conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    db_message = Message(
        conversation_id=conversation_id,
        role=message.role,
        content=message.content,
        platform_message_id=message.platform_message_id,
        ai_generated=message.ai_generated,
        intent_detected=message.intent_detected,
        suggested_actions=message.suggested_actions,
        attachments=message.attachments,
    )
    db.add(db_message)

    # Update conversation
    conversation.last_message_at = db_message.sent_at

    db.commit()
    db.refresh(db_message)

    return db_message


@router.post("/{conversation_id}/reply")
async def reply_to_conversation(
    conversation_id: str,
    content: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """AI回复对话"""
    # Get conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get customer
    customer = db.query(Customer).filter(
        Customer.id == conversation.customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Get message history
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.sent_at).limit(20).all()

    # Get agent and handle message
    agent = get_agent()

    async def reply_generator():
        try:
            result = await agent.handle_message(
                conversation_id=conversation_id,
                customer_id=conversation.customer_id,
                platform=conversation.platform,
                incoming_message=content,
                message_history=[{
                    "role": m.role,
                    "content": m.content
                } for m in messages],
                customer_data={
                    "id": customer.id,
                    "username": customer.username,
                    "email": customer.email,
                    "whatsapp": customer.whatsapp,
                    "country": customer.country,
                    "category": customer.category,
                    "account_type": customer.account_type,
                }
            )

            if result.get("success"):
                # Save AI reply
                db_message = Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=result.get("reply", ""),
                    ai_generated=True,
                    intent_detected=result.get("intent"),
                    suggested_actions=result.get("suggested_actions", []),
                )
                db.add(db_message)

                # Update conversation
                conversation.current_intent = result.get("intent")
                conversation.intent_confidence = result.get("intent_confidence", 0.0)
                conversation.ai_handled = True
                conversation.last_message_at = db_message.sent_at

                db.commit()

                yield {
                    "type": "reply",
                    "reply": result.get("reply"),
                    "intent": result.get("intent"),
                    "intent_level": result.get("intent_level"),
                    "suggested_actions": result.get("suggested_actions", []),
                    "message_id": str(db_message.id)
                }
            else:
                yield {
                    "type": "error",
                    "error": result.get("error", "Failed to generate reply")
                }

        except Exception as e:
            yield {
                "type": "error",
                "error": str(e)
            }

    return StreamingResponse(
        reply_generator(),
        media_type="text/event-stream"
    )


@router.post("/{conversation_id}/takeover")
async def takeover_conversation(
    conversation_id: str,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """人工接管对话"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.manual_takeover = True
    conversation.takeover_reason = reason or "manual_takeover"
    conversation.ai_handled = False

    db.commit()

    return {"message": "Conversation taken over", "reason": reason}


@router.post("/{conversation_id}/release")
async def release_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """释放对话（交回AI）"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.manual_takeover = False
    conversation.takeover_reason = None
    conversation.ai_handled = True

    db.commit()

    return {"message": "Conversation released to AI"}

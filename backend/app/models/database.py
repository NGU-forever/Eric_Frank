"""
SQLAlchemy database models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum,
    JSON, Float, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.db import Base


class WorkflowStatus(str, enum.Enum):
    """Workflow status enum"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatus(str, enum.Enum):
    """Execution status enum"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OutreachStatus(str, enum.Enum):
    """Outreach status enum"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    FAILED = "failed"
    BOUNCED = "bounced"


class ConversationStatus(str, enum.Enum):
    """Conversation status enum"""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"


class TaskStatus(str, enum.Enum):
    """Task status enum"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class IntentLevel(str, enum.Enum):
    """Intent level enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # admin, user, operator
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    workflows = relationship("Workflow", back_populates="user", cascade="all, delete-orphan")


class Workflow(Base):
    """Workflow model"""
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    config_json = Column(JSON)
    variables = Column(JSON, default={})
    user_id = Column(Integer, ForeignKey("users.id"))
    version = Column(String(20), default="1.0.0")
    tags = Column(JSON, default=[])  # List of tag strings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="workflows")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_workflow_user_status', 'user_id', 'status'),
    )


class WorkflowExecution(Base):
    """Workflow execution model"""
    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id"))
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    current_step = Column(String(100))
    context_json = Column(JSON)
    error_msg = Column(Text)
    error_stack = Column(Text)
    input_data = Column(JSON)
    output_data = Column(JSON)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    completed_steps = Column(JSON, default=[])  # List of step names
    failed_steps = Column(JSON, default=[])  # List of step names
    paused_steps = Column(JSON, default=[])  # List of step names
    metrics = Column(JSON, default={})  # Execution metrics

    # Relationships
    workflow = relationship("Workflow", back_populates="executions")

    __table_args__ = (
        Index('idx_execution_workflow_status', 'workflow_id', 'status'),
        Index('idx_execution_started_at', 'started_at'),
    )


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100))
    platform = Column(String(50))  # tiktok, instagram, facebook, youtube, etc.
    email = Column(String(255), index=True)
    whatsapp = Column(String(20))
    phone = Column(String(20))
    country = Column(String(10), index=True)
    category = Column(String(50))  # fashion, beauty, electronics, etc.
    subcategory = Column(String(50))
    follower_count = Column(Integer)
    account_type = Column(String(20))  # creator, brand, mcn, retailer
    intent_level = Column(Enum(IntentLevel))
    tags_json = Column(JSON, default=[])  # List of tags
    source_data_json = Column(JSON)  # Raw data from source
    contact_info = Column(JSON)  # Additional contact info
    social_links = Column(JSON)  # Links to social profiles
    website = Column(String(255))
    company_name = Column(String(100))
    job_title = Column(String(100))

    # Status tracking
    status = Column(String(20), default="new")  # new, contacted, engaged, converted, lost
    first_contacted_at = Column(DateTime)
    last_contacted_at = Column(DateTime)
    last_replied_at = Column(DateTime)

    # Metadata
    notes = Column(Text)
    custom_fields = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    conversations = relationship("Conversation", back_populates="customer", cascade="all, delete-orphan")
    outreach_logs = relationship("OutreachLog", back_populates="customer", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_customer_platform_status', 'platform', 'status'),
        Index('idx_customer_country_category', 'country', 'category'),
        UniqueConstraint('username', 'platform', name='uq_customer_username_platform'),
    )


class Conversation(Base):
    """Conversation model"""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    platform = Column(String(50))  # email, whatsapp, instagram_dm, etc.
    platform_conversation_id = Column(String(255))  # External conversation ID
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)

    # Intent tracking
    intent_level_json = Column(JSON, default={})  # History of intent levels
    current_intent = Column(String(50))  # price_inquiry, collaboration, sample_request, etc.
    intent_confidence = Column(Float, default=0.0)

    # Metadata
    summary = Column(Text)
    tags = Column(JSON, default=[])
    custom_fields = Column(JSON, default={})

    # AI handling
    ai_handled = Column(Boolean, default=False)
    manual_takeover = Column(Boolean, default=False)
    takeover_reason = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime)

    # Relationships
    customer = relationship("Customer", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_conversation_customer_status', 'customer_id', 'status'),
        Index('idx_conversation_platform_id', 'platform', 'platform_conversation_id'),
    )


class Message(Base):
    """Message model"""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    role = Column(String(20))  # user, system, assistant
    content = Column(Text)
    platform_message_id = Column(String(255))

    # AI metadata
    ai_generated = Column(Boolean, default=False)
    ai_confidence = Column(Float)
    intent_detected = Column(String(50))
    suggested_actions = Column(JSON, default=[])

    # Status
    sent_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    failed_at = Column(DateTime)
    error_message = Column(Text)

    # Attachments
    attachments = Column(JSON, default=[])

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index('idx_message_conversation_sent', 'conversation_id', 'sent_at'),
    )


class OutreachLog(Base):
    """Outreach log model"""
    __tablename__ = "outreach_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    channel = Column(String(50))  # email, whatsapp
    status = Column(Enum(OutreachStatus), default=OutreachStatus.PENDING)

    # Message info
    message_id = Column(String(255))  # External message ID
    subject = Column(String(255))  # For emails
    content = Column(Text)
    template_id = Column(String(100))

    # Account used
    account_id = Column(Integer)  # Reference to accounts table
    account_type = Column(String(20))  # gmail, outlook, whatsapp_business

    # Scheduling
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)

    # Tracking
    delivered_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    replied_at = Column(DateTime)
    bounced_at = Column(DateTime)

    # Error handling
    error_msg = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # Metrics
    cost = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="outreach_logs")

    __table_args__ = (
        Index('idx_outreach_customer_status', 'customer_id', 'status'),
        Index('idx_outreach_channel_status', 'channel', 'status'),
        Index('idx_outreach_scheduled', 'scheduled_at'),
    )


class Account(Base):
    """Account model for email/WhatsApp credentials"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    account_type = Column(String(20))  # gmail, outlook, whatsapp_business
    name = Column(String(100))
    email = Column(String(255))
    phone_number = Column(String(20))

    # Credentials (encrypted in production)
    credentials_json = Column(JSON)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_used = Column(DateTime)

    # Rate limiting
    daily_limit = Column(Integer, default=100)
    today_sent = Column(Integer, default=0)
    last_reset = Column(DateTime, default=datetime.utcnow)

    # Metadata
    labels = Column(JSON, default=[])

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_account_user_type', 'user_id', 'account_type'),
        UniqueConstraint('email', 'account_type', name='uq_account_email_type'),
    )


class TaskQueue(Base):
    """Task queue model"""
    __tablename__ = "task_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type = Column(String(50))  # outreach, check_replies, generate_report, etc.
    payload_json = Column(JSON)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)

    # Priority
    priority = Column(Integer, default=0)  # Higher = more important

    # Scheduling
    scheduled_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Retry handling
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    retry_after = Column(DateTime)

    # Worker info
    worker_id = Column(String(100))
    celery_task_id = Column(String(255), index=True)

    # Error handling
    error_msg = Column(Text)
    error_stack = Column(Text)

    # Dependencies
    depends_on = Column(JSON)  # List of task IDs that must complete first

    # Result
    result_json = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_task_type_status', 'task_type', 'status'),
        Index('idx_task_scheduled', 'scheduled_at'),
        Index('idx_task_celery_id', 'celery_task_id'),
    )


class Template(Base):
    """Message template model"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    template_type = Column(String(20))  # email, whatsapp
    language = Column(String(10), default="en")
    category = Column(String(50))  # introduction, followup, inquiry, etc.

    # Content
    subject_template = Column(String(255))  # For emails
    body_template = Column(Text)
    variables = Column(JSON, default=[])  # List of variable names

    # Usage
    use_count = Column(Integer, default=0)
    success_rate = Column(Float)

    # Status
    is_active = Column(Boolean, default=True)

    # Owner
    user_id = Column(Integer, ForeignKey("users.id"))
    is_default = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50))  # create, update, delete, execute, pause, resume, takeover
    resource_type = Column(String(50))  # workflow, customer, conversation, etc.
    resource_id = Column(String(255))

    # Details
    details_json = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))

    # Result
    success = Column(Boolean, default=True)
    error_msg = Column(Text)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_created', 'created_at'),
    )


class StatsDaily(Base):
    """Daily statistics model"""
    __tablename__ = "stats_daily"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, index=True)  # Only date part matters

    # Customer stats
    new_customers = Column(Integer, default=0)
    active_customers = Column(Integer, default=0)
    converted_customers = Column(Integer, default=0)

    # Outreach stats
    emails_sent = Column(Integer, default=0)
    whatsapp_sent = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    emails_replied = Column(Integer, default=0)

    # Conversation stats
    new_conversations = Column(Integer, default=0)
    active_conversations = Column(Integer, default=0)
    ai_handled = Column(Integer, default=0)
    manual_takeovers = Column(Integer, default=0)

    # Workflow stats
    workflows_executed = Column(Integer, default=0)
    workflows_completed = Column(Integer, default=0)
    workflows_failed = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_stats_user_date'),
    )

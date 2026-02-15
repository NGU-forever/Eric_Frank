"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


# ============================================
# Base Schemas
# ============================================

class TimestampsMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================
# Auth Schemas
# ============================================

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase, TimestampsMixin):
    """User response schema"""
    id: int
    role: str
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[int] = None
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str


# ============================================
# Workflow Schemas
# ============================================

class WorkflowStatusEnum(str, Enum):
    """Workflow status enum"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ExecutionStatusEnum(str, Enum):
    """Execution status enum"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepDefinitionSchema(BaseModel):
    """Workflow step definition schema"""
    name: str
    skill_name: str
    config: Dict[str, Any] = Field(default_factory=dict)
    condition: str = "always"
    condition_expression: Optional[str] = None
    retry_on_failure: bool = True
    max_retries: int = Field(default=3, ge=0)
    timeout: Optional[int] = Field(None, ge=1)
    on_failure_action: Optional[str] = Field(None, pattern="^(skip|stop|continue)$")


class TransitionSchema(BaseModel):
    """Workflow transition schema"""
    from_step: str
    to_step: str
    condition: Optional[str] = None


class WorkflowCreate(BaseModel):
    """Workflow creation schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    steps: List[StepDefinitionSchema] = Field(default_factory=list)
    transitions: List[TransitionSchema] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    version: str = "1.0.0"


class WorkflowUpdate(BaseModel):
    """Workflow update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    steps: Optional[List[StepDefinitionSchema]] = None
    transitions: Optional[List[TransitionSchema]] = None
    variables: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    status: Optional[WorkflowStatusEnum] = None
    version: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Workflow response schema"""
    id: str
    name: str
    description: Optional[str]
    status: WorkflowStatusEnum
    version: str
    tags: List[str]
    variables: Dict[str, Any]
    config_json: Dict[str, Any]
    user_id: int

    class Config:
        from_attributes = True


class WorkflowExecuteRequest(BaseModel):
    """Workflow execution request schema"""
    workflow_id: str
    input_data: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResponse(BaseModel):
    """Execution response schema"""
    id: str
    workflow_id: str
    status: ExecutionStatusEnum
    current_step: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    error_msg: Optional[str]
    completed_steps: List[str]
    failed_steps: List[str]
    metrics: Dict[str, Any]

    class Config:
        from_attributes = True


class ExecutionInterruptRequest(BaseModel):
    """Execution interrupt request schema"""
    action: str = Field(..., pattern="^(pause|resume|cancel|takeover|update_state)$")
    data: Optional[Dict[str, Any]] = None


# ============================================
# Customer Schemas
# ============================================

class IntentLevelEnum(str, Enum):
    """Intent level enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class CustomerStatusEnum(str, Enum):
    """Customer status enum"""
    NEW = "new"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    CONVERTED = "converted"
    LOST = "lost"


class AccountTypeEnum(str, Enum):
    """Account type enum"""
    CREATOR = "creator"
    BRAND = "brand"
    MCN = "mcn"
    RETAILER = "retailer"


class CustomerCreate(BaseModel):
    """Customer creation schema"""
    username: Optional[str] = None
    platform: Optional[str] = None
    email: Optional[EmailStr] = None
    whatsapp: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    follower_count: Optional[int] = Field(None, ge=0)
    account_type: Optional[AccountTypeEnum] = None
    website: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    """Customer update schema"""
    email: Optional[EmailStr] = None
    whatsapp: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    follower_count: Optional[int] = Field(None, ge=0)
    account_type: Optional[AccountTypeEnum] = None
    website: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    status: Optional[CustomerStatusEnum] = None
    intent_level: Optional[IntentLevelEnum] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class CustomerResponse(BaseModel):
    """Customer response schema"""
    id: int
    username: Optional[str]
    platform: Optional[str]
    email: Optional[str]
    whatsapp: Optional[str]
    phone: Optional[str]
    country: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    follower_count: Optional[int]
    account_type: Optional[str]
    website: Optional[str]
    company_name: Optional[str]
    job_title: Optional[str]
    status: str
    intent_level: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerListResponse(BaseModel):
    """Customer list response schema"""
    items: List[CustomerResponse]
    total: int
    page: int
    page_size: int


# ============================================
# Conversation Schemas
# ============================================

class ConversationStatusEnum(str, Enum):
    """Conversation status enum"""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ConversationCreate(BaseModel):
    """Conversation creation schema"""
    customer_id: int
    platform: str
    platform_conversation_id: Optional[str] = None


class ConversationResponse(BaseModel):
    """Conversation response schema"""
    id: str
    customer_id: int
    platform: str
    status: str
    current_intent: Optional[str]
    intent_confidence: float
    ai_handled: bool
    manual_takeover: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime]

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Message creation schema"""
    conversation_id: str
    role: str = Field(..., pattern="^(user|system|assistant)$")
    content: str
    platform_message_id: Optional[str] = None
    ai_generated: bool = False
    intent_detected: Optional[str] = None
    suggested_actions: List[str] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)


class MessageResponse(BaseModel):
    """Message response schema"""
    id: str
    conversation_id: str
    role: str
    content: str
    platform_message_id: Optional[str]
    ai_generated: bool
    sent_at: datetime
    read_at: Optional[datetime]
    intent_detected: Optional[str]
    suggested_actions: List[str]
    attachments: List[str]

    class Config:
        from_attributes = True


class ConversationWithMessagesResponse(ConversationResponse):
    """Conversation with messages response schema"""
    messages: List[MessageResponse]


# ============================================
# Outreach Schemas
# ============================================

class OutreachStatusEnum(str, Enum):
    """Outreach status enum"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    DELIVERED = "delivered"
    OPENED = "opened"
    REPLIED = "replied"
    FAILED = "failed"
    BOUNCED = "bounced"


class OutreachCreate(BaseModel):
    """Outreach creation schema"""
    customer_id: int
    channel: str = Field(..., pattern="^(email|whatsapp)$")
    subject: Optional[str] = None
    content: str
    template_id: Optional[str] = None
    account_id: Optional[int] = None
    scheduled_at: Optional[datetime] = None


class OutreachResponse(BaseModel):
    """Outreach response schema"""
    id: str
    customer_id: int
    channel: str
    status: str
    subject: Optional[str]
    template_id: Optional[str]
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    opened_at: Optional[datetime]
    replied_at: Optional[datetime]
    error_msg: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BulkOutreachRequest(BaseModel):
    """Bulk outreach request schema"""
    customer_ids: List[int]
    channel: str = Field(..., pattern="^(email|whatsapp)$")
    template_id: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None


# ============================================
# Account Schemas
# ============================================

class AccountCreate(BaseModel):
    """Account creation schema"""
    account_type: str = Field(..., pattern="^(gmail|outlook|whatsapp_business)$")
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    credentials: Dict[str, Any]
    daily_limit: int = Field(default=100, ge=1, le=1000)


class AccountUpdate(BaseModel):
    """Account update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
    daily_limit: Optional[int] = Field(None, ge=1, le=1000)
    credentials: Optional[Dict[str, Any]] = None


class AccountResponse(BaseModel):
    """Account response schema"""
    id: int
    account_type: str
    name: str
    email: Optional[str]
    phone_number: Optional[str]
    is_active: bool
    is_verified: bool
    daily_limit: int
    today_sent: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Template Schemas
# ============================================

class TemplateCreate(BaseModel):
    """Template creation schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    template_type: str = Field(..., pattern="^(email|whatsapp)$")
    language: str = "en"
    category: str
    subject_template: Optional[str] = None
    body_template: str
    variables: List[str] = Field(default_factory=list)


class TemplateUpdate(BaseModel):
    """Template update schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    subject_template: Optional[str] = None
    body_template: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TemplateResponse(BaseModel):
    """Template response schema"""
    id: int
    name: str
    description: Optional[str]
    template_type: str
    language: str
    category: str
    subject_template: Optional[str]
    body_template: str
    variables: List[str]
    use_count: int
    success_rate: Optional[float]
    is_active: bool
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Stats Schemas
# ============================================

class StatsResponse(BaseModel):
    """Statistics response schema"""
    date: datetime

    # Customer stats
    new_customers: int
    active_customers: int
    converted_customers: int

    # Outreach stats
    emails_sent: int
    whatsapp_sent: int
    emails_opened: int
    emails_replied: int

    # Conversation stats
    new_conversations: int
    active_conversations: int
    ai_handled: int
    manual_takeovers: int

    # Workflow stats
    workflows_executed: int
    workflows_completed: int
    workflows_failed: int


class DashboardStats(BaseModel):
    """Dashboard statistics schema"""
    today: StatsResponse
    week: StatsResponse
    month: StatsResponse
    conversion_rate: float
    avg_response_time: float


# ============================================
# Skill Schemas
# ============================================

class SkillMetadataResponse(BaseModel):
    """Skill metadata response schema"""
    name: str
    display_name: str
    description: str
    category: str
    version: str
    config_schema: Dict[str, Any]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    timeout: int
    retry_count: int


class SkillListResponse(BaseModel):
    """Skill list response schema"""
    skills: List[SkillMetadataResponse]
    categories: List[str]


# ============================================
# Common Schemas
# ============================================

class PaginationParams(BaseModel):
    """Pagination parameters schema"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[TypeVar("T")]):
    """Generic paginated response schema"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Success response schema"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class SearchFilters(BaseModel):
    """Search filters schema"""
    query: Optional[str] = None
    country: Optional[List[str]] = None
    category: Optional[List[str]] = None
    status: Optional[List[str]] = None
    intent_level: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

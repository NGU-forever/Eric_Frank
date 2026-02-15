"""
Context management for Agent execution
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json
from dataclasses import dataclass, field, asdict


@dataclass
class ExecutionContext:
    """
    Execution context passed between Skills and workflow steps
    """
    # Workflow identification
    workflow_id: str
    execution_id: str
    user_id: Optional[int] = None

    # Step tracking
    current_step: Optional[str] = None
    step_history: list = field(default_factory=list)

    # Data storage
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    shared_state: Dict[str, Any] = field(default_factory=dict)

    # Execution metadata
    started_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # Status and error handling
    status: str = "running"  # running, paused, completed, failed
    error_message: Optional[str] = None
    error_stack: Optional[str] = None

    # Interruption handling
    interrupted: bool = False
    interrupt_reason: Optional[str] = None

    # Metrics
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for storage"""
        data = asdict(self)
        # Convert datetime to ISO string
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExecutionContext":
        """Create context from dictionary"""
        # Convert ISO string to datetime
        for key in ["started_at", "updated_at", "completed_at"]:
            if data.get(key) and isinstance(data[key], str):
                data[key] = datetime.fromisoformat(data[key])
        return cls(**data)

    def update_timestamp(self):
        """Update the timestamp"""
        self.updated_at = datetime.utcnow()

    def add_step(self, step_name: str):
        """Add a step to the history"""
        self.step_history.append({
            "step": step_name,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.current_step = step_name
        self.update_timestamp()

    def set_input(self, key: str, value: Any):
        """Set input data"""
        self.input_data[key] = value
        self.update_timestamp()

    def set_output(self, key: str, value: Any):
        """Set output data"""
        self.output_data[key] = value
        self.update_timestamp()

    def set_state(self, key: str, value: Any):
        """Set shared state"""
        self.shared_state[key] = value
        self.update_timestamp()

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get from shared state"""
        return self.shared_state.get(key, default)

    def increment_metric(self, metric: str, value: int = 1):
        """Increment a metric"""
        self.metrics[metric] = self.metrics.get(metric, 0) + value

    def set_error(self, message: str, stack: Optional[str] = None):
        """Set error status"""
        self.status = "failed"
        self.error_message = message
        self.error_stack = stack
        self.update_timestamp()

    def complete(self):
        """Mark execution as completed"""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.update_timestamp()

    def pause(self, reason: Optional[str] = None):
        """Pause execution"""
        self.status = "paused"
        self.interrupted = True
        self.interrupt_reason = reason
        self.update_timestamp()

    def resume(self):
        """Resume execution"""
        self.status = "running"
        self.interrupted = False
        self.interrupt_reason = None
        self.update_timestamp()

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


@dataclass
class MessageContext:
    """
    Context for message/conversation handling
    """
    conversation_id: str
    customer_id: int
    platform: str

    # Message data
    incoming_message: Optional[str] = None
    message_history: list = field(default_factory=list)

    # Customer data
    customer_data: Dict[str, Any] = field(default_factory=dict)

    # Intent analysis
    detected_intent: Optional[str] = None
    intent_confidence: float = 0.0
    intent_level: Optional[str] = None  # low, medium, high

    # Response
    generated_reply: Optional[str] = None
    suggested_actions: list = field(default_factory=list)

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processing_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if isinstance(data["timestamp"], datetime):
            data["timestamp"] = data["timestamp"].isoformat()
        return data

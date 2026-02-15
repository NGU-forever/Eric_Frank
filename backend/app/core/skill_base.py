"""
Base Skill class for all plugin skills
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import traceback
from enum import Enum

from app.core.context import ExecutionContext
from app.config import settings


class SkillStatus(Enum):
    """Skill execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class BaseSkill(ABC):
    """
    Abstract base class for all Skill plugins

    All skills must inherit from this class and implement the required methods.
    """

    # Skill metadata (must be set by subclasses)
    name: str
    display_name: str
    description: str
    category: str  # data, outreach, ai, monitoring, etc.
    version: str = "1.0.0"

    # Configuration
    config_schema: Dict[str, Any] = {}
    default_config: Dict[str, Any] = {}

    # Input/Output schemas
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}

    # Execution settings
    timeout: int = 300  # seconds
    retry_count: int = 3
    retry_delay: int = 1  # seconds

    # Skill state
    _status: SkillStatus = SkillStatus.PENDING
    _start_time: Optional[datetime] = None
    _end_time: Optional[datetime] = None
    _error: Optional[Exception] = None

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize skill with configuration

        Args:
            config: Skill-specific configuration
        """
        self.config = {**self.default_config, **(config or {})}
        self._validate_config()

    def _validate_config(self):
        """Validate the configuration"""
        # Can be overridden for custom validation
        pass

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Main execution method - must be implemented by subclasses

        Args:
            context: The execution context with input data

        Returns:
            Dict containing the skill's output data

        Raises:
            Exception: If execution fails (will be caught and handled)
        """
        pass

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Validate input data against the schema

        Args:
            data: Input data to validate

        Returns:
            True if valid, False otherwise

        Note:
            Can be overridden for custom validation logic
        """
        # Simple schema validation
        for field, schema in self.input_schema.items():
            if schema.get("required", False) and field not in data:
                return False
        return True

    def validate_output(self, data: Dict[str, Any]) -> bool:
        """
        Validate output data against the schema

        Args:
            data: Output data to validate

        Returns:
            True if valid, False otherwise
        """
        # Simple schema validation
        for field, schema in self.output_schema.items():
            if schema.get("required", False) and field not in data:
                return False
        return True

    def on_start(self, context: ExecutionContext):
        """
        Called when skill starts execution

        Can be overridden for custom logic
        """
        self._status = SkillStatus.RUNNING
        self._start_time = datetime.utcnow()
        context.add_step(f"{self.name}_start")

    def on_success(self, context: ExecutionContext, output: Dict[str, Any]):
        """
        Called when skill completes successfully

        Can be overridden for custom logic (e.g., logging, notifications)
        """
        self._status = SkillStatus.SUCCESS
        self._end_time = datetime.utcnow()
        context.add_step(f"{self.name}_success")

    def on_failure(self, error: Exception, context: ExecutionContext):
        """
        Called when skill fails

        Can be overridden for custom error handling (e.g., notifications)
        """
        self._status = SkillStatus.FAILED
        self._error = error
        self._end_time = datetime.utcnow()
        context.add_step(f"{self.name}_failed")

        # Log the error
        error_msg = f"Skill {self.name} failed: {str(error)}"
        if settings.DEBUG:
            error_msg += f"\n{traceback.format_exc()}"

        context.set_error(error_msg, traceback.format_exc() if settings.DEBUG else None)

    def on_skip(self, context: ExecutionContext, reason: str):
        """
        Called when skill is skipped

        Can be overridden for custom logic
        """
        self._status = SkillStatus.SKIPPED
        self._end_time = datetime.utcnow()
        context.add_step(f"{self.name}_skipped")
        context.set_state(f"{self.name}_skip_reason", reason)

    def get_execution_time(self) -> float:
        """Get the execution time in seconds"""
        if self._start_time and self._end_time:
            return (self._end_time - self._start_time).total_seconds()
        return 0.0

    def get_status(self) -> SkillStatus:
        """Get current status"""
        return self._status

    def get_error(self) -> Optional[Exception]:
        """Get the error if any"""
        return self._error

    def get_metadata(self) -> Dict[str, Any]:
        """Get skill metadata"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "config_schema": self.config_schema,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
        }

    def get_info(self) -> Dict[str, Any]:
        """Get skill info for display/UI"""
        return {
            **self.get_metadata(),
            "status": self._status.value if self._status else None,
            "execution_time": self.get_execution_time(),
            "error": str(self._error) if self._error else None,
        }

    async def run(self, context: ExecutionContext) -> Dict[str, Any]:
        """
        Main entry point for running a skill with lifecycle hooks

        Args:
            context: The execution context

        Returns:
            Dict containing the skill's output data
        """
        # Validate input
        if not self.validate_input(context.input_data):
            raise ValueError(f"Invalid input for skill {self.name}")

        # Call on_start
        self.on_start(context)

        # Execute the skill (with retry logic)
        last_error = None
        for attempt in range(self.retry_count + 1):
            try:
                output = await self.execute(context)

                # Validate output
                if not self.validate_output(output):
                    raise ValueError(f"Invalid output from skill {self.name}")

                # Success - call on_success and return
                self.on_success(context, output)
                return output

            except Exception as e:
                last_error = e
                if attempt < self.retry_count:
                    # Retry after delay
                    import asyncio
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    # Final attempt failed - call on_failure and re-raise
                    self.on_failure(e, context)
                    raise

        # Should never reach here
        raise last_error or Exception("Skill execution failed")

    @classmethod
    def get_all_subclasses(cls) -> List["BaseSkill"]:
        """Get all subclasses of BaseSkill"""
        return cls.__subclasses__()


class SkillRegistry:
    """
    Registry for managing skill plugins
    """
    _skills: Dict[str, type] = {}

    @classmethod
    def register(cls, skill_class: type):
        """Register a skill class"""
        if not issubclass(skill_class, BaseSkill):
            raise TypeError(f"{skill_class} must be a subclass of BaseSkill")
        cls._skills[skill_class.name] = skill_class
        return skill_class

    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """Get a skill class by name"""
        return cls._skills.get(name)

    @classmethod
    def list_all(cls) -> Dict[str, type]:
        """Get all registered skills"""
        return cls._skills.copy()

    @classmethod
    def create_instance(cls, name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseSkill]:
        """Create an instance of a registered skill"""
        skill_class = cls.get(name)
        if skill_class:
            return skill_class(config)
        return None

    @classmethod
    def get_categories(cls) -> List[str]:
        """Get all unique skill categories"""
        categories = set()
        for skill_class in cls._skills.values():
            categories.add(skill_class.category)
        return sorted(categories)

    @classmethod
    def get_by_category(cls, category: str) -> Dict[str, type]:
        """Get all skills in a category"""
        return {
            name: skill_class
            for name, skill_class in cls._skills.items()
            if skill_class.category == category
        }


# Decorator for easy registration
def register_skill(cls):
    """Decorator to register a skill class"""
    return SkillRegistry.register(cls)

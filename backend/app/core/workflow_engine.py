"""
Workflow engine based on LangGraph for executing skill pipelines
"""
import asyncio
import json
from typing import Dict, Any, Optional, List, AsyncIterator, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.sqlite import SqliteSaver
except ImportError:
    # Mock classes for missing dependencies
    class StateGraph:
        def __init__(self, *args, **kwargs): pass
        def add_node(self, *args, **kwargs): pass
        def add_edge(self, *args, **kwargs): pass
        def set_entry_point(self, *args, **kwargs): pass
        def compile(self, *args, **kwargs): return self
        def astream(self, *args, **kwargs): 
            async def _gen(): 
                if False: yield {}
            return _gen()
    END = "END"
    class SqliteSaver:
        def __init__(self, *args, **kwargs): pass
        @classmethod
        def from_conn_string(cls, *args, **kwargs): return cls()

from app.core.context import ExecutionContext
from app.core.skill_base import BaseSkill, SkillRegistry
from app.config import settings


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepCondition(Enum):
    """Step execution conditions"""
    ALWAYS = "always"
    ON_SUCCESS = "on_success"
    ON_FAILURE = "on_failure"
    ON_SKIP = "on_skip"
    CUSTOM = "custom"


@dataclass
class StepDefinition:
    """Definition of a workflow step"""
    name: str
    skill_name: str
    config: Dict[str, Any] = field(default_factory=dict)
    condition: StepCondition = StepCondition.ALWAYS
    condition_expression: Optional[str] = None  # For custom conditions
    retry_on_failure: bool = True
    max_retries: int = 3
    timeout: Optional[int] = None
    on_failure_action: Optional[str] = None  # "skip", "stop", "continue"


@dataclass
class Transition:
    """Definition of a transition between steps"""
    from_step: str
    to_step: str
    condition: Optional[str] = None


@dataclass
class WorkflowDefinition:
    """Definition of a workflow"""
    name: str
    description: str
    version: str = "1.0.0"
    steps: List[StepDefinition] = field(default_factory=list)
    transitions: List[Transition] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "steps": [
                {
                    "name": s.name,
                    "skill_name": s.skill_name,
                    "config": s.config,
                    "condition": s.condition.value,
                    "condition_expression": s.condition_expression,
                    "retry_on_failure": s.retry_on_failure,
                    "max_retries": s.max_retries,
                    "timeout": s.timeout,
                    "on_failure_action": s.on_failure_action,
                }
                for s in self.steps
            ],
            "transitions": [
                {
                    "from_step": t.from_step,
                    "to_step": t.to_step,
                    "condition": t.condition,
                }
                for t in self.transitions
            ],
            "variables": self.variables,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowDefinition":
        """Create from dictionary"""
        steps = [
            StepDefinition(
                name=s["name"],
                skill_name=s["skill_name"],
                config=s.get("config", {}),
                condition=StepCondition(s.get("condition", "always")),
                condition_expression=s.get("condition_expression"),
                retry_on_failure=s.get("retry_on_failure", True),
                max_retries=s.get("max_retries", 3),
                timeout=s.get("timeout"),
                on_failure_action=s.get("on_failure_action"),
            )
            for s in data.get("steps", [])
        ]

        transitions = [
            Transition(
                from_step=t["from_step"],
                to_step=t["to_step"],
                condition=t.get("condition"),
            )
            for t in data.get("transitions", [])
        ]

        return cls(
            name=data["name"],
            description=data["description"],
            version=data.get("version", "1.0.0"),
            steps=steps,
            transitions=transitions,
            variables=data.get("variables", {}),
            metadata=data.get("metadata", {}),
        )


class WorkflowExecution:
    """
    Represents a single workflow execution
    """
    def __init__(
        self,
        execution_id: str,
        workflow_definition: WorkflowDefinition,
        initial_state: Dict[str, Any],
    ):
        self.execution_id = execution_id
        self.workflow = workflow_definition
        self.state = initial_state.copy()
        self.context = ExecutionContext(
            workflow_id=workflow_definition.name,
            execution_id=execution_id,
            user_id=initial_state.get("user_id"),
        )
        self.context.input_data = initial_state.get("input_data", {})
        self.context.shared_state = initial_state.get("shared_state", {})

        self.status = WorkflowStatus.PENDING
        self.current_step: Optional[str] = None
        self.completed_steps: List[str] = []
        self.failed_steps: List[str] = []
        self.paused_steps: List[str] = []

        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

        self.error_message: Optional[str] = None
        self.error_stack: Optional[str] = None

        self._pause_event = asyncio.Event()
        self._cancel_event = asyncio.Event()

    def start(self):
        """Mark as started"""
        self.status = WorkflowStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self):
        """Mark as completed"""
        self.status = WorkflowStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.context.complete()

    def fail(self, error: str, stack: Optional[str] = None):
        """Mark as failed"""
        self.status = WorkflowStatus.FAILED
        self.error_message = error
        self.error_stack = stack
        self.context.set_error(error, stack)

    def pause(self):
        """Pause execution"""
        self.status = WorkflowStatus.PAUSED
        self.context.pause()

    def resume(self):
        """Resume execution"""
        self.status = WorkflowStatus.RUNNING
        self.context.resume()
        self._pause_event.set()

    def cancel(self):
        """Cancel execution"""
        self.status = WorkflowStatus.CANCELLED
        self._cancel_event.set()

    async def wait_for_resume(self):
        """Wait until execution is resumed"""
        await self._pause_event.wait()
        self._pause_event.clear()

    def is_cancelled(self) -> bool:
        """Check if cancelled"""
        return self._cancel_event.is_set()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "execution_id": self.execution_id,
            "workflow_name": self.workflow.name,
            "status": self.status.value,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "paused_steps": self.paused_steps,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "context": self.context.to_dict(),
        }


class WorkflowEngine:
    """
    Main workflow engine for executing skill pipelines
    """
    def __init__(self, checkpoint_path: Optional[str] = None):
        self.checkpoint_saver = SqliteSaver.from_conn_string(
            checkpoint_path or "file:checkpoints?mode=memory&cache=shared"
        )
        self._executions: Dict[str, WorkflowExecution] = {}
        self._callbacks: Dict[str, List[Callable]] = {}

    def register_callback(self, execution_id: str, callback: Callable):
        """Register a callback for execution updates"""
        if execution_id not in self._callbacks:
            self._callbacks[execution_id] = []
        self._callbacks[execution_id].append(callback)

    def _notify_callbacks(self, execution_id: str, execution: WorkflowExecution):
        """Notify registered callbacks of updates"""
        if execution_id in self._callbacks:
            for callback in self._callbacks[execution_id]:
                try:
                    asyncio.create_task(callback(execution))
                except Exception:
                    pass

    def validate_definition(self, workflow: WorkflowDefinition) -> List[str]:
        """
        Validate a workflow definition

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check that all referenced skills exist
        for step in workflow.steps:
            if not SkillRegistry.get(step.skill_name):
                errors.append(f"Step '{step.name}' references unknown skill '{step.skill_name}'")

        # Check that step names are unique
        step_names = [s.name for s in workflow.steps]
        if len(step_names) != len(set(step_names)):
            errors.append("Step names must be unique")

        # Validate transitions
        step_names_set = set(step_names + ["START", "END"])
        for transition in workflow.transitions:
            if transition.from_step not in step_names_set:
                errors.append(f"Transition from unknown step '{transition.from_step}'")
            if transition.to_step not in step_names_set and transition.to_step != "END":
                errors.append(f"Transition to unknown step '{transition.to_step}'")

        return errors

    async def execute(
        self,
        workflow: WorkflowDefinition,
        initial_state: Dict[str, Any],
        execution_id: str,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a workflow and yield status updates

        Args:
            workflow: The workflow definition
            initial_state: Initial state for the execution
            execution_id: Unique execution ID

        Yields:
            Dict with execution status updates
        """
        # Validate workflow
        errors = self.validate_definition(workflow)
        if errors:
            yield {
                "type": "error",
                "execution_id": execution_id,
                "errors": errors,
            }
            return

        # Create execution object
        execution = WorkflowExecution(execution_id, workflow, initial_state)
        self._executions[execution_id] = execution

        # Build execution graph
        step_map = {s.name: s for s in workflow.steps}
        transition_map: Dict[str, List[str]] = {}

        # Build transition map
        for step in workflow.steps:
            transition_map[step.name] = []
        for transition in workflow.transitions:
            if transition.from_step not in transition_map:
                transition_map[transition.from_step] = []
            transition_map[transition.from_step].append(transition.to_step)

        # Start execution
        execution.start()
        yield {
            "type": "started",
            "execution_id": execution_id,
            "status": execution.status.value,
        }
        self._notify_callbacks(execution_id, execution)

        try:
            # Execute steps in order (or following transitions)
            current_step_name = workflow.steps[0].name if workflow.steps else None

            while current_step_name:
                # Check for cancellation
                if execution.is_cancelled():
                    execution.cancel()
                    yield {
                        "type": "cancelled",
                        "execution_id": execution_id,
                        "status": execution.status.value,
                    }
                    self._notify_callbacks(execution_id, execution)
                    break

                # Get step definition
                step = step_map.get(current_step_name)
                if not step:
                    break

                execution.current_step = current_step_name

                # Check if step should execute
                should_execute = self._should_execute_step(step, execution)
                if not should_execute:
                    execution.paused_steps.append(current_step_name)
                    yield {
                        "type": "step_skipped",
                        "execution_id": execution_id,
                        "step": current_step_name,
                    }
                    current_step_name = self._get_next_step(current_step_name, transition_map, execution)
                    continue

                # Yield step started
                yield {
                    "type": "step_started",
                    "execution_id": execution_id,
                    "step": current_step_name,
                    "skill": step.skill_name,
                }
                self._notify_callbacks(execution_id, execution)

                # Create skill instance
                skill = SkillRegistry.create_instance(step.skill_name, step.config)
                if not skill:
                    yield {
                        "type": "error",
                        "execution_id": execution_id,
                        "error": f"Skill '{step.skill_name}' not found",
                    }
                    execution.fail(f"Skill '{step.skill_name}' not found")
                    break

                # Execute skill with timeout
                try:
                    timeout = step.timeout or skill.timeout
                    output = await asyncio.wait_for(skill.run(execution.context), timeout=timeout)

                    # Store output
                    execution.context.set_output(current_step_name, output)
                    execution.completed_steps.append(current_step_name)

                    yield {
                        "type": "step_completed",
                        "execution_id": execution_id,
                        "step": current_step_name,
                        "output": output,
                    }
                    self._notify_callbacks(execution_id, execution)

                    # Move to next step
                    current_step_name = self._get_next_step(current_step_name, transition_map, execution)

                except asyncio.TimeoutError:
                    execution.failed_steps.append(current_step_name)
                    yield {
                        "type": "step_timeout",
                        "execution_id": execution_id,
                        "step": current_step_name,
                    }

                    if step.on_failure_action == "stop":
                        execution.fail(f"Step '{current_step_name}' timed out")
                        break
                    elif step.on_failure_action == "skip":
                        current_step_name = self._get_next_step(current_step_name, transition_map, execution)

                except Exception as e:
                    execution.failed_steps.append(current_step_name)
                    yield {
                        "type": "step_failed",
                        "execution_id": execution_id,
                        "step": current_step_name,
                        "error": str(e),
                    }

                    if step.on_failure_action == "stop":
                        execution.fail(str(e))
                        break
                    elif step.on_failure_action == "skip":
                        current_step_name = self._get_next_step(current_step_name, transition_map, execution)

                # Check for pause
                if execution.status == WorkflowStatus.PAUSED:
                    yield {
                        "type": "paused",
                        "execution_id": execution_id,
                        "step": current_step_name,
                        "status": execution.status.value,
                    }
                    self._notify_callbacks(execution_id, execution)
                    await execution.wait_for_resume()
                    yield {
                        "type": "resumed",
                        "execution_id": execution_id,
                        "step": current_step_name,
                        "status": execution.status.value,
                    }

            # Mark as completed
            execution.complete()
            yield {
                "type": "completed",
                "execution_id": execution_id,
                "status": execution.status.value,
                "context": execution.context.to_dict(),
            }
            self._notify_callbacks(execution_id, execution)

        except Exception as e:
            execution.fail(str(e))
            yield {
                "type": "error",
                "execution_id": execution_id,
                "error": str(e),
            }
            self._notify_callbacks(execution_id, execution)

        finally:
            # Clean up
            if execution_id in self._callbacks:
                del self._callbacks[execution_id]

    def _should_execute_step(self, step: StepDefinition, execution: WorkflowExecution) -> bool:
        """Check if a step should execute based on its condition"""
        if step.condition == StepCondition.ALWAYS:
            return True
        elif step.condition == StepCondition.ON_SUCCESS:
            # Execute if previous step succeeded
            if execution.completed_steps:
                return True
            return False
        elif step.condition == StepCondition.ON_FAILURE:
            # Execute if previous step failed
            if execution.failed_steps:
                return True
            return False
        elif step.condition == StepCondition.ON_SKIP:
            # Execute if previous step was skipped
            if execution.paused_steps:
                return True
            return False
        elif step.condition == StepCondition.CUSTOM:
            # Evaluate custom expression
            if step.condition_expression:
                return self._evaluate_condition(step.condition_expression, execution.context)
            return True
        return True

    def _get_next_step(
        self,
        current_step: str,
        transition_map: Dict[str, List[str]],
        execution: WorkflowExecution,
    ) -> Optional[str]:
        """Get the next step to execute"""
        # Check transitions from current step
        transitions = transition_map.get(current_step, [])

        for transition in transitions:
            # If there's a condition, evaluate it
            if transition.condition:
                if self._evaluate_condition(transition.condition, execution.context):
                    return transition.to_step
            else:
                # No condition, take the first transition
                return transition.to_step

        # No transitions, return None (end of workflow)
        return None

    def _evaluate_condition(self, expression: str, context: ExecutionContext) -> bool:
        """
        Evaluate a condition expression

        Simple expression evaluation - supports:
        - state.key == value
        - state.key != value
        - state.key in [value1, value2]
        - state.key contains "substring"
        """
        try:
            # Extract the key and operator
            expr = expression.strip()

            # Simple parsing for common patterns
            if "==" in expr:
                key, value = expr.split("==", 1)
                key = key.strip().replace("state.", "")
                value = value.strip().strip('"\'')
                return str(context.get_state(key)) == value
            elif "!=" in expr:
                key, value = expr.split("!=", 1)
                key = key.strip().replace("state.", "")
                value = value.strip().strip('"\'')
                return str(context.get_state(key)) != value
            elif " in " in expr:
                parts = expr.split(" in ", 1)
                key = parts[0].strip().replace("state.", "")
                values = parts[1].strip()[1:-1].split(",")  # Remove brackets and split
                values = [v.strip().strip('"\'') for v in values]
                return str(context.get_state(key)) in values
            elif " contains " in expr:
                parts = expr.split(" contains ", 1)
                key = parts[0].strip().replace("state.", "")
                value = parts[1].strip().strip('"\'')
                return value in str(context.get_state(key, ""))

            return False
        except Exception:
            return False

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get an execution by ID"""
        return self._executions.get(execution_id)

    def pause_execution(self, execution_id: str):
        """Pause an execution"""
        execution = self._executions.get(execution_id)
        if execution:
            execution.pause()

    def resume_execution(self, execution_id: str):
        """Resume a paused execution"""
        execution = self._executions.get(execution_id)
        if execution:
            execution.resume()

    def cancel_execution(self, execution_id: str):
        """Cancel an execution"""
        execution = self._executions.get(execution_id)
        if execution:
            execution.cancel()

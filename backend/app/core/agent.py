"""
Agent Orchestrator - Main coordinator for the AI Agent system
"""
import asyncio
import uuid
from typing import Dict, Any, Optional, List, AsyncIterator
from datetime import datetime

from app.core.context import ExecutionContext, MessageContext
from app.core.skill_base import BaseSkill, SkillRegistry
from app.core.workflow_engine import (
    WorkflowEngine,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStatus,
)
from app.config import settings


class AgentOrchestrator:
    """
    Main Agent Orchestrator class

    Coordinates skill execution, workflow management, and message handling
    """

    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {}
        self.workflow_engine = WorkflowEngine()
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._conversations: Dict[str, MessageContext] = {}

    def register_skill(self, skill: BaseSkill):
        """
        Register a skill plugin

        Args:
            skill: The skill instance to register
        """
        self.skills[skill.name] = skill

    def register_workflow(self, workflow: WorkflowDefinition):
        """
        Register a workflow definition

        Args:
            workflow: The workflow definition to register
        """
        self._workflows[workflow.name] = workflow

    def get_workflow(self, name: str) -> Optional[WorkflowDefinition]:
        """Get a workflow by name"""
        return self._workflows.get(name)

    def list_workflows(self) -> List[WorkflowDefinition]:
        """List all registered workflows"""
        return list(self._workflows.values())

    def list_skills(self) -> List[BaseSkill]:
        """List all registered skills"""
        return list(self.skills.values())

    async def execute_workflow(
        self,
        workflow_name: str,
        input_data: Dict[str, Any],
        user_id: Optional[int] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a workflow

        Args:
            workflow_name: Name of the workflow to execute
            input_data: Input data for the workflow
            user_id: Optional user ID

        Yields:
            Dict with execution status updates
        """
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            yield {
                "type": "error",
                "error": f"Workflow '{workflow_name}' not found",
            }
            return

        execution_id = str(uuid.uuid4())
        initial_state = {
            "user_id": user_id,
            "input_data": input_data,
            "shared_state": {},
        }

        async for update in self.workflow_engine.execute(
            workflow, initial_state, execution_id
        ):
            yield update

    def pause_execution(self, execution_id: str):
        """Pause a workflow execution"""
        self.workflow_engine.pause_execution(execution_id)

    def resume_execution(self, execution_id: str):
        """Resume a paused workflow execution"""
        self.workflow_engine.resume_execution(execution_id)

    def cancel_execution(self, execution_id: str):
        """Cancel a workflow execution"""
        self.workflow_engine.cancel_execution(execution_id)

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow execution"""
        execution = self.workflow_engine.get_execution(execution_id)
        if execution:
            return execution.to_dict()
        return None

    async def handle_interrupt(
        self,
        execution_id: str,
        action: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Handle an interrupt/intervention during execution

        Args:
            execution_id: The execution ID
            action: Action to take (pause, resume, cancel, takeover, update_state)
            data: Optional data for the action

        Returns:
            Dict with result of the action
        """
        execution = self.workflow_engine.get_execution(execution_id)
        if not execution:
            return {
                "success": False,
                "error": "Execution not found",
            }

        if action == "pause":
            self.pause_execution(execution_id)
            return {"success": True, "status": "paused"}

        elif action == "resume":
            self.resume_execution(execution_id)
            return {"success": True, "status": "resumed"}

        elif action == "cancel":
            self.cancel_execution(execution_id)
            return {"success": True, "status": "cancelled"}

        elif action == "takeover":
            # Mark execution as paused for manual takeover
            execution.pause("manual_takeover")
            execution.context.set_state("manual_takeover", True)
            if data:
                execution.context.set_state("takeover_data", data)
            return {
                "success": True,
                "status": "paused",
                "context": execution.context.to_dict(),
            }

        elif action == "update_state":
            if data:
                for key, value in data.items():
                    execution.context.set_state(key, value)
            return {"success": True}

        return {
            "success": False,
            "error": f"Unknown action: {action}",
        }

    async def handle_message(
        self,
        conversation_id: str,
        customer_id: int,
        platform: str,
        incoming_message: str,
        message_history: Optional[List[Dict]] = None,
        customer_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Handle an incoming message from a customer

        Args:
            conversation_id: Conversation ID
            customer_id: Customer ID
            platform: Platform (email, whatsapp, etc.)
            incoming_message: The incoming message
            message_history: Previous message history
            customer_data: Customer data

        Returns:
            Dict with reply and intent analysis
        """
        # Create message context
        context = MessageContext(
            conversation_id=conversation_id,
            customer_id=customer_id,
            platform=platform,
            incoming_message=incoming_message,
            message_history=message_history or [],
            customer_data=customer_data or {},
        )

        # Get AI reply skill
        ai_reply_skill = self.skills.get("ai_reply")
        if not ai_reply_skill:
            return {
                "success": False,
                "error": "AI reply skill not found",
            }

        # Execute skill
        try:
            start_time = datetime.utcnow()

            # Create execution context
            exec_context = ExecutionContext(
                workflow_id="message_handler",
                execution_id=str(uuid.uuid4()),
            )
            exec_context.input_data = {
                "conversation_id": conversation_id,
                "customer_id": customer_id,
                "platform": platform,
                "message": incoming_message,
                "history": message_history or [],
                "customer": customer_data or {},
            }

            # Execute skill
            result = await ai_reply_skill.run(exec_context)

            # Update context with result
            context.detected_intent = result.get("intent")
            context.intent_confidence = result.get("intent_confidence", 0.0)
            context.intent_level = result.get("intent_level")
            context.generated_reply = result.get("reply")
            context.suggested_actions = result.get("suggested_actions", [])

            # Calculate processing time
            context.processing_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": True,
                "reply": context.generated_reply,
                "intent": context.detected_intent,
                "intent_level": context.intent_level,
                "suggested_actions": context.suggested_actions,
                "processing_time": context.processing_time,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_conversation(self, conversation_id: str) -> Optional[MessageContext]:
        """Get a conversation context"""
        return self._conversations.get(conversation_id)

    def update_conversation(self, conversation_id: str, data: Dict[str, Any]):
        """Update a conversation context"""
        if conversation_id in self._conversations:
            for key, value in data.items():
                setattr(self._conversations[conversation_id], key, value)

    def cleanup_conversation(self, conversation_id: str):
        """Remove a conversation context"""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]


# Global agent instance
_agent_instance: Optional[AgentOrchestrator] = None


def get_agent() -> AgentOrchestrator:
    """Get the global agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AgentOrchestrator()
    return _agent_instance


def reset_agent():
    """Reset the global agent instance (for testing)"""
    global _agent_instance
    _agent_instance = None

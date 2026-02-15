"""
AI Provider适配器

支持通义千问、文心一言、OpenAI等多种AI模型
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx
import json
from datetime import datetime

from app.config import settings


class AIProvider(ABC):
    """AI模型提供商抽象基类"""

    @abstractmethod
    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        Chat completion

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    async def chat_completion_with_stream(
        self,
        messages: List[Dict[str, str]],
    ):
        """
        Chat completion with streaming

        Yields:
            Chunks of the response
        """
        pass

    @abstractmethod
    async def intent_classification(self, text: str) -> Dict[str, Any]:
        """
        Classify intent of text

        Args:
            text: Input text

        Returns:
            Dict with 'intent', 'confidence', 'level'
        """
        pass


class TongyiProvider(AIProvider):
    """
    通义千问实现

    使用Dashscope API
    """
    def __init__(self):
        self.api_key = settings.TONGYI_API_KEY
        self.api_base = settings.TONGYI_API_BASE or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen-turbo"

    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """Chat completion"""
        if not self.api_key:
            raise ValueError("TONGYI_API_KEY not configured")

        url = f"{self.api_base}/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]

    async def chat_completion_with_stream(
        self,
        messages: List[Dict[str, str]],
    ):
        """Chat completion with streaming"""
        if not self.api_key:
            raise ValueError("TONGYI_API_KEY not configured")

        url = f"{self.api_base}/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": True
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue

    async def intent_classification(self, text: str) -> Dict[str, Any]:
        """Classify intent of text"""
        system_prompt = """You are an intent classifier for a B2B trading context.

Classify the following text into one of these intents:
- price_inquiry: Asking about pricing, costs, quotes
- product_inquiry: Asking about products, catalog, specifications
- sample_request: Requesting samples or trials
- moq_inquiry: Asking about minimum order quantity
- collaboration_inquiry: Discussing partnership or collaboration
- shipping_inquiry: Asking about shipping, delivery, logistics
- payment_inquiry: Asking about payment terms and methods
- lead_time_inquiry: Asking about production or delivery time
- complaint: Expressing dissatisfaction or reporting issues
- greeting: Simple greeting or introduction
- goodbye: Ending the conversation
- urgent: Urgent request or emergency
- complex_negotiation: Complex discussion requiring human intervention

Respond with JSON format:
{
    "intent": "intent_name",
    "confidence": 0.0-1.0,
    "level": "low|medium|high|very_high",
    "reasoning": "brief explanation"
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ]

        response = await self.chat_completion(messages)

        # Try to parse JSON response
        try:
            # Find JSON in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                result = json.loads(json_str)
                return {
                    "intent": result.get("intent", "general"),
                    "confidence": result.get("confidence", 0.5),
                    "level": result.get("level", "low"),
                    "reasoning": result.get("reasoning", "")
                }
        except (json.JSONDecodeError, KeyError):
            pass

        return {
            "intent": "general",
            "confidence": 0.3,
            "level": "low",
            "reasoning": "Could not parse response"
        }


class QwenProvider(AIProvider):
    """
    Qwen实现

    使用Qwen SDK或API
    """
    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        self.model = "qwen-turbo"

    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """Chat completion"""
        if not self.api_key:
            raise ValueError("QWEN_API_KEY not configured")

        # Use Qwen API
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

        payload = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "result_format": "message"
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return data["output"]["choices"][0]["message"]["content"]

    async def chat_completion_with_stream(
        self,
        messages: List[Dict[str, str]],
    ):
        """Chat completion with streaming"""
        # Implement streaming
        yield ""

    async def intent_classification(self, text: str) -> Dict[str, Any]:
        """Classify intent of text"""
        # Use same logic as Tongyi for now
        provider = TongyiProvider()
        return await provider.intent_classification(text)


class OpenAIProvider(AIProvider):
    """
    OpenAI实现

    使用OpenAI API
    """
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.api_base = settings.OPENAI_API_BASE or "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo"

    async def chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """Chat completion"""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        url = f"{self.api_base}/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]

    async def chat_completion_with_stream(
        self,
        messages: List[Dict[str, str]],
    ):
        """Chat completion with streaming"""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        url = f"{self.api_base}/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": True
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue

    async def intent_classification(self, text: str) -> Dict[str, Any]:
        """Classify intent of text"""
        provider = TongyiProvider()  # Reuse Tongyi's prompt
        provider.api_key = self.api_key
        provider.api_base = self.api_base
        provider.model = self.model
        return await provider.intent_classification(text)


# Provider registry
PROVIDERS = {
    "tongyi": TongyiProvider,
    "qwen": QwenProvider,
    "openai": OpenAIProvider,
}


# Global provider instance
_provider_instance: Optional[AIProvider] = None


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Get AI provider instance

    Args:
        provider_name: Provider name (tongyi, qwen, openai). If None, uses settings.AI_PROVIDER

    Returns:
        AIProvider instance
    """
    global _provider_instance

    provider_name = provider_name or settings.AI_PROVIDER or "tongyi"

    if _provider_instance is None or not isinstance(
        _provider_instance, PROVIDERS.get(provider_name, TongyiProvider)
    ):
        provider_class = PROVIDERS.get(provider_name, TongyiProvider)
        _provider_instance = provider_class()

    return _provider_instance


def reset_ai_provider():
    """Reset AI provider instance (for testing)"""
    global _provider_instance
    _provider_instance = None

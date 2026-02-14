"""
WhatsApp服务

使用WhatsApp Business API
"""
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime

from app.config import settings


class WhatsAppService:
    """WhatsApp Business API服务"""

    def __init__(
        self,
        phone_number_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        self.phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = access_token or settings.WHATSAPP_ACCESS_TOKEN
        self.api_base = "https://graph.facebook.com/v18.0"

    async def send_message(
        self,
        to: str,
        text: str,
        message_type: str = "text",
        preview_url: bool = False,
    ) -> Dict[str, Any]:
        """
        发送WhatsApp消息

        Args:
            to: 接收者电话号码（带国家代码，如 +1234567890）
            text: 消息文本
            message_type: 消息类型 (text, template)
            preview_url: 是否预览URL

        Returns:
            Dict包含发送结果
        """
        if not self.phone_number_id:
            raise ValueError("WHATSAPP_PHONE_NUMBER_ID not configured")
        if not self.access_token:
            raise ValueError("WHATSAPP_ACCESS_TOKEN not configured")

        url = f"{self.api_base}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": message_type,
            "text": {
                "body": text,
                "preview_url": preview_url
            }
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return {
            "success": True,
            "to": to,
            "sent_at": datetime.utcnow().isoformat(),
            "message_id": data.get("messages", [{}])[0].get("id")
        }

    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "en",
        components: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        发送WhatsApp模板消息

        Args:
            to: 接收者电话号码
            template_name: 模板名称
            language_code: 语言代码
            components: 模板组件

        Returns:
            Dict包含发送结果
        """
        url = f"{self.api_base}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }

        if components:
            payload["template"]["components"] = components

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return {
            "success": True,
            "to": to,
            "sent_at": datetime.utcnow().isoformat(),
            "message_id": data.get("messages", [{}])[0].get("id")
        }

    async def send_media_message(
        self,
        to: str,
        media_url: str,
        media_type: str = "image",
        caption: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        发送WhatsApp媒体消息

        Args:
            to: 接收者电话号码
            media_url: 媒体URL
            media_type: 媒体类型 (image, video, audio, document)
            caption: 媒体说明

        Returns:
            Dict包含发送结果
        """
        url = f"{self.api_base}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": media_type,
            media_type: {
                "link": media_url
            }
        }

        if caption:
            payload[media_type]["caption"] = caption

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return {
            "success": True,
            "to": to,
            "sent_at": datetime.utcnow().isoformat(),
            "message_id": data.get("messages", [{}])[0].get("id")
        }

    async def send_location_message(
        self,
        to: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        发送WhatsApp位置消息

        Args:
            to: 接收者电话号码
            latitude: 纬度
            longitude: 经度
            name: 位置名称
            address: 地址

        Returns:
            Dict包含发送结果
        """
        url = f"{self.api_base}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "location",
            "location": {
                "latitude": latitude,
                "longitude": longitude
            }
        }

        if name:
            payload["location"]["name"] = name
        if address:
            payload["location"]["address"] = address

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return {
            "success": True,
            "to": to,
            "sent_at": datetime.utcnow().isoformat(),
            "message_id": data.get("messages", [{}])[0].get("id")
        }

    async def send_contact_message(
        self,
        to: str,
        contacts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        发送WhatsApp联系人消息

        Args:
            to: 接收者电话号码
            contacts: 联系人列表

        Returns:
            Dict包含发送结果
        """
        url = f"{self.api_base}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "contacts",
            "contacts": contacts
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return {
            "success": True,
            "to": to,
            "sent_at": datetime.utcnow().isoformat(),
            "message_id": data.get("messages", [{}])[0].get("id")
        }

    async def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        验证Webhook

        Args:
            mode: 模式
            token: 验证token
            challenge: 挑战

        Returns:
            挑战值（如果验证成功）
        """
        verify_token = settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN

        if mode == "subscribe" and token == verify_token:
            return challenge

        return None

    async def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        获取消息详情

        Args:
            message_id: 消息ID

        Returns:
            消息详情
        """
        url = f"{self.api_base}/{message_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        标记消息为已读

        Args:
            message_id: 消息ID

        Returns:
            操作结果
        """
        url = f"{self.api_base}/{message_id}"

        payload = {
            "messaging_product": "whatsapp",
            "status": "read"
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

        return {"success": True}

    async def get_phone_number_info(self) -> Dict[str, Any]:
        """
        获取电话号码信息

        Returns:
            电话号码信息
        """
        url = f"{self.api_base}/{self.phone_number_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def verify_number(self, phone: str) -> Dict[str, Any]:
        """
        验证电话号码是否为WhatsApp用户

        Args:
            phone: 电话号码（不带+和国家代码）

        Returns:
            验证结果
        """
        url = f"{self.api_base}/{self.phone_number_id}/contacts"

        payload = {
            "blocking": "wait",
            "contacts": [f"+{phone}"],
            "force_check": True
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_business_profile(self) -> Dict[str, Any]:
        """
        获取企业资料

        Returns:
            企业资料
        """
        url = f"{self.api_base}/{self.phone_number_id}/whatsapp_business_profile"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def update_business_profile(
        self,
        about: Optional[str] = None,
        address: Optional[str] = None,
        description: Optional[str] = None,
        email: Optional[str] = None,
        profile_picture_url: Optional[str] = None,
        websites: Optional[List[str]] = None,
        vertical: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        更新企业资料

        Args:
            about: 关于
            address: 地址
            description: 描述
            email: 邮箱
            profile_picture_url: 头像URL
            websites: 网站列表
            vertical: 行业

        Returns:
            更新结果
        """
        url = f"{self.api_base}/{self.phone_number_id}/whatsapp_business_profile"

        payload = {}
        if about is not None:
            payload["about"] = about
        if address is not None:
            payload["address"] = address
        if description is not None:
            payload["description"] = description
        if email is not None:
            payload["email"] = email
        if profile_picture_url is not None:
            payload["profile_picture_url"] = profile_picture_url
        if websites is not None:
            payload["websites"] = websites
        if vertical is not None:
            payload["vertical"] = vertical

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()


def get_whatsapp_service(
    phone_number_id: Optional[str] = None,
    access_token: Optional[str] = None,
) -> WhatsAppService:
    """
    获取WhatsApp服务实例

    Args:
        phone_number_id: 电话号码ID
        access_token: 访问令牌

    Returns:
        WhatsAppService实例
    """
    return WhatsAppService(phone_number_id, access_token)

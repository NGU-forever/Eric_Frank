"""
邮件服务

支持SMTP、Gmail API、Outlook API
"""
from typing import Dict, Any, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
from datetime import datetime

from app.config import settings


class EmailService:
    """邮件服务基类"""

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        发送邮件

        Args:
            to: 收件人邮箱
            subject: 主题
            body: 正文
            html: HTML正文（可选）
            from_email: 发件人邮箱（可选）
            reply_to: 回复地址（可选）

        Returns:
            Dict包含发送结果
        """
        pass

    async def send_bulk_emails(
        self,
        recipients: List[Dict[str, str]],
        subject: str,
        body: str,
        html: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        批量发送邮件

        Args:
            recipients: 收件人列表，每个元素包含 email 和可选的 variables
            subject: 主题模板
            body: 正文模板
            html: HTML正文模板（可选）

        Returns:
            发送结果列表
        """
        pass


class SMTPEmailService(EmailService):
    """SMTP邮件服务"""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,
    ):
        self.host = host or settings.SMTP_HOST
        self.port = port or settings.SMTP_PORT
        self.username = username or settings.SMTP_USER
        self.password = password or settings.SMTP_PASSWORD
        self.use_tls = use_tls

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """发送邮件"""
        from_email = from_email or self.username

        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = from_email
        msg["To"] = to
        msg["Subject"] = subject
        if reply_to:
            msg["Reply-To"] = reply_to

        # Add plain text version
        text_part = MIMEText(body, "plain", "utf-8")
        msg.attach(text_part)

        # Add HTML version if provided
        if html:
            html_part = MIMEText(html, "html", "utf-8")
            msg.attach(html_part)

        # Send
        try:
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return {
                "success": True,
                "to": to,
                "sent_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "to": to,
                "error": str(e)
            }

    async def send_bulk_emails(
        self,
        recipients: List[Dict[str, str]],
        subject: str,
        body: str,
        html: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """批量发送邮件"""
        results = []

        for recipient in recipients:
            email = recipient.get("email")
            if not email:
                continue

            # Replace variables in subject and body
            variables = recipient.get("variables", {})
            final_subject = self._replace_variables(subject, variables)
            final_body = self._replace_variables(body, variables)
            final_html = self._replace_variables(html, variables) if html else None

            result = await self.send_email(
                to=email,
                subject=final_subject,
                body=final_body,
                html=final_html,
            )
            results.append(result)

        return results

    def _replace_variables(self, text: str, variables: Dict[str, str]) -> str:
        """替换模板中的变量"""
        if not text:
            return text

        result = text
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))

        return result


class GmailEmailService(EmailService):
    """Gmail API邮件服务"""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or settings.GMAIL_CLIENT_ID
        self.client_secret = client_secret or settings.GMAIL_CLIENT_SECRET

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """发送邮件"""
        if not access_token:
            raise ValueError("access_token is required for Gmail API")

        # Create message
        from_email = from_email or "me"

        # Build message
        message = MIMEMultipart()
        message["To"] = to
        message["Subject"] = subject
        if from_email != "me":
            message["From"] = from_email
        if reply_to:
            message["Reply-To"] = reply_to

        # Add body
        if html:
            msg_alternative = MIMEMultipart("alternative")
            msg_text = MIMEText(body, "plain", "utf-8")
            msg_html = MIMEText(html, "html", "utf-8")
            msg_alternative.attach(msg_text)
            msg_alternative.attach(msg_html)
            message.attach(msg_alternative)
        else:
            message.attach(MIMEText(body, "plain", "utf-8"))

        # Encode to base64url
        import base64
        from email import message as email_message

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send via Gmail API
        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {"raw": raw}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return {
            "success": True,
            "to": to,
            "sent_at": datetime.utcnow().isoformat(),
            "message_id": data.get("id")
        }

    async def send_bulk_emails(
        self,
        recipients: List[Dict[str, str]],
        subject: str,
        body: str,
        html: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """批量发送邮件"""
        results = []

        for recipient in recipients:
            email = recipient.get("email")
            if not email:
                continue

            variables = recipient.get("variables", {})
            final_subject = self._replace_variables(subject, variables)
            final_body = self._replace_variables(body, variables)
            final_html = self._replace_variables(html, variables) if html else None

            result = await self.send_email(
                to=email,
                subject=final_subject,
                body=final_body,
                html=final_html,
                access_token=access_token,
            )
            results.append(result)

        return results

    def _replace_variables(self, text: str, variables: Dict[str, str]) -> str:
        """替换模板中的变量"""
        if not text:
            return text

        result = text
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))

        return result


class OutlookEmailService(EmailService):
    """Outlook API邮件服务"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ):
        self.client_id = client_id or settings.OUTLOOK_CLIENT_ID
        self.client_secret = client_secret or settings.OUTLOOK_CLIENT_SECRET
        self.tenant_id = tenant_id or settings.OUTLOOK_TENANT_ID

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
        from_email: Optional[str] = None,
        reply_to: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """发送邮件"""
        if not access_token:
            raise ValueError("access_token is required for Outlook API")

        # Build message
        message_body = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if html else "Text",
                    "content": html or body
                },
                "toRecipients": [
                    {"emailAddress": {"address": to}}
                ]
            }
        }

        if from_email:
            message_body["message"]["from"] = {"emailAddress": {"address": from_email}}

        if reply_to:
            message_body["message"]["replyTo"] = [
                {"emailAddress": {"address": reply_to}}
            ]

        # Send via Microsoft Graph API
        url = f"https://graph.microsoft.com/v1.0/users/{from_email or 'me'}/sendMail"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=message_body, headers=headers)
            response.raise_for_status()

        return {
            "success": True,
            "to": to,
            "sent_at": datetime.utcnow().isoformat()
        }

    async def send_bulk_emails(
        self,
        recipients: List[Dict[str, str]],
        subject: str,
        body: str,
        html: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """批量发送邮件"""
        results = []

        for recipient in recipients:
            email = recipient.get("email")
            if not email:
                continue

            variables = recipient.get("variables", {})
            final_subject = self._replace_variables(subject, variables)
            final_body = self._replace_variables(body, variables)
            final_html = self._replace_variables(html, variables) if html else None

            result = await self.send_email(
                to=email,
                subject=final_subject,
                body=final_body,
                html=final_html,
                access_token=access_token,
            )
            results.append(result)

        return results

    def _replace_variables(self, text: str, variables: Dict[str, str]) -> str:
        """替换模板中的变量"""
        if not text:
            return text

        result = text
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))

        return result


# Service factory
def get_email_service(
    service_type: str = "smtp",
    **kwargs
) -> EmailService:
    """
    获取邮件服务实例

    Args:
        service_type: 服务类型 (smtp, gmail, outlook)
        **kwargs: 服务配置参数

    Returns:
        EmailService实例
    """
    if service_type == "smtp":
        return SMTPEmailService(**kwargs)
    elif service_type == "gmail":
        return GmailEmailService(**kwargs)
    elif service_type == "outlook":
        return OutlookEmailService(**kwargs)
    else:
        raise ValueError(f"Unknown email service type: {service_type}")

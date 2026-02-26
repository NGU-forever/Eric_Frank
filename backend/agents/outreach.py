"""
backend/agents/outreach.py
--------------------------
Agent 4: Outreach Engine
Sends approved icebreaker via email (Instantly API) and WhatsApp (Wati API).
Includes human-review gate, anti-ban random delays, and daily send cap.
"""
from __future__ import annotations

import logging
import os
import random
import time

import httpx
from pydantic import BaseModel

from backend.db.crud import SupabaseCRUD

logger = logging.getLogger(__name__)

DAILY_SEND_LIMIT = int(os.environ.get("DAILY_SEND_LIMIT", "50"))


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class OutreachInput(BaseModel):
    lead_id: str
    send_email: bool = True
    send_whatsapp: bool = True


class OutreachOutput(BaseModel):
    lead_id: str
    email_sent: bool
    whatsapp_sent: bool
    message: str


# ---------------------------------------------------------------------------
# Human-review gate
# ---------------------------------------------------------------------------

class ApprovalRequiredError(Exception):
    """Raised when a lead has not been approved for outreach."""


def _assert_approved(lead: dict) -> None:
    if lead.get("blacklisted"):
        raise ValueError(f"Lead {lead['id']} is blacklisted — outreach blocked.")
    if not lead.get("is_approved"):
        raise ApprovalRequiredError(
            f"Lead {lead['id']} ({lead.get('company_name')}) is Pending Approval. "
            "A human must approve the draft before outreach."
        )
    if lead.get("daily_send_count", 0) >= DAILY_SEND_LIMIT:
        raise RuntimeError(
            f"Daily send limit ({DAILY_SEND_LIMIT}) reached. Outreach blocked."
        )


# ---------------------------------------------------------------------------
# Instantly API — email
# ---------------------------------------------------------------------------

def _send_email_instantly(to_email: str, subject: str, body: str) -> bool:
    api_key = os.environ.get("INSTANTLY_API_KEY", "")
    campaign_id = os.environ.get("INSTANTLY_CAMPAIGN_ID", "")

    if not api_key:
        logger.warning("[Outreach] INSTANTLY_API_KEY not set — simulating email send.")
        return True  # Simulate success for demo

    try:
        resp = httpx.post(
            "https://api.instantly.ai/api/v1/lead/add",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": api_key,
                "campaign_id": campaign_id,
                "skip_if_in_workspace": True,
                "leads": [
                    {
                        "email": to_email,
                        "personalization": body,
                        "email_subject": subject,
                    }
                ],
            },
            timeout=20,
        )
        resp.raise_for_status()
        logger.info(f"[Outreach] Email queued via Instantly to {to_email}")
        return True
    except Exception as exc:
        logger.error(f"[Outreach] Instantly API error: {exc}")
        return False


# ---------------------------------------------------------------------------
# Wati API — WhatsApp
# ---------------------------------------------------------------------------

def _send_whatsapp_wati(phone: str, message: str) -> bool:
    api_key = os.environ.get("WATI_API_KEY", "")
    endpoint = os.environ.get("WATI_ENDPOINT", "")

    if not api_key or not endpoint:
        logger.warning("[Outreach] WATI_API_KEY/ENDPOINT not set — simulating WhatsApp send.")
        return True

    try:
        resp = httpx.post(
            f"{endpoint}/api/v1/sendSessionMessage/{phone}",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"messageText": message},
            timeout=20,
        )
        resp.raise_for_status()
        logger.info(f"[Outreach] WhatsApp sent via Wati to {phone}")
        return True
    except Exception as exc:
        logger.error(f"[Outreach] Wati API error: {exc}")
        return False


# ---------------------------------------------------------------------------
# Parse icebreaker_text
# ---------------------------------------------------------------------------

def _parse_icebreaker(text: str) -> tuple[str, str, str]:
    """Extract subject, email body, WhatsApp message from stored icebreaker_text."""
    subject = ""
    email_body = ""
    whatsapp = ""
    section = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("SUBJECT:"):
            subject = stripped[len("SUBJECT:"):].strip()
        elif stripped == "EMAIL:":
            section = "email"
        elif stripped == "WHATSAPP:":
            section = "whatsapp"
        elif section == "email":
            email_body += line + "\n"
        elif section == "whatsapp":
            whatsapp += line + "\n"

    return subject, email_body.strip(), whatsapp.strip()


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def run_outreach(input_data: OutreachInput) -> OutreachOutput:
    db = SupabaseCRUD()
    lead = db.get_lead_by_id(input_data.lead_id)

    if not lead:
        raise ValueError(f"Lead {input_data.lead_id} not found.")

    # Human-review gate
    _assert_approved(lead)

    icebreaker = lead.get("icebreaker_text", "")
    subject, email_body, whatsapp_msg = _parse_icebreaker(icebreaker)

    email_sent = False
    whatsapp_sent = False

    # Anti-ban: random delay between lead sends
    delay = random.randint(45, 120)
    logger.info(f"[Outreach] Waiting {delay}s before sending (anti-ban delay)...")
    time.sleep(delay)

    # Email send
    if input_data.send_email and lead.get("verified_email"):
        email_sent = _send_email_instantly(
            to_email=lead["verified_email"],
            subject=subject or "Introduction",
            body=email_body,
        )

    # WhatsApp send
    if input_data.send_whatsapp and lead.get("whatsapp_number"):
        whatsapp_sent = _send_whatsapp_wati(
            phone=lead["whatsapp_number"],
            message=whatsapp_msg,
        )

    # Update DB status
    new_status = "Emailed" if email_sent else lead.get("lead_status", "Approved")
    if whatsapp_sent:
        new_status = "WhatsApped"

    db.increment_daily_send(input_data.lead_id)
    db.update_lead_status(input_data.lead_id, new_status)

    msg = f"email_sent={email_sent}, whatsapp_sent={whatsapp_sent}, status={new_status}"
    logger.info(f"[Outreach] Lead {input_data.lead_id}: {msg}")

    return OutreachOutput(
        lead_id=input_data.lead_id,
        email_sent=email_sent,
        whatsapp_sent=whatsapp_sent,
        message=msg,
    )

"""
backend/agents/sdr.py
---------------------
Agent 5: SDR Assistant
Classifies incoming reply intent (A/B/C) using Claude,
then takes automated follow-up actions.
"""
from __future__ import annotations

import logging
import os

import anthropic
import httpx
from pydantic import BaseModel

from backend.db.crud import SupabaseCRUD

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class SDRInput(BaseModel):
    lead_id: str
    incoming_message: str


class SDROutput(BaseModel):
    lead_id: str
    intent_class: str          # "A" | "B" | "C"
    action_taken: str
    calendly_link: str | None = None


# ---------------------------------------------------------------------------
# Intent classification
# ---------------------------------------------------------------------------

A_KEYWORDS = {"quote", "price", "meeting", "sample", "interested", "call", "demo", "order"}
B_KEYWORDS = {"later", "expensive", "not now", "busy", "next month", "follow up"}
C_KEYWORDS = {"unsubscribe", "not interested", "remove", "stop", "spam", "no thanks"}

CLASSIFY_PROMPT = """\
You are a B2B sales SDR. Classify the following customer reply into one category:

A - High intent (mentions pricing, meeting, sample, or shows clear buying interest)
B - Nurture (asks to follow up later, mentions budget concerns, or is mildly interested)
C - Reject (asks to unsubscribe, shows no interest, or is hostile)

Reply message:
"{message}"

Respond with ONLY a single letter: A, B, or C.
"""


def _classify_intent(message: str) -> str:
    """
    First try keyword matching (fast + free).
    Fall back to LLM classification for ambiguous messages.
    """
    msg_lower = message.lower()

    if any(kw in msg_lower for kw in C_KEYWORDS):
        return "C"
    if any(kw in msg_lower for kw in A_KEYWORDS):
        return "A"
    if any(kw in msg_lower for kw in B_KEYWORDS):
        return "B"

    # LLM fallback
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        logger.warning("[SDR] ANTHROPIC_API_KEY not set — defaulting to B (Nurture).")
        return "B"

    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=5,
            messages=[
                {
                    "role": "user",
                    "content": CLASSIFY_PROMPT.format(message=message),
                }
            ],
        )
        result = resp.content[0].text.strip().upper()
        if result in ("A", "B", "C"):
            return result
        return "B"
    except Exception as exc:
        logger.error(f"[SDR] LLM classification failed: {exc}")
        return "B"


# ---------------------------------------------------------------------------
# Actions per intent class
# ---------------------------------------------------------------------------

def _get_calendly_link() -> str:
    base = os.environ.get("CALENDLY_LINK", "https://calendly.com/your-team/30min")
    return base


def _send_feishu_notification(lead_id: str, company_name: str) -> None:
    webhook = os.environ.get("FEISHU_WEBHOOK_URL", "")
    if not webhook:
        logger.warning("[SDR] FEISHU_WEBHOOK_URL not set — skipping notification.")
        return
    try:
        httpx.post(
            webhook,
            json={
                "msg_type": "text",
                "content": {
                    "text": (
                        f"🎯 高意向客户!\n"
                        f"公司: {company_name}\n"
                        f"Lead ID: {lead_id}\n"
                        f"状态已更新为 Meeting_Booked"
                    )
                },
            },
            timeout=10,
        )
        logger.info("[SDR] 飞书通知已发送")
    except Exception as exc:
        logger.error(f"[SDR] 飞书通知失败: {exc}")


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def run_sdr(input_data: SDRInput) -> SDROutput:
    db = SupabaseCRUD()
    lead = db.get_lead_by_id(input_data.lead_id)

    if not lead:
        raise ValueError(f"Lead {input_data.lead_id} not found.")

    msg = input_data.incoming_message
    logger.info(f"[SDR] Classifying reply from {lead.get('company_name')}: '{msg[:80]}...'")

    intent = _classify_intent(msg)
    action = ""
    calendly_link = None

    if intent == "A":
        # High intent → book meeting, notify team
        calendly_link = _get_calendly_link()
        db.update_lead_status(input_data.lead_id, "Meeting_Booked")
        _send_feishu_notification(input_data.lead_id, lead.get("company_name", "Unknown"))
        action = f"Calendly link generated: {calendly_link}. Feishu notification sent."
        logger.info(f"[SDR] 🎯 A类客户 — 会议预约链接已生成: {calendly_link}")

    elif intent == "B":
        # Nurture → tag for follow-up
        db.update_lead_status(input_data.lead_id, "Nurture")
        action = "Lead tagged as Nurture for future follow-up."
        logger.info(f"[SDR] 📌 B类客户 — 标记 Nurture")

    elif intent == "C":
        # Reject → blacklist
        db.blacklist_lead(input_data.lead_id)
        action = "Lead blacklisted — removed from outreach pipeline."
        logger.info(f"[SDR] 🚫 C类客户 — 已加入黑名单")

    return SDROutput(
        lead_id=input_data.lead_id,
        intent_class=intent,
        action_taken=action,
        calendly_link=calendly_link,
    )

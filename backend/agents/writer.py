"""
backend/agents/writer.py
------------------------
Agent 3: Copy Master
Generates personalised icebreaker emails + WhatsApp messages using Claude 3.5 Sonnet.
Saves drafts with is_approved=False and status='Drafted'.
"""
from __future__ import annotations

import logging
import os

import anthropic
from pydantic import BaseModel

from backend.db.crud import SupabaseCRUD

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class WriterInput(BaseModel):
    lead_id: str


class WriterOutput(BaseModel):
    lead_id: str
    email_subject: str
    email_body: str
    whatsapp_message: str


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

OUR_PRODUCT_BRIEF = os.environ.get(
    "OUR_PRODUCT_BRIEF",
    "We manufacture high-precision industrial valves with ISO 9001 certification, "
    "offering 30% faster lead times than industry average and dedicated aftersales support.",
)

EMAIL_PROMPT_TEMPLATE = """\
You are an expert B2B sales copywriter. Write a cold outreach email in English.

Target company: {company_name}
Decision maker: {decision_maker_name}
Company background: {company_context}
Our product/service: {product_brief}

Requirements:
- Subject line: compelling, under 8 words, no spam words
- Email body: 3 short paragraphs max
  - Para 1: personalised observation about THEIR business (use company_context)
  - Para 2: specific value proposition connecting our product to their problem
  - Para 3: single clear CTA (e.g., "Would a 15-minute call this week work?")
- Tone: professional but human, never pushy
- Do NOT use generic openers like "I hope this email finds you well"

Respond in this EXACT format:
SUBJECT: <subject line here>
BODY:
<email body here>
WHATSAPP:
<whatsapp message, max 3 sentences, casual but professional>
"""


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def run_writer(input_data: WriterInput) -> WriterOutput:
    """
    Reads lead from DB, generates personalised copy, saves draft.
    """
    db = SupabaseCRUD()
    lead = db.get_lead_by_id(input_data.lead_id)

    if not lead:
        raise ValueError(f"[Writer] Lead {input_data.lead_id} not found in DB.")

    logger.info(f"[Writer] Generating copy for: {lead['company_name']}")

    prompt = EMAIL_PROMPT_TEMPLATE.format(
        company_name=lead.get("company_name", "the company"),
        decision_maker_name=lead.get("decision_maker_name") or "there",
        company_context=lead.get("company_context") or "No specific context available.",
        product_brief=OUR_PRODUCT_BRIEF,
    )

    # Claude 3.5 Sonnet call
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text
    else:
        logger.warning("[Writer] ANTHROPIC_API_KEY not set — using mock copy.")
        raw = (
            f"SUBJECT: Quick question about {lead.get('company_name', 'your business')}\n"
            "BODY:\nI noticed your company has been expanding its distribution network.\n\n"
            "Our precision valves can reduce your procurement lead time by 30%.\n\n"
            "Would a 15-minute call this week work for you?\n"
            "WHATSAPP:\nHi! Saw your company online — we make industrial valves with 30% faster "
            "delivery. Worth a quick chat?"
        )

    # Parse response
    subject, body, whatsapp = _parse_llm_response(raw)

    # Persist to DB
    icebreaker_text = f"SUBJECT: {subject}\n\nEMAIL:\n{body}\n\nWHATSAPP:\n{whatsapp}"
    db.update_lead(
        input_data.lead_id,
        {
            "icebreaker_text": icebreaker_text,
            "is_approved": False,
            "lead_status": "Drafted",
        },
    )

    logger.info(
        f"[Writer] ✅ 文案已生成，等待人工审核 — Lead: {lead['company_name']} ({input_data.lead_id})"
    )

    return WriterOutput(
        lead_id=input_data.lead_id,
        email_subject=subject,
        email_body=body,
        whatsapp_message=whatsapp,
    )


def _parse_llm_response(raw: str) -> tuple[str, str, str]:
    """Parse the structured LLM output into (subject, email_body, whatsapp)."""
    subject = ""
    body = ""
    whatsapp = ""

    lines = raw.strip().splitlines()
    section = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("SUBJECT:"):
            subject = stripped[len("SUBJECT:"):].strip()
        elif stripped == "BODY:":
            section = "body"
        elif stripped == "WHATSAPP:":
            section = "whatsapp"
        elif section == "body":
            body += line + "\n"
        elif section == "whatsapp":
            whatsapp += line + "\n"

    return subject.strip(), body.strip(), whatsapp.strip()

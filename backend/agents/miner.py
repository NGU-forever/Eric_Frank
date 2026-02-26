"""
backend/agents/miner.py
-----------------------
Agent 2: Deep Miner
Scrapes company websites, queries Apollo for decision-maker contacts,
and enriches the DB record.
"""
from __future__ import annotations

import logging
import os
import re

import httpx
from pydantic import BaseModel

from backend.db.crud import SupabaseCRUD

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class MinerInput(BaseModel):
    lead_id: str
    website_url: str


class MinerOutput(BaseModel):
    lead_id: str
    company_context: str
    decision_maker_name: str | None
    verified_email: str | None


# ---------------------------------------------------------------------------
# Website scraping (Firecrawl / httpx fallback)
# ---------------------------------------------------------------------------

def _scrape_website(url: str) -> str:
    """
    Attempt Firecrawl API first; fall back to raw httpx GET + regex extraction.
    Returns the plain-text summary of the homepage.
    """
    firecrawl_key = os.environ.get("FIRECRAWL_API_KEY", "")

    if firecrawl_key:
        try:
            resp = httpx.post(
                "https://api.firecrawl.dev/v0/scrape",
                headers={"Authorization": f"Bearer {firecrawl_key}"},
                json={"url": url, "pageOptions": {"onlyMainContent": True}},
                timeout=20,
            )
            resp.raise_for_status()
            return resp.json().get("data", {}).get("content", "")[:3000]
        except Exception as exc:
            logger.warning(f"[Miner] Firecrawl failed for {url}: {exc}. Using httpx fallback.")

    # httpx fallback
    try:
        resp = httpx.get(url, timeout=15, follow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0 (compatible; B2BBot/1.0)"})
        resp.raise_for_status()
        # Naively strip HTML tags
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:3000]
    except Exception as exc:
        logger.error(f"[Miner] Could not scrape {url}: {exc}")
        return f"[Scraping failed for {url}]"


# ---------------------------------------------------------------------------
# Apollo API — decision-maker lookup
# ---------------------------------------------------------------------------

def _query_apollo(domain: str) -> tuple[str | None, str | None]:
    """
    Returns (decision_maker_name, email) or (None, None).
    Queries Apollo.io People Search filtered to CEO / Procurement Director.
    """
    api_key = os.environ.get("APOLLO_API_KEY", "")
    if not api_key:
        logger.warning("[Miner] APOLLO_API_KEY not set — skipping contact enrichment.")
        return None, None

    try:
        resp = httpx.post(
            "https://api.apollo.io/v1/mixed_people/search",
            headers={"Content-Type": "application/json", "Cache-Control": "no-cache"},
            json={
                "api_key": api_key,
                "q_organization_domains": domain,
                "person_titles": ["CEO", "Procurement Director", "Purchasing Manager", "Owner"],
                "page": 1,
                "per_page": 1,
            },
            timeout=20,
        )
        resp.raise_for_status()
        people = resp.json().get("people", [])
        if not people:
            return None, None

        person = people[0]
        name = person.get("name")
        email = person.get("email")
        return name, email
    except Exception as exc:
        logger.error(f"[Miner] Apollo API error for {domain}: {exc}")
        return None, None


# ---------------------------------------------------------------------------
# Email validation (basic)
# ---------------------------------------------------------------------------

def _is_valid_email(email: str | None) -> bool:
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def run_miner(input_data: MinerInput) -> MinerOutput:
    """
    Enriches a lead with company context and decision-maker contact info.
    """
    logger.info(f"[Miner] Processing lead {input_data.lead_id}: {input_data.website_url}")

    # 1. Scrape website
    raw_text = _scrape_website(input_data.website_url)
    # Take first meaningful 500 chars as context summary
    company_context = raw_text[:500].strip() or "No content extracted."

    # 2. Extract domain for Apollo query
    domain_match = re.search(r"https?://(?:www\.)?([^/]+)", input_data.website_url)
    domain = domain_match.group(1) if domain_match else input_data.website_url

    # 3. Decision-maker lookup
    name, email = _query_apollo(domain)
    verified_email = email if _is_valid_email(email) else None

    # 4. Update DB
    db = SupabaseCRUD()
    updates: dict = {
        "company_context": company_context,
        "lead_status": "Mined",
    }
    if name:
        updates["decision_maker_name"] = name
    if verified_email:
        updates["verified_email"] = verified_email

    db.update_lead(input_data.lead_id, updates)
    logger.info(f"[Miner] Lead {input_data.lead_id} enriched. Contact: {name} <{verified_email}>")

    return MinerOutput(
        lead_id=input_data.lead_id,
        company_context=company_context,
        decision_maker_name=name,
        verified_email=verified_email,
    )

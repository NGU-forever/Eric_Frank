"""
backend/agents/scout.py
-----------------------
Agent 1: Market Scout
Searches the web (via ddgs, free) for B2B distributors,
filters out marketplace noise, and writes clean leads to the DB.
"""
from __future__ import annotations

import logging
from typing import Any

from ddgs import DDGS
from pydantic import BaseModel, field_validator

from backend.db.crud import SupabaseCRUD

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ScoutInput(BaseModel):
    product_keyword: str
    competitor_domain: str | None = None
    max_results: int = 10


class LeadItem(BaseModel):
    company_name: str
    website_url: str

    @field_validator("website_url")
    @classmethod
    def normalise_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v


class ScoutOutput(BaseModel):
    leads: list[LeadItem]
    skipped: int = 0


# ---------------------------------------------------------------------------
# Blocklist
# ---------------------------------------------------------------------------

BLOCKED_DOMAINS = {
    "alibaba.com",
    "made-in-china.com",
    "yellowpages.com",
    "thomasnet.com",
    "indiamart.com",
    "dhgate.com",
    "globalspec.com",
    "kompass.com",
}


def _is_blocked(url: str) -> bool:
    for blocked in BLOCKED_DOMAINS:
        if blocked in url:
            return True
    return False


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def _build_search_query(keyword: str, competitor_domain: str | None) -> str:
    base = (
        f'Find B2B distributors for "{keyword}", '
        'exclude Alibaba, Made-in-China platforms, site:distributor OR site:wholesaler'
    )
    if competitor_domain:
        base += f' -site:{competitor_domain}'
    return base


def _call_ddgs(query: str, num_results: int = 10) -> list[dict[str, Any]]:
    """Use ddgs (free DuckDuckGo metasearch) — no API key required."""
    try:
        raw = DDGS().text(query, max_results=num_results, backend="duckduckgo")
    except Exception as exc:
        logger.warning(f"[Scout] ddgs search failed: {exc} — returning mock results.")
        return [
            {"title": "Demo Distributor Co.", "link": "https://demo-distributor.com"},
            {"title": "Global Parts Inc.", "link": "https://globalpartsinc.com"},
        ]

    # ddgs returns {"title", "href", "body"}; normalise to {"title", "link"} for downstream
    return [
        {"title": r.get("title", ""), "link": r.get("href", "")}
        for r in raw
        if r.get("href")
    ]


def run_scout(input_data: ScoutInput) -> ScoutOutput:
    """
    Main Scout entry point.
    Returns cleaned leads and persists them to the database.
    """
    logger.info(f"[Scout] Searching for: {input_data.product_keyword}")

    query = _build_search_query(input_data.product_keyword, input_data.competitor_domain)
    raw_results = _call_ddgs(query, input_data.max_results)

    leads: list[LeadItem] = []
    skipped = 0
    db = SupabaseCRUD()

    for item in raw_results:
        url: str = item.get("link", "")
        title: str = item.get("title", "Unknown")

        if not url or _is_blocked(url):
            skipped += 1
            logger.debug(f"[Scout] Skipped (blocked domain): {url}")
            continue

        lead = LeadItem(company_name=title, website_url=url)
        leads.append(lead)

        try:
            db.upsert_lead(
                {
                    "company_name": lead.company_name,
                    "website_url": lead.website_url,
                    "lead_status": "Scouted",
                }
            )
            logger.info(f"[Scout] Saved lead: {lead.company_name} ({lead.website_url})")
        except Exception as exc:
            logger.error(f"[Scout] DB upsert failed for {url}: {exc}")
            skipped += 1

    logger.info(f"[Scout] Done. Saved {len(leads)} leads, skipped {skipped}.")
    return ScoutOutput(leads=leads, skipped=skipped)

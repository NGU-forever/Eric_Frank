"""
backend/workflows/main_graph.py
--------------------------------
LangGraph StateGraph orchestrating the full B2B outreach pipeline:

  Scout → Miner → Writer → HumanReview → Outreach → SDR

HumanReview is a blocking interrupt: the graph pauses and waits for
an external /approve_draft API call before proceeding.
"""
from __future__ import annotations

import logging
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.agents.scout import run_scout, ScoutInput
from backend.agents.miner import run_miner, MinerInput
from backend.agents.writer import run_writer, WriterInput
from backend.agents.outreach import run_outreach, OutreachInput, ApprovalRequiredError
from backend.agents.sdr import run_sdr, SDRInput

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Graph State
# ---------------------------------------------------------------------------

class B2BState(TypedDict):
    # Inputs
    product_keyword: str
    competitor_domain: str | None

    # Populated by Scout
    lead_ids: list[str]           # UUIDs of saved leads

    # Current working lead (one at a time for simplicity)
    current_lead_id: str | None

    # Flow control
    is_approved: bool             # set externally via /approve_draft
    incoming_reply: str | None    # set externally for SDR processing

    # Output / status log
    log: list[str]


# ---------------------------------------------------------------------------
# Node implementations
# ---------------------------------------------------------------------------

def scout_node(state: B2BState) -> B2BState:
    logger.info("[Graph] Node: Scout")
    result = run_scout(
        ScoutInput(
            product_keyword=state["product_keyword"],
            competitor_domain=state.get("competitor_domain"),
        )
    )
    lead_ids = [lead.website_url for lead in result.leads]  # placeholder — real IDs from DB
    # Retrieve actual IDs from DB (crude: just use first lead for demo)
    from backend.db.crud import SupabaseCRUD
    db = SupabaseCRUD()
    real_ids = []
    for lead in result.leads:
        row = db.get_lead_by_url(lead.website_url)
        if row:
            real_ids.append(row["id"])

    log = state.get("log", [])
    log.append(f"Scout: found {len(real_ids)} leads")
    return {
        **state,
        "lead_ids": real_ids,
        "current_lead_id": real_ids[0] if real_ids else None,
        "log": log,
    }


def miner_node(state: B2BState) -> B2BState:
    logger.info("[Graph] Node: Miner")
    lead_id = state.get("current_lead_id")
    if not lead_id:
        return {**state, "log": state.get("log", []) + ["Miner: no lead to process"]}

    from backend.db.crud import SupabaseCRUD
    db = SupabaseCRUD()
    lead = db.get_lead_by_id(lead_id)

    run_miner(MinerInput(lead_id=lead_id, website_url=lead["website_url"]))
    log = state.get("log", [])
    log.append(f"Miner: enriched lead {lead_id}")
    return {**state, "log": log}


def writer_node(state: B2BState) -> B2BState:
    logger.info("[Graph] Node: Writer")
    lead_id = state.get("current_lead_id")
    if not lead_id:
        return {**state, "log": state.get("log", []) + ["Writer: no lead to process"]}

    run_writer(WriterInput(lead_id=lead_id))
    log = state.get("log", [])
    log.append(f"Writer: draft created for {lead_id}, awaiting approval")
    return {**state, "log": log, "is_approved": False}


def human_review_node(state: B2BState) -> B2BState:
    """
    Blocking node — the graph stops here until is_approved is set to True
    by an external API call (/approve_draft). LangGraph's interrupt mechanism
    handles the persistence via MemorySaver checkpointing.
    """
    logger.info("[Graph] Node: HumanReview — WAITING for approval...")
    log = state.get("log", [])
    log.append("HumanReview: paused — waiting for human approval")
    return {**state, "log": log}


def outreach_node(state: B2BState) -> B2BState:
    logger.info("[Graph] Node: Outreach")
    lead_id = state.get("current_lead_id")
    if not lead_id:
        return state

    try:
        run_outreach(OutreachInput(lead_id=lead_id))
        log = state.get("log", []) + [f"Outreach: sent to lead {lead_id}"]
    except ApprovalRequiredError as e:
        log = state.get("log", []) + [f"Outreach: blocked — {e}"]
    return {**state, "log": log}


def sdr_node(state: B2BState) -> B2BState:
    logger.info("[Graph] Node: SDR")
    lead_id = state.get("current_lead_id")
    incoming = state.get("incoming_reply", "")
    if not lead_id or not incoming:
        return {**state, "log": state.get("log", []) + ["SDR: no reply to process"]}

    result = run_sdr(SDRInput(lead_id=lead_id, incoming_message=incoming))
    log = state.get("log", [])
    log.append(f"SDR: classified as {result.intent_class} — {result.action_taken}")
    return {**state, "log": log}


# ---------------------------------------------------------------------------
# Conditional edge: HumanReview → Outreach or block
# ---------------------------------------------------------------------------

def route_after_review(state: B2BState) -> str:
    if state.get("is_approved"):
        logger.info("[Graph] Review approved → Outreach")
        return "Outreach"
    else:
        logger.info("[Graph] Review not yet approved → waiting")
        return "HumanReview"   # Loop back / pause


# ---------------------------------------------------------------------------
# Build graph
# ---------------------------------------------------------------------------

def build_graph() -> tuple[object, MemorySaver]:
    """Compile the B2B LangGraph and return (compiled_graph, checkpointer)."""
    checkpointer = MemorySaver()

    builder = StateGraph(B2BState)

    # Add nodes
    builder.add_node("Scout", scout_node)
    builder.add_node("Miner", miner_node)
    builder.add_node("Writer", writer_node)
    builder.add_node("HumanReview", human_review_node)
    builder.add_node("Outreach", outreach_node)
    builder.add_node("SDR", sdr_node)

    # Linear edges
    builder.add_edge(START, "Scout")
    builder.add_edge("Scout", "Miner")
    builder.add_edge("Miner", "Writer")
    builder.add_edge("Writer", "HumanReview")

    # Conditional edge after HumanReview
    builder.add_conditional_edges(
        "HumanReview",
        route_after_review,
        {"Outreach": "Outreach", "HumanReview": "HumanReview"},
    )

    builder.add_edge("Outreach", "SDR")
    builder.add_edge("SDR", END)

    compiled = builder.compile(checkpointer=checkpointer)
    logger.info("[Graph] LangGraph compiled successfully.")
    return compiled, checkpointer


# Module-level singletons (shared with FastAPI app)
graph, memory = build_graph()

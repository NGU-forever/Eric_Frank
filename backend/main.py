"""
backend/main.py
---------------
FastAPI application entry point.

Exposed endpoints:
  POST  /run_workflow   — trigger B2B pipeline for a product keyword
  POST  /approve_draft  — human approves a lead draft, resumes graph
  POST  /sdr_reply      — feed a customer reply into the SDR agent
  GET   /leads          — list all leads with optional filters
  GET   /health         — container health check

Startup: auto-creates DB tables via init_db() — safe to call multiple times.
Host binding: 0.0.0.0 (required for Docker container external access).
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from pydantic import BaseModel

from backend.db.crud import SupabaseCRUD, init_db
from backend.workflows.main_graph import graph

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="B2B AI Outreach API",
    description="AI-powered B2B lead generation and personalised outreach pipeline.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Startup: initialise DB schema
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event() -> None:
    logger.info("[Startup] Initialising database schema...")
    try:
        init_db()
    except Exception as exc:
        logger.error(f"[Startup] DB init failed: {exc}. Will retry on first request.")


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class RunWorkflowRequest(BaseModel):
    product_keyword: str
    competitor_domain: Optional[str] = None


class RunWorkflowResponse(BaseModel):
    thread_id: str
    message: str
    leads_found: int = 0


class ApproveDraftRequest(BaseModel):
    lead_id: str
    thread_id: str


class SDRReplyRequest(BaseModel):
    lead_id: str
    thread_id: str
    incoming_message: str


# ---------------------------------------------------------------------------
# Background task: run the full LangGraph pipeline
# ---------------------------------------------------------------------------

def _run_pipeline(thread_id: str, keyword: str, competitor_domain: Optional[str]) -> None:
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "product_keyword": keyword,
        "competitor_domain": competitor_domain,
        "lead_ids": [],
        "current_lead_id": None,
        "is_approved": False,
        "incoming_reply": None,
        "log": [],
    }
    try:
        logger.info(f"[Pipeline] Starting thread {thread_id} for keyword: {keyword}")
        for step in graph.stream(initial_state, config=config):
            node_name = list(step.keys())[0]
            logger.info(f"[Pipeline] Completed node: {node_name}")
            # Stop streaming at HumanReview (interrupt point)
            if node_name == "HumanReview":
                logger.info(f"[Pipeline] Thread {thread_id} paused at HumanReview.")
                return
        logger.info(f"[Pipeline] Thread {thread_id} completed.")
    except Exception as exc:
        logger.error(f"[Pipeline] Thread {thread_id} failed: {exc}")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "B2B AI Outreach API"}


@app.post("/run_workflow", response_model=RunWorkflowResponse)
async def run_workflow(
    request: RunWorkflowRequest,
    background_tasks: BackgroundTasks,
) -> RunWorkflowResponse:
    """
    Trigger the B2B outreach pipeline.
    Returns immediately with a thread_id.
    The pipeline runs in the background and pauses at HumanReview.
    """
    thread_id = str(uuid.uuid4())
    background_tasks.add_task(
        _run_pipeline,
        thread_id,
        request.product_keyword,
        request.competitor_domain,
    )
    logger.info(f"[API] Workflow started — thread_id={thread_id}, keyword={request.product_keyword}")
    return RunWorkflowResponse(
        thread_id=thread_id,
        message=(
            f"Pipeline started for '{request.product_keyword}'. "
            f"Use thread_id={thread_id} to track progress. "
            "The workflow will pause at HumanReview — call /approve_draft when ready."
        ),
    )


@app.post("/approve_draft")
async def approve_draft(
    request: ApproveDraftRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    """
    Human approves a lead draft and resumes the LangGraph from HumanReview.
    """
    db = SupabaseCRUD()
    lead = db.get_lead_by_id(request.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {request.lead_id} not found.")

    # Mark approved in DB
    db.approve_lead(request.lead_id)
    logger.info(f"[API] Lead {request.lead_id} approved by human.")

    # Resume graph from checkpoint
    config = {"configurable": {"thread_id": request.thread_id}}

    def _resume():
        try:
            for step in graph.stream(
                {"is_approved": True, "current_lead_id": request.lead_id},
                config=config,
            ):
                node_name = list(step.keys())[0]
                logger.info(f"[Pipeline] Resumed node: {node_name}")
        except Exception as exc:
            logger.error(f"[Pipeline] Resume failed: {exc}")

    background_tasks.add_task(_resume)

    return {
        "message": f"Lead {request.lead_id} approved. Outreach pipeline resumed.",
        "thread_id": request.thread_id,
    }


@app.post("/sdr_reply")
async def sdr_reply(request: SDRReplyRequest) -> dict:
    """
    Feed a customer reply into the SDR agent for intent classification.
    """
    from backend.agents.sdr import run_sdr, SDRInput

    result = run_sdr(
        SDRInput(
            lead_id=request.lead_id,
            incoming_message=request.incoming_message,
        )
    )
    return {
        "lead_id": result.lead_id,
        "intent_class": result.intent_class,
        "action_taken": result.action_taken,
        "calendly_link": result.calendly_link,
    }


@app.get("/leads")
async def list_leads(
    status: Optional[str] = Query(None, description="Filter by lead_status"),
    is_approved: Optional[bool] = Query(None, description="Filter by approval flag"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict:
    """List leads from DB with optional filters."""
    db = SupabaseCRUD()
    leads = db.list_leads(
        status=status,
        is_approved=is_approved,
        limit=limit,
        offset=offset,
    )
    return {"total": len(leads), "leads": leads}


@app.get("/leads/{lead_id}")
async def get_lead(lead_id: str) -> dict:
    """Get a single lead by UUID."""
    db = SupabaseCRUD()
    lead = db.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail=f"Lead {lead_id} not found.")
    return lead


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    # host="0.0.0.0" is CRITICAL for Docker container external access
    uvicorn.run(app, host="0.0.0.0", port=8000)

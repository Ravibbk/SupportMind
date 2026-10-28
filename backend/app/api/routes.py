"""REST API Route Handlers for SupportMind Copilot."""

import csv
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from app.agents.action_agent import ActionAgent
from app.agents.router import _SESSION_MEMORY, RouterAgent
from app.api.schemas import (
    ActionDecisionRequest,
    ChatRequest,
    ChatResponse,
    ClassifyRequest,
    ClassifyResponse,
    OrderSchema,
    TicketSchema,
)
from app.core.tracing import tracer
from app.db.models import get_db_connection
from app.ml.classifier import predict

router = APIRouter(prefix="/api")

# Singleton agent orchestrator instances
_router_agent = RouterAgent()
_action_agent = ActionAgent()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EVAL_SUMMARY_CSV = BASE_DIR.parent / "eval" / "results" / "benchmark_summary.csv"


# ==============================================================================
# 1. Chat & Conversational History
# ==============================================================================

@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """Send customer inquiry to SupportMind Copilot.

    Executes security guardrails (PII redaction, prompt injection defense),
    intent routing (Knowledge, Data, or Action Agent), RAG retrieval with citations,
    and hallucination auditing by the Critic Agent.
    """
    session_id = request.session_id or f"sess_{uuid.uuid4().hex[:10]}"
    try:
        resp = _router_agent.process_message(
            session_id=session_id,
            user_message=request.message,
            prompt_version=request.prompt_version or "v3"
        )
        return ChatResponse(
            session_id=resp.session_id,
            answer=resp.answer,
            agent_chosen=resp.agent_chosen,
            category=resp.category,
            urgency=resp.urgency,
            classification_confidence=resp.classification_confidence,
            citations=[{"source": c.source, "section": c.section, "snippet": c.snippet} for c in resp.citations],
            pending_action=resp.pending_action,
            retrieved_chunks=resp.retrieved_chunks,
            critic_verdict=resp.critic_verdict,
            pii_types_detected=resp.pii_types_detected,
            trace_id=resp.trace_id,
            latency_ms=resp.latency_ms,
            estimated_cost_usd=resp.estimated_cost_usd
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing chat turn: {str(e)}"
        )


@router.get("/chat/{session_id}", tags=["Chat"])
async def get_session_history(session_id: str) -> dict[str, Any]:
    """Retrieve turn history and conversation memory for a session."""
    history = _SESSION_MEMORY.get(session_id, [])
    return {
        "session_id": session_id,
        "turns_count": len(history) // 2,
        "history": history
    }


# ==============================================================================
# 2. Human-in-the-Loop Action Approval
# ==============================================================================

@router.get("/actions/pending", tags=["Actions"])
async def list_pending_actions() -> list[dict[str, Any]]:
    """List all actions awaiting human supervisor approval (refunds, high-priority tickets)."""
    return _action_agent.get_pending_actions()


@router.post("/actions/{action_id}/approve", tags=["Actions"])
async def approve_action(action_id: str) -> dict[str, Any]:
    """Approve a pending action to disburse refund or escalate high-urgency ticket."""
    result = _action_agent.approve_action(action_id)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
    return result


@router.post("/actions/{action_id}/reject", tags=["Actions"])
async def reject_action(action_id: str, request: ActionDecisionRequest | None = None) -> dict[str, Any]:
    """Reject a pending action with an optional supervisor reason."""
    reason = request.reason if request else None
    result = _action_agent.reject_action(action_id, reason=reason)
    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
    return result


# ==============================================================================
# 3. Orders & Tracking
# ==============================================================================

@router.get("/orders/{order_id}", response_model=OrderSchema, tags=["Orders"])
async def get_order_by_id(order_id: str) -> OrderSchema:
    """Fetch order details by Order ID (e.g. ORD-10025)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT order_id, customer_name, email, product_title, price_usd,
               status, order_date, expected_delivery, carrier
        FROM orders
        WHERE UPPER(order_id) = ?
    """, (order_id.strip().upper(),))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_id} not found."
        )
    return OrderSchema(**dict(row))


@router.get("/orders", response_model=list[OrderSchema], tags=["Orders"])
async def list_orders(
    q: str | None = Query(None, description="Search by customer name, product, or order ID"),
    order_status: str | None = Query(None, description="Filter by status: Delivered, In Transit, Delayed, Cancelled"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> list[OrderSchema]:
    """List and search fulfillment orders with pagination."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query_sql = "SELECT * FROM orders WHERE 1=1"
    params = []

    if q:
        query_sql += " AND (order_id LIKE ? OR customer_name LIKE ? OR product_title LIKE ?)"
        wildcard = f"%{q.strip()}%"
        params.extend([wildcard, wildcard, wildcard])

    if order_status:
        query_sql += " AND LOWER(status) = ?"
        params.append(order_status.strip().lower())

    query_sql += " ORDER BY order_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query_sql, params)
    rows = cursor.fetchall()
    conn.close()

    return [OrderSchema(**dict(r)) for r in rows]


# ==============================================================================
# 4. Support Tickets
# ==============================================================================

@router.get("/tickets", response_model=list[TicketSchema], tags=["Tickets"])
async def list_tickets(
    category: str | None = Query(None, description="Filter by category"),
    ticket_status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100)
) -> list[TicketSchema]:
    """List customer support tickets."""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if category:
        sql += " AND LOWER(category) = ?"
        params.append(category.strip().lower())

    if ticket_status:
        sql += " AND LOWER(status) = ?"
        params.append(ticket_status.strip().lower())

    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    return [TicketSchema(**dict(r)) for r in rows]


# ==============================================================================
# 5. Machine Learning Classifier
# ==============================================================================

@router.post("/classify", response_model=ClassifyResponse, tags=["ML"])
async def classify_ticket(request: ClassifyRequest) -> ClassifyResponse:
    """Predict customer inquiry category, urgency tier, and confidence score."""
    result = predict(request.text)
    return ClassifyResponse(
        category=result.category,
        urgency=result.urgency,
        confidence=result.confidence,
        probabilities=result.probabilities
    )


# ==============================================================================
# 6. Evaluation Lab & Observability Traces
# ==============================================================================

@router.get("/eval/results", tags=["Evaluation"])
async def get_eval_results() -> list[dict[str, Any]]:
    """Retrieve measured benchmark results from the Evaluation Lab."""
    # Check primary or fallback paths
    candidates = [
        EVAL_SUMMARY_CSV,
        BASE_DIR / "eval" / "results" / "benchmark_summary.csv",
        Path("eval/results/benchmark_summary.csv")
    ]
    target_csv = None
    for c in candidates:
        if c.exists():
            target_csv = c
            break

    if not target_csv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation benchmark results not found. Run eval/run_eval.py first."
        )

    records = []
    with open(target_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


@router.get("/traces", tags=["Observability"])
async def get_traces(
    session_id: str | None = Query(None, description="Filter traces by session UUID"),
    limit: int = Query(50, ge=1, le=200)
) -> list[dict[str, Any]]:
    """Fetch chronological execution telemetry traces (agent pathway, tools, latency, cost)."""
    if session_id:
        return tracer.get_session_traces(session_id, limit=limit)
    return tracer.get_recent_traces(limit=limit)

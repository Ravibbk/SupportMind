"""Pydantic validation schemas for SupportMind REST API."""

from typing import Any

from pydantic import BaseModel, Field


# --- Chat Schemas ---
class ChatRequest(BaseModel):
    """Inbound customer or agent chat request."""

    message: str = Field(..., min_length=1, description="Customer message text", json_schema_extra={"example": "What is the return window for clothing?"})
    session_id: str | None = Field(None, description="Client session UUID", json_schema_extra={"example": "sess_12345"})
    prompt_version: str | None = Field("v3", description="Prompt version: v1, v2, or v3", json_schema_extra={"example": "v3"})


class CitationSchema(BaseModel):
    """Citation identifying verified document source, section, and snippet."""

    source: str
    section: str
    snippet: str


class ChatResponse(BaseModel):
    """Outbound structured copilot answer with citations, traces, and pending actions."""

    session_id: str
    answer: str
    agent_chosen: str
    category: str
    urgency: str
    classification_confidence: float
    citations: list[CitationSchema] = Field(default_factory=list)
    pending_action: dict[str, Any] | None = None
    retrieved_chunks: list[dict[str, Any]] = Field(default_factory=list)
    critic_verdict: dict[str, Any] | None = None
    pii_types_detected: list[str] = Field(default_factory=list)
    trace_id: str
    latency_ms: float
    estimated_cost_usd: float


# --- Action Schemas ---
class ActionDecisionRequest(BaseModel):
    """Supervisor decision payload to approve or reject a pending action."""

    reason: str | None = Field(None, description="Optional supervisor note or rejection reason")


# --- Classification Schemas ---
class ClassifyRequest(BaseModel):
    """Inquiry text payload for ticket classifier."""

    text: str = Field(..., min_length=1, description="Customer message text to categorize", json_schema_extra={"example": "Why was my visa card billed twice?"})


class ClassifyResponse(BaseModel):
    """Predicted category, urgency level, and model confidence."""

    category: str
    urgency: str
    confidence: float
    probabilities: dict[str, float] = Field(default_factory=dict)


# --- Order & Ticket Schemas ---
class OrderSchema(BaseModel):
    """Fulfillment order data structure."""

    order_id: str
    customer_name: str
    email: str
    product_title: str
    price_usd: float
    status: str
    order_date: str
    expected_delivery: str
    carrier: str


class TicketSchema(BaseModel):
    """Customer support ticket record."""

    ticket_id: str
    session_id: str
    customer_email: str | None = None
    category: str
    urgency: str
    status: str
    subject: str
    description: str
    created_at: str

"""Master Agent Router and Orchestrator for SupportMind.

Integrates:
1. PII Masking and Prompt Injection Security Guardrails
2. Machine Learning Intent Classification
3. Multi-Agent Routing: Knowledge Agent, Data Agent, Action Agent
4. Critic Agent Faithfulness Audit
5. Short-term Session Memory (last 5 turns)
6. Tracing and Telemetry Recording to SQLite
"""

import re
import time
from dataclasses import asdict
from typing import Any

from pydantic import BaseModel, Field

from app.agents.action_agent import ActionAgent
from app.agents.critic_agent import CriticAgent, CriticVerdict
from app.agents.data_agent import DataAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.core.tracing import TraceRecord, calculate_cost, tracer
from app.guardrails.injection import check_prompt_injection, get_safe_refusal_message
from app.guardrails.pii import mask_pii
from app.ml.classifier import TicketClassificationResult, predict
from app.rag.chunker import Chunk
from app.rag.pipeline import Citation

# In-memory session memory buffer: session_id -> list of turn dicts
_SESSION_MEMORY: dict[str, list[dict[str, str]]] = {}
MAX_SESSION_HISTORY = 5


class AgentChatResponse(BaseModel):
    """Complete response returned by the SupportMind Agent system."""

    session_id: str
    answer: str
    agent_chosen: str
    category: str
    urgency: str
    classification_confidence: float
    citations: list[Citation] = Field(default_factory=list)
    pending_action: dict[str, Any] | None = None
    retrieved_chunks: list[dict[str, Any]] = Field(default_factory=list)
    critic_verdict: dict[str, Any] | None = None
    pii_types_detected: list[str] = Field(default_factory=list)
    trace_id: str
    latency_ms: float
    estimated_cost_usd: float


class RouterAgent:
    """Master orchestrator routing user inquiries to specialized agents."""

    def __init__(
        self,
        knowledge_agent: KnowledgeAgent | None = None,
        data_agent: DataAgent | None = None,
        action_agent: ActionAgent | None = None,
        critic_agent: CriticAgent | None = None
    ):
        self.knowledge_agent = knowledge_agent or KnowledgeAgent()
        self.data_agent = data_agent or DataAgent()
        self.action_agent = action_agent or ActionAgent()
        self.critic_agent = critic_agent or CriticAgent()

    def process_message(
        self,
        session_id: str,
        user_message: str,
        prompt_version: str = "v3"
    ) -> AgentChatResponse:
        """Process an incoming customer message through the agentic lifecycle."""
        start_time = time.perf_counter()

        # Step 1: Guardrail Check - Prompt Injection Detection
        injection_result = check_prompt_injection(user_message)
        if not injection_result.is_safe:
            refusal = get_safe_refusal_message(injection_result.reason)
            latency = round((time.perf_counter() - start_time) * 1000, 2)
            trace = tracer.record(TraceRecord(
                session_id=session_id,
                agent_chosen="security_guardrail",
                tools_called=["check_prompt_injection"],
                prompt_version=prompt_version,
                retrieved_chunks_count=0,
                latency_ms=latency,
                token_count=40,
                estimated_cost_usd=calculate_cost(40),
                critic_flagged=True,
                critic_notes=f"Blocked prompt injection: {injection_result.reason}"
            ))
            return AgentChatResponse(
                session_id=session_id,
                answer=refusal,
                agent_chosen="security_guardrail",
                category="other",
                urgency="high",
                classification_confidence=1.0,
                citations=[],
                pending_action=None,
                retrieved_chunks=[],
                critic_verdict={"is_faithful": False, "notes": injection_result.reason},
                pii_types_detected=[],
                trace_id=trace.trace_id,
                latency_ms=latency,
                estimated_cost_usd=calculate_cost(40)
            )

        # Step 2: Guardrail Check - PII Masking
        sanitized_message, pii_detected = mask_pii(user_message)

        # Step 3: Intent & Category Classification
        classification: TicketClassificationResult = predict(sanitized_message)

        # Step 4: Routing Decision
        # Check explicit Order Query intent
        has_order_id = bool(re.search(r"\bORD-\d{5}\b", user_message, re.I))
        has_tracking_intent = any(w in user_message.lower() for w in ["where is my order", "track my package", "order status", "status of order"])
        has_refund_intent = bool(re.search(r"\b(start|issue|process|request|create|need|want)\b.*?\b(refund|return label|money back)\b", user_message, re.I)) or "refund request" in user_message.lower()

        pending_action_dict = None
        citations: list[Citation] = []
        retrieved_chunks: list[dict[str, Any]] = []
        critic_dict: dict[str, Any] | None = None
        tools_called = ["classifier.predict"]
        agent_chosen = "knowledge_agent"
        answer = ""

        # Route A: Data Agent (Order / Fulfillment Lookups)
        if has_order_id or (has_tracking_intent and ("@" in user_message or classification.category == "delivery")):
            agent_chosen = "data_agent"
            data_resp = self.data_agent.handle_query(user_message)
            answer = data_resp["answer"]
            tools_called.append(data_resp["tool_called"])

        # Route B: Action Agent (Refund or High-Urgency Ticket with Human-in-the-loop)
        elif has_refund_intent:
            agent_chosen = "action_agent"
            order_match = re.search(r"\bORD-\d{5}\b", user_message, re.I)
            order_id = order_match.group(0).upper() if order_match else "ORD-UNKNOWN"

            # Trigger start_refund_request tool
            action = self.action_agent.start_refund_request(
                session_id=session_id,
                order_id=order_id,
                amount=89.99,  # Default or extracted merchandise price
                reason=sanitized_message
            )
            tools_called.append("start_refund_request")
            pending_action_dict = asdict(action)
            answer = (
                f"I have initiated a refund request (`{action.action_id}`) for order **{order_id}**. "
                f"Because this action involves financial disbursement, it requires **human supervisor authorization**. "
                f"Please review the pending action card below to approve or reject."
            )

        # Route C: Knowledge Agent (RAG Policy Search with Citations)
        else:
            agent_chosen = "knowledge_agent"
            tools_called.append("rag_pipeline.retrieve_and_generate")
            rag_resp = self.knowledge_agent.handle_query(
                query=sanitized_message,
                prompt_version=prompt_version,
                top_k=4
            )
            answer = rag_resp.answer
            citations = rag_resp.citations
            retrieved_chunks = rag_resp.retrieved_chunks

            # Convert retrieved chunks back to Chunk objects for the critic
            chunk_objs = [
                Chunk(chunk_id=c["chunk_id"], text=c["text"], source=c["source"], section=c["section"], chunk_index=0)
                for c in retrieved_chunks
            ]

            # Step 5: Critic Agent Faithfulness Audit
            critic_verdict: CriticVerdict = self.critic_agent.evaluate_faithfulness(
                query=sanitized_message,
                draft_answer=answer,
                retrieved_chunks=chunk_objs
            )
            tools_called.append("critic_agent.evaluate_faithfulness")
            critic_dict = {
                "is_faithful": critic_verdict.is_faithful,
                "faithfulness_score": critic_verdict.faithfulness_score,
                "flagged_claims": critic_verdict.flagged_claims,
                "notes": critic_verdict.notes
            }

            # If critic flags hallucination, enforce fallback
            if not critic_verdict.is_faithful:
                answer += "\n\n*(Note: Some specific details in this answer are pending verification against official policy documentation.)*"

        # Step 6: Maintain Short-Term Session Memory
        global _SESSION_MEMORY
        if session_id not in _SESSION_MEMORY:
            _SESSION_MEMORY[session_id] = []
        _SESSION_MEMORY[session_id].append({"role": "user", "content": sanitized_message})
        _SESSION_MEMORY[session_id].append({"role": "assistant", "content": answer})
        if len(_SESSION_MEMORY[session_id]) > (MAX_SESSION_HISTORY * 2):
            _SESSION_MEMORY[session_id] = _SESSION_MEMORY[session_id][-(MAX_SESSION_HISTORY * 2):]

        latency = round((time.perf_counter() - start_time) * 1000, 2)
        token_count = max(50, len(sanitized_message.split()) * 2 + len(answer.split()) * 2)
        cost = calculate_cost(token_count)

        # Step 7: Record Trace Telemetry
        trace = tracer.record(TraceRecord(
            session_id=session_id,
            agent_chosen=agent_chosen,
            tools_called=tools_called,
            prompt_version=prompt_version,
            retrieved_chunks_count=len(retrieved_chunks),
            latency_ms=latency,
            token_count=token_count,
            estimated_cost_usd=cost,
            critic_flagged=not critic_dict["is_faithful"] if critic_dict else False,
            critic_notes=critic_dict["notes"] if critic_dict else ""
        ))

        return AgentChatResponse(
            session_id=session_id,
            answer=answer,
            agent_chosen=agent_chosen,
            category=classification.category,
            urgency=classification.urgency,
            classification_confidence=classification.confidence,
            citations=citations,
            pending_action=pending_action_dict,
            retrieved_chunks=retrieved_chunks,
            critic_verdict=critic_dict,
            pii_types_detected=pii_detected,
            trace_id=trace.trace_id,
            latency_ms=latency,
            estimated_cost_usd=cost
        )

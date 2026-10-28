"""Observability and Tracing System for SupportMind.

Logs every agent decision, tool execution, chunk retrieval, latency metric,
and token cost calculation to SQLite for UI Agent Trace inspections.
"""

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from app.db.models import get_db_connection

# In-memory fast ring buffer for active session trace inspection
_RECENT_TRACES: list[dict[str, Any]] = []
MAX_IN_MEMORY_TRACES = 200


@dataclass
class TraceRecord:
    """Detailed telemetry record for an agent execution turn."""

    session_id: str
    agent_chosen: str
    tools_called: list[str] = field(default_factory=list)
    prompt_version: str = "v3"
    retrieved_chunks_count: int = 0
    latency_ms: float = 0.0
    token_count: int = 0
    estimated_cost_usd: float = 0.0
    critic_flagged: bool = False
    critic_notes: str = ""
    trace_id: str = field(default_factory=lambda: f"TRC-{uuid.uuid4().hex[:10].upper()}")
    created_at: str | None = None


def calculate_cost(tokens: int, model_name: str = "gemini-2.5-flash") -> float:
    """Calculate approximate LLM API cost in USD based on token counts.

    Gemini 2.5 Flash pricing: approx $0.15 per 1M tokens combined.
    """
    cost_per_million = 0.15
    return round((tokens / 1_000_000) * cost_per_million, 6)


class TracingSystem:
    """Manages recording and querying execution traces."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path

    def record(self, trace: TraceRecord) -> TraceRecord:
        """Persist trace to SQLite database and in-memory ring buffer."""
        record_dict = asdict(trace)
        if not trace.created_at:
            trace.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
            record_dict["created_at"] = trace.created_at

        # 1. Update in-memory buffer
        global _RECENT_TRACES
        _RECENT_TRACES.insert(0, record_dict)
        if len(_RECENT_TRACES) > MAX_IN_MEMORY_TRACES:
            _RECENT_TRACES = _RECENT_TRACES[:MAX_IN_MEMORY_TRACES]

        # 2. Persist to SQLite
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO traces (
                    trace_id, session_id, agent_chosen, tools_called,
                    prompt_version, retrieved_chunks_count, latency_ms,
                    token_count, estimated_cost_usd, critic_flagged, critic_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trace.trace_id,
                trace.session_id,
                trace.agent_chosen,
                json.dumps(trace.tools_called),
                trace.prompt_version,
                trace.retrieved_chunks_count,
                trace.latency_ms,
                trace.token_count,
                trace.estimated_cost_usd,
                1 if trace.critic_flagged else 0,
                trace.critic_notes
            ))
            conn.commit()
            conn.close()
        except Exception:
            # Observability logging should never crash the core application flow
            pass

        return trace

    def get_traces_for_session(self, session_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Fetch chronological traces for a specific conversation session."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM traces
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (session_id, limit))
            rows = cursor.fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return [t for t in _RECENT_TRACES if t.get("session_id") == session_id][:limit]

    def get_session_traces(self, session_id: str, limit: int = 20) -> list[dict[str, Any]]:
        """Alias for get_traces_for_session."""
        return self.get_traces_for_session(session_id, limit=limit)

    def get_recent_traces(self, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch globally recent traces across all sessions."""
        try:
            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM traces ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except Exception:
            return _RECENT_TRACES[:limit]


# Global tracing singleton
tracer = TracingSystem()

"""Pipeline SSE events — Kanban stages + the audit "wow-beat" micro-events.

The frontend consumes these to drive the live monitor and the 3D self-correction
animation (spike E paced the cadence). ``sse_line`` renders an event as a
``text/event-stream`` frame.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Stage(StrEnum):
    """Pipeline stage / event names emitted over SSE."""

    QUEUED = "queued"
    INGESTING = "ingesting"
    PLANNING = "planning"
    HATS_RUNNING = "hats_running"
    AUDITING = "auditing"
    SCORING = "scoring"
    COMPLETE = "complete"
    # audit wow-beats (spike E sequence)
    AUDIT_STARTED = "audit_started"
    INCONSISTENCY_FLAGGED = "inconsistency_flagged"
    PHOENIX_CONSULTATION = "phoenix_consultation"
    ANCHOR_RETRIEVAL = "anchor_retrieval"
    SCORE_CORRECTED = "score_corrected"
    GRAPH_RESHAPE = "graph_reshape"


def _now() -> str:
    return datetime.now(UTC).isoformat()


class PipelineEvent(BaseModel):
    """One streamed pipeline event."""

    stage: Stage
    payload: dict[str, Any] = Field(default_factory=dict)
    ts: str = Field(default_factory=_now)


def sse_line(event: PipelineEvent) -> str:
    """Render an event as an SSE frame (``event:`` + ``data:`` + blank line)."""
    data = json.dumps(event.payload, separators=(",", ":"), ensure_ascii=False)
    return f"event: {event.stage.value}\ndata: {data}\n\n"

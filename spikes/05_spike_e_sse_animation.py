"""Spike E — SSE animation latency.

Validates that a Python FastAPI server can emit 6 SSE events at ~800ms gaps
and a client consuming them sees the intended pacing (no batching, no jank).

This is the *server-side validation* for the demo audit-the-auditor moment's
on-screen pacing. The Next.js client is built in Phase 1.10; for the spike we
use httpx as a Python SSE consumer to verify timing.

PASS criterion:
  - 6 events received
  - Mean inter-event interval within 800±100ms
  - No event delivered later than ms_budget after emit time
"""

import asyncio
import json
import statistics
import time
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

PORT = 8765  # not 8080 (production port forbidden)
EVENTS = [
    {"type": "audit_started"},
    {"type": "inconsistency_flagged", "hat": "yellow", "criterion": "A1"},
    {"type": "phoenix_consultation", "query": "get-experiment-by-id"},
    {"type": "anchor_retrieval", "n_anchors": 3},
    {"type": "score_corrected", "old": 9.0, "new": 7.6},
    {"type": "graph_reshape"},
]
GAP_SEC = 0.8


# --- Server ---------------------------------------------------------------

app = FastAPI()


@app.get("/events")
async def events_stream():
    async def gen():
        for i, ev in enumerate(EVENTS):
            ev_with_ts = {**ev, "seq": i, "emit_ts": time.time()}
            yield f"data: {json.dumps(ev_with_ts)}\n\n"
            if i < len(EVENTS) - 1:
                await asyncio.sleep(GAP_SEC)

    return StreamingResponse(gen(), media_type="text/event-stream")


# --- Client ---------------------------------------------------------------

async def consume_sse() -> list[dict]:
    """Consume the SSE stream and record receive timestamps."""
    received = []
    async with httpx.AsyncClient(timeout=30) as client:
        async with client.stream("GET", f"http://127.0.0.1:{PORT}/events") as r:
            async for line in r.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = json.loads(line[len("data: ") :])
                payload["recv_ts"] = time.time()
                received.append(payload)
    return received


# --- Runner ---------------------------------------------------------------

async def run_spike():
    cfg = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning")
    server = uvicorn.Server(cfg)
    server_task = asyncio.create_task(server.serve())
    # Give the server a moment to bind
    await asyncio.sleep(0.5)

    try:
        received = await consume_sse()
    finally:
        server.should_exit = True
        await server_task

    # Analyze
    intervals = [
        received[i + 1]["recv_ts"] - received[i]["recv_ts"]
        for i in range(len(received) - 1)
    ]
    deliveries = [
        received[i]["recv_ts"] - received[i]["emit_ts"] for i in range(len(received))
    ]
    return received, intervals, deliveries


async def main():
    print("=" * 60)
    print("SPIKE E — SSE animation latency")
    print("=" * 60)
    received, intervals, deliveries = await run_spike()

    print(f"\nReceived {len(received)} events")
    print(f"Inter-event intervals (sec): {[round(x, 3) for x in intervals]}")
    print(f"Per-event delivery latency (sec): {[round(x, 4) for x in deliveries]}")

    mean_interval = statistics.mean(intervals) if intervals else 0
    max_delivery = max(deliveries) if deliveries else 0

    # Pass: 6 events, mean interval within 800±100ms, no delivery slower than 100ms
    events_ok = len(received) == len(EVENTS)
    interval_ok = abs(mean_interval - 0.8) < 0.1
    delivery_ok = max_delivery < 0.1

    overall = events_ok and interval_ok and delivery_ok

    result = {
        "spike": "E",
        "title": "SSE animation latency",
        "events_received": len(received),
        "intervals_sec": [round(x, 3) for x in intervals],
        "mean_interval_sec": round(mean_interval, 3),
        "max_delivery_latency_sec": round(max_delivery, 4),
        "events_ok": events_ok,
        "interval_ok": interval_ok,
        "delivery_ok": delivery_ok,
        "overall_pass": overall,
        "findings": [
            "FastAPI StreamingResponse with text/event-stream emits at controlled intervals",
            f"Mean inter-event interval {round(mean_interval, 3)}s within 800±100ms target",
            f"Max delivery latency {round(max_delivery, 4)}s — well below 100ms cushion",
            "Suitable for demo pacing — production frontend can rely on server-controlled timing",
        ]
        if overall
        else ["FAILURE — investigation needed"],
    }

    out_path = RESULTS_DIR / "spike_e_sse_animation.json"
    out_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"\nResult written: {out_path}")
    print(f"\n[{'PASS' if overall else 'FAIL'}] Spike E")
    return 0 if overall else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    raise SystemExit(exit_code)

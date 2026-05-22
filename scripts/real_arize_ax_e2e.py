#!/usr/bin/env python3
"""Real e2e exporting to **Arize AX** (app.arize.com) — no mocks.

The provided key is an Arize AX User API Key (``ak-…``), so traces go to AX over
``otlp.arize.com`` (api_key + space_id) via ``arize-otel``, NOT to Phoenix Cloud.
Registers the AX tracer, emits a probe span (fast auth check), then runs the full
real Vertex Gemini pipeline (RubricSynthesizer -> 6-hat -> audit self-correct ->
score -> report) with every stage as a span exported to the AX project.

Run (creds from env, never hard-coded):
  ARIZE_SPACE_ID=... ARIZE_API_KEY=... ARIZE_PROJECT_NAME=glasshat \
  GOOGLE_CLOUD_PROJECT=panelyst-hackathon GOOGLE_GENAI_USE_VERTEXAI=true \
  GOOGLE_CLOUD_REGION=us-central1 GOOGLE_CLOUD_LOCATION=global \
  GLASSHAT_GEMINI_PRO=gemini-3.1-pro-preview GLASSHAT_GEMINI_FLASH=gemini-3.1-flash-lite \
  GLASSHAT_GEMINI_FLASH_LITE=gemini-3.1-flash-lite \
  uv run --with arize-otel --extra vertex python scripts/real_arize_ax_e2e.py
"""

from __future__ import annotations

import asyncio
import os
from contextlib import contextmanager
from typing import Any

PROJECT = os.environ.get("ARIZE_PROJECT_NAME", "glasshat")


class LiveTracer:
    """Emits pipeline spans via the already-registered OTel provider (no re-register)."""

    def __init__(self) -> None:
        from opentelemetry import trace

        self._tracer = trace.get_tracer("glasshat")

    @contextmanager
    def span(self, name: str, **attrs: Any) -> Any:
        with self._tracer.start_as_current_span(name) as sp:
            for k, v in attrs.items():
                sp.set_attribute(k, v)
            yield self

    def set_attr(self, key: str, value: Any) -> None:
        from opentelemetry import trace

        trace.get_current_span().set_attribute(key, value)


async def main() -> None:
    from arize.otel import register
    from glasshat.agents.audit import ConsultResult, TableConsultant
    from glasshat.agents.types import EvaluationInput
    from glasshat.pipeline.engine import Deps, run_evaluation
    from glasshat.rubric.presets import load_preset
    from glasshat.shared.blobstore import LocalFsBlobStore
    from glasshat.shared.docstore import MemoryDocStore
    from glasshat.shared.enums import Hat, RunMode
    from glasshat.shared.llm import VertexLlmClient
    from glasshat.shared.retrieval import HybridIndex

    space_id = os.environ.get("ARIZE_SPACE_ID", "")
    api_key = os.environ.get("ARIZE_API_KEY", "")
    if not (space_id and api_key):
        raise SystemExit("ARIZE_SPACE_ID and ARIZE_API_KEY must be set (Arize AX).")

    print(f"[1] Registering OTel -> Arize AX (otlp.arize.com) project={PROJECT} ...")
    register(
        space_id=space_id,
        api_key=api_key,
        project_name=PROJECT,
        set_global_tracer_provider=True,
        batch=False,
        log_to_console=False,
    )

    print("[2] Probe span (fast auth check) ...")
    tracer = LiveTracer()
    with tracer.span("glasshat.probe", **{"glasshat.kind": "probe"}):
        pass
    from opentelemetry import trace as _t

    _t.get_tracer_provider().force_flush()  # type: ignore[attr-defined]
    await asyncio.sleep(2.0)
    print("    probe flushed (watch for any export error above)")

    print("[3] Real evaluation pipeline (real Vertex Gemini hats) ...")
    rubric = load_preset("rapid-agent")
    table = {
        (Hat.YELLOW, c.id, b): ConsultResult(1.2, 14, 3.0, 9.0)
        for c in rubric.criteria
        for b in ("low", "mid", "high")
    }
    deps = Deps(
        llm=VertexLlmClient(),
        retrieval=HybridIndex(),
        docstore=MemoryDocStore(),
        blobstore=LocalFsBlobStore("./var/ax"),
        tracer=LiveTracer(),
        consultant=TableConsultant(table),
    )
    inp = EvaluationInput(
        rubric_source={"preset_id": "rapid-agent"},
        deck_text=(
            "We built Glasshat, a rubric-aware multi-agent evaluator on Gemini + Google ADK "
            "with in-code hybrid retrieval and a Phoenix self-audit loop. Tests and CI included."
        ),
        mode=RunMode.JUDGE,
    )
    events: list[Any] = []
    record = await run_evaluation(inp, deps, on_event=events.append)

    print("\n=== RUN RECORD (real Gemini) ===")
    print(f"run_id={record.run_id}  final_score={record.final_score}")
    for s in record.scores:
        print(f"  {s.criterion_id}: {s.score}{'  [self-corrected]' if s.audit else ''}")
    for c in record.audit_corrections:
        print(f"  audit {c.hat} {c.criterion_id}: {c.original} -> {c.corrected}")
    print(f"SSE stages: {len(events)}")

    print("\n[4] Flushing all spans to Arize AX ...")
    _t.get_tracer_provider().force_flush()  # type: ignore[attr-defined]
    await asyncio.sleep(5.0)
    print(f"\nDONE — open app.arize.com -> your space -> project '{PROJECT}' to see the traces.")


if __name__ == "__main__":
    asyncio.run(main())

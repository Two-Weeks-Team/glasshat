from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from glasshat.agents.audit import ConsultResult, TableConsultant
from glasshat.api import create_app
from glasshat.pipeline.engine import Deps
from glasshat.rubric.presets import load_preset
from glasshat.shared.blobstore import LocalFsBlobStore
from glasshat.shared.docstore import MemoryDocStore
from glasshat.shared.enums import Hat
from glasshat.shared.llm import MockLlmClient
from glasshat.shared.retrieval import HybridIndex
from glasshat.shared.tracing import NoOpTracer


class _OverconfidentYellowLlm(MockLlmClient):
    async def generate(self, prompt: str, *, tier: str = "flash", **kw: Any) -> str:
        if "YELLOW" in prompt:
            return "SCORE: 9.0\nRATIONALE: optimistic"
        return await super().generate(prompt, tier=tier, **kw)


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    r = load_preset("rapid-agent")
    table = {
        (Hat.YELLOW, c.id, b): ConsultResult(1.74, 14, 6.0, 8.5)
        for c in r.criteria
        for b in ("low", "mid", "high")
    }
    deps = Deps(
        llm=_OverconfidentYellowLlm(embedding_dim=8),
        retrieval=HybridIndex(),
        docstore=MemoryDocStore(),
        blobstore=LocalFsBlobStore(str(tmp_path)),
        tracer=NoOpTracer(),
        consultant=TableConsultant(table),
    )
    return TestClient(create_app(deps=deps))


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_presets_lists_all(client: TestClient) -> None:
    r = client.get("/api/presets")
    assert r.status_code == 200
    body = r.json()
    ids = {p["id"] for p in body}
    assert {"rapid-agent", "qdrant", "cmux-aim", "gemini3"} <= ids
    ra = next(p for p in body if p["id"] == "rapid-agent")
    assert ra["criteria_count"] == 4
    assert ra["final_scale"] == "0-100"
    assert ra["label"] == "Rapid Agent"
    assert ra["source_type"] == "preset"


def test_plan_preview(client: TestClient) -> None:
    r = client.post(
        "/api/plan", json={"rubric_source": {"preset_id": "rapid-agent"}, "deck_text": "x"}
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body["hats_enabled"]) == 6
    assert len(body["criteria_in_scope"]) == 4


def test_evaluate_then_get_run(client: TestClient) -> None:
    r = client.post(
        "/api/evaluate",
        json={
            "rubric_source": {"preset_id": "rapid-agent"},
            "deck_text": "we built a novel system",
            "mode": "judge",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["final_score"] > 0
    assert len(body["audit_corrections"]) >= 1
    run_id = body["run_id"]
    got = client.get(f"/api/runs/{run_id}")
    assert got.status_code == 200 and got.json()["run_id"] == run_id


def test_get_missing_run_404(client: TestClient) -> None:
    assert client.get("/api/runs/does-not-exist").status_code == 404


def test_stream_emits_complete_and_correction(client: TestClient) -> None:
    r = client.post(
        "/api/evaluate/stream",
        json={"rubric_source": {"preset_id": "rapid-agent"}, "deck_text": "x y z"},
    )
    assert r.status_code == 200
    assert "event: complete" in r.text
    assert "event: score_corrected" in r.text


def test_override_appends_to_record(client: TestClient) -> None:
    run_id = client.post(
        "/api/evaluate",
        json={"rubric_source": {"preset_id": "rapid-agent"}, "deck_text": "x", "mode": "judge"},
    ).json()["run_id"]
    o = client.post(
        f"/api/runs/{run_id}/override",
        json={"criterion_id": "tech-implementation", "score": 4.0, "reason": "manual review"},
    )
    assert o.status_code == 200
    stored = client.get(f"/api/runs/{run_id}").json()
    assert any(ov["criterion_id"] == "tech-implementation" for ov in stored["overrides"])

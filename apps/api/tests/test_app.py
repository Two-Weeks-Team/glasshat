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


# --- D: API hardening (rate limit + CORS allowlist + input validation) ------


def _mock_deps(tmp_path: Path) -> Deps:
    r = load_preset("rapid-agent")
    table = {
        (Hat.YELLOW, c.id, b): ConsultResult(1.74, 14, 6.0, 8.5)
        for c in r.criteria
        for b in ("low", "mid", "high")
    }
    return Deps(
        llm=MockLlmClient(embedding_dim=8),
        retrieval=HybridIndex(),
        docstore=MemoryDocStore(),
        blobstore=LocalFsBlobStore(str(tmp_path)),
        tracer=NoOpTracer(),
        consultant=TableConsultant(table),
    )


def test_evaluate_is_rate_limited_per_ip(tmp_path: Path) -> None:
    from glasshat.shared.config import Settings

    settings = Settings(_env_file=None, rate_limit_per_minute=2)  # type: ignore[call-arg]
    c = TestClient(create_app(deps=_mock_deps(tmp_path), settings=settings))
    body = {"rubric_source": {"preset_id": "rapid-agent"}, "deck_text": "x"}
    assert c.post("/api/evaluate", json=body).status_code == 200
    assert c.post("/api/evaluate", json=body).status_code == 200
    blocked = c.post("/api/evaluate", json=body)
    assert blocked.status_code == 429
    assert "rate limit" in blocked.json()["detail"].lower()


def test_rate_limit_disabled_when_zero(tmp_path: Path) -> None:
    from glasshat.shared.config import Settings

    settings = Settings(_env_file=None, rate_limit_per_minute=0)  # type: ignore[call-arg]
    c = TestClient(create_app(deps=_mock_deps(tmp_path), settings=settings))
    body = {"rubric_source": {"preset_id": "rapid-agent"}, "deck_text": "x"}
    for _ in range(5):
        assert c.post("/api/evaluate", json=body).status_code == 200


def test_plan_endpoint_is_rate_limited(tmp_path: Path) -> None:
    """S2: the unguarded Vertex-backed /api/plan must share the rate limiter."""
    from glasshat.shared.config import Settings

    settings = Settings(_env_file=None, rate_limit_per_minute=1)  # type: ignore[call-arg]
    c = TestClient(create_app(deps=_mock_deps(tmp_path), settings=settings))
    body = {"rubric_source": {"preset_id": "rapid-agent"}, "deck_text": "x"}
    assert c.post("/api/plan", json=body).status_code == 200
    assert c.post("/api/plan", json=body).status_code == 429


def test_override_endpoint_is_rate_limited(tmp_path: Path) -> None:
    """M1: score override (run_id-only auth) must not be unbounded."""
    from glasshat.shared.config import Settings

    settings = Settings(_env_file=None, rate_limit_per_minute=2)  # type: ignore[call-arg]
    c = TestClient(create_app(deps=_mock_deps(tmp_path), settings=settings))
    run_id = c.post(  # budget 1/2 — creates a run to override
        "/api/evaluate",
        json={"rubric_source": {"preset_id": "rapid-agent"}, "deck_text": "x", "mode": "judge"},
    ).json()["run_id"]
    ov = {"criterion_id": "tech-implementation", "score": 4.0, "reason": "r"}
    assert c.post(f"/api/runs/{run_id}/override", json=ov).status_code == 200  # 2/2
    assert c.post(f"/api/runs/{run_id}/override", json=ov).status_code == 429  # blocked


def test_rate_limit_keys_real_client_ip_not_spoofed_xff(tmp_path: Path) -> None:
    """A rotated *leftmost* X-Forwarded-For must NOT mint fresh buckets — the
    limiter keys on the second-to-last entry (the Cloud-Run-appended real client).
    """
    from glasshat.shared.config import Settings

    settings = Settings(_env_file=None, rate_limit_per_minute=1)  # type: ignore[call-arg]
    c = TestClient(create_app(deps=_mock_deps(tmp_path), settings=settings))
    body = {"rubric_source": {"preset_id": "rapid-agent"}, "deck_text": "x"}
    # Same real client (second-to-last = 9.9.9.9); only the spoofable leftmost differs.
    h1 = {"X-Forwarded-For": "1.1.1.1, 9.9.9.9, 10.0.0.1"}
    h2 = {"X-Forwarded-For": "2.2.2.2, 9.9.9.9, 10.0.0.1"}
    assert c.post("/api/evaluate", json=body, headers=h1).status_code == 200
    assert c.post("/api/evaluate", json=body, headers=h2).status_code == 429  # spoof can't escape
    # A genuinely different client (different second-to-last) gets its own bucket.
    h3 = {"X-Forwarded-For": "3.3.3.3, 8.8.8.8, 10.0.0.1"}
    assert c.post("/api/evaluate", json=body, headers=h3).status_code == 200


def test_cors_allowlist_reflects_configured_origin(tmp_path: Path) -> None:
    from glasshat.shared.config import Settings

    settings = Settings(_env_file=None, cors_allow_origins="https://glasshat.example")  # type: ignore[call-arg]
    c = TestClient(create_app(deps=_mock_deps(tmp_path), settings=settings))
    allowed = c.options(
        "/api/evaluate",
        headers={
            "Origin": "https://glasshat.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert allowed.headers.get("access-control-allow-origin") == "https://glasshat.example"
    denied = c.options(
        "/api/evaluate",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert denied.headers.get("access-control-allow-origin") != "https://evil.example"


def test_evaluate_rejects_non_github_repo_url(client: TestClient) -> None:
    r = client.post(
        "/api/evaluate",
        json={"rubric_source": {"preset_id": "rapid-agent"}, "repo_url": "https://gitlab.com/a/b"},
    )
    assert r.status_code == 422  # pydantic validation rejects at the boundary


class _RaisingLlm(MockLlmClient):
    """Embeds normally (ingest succeeds) but raises during generation, so the
    pipeline fails mid-run — used to prove the SSE stream terminates."""

    async def generate(self, prompt: str, *, tier: str = "flash", **kw: Any) -> str:
        raise RuntimeError("synthesizer boom")


def test_stream_terminates_when_engine_raises(tmp_path: Path) -> None:
    """An exception inside the pipeline must close the SSE stream (sentinel in the
    `finally`), not hang — if TestClient returns, the generator terminated."""
    deps = _mock_deps(tmp_path)
    deps.llm = _RaisingLlm(embedding_dim=8)
    c = TestClient(create_app(deps=deps))
    r = c.post(
        "/api/evaluate/stream",
        json={"rubric_source": {"preset_id": "rapid-agent"}, "deck_text": "x y z"},
    )
    # The request returned (no hang) and the stream never reached completion,
    # but closed gracefully with an `error` event (no 500, no internal leak).
    assert r.status_code == 200
    assert "event: complete" not in r.text
    assert "event: error" in r.text
    assert "synthesizer boom" not in r.text  # internal error text not leaked
    # Early stages still streamed before the failure.
    assert "event: queued" in r.text

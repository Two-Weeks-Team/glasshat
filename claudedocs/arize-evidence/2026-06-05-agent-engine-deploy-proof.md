# Glasshat on the Gemini Enterprise Agent Platform — live deploy + Arize AX proof

**Date:** 2026-06-05 · **Project:** `panelyst-hackathon` (number 916178791322) · **Region:** us-central1
**Machine-readable capture:** [`ax-live-capture.json`](./ax-live-capture.json) (re-runnable; numbers below come from it).

## What is genuinely proven

The glasshat evaluation pipeline — the **ADK 2.0 Workflow** graph (sequential spine →
6-hat parallel fan-out → JoinNode → audit) — is **deployed on the Gemini Enterprise
Agent Platform (Agent Runtime / Agent Engine)**, **serves live queries**, and its **full
nested trace + a hit@13 experiment land in Arize AX** (project `glasshat`, space
`U3BhY2U6NDUxMzY6V012Yg==` = Space:45136). Captured with real `ARIZE_SPACE_ID` +
`ARIZE_API_KEY` present.

| Item | Value (verifiable) |
|---|---|
| **Live Agent Engine resource** | `projects/916178791322/locations/us-central1/reasoningEngines/7480191458771730432` (serving; earlier proof resources cleaned up). A `stream_query` returns a real `RunRecord` (live `final_score` ~43–49 on real Gemini). |
| **Nested Arize AX trace** | A **2-query snapshot = 104 spans**; accumulated over the session (`ax-live-capture.json`, last 4 h): **72× AsyncGenerateContent + 75× AsyncEmbedContent** (the six hats' Gemini generate + embedding calls) under **`agent_run [glasshat_eval]` → `invocation [glasshat]` → `invocation [7480…]`**. The deployed resource genuinely produced these — verified via `client.spans.list(project="glasshat")`. ADK + google-genai OpenInference instrumentors on an **isolated** provider (`set_global_tracer_provider=False`). |
| **Arize AX Experiment (hit@13)** | Experiment **`glasshat-hit-at-13-gemini`** (id `RXhwZXJpbWVudDo5ODkwNTpCbW5v`) over dataset **`glasshat-golden`**, + a **`glasshat-prompt-injection`** code evaluator. **hit@13 = 0.6154** on real Gemini (8/13 winners in the top-13) vs **0.3846** mock / **0.26** chance. Produced by `experiments/run_arize_experiment.py` (the experiment harness, *not* the deployed agent). Binary Winner-label → **hit@13, NOT a rank curve**; audit Δ=0 on this golden set. |
| Deploy driver | `deploy/agent_engine_deploy.py` via `vertexai.Client().agent_engines.create(...)` |
| Packaging | merged PEP-420 `glasshat/` source tree as `extra_packages` (wheels are copied, not installed → don't import) |
| Governance | `identity_type=AGENT_IDENTITY`; managed Sessions + Memory Bank auto-created |

### Provenance (so the three facts aren't conflated)
- The **deployed resource `7480…`** is what serves `stream_query` **and** what emitted the nested AX trace (its `invocation [7480…]` spans + the per-hat Gemini spans under them).
- The **hit@13 0.6154** comes from the **experiment harness** (`run_arize_experiment.py`, real Gemini over the golden set) — the *same* pipeline, a *different* invocation, pushed to the *same* Arize space. It is not produced by querying the deployed agent.

### Reproduce
```python
# query the live deployed agent (emits a nested AX trace)
import json, vertexai
client = vertexai.Client(project="panelyst-hackathon", location="us-central1")
agent = client.agent_engines.get(
    name="projects/916178791322/locations/us-central1/reasoningEngines/7480191458771730432")
msg = json.dumps({"rubric_source": {"preset_id": "rapid-agent"},
                  "deck_text": "RAG meeting-scheduler agent.", "mode": "judge"})
events = list(agent.stream_query(message=msg, user_id="proof"))   # → RunRecord JSON
```
```bash
# the hit@13 Arize AX experiment on real Gemini (creds in env)
ARIZE_SPACE_ID=… ARIZE_API_KEY=… LLM_BACKEND=gemini-enterprise \
  uv run --with-requirements deploy/requirements-cloud.txt python experiments/run_arize_experiment.py
```

## Five real bugs found + fixed during the live deploy (all in the driver/agent)
1. **Reserved env vars** — `GOOGLE_CLOUD_PROJECT`/`LOCATION` are platform-reserved (`400 FAILED_PRECONDITION`); removed from `env_vars` (the platform provides them).
2. **`cloudpickle`** missing from the remote requirements (Agent Engine deserializes the agent with it).
3. **Packaging** — `extra_packages` copies source, it does not pip-install; switched from wheels to a single merged `glasshat/` namespace tree → fixed `No module named 'glasshat'`.
4. **Tracer double-registration** — `MONITOR_BACKEND=arize` made the pipeline's manual ArizeTracer register a 2nd provider; dropped it so the instrumentor (`set_up`) is the single source.
5. **`Event.invocation_id`** — the managed Session requires it (`400 INVALID_ARGUMENT`); the custom agent now carries it from the ADK context → the result event persists and the query returns.

## Claim discipline
"Deployed on Agent Platform + serving live queries + traced + measured in Arize AX" is
literally true and reproducible (resource id, span breakdown, experiment id all in
`ax-live-capture.json`). The honest caveat is **hit@13 (binary Winner labels), not a
rank curve**; audit Δ=0 on this golden set. No "un-gameable", no "503 anchors", no rank
curve. The remaining owner-only input is the Cloud Run prod security hardening
(`SCORING_MODE=structured` + `JUDGE_API_TOKEN`), which needs a user-gated prod redeploy.

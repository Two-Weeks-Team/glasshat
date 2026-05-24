# Rapid Agent — Visual Proof Checklist (2026-05-24)

A judge-runnable checklist for the **visible** proof surfaces, not a script.
Companion to [`docs/rapid-agent-compliance.md`](../rapid-agent-compliance.md) and
[`docs/evidence-matrix.md`](../evidence-matrix.md).

## Live URLs

- Web: https://glasshat-web-o366v7tl2q-uc.a.run.app (`/judge` · `/participate`)
- API: https://glasshat-api-o366v7tl2q-uc.a.run.app (`/health` · `/api/evaluate`)

> The visual proof surfaces (proof strip, proof timeline, self-correction card,
> proof receipt) ship on branch `feat/rapid-agent-visual-proof`. The live site
> shows them after that branch is merged and redeployed; until then capture the
> screenshot locally (recipe at the bottom). The live API is current.

## Verify the live API

Health:
```bash
curl -fsS https://glasshat-api-o366v7tl2q-uc.a.run.app/health
```
Observed 2026-05-24: `{"status":"ok"}` (HTTP 200).

Evaluation (real Gemini `gemini-3.1-flash-lite`):
```bash
curl -s -X POST https://glasshat-api-o366v7tl2q-uc.a.run.app/api/evaluate \
  -H 'content-type: application/json' \
  -d '{"rubric_source":{"preset_id":"rapid-agent"},"deck_text":"Glasshat is a rubric-aware evaluation engine on Gemini and Google ADK with Arize AX observability and the Phoenix MCP calibration path...","mode":"judge"}'
```
Observed 2026-05-24:

| Field | Value |
|---|---|
| run id | `f6c60067-ab0a-4dd9-ae4d-75211c659100` |
| final score | `53.12` |
| audit corrections | `4` |
| criteria | `4` |
| corrected hats | `yellow ×4` |
| headline correction | `yellow` / `tech-implementation` · `9.0 → 7.84` (n=7) |

This is a real self-correction: the YELLOW (optimism) hat is pulled back from an
over-confident `9.0` toward the calibrated prior.

## What a judge should see in `/participate` (first 60 seconds)

On first paint (a cached real `gemini-3.1-flash-lite` sample — no run needed),
in order:

1. **Proof strip** (top): five chips — Gemini / Vertex, Google ADK, Cloud Run,
   Arize AX (all green = live) and Phoenix MCP (amber = wired / E2E).
2. **Proof timeline**: Input → RubricSynthesizer → BluePlanner → SixHatPanel →
   Audit → Final score, with the **Arize AX observability rail** beneath the
   agents and the **Phoenix MCP calibration path** feeding Audit; the Audit node
   shows a before → after score movement.
3. **Self-correction card**: which hat over-scored, original → corrected, the
   delta, the calibration basis, and a bar that slides from the over-confident
   origin to the calibrated value. Caption: *"Glasshat catches its own
   over-confidence and corrects the score before the judge locks it."*
4. **3D self-correction graph**: the constellation reshapes corrected nodes from
   their over-confident origin (loads on click in the sample for performance;
   renders immediately on a real run).
5. **Proof receipt**: copyable run id + live fields (final score, corrections,
   criteria, timestamp) and static deployment config (model, tracer, deployment,
   consultant), each tagged live vs static.

Submitting a pitch and approving the plan runs the same surfaces **live** (the
timeline animates from the SSE stream; the correction card and receipt fill from
the real RunRecord).

## Live vs wired / E2E-only

| Claim | State | Note |
|---|---|---|
| Gemini / Vertex (`gemini-3.1-flash-lite`) | **live** | every `/api/evaluate` request |
| Google ADK runtime | **live** | orchestrates + instruments the pipeline |
| Cloud Run | **live** | API + web, `panelyst-hackathon`, us-central1 |
| Arize AX tracing | **live** | OpenInference/OTLP spans → `otlp.arize.com` |
| Phoenix MCP calibration | **wired / E2E** | `scripts/real_e2e.py` proves the ADK→MCP stdio round trip; the deployed audit uses the spike-D calibrated table prior, not a per-request MCP call |
| Run-history durability | **limited** | `DOCSTORE_BACKEND=memory` — run lookup is not guaranteed across cold restarts (see `infra/deploy.sh`) |

## Screenshot

Path (committed if captured): `docs/evidence/participate-proof-2026-05-24.png`.

Capture locally (shows all four surfaces on first paint):
```bash
cd apps/web && pnpm install && pnpm dev   # http://localhost:3000/participate
# Screenshot the first viewport: proof strip + proof timeline + self-correction
# card + (scroll) proof receipt. Desktop width >= 1280px.
```

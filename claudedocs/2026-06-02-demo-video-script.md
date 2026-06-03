# Glasshat — Demo Video Script (≤ 3:00 beat sheet)

> **Scope:** this is the *script/beat sheet only*. Recording, narration capture,
> screen-capture, editing, captions, and upload are the teammate's job — out of
> scope for this document. Hand this to whoever records.

**Track:** Google Cloud Rapid Agent Hackathon — **Arize track**.
**Live model:** Vertex AI **`gemini-3.1-flash-lite`** (global endpoint).
**One-liner:** *"Glasshat doesn't just judge projects — it audits the judge."*

## Hard rules for the recording

- **Total runtime ≤ 3:00.** Aim for 2:40 to leave breathing room.
- **No third-party logos** on screen except **Google Cloud / Gemini / Vertex AI**
  and **Arize / Arize AX / Phoenix** (the sponsor + track stack). No competitor
  marks, no Qdrant logo (the Qdrant rubric is *judged content*, not a dependency —
  see the on-screen caption in Beat 5).
- **Fixed "wow" input** (do NOT improvise input live): use the pre-seeded sample
  cohort on `/judge` + the canned deck on `/participate`. Improvising risks a cold
  Vertex call (~cold start 5–7 s + ~live run) on camera. Warm the service first
  (hit `/health` and run one sample) ~2 min before recording.
- **Honesty (Skeptic-safe) line is mandatory** — see Beat 4. Do not claim more
  than the deployed reality.

## Beats

### 0:00–0:15 — Cold open (the thesis)
- **On screen:** the landing hero, full-bleed. The headline *"It audits the judge."*
- **VO:** "Every hackathon, every grant, every promotion runs on human-or-AI
  judgment that nobody audits. Glasshat audits the judgment itself."

### 0:15–0:45 — The pipeline, made visible (Gemini + Google ADK)
- **On screen:** `/participate` → run the canned sample. The SSE trace timeline
  streams: *ingest → rubric synthesis → six-hat panel → audit → score → report.*
- **VO:** "It ingests a deck, a GitHub repo, and the evaluator's own rules, then
  synthesizes a rubric that mirrors those rules. Six perspectives — a six-hat
  panel — each retrieve evidence and score, all on **Gemini 3.1 Flash-Lite via
  Vertex AI**, orchestrated with **Google ADK**."
- **Caption chip:** `Gemini 3.1 Flash-Lite · Vertex AI · Google ADK`

### 0:45–1:25 — The wow: self-correction on screen
- **On screen:** the audit step fires — an over-confident YELLOW score visibly
  recedes (ScoreBar ghost-origin), the 3D constellation reshapes, the final score
  drops from the raw consensus to the calibrated number.
- **VO:** "Here's the moment. The optimism hat over-scored. Against a **calibration
  prior recovered from held-out spike-D anchors** — strongest exactly where the
  evidence is thin — the audit catches its own over-confidence and pulls the score
  back — live, with the math shown, not hidden."
- **Caption chip:** `clip(score − 0.8·mean_delta, p25, p75) · ±2.0 cap`

### 1:25–1:55 — Why it matters: the audit changes who wins
- **On screen:** `/judge` → the **Rank-Flip Board**. Left column "without audit",
  right column "with Glasshat audit" — a row visibly moves to #1.
- **VO:** "On a whole cohort, the audit doesn't just nudge a number — it changes
  *who wins*. The raw consensus ranks one project first; the audited rank puts a
  different, better-evidenced project on top."

### 1:55–2:25 — The observability story (Arize AX + Phoenix MCP)
- **On screen:** the trace/proof panel — every agent + every hat is its own span;
  show the `dataset_lookup` / `phoenix_consultation` / `anchor_retrieval` events
  in the SSE stream.
- **VO (HONEST — read verbatim):** "Every step is a trace span in **Arize AX**.
  The Phoenix-MCP calibration consultant — which reads a Phoenix dataset over MCP
  and writes each correction back, so the calibration *can* improve over time — is
  implemented and wired, but the credential-free demo image you're watching runs
  the deterministic spike-D prior. The live MCP path activates by config flag when
  a Phoenix endpoint is set. We show you exactly which one is running, not more."
- **Caption chip:** `Arize AX · Phoenix MCP (wired; demo runs spike-D prior)`

### 2:25–2:45 — Close (live + open)
- **On screen:** the live URL typed into a browser, `/health` returning
  `{"status":"ok"}`, then the repo's Apache-2.0 license.
- **VO:** "It's live, it's reproducible, and it's open — Apache-2.0. Glasshat:
  the audit layer for AI evaluation."
- **Caption chip:** `live · reproducible · Apache-2.0`

## On-screen captions reference (lower-third, no logos)

| Beat | Caption |
|---|---|
| 2 | `Gemini 3.1 Flash-Lite · Vertex AI · Google ADK` |
| 3 | `clip(score − 0.8·mean_delta, p25, p75) · ±2.0 cap` |
| 5 | `Arize AX · Phoenix MCP (wired; demo runs spike-D prior)` |
| 5 | (small) `Qdrant rubric shown is judged content, not a dependency` |
| 6 | `live · reproducible · Apache-2.0` |

## Pre-flight checklist (recorder)

1. ~2 min before: `curl -fsS <API_URL>/health` → `{"status":"ok"}`; run one
   `/participate` sample to warm Vertex.
2. Use the **pre-seeded** `/judge` cohort and the **canned** `/participate` deck.
3. Confirm only sponsor/track logos appear; hide browser extensions/bookmarks.
4. Read the Beat 5 honesty line **verbatim**.

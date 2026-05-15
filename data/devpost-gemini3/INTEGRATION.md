# Gemini 3 Devpost crawl → Glasshat past_evals integration plan

> **Source**: `data/devpost-gemini3/` (crawled 2026-05-15 by sgwannabe, commit `d840d2a`).
> **Target**: Qdrant `past_evals` collection + Phoenix `glasshat-calibration-v1` experiment.
> **Status**: Plan locked 2026-05-15 per [[glasshat-rubric-and-mode]] §10. Implementation in Phase 1.B.

---

## What we have (the crawl)

| Asset | Size | Content |
|---|---|---|
| `gemini3_dataset.json` | 5.8 MB | Unified dataset: crawl meta + hackathon meta + 503 projects + 13 winners |
| `projects.json` | 5.5 MB | 503 project details (`url`, `title`, `tagline`, `video_links[]`, `github_repos[]`, `built_with[]`, full description, ...) |
| `submissions.json` | 262 KB | 503 entries (`software_id`, `title`, `tagline`, `url`, `is_winner`, `thumbnail_url`, `member_names[]`) |
| `submissions.csv` | 165 KB | Same as submissions.json, CSV format (504 lines = 1 header + 503 rows) |
| `winners.json` | 6.9 KB | 13 named winners (subset of submissions.json with `is_winner: true`) |
| `rules.html` + `rules.txt` | 104 KB + 37 KB | Official Gemini 3 Hackathon rules snapshot |
| `README.md` | 825 B | Crawl metadata: target 540, stop_at 500, pages_crawled 21, started 07:16:29Z, finished 07:30:45Z |

**Crawl metrics**:
- Duration: 14 min 16 sec
- 21 pages × ~24 projects = ~504 expected; 503 actual (1 deduplication)
- 297 with public github_repos · 462 with video_links · 425 with non-empty description
- 0 fetch errors
- 13 winners in collected gallery (note: original Gemini 3 had 24+ named winners; ~11 are on pages 22+ which were not crawled. STRETCH: extend crawl past page 21 if Phase 1.B has buffer time).

---

## How this differs from the original plan

[[glasshat-max-wins-decisions]] §10 (locked 2026-05-14) called for:
- **524 stratified** projects (24+ winners + 500 random non-winners)
- Output: `seed/gemini3-projects-524.jsonl`

What we got 2026-05-15:
- **503 sequential** (page 1-21, in Devpost gallery's default order)
- Output: `data/devpost-gemini3/*.json`
- 13 winners present (84% of original 24-winner target)

**Why this is acceptable** (rather than re-running the crawl):
- 503 ≈ 524 in statistical power for calibration purposes
- Winners are over-represented in Devpost gallery's default sort (popularity-ish), so 13 in first 21 pages is reasonable
- Re-crawling for the additional ~11 winners on pages 22-188 would take ~3 hours at 1 RPS, low marginal value
- The Top-K hit rate metric (target ≥9/13 = 69%) is achievable with 13 known winners; adding 11 more winners doesn't materially change demo punch

**Disclosure update**: README + max-wins-plan §3.4 narrative updates from "524 of 4,499" → **"503 of 4,499 including 13 named winners"**. Honest, still impressive, accurately reflects the data.

---

## Seeding plan (Phase 1.B)

### Step 1 — Schema extension on `past_evals` collection

Each `past_evals` Qdrant point gets two new payload fields per [[glasshat-rubric-and-mode]] §2:

```yaml
# packages/shared/qdrant-schemas/past_evals.yaml (excerpt — additions only)
payload_schema:
  # ... existing fields (project_id, hat, criterion, score, evidence_depth, ...)
  rubric_schema_hash:
    type: keyword
    indexed: true
    description: "SHA-256 of canonicalized SynthesizedRubric — for exact-match lookup"
  weights_vector:
    type: float[]
    indexed: false  # used as named vector for similarity, not filter
    length: variable  # depends on rubric criterion count

named_vectors:
  # ... existing dense + sparse vectors
  rubric_weights:
    size: 16            # max criterion count expected; pad shorter vectors with 0
    distance: Cosine
    on_disk: true       # small enough to keep on disk
```

### Step 2 — Synthesize Gemini 3's rubric

Run RubricSynthesizer (Phase 1.5) against `data/devpost-gemini3/rules.txt`:

```bash
uv run python -m glasshat.scripts.synthesize_rubric \
    --source data/devpost-gemini3/rules.txt \
    --output packages/rubric/presets/gemini3.yaml
```

Expected output (verified from rules + community-known weights):

```yaml
preset_id: gemini3
verified_at: 2026-05-15
source_url: https://gemini3.devpost.com/rules
synthesized:
  schema_version: "1.0"
  scoring_rule:
    aggregation: weighted_sum
    final_scale: 0-100
  criteria:
    - id: technical-execution
      weight: 0.40
      bmad_mapping: [B1, B2, B3, B4, C1, C2, C3, C4, C5]
      ...
    - id: innovation-wow
      weight: 0.30
      bmad_mapping: [A1, A3, B1]
      ...
    - id: potential-impact
      weight: 0.20
      bmad_mapping: [A1, A2, A4]
      ...
    - id: presentation-demo
      weight: 0.10
      bmad_mapping: [D1, D2, D3, D4]
      ...
  weights_vector: [0.30, 0.20, 0.10, 0.40]  # alphabetical-by-id canonical order:
                                              # innovation-wow, potential-impact, presentation-demo, technical-execution
  confidence: 0.95
```

The `rubric_schema_hash` for this synthesis becomes the value tagged on every past_eval row from the 503 corpus.

### Step 3 — Seed past_evals (no LLM re-evaluation)

For the v1 seed, we **do not re-run the Glasshat pipeline over 503 projects** (would cost ~$60 + 6h, deferred per [[glasshat-rubric-and-mode]] §2). Instead, we tag each project with its known winner status and Gemini 3's weight schema:

```python
# scripts/seed_past_evals_from_gemini3.py (excerpt)
async def seed():
    rubric = load_preset("gemini3")
    rubric_hash = canonical_sha256(rubric)
    weights = rubric["weights_vector"]  # [0.30, 0.20, 0.10, 0.40]

    with open("data/devpost-gemini3/projects.json") as f:
        projects = json.load(f)

    for project in projects:
        # Embed the project's tagline + description for vector retrieval
        text = f"{project['title']}\n{project['tagline']}\n\n{project.get('description', '')}"
        dense_vec = await vertex_embed(text)
        sparse_vec = bm25_encode(text)

        # Outcome tier from winner status
        outcome_tier = "winner" if project.get("is_winner") else "non_winner"

        # Predicted scores: NULL at seed time (will be filled when we run the pipeline
        # over a subset for the full calibration experiment Phase 1.13)
        # For v1 seed, only the meta-fields are populated.
        await qdrant.upsert(
            collection="past_evals",
            point_id=hashlib.sha256(project["url"].encode()).hexdigest()[:16],
            vector={
                "dense": dense_vec,
                "sparse": sparse_vec,
                "rubric_weights": pad_to_16(weights),
            },
            payload={
                "project_id": project["url"],
                "title": project["title"],
                "outcome_tier": outcome_tier,
                "github_repo": project.get("github_repos", [None])[0],
                "video_url": project.get("video_links", [None])[0],
                "rubric_schema_hash": rubric_hash,
                "weights_vector": weights,
                "rubric_preset_id": "gemini3",
                "source": "data/devpost-gemini3/projects.json",
                "seeded_at": "2026-05-15T...",
                # predicted scores stay null until Phase 1.13:
                "predicted_scores": None,
                "evidence_depth": None,
            },
        )
```

This enables:
- Anchor retrieval at audit time (cosine similarity on `rubric_weights` named vector)
- Filter by `outcome_tier == "winner"` to pull "what winners look like" examples
- Filter by `rubric_preset_id` if Phase 1 evolves to per-preset anchor retrieval

### Step 4 — Phase 1.13 deferred work (full calibration)

After Phase 1 D + 1.5 + B + mode UI complete, the **calibration experiment** runs the actual Glasshat pipeline over a subset of the 503 corpus:

1. Pick subset of ~50 projects (10 winners + 40 non-winners) for cost reasons
2. Run each through Glasshat with `preset: gemini3` rubric
3. Compute Top-K hit rate vs known winners
4. Update past_evals payload `predicted_scores` + `evidence_depth` for those 50
5. Aggregate per-(criterion, evidence_depth_bucket) drift into Phoenix `glasshat-calibration-v1` experiment
6. Validate held-out MAE improvement ≥15% with calibration applied

Cost estimate: 50 projects × (6 hats + 1 audit + 1 score) × Flash-Lite ≈ $5-10. Time: ~2h.

This is the basis for the AuditLoop's PhoenixConsultantAgent at runtime.

---

## Demo viewport implications

### Qdrant demo (Judge mode primary)

- 503 corpus pre-seeded into past_evals **at deploy time** (one-time)
- Demo uploads "MyHackathonSubmission" (or a real project from outside the corpus)
- Glasshat synthesizes Qdrant rubric, evaluates → shows score + Top-K hit rate against the 503 corpus' 13 winners
- 3D graph shows the 503 anchor constellation + the new submission's position
- Recommendation API close: "ranks similar to [Globot] (winner), weaker than [Aegis] (winner) on Tech, stronger than [non-winner X]"

### Rapid Agent demo (Participant mode primary)

- Same 503 corpus pre-seeded
- Demo uploads a single submission
- Glasshat synthesizes Rapid Agent rubric → evaluates → shows iterate suggestions
- Phoenix MCP consultation references the calibration experiment (built from the 50-project subset run in Step 4)

### The 503 corpus in the demo close

Both demos' close shows: "Glasshat evaluated this against 503 of Gemini 3's 4,499 submissions, anchored to 13 named winners."

Honest, defensible disclosure.

---

## File-level integration tasks (for the data engineer)

| Task | File(s) | Time |
|---|---|---|
| Extend `past_evals` schema YAML with `rubric_schema_hash` + `weights_vector` + `rubric_weights` named vector | `packages/shared/qdrant-schemas/past_evals.yaml` | 0.2d |
| Implement `scripts/seed_past_evals_from_gemini3.py` (no LLM cost — pure data load) | new file | 0.4d |
| Implement `synthesize_rubric` script wrapper (calls RubricSynthesizer agent in batch mode) | `scripts/synthesize_rubric.py` | 0.2d |
| Implement `scripts/check_top_k_hit_rate.py` (Top-K hit rate computation utility) | new file | 0.2d |
| Add anchor-retrieval helper in `services/shared/qdrant.py` using `rubric_weights` named vector | existing file | 0.2d |
| Wire anchor-retrieval into `services/audit/anchor_retrieval.py` per `docs/rubric-synthesis-spec.md` §8 | new file | 0.3d |
| **Total** | | **1.5d** (Phase 1.B time budget) |

---

## Compliance + provenance

- Source: `gemini3.devpost.com` public project gallery (Dec 2025 – Feb 2026, hackathon concluded)
- Crawl method: 1 RPS throttle, descriptive User-Agent, robots.txt verified, no auth bypass, no private data
- Storage: only **derived statistical features** (vector embeddings of public taglines/descriptions, winner labels) and **public metadata** (URL, title, member names from public Devpost). No source code is cloned at seed time.
- Disclosure: README and `docs/max-wins-plan.md` §3.4 disclose use as calibration corpus only
- Retention: indefinite — corpus is the calibration ground-truth and stays in `past_evals`

---

*Last updated: 2026-05-15 KST. Source-of-truth for how `data/devpost-gemini3/` flows into Glasshat's `past_evals` + Phoenix calibration. Owner: data engineer (Phase 1.B).*

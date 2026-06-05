"""Offline calibration experiment: hit@k against historical hackathon outcomes.

Builds a golden set from the Gemini-3 Devpost crawl and reports how many of the
evaluator's top-``k`` ranked submissions were actual winners (hit@k), for the
pre-audit vs post-audit ranking.

Honesty constraints (do not relax):
- The source has a **binary** Winner badge only — there is NO rank or score in it.
  So this computes **hit@k**, never a rank-agreement curve.
- It runs fully offline on the deterministic ``mock`` backend (CI-smoke-safe). The
  mock scorer does not read meaning from text, so its hit@k is an *illustrative
  baseline*, not evidence of ranking skill; the live figure comes from running the
  SAME harness with ``LLM_BACKEND=vertex`` (user-gated). The reported
  ``CalibrationResult.backend`` always says which was used.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from glasshat.agents.types import EvaluationInput
from glasshat.pipeline.engine import Deps, default_deps, run_evaluation
from glasshat.shared.enums import RunMode
from pydantic import BaseModel

# The Gemini-3 Devpost crawl carried exactly 13 Winner-badged submissions.
DEFAULT_K = 13

CAVEAT = (
    "Offline hit@{k} on {n} historical Gemini-3 Devpost submissions with binary "
    "Winner-badge labels ({n_winners} winners). The source has no rank or score, so "
    "this is hit@{k}, not a rank curve. Backend={backend}: the mock scorer is "
    "deterministic and illustrative (it does not read meaning from text); the live "
    "figure is produced by the same harness with LLM_BACKEND=vertex."
)


class GoldenEntry(BaseModel):
    """One labelled submission. ``placed`` is the only ground truth that exists."""

    software_id: str
    title: str
    tagline: str
    placed: bool

    def deck_text(self) -> str:
        return f"{self.title}. {self.tagline}".strip()


class CalibrationResult(BaseModel):
    """The hit@k before/after the audit, with full provenance for the UI caveat."""

    backend: str
    preset_id: str
    n: int
    n_winners: int
    k: int
    hit_at_k_pre_audit: float
    hit_at_k_post_audit: float
    delta: float
    caveat: str


def build_golden_from_devpost(
    winners_path: str | Path,
    submissions_path: str | Path,
    *,
    n_non_winners: int = 37,
) -> list[GoldenEntry]:
    """Build a golden set = all winners + a deterministic sample of non-winners.

    The sample is the first ``n_non_winners`` non-winners by ``software_id`` (sorted)
    so the set is reproducible with no randomness. ``winners_path`` is accepted for
    explicitness but the labels come from ``submissions.json``'s ``is_winner`` flag."""
    _ = winners_path  # labels are taken from submissions.json (is_winner) directly
    subs = json.loads(Path(submissions_path).read_text(encoding="utf-8"))
    winners = [s for s in subs if s.get("is_winner")]
    non_winners = sorted(
        (s for s in subs if not s.get("is_winner")), key=lambda s: str(s["software_id"])
    )[:n_non_winners]
    return [_entry(s) for s in [*winners, *non_winners]]


def _entry(s: dict[str, object]) -> GoldenEntry:
    return GoldenEntry(
        software_id=str(s.get("software_id", "")),
        title=str(s.get("title", "")),
        tagline=str(s.get("tagline", "")),
        placed=bool(s.get("is_winner")),
    )


def load_golden(path: str | Path) -> list[GoldenEntry]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [GoldenEntry.model_validate(e) for e in data]


def hit_at_k(scored: list[tuple[float, bool]], k: int) -> float:
    """Fraction of the top-``k`` highest-scored entries that were actual winners.

    Ties are broken by the input order (stable sort), so the metric is deterministic.
    """
    if k <= 0 or not scored:
        return 0.0
    top = sorted(scored, key=lambda x: x[0], reverse=True)[:k]
    return round(sum(1 for _, placed in top if placed) / k, 4)


async def run_calibration(
    golden: list[GoldenEntry],
    *,
    deps_factory: Callable[[], Deps] | None = None,
    preset_id: str = "rapid-agent",
    k: int = DEFAULT_K,
    backend: str = "mock",
) -> CalibrationResult:
    """Score every golden entry and compute hit@k for the pre- vs post-audit ranking.

    A fresh ``Deps`` per entry gives each submission its own retrieval index. The
    pre-audit ranking uses ``pre_audit_final_score`` (no calibration applied); the
    post-audit ranking uses ``final_score`` — so the delta shows what the audit did
    to the ranking, not just to individual scores."""
    factory = deps_factory or default_deps
    pre: list[tuple[float, bool]] = []
    post: list[tuple[float, bool]] = []
    for entry in golden:
        inp = EvaluationInput(
            rubric_source={"preset_id": preset_id},
            deck_text=entry.deck_text(),
            mode=RunMode.JUDGE,
        )
        record = await run_evaluation(inp, factory())
        pre.append((record.pre_audit_final_score, entry.placed))
        post.append((record.final_score, entry.placed))
    n_winners = sum(1 for e in golden if e.placed)
    hit_pre = hit_at_k(pre, k)
    hit_post = hit_at_k(post, k)
    return CalibrationResult(
        backend=backend,
        preset_id=preset_id,
        n=len(golden),
        n_winners=n_winners,
        k=k,
        hit_at_k_pre_audit=hit_pre,
        hit_at_k_post_audit=hit_post,
        delta=round(hit_post - hit_pre, 4),
        caveat=CAVEAT.format(k=k, n=len(golden), n_winners=n_winners, backend=backend),
    )

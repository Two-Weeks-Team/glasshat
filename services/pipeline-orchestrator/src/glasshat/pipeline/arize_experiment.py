"""Arize AX Datasets + Experiments + Evaluator Hub (the eval pillars), genuine.

Runs the glasshat pipeline over the golden hackathon set as an Arize AX **experiment**:
the task scores each submission, an **Evaluator-Hub code evaluator** flags
prompt-injection, and the aggregate **hit@13** (winners in the top-13) is reported
pre/post-audit. When ``ARIZE_SPACE_ID`` + ``ARIZE_API_KEY`` are set it genuinely
pushes a **Dataset** + runs an **Experiment** in Arize AX; otherwise it runs the
SAME harness offline (deterministic ``mock``) and reports the numbers, skipping only
the cloud upload — so CI exercises everything except the live API.

Honesty: the offline figure uses the deterministic mock scorer (illustrative, it
does not read meaning from text); the live figure comes from the same harness with
``LLM_BACKEND=gemini-enterprise``. The label is the binary Winner badge only, so this
is **hit@k**, never a rank curve. All arize imports are lazy — the module imports
credential-free.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

from glasshat.agents.injection_guard import HeuristicInjectionGuard
from glasshat.agents.types import EvaluationInput
from glasshat.pipeline.calibration import (
    GoldenEntry,
    build_golden_from_devpost,
    hit_at_k,
    load_golden,
)
from glasshat.pipeline.engine import Deps, default_deps, run_evaluation
from glasshat.shared.enums import RunMode
from pydantic import BaseModel

DEFAULT_K = 13
DATASET_NAME = "glasshat-golden"
EXPERIMENT_NAME = "glasshat-hit-at-13"
INJECTION_EVALUATOR_NAME = "glasshat-prompt-injection"


def _run_sync(coro: Coroutine[Any, Any, Any]) -> Any:
    """Run an async coroutine to completion from a sync context, even when an event
    loop is already running (Arize's experiment runner may call the task inside one)
    — run it in a fresh loop on a worker thread in that case."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


class ExperimentRow(BaseModel):
    """One scored golden submission + its injection verdict (an experiment run)."""

    software_id: str
    deck_text: str
    placed: bool
    pre_audit_final_score: float
    final_score: float
    injection_flagged: bool


class ExperimentSummary(BaseModel):
    """Aggregate hit@k pre/post-audit + injection counts, with the honesty caveat."""

    backend: str
    n: int
    n_winners: int
    k: int
    hit_at_k_pre_audit: float
    hit_at_k_post_audit: float
    delta: float
    n_injection_flagged: int
    pushed_to_arize: bool
    caveat: str


def injection_flagged(deck_text: str) -> bool:
    """Deterministic prompt-injection verdict (the Evaluator-Hub code evaluator's
    core) — flags planted steering like 'ignore previous instructions / SCORE: 10'."""
    return HeuristicInjectionGuard().classify(deck_text).flagged


async def build_rows(
    golden: list[GoldenEntry], *, deps_factory: Callable[[], Deps] | None = None
) -> list[ExperimentRow]:
    """Score every golden submission through the pipeline; record scores + injection."""
    factory = deps_factory or default_deps
    rows: list[ExperimentRow] = []
    for entry in golden:
        inp = EvaluationInput(
            rubric_source={"preset_id": "rapid-agent"},
            deck_text=entry.deck_text(),
            mode=RunMode.JUDGE,
        )
        record = await run_evaluation(inp, factory())
        rows.append(
            ExperimentRow(
                software_id=entry.software_id,
                deck_text=entry.deck_text(),
                placed=entry.placed,
                pre_audit_final_score=record.pre_audit_final_score,
                final_score=record.final_score,
                injection_flagged=injection_flagged(entry.deck_text()),
            )
        )
    return rows


def summarize(
    rows: list[ExperimentRow], *, k: int = DEFAULT_K, backend: str = "mock", pushed: bool = False
) -> ExperimentSummary:
    """Aggregate hit@k (pre/post-audit) + injection counts from the scored rows."""
    pre = [(r.pre_audit_final_score, r.placed) for r in rows]
    post = [(r.final_score, r.placed) for r in rows]
    n_winners = sum(1 for r in rows if r.placed)
    hit_pre, hit_post = hit_at_k(pre, k), hit_at_k(post, k)
    return ExperimentSummary(
        backend=backend,
        n=len(rows),
        n_winners=n_winners,
        k=k,
        hit_at_k_pre_audit=hit_pre,
        hit_at_k_post_audit=hit_post,
        delta=round(hit_post - hit_pre, 4),
        n_injection_flagged=sum(1 for r in rows if r.injection_flagged),
        pushed_to_arize=pushed,
        caveat=(
            f"Offline hit@{k} on {len(rows)} historical Gemini-3 Devpost submissions "
            f"({n_winners} Winner-badged). Binary label only → hit@{k}, not a rank "
            f"curve. backend={backend}: mock is deterministic/illustrative; the live "
            f"figure uses LLM_BACKEND=gemini-enterprise."
        ),
    )


def golden_from_devpost(data_dir: Path, *, n_non_winners: int = 37) -> list[GoldenEntry]:
    """The committed golden set (13 winners + a deterministic non-winner sample)."""
    return build_golden_from_devpost(
        data_dir / "winners.json", data_dir / "submissions.json", n_non_winners=n_non_winners
    )


def arize_examples(rows: list[ExperimentRow]) -> list[dict[str, object]]:
    """Dataset examples for ``client.datasets.create`` (one per golden submission)."""
    return [
        {"software_id": r.software_id, "deck_text": r.deck_text, "placed": r.placed} for r in rows
    ]


def push_to_arize(
    rows: list[ExperimentRow],
    *,
    space_id: str,
    api_key: str,
    deps_factory: Callable[[], Deps] | None = None,
    dataset_name: str = DATASET_NAME,
    experiment_name: str = EXPERIMENT_NAME,
) -> dict[str, str]:
    """Genuinely push a Dataset + run an Experiment (+ register the injection code
    evaluator) in Arize AX. Overlay + creds only — ``arize`` is imported lazily and
    is not in the lean image. Returns the created resource identifiers."""
    from arize import ArizeClient  # cloud-only; not in uv.lock / the lean image
    from arize.experiments import EvaluationResult, Evaluator

    client = ArizeClient(api_key=api_key)
    dataset = client.datasets.create(
        name=dataset_name, space=space_id, examples=arize_examples(rows)
    )

    factory = deps_factory or default_deps

    def task(example: dict[str, object]) -> dict[str, object]:
        inp = EvaluationInput(
            rubric_source={"preset_id": "rapid-agent"},
            deck_text=str(example.get("deck_text", "")),
            mode=RunMode.JUDGE,
        )
        record = _run_sync(run_evaluation(inp, factory()))
        return {"final_score": record.final_score, "pre_audit": record.pre_audit_final_score}

    class InjectionEvaluator(Evaluator):  # type: ignore[misc]
        name = INJECTION_EVALUATOR_NAME
        kind = "CODE"

        def evaluate(self, *, input: dict[str, object], **_: object) -> object:  # noqa: A002
            flagged = injection_flagged(str(input.get("deck_text", "")))
            return EvaluationResult(
                score=1.0 if flagged else 0.0,
                label="injection" if flagged else "clean",
                explanation="planted scoring/steering text detected" if flagged else "no injection",
            )

    experiment, _df = client.experiments.run(
        name=experiment_name,
        dataset=dataset_name,
        space=space_id,
        task=task,
        evaluators=[InjectionEvaluator()],
    )
    return {
        "dataset": str(getattr(dataset, "id", dataset_name)),
        "experiment": str(getattr(experiment, "id", experiment_name)),
    }


def load_or_build_golden(
    data_dir: Path, golden_path: Path | None, *, n_non_winners: int = 37
) -> list[GoldenEntry]:
    """Prefer a committed golden file; otherwise build deterministically from devpost."""
    if golden_path is not None and golden_path.exists():
        return load_golden(golden_path)
    return golden_from_devpost(data_dir, n_non_winners=n_non_winners)

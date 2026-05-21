"""In-code hybrid retrieval — the Qdrant replacement.

Dense cosine similarity + sparse BM25 are fused with Reciprocal Rank Fusion
(RRF). Embeddings come from an injected :class:`~glasshat.shared.protocols.LlmClient`
(so this module needs no external vector DB and no credentials). A weight-aware
anchor search ranks past evaluations by cosine of their stored ``weights_vector``,
per ``docs/rubric-synthesis-spec.md`` §8.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity in [-1, 1]; 0.0 if either vector is zero-length."""
    va = np.asarray(a, dtype=float)
    vb = np.asarray(b, dtype=float)
    na = float(np.linalg.norm(va))
    nb = float(np.linalg.norm(vb))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(va, vb) / (na * nb))


def rrf_fuse(rankings: Sequence[Sequence[str]], *, k: int = 60) -> dict[str, float]:
    """Reciprocal Rank Fusion: score(item) = sum 1/(k + rank) over input rankings.

    ``rank`` is 1-based position within each ranking. Items appearing high in
    multiple rankings accumulate the most score.
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank)
    return scores

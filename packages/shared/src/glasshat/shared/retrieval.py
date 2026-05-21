"""In-code hybrid retrieval — the Qdrant replacement.

Dense cosine similarity + sparse BM25 are fused with Reciprocal Rank Fusion
(RRF). Embeddings come from an injected :class:`~glasshat.shared.protocols.LlmClient`
(so this module needs no external vector DB and no credentials). A weight-aware
anchor search ranks past evaluations by cosine of their stored ``weights_vector``,
per ``docs/rubric-synthesis-spec.md`` §8.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from rank_bm25 import BM25Okapi


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


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


@dataclass
class Document:
    """An indexable item: text for sparse, optional dense vector, free-form payload."""

    id: str
    text: str
    vector: list[float] | None = None
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchHit:
    """A retrieval result with its fused score and per-modality ranks."""

    doc: Document
    score: float
    dense_rank: int | None = None
    sparse_rank: int | None = None


class HybridIndex:
    """Dense (cosine) + sparse (BM25) retrieval fused with RRF.

    Implements :class:`~glasshat.shared.protocols.Retrieval`. Embeddings are
    supplied on the documents (produced by an injected ``LlmClient`` upstream);
    this index performs no embedding itself and needs no external service.
    """

    def __init__(self) -> None:
        self._docs: list[Document] = []
        self._bm25: BM25Okapi | None = None

    def index(self, docs: Iterable[Document]) -> None:
        self._docs = list(docs)
        if self._docs:
            self._bm25 = BM25Okapi([_tokenize(d.text) for d in self._docs])
        else:
            self._bm25 = None

    def _dense_ranking(self, query_vector: Sequence[float]) -> list[str]:
        scored = [
            (d.id, cosine_similarity(query_vector, d.vector))
            for d in self._docs
            if d.vector is not None
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [doc_id for doc_id, _ in scored]

    def _sparse_ranking(self, query: str) -> list[str]:
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(_tokenize(query))
        order = sorted(range(len(self._docs)), key=lambda i: scores[i], reverse=True)
        return [self._docs[i].id for i in order]

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        query_vector: Sequence[float] | None = None,
        **kwargs: Any,
    ) -> list[SearchHit]:
        if not self._docs:
            return []
        dense = self._dense_ranking(query_vector) if query_vector is not None else []
        sparse = self._sparse_ranking(query)
        dense_pos = {doc_id: i + 1 for i, doc_id in enumerate(dense)}
        sparse_pos = {doc_id: i + 1 for i, doc_id in enumerate(sparse)}
        fused = rrf_fuse([r for r in (dense, sparse) if r])
        by_id = {d.id: d for d in self._docs}
        ranked = sorted(fused.items(), key=lambda pair: pair[1], reverse=True)
        return [
            SearchHit(
                doc=by_id[doc_id],
                score=score,
                dense_rank=dense_pos.get(doc_id),
                sparse_rank=sparse_pos.get(doc_id),
            )
            for doc_id, score in ranked[:top_k]
        ]

    def weight_aware_anchor(
        self, weights_vector: Sequence[float], *, top_k: int = 3
    ) -> list[SearchHit]:
        """Rank indexed docs by cosine of their payload ``weights_vector`` (spec §8)."""
        scored = [
            (d, cosine_similarity(weights_vector, d.payload["weights_vector"]))
            for d in self._docs
            if "weights_vector" in d.payload
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [SearchHit(doc=d, score=s) for d, s in scored[:top_k]]

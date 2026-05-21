import math

import pytest
from glasshat.shared.protocols import Retrieval
from glasshat.shared.retrieval import (
    Document,
    HybridIndex,
    cosine_similarity,
    rrf_fuse,
)


def test_cosine_identical() -> None:
    assert cosine_similarity([1, 2, 3], [1, 2, 3]) == pytest.approx(1.0)


def test_cosine_orthogonal() -> None:
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)


def test_cosine_known_value() -> None:
    assert cosine_similarity([1, 0], [1, 1]) == pytest.approx(1 / math.sqrt(2))


def test_cosine_zero_vector_is_zero() -> None:
    assert cosine_similarity([0, 0], [1, 1]) == 0.0


def test_rrf_item_in_two_lists_beats_singletons() -> None:
    fused = rrf_fuse([["a", "x"], ["a", "y"]])
    assert fused["a"] > fused["x"]
    assert fused["a"] > fused["y"]


def test_rrf_is_symmetric_for_swapped_lists() -> None:
    fused = rrf_fuse([["a", "b"], ["b", "a"]])
    assert fused["a"] == pytest.approx(fused["b"])


def test_rrf_empty_returns_empty() -> None:
    assert rrf_fuse([]) == {}


def test_hybrid_index_implements_retrieval_protocol() -> None:
    assert isinstance(HybridIndex(), Retrieval)


def test_hybrid_search_combines_dense_and_sparse() -> None:
    idx = HybridIndex()
    idx.index(
        [
            Document(id="both", text="vector database hybrid search", vector=[1.0, 0.0, 0.0]),
            Document(id="dense", text="unrelated words here", vector=[0.9, 0.1, 0.0]),
            Document(id="sparse", text="vector database ranking", vector=[0.0, 1.0, 0.0]),
            Document(id="none", text="nothing relevant at all", vector=[0.0, 0.0, 1.0]),
        ]
    )
    hits = idx.search("vector database", top_k=4, query_vector=[1.0, 0.0, 0.0])
    ids = [h.doc.id for h in hits]
    assert ids[0] == "both"  # strong on BOTH dense and sparse -> RRF #1
    assert set(ids) == {"both", "dense", "sparse", "none"}
    assert hits[0].score >= hits[-1].score


def test_search_empty_index_returns_empty() -> None:
    assert HybridIndex().search("anything", query_vector=[1.0, 0.0]) == []


def test_sparse_only_search_without_query_vector() -> None:
    idx = HybridIndex()
    idx.index(
        [
            Document(id="hit", text="machine learning pipeline"),
            Document(id="miss", text="cooking recipes"),
        ]
    )
    hits = idx.search("machine learning", top_k=2)
    assert hits[0].doc.id == "hit"


def test_weight_aware_anchor_returns_nearest_by_weights() -> None:
    idx = HybridIndex()
    idx.index(
        [
            Document(id="near", text="a", payload={"weights_vector": [0.25, 0.25, 0.25, 0.25]}),
            Document(id="far", text="b", payload={"weights_vector": [0.7, 0.1, 0.1, 0.1]}),
        ]
    )
    hits = idx.weight_aware_anchor([0.25, 0.25, 0.25, 0.25], top_k=1)
    assert len(hits) == 1
    assert hits[0].doc.id == "near"

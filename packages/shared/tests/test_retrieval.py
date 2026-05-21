import math

import pytest
from glasshat.shared.retrieval import cosine_similarity, rrf_fuse


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

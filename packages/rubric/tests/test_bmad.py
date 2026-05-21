from glasshat.rubric.bmad import BMAD_VOCABULARY, is_valid_primitive


def test_seventeen_primitives() -> None:
    assert len(BMAD_VOCABULARY) == 17
    assert set(BMAD_VOCABULARY) >= {"A1", "A4", "B1", "B4", "C1", "C5", "D1", "D4"}


def test_labels_present() -> None:
    assert BMAD_VOCABULARY["C3"] == "testing"
    assert BMAD_VOCABULARY["A1"] == "problem clarity"
    assert BMAD_VOCABULARY["D3"] == "visual polish"


def test_families_are_complete() -> None:
    assert {k for k in BMAD_VOCABULARY if k.startswith("A")} == {"A1", "A2", "A3", "A4"}
    assert {k for k in BMAD_VOCABULARY if k.startswith("B")} == {"B1", "B2", "B3", "B4"}
    assert {k for k in BMAD_VOCABULARY if k.startswith("C")} == {"C1", "C2", "C3", "C4", "C5"}
    assert {k for k in BMAD_VOCABULARY if k.startswith("D")} == {"D1", "D2", "D3", "D4"}


def test_is_valid_primitive() -> None:
    assert is_valid_primitive("C1")
    assert not is_valid_primitive("Z9")
    assert not is_valid_primitive("c1")  # case-sensitive

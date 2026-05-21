import json
from pathlib import Path

import glasshat.rubric.schema as schema_mod
import pytest
from glasshat.rubric.schema import SCHEMA_PATH, schema_matches_disk, synthesized_schema


def test_synthesized_schema_is_a_json_schema() -> None:
    schema = synthesized_schema()
    assert schema["type"] == "object"
    assert "criteria" in schema["properties"]


def test_disk_schema_exists_and_matches_model() -> None:
    assert SCHEMA_PATH.exists(), "run scripts/gen_rubric_schema.py and commit the result"
    disk = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert disk == synthesized_schema(), (
        "synthesized.schema.json is stale — run scripts/gen_rubric_schema.py and commit"
    )
    assert schema_matches_disk()


def test_schema_matches_disk_false_when_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(schema_mod, "SCHEMA_PATH", tmp_path / "absent.json")
    assert schema_mod.schema_matches_disk() is False

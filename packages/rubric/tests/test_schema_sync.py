import json

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

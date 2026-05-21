import json

from glasshat.pipeline.events import PipelineEvent, Stage, sse_line


def test_stage_constants_cover_wow_beats() -> None:
    assert {
        Stage.AUDIT_STARTED,
        Stage.INCONSISTENCY_FLAGGED,
        Stage.PHOENIX_CONSULTATION,
        Stage.ANCHOR_RETRIEVAL,
        Stage.SCORE_CORRECTED,
        Stage.GRAPH_RESHAPE,
    }.issubset(set(Stage))


def test_pipeline_event_defaults_timestamp() -> None:
    e = PipelineEvent(stage=Stage.SCORE_CORRECTED, payload={"hat": "yellow"})
    assert e.ts  # auto timestamp


def test_sse_line_format() -> None:
    e = PipelineEvent(stage=Stage.SCORE_CORRECTED, payload={"hat": "yellow", "to": 7.6})
    line = sse_line(e)
    assert line.startswith("event: score_corrected\n")
    assert line.endswith("\n\n")
    data = line.split("data: ", 1)[1].strip()
    assert json.loads(data)["to"] == 7.6

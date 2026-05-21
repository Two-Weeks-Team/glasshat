from pathlib import Path

import pytest
from glasshat.shared.config import Settings
from glasshat.shared.docstore import MemoryDocStore, SqliteDocStore, get_docstore
from glasshat.shared.protocols import DocStore


def test_memory_is_docstore() -> None:
    assert isinstance(MemoryDocStore(), DocStore)


def test_memory_put_get_missing() -> None:
    s = MemoryDocStore()
    s.put("runs", "r1", {"score": 5, "mode": "judge"})
    assert s.get("runs", "r1") == {"score": 5, "mode": "judge"}
    assert s.get("runs", "missing") is None
    assert s.get("nope", "r1") is None


def test_memory_query_equality_filter() -> None:
    s = MemoryDocStore()
    s.put("runs", "r1", {"mode": "judge"})
    s.put("runs", "r2", {"mode": "participant"})
    assert len(s.query("runs")) == 2
    judge = s.query("runs", mode="judge")
    assert len(judge) == 1 and judge[0]["mode"] == "judge"


def test_sqlite_roundtrip_and_persistence(tmp_path: Path) -> None:
    db = str(tmp_path / "d.db")
    SqliteDocStore(db).put("runs", "r1", {"x": 1, "mode": "judge"})
    reopened = SqliteDocStore(db)  # fresh instance, same file
    assert reopened.get("runs", "r1") == {"x": 1, "mode": "judge"}
    assert reopened.get("runs", "absent") is None


def test_sqlite_query(tmp_path: Path) -> None:
    s = SqliteDocStore(str(tmp_path / "d.db"))
    s.put("c", "a", {"k": "v1"})
    s.put("c", "b", {"k": "v2"})
    assert len(s.query("c")) == 2
    assert s.query("c", k="v1")[0]["k"] == "v1"


def test_get_docstore_memory_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DOCSTORE_BACKEND", raising=False)
    assert isinstance(get_docstore(Settings(_env_file=None)), MemoryDocStore)  # type: ignore[call-arg]


def test_get_docstore_sqlite(tmp_path: Path) -> None:
    s = Settings(  # type: ignore[call-arg]
        _env_file=None,
        docstore_backend="sqlite",
        docstore_sqlite_path=str(tmp_path / "x.db"),
    )
    assert isinstance(get_docstore(s), SqliteDocStore)

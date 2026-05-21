from pathlib import Path

import pytest
from glasshat.shared.blobstore import LocalFsBlobStore, get_blobstore
from glasshat.shared.config import Settings
from glasshat.shared.protocols import BlobStore


def test_localfs_is_blobstore(tmp_path: Path) -> None:
    assert isinstance(LocalFsBlobStore(str(tmp_path)), BlobStore)


def test_localfs_put_get_roundtrip(tmp_path: Path) -> None:
    store = LocalFsBlobStore(str(tmp_path))
    ref = store.put_blob("runs/r1/deck.pdf", b"hello world")
    assert isinstance(ref, str) and ref.startswith("file://")
    assert store.get_blob("runs/r1/deck.pdf") == b"hello world"


def test_localfs_get_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        LocalFsBlobStore(str(tmp_path)).get_blob("absent.bin")


def test_get_blobstore_localfs_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("BLOB_BACKEND", raising=False)
    s = Settings(_env_file=None, blob_local_dir=str(tmp_path))  # type: ignore[call-arg]
    assert isinstance(get_blobstore(s), LocalFsBlobStore)

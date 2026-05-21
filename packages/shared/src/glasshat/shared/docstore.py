"""Document persistence behind the ``DocStore`` protocol.

``memory`` (default, tests) and ``sqlite`` (local file) are complete stdlib
implementations. ``firestore`` lazily imports the Google SDK and is selected for
cloud deployment. All three store free-form JSON documents keyed by
``(collection, doc_id)`` and support equality-filtered queries.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Mapping
from typing import Any

from glasshat.shared.config import Settings, get_settings


def _matches(doc: Mapping[str, Any], filters: Mapping[str, Any]) -> bool:
    return all(doc.get(key) == value for key, value in filters.items())


class MemoryDocStore:
    """In-process dict-backed document store."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, dict[str, Any]]] = {}

    def get(self, collection: str, doc_id: str) -> Mapping[str, Any] | None:
        return self._data.get(collection, {}).get(doc_id)

    def put(self, collection: str, doc_id: str, doc: Mapping[str, Any]) -> None:
        self._data.setdefault(collection, {})[doc_id] = dict(doc)

    def query(self, collection: str, **filters: Any) -> list[Mapping[str, Any]]:
        docs = self._data.get(collection, {}).values()
        return [d for d in docs if _matches(d, filters)]


class SqliteDocStore:
    """SQLite-backed document store (JSON body, persists to disk)."""

    def __init__(self, path: str) -> None:
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS docs ("
            "collection TEXT, doc_id TEXT, body TEXT, PRIMARY KEY (collection, doc_id))"
        )
        self._conn.commit()

    def get(self, collection: str, doc_id: str) -> Mapping[str, Any] | None:
        row = self._conn.execute(
            "SELECT body FROM docs WHERE collection = ? AND doc_id = ?", (collection, doc_id)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def put(self, collection: str, doc_id: str, doc: Mapping[str, Any]) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO docs (collection, doc_id, body) VALUES (?, ?, ?)",
            (collection, doc_id, json.dumps(dict(doc))),
        )
        self._conn.commit()

    def query(self, collection: str, **filters: Any) -> list[Mapping[str, Any]]:
        rows = self._conn.execute(
            "SELECT body FROM docs WHERE collection = ?", (collection,)
        ).fetchall()
        docs = [json.loads(r[0]) for r in rows]
        return [d for d in docs if _matches(d, filters)]


class FirestoreDocStore:  # pragma: no cover - requires the firestore extra + GCP
    """Firestore-backed document store for cloud deployment."""

    def __init__(self, settings: Settings | None = None) -> None:
        from google.cloud import firestore

        settings = settings or get_settings()
        project = settings.firestore_project_id or settings.google_cloud_project
        self._db = firestore.Client(project=project)

    def get(self, collection: str, doc_id: str) -> Mapping[str, Any] | None:
        snap = self._db.collection(collection).document(doc_id).get()
        return snap.to_dict() if snap.exists else None

    def put(self, collection: str, doc_id: str, doc: Mapping[str, Any]) -> None:
        self._db.collection(collection).document(doc_id).set(dict(doc))

    def query(self, collection: str, **filters: Any) -> list[Mapping[str, Any]]:
        ref: Any = self._db.collection(collection)
        for key, value in filters.items():
            ref = ref.where(key, "==", value)
        return [doc.to_dict() for doc in ref.stream()]


def get_docstore(settings: Settings | None = None) -> DocStoreImpl:
    """Return the configured document store (``memory`` default)."""
    settings = settings or get_settings()
    if settings.docstore_backend == "sqlite":
        return SqliteDocStore(settings.docstore_sqlite_path)
    if settings.docstore_backend == "firestore":
        return FirestoreDocStore(settings)
    return MemoryDocStore()


DocStoreImpl = MemoryDocStore | SqliteDocStore | FirestoreDocStore

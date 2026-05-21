"""Binary blob persistence behind the ``BlobStore`` protocol.

``local-fs`` (default, dev/tests) writes under a base directory and returns a
``file://`` URI. ``gcs`` lazily imports the Google SDK for cloud deployment and
returns a ``gs://`` URI. Keys may contain ``/`` to namespace by run/submission.
"""

from __future__ import annotations

from pathlib import Path

from glasshat.shared.config import Settings, get_settings


class LocalFsBlobStore:
    """Filesystem blob store rooted at ``base_dir``."""

    def __init__(self, base_dir: str) -> None:
        self._base = Path(base_dir)

    def put_blob(self, key: str, data: bytes) -> str:
        path = self._base / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path.resolve().as_uri()

    def get_blob(self, key: str) -> bytes:
        return (self._base / key).read_bytes()


class GcsBlobStore:  # pragma: no cover - requires the gcs extra + GCP
    """Cloud Storage blob store."""

    def __init__(self, bucket: str, settings: Settings | None = None) -> None:
        from google.cloud import storage

        settings = settings or get_settings()
        self._bucket = storage.Client(project=settings.google_cloud_project).bucket(bucket)

    def put_blob(self, key: str, data: bytes) -> str:
        self._bucket.blob(key).upload_from_string(data)
        return f"gs://{self._bucket.name}/{key}"

    def get_blob(self, key: str) -> bytes:
        return bytes(self._bucket.blob(key).download_as_bytes())


def get_blobstore(settings: Settings | None = None) -> LocalFsBlobStore | GcsBlobStore:
    """Return the configured blob store (``local-fs`` default)."""
    settings = settings or get_settings()
    if settings.blob_backend == "gcs":
        return GcsBlobStore(settings.gcs_uploads_bucket, settings)  # pragma: no cover
    return LocalFsBlobStore(settings.blob_local_dir)

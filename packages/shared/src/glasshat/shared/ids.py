"""Deterministic identity helpers: canonical JSON, SHA-256, UUIDv4.

Canonicalization is the basis for ``rubric_schema_hash`` (see
:mod:`glasshat.rubric.canonical`): the same logical object must always
serialize to the same bytes regardless of key insertion order.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any


def canonical_json(obj: Any) -> str:
    """Serialize ``obj`` to a stable, compact JSON string (sorted keys, no spaces)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(text: str) -> str:
    """Return the hex SHA-256 digest of ``text`` (UTF-8)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def new_uuid() -> str:
    """Return a fresh random UUIDv4 as a string."""
    return str(uuid.uuid4())

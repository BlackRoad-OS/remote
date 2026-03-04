"""Fast file checksumming for change detection."""

from __future__ import annotations

import hashlib
from pathlib import Path

BLOCK_SIZE = 65536


def hash_file(path: Path, algorithm: str = "sha256") -> str:
    """Return hex digest of a file using the given hash algorithm."""
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while True:
            block = f.read(BLOCK_SIZE)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def hash_bytes(data: bytes, algorithm: str = "sha256") -> str:
    """Return hex digest of raw bytes."""
    return hashlib.new(algorithm, data).hexdigest()

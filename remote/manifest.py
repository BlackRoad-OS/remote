"""Directory manifest — a snapshot of every file's metadata and checksum."""

from __future__ import annotations

import json
import os
import stat
from dataclasses import asdict, dataclass
from pathlib import Path

from remote.checksum import hash_file


@dataclass(frozen=True, order=True)
class FileEntry:
    """Metadata for a single file inside a sync root."""

    rel_path: str
    size: int
    mtime_ns: int
    checksum: str
    mode: int


def scan_directory(root: Path, algorithm: str = "sha256") -> list[FileEntry]:
    """Walk *root* recursively and return a sorted list of FileEntry objects.

    Symlinks are skipped. Hidden files (starting with ``"."``) are included.
    """
    root = root.resolve()
    entries: list[FileEntry] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fname in filenames:
            full = Path(dirpath) / fname
            if full.is_symlink():
                continue
            st = full.stat()
            if not stat.S_ISREG(st.st_mode):
                continue
            rel = str(full.relative_to(root))
            entries.append(
                FileEntry(
                    rel_path=rel,
                    size=st.st_size,
                    mtime_ns=st.st_mtime_ns,
                    checksum=hash_file(full, algorithm),
                    mode=st.st_mode,
                )
            )
    entries.sort()
    return entries


def manifest_to_json(entries: list[FileEntry]) -> str:
    """Serialize a manifest to a JSON string."""
    return json.dumps([asdict(e) for e in entries], indent=2)


def manifest_from_json(text: str) -> list[FileEntry]:
    """Deserialize a manifest from a JSON string."""
    return sorted(FileEntry(**obj) for obj in json.loads(text))

"""Compute the difference between two manifests."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from remote.manifest import FileEntry


class ChangeKind(Enum):
    ADDED = auto()
    DELETED = auto()
    MODIFIED = auto()


@dataclass(frozen=True)
class Change:
    kind: ChangeKind
    rel_path: str
    source_entry: FileEntry | None = None
    target_entry: FileEntry | None = None


def diff_manifests(
    source: list[FileEntry],
    target: list[FileEntry],
) -> list[Change]:
    """Compare *source* (what we have) to *target* (what we want).

    Returns a list of :class:`Change` objects describing what must happen to
    make *source* match *target*.

    - ADDED   → file exists in target but not source (needs copy)
    - DELETED → file exists in source but not target (needs removal)
    - MODIFIED → file exists in both but checksum differs (needs update)
    """
    src_map = {e.rel_path: e for e in source}
    tgt_map = {e.rel_path: e for e in target}

    changes: list[Change] = []

    all_paths = sorted(set(src_map) | set(tgt_map))
    for p in all_paths:
        in_src = p in src_map
        in_tgt = p in tgt_map
        if in_tgt and not in_src:
            changes.append(Change(ChangeKind.ADDED, p, target_entry=tgt_map[p]))
        elif in_src and not in_tgt:
            changes.append(Change(ChangeKind.DELETED, p, source_entry=src_map[p]))
        elif src_map[p].checksum != tgt_map[p].checksum:
            changes.append(
                Change(
                    ChangeKind.MODIFIED,
                    p,
                    source_entry=src_map[p],
                    target_entry=tgt_map[p],
                )
            )

    return changes

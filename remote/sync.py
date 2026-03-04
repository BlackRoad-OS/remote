"""Core sync engine — applies a diff to make source match target."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from remote.diff import Change, ChangeKind, diff_manifests
from remote.manifest import FileEntry, scan_directory


@dataclass
class SyncResult:
    """Summary of a sync operation."""

    copied: list[str]
    deleted: list[str]
    updated: list[str]
    errors: list[str]

    @property
    def total_changes(self) -> int:
        return len(self.copied) + len(self.deleted) + len(self.updated)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def sync(
    source_root: Path,
    target_root: Path,
    *,
    delete: bool = False,
) -> SyncResult:
    """One-way sync: make *source_root* match *target_root*.

    Files present in *target_root* but missing from *source_root* are copied.
    Files modified in *target_root* overwrite those in *source_root*.
    If *delete* is True, files in *source_root* not in *target_root* are removed.

    Returns a :class:`SyncResult` summarising what happened.
    """
    source_root = Path(source_root).resolve()
    target_root = Path(target_root).resolve()

    src_manifest = scan_directory(source_root) if source_root.exists() else []
    tgt_manifest = scan_directory(target_root)

    changes = diff_manifests(src_manifest, tgt_manifest)

    result = SyncResult(copied=[], deleted=[], updated=[], errors=[])

    for change in changes:
        try:
            _apply_change(change, source_root, target_root, delete, result)
        except Exception as exc:
            result.errors.append(f"{change.rel_path}: {exc}")

    return result


def _apply_change(
    change: Change,
    source_root: Path,
    target_root: Path,
    delete: bool,
    result: SyncResult,
) -> None:
    src_path = source_root / change.rel_path
    tgt_path = target_root / change.rel_path

    if change.kind is ChangeKind.ADDED:
        src_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tgt_path, src_path)
        result.copied.append(change.rel_path)

    elif change.kind is ChangeKind.MODIFIED:
        src_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tgt_path, src_path)
        result.updated.append(change.rel_path)

    elif change.kind is ChangeKind.DELETED:
        if delete:
            src_path.unlink()
            # Remove empty parent directories up to source_root
            parent = src_path.parent
            while parent != source_root:
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent
            result.deleted.append(change.rel_path)

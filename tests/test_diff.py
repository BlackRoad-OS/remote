"""Tests for remote.diff."""

from remote.diff import Change, ChangeKind, diff_manifests
from remote.manifest import FileEntry


def _entry(path: str, checksum: str = "aaa", size: int = 10) -> FileEntry:
    return FileEntry(rel_path=path, size=size, mtime_ns=0, checksum=checksum, mode=0o100644)


class TestDiffManifests:
    def test_identical(self):
        m = [_entry("a.txt")]
        assert diff_manifests(m, m) == []

    def test_added(self):
        source: list[FileEntry] = []
        target = [_entry("new.txt")]
        changes = diff_manifests(source, target)
        assert len(changes) == 1
        assert changes[0].kind is ChangeKind.ADDED
        assert changes[0].rel_path == "new.txt"

    def test_deleted(self):
        source = [_entry("old.txt")]
        target: list[FileEntry] = []
        changes = diff_manifests(source, target)
        assert len(changes) == 1
        assert changes[0].kind is ChangeKind.DELETED
        assert changes[0].rel_path == "old.txt"

    def test_modified(self):
        source = [_entry("f.txt", checksum="old")]
        target = [_entry("f.txt", checksum="new")]
        changes = diff_manifests(source, target)
        assert len(changes) == 1
        assert changes[0].kind is ChangeKind.MODIFIED

    def test_mixed_changes(self):
        source = [
            _entry("keep.txt", checksum="same"),
            _entry("modify.txt", checksum="v1"),
            _entry("remove.txt"),
        ]
        target = [
            _entry("add.txt"),
            _entry("keep.txt", checksum="same"),
            _entry("modify.txt", checksum="v2"),
        ]
        changes = diff_manifests(source, target)
        kinds = {c.rel_path: c.kind for c in changes}
        assert kinds == {
            "add.txt": ChangeKind.ADDED,
            "modify.txt": ChangeKind.MODIFIED,
            "remove.txt": ChangeKind.DELETED,
        }
        # keep.txt should NOT appear
        assert "keep.txt" not in kinds

    def test_empty_to_empty(self):
        assert diff_manifests([], []) == []

    def test_same_path_same_checksum_no_change(self):
        e = _entry("x.txt", checksum="abc")
        assert diff_manifests([e], [e]) == []

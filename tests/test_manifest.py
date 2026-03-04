"""Tests for remote.manifest."""

import json
from pathlib import Path

from remote.manifest import FileEntry, manifest_from_json, manifest_to_json, scan_directory


class TestScanDirectory:
    def test_empty_directory(self, tmp_path: Path):
        entries = scan_directory(tmp_path)
        assert entries == []

    def test_single_file(self, tmp_path: Path):
        (tmp_path / "a.txt").write_text("hello")
        entries = scan_directory(tmp_path)
        assert len(entries) == 1
        assert entries[0].rel_path == "a.txt"
        assert entries[0].size == 5

    def test_nested_files(self, tmp_path: Path):
        sub = tmp_path / "sub" / "deep"
        sub.mkdir(parents=True)
        (tmp_path / "root.txt").write_text("r")
        (sub / "nested.txt").write_text("n")
        entries = scan_directory(tmp_path)
        paths = [e.rel_path for e in entries]
        assert "root.txt" in paths
        assert "sub/deep/nested.txt" in paths

    def test_sorted_output(self, tmp_path: Path):
        for name in ["c.txt", "a.txt", "b.txt"]:
            (tmp_path / name).write_text(name)
        entries = scan_directory(tmp_path)
        paths = [e.rel_path for e in entries]
        assert paths == sorted(paths)

    def test_skips_symlinks(self, tmp_path: Path):
        real = tmp_path / "real.txt"
        real.write_text("real")
        link = tmp_path / "link.txt"
        link.symlink_to(real)
        entries = scan_directory(tmp_path)
        assert len(entries) == 1
        assert entries[0].rel_path == "real.txt"

    def test_hidden_files_included(self, tmp_path: Path):
        (tmp_path / ".hidden").write_text("secret")
        entries = scan_directory(tmp_path)
        assert len(entries) == 1
        assert entries[0].rel_path == ".hidden"

    def test_checksum_changes_with_content(self, tmp_path: Path):
        f = tmp_path / "file.txt"
        f.write_text("version 1")
        e1 = scan_directory(tmp_path)
        f.write_text("version 2")
        e2 = scan_directory(tmp_path)
        assert e1[0].checksum != e2[0].checksum


class TestManifestSerialization:
    def test_roundtrip(self, tmp_path: Path):
        (tmp_path / "a.txt").write_text("aaa")
        (tmp_path / "b.txt").write_text("bbb")
        original = scan_directory(tmp_path)
        serialized = manifest_to_json(original)
        restored = manifest_from_json(serialized)
        assert original == restored

    def test_json_format(self, tmp_path: Path):
        (tmp_path / "x.txt").write_text("x")
        entries = scan_directory(tmp_path)
        text = manifest_to_json(entries)
        parsed = json.loads(text)
        assert isinstance(parsed, list)
        assert "rel_path" in parsed[0]
        assert "checksum" in parsed[0]

    def test_empty_manifest_roundtrip(self):
        text = manifest_to_json([])
        assert manifest_from_json(text) == []

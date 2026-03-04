"""Tests for remote.sync — full integration / e2e tests."""

from pathlib import Path

from remote.sync import sync


class TestSync:
    def test_sync_new_files(self, tmp_path: Path):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        (tgt / "a.txt").write_text("alpha")
        (tgt / "b.txt").write_text("bravo")

        result = sync(src, tgt)

        assert result.ok
        assert set(result.copied) == {"a.txt", "b.txt"}
        assert (src / "a.txt").read_text() == "alpha"
        assert (src / "b.txt").read_text() == "bravo"

    def test_sync_updates_modified(self, tmp_path: Path):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        (src / "f.txt").write_text("old")
        (tgt / "f.txt").write_text("new")

        result = sync(src, tgt)

        assert result.ok
        assert result.updated == ["f.txt"]
        assert (src / "f.txt").read_text() == "new"

    def test_sync_no_delete_by_default(self, tmp_path: Path):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        (src / "extra.txt").write_text("should stay")

        result = sync(src, tgt)

        assert result.ok
        assert result.deleted == []
        assert (src / "extra.txt").exists()

    def test_sync_delete_flag(self, tmp_path: Path):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        (src / "gone.txt").write_text("bye")

        result = sync(src, tgt, delete=True)

        assert result.ok
        assert result.deleted == ["gone.txt"]
        assert not (src / "gone.txt").exists()

    def test_sync_nested_directories(self, tmp_path: Path):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        deep = tgt / "a" / "b" / "c"
        deep.mkdir(parents=True)
        (deep / "deep.txt").write_text("deep")

        result = sync(src, tgt)

        assert result.ok
        assert (src / "a" / "b" / "c" / "deep.txt").read_text() == "deep"

    def test_sync_already_in_sync(self, tmp_path: Path):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        (src / "same.txt").write_text("identical")
        (tgt / "same.txt").write_text("identical")

        result = sync(src, tgt)

        assert result.ok
        assert result.total_changes == 0

    def test_sync_source_does_not_exist(self, tmp_path: Path):
        src = tmp_path / "nonexistent"
        tgt = tmp_path / "tgt"
        tgt.mkdir()
        (tgt / "file.txt").write_text("data")

        result = sync(src, tgt)

        assert result.ok
        assert result.copied == ["file.txt"]
        assert (src / "file.txt").read_text() == "data"

    def test_sync_mixed_operations(self, tmp_path: Path):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        # file to keep (identical)
        (src / "keep.txt").write_text("same")
        (tgt / "keep.txt").write_text("same")
        # file to update
        (src / "update.txt").write_text("old")
        (tgt / "update.txt").write_text("new")
        # file to add
        (tgt / "new.txt").write_text("fresh")
        # file to delete
        (src / "stale.txt").write_text("remove me")

        result = sync(src, tgt, delete=True)

        assert result.ok
        assert result.copied == ["new.txt"]
        assert result.updated == ["update.txt"]
        assert result.deleted == ["stale.txt"]
        assert (src / "keep.txt").read_text() == "same"
        assert (src / "update.txt").read_text() == "new"
        assert (src / "new.txt").read_text() == "fresh"
        assert not (src / "stale.txt").exists()


class TestSyncResult:
    def test_total_changes(self, tmp_path: Path):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        (tgt / "a.txt").write_text("a")
        result = sync(src, tgt)
        assert result.total_changes == 1

    def test_ok_property(self, tmp_path: Path):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        result = sync(src, tgt)
        assert result.ok is True

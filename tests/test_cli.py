"""Tests for remote.cli."""

from pathlib import Path

from remote.cli import main


class TestCLI:
    def test_no_args_returns_zero(self):
        assert main([]) == 0

    def test_sync_basic(self, tmp_path: Path):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        (tgt / "file.txt").write_text("data")

        rc = main(["sync", str(src), str(tgt)])

        assert rc == 0
        assert (src / "file.txt").read_text() == "data"

    def test_sync_with_delete(self, tmp_path: Path):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        (src / "orphan.txt").write_text("bye")

        rc = main(["sync", str(src), str(tgt), "--delete"])

        assert rc == 0
        assert not (src / "orphan.txt").exists()

    def test_sync_already_in_sync(self, tmp_path: Path, capsys):
        src = tmp_path / "src"
        tgt = tmp_path / "tgt"
        src.mkdir()
        tgt.mkdir()
        (src / "f.txt").write_text("same")
        (tgt / "f.txt").write_text("same")

        rc = main(["sync", str(src), str(tgt)])
        captured = capsys.readouterr()

        assert rc == 0
        assert "Already in sync" in captured.out

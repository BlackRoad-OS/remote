"""Tests for remote.checksum."""

import hashlib
import tempfile
from pathlib import Path

from remote.checksum import hash_bytes, hash_file


class TestHashFile:
    def test_empty_file(self, tmp_path: Path):
        f = tmp_path / "empty"
        f.write_bytes(b"")
        assert hash_file(f) == hashlib.sha256(b"").hexdigest()

    def test_small_file(self, tmp_path: Path):
        data = b"hello world"
        f = tmp_path / "hello.txt"
        f.write_bytes(data)
        assert hash_file(f) == hashlib.sha256(data).hexdigest()

    def test_large_file(self, tmp_path: Path):
        """File larger than BLOCK_SIZE (64 KiB)."""
        data = b"x" * 200_000
        f = tmp_path / "big"
        f.write_bytes(data)
        assert hash_file(f) == hashlib.sha256(data).hexdigest()

    def test_md5_algorithm(self, tmp_path: Path):
        data = b"test data"
        f = tmp_path / "md5"
        f.write_bytes(data)
        assert hash_file(f, algorithm="md5") == hashlib.md5(data).hexdigest()

    def test_deterministic(self, tmp_path: Path):
        data = b"determinism check"
        f = tmp_path / "det"
        f.write_bytes(data)
        assert hash_file(f) == hash_file(f)


class TestHashBytes:
    def test_basic(self):
        assert hash_bytes(b"abc") == hashlib.sha256(b"abc").hexdigest()

    def test_empty(self):
        assert hash_bytes(b"") == hashlib.sha256(b"").hexdigest()

    def test_md5(self):
        assert hash_bytes(b"abc", "md5") == hashlib.md5(b"abc").hexdigest()

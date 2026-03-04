# remote

Offline-first file sync for BlackRoad OS.

**Status:** v0.1.0 — core sync engine working, 39/39 tests passing.

## What's Working (as of 2026-03-04)

| Feature | Status | Tests |
|---|---|---|
| SHA-256 file checksumming | Working | 8/8 |
| Directory manifest (scan, serialize, deserialize) | Working | 10/10 |
| Manifest diffing (added, deleted, modified detection) | Working | 7/7 |
| One-way file sync (copy new, update modified) | Working | 10/10 |
| Sync with `--delete` (remove orphaned files) | Working | included above |
| Nested directory sync | Working | included above |
| CLI (`remote sync`) | Working | 4/4 |

### Core Modules

- **`remote.checksum`** — SHA-256 (or configurable) file hashing for change detection
- **`remote.manifest`** — Scan a directory tree into a sorted list of file entries (path, size, mtime, checksum, mode); serialize/deserialize to JSON
- **`remote.diff`** — Compare two manifests and produce a changeset (ADDED, DELETED, MODIFIED)
- **`remote.sync`** — Apply a diff to make a source directory match a target; supports `--delete` to remove orphaned files
- **`remote.cli`** — Command-line interface

## Install

```
pip install -e .
```

## Usage

```bash
# Sync target directory into source (one-way)
remote sync ./local ./authoritative

# Sync with deletion of orphaned files
remote sync ./local ./authoritative --delete
```

## Run Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## License

BlackRoad OS, Inc. Proprietary Software License.

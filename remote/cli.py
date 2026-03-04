"""Minimal CLI for remote sync."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from remote.sync import sync


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="remote",
        description="Offline-first file sync for BlackRoad OS",
    )
    sub = parser.add_subparsers(dest="command")

    sync_p = sub.add_parser("sync", help="Sync files from target into source")
    sync_p.add_argument("source", type=Path, help="Local directory to update")
    sync_p.add_argument("target", type=Path, help="Authoritative directory to sync from")
    sync_p.add_argument(
        "--delete",
        action="store_true",
        help="Remove files in source that are not in target",
    )

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "sync":
        result = sync(args.source, args.target, delete=args.delete)

        if result.copied:
            print(f"Copied  ({len(result.copied)}):")
            for p in result.copied:
                print(f"  + {p}")
        if result.updated:
            print(f"Updated ({len(result.updated)}):")
            for p in result.updated:
                print(f"  ~ {p}")
        if result.deleted:
            print(f"Deleted ({len(result.deleted)}):")
            for p in result.deleted:
                print(f"  - {p}")
        if result.errors:
            print(f"Errors  ({len(result.errors)}):")
            for e in result.errors:
                print(f"  ! {e}")

        if result.total_changes == 0 and result.ok:
            print("Already in sync.")

        return 0 if result.ok else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

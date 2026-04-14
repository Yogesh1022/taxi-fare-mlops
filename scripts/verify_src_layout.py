"""Verify src-layout package markers and import resolution.

Usage:
    python scripts/verify_src_layout.py
    python scripts/verify_src_layout.py --check-imports
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Iterable

DEFAULT_MODULES = ("data", "features", "models", "deployment", "utils")


def find_missing_init_files(src_root: pathlib.Path) -> list[pathlib.Path]:
    """Return package directories that contain .py files but no __init__.py."""
    missing: list[pathlib.Path] = []
    for directory in src_root.rglob("*"):
        if not directory.is_dir() or directory.name == "__pycache__":
            continue

        has_py_files = any(item.is_file() and item.suffix == ".py" for item in directory.iterdir())
        if has_py_files and not (directory / "__init__.py").exists():
            missing.append(directory)

    return missing


def verify_imports(src_root: pathlib.Path, modules: Iterable[str]) -> None:
    """Import top-level modules expected to be available from src layout."""
    sys.path.insert(0, str(src_root.resolve()))
    for module in modules:
        __import__(module)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify src layout package integrity")
    parser.add_argument("--src", default="src", help="Path to src directory")
    parser.add_argument(
        "--check-imports",
        action="store_true",
        help="Also import expected top-level modules from src",
    )
    parser.add_argument(
        "--modules",
        nargs="*",
        default=list(DEFAULT_MODULES),
        help="Top-level modules to import when --check-imports is enabled",
    )
    args = parser.parse_args()

    src_root = pathlib.Path(args.src)
    if not src_root.exists() or not src_root.is_dir():
        print(f"ERROR: src directory not found: {src_root}")
        return 1

    missing = find_missing_init_files(src_root)
    if missing:
        print("Missing __init__.py in package directories:")
        for path in sorted(missing):
            print(f" - {path}")
        return 1

    if args.check_imports:
        try:
            verify_imports(src_root, args.modules)
        except Exception as exc:
            print(f"Import verification failed: {exc}")
            return 1

    print("src package structure verified.")
    if args.check_imports:
        print("Top-level module imports verified.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

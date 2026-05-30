#!/usr/bin/env python3
"""Produce dist/anki_flash_feedback.ankiaddon from src/anki_flash_feedback/.

AnkiWeb rules enforced here:
- __init__.py must be at the zip root (no top-level folder).
- Exclude __pycache__/, *.pyc, meta.json.
"""

import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SRC_DIR = REPO_ROOT / "src" / "anki_flash_feedback"
DIST_DIR = REPO_ROOT / "dist"

_EXCLUDE_SUFFIXES = {".pyc"}
_EXCLUDE_DIRS = {"__pycache__"}
_EXCLUDE_FILES = {"meta.json"}


def _include(rel: Path) -> bool:
    if rel.name in _EXCLUDE_FILES:
        return False
    if rel.suffix in _EXCLUDE_SUFFIXES:
        return False
    return not any(part in _EXCLUDE_DIRS for part in rel.parts)


def build() -> None:
    DIST_DIR.mkdir(exist_ok=True)
    out = DIST_DIR / "anki_flash_feedback.ankiaddon"

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fpath in sorted(SRC_DIR.rglob("*")):
            if not fpath.is_file():
                continue
            rel = fpath.relative_to(SRC_DIR)
            if not _include(rel):
                continue
            zf.write(fpath, rel)
            print(f"  + {rel}")

    print(f"\nBuilt: {out}")


if __name__ == "__main__":
    build()

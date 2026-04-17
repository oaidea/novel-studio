#!/usr/bin/env python3
"""
index_refresh.py

Planned purpose:
- refresh active indexes under .novel-studio/indexes/
- provide stable low-token entrypoints for next-chapter planning

Current state:
- scaffold placeholder only
"""

from pathlib import Path
import sys

INDEX_FILES = [
    "active-characters.md",
    "active-events.md",
    "active-spaces.md",
    "active-scenes.md",
    "pending-foreshadowing.md",
]


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: index_refresh.py <project-dir>")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    idx_dir = root / ".novel-studio" / "indexes"
    idx_dir.mkdir(parents=True, exist_ok=True)

    for name in INDEX_FILES:
        target = idx_dir / name
        if not target.exists():
            heading = name.replace('.md', '').replace('-', ' ')
            target.write_text(f"# {heading}\n\n- 待刷新\n")

    print(f"prepared index scaffolds under: {idx_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

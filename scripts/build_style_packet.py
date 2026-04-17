#!/usr/bin/env python3
"""
build_style_packet.py

Planned purpose:
- generate a style overlay scaffold for a chapter
- link a chapter packet to project-level mother style

Current state:
- scaffold placeholder only
"""

from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) < 4:
        print("usage: build_style_packet.py <project-dir> <chapter-id> <project-style-card-path>")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    chapter_id = sys.argv[2]
    style_card = sys.argv[3]

    out = root / ".novel-studio" / "packets" / f"{chapter_id}-style-overlay.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    if not out.exists():
        out.write_text(
            f"# {chapter_id} 风格调用说明\n\n"
            f"- 继承的项目风格卡：`{style_card}`\n"
            "- 本章局部风格偏移：\n"
            "- 本章不可偏离的母风格底线：\n"
        )

    print(f"prepared chapter style overlay scaffold: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

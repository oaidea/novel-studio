#!/usr/bin/env python3
"""
build_input_pack.py

Build a chapter-scoped minimal input pack list from the current packet-first
artifacts so the chapter can be written with a smaller, clearer context set.
"""

from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: build_input_pack.py <project-dir> <chapter-id>")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    chapter_id = sys.argv[2]

    summary = root / ".novel-studio" / "summaries" / f"{chapter_id}-summary.md"
    packet = root / ".novel-studio" / "packets" / f"{chapter_id}-packet.md"
    style_overlay = root / ".novel-studio" / "packets" / f"{chapter_id}-style-overlay.md"
    object_summary = root / ".novel-studio" / "summaries" / f"{chapter_id}-objects.md"
    indexes = root / ".novel-studio" / "indexes"
    out = root / ".novel-studio" / "logs" / f"{chapter_id}-input-pack.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = [f"# {chapter_id} 最小输入包", "", "## 必带（核心输入层）", ""]
    for path in [summary, packet, style_overlay, object_summary]:
        lines.append(f"- `{path.relative_to(root)}`")

    lines += ["", "## 推荐带（增强上下文层）", ""]
    added = False
    for name in ["active-characters.md", "active-events.md", "active-spaces.md", "active-scenes.md", "pending-foreshadowing.md"]:
        idx = indexes / name
        if idx.exists():
            lines.append(f"- `{idx.relative_to(root)}`")
            added = True
    if not added:
        lines.append("- 暂无活动索引文件")

    lines += ["", "## 一句话说明", "- 这一包的目标是：不依赖前文章节全文，也能启动当前章正文写作。", ""]
    out.write_text("\n".join(lines))
    print(f"prepared input pack file: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

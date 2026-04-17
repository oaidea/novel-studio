#!/usr/bin/env python3
"""
build_object_state_summary.py

Create a chapter-scoped object state summary scaffold based on packet object lists.
"""

from pathlib import Path
import sys


SECTIONS = ["人物", "事件", "空间", "场景"]


def extract_items(packet: Path, section_name: str):
    if not packet.exists():
        return []
    lines = packet.read_text().splitlines()
    items = []
    capture = False
    for line in lines:
        stripped = line.strip()
        if stripped == f"### {section_name}":
            capture = True
            continue
        if capture and stripped.startswith("### "):
            break
        if capture and stripped.startswith("- "):
            item = stripped[2:].strip()
            if item:
                items.append(item)
    return items


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: build_object_state_summary.py <project-dir> <chapter-id>")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    chapter_id = sys.argv[2]
    packet = root / ".novel-studio" / "packets" / f"{chapter_id}-packet.md"
    out = root / ".novel-studio" / "summaries" / f"{chapter_id}-objects.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    chars = extract_items(packet, "人物")
    events = extract_items(packet, "事件")
    spaces = extract_items(packet, "空间")
    scenes = extract_items(packet, "场景")

    lines = [f"# {chapter_id} 对象状态摘要", ""]
    lines += ["## 一、相关人物当前状态", ""]
    lines += [f"- {x}：" for x in chars] if chars else ["- "]
    lines += ["", "## 二、相关事件当前状态", ""]
    lines += [f"- {x}：" for x in events] if events else ["- "]
    lines += ["", "## 三、相关空间当前状态", ""]
    lines += [f"- {x}：" for x in spaces] if spaces else ["- "]
    lines += ["", "## 四、相关场景当前状态", ""]
    lines += [f"- {x}：" for x in scenes] if scenes else ["- "]
    lines += ["", "## 五、这一章最该记住的对象约束", "- ", "- ", "- ", ""]

    out.write_text("\n".join(lines))
    print(f"prepared object state summary scaffold: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

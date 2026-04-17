#!/usr/bin/env python3
"""
build_object_state_summary.py

Create a chapter-scoped object state summary scaffold based on packet object lists.
Current version also tries to pull a first line / first useful bullet from matched cards.
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


def match_card(folder: Path, item: str) -> Path | None:
    if not folder.exists() or not item:
        return None
    item_lower = item.lower()
    for p in sorted(folder.glob("*.md")):
        stem = p.stem.lower()
        if stem in {"readme", "scene-index"}:
            continue
        if item_lower in stem:
            return p
    return None


def extract_hint(path: Path) -> str:
    if not path or not path.exists():
        return ""
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            return stripped[2:].strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith(">"):
            return stripped
    return ""


def block(title: str, items: list[str], folder: Path):
    lines = [title, ""]
    if not items:
        lines.append("- ")
        return lines
    for item in items:
        card = match_card(folder, item)
        hint = extract_hint(card) if card else ""
        if card and hint:
            lines.append(f"- {item}：{hint}（参考 `{card.name}`）")
        elif card:
            lines.append(f"- {item}（参考 `{card.name}`）")
        else:
            lines.append(f"- {item}：")
    return lines


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

    char_dir = root / "settings" / "subsettings" / "characters"
    event_dir = root / "settings" / "subsettings" / "events"
    space_dir = root / "settings" / "subsettings" / "spaces" / "cards"
    scene_dir = root / "settings" / "subsettings" / "scenes" / "cards"

    lines = [f"# {chapter_id} 对象状态摘要", ""]
    lines += block("## 一、相关人物当前状态", chars, char_dir)
    lines += [""]
    lines += block("## 二、相关事件当前状态", events, event_dir)
    lines += [""]
    lines += block("## 三、相关空间当前状态", spaces, space_dir)
    lines += [""]
    lines += block("## 四、相关场景当前状态", scenes, scene_dir)
    lines += ["", "## 五、这一章最该记住的对象约束", "- ", "- ", "- ", ""]

    out.write_text("\n".join(lines))
    print(f"prepared object state summary scaffold: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
build_input_pack.py

Build chapter-scoped input pack files in two forms:
- model input pack: minimal, low-token oriented
- review input pack: fuller, human-auditable
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

    model_out = root / ".novel-studio" / "logs" / f"{chapter_id}-input-pack-model.md"
    review_out = root / ".novel-studio" / "logs" / f"{chapter_id}-input-pack-review.md"
    model_out.parent.mkdir(parents=True, exist_ok=True)

    core = [summary, packet, style_overlay, object_summary]
    index_names = ["active-characters.md", "active-events.md", "active-spaces.md", "active-scenes.md", "pending-foreshadowing.md"]
    existing_indexes = [indexes / n for n in index_names if (indexes / n).exists()]

    model_lines = [f"# {chapter_id} 模型输入包", "", "## 核心输入", ""]
    model_lines.extend([f"- `{p.relative_to(root)}`" for p in core])
    model_lines += ["", "## 说明", "- 目标：尽量低 token，优先保证当前章可写。", "- 默认只带核心输入，不额外展开完整对象卡。", ""]
    model_out.write_text("\n".join(model_lines))

    review_lines = [f"# {chapter_id} 人工审阅输入包", "", "## 核心输入", ""]
    review_lines.extend([f"- `{p.relative_to(root)}`" for p in core])
    review_lines += ["", "## 推荐带（增强上下文）", ""]
    if existing_indexes:
        review_lines.extend([f"- `{p.relative_to(root)}`" for p in existing_indexes])
    else:
        review_lines.append("- 暂无活动索引文件")
    review_lines += ["", "## 说明", "- 目标：给人工快速审阅本章准备状态。", "- 比模型输入版更完整，适合检查承接、对象和风格。", ""]
    review_out.write_text("\n".join(review_lines))

    print(f"prepared input pack files: {model_out} , {review_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

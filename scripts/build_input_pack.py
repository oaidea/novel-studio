#!/usr/bin/env python3
"""
build_input_pack.py

Build chapter-scoped input pack files in two forms:
- model input pack: low-token oriented (with minimal vs standard levels)
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

    model_min = root / ".novel-studio" / "logs" / f"{chapter_id}-input-pack-model-min.md"
    model_std = root / ".novel-studio" / "logs" / f"{chapter_id}-input-pack-model-std.md"
    review_out = root / ".novel-studio" / "logs" / f"{chapter_id}-input-pack-review.md"
    model_min.parent.mkdir(parents=True, exist_ok=True)

    core_min = [summary, packet, style_overlay]
    core_std = [summary, packet, style_overlay, object_summary]
    index_names = ["active-characters.md", "active-events.md", "active-spaces.md", "active-scenes.md", "pending-foreshadowing.md"]
    existing_indexes = [indexes / n for n in index_names if (indexes / n).exists()]

    min_lines = [f"# {chapter_id} 模型输入包（极简）", "", "## 核心输入", ""]
    min_lines.extend([f"- `{p.relative_to(root)}`" for p in core_min])
    min_lines += ["", "## 说明", "- 目标：极致节省 token。", "- 适用于本章承接简单、对象变化不多的情况。", ""]
    model_min.write_text("\n".join(min_lines))

    std_lines = [f"# {chapter_id} 模型输入包（标准）", "", "## 核心输入", ""]
    std_lines.extend([f"- `{p.relative_to(root)}`" for p in core_std])
    std_lines += ["", "## 说明", "- 目标：在低 token 前提下，保留对象状态层。", "- 适用于本章对象变化较多或承接要求更高的情况。", ""]
    model_std.write_text("\n".join(std_lines))

    review_lines = [f"# {chapter_id} 人工审阅输入包", "", "## 核心输入", ""]
    review_lines.extend([f"- `{p.relative_to(root)}`" for p in core_std])
    review_lines += ["", "## 推荐带（增强上下文）", ""]
    if existing_indexes:
        review_lines.extend([f"- `{p.relative_to(root)}`" for p in existing_indexes])
    else:
        review_lines.append("- 暂无活动索引文件")
    review_lines += ["", "## 说明", "- 目标：给人快速核对本章准备状态。", "- 比模型输入版更完整，适合检查承接、对象和风格。", ""]
    review_out.write_text("\n".join(review_lines))

    print(f"prepared input pack files: {model_min} , {model_std} , {review_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

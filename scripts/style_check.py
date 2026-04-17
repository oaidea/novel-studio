#!/usr/bin/env python3
"""
style_check.py

Create a style-consistency check file for a chapter and, when available,
embed the current project style card path for reference.
"""

from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: style_check.py <project-dir> <chapter-id>")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    chapter_id = sys.argv[2]
    out = root / ".novel-studio" / "logs" / f"{chapter_id}-style-check.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    style_card = root / "settings" / "subsettings" / "project-style-card.md"
    style_ref = str(style_card.relative_to(root)) if style_card.exists() else "（未找到项目风格卡）"

    out.write_text(
        f"# {chapter_id} 风格一致性检查\n\n"
        f"- 项目风格卡：`{style_ref}`\n\n"
        "- [ ] 句子节奏仍像这本书\n"
        "- [ ] 对话气质没有偏离项目母风格\n"
        "- [ ] 感官描写方式仍符合项目习惯\n"
        "- [ ] 信息释放方式没有突然变味\n"
        "- [ ] 情绪表达没有越出项目边界\n"
        "- [ ] 章末钩子仍符合本书钩子习惯\n"
        "- [ ] 这章只是任务不同，不是风格断裂\n"
    )

    print(f"prepared style check scaffold for {chapter_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

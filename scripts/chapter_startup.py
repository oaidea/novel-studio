#!/usr/bin/env python3
"""
novel-studio chapter startup script skeleton

Planned purpose:
- create startup checklist for a new chapter
- create chapter packet placeholder
- create chapter summary placeholder for previous chapter if needed

Current state:
- scaffold placeholder only
"""

from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: chapter_startup.py <project-dir> <chapter-id>")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    chapter_id = sys.argv[2]

    packet = root / ".novel-studio" / "packets" / f"{chapter_id}-packet.md"
    startup = root / ".novel-studio" / "logs" / f"{chapter_id}-startup-checklist.md"

    packet.parent.mkdir(parents=True, exist_ok=True)
    startup.parent.mkdir(parents=True, exist_ok=True)

    if not packet.exists():
        packet.write_text(f"# {chapter_id} Chapter Packet\n\n- 本章目标：\n- 本章阻力：\n- 本章代价：\n- 本章结束状态：\n")

    if not startup.exists():
        startup.write_text(
            f"# {chapter_id} 启动清单\n\n"
            "- [ ] 已有上一章 summary\n"
            "- [ ] 已预测本章依赖人物\n"
            "- [ ] 已预测本章依赖空间\n"
            "- [ ] 已预测本章依赖时间\n"
            "- [ ] 已预测本章依赖事件\n"
            "- [ ] 已预测本章依赖伏笔\n"
            "- [ ] 已明确本章目的\n"
            "- [ ] 已有本章框架\n"
            "- [ ] 已生成 chapter packet\n"
            "- [ ] 已列出本章预计改动哪些卡片\n"
        )

    print(f"prepared startup files for {chapter_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

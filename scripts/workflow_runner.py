#!/usr/bin/env python3
"""
workflow_runner.py

Lightweight workflow entrypoint for the current novel-studio scaffold chain.
Supports mode switches and minimal self-healing orchestration logic.
"""

from pathlib import Path
import subprocess
import sys
import json


SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def note(msg: str) -> None:
    print(f"[note] {msg}")


def ensure_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content)
        note(f"prepared scaffold: {path}")


def ensure_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        note(f"prepared json scaffold: {path}")


def main() -> int:
    if len(sys.argv) < 4:
        print("usage: workflow_runner.py <project-dir> <chapter-id> <mode> [project-name]")
        print("modes: startup | style | style-full | chapter-full | writeback | refresh | full")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    chapter_id = sys.argv[2]
    mode = sys.argv[3]
    project_name = sys.argv[4] if len(sys.argv) >= 5 else root.name

    style_card = root / "settings" / "subsettings" / "project-style-card.md"
    packet = root / ".novel-studio" / "packets" / f"{chapter_id}-packet.md"
    style_overlay = root / ".novel-studio" / "packets" / f"{chapter_id}-style-overlay.md"
    indexes = root / ".novel-studio" / "indexes"
    summaries = root / ".novel-studio" / "summaries"
    summary = summaries / f"{chapter_id}-summary.md"
    state_json = root / ".novel-studio" / "state.json"
    meta_json = root / ".novel-studio" / "chapter-meta.json"

    if mode == "startup":
        run([str(SCRIPT_DIR / "chapter_startup.py"), str(root), chapter_id])
    elif mode == "style":
        if not style_card.exists():
            note("project style card not found; consider running extract_project_style.py first")
        run([str(SCRIPT_DIR / "style_check.py"), str(root), chapter_id])
    elif mode == "style-full":
        if not style_card.exists():
            note("project style card not found; extracting project style scaffold now")
            run([str(SCRIPT_DIR / "extract_project_style.py"), str(root), project_name])
        if not packet.exists():
            note("chapter packet not found; startup will prepare one")
            run([str(SCRIPT_DIR / "chapter_startup.py"), str(root), chapter_id])
        if style_card.exists() and not style_overlay.exists():
            run([str(SCRIPT_DIR / "build_style_packet.py"), str(root), chapter_id, str(style_card.relative_to(root))])
        run([str(SCRIPT_DIR / "style_check.py"), str(root), chapter_id])
    elif mode == "chapter-full":
        if not summary.exists():
            ensure_file(
                summary,
                f"# {chapter_id} 摘要\n\n## 一、本章发生了什么\n- \n\n## 二、人物停在哪\n- \n\n## 三、事件推进到哪\n- \n\n## 四、空间 / 场景状态变化\n- \n\n## 五、时间锚点\n- \n\n## 六、下一章承接点\n- \n",
            )
        if not packet.exists():
            run([str(SCRIPT_DIR / "chapter_startup.py"), str(root), chapter_id])
        if not style_card.exists():
            note("project style card not found; extracting project style scaffold now")
            run([str(SCRIPT_DIR / "extract_project_style.py"), str(root), project_name])
        if style_card.exists() and not style_overlay.exists():
            run([str(SCRIPT_DIR / "build_style_packet.py"), str(root), chapter_id, str(style_card.relative_to(root))])
        if not indexes.exists():
            note("indexes directory not found; refresh will prepare it")
            run([str(SCRIPT_DIR / "index_refresh.py"), str(root)])
        note("chapter-full ready: packet / summary / style overlay / indexes are prepared for writing")
    elif mode == "writeback":
        run([str(SCRIPT_DIR / "writeback_sync.py"), str(root), chapter_id])
    elif mode == "refresh":
        run([str(SCRIPT_DIR / "index_refresh.py"), str(root)])
    elif mode == "full":
        if not packet.exists():
            note("chapter packet not found; startup will prepare one")
        if not indexes.exists():
            note("indexes directory not found; refresh will prepare it")
        if not summary.exists():
            ensure_file(
                summary,
                f"# {chapter_id} 摘要\n\n## 一、本章发生了什么\n- \n\n## 二、人物停在哪\n- \n\n## 三、事件推进到哪\n- \n\n## 四、空间 / 场景状态变化\n- \n\n## 五、时间锚点\n- \n\n## 六、下一章承接点\n- \n",
            )
        ensure_json(
            state_json,
            {
                "project": root.name,
                "currentArc": "",
                "currentChapter": chapter_id,
                "currentTimeAnchor": "",
                "currentConflicts": [],
                "topPriorities": [],
                "pendingForeshadowing": [],
            },
        )
        ensure_json(meta_json, {"chapters": []})

        if not style_card.exists():
            note("project style card not found; extracting project style scaffold now")
            run([str(SCRIPT_DIR / "extract_project_style.py"), str(root), project_name])

        if not packet.exists():
            run([str(SCRIPT_DIR / "chapter_startup.py"), str(root), chapter_id])

        if style_card.exists() and not style_overlay.exists():
            run([str(SCRIPT_DIR / "build_style_packet.py"), str(root), chapter_id, str(style_card.relative_to(root))])

        run([str(SCRIPT_DIR / "writeback_sync.py"), str(root), chapter_id])
        run([str(SCRIPT_DIR / "style_check.py"), str(root), chapter_id])
        run([str(SCRIPT_DIR / "index_refresh.py"), str(root)])
    else:
        print(f"unknown mode: {mode}")
        print("modes: startup | style | style-full | chapter-full | writeback | refresh | full")
        return 1

    print(f"workflow mode '{mode}' completed for {chapter_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

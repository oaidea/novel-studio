#!/usr/bin/env python3
"""
workflow_runner.py

Lightweight workflow entrypoint for the current novel-studio scaffold chain.
Supports small mode switches and a minimal amount of orchestration logic.
"""

from pathlib import Path
import subprocess
import sys


SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def note(msg: str) -> None:
    print(f"[note] {msg}")


def main() -> int:
    if len(sys.argv) < 4:
        print("usage: workflow_runner.py <project-dir> <chapter-id> <mode>")
        print("modes: startup | style | writeback | refresh | full")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    chapter_id = sys.argv[2]
    mode = sys.argv[3]

    style_card = root / "settings" / "subsettings" / "project-style-card.md"
    packet = root / ".novel-studio" / "packets" / f"{chapter_id}-packet.md"
    indexes = root / ".novel-studio" / "indexes"
    summaries = root / ".novel-studio" / "summaries"

    if mode == "startup":
        run([str(SCRIPT_DIR / "chapter_startup.py"), str(root), chapter_id])
    elif mode == "style":
        if not style_card.exists():
            note("project style card not found; consider running extract_project_style.py first")
        run([str(SCRIPT_DIR / "style_check.py"), str(root), chapter_id])
    elif mode == "writeback":
        run([str(SCRIPT_DIR / "writeback_sync.py"), str(root), chapter_id])
    elif mode == "refresh":
        run([str(SCRIPT_DIR / "index_refresh.py"), str(root)])
    elif mode == "full":
        if not style_card.exists():
            note("project style card not found; consider running extract_project_style.py first")
        if not packet.exists():
            note("chapter packet not found; startup will prepare one")
        if not indexes.exists():
            note("indexes directory not found; refresh will prepare it")
        if not summaries.exists() or not any(summaries.glob("*.md")):
            note("no chapter summaries found; packet-first continuity may be weak until summaries are added")

        if not packet.exists():
            run([str(SCRIPT_DIR / "chapter_startup.py"), str(root), chapter_id])
        run([str(SCRIPT_DIR / "writeback_sync.py"), str(root), chapter_id])
        run([str(SCRIPT_DIR / "style_check.py"), str(root), chapter_id])
        run([str(SCRIPT_DIR / "index_refresh.py"), str(root)])
    else:
        print(f"unknown mode: {mode}")
        print("modes: startup | style | writeback | refresh | full")
        return 1

    print(f"workflow mode '{mode}' completed for {chapter_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

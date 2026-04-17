#!/usr/bin/env python3
"""
workflow_runner.py

Lightweight workflow entrypoint for the current novel-studio scaffold chain.
Supports small mode switches so users do not need to invoke every script manually.
"""

from pathlib import Path
import subprocess
import sys


SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    if len(sys.argv) < 4:
        print("usage: workflow_runner.py <project-dir> <chapter-id> <mode>")
        print("modes: startup | style | writeback | refresh | full")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    chapter_id = sys.argv[2]
    mode = sys.argv[3]

    if mode == "startup":
        run([str(SCRIPT_DIR / "chapter_startup.py"), str(root), chapter_id])
    elif mode == "style":
        run([str(SCRIPT_DIR / "style_check.py"), str(root), chapter_id])
    elif mode == "writeback":
        run([str(SCRIPT_DIR / "writeback_sync.py"), str(root), chapter_id])
    elif mode == "refresh":
        run([str(SCRIPT_DIR / "index_refresh.py"), str(root)])
    elif mode == "full":
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

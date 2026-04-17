#!/usr/bin/env python3
"""
workflow_runner.py

Planned purpose:
- provide one lightweight entrypoint to call the current scaffold chain
- stay minimal until the workflow is more stable
"""

from pathlib import Path
import subprocess
import sys


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: workflow_runner.py <project-dir> <chapter-id>")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    chapter_id = sys.argv[2]
    script_dir = Path(__file__).resolve().parent

    run([str(script_dir / "chapter_startup.py"), str(root), chapter_id])
    run([str(script_dir / "writeback_sync.py"), str(root), chapter_id])
    run([str(script_dir / "style_check.py"), str(root), chapter_id])
    run([str(script_dir / "index_refresh.py"), str(root)])

    print(f"prepared minimal workflow chain for {chapter_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
novel-studio bootstrap script skeleton

Planned purpose:
- initialize a packet-first novel project skeleton
- create .novel-studio internal structure
- optionally generate starter docs and indexes

Current state:
- scaffold placeholder only
- implementation intentionally left minimal until workflow is frozen
"""

from pathlib import Path
import json
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: init_novel_project.py <project-dir>")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    paths = [
        root / "docs",
        root / "analysis",
        root / "chapters" / "published",
        root / "chapters" / "drafts",
        root / "chapters" / "candidates",
        root / "brainstorm",
        root / "nav",
        root / "settings" / "core",
        root / "settings" / "world",
        root / "settings" / "subsettings" / "characters" / "changes",
        root / "settings" / "subsettings" / "characters" / "templates",
        root / "settings" / "subsettings" / "relationships",
        root / "settings" / "subsettings" / "timeline",
        root / "settings" / "subsettings" / "foreshadowing",
        root / "settings" / "subsettings" / "spaces" / "cards",
        root / "settings" / "subsettings" / "spaces" / "changes",
        root / "settings" / "subsettings" / "spaces" / "templates",
        root / "settings" / "subsettings" / "scenes" / "cards",
        root / "settings" / "subsettings" / "scenes" / "changes",
        root / "settings" / "subsettings" / "scenes" / "templates",
        root / "workflow",
        root / ".novel-studio" / "summaries",
        root / ".novel-studio" / "packets",
        root / ".novel-studio" / "indexes",
        root / ".novel-studio" / "logs",
    ]

    for path in paths:
        path.mkdir(parents=True, exist_ok=True)

    state_path = root / ".novel-studio" / "state.json"
    meta_path = root / ".novel-studio" / "chapter-meta.json"

    if not state_path.exists():
        state_path.write_text(json.dumps({
            "project": root.name,
            "currentArc": "",
            "currentChapter": "",
            "currentTimeAnchor": "",
            "currentConflicts": [],
            "topPriorities": [],
            "pendingForeshadowing": []
        }, ensure_ascii=False, indent=2) + "\n")

    if not meta_path.exists():
        meta_path.write_text(json.dumps({"chapters": []}, ensure_ascii=False, indent=2) + "\n")

    print(f"initialized packet-first novel project skeleton at: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

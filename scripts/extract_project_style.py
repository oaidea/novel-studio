#!/usr/bin/env python3
"""
extract_project_style.py

Generate a project-level style card scaffold and record which chapter files
were used as the current extraction basis.

Current behavior is intentionally light-weight:
- prefers published chapters
- falls back to draft/candidate chapters
- does not yet do real NLP extraction
- but produces a usable structured scaffold with source tracking
"""

from pathlib import Path
import sys


def find_chapter_sources(root: Path) -> list[Path]:
    chapters = []
    for sub in [
        root / "chapters" / "published",
        root / "chapters" / "drafts",
        root / "chapters" / "candidates",
    ]:
        if sub.exists():
            chapters.extend(sorted(sub.glob("*.md")))
    return chapters


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: extract_project_style.py <project-dir> <project-name>")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    project_name = sys.argv[2]

    out = root / "settings" / "subsettings" / "project-style-card.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    chapter_sources = find_chapter_sources(root)
    rel_sources = [str(p.relative_to(root)) for p in chapter_sources[:12]]

    lines = [f"# {project_name}项目风格卡", "", "## 一、风格提取来源", ""]
    if rel_sources:
        lines.extend([f"- `{src}`" for src in rel_sources])
    else:
        lines.append("- 暂无可用章节，当前为纯 scaffold")

    lines += [
        "",
        "## 二、叙事气质",
        "- 根据上述章节进一步提纯",
        "",
        "## 三、句子与段落习惯",
        "- 根据上述章节进一步提纯",
        "",
        "## 四、对话质感",
        "- 根据上述章节进一步提纯",
        "",
        "## 五、感官描写方式",
        "- 根据上述章节进一步提纯",
        "",
        "## 六、信息释放方式",
        "- 根据上述章节进一步提纯",
        "",
        "## 七、情绪表达方式",
        "- 根据上述章节进一步提纯",
        "",
        "## 八、章末钩子习惯",
        "- 根据上述章节进一步提纯",
        "",
        "## 九、禁忌写法",
        "- 根据上述章节进一步提纯",
        "",
        "## 十、一句话母风格总结",
        "- 待提纯",
        "",
        "## 十一、说明",
        "- 当前版本已开始真实读取章节文件并记录来源。",
        "- 后续可进一步升级为真正的风格特征抽取。",
    ]

    out.write_text("\n".join(lines) + "\n")
    print(f"prepared project style card scaffold from {len(rel_sources)} source files: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

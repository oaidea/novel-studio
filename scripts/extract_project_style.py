#!/usr/bin/env python3
"""
extract_project_style.py

Planned purpose:
- generate a project-level style card scaffold
- support two input modes:
  1) external sample mode
  2) existing chapters mode

Current state:
- scaffold placeholder only
"""

from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: extract_project_style.py <project-dir> <project-name>")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    project_name = sys.argv[2]

    out = root / "settings" / "subsettings" / "project-style-card.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    if not out.exists():
        out.write_text(
            f"# {project_name}项目风格卡\n\n"
            "## 一、叙事气质\n- \n\n"
            "## 二、句子与段落习惯\n- \n\n"
            "## 三、对话质感\n- \n\n"
            "## 四、感官描写方式\n- \n\n"
            "## 五、信息释放方式\n- \n\n"
            "## 六、情绪表达方式\n- \n\n"
            "## 七、章末钩子习惯\n- \n\n"
            "## 八、禁忌写法\n- \n"
        )

    print(f"prepared project style card scaffold: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

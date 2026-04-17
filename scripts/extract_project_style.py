#!/usr/bin/env python3
"""
extract_project_style.py

Generate a project-level style card scaffold, prioritize source chapters by
reliability, and compute a few light-weight style indicators.
"""

from pathlib import Path
import re
import sys


SOURCE_GROUPS = [
    ("published", "最高优先级"),
    ("drafts", "中优先级"),
    ("candidates", "较低优先级"),
]


def collect_sources(root: Path):
    groups = []
    for folder_name, label in SOURCE_GROUPS:
        folder = root / "chapters" / folder_name
        files = sorted(folder.glob("*.md")) if folder.exists() else []
        groups.append((folder_name, label, files))
    return groups


def calc_metrics(paths: list[Path]):
    paragraph_lengths = []
    dialogue_lines = 0
    nonempty_lines = 0
    section_breaks = 0
    question_lines = 0

    for path in paths:
        text = path.read_text()
        lines = text.splitlines()
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            nonempty_lines += 1
            if stripped == "---":
                section_breaks += 1
            if stripped.startswith("“") or stripped.startswith('"'):
                dialogue_lines += 1
            if "？" in stripped or "?" in stripped:
                question_lines += 1

        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        for p in paragraphs:
            if p != "---":
                paragraph_lengths.append(len(p))

    avg_para = round(sum(paragraph_lengths) / len(paragraph_lengths), 1) if paragraph_lengths else 0
    dialogue_ratio = round(dialogue_lines / nonempty_lines, 3) if nonempty_lines else 0
    q_ratio = round(question_lines / nonempty_lines, 3) if nonempty_lines else 0

    return {
        "avg_paragraph_length": avg_para,
        "dialogue_line_ratio": dialogue_ratio,
        "section_breaks": section_breaks,
        "question_line_ratio": q_ratio,
        "sample_file_count": len(paths),
    }


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: extract_project_style.py <project-dir> <project-name>")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    project_name = sys.argv[2]

    out = root / "settings" / "subsettings" / "project-style-card.md"
    out.parent.mkdir(parents=True, exist_ok=True)

    groups = collect_sources(root)
    preferred_paths = []
    lines = [f"# {project_name}项目风格卡", "", "## 一、风格提取来源", ""]

    for folder_name, label, files in groups:
        lines.append(f"### {folder_name}（{label}）")
        if files:
            for p in files[:12]:
                lines.append(f"- `{p.relative_to(root)}`")
            if not preferred_paths and files:
                preferred_paths = files[:12]
        else:
            lines.append("- 无")
        lines.append("")

    metrics = calc_metrics(preferred_paths) if preferred_paths else {
        "avg_paragraph_length": 0,
        "dialogue_line_ratio": 0,
        "section_breaks": 0,
        "question_line_ratio": 0,
        "sample_file_count": 0,
    }

    lines += [
        "## 二、轻量风格指标（当前版本）",
        f"- 样本章节数：{metrics['sample_file_count']}",
        f"- 平均段落长度：{metrics['avg_paragraph_length']}",
        f"- 对话行占比：{metrics['dialogue_line_ratio']}",
        f"- 分节符数量：{metrics['section_breaks']}",
        f"- 问句行占比：{metrics['question_line_ratio']}",
        "",
        "## 三、叙事气质",
        "- 根据高优先级样本进一步提纯",
        "",
        "## 四、句子与段落习惯",
        "- 结合轻量指标与样本进一步提纯",
        "",
        "## 五、对话质感",
        "- 结合高优先级样本进一步提纯",
        "",
        "## 六、感官描写方式",
        "- 根据高优先级样本进一步提纯",
        "",
        "## 七、信息释放方式",
        "- 根据高优先级样本进一步提纯",
        "",
        "## 八、情绪表达方式",
        "- 根据高优先级样本进一步提纯",
        "",
        "## 九、章末钩子习惯",
        "- 根据高优先级样本进一步提纯",
        "",
        "## 十、禁忌写法",
        "- 根据当前项目已有章节反推",
        "",
        "## 十一、一句话母风格总结",
        "- 待提纯",
        "",
        "## 十二、说明",
        "- 当前版本已支持风格提取来源优先级：published > drafts > candidates。",
        "- 当前版本已加入第一批轻量风格指标，用于辅助提纯母风格。",
    ]

    out.write_text("\n".join(lines) + "\n")
    print(f"prepared project style card from prioritized sources: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

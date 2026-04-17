#!/usr/bin/env python3
"""
extract_project_style.py

Generate a project-level style card scaffold, prioritize source chapters by
reliability, and compute light-weight style indicators with first-pass heuristic
judgements.
"""

from pathlib import Path
import re
import sys


SOURCE_GROUPS = [
    ("published", "最高优先级"),
    ("drafts", "中优先级"),
    ("candidates", "较低优先级"),
]

SENSE_WORDS = {
    "visual": ["看", "望", "影", "光", "色", "亮", "暗"],
    "audio": ["听", "响", "声", "静", "吵", "雨声", "风声"],
    "touch": ["冷", "热", "凉", "烫", "湿", "麻", "疼"],
    "smell": ["味", "香", "腥", "焦", "潮", "烟气"],
}


def collect_sources(root: Path):
    groups = []
    for folder_name, label in SOURCE_GROUPS:
        folder = root / "chapters" / folder_name
        files = sorted(folder.glob("*.md")) if folder.exists() else []
        groups.append((folder_name, label, files))
    return groups


def calc_metrics(paths: list[Path]):
    paragraph_lengths = []
    paragraph_line_counts = []
    dialogue_lines = 0
    nonempty_lines = 0
    section_breaks = 0
    question_lines = 0
    punctuation_counts = {"。": 0, "，": 0, "……": 0, "！": 0, "？": 0}
    sense_hits = {k: 0 for k in SENSE_WORDS}
    ending_lines = []

    for path in paths:
        text = path.read_text()
        lines = text.splitlines()
        content_lines = [ln.strip() for ln in lines if ln.strip()]
        ending_lines.extend(content_lines[-3:])

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

            punctuation_counts["。"] += stripped.count("。")
            punctuation_counts["，"] += stripped.count("，")
            punctuation_counts["……"] += stripped.count("……")
            punctuation_counts["！"] += stripped.count("！")
            punctuation_counts["？"] += stripped.count("？")

            for key, words in SENSE_WORDS.items():
                for word in words:
                    sense_hits[key] += stripped.count(word)

        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        for p in paragraphs:
            if p != "---":
                paragraph_lengths.append(len(p))
                paragraph_line_counts.append(len([ln for ln in p.splitlines() if ln.strip()]))

    avg_para = round(sum(paragraph_lengths) / len(paragraph_lengths), 1) if paragraph_lengths else 0
    avg_para_lines = round(sum(paragraph_line_counts) / len(paragraph_line_counts), 1) if paragraph_line_counts else 0
    dialogue_ratio = round(dialogue_lines / nonempty_lines, 3) if nonempty_lines else 0
    q_ratio = round(question_lines / nonempty_lines, 3) if nonempty_lines else 0

    ending_q = sum(1 for ln in ending_lines if "？" in ln or "?" in ln)
    ending_ex = sum(1 for ln in ending_lines if "！" in ln)
    ending_ellipsis = sum(1 for ln in ending_lines if "……" in ln)

    return {
        "avg_paragraph_length": avg_para,
        "avg_paragraph_line_count": avg_para_lines,
        "dialogue_line_ratio": dialogue_ratio,
        "section_breaks": section_breaks,
        "question_line_ratio": q_ratio,
        "punctuation_counts": punctuation_counts,
        "sense_hits": sense_hits,
        "ending_question_lines": ending_q,
        "ending_exclaim_lines": ending_ex,
        "ending_ellipsis_lines": ending_ellipsis,
        "sample_file_count": len(paths),
    }


def judge_metrics(metrics: dict) -> dict:
    dialogue_ratio = metrics["dialogue_line_ratio"]
    avg_len = metrics["avg_paragraph_length"]
    avg_lines = metrics["avg_paragraph_line_count"]

    if dialogue_ratio >= 0.35:
        dialogue_style = "对话驱动偏高"
    elif dialogue_ratio >= 0.18:
        dialogue_style = "对话驱动中等"
    else:
        dialogue_style = "对话驱动偏低"

    if avg_len <= 55 and avg_lines <= 2.2:
        paragraph_style = "段落偏短促"
    elif avg_len <= 110:
        paragraph_style = "段落中性"
    else:
        paragraph_style = "段落偏铺陈"

    sense_hits = metrics["sense_hits"]
    dominant_sense = max(sense_hits, key=sense_hits.get) if any(sense_hits.values()) else "none"
    sense_map = {
        "visual": "感官描写更偏视觉",
        "audio": "感官描写更偏听觉",
        "touch": "感官描写更偏触感",
        "smell": "感官描写更偏气味",
        "none": "感官描写倾向暂不明显",
    }

    ending_q = metrics["ending_question_lines"]
    ending_e = metrics["ending_ellipsis_lines"]
    ending_ex = metrics["ending_exclaim_lines"]
    if ending_q >= max(ending_e, ending_ex) and ending_q > 0:
        hook_style = "章末更偏问句钩"
    elif ending_e >= max(ending_q, ending_ex) and ending_e > 0:
        hook_style = "章末更偏省略钩"
    elif ending_ex > 0:
        hook_style = "章末更偏感叹钩"
    else:
        hook_style = "章末更偏叙述钩"

    return {
        "dialogue_style": dialogue_style,
        "paragraph_style": paragraph_style,
        "sense_style": sense_map[dominant_sense],
        "hook_style": hook_style,
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
        "avg_paragraph_line_count": 0,
        "dialogue_line_ratio": 0,
        "section_breaks": 0,
        "question_line_ratio": 0,
        "punctuation_counts": {"。": 0, "，": 0, "……": 0, "！": 0, "？": 0},
        "sense_hits": {k: 0 for k in SENSE_WORDS},
        "ending_question_lines": 0,
        "ending_exclaim_lines": 0,
        "ending_ellipsis_lines": 0,
        "sample_file_count": 0,
    }
    judgements = judge_metrics(metrics)

    lines += [
        "## 二、轻量风格指标（当前版本）",
        f"- 样本章节数：{metrics['sample_file_count']}",
        f"- 平均段落长度：{metrics['avg_paragraph_length']}",
        f"- 单段平均行数：{metrics['avg_paragraph_line_count']}",
        f"- 对话行占比：{metrics['dialogue_line_ratio']}",
        f"- 分节符数量：{metrics['section_breaks']}",
        f"- 问句行占比：{metrics['question_line_ratio']}",
        f"- 标点统计：句号 {metrics['punctuation_counts']['。']} / 逗号 {metrics['punctuation_counts']['，']} / 省略号 {metrics['punctuation_counts']['……']} / 感叹号 {metrics['punctuation_counts']['！']} / 问号 {metrics['punctuation_counts']['？']}",
        f"- 感官词命中：视觉 {metrics['sense_hits']['visual']} / 听觉 {metrics['sense_hits']['audio']} / 触感 {metrics['sense_hits']['touch']} / 气味 {metrics['sense_hits']['smell']}",
        f"- 章末三行特征：问句 {metrics['ending_question_lines']} / 感叹 {metrics['ending_exclaim_lines']} / 省略号 {metrics['ending_ellipsis_lines']}",
        "",
        "## 三、第一轮风格判断（启发式）",
        f"- {judgements['dialogue_style']}",
        f"- {judgements['paragraph_style']}",
        f"- {judgements['sense_style']}",
        f"- {judgements['hook_style']}",
        "",
        "## 四、叙事气质",
        "- 根据高优先级样本进一步提纯",
        "",
        "## 五、句子与段落习惯",
        "- 结合轻量指标与样本进一步提纯",
        "",
        "## 六、对话质感",
        "- 结合高优先级样本进一步提纯",
        "",
        "## 七、感官描写方式",
        "- 根据高优先级样本进一步提纯",
        "",
        "## 八、信息释放方式",
        "- 根据高优先级样本进一步提纯",
        "",
        "## 九、情绪表达方式",
        "- 根据高优先级样本进一步提纯",
        "",
        "## 十、章末钩子习惯",
        "- 根据高优先级样本进一步提纯",
        "",
        "## 十一、禁忌写法",
        "- 根据当前项目已有章节反推",
        "",
        "## 十二、一句话母风格总结",
        "- 待提纯",
        "",
        "## 十三、说明",
        "- 当前版本已支持风格提取来源优先级：published > drafts > candidates。",
        "- 当前版本已加入启发式第一轮风格判断，用于辅助提纯母风格。",
    ]

    out.write_text("\n".join(lines) + "\n")
    print(f"prepared project style card from prioritized sources: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

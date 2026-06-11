#!/usr/bin/env python3
"""
humanize_pass.py

A lightweight first-pass humanize / 去AI味 helper for novel-studio.
Current version:
- reads a source chapter markdown
- writes a sidecar draft for manual review
- emits a structured rewrite brief
- preserves source text
- generates a rewritten draft with light / medium / heavy levels

v2 (2026-06-11): 老司机定制8条新规则
  - 规则1: 检测「不是…而是…」「不像…而像…」机械对比句式
  - 规则2: 检测多句号段落，建议拆段（一段一意）
  - 规则3: 去多余连接词（已有，强化）
  - 规则4: 去多余形容词（通过比喻/虚词密度间接检测）
  - 规则5: 去多余比喻（检测比喻词密度）
  - 规则6: 检测「没有…也没有…」排比否定句式
  - 规则7: 去解释腔（已有，强化）
  - 规则8: 去填充词（检测「不知道…」「不由得」「下意识」）
"""

from pathlib import Path
import sys
from datetime import datetime, timezone
import re
from ns_io_local import read_text, write_text

# 尝试导入 AI 评分引擎
try:
    from ai_scoring import score_full, compare_scores, _score_to_grade
    HAS_AI_SCORING = True
except ImportError:
    HAS_AI_SCORING = False
    def score_full(*args, **kwargs): return None
    def compare_scores(*args, **kwargs): return None
    def _score_to_grade(*args): return "N/A"


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
CHECKLIST = REPO_ROOT / "references" / "humanize-checklist.md"


def _dim_delta(before_dims: dict, after_dims: dict, key: str) -> str:
    """格式化维度变化"""
    b = before_dims.get(key, 0)
    a = after_dims.get(key, 0)
    d = round(a - b, 1)
    return f"+{d}" if d > 0 else str(d)


def find_candidate_chapter(root: Path, chapter_id: str) -> Path | None:
    candidates = [
        root / "chapters" / "candidates" / f"{chapter_id}.md",
        root / "chapters" / "published" / f"{chapter_id}.md",
        root / "chapters" / f"{chapter_id}.md",
    ]
    for path in candidates:
        if path.exists():
            return path
    for path in root.rglob(f"{chapter_id}.md"):
        if ".novel-studio" in path.parts:
            continue
        return path
    return None


def analyze_text(text: str) -> dict:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    lines = text.splitlines()
    sentence_count = sum(len(re.findall(r"[。！？!?]", line)) for line in lines)
    connector_hits = sum(text.count(token) for token in ["因此", "此外", "同时", "然而", "不过", "于是", "不仅", "而且"])
    ai_taste_hits = sum(text.count(token) for token in ["重要", "意味着", "某种程度上", "可以说", "本质上", "换句话说", "进一步", "某种意义上"])
    dialogue_hits = text.count("\u201c") + text.count('"')
    action_hits = sum(text.count(token) for token in ["看", "抬", "握", "走", "站", "顿", "笑", "退", "推", "坐"])
    avg_para_len = round(sum(len(p) for p in paragraphs) / len(paragraphs), 1) if paragraphs else 0

    # === 老司机定制规则 (2026-06-11) ===
    # 规则1: 对比转折句式 — 不是……而是…… / 不像……而像……
    contrast_pattern_hits = len(re.findall(r'不是.{1,30}而是|不像.{1,30}而像', text))
    # 规则2: 多句号段落 — 一段里 >=2 个句号（排除对话密集段）
    multi_sentence_paras = sum(
        1 for p in paragraphs
        if len(re.findall(r'[。！？!?]', p)) >= 2
        and p.count('"') + p.count('\u201c') < 2
    )
    # 规则5: 多余比喻 — 像/如/仿佛/好比/宛如/犹如/似的/般 总命中数
    metaphor_tokens = ["像", "如", "仿佛", "好比", "宛如", "犹如", "似的", "\u822c"]
    metaphor_hits = sum(len(re.findall(re.escape(t), text)) for t in metaphor_tokens)
    # 规则6: 排比否定 — 没有……也没有……
    negation_parallel_hits = len(re.findall(r'没有.{1,30}也没有', text))
    # 规则8: 填充词 — 不知道… / 不由得 / 下意识
    filler_hits = sum(len(re.findall(pat, text)) for pat in [
        r'不知道.{1,20}[。，]',
        r'不由得.{1,10}[。，]',
        r'下意识.{1,10}[。，]',
    ])

    risks = []
    # 原有规则
    if connector_hits >= 6:
        risks.append("连接词偏多，容易出现解释腔")
    if ai_taste_hits >= 6:
        risks.append("抽象判断词偏多，AI 味偏重")
    if dialogue_hits == 0 and action_hits < 6:
        risks.append("动作与对话锚点偏少，段落可能发虚")
    if avg_para_len and avg_para_len > 120:
        risks.append("段落整体偏长，节奏可能过平")
    if sentence_count and len(paragraphs) and sentence_count / max(len(paragraphs), 1) > 5:
        risks.append("单段句子偏密，建议拆节奏")

    # 老司机定制规则风险
    if contrast_pattern_hits >= 2:
        risks.append("不是…而是/不像…而像 句式偏多，AI 腔明显")
    if paragraphs and multi_sentence_paras / max(len(paragraphs), 1) > 0.3:
        risks.append("多句号段落占比偏高，建议拆段（一段一意）")
    if paragraphs and metaphor_hits / max(len(paragraphs), 1) > 0.5:
        risks.append("比喻密度偏高，一段可能有多个比喻堆叠")
    if negation_parallel_hits >= 1:
        risks.append("出现「没有…也没有…」排比否定句式，建议改写")
    if filler_hits >= 2:
        risks.append("「不知道…/不由得/下意识」填充词偏多")

    return {
        "paragraphCount": len(paragraphs),
        "sentenceCount": sentence_count,
        "connectorHits": connector_hits,
        "aiTasteHits": ai_taste_hits,
        "dialogueHits": dialogue_hits,
        "actionHits": action_hits,
        "avgParagraphLength": avg_para_len,
        "contrastPatternHits": contrast_pattern_hits,
        "multiSentenceParagraphs": multi_sentence_paras,
        "metaphorHits": metaphor_hits,
        "negationParallelHits": negation_parallel_hits,
        "fillerHits": filler_hits,
        "risks": risks,
    }


def infer_level(stats: dict) -> str:
    score = 0
    score += 1 if stats["connectorHits"] >= 6 else 0
    score += 1 if stats["aiTasteHits"] >= 6 else 0
    score += 1 if stats["dialogueHits"] == 0 else 0
    score += 1 if stats["actionHits"] < 6 else 0
    score += 1 if stats["avgParagraphLength"] and stats["avgParagraphLength"] > 120 else 0
    # 老司机定制规则加分
    score += 1 if stats["contrastPatternHits"] >= 2 else 0
    score += 1 if stats["fillerHits"] >= 2 else 0
    score += 1 if stats["negationParallelHits"] >= 1 else 0
    if score >= 5:
        return "heavy"
    if score >= 3:
        return "medium"
    return "light"


def build_revision_guidance(stats: dict, level: str) -> list[str]:
    guidance = [
        "优先删掉解释性连接词，能直说就直说。",
        "优先把抽象判断改成动作、停顿、感官或对话承载。",
        "不要追求句句工整，适当放短句、碎句、留白。",
        "人物说话尽量拉开差异，不要统一模型腔。",
    ]
    if level in {"medium", "heavy"}:
        guidance.append("本次去AI味强度不低，修稿时允许轻度拆句和节奏重排。")
    if level == "heavy":
        guidance.append("本次为 heavy 档，允许明显压缩解释腔和抽象判断，但仍不要改剧情事实。")

    # 原有规则指引
    if stats["connectorHits"] >= 6:
        guidance.append("本稿连接词偏多，修稿时优先压「因此/同时/然而/此外」这一类。")
    if stats["aiTasteHits"] >= 6:
        guidance.append("本稿抽象评价词偏多，优先删「重要/意味着/本质上/可以说」这类抬高句。")
    if stats["dialogueHits"] == 0:
        guidance.append("本稿对话锚点少，若章节允许，可补一两个短对话或内在反应点。")
    if stats["actionHits"] < 6:
        guidance.append("本稿动作动词偏少，建议多用「看/抬/顿/退/握/坐/推」之类具体动作承情绪。")

    # 老司机定制规则指引
    if stats["contrastPatternHits"] >= 2:
        guidance.append("本稿「不是…而是/不像…而像」句式偏多，优先拆掉对比结构，直接说结论。")
    if stats["multiSentenceParagraphs"] > 0:
        para_count = stats["paragraphCount"]
        if para_count and stats["multiSentenceParagraphs"] / max(para_count, 1) > 0.3:
            guidance.append("本稿多句号段落占比高，建议将多个句号的段落拆成短段，一段一意。")
        elif stats["multiSentenceParagraphs"] >= 3:
            guidance.append("本稿存在多句号段落，检查是否可拆段以打破匀称节奏。")
    if stats["metaphorHits"] > 0 and stats["paragraphCount"]:
        if stats["metaphorHits"] / max(stats["paragraphCount"], 1) > 0.5:
            guidance.append("本稿比喻密度偏高，建议每段最多保留一个比喻，其余砍掉。")
    if stats["negationParallelHits"] >= 1:
        guidance.append("本稿出现「没有…也没有…」排比否定句式，建议改写成更自然的表达。")
    if stats["fillerHits"] >= 2:
        guidance.append("本稿「不知道/不由得/下意识」填充词偏多，建议删掉填充词，用动作/反应代替。")

    return guidance


def conservative_rewrite(text: str, level: str) -> str:
    rewritten = text

    # 原有词级替换
    replacements = [
        ("某种程度上", "有点"),
        ("可以说", "算是"),
        ("换句话说", "说白了"),
        ("本质上", "说到底"),
        ("进一步", "再往下"),
        ("某种意义上", "往轻里说"),
    ]
    if level in {"medium", "heavy"}:
        replacements += [
            ("这意味着", "这就让"),
            ("这很重要", "这事不小"),
            ("显得尤为重要", "一下子就变得扎眼"),
        ]

    # 老司机定制：填充词替换
    if level in {"medium", "heavy"}:
        replacements += [
            ("不由得", ""),
            ("下意识地", ""),
            ("下意识", ""),
        ]

    for old, new in replacements:
        rewritten = rewritten.replace(old, new)

    # 原有连接词清理
    rewritten = re.sub(r"因此，?", "", rewritten)
    rewritten = re.sub(r"此外，?", "", rewritten)
    rewritten = re.sub(r"与此同时，?", "", rewritten)
    rewritten = re.sub(r"然而，?", "但", rewritten)
    rewritten = re.sub(r"不过，?", "但", rewritten)

    # 老司机定制：标记 "不是…而是…" 句式供人工审核
    # 保守策略：加注释标记，不直接改写（避免改错）
    rewritten = re.sub(
        r'(不是.{1,30}而是.{1,30}?[。，])',
        r'<!-- HUMANIZE: 对比句式，建议改写 -->\1',
        rewritten,
    )
    rewritten = re.sub(
        r'(没有.{1,30}也没有.{1,30}?[。，])',
        r'<!-- HUMANIZE: 排比否定，建议改写 -->\1',
        rewritten,
    )

    # 段落级处理
    paragraphs = rewritten.split("\n\n")
    new_paragraphs = []
    for para in paragraphs:
        p = para.strip()
        if not p:
            new_paragraphs.append(para)
            continue

        # 原有：长段落轻度拆分
        if level in {"medium", "heavy"} and len(p) > 140 and "，" in p and "\u201c" not in p:
            p = p.replace("，", "。", 1)
        if level == "heavy" and len(p) > 180 and "，" in p:
            p = p.replace("，", "。", 1)

        # 老司机定制：heavy 模式下对多句号段落尝试拆分
        if level == "heavy" and len(re.findall(r'[。！？!?]', p)) >= 2 and '\u201c' not in p:
            # 在第一个句号处拆段（如果段落够长）
            sentences = re.split(r'(?<=[。！？!?])', p, maxsplit=1)
            if len(sentences) == 2 and len(sentences[0]) > 20:
                p = sentences[0].strip() + "\n\n" + sentences[1].strip()

        new_paragraphs.append(p)

    rewritten = "\n\n".join(new_paragraphs)
    return rewritten


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: humanize_pass.py <project-dir> <chapter-id> [light|medium|heavy]")
        return 1

    root = Path(sys.argv[1]).expanduser().resolve()
    chapter_id = sys.argv[2]
    source = find_candidate_chapter(root, chapter_id)
    if not source:
        print(f"[error] chapter source not found for: {chapter_id}")
        return 1

    logs_dir = root / ".novel-studio" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    output = logs_dir / f"{chapter_id}-humanize-pass.md"

    checklist_text = read_text(CHECKLIST) if CHECKLIST.exists() else ""
    source_text = read_text(source)
    stats = analyze_text(source_text)
    requested_level = sys.argv[3].strip().lower() if len(sys.argv) >= 4 else ""
    level = requested_level if requested_level in {"light", "medium", "heavy"} else infer_level(stats)
    guidance = build_revision_guidance(stats, level)
    rewritten = conservative_rewrite(source_text, level)

    lines = []
    lines.append(f"# {chapter_id} 去AI味（humanize）工作稿")
    lines.append("")
    lines.append("## 生成信息")
    lines.append("")
    lines.append(f"- 生成时间（UTC）：{datetime.now(timezone.utc).isoformat()}")
    lines.append(f"- 来源章节：`{source.relative_to(root)}`")
    lines.append("- 内部能力名：`humanize`")
    lines.append("- 用户侧中文名：`去AI味`")
    lines.append(f"- 去AI味强度：`{level}`")
    lines.append("- 当前策略：保守旁路输出，不直接覆盖原章")
    lines.append("")
    lines.append("## 快速诊断")
    lines.append("")
    lines.append(f"- 段落数：{stats['paragraphCount']}")
    lines.append(f"- 句子数（粗略）：{stats['sentenceCount']}")
    lines.append(f"- 连接词命中：{stats['connectorHits']}")
    lines.append(f"- AI 味词命中：{stats['aiTasteHits']}")
    lines.append(f"- 对话锚点：{stats['dialogueHits']}")
    lines.append(f"- 动作动词命中：{stats['actionHits']}")
    lines.append(f"- 平均段长：{stats['avgParagraphLength']}")
    lines.append("")
    lines.append("### 老司机定制指标 (2026-06-11)")
    lines.append("")
    lines.append(f"- 对比转折句式（不是…而是/不像…而像）：{stats['contrastPatternHits']}")
    lines.append(f"- 多句号段落（>=2 句号）：{stats['multiSentenceParagraphs']}")
    lines.append(f"- 比喻词命中（像/如/仿佛/好比…）：{stats['metaphorHits']}")
    lines.append(f"- 排比否定（没有…也没有…）：{stats['negationParallelHits']}")
    lines.append(f"- 填充词命中（不知道/不由得/下意识）：{stats['fillerHits']}")
    lines.append("")
    lines.append("## 去AI味风险提示")
    lines.append("")
    if stats["risks"]:
        for item in stats["risks"]:
            lines.append(f"- {item}")
    else:
        lines.append("- 当前未见特别突出的 AI 味风险，可做轻量去AI味。")
    lines.append("")
    lines.append("## 修订指令（可直接给模型/编辑者）")
    lines.append("")
    for item in guidance:
        lines.append(f"- {item}")
    lines.append("")

    # ── AI 评分（去AI味前后对比）──
    if HAS_AI_SCORING:
        before_score = score_full(source_text, source_label=f"{chapter_id} (原始)")
        after_score = score_full(rewritten, source_label=f"{chapter_id} (去AI味后)")
        delta = round(after_score.overall_score - before_score.overall_score, 1)
        delta_str = f"+{delta}" if delta > 0 else str(delta)

        lines.append("## 🎯 AI味评分（去AI味前后对比）")
        lines.append("")
        lines.append(f"| 状态 | 综合分 | 显性AI味 | 结构性AI味 | 隐性AI味 | 等级 |")
        lines.append(f"|------|--------|----------|------------|----------|------|")

        b_dims = {d.key: d.score for d in before_score.dimension_overall}
        a_dims = {d.key: d.score for d in after_score.dimension_overall}
        lines.append(
            f"| 去AI味前 | **{before_score.overall_score}/10** | "
            f"{b_dims.get('overt', '-')} | {b_dims.get('structural', '-')} | "
            f"{b_dims.get('subtle', '-')} | {_score_to_grade(before_score.overall_score)[:3]} |"
        )
        lines.append(
            f"| 去AI味后 | **{after_score.overall_score}/10** | "
            f"{a_dims.get('overt', '-')} | {a_dims.get('structural', '-')} | "
            f"{a_dims.get('subtle', '-')} | {_score_to_grade(after_score.overall_score)[:3]} |"
        )
        lines.append(
            f"| 📈 提升 | **{delta_str}** | "
            f"{_dim_delta(b_dims, a_dims, 'overt')} | "
            f"{_dim_delta(b_dims, a_dims, 'structural')} | "
            f"{_dim_delta(b_dims, a_dims, 'subtle')} | — |"
        )
        lines.append("")

        # 分段评分摘要
        lines.append("### 分段评分")
        lines.append("")
        lines.append("| 段落 | 去AI味前 | 去AI味后 | 变化 |")
        lines.append("|------|----------|----------|------|")
        for i, (bs, as_) in enumerate(zip(before_score.segments, after_score.segments), 1):
            seg_delta = round(as_.overall - bs.overall, 1)
            seg_delta_str = f"+{seg_delta}" if seg_delta > 0 else str(seg_delta)
            flag = "🟢" if as_.overall >= 7 else ("🟡" if as_.overall >= 5 else "🔴")
            lines.append(f"| {flag} 段{i} | {bs.overall} | {as_.overall} | {seg_delta_str} |")
        lines.append("")

        # 修改建议
        if after_score.suggestions:
            lines.append("### 评分建议")
            lines.append("")
            for s in after_score.suggestions:
                lines.append(f"- {s}")
            lines.append("")

    lines.append("")
    lines.append("## 去AI味处理建议")
    lines.append("")
    lines.append("请对照以下原则，人工或后续脚本继续处理：")
    lines.append("")
    for raw in checklist_text.splitlines():
        lines.append(raw)
    lines.append("")
    lines.append("## 去AI味初稿（自动保守改写版）")
    lines.append("")
    lines.append(rewritten.rstrip())
    lines.append("")
    lines.append("## 原文存档")
    lines.append("")
    lines.append(source_text.rstrip())
    lines.append("")

    write_text(output, "\n".join(lines))
    print(f"[ok] humanize sidecar written: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

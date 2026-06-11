#!/usr/bin/env python3
"""
ai_scoring.py — AI味评分引擎

为小说正文提供 0-10 分的 AI 味量化评分。
10 分 = 完全看不出 AI / 0 分 = 100% AI 生成。

核心特性：
  - 三维度评分：显性AI味 / 结构性AI味 / 隐性AI味
  - 分段打分：逐段计算得分 + 全文汇总
  - 可独立命令行使用，也可被 humanize_pass.py 导入
  - 输出去AI味前后对比（before/after delta）

用法：
  # 独立评分
  python3 ai_scoring.py <project-dir> <chapter-id>

  # 对比评分（去AI味前后）
  python3 ai_scoring.py <project-dir> <chapter-id> --compare <humanized-file>

  # JSON 输出（供脚本调用）
  python3 ai_scoring.py <project-dir> <chapter-id> --json
"""

from pathlib import Path
import sys
import json
import re
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Optional

# 尝试导入 ns_io_local，失败则使用内置读写
try:
    from ns_io_local import read_text, write_text
except ImportError:
    def read_text(path: Path) -> str:
        return path.read_text(encoding="utf-8")
    def write_text(path: Path, text: str) -> None:
        path.write_text(text, encoding="utf-8")


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent


# ────────────────────────────────────────
#  评分数据结构
# ────────────────────────────────────────

@dataclass
class DimensionScore:
    """单个维度的评分"""
    name: str                    # 维度名称
    key: str                     # 维度键名
    description: str             # 维度说明
    raw_score: float             # 原始得分 (0-10)
    penalties: list[dict] = field(default_factory=list)  # 扣分明细
    max_penalty: float = 10.0

    @property
    def score(self) -> float:
        return max(0.0, round(self.raw_score, 1))


@dataclass
class SegmentScore:
    """单个段落的评分"""
    index: int                   # 段落序号 (1-based)
    text_preview: str            # 段落前50字预览
    char_count: int              # 段落字数
    dimensions: list[DimensionScore]
    overall: float               # 段落综合分


@dataclass
class ScoringReport:
    """完整评分报告"""
    source: str                  # 来源标识
    timestamp: str               # 评分时间
    total_paragraphs: int
    total_chars: int
    segments: list[SegmentScore] = field(default_factory=list)
    dimension_overall: list[DimensionScore] = field(default_factory=list)
    overall_score: float = 0.0   # 全文综合分
    lowest_segment: Optional[dict] = None   # 最低分段落
    suggestions: list[str] = field(default_factory=list)


# ────────────────────────────────────────
#  检测工具函数
# ────────────────────────────────────────

def _count_pattern(text: str, pattern: str) -> int:
    """正则匹配计数"""
    return len(re.findall(pattern, text))


def _has_any(text: str, tokens: list[str]) -> int:
    """统计 tokens 在文本中出现的总次数"""
    return sum(text.count(t) for t in tokens)


# ────────────────────────────────────────
#  维度一：显性AI味（高AI率）
#  一眼看出的AI痕迹
# ────────────────────────────────────────

D1_PATTERNS = {
    "机械对比句式（不是…而是…）": {
        "pattern": r'不是.{1,30}而是',
        "penalty": 3.0,
        "desc": "先否定再肯定的模板腔"
    },
    "机械对比句式（不像…而像…）": {
        "pattern": r'不像.{1,30}而像',
        "penalty": 3.0,
        "desc": "先否定再肯定的模板腔"
    },
    "排比否定（没有…也没有…）": {
        "pattern": r'没有.{1,30}也没有',
        "penalty": 2.5,
        "desc": "排比式否定，像答题"
    },
    "填充词（不知道…）": {
        "pattern": r'不知道.{1,20}[。，]',
        "penalty": 2.0,
        "desc": "作者替角色解释情绪"
    },
    "填充词（不由得）": {
        "pattern": r'不由得',
        "penalty": 1.5,
        "desc": "替角色解释行为原因"
    },
    "填充词（下意识）": {
        "pattern": r'下意识',
        "penalty": 1.5,
        "desc": "替角色解释行为原因"
    },
    "情绪标签直贴": {
        "pattern": r'感到.{1,10}[，。]|显得.{1,10}[，。]',
        "penalty": 1.0,
        "desc": "直接贴情绪标签而非呈现"
    },
    "物件当主语": {
        "pattern": r'(空气|气氛|灯光|沉默|氛围).{1,20}(传来|弥漫|笼罩|洒落|透着|充满)',
        "penalty": 1.0,
        "desc": "物件或抽象概念做主语"
    },
    "说明腔动作": {
        "pattern": r'(将.{1,10}放置|把.{1,10}转向|迈动步伐|伸出手来.{1,10}打开)',
        "penalty": 1.0,
        "desc": "动作描写过于说明书化"
    },
}


def score_dimension_1(text: str, segment_length: int) -> DimensionScore:
    """维度一：显性AI味评分"""
    penalties = []
    total_penalty = 0.0

    for name, cfg in D1_PATTERNS.items():
        hits = _count_pattern(text, cfg["pattern"])
        if hits > 0:
            p = min(cfg["penalty"] * hits, 6.0)  # 单类型最多扣6分
            total_penalty += p
            penalties.append({
                "name": name,
                "hits": hits,
                "penalty": round(p, 1),
                "desc": cfg["desc"]
            })

    raw = 10.0 - total_penalty
    return DimensionScore(
        name="显性AI味",
        key="overt",
        description="一眼看出的AI痕迹：对比句式、填充词、情绪标签、物件主语等",
        raw_score=raw,
        penalties=penalties
    )


# ────────────────────────────────────────
#  维度二：结构性AI味（中AI率）
#  读几段后察觉的结构模式
# ────────────────────────────────────────

D2_CONNECTORS = ["因此", "此外", "同时", "然而", "不仅", "而且", "于是", "不过", "与此同时"]
D2_EXPLAIN_WORDS = ["重要", "意味着", "某种程度上", "可以说", "本质上", "换句话说", "进一步", "某种意义上"]
D2_METAPHOR_WORDS = ["像", "如", "仿佛", "好比", "宛如", "犹如", "似的"]


def score_dimension_2(text: str, segment_length: int, paragraph_count: int) -> DimensionScore:
    """维度二：结构性AI味评分"""
    penalties = []
    total_penalty = 0.0

    # 连接词密度
    connector_hits = _has_any(text, D2_CONNECTORS)
    density = connector_hits / max(segment_length, 1) * 100
    if density > 3:
        p = min(round((density - 3) * 0.8, 1), 4.0)
        total_penalty += p
        penalties.append({
            "name": "连接词密度过高",
            "hits": connector_hits,
            "penalty": round(p, 1),
            "desc": f"连接词密度 {density:.1f}%，建议 <3%"
        })

    # 解释腔（抽象判断词）
    explain_hits = _has_any(text, D2_EXPLAIN_WORDS)
    if explain_hits >= 2:
        p = min(explain_hits * 0.8, 4.0)
        total_penalty += p
        penalties.append({
            "name": "解释腔（抽象判断词）",
            "hits": explain_hits,
            "penalty": round(p, 1),
            "desc": "抽象评价词偏多，建议用动作代替"
        })

    # 比喻堆叠（同一段内）
    metaphor_hits = _has_any(text, D2_METAPHOR_WORDS)
    if metaphor_hits >= 3:
        p = min((metaphor_hits - 2) * 1.0, 4.0)
        total_penalty += p
        penalties.append({
            "name": "比喻堆叠",
            "hits": metaphor_hits,
            "penalty": round(p, 1),
            "desc": "一段里比喻词过多，建议每段最多一个"
        })

    # 多句号段落（在全文中检测，这里只对段落本身）
    period_count = _count_pattern(text, r'[。！？!?]')
    if period_count >= 2 and text.count('"') + text.count('\u201c') < 2:
        p = min((period_count - 1) * 0.5, 3.0)
        total_penalty += p
        penalties.append({
            "name": "多句号段落",
            "hits": period_count,
            "penalty": round(p, 1),
            "desc": "一段多句，节奏太平，建议拆段"
        })

    raw = 10.0 - total_penalty
    return DimensionScore(
        name="结构性AI味",
        key="structural",
        description="读几段后察觉的模式：连接词密度、比喻堆叠、解释腔、段落结构",
        raw_score=raw,
        penalties=penalties
    )


# ────────────────────────────────────────
#  维度三：隐性AI味（低AI率）
#  细细品味才会察觉的微妙痕迹
# ────────────────────────────────────────

D3_VAGUE_WORDS = ["微微", "缓缓", "轻轻", "仿佛", "似乎", "某种", "一丝",
                   "几分", "隐隐", "些许", "略微", "稍稍", "略微"]
D3_ABSTRACT_WORDS = ["意义", "本质", "存在", "生命", "灵魂", "命运", "内心",
                      "感受", "情绪", "意识", "境界", "层次"]


def score_dimension_3(text: str, segment_length: int) -> DimensionScore:
    """维度三：隐性AI味评分"""
    penalties = []
    total_penalty = 0.0

    # 虚化词密度
    vague_hits = _has_any(text, D3_VAGUE_WORDS)
    vague_density = vague_hits / max(segment_length, 1) * 100
    if vague_density > 2:
        p = min(round((vague_density - 2) * 0.5, 1), 3.0)
        total_penalty += p
        penalties.append({
            "name": "虚化词密度偏高",
            "hits": vague_hits,
            "penalty": round(p, 1),
            "desc": f"虚化词密度 {vague_density:.1f}%，像滤镜开太大"
        })

    # 抽象词密度
    abstract_hits = _has_any(text, D3_ABSTRACT_WORDS)
    abstract_density = abstract_hits / max(segment_length, 1) * 100
    if abstract_density > 3:
        p = min(round((abstract_density - 3) * 0.4, 1), 3.0)
        total_penalty += p
        penalties.append({
            "name": "抽象词密度偏高",
            "hits": abstract_hits,
            "penalty": round(p, 1),
            "desc": f"抽象词密度 {abstract_density:.1f}%，容易发虚"
        })

    # 的密度（形容修饰密度）
    de_count = text.count("的")
    de_density = de_count / max(segment_length, 1) * 100
    if de_density > 6:
        p = min(round((de_density - 6) * 0.3, 1), 2.0)
        total_penalty += p
        penalties.append({
            "name": "「的」密度偏高",
            "hits": de_count,
            "penalty": round(p, 1),
            "desc": f"形容修饰密度 {de_density:.1f}%，句子可能偏肿"
        })

    # 句子长度方差（用标点间隔粗略估算）
    sentences = re.split(r'[。！？!?\n]', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]
    if len(sentences) >= 3:
        lengths = [len(s) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        if avg_len > 0:
            # 计算变异系数 CV = std/mean
            variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
            cv = (variance ** 0.5) / avg_len if avg_len > 0 else 0
            if cv < 0.2:  # 句长太均匀
                p = round((0.2 - cv) * 10, 1)
                p = min(p, 2.0)
                total_penalty += p
                penalties.append({
                    "name": "句长过于均匀",
                    "hits": len(sentences),
                    "penalty": round(p, 1),
                    "desc": f"句长变异系数 {cv:.2f}，太匀称像AI"
                })

    raw = 10.0 - total_penalty
    return DimensionScore(
        name="隐性AI味",
        key="subtle",
        description="细细品味才察觉的痕迹：虚化词密度、抽象词密度、形容密度、句长均匀度",
        raw_score=raw,
        penalties=penalties
    )


# ────────────────────────────────────────
#  评分引擎
# ────────────────────────────────────────

def score_segment(text: str, index: int, total_paras: int) -> SegmentScore:
    """对单个段落进行三维度评分"""
    text = text.strip()
    if not text:
        return SegmentScore(
            index=index,
            text_preview="(空段落)",
            char_count=0,
            dimensions=[],
            overall=10.0
        )

    d1 = score_dimension_1(text, len(text))
    d2 = score_dimension_2(text, len(text), total_paras)
    d3 = score_dimension_3(text, len(text))

    # 综合分 = 加权平均（显性权重最高）
    overall = round(d1.score * 0.45 + d2.score * 0.30 + d3.score * 0.25, 1)

    return SegmentScore(
        index=index,
        text_preview=text[:50].replace("\n", " ") + ("…" if len(text) > 50 else ""),
        char_count=len(text),
        dimensions=[d1, d2, d3],
        overall=overall
    )


def score_full(text: str, source_label: str = "") -> ScoringReport:
    """对全文进行评分（分段 + 汇总）"""
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [p for p in text.split("\n") if p.strip()]

    segments = []
    d1_total, d2_total, d3_total = 0.0, 0.0, 0.0
    lowest_score = 10.0
    lowest_idx = 0
    all_penalties: dict[str, list] = {"overt": [], "structural": [], "subtle": []}

    for i, para in enumerate(paragraphs, 1):
        seg = score_segment(para, i, len(paragraphs))
        segments.append(seg)

        for dim in seg.dimensions:
            if dim.key == "overt":
                d1_total += dim.score
                all_penalties["overt"].extend(dim.penalties)
            elif dim.key == "structural":
                d2_total += dim.score
                all_penalties["structural"].extend(dim.penalties)
            elif dim.key == "subtle":
                d3_total += dim.score
                all_penalties["subtle"].extend(dim.penalties)

        if seg.overall < lowest_score:
            lowest_score = seg.overall
            lowest_idx = i

    n = len(segments)
    d1_avg = round(d1_total / n, 1) if n > 0 else 10.0
    d2_avg = round(d2_total / n, 1) if n > 0 else 10.0
    d3_avg = round(d3_total / n, 1) if n > 0 else 10.0
    overall = round(sum(s.overall for s in segments) / n, 1) if n > 0 else 10.0

    # 构建维度汇总
    dim_summary = [
        DimensionScore(
            name="显性AI味",
            key="overt",
            description="一眼看出的AI痕迹",
            raw_score=d1_avg,
            penalties=_merge_penalties(all_penalties["overt"])
        ),
        DimensionScore(
            name="结构性AI味",
            key="structural",
            description="读几段后察觉的模式",
            raw_score=d2_avg,
            penalties=_merge_penalties(all_penalties["structural"])
        ),
        DimensionScore(
            name="隐性AI味",
            key="subtle",
            description="细细品味才察觉的痕迹",
            raw_score=d3_avg,
            penalties=_merge_penalties(all_penalties["subtle"])
        ),
    ]

    # 生成建议
    suggestions = _generate_suggestions(dim_summary, segments)

    # 最低分段落信息
    lowest_info = None
    if n > 0 and lowest_idx > 0:
        lowest_seg = segments[lowest_idx - 1]
        lowest_info = {
            "index": lowest_idx,
            "score": lowest_seg.overall,
            "preview": lowest_seg.text_preview,
            "top_penalties": _get_top_penalties(lowest_seg)
        }

    return ScoringReport(
        source=source_label or "未知来源",
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_paragraphs=n,
        total_chars=sum(s.char_count for s in segments),
        segments=segments,
        dimension_overall=dim_summary,
        overall_score=overall,
        lowest_segment=lowest_info,
        suggestions=suggestions
    )


def _merge_penalties(penalties: list[dict]) -> list[dict]:
    """合并同类扣分项"""
    merged: dict[str, dict] = {}
    for p in penalties:
        name = p["name"]
        if name in merged:
            merged[name]["hits"] += p["hits"]
            merged[name]["penalty"] = round(merged[name]["penalty"] + p["penalty"], 1)
        else:
            merged[name] = dict(p)
    return sorted(merged.values(), key=lambda x: x["penalty"], reverse=True)


def _get_top_penalties(seg: SegmentScore) -> list[dict]:
    """获取段落中扣分最多的几项"""
    all_pens = []
    for dim in seg.dimensions:
        all_pens.extend(dim.penalties)
    return sorted(all_pens, key=lambda x: x["penalty"], reverse=True)[:5]


def _generate_suggestions(dims: list[DimensionScore], segments: list[SegmentScore]) -> list[str]:
    """根据评分结果生成修改建议"""
    suggestions = []

    for dim in dims:
        if dim.score < 5:
            suggestions.append(f"⚠️ {dim.name}得分 {dim.score}/10，需重点关注")
            for p in dim.penalties[:3]:
                suggestions.append(f"  → {p['name']}：{p['desc']} (命中 {p['hits']} 次)")
        elif dim.score < 7:
            suggestions.append(f"⚡ {dim.name}得分 {dim.score}/10，建议改进")

    # 找最低分段
    if segments:
        worst = min(segments, key=lambda s: s.overall)
        if worst.overall < 5:
            suggestions.append(f"🔴 第 {worst.index} 段评分最低 ({worst.overall}/10)，建议优先修改")
        elif worst.overall < 6.5:
            suggestions.append(f"🟡 第 {worst.index} 段评分偏低 ({worst.overall}/10)")

    if not suggestions:
        suggestions.append("✅ 整体表现良好，未发现明显 AI 味问题")

    return suggestions


# ────────────────────────────────────────
#  CLI 主入口
# ────────────────────────────────────────

def _find_chapter_source(root: Path, chapter_id: str) -> Path | None:
    candidates = [
        root / "chapters" / "candidates" / f"{chapter_id}.md",
        root / "chapters" / "published" / f"{chapter_id}.md",
        root / "chapters" / f"{chapter_id}.md",
    ]
    for p in candidates:
        if p.exists():
            return p
    for p in root.rglob(f"{chapter_id}.md"):
        if ".novel-studio" in p.parts:
            continue
        return p
    return None


def _score_to_grade(score: float) -> str:
    """分数转等级"""
    if score >= 9:
        return "S (几乎无AI味)"
    if score >= 8:
        return "A (少量AI味)"
    if score >= 7:
        return "B (轻微AI味)"
    if score >= 6:
        return "C (中等AI味)"
    if score >= 4:
        return "D (明显AI味)"
    if score >= 2:
        return "E (严重AI味)"
    return "F (纯AI腔)"


def _format_report(report: ScoringReport, compare_report: Optional[ScoringReport] = None) -> str:
    """格式化评分报告为 Markdown"""
    lines = []
    lines.append(f"# AI味评分报告 — {report.source}")
    lines.append("")
    lines.append(f"- 评分时间：{report.timestamp}")
    lines.append(f"- 总段落数：{report.total_paragraphs}")
    lines.append(f"- 总字数：{report.total_chars}")

    # 综合评分
    lines.append("")
    lines.append("## 📊 综合评分")
    lines.append("")
    grade = _score_to_grade(report.overall_score)
    lines.append(f"| 综合分 | 等级 |")
    lines.append(f"|--------|------|")
    lines.append(f"| **{report.overall_score}/10** | **{grade}** |")

    # 对比
    if compare_report:
        delta = round(report.overall_score - compare_report.overall_score, 1)
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        lines.append(f"| 去AI味前 | {compare_report.overall_score}/10 |")
        lines.append(f"| 去AI味后 | {report.overall_score}/10 |")
        lines.append(f"| 提升 | **{delta_str}** |")
        lines.append("")

    # 三维度评分
    lines.append("")
    lines.append("## 🎯 三维度评分")
    lines.append("")
    lines.append("| 维度 | 得分 | 评级 | 说明 |")
    lines.append("|------|------|------|------|")
    for dim in report.dimension_overall:
        dim_grade = "🟢" if dim.score >= 8 else ("🟡" if dim.score >= 6 else ("🟠" if dim.score >= 4 else "🔴"))
        lines.append(f"| {dim_grade} {dim.name} | **{dim.score}/10** | {_score_to_grade(dim.score)[:2]} | {dim.description} |")

    # 分段评分
    lines.append("")
    lines.append("## 📝 分段评分")
    lines.append("")
    lines.append("| 段落 | 字数 | 显性 | 结构 | 隐性 | 综合 |")
    lines.append("|------|------|------|------|------|------|")
    for seg in report.segments:
        d1 = seg.dimensions[0].score if len(seg.dimensions) > 0 else "-"
        d2 = seg.dimensions[1].score if len(seg.dimensions) > 1 else "-"
        d3 = seg.dimensions[2].score if len(seg.dimensions) > 2 else "-"
        flag = "🔴" if seg.overall < 5 else ("🟡" if seg.overall < 7 else "🟢")
        lines.append(f"| {flag} 段{seg.index} | {seg.char_count} | {d1} | {d2} | {d3} | **{seg.overall}** |")

    # 最低分段落详情
    if report.lowest_segment:
        lines.append("")
        lines.append("## 🔍 最低分段落")
        lines.append("")
        ls = report.lowest_segment
        lines.append(f"- 段落：第 {ls['index']} 段")
        lines.append(f"- 得分：**{ls['score']}/10**")
        lines.append(f"- 内容预览：_{ls['preview']}_")
        if ls.get("top_penalties"):
            lines.append("")
            lines.append("**主要扣分项：**")
            for p in ls["top_penalties"][:3]:
                lines.append(f"- {p['name']} (命中 {p['hits']} 次，扣 {p['penalty']} 分)")

    # 修改建议
    lines.append("")
    lines.append("## 💡 修改建议")
    lines.append("")
    for s in report.suggestions:
        lines.append(f"{s}")

    return "\n".join(lines)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="AI味评分引擎 — 0-10 分量化评估小说正文的 AI 腔程度"
    )
    parser.add_argument("project_dir", help="项目根目录")
    parser.add_argument("chapter_id", help="章节标识")
    parser.add_argument("--compare", "-c", help="去AI味后文件路径（输出前后对比）")
    parser.add_argument("--json", "-j", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--output", "-o", help="输出文件路径（默认输出到 .novel-studio/logs/）")

    args = parser.parse_args()
    root = Path(args.project_dir).expanduser().resolve()
    chapter_id = args.chapter_id

    source = _find_chapter_source(root, chapter_id)
    if not source:
        print(f"[error] 找不到章节文件: {chapter_id}")
        return 1

    source_text = read_text(source)

    # 评分
    report = score_full(source_text, source_label=f"{chapter_id} (原始)")
    compare_report = None

    if args.compare:
        compare_path = Path(args.compare).expanduser().resolve()
        if not compare_path.exists():
            print(f"[error] 对比文件不存在: {args.compare}")
            return 1
        compare_text = read_text(compare_path)
        compare_report = score_full(compare_text, source_label=f"{chapter_id} (去AI味前)")

    if args.json:
        output_data = {
            "report": asdict(report) if hasattr(report, '__dataclass_fields__') else report,
        }
        if compare_report:
            output_data["compare"] = asdict(compare_report) if hasattr(compare_report, '__dataclass_fields__') else compare_report
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
        return 0

    # 格式化输出
    report_text = _format_report(report, compare_report)
    print(report_text)

    # 保存文件
    if args.output:
        out_path = Path(args.output).expanduser().resolve()
    else:
        logs_dir = root / ".novel-studio" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        suffix = "-ai-score-compare.md" if compare_report else "-ai-score.md"
        out_path = logs_dir / f"{chapter_id}{suffix}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_text(out_path, report_text)
    print(f"\n[ok] 评分报告已保存: {out_path}")
    return 0


# ────────────────────────────────────────
#  供 humanize_pass.py 调用的接口
# ────────────────────────────────────────

def compare_scores(before_text: str, after_text: str) -> dict:
    """
    对比去AI味前后的评分。

    返回:
        {
            "before": float,     # 去AI味前综合分
            "after": float,      # 去AI味后综合分
            "delta": float,      # 提升幅度
            "before_report": dict,
            "after_report": dict,
        }
    """
    before_report = score_full(before_text, source_label="去AI味前")
    after_report = score_full(after_text, source_label="去AI味后")
    delta = round(after_report.overall_score - before_report.overall_score, 1)

    return {
        "before": before_report.overall_score,
        "after": after_report.overall_score,
        "delta": delta,
        "improved": delta > 0,
        "before_dimensions": {
            dim.key: dim.score for dim in before_report.dimension_overall
        },
        "after_dimensions": {
            dim.key: dim.score for dim in after_report.dimension_overall
        },
    }


def quick_score(text: str) -> float:
    """快速评分（仅返回综合分）"""
    report = score_full(text)
    return report.overall_score


if __name__ == "__main__":
    raise SystemExit(main())

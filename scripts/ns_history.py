#!/usr/bin/env python3
"""
ns_history.py

Novel Studio 创作历史管理。

每次小说创作/润色/修改等产生新内容的操作，生成一条独立的历史记录文件。
每条记录保存：创作目的/要求、生成模型信息、生成结果。

历史文件存储在项目目录下：
  <project>/.novel-studio/history/<timestamp>_<chapter>_<type>.md

Usage:
  python3 scripts/ns_history.py record <project> <chapter>         # 记录一条创作历史
    --type <write_chapter|rewrite|humanize|review|...>
    --purpose "<创作目的/要求>"
    --result-file <path>          # 生成结果文件路径（可选：--result-text 替代）
    --result-text "<生成结果>"     # 直接传生成结果文本
    [--model <model_name>]
    [--model-provider <provider>]
    [--model-api <api_type>]
    [--model-base-url <url>]
    [--model-temperature <float>]
    [--model-max-tokens <int>]
    [--work-mode <system|direct>]
    [--input-chars <int>]
    [--output-chars <int>]
    [--elapsed-seconds <float>]
    [--manifest-path <path>]      # direct API manifest 路径

  python3 scripts/ns_history.py list <project>                     # 列出所有历史记录
    [--chapter <id>]              # 按章节筛选
    [--type <type>]               # 按类型筛选
    [--recent <N>]                # 只看最近 N 条
    [--json]                      # JSON 格式输出

  python3 scripts/ns_history.py view <project> <history-id>        # 查看一条历史记录
    [--json]                      # JSON 格式输出（含 frontmatter）

  python3 scripts/ns_history.py delete <project> <history-id>      # 删除一条历史记录
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import re
import sys
import uuid

HISTORY_DIR = ".novel-studio"
HISTORY_SUBDIR = "history"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _project_root(project: str) -> Path:
    return Path(project).expanduser().resolve()


def _history_dir(project: str) -> Path:
    d = _project_root(project) / HISTORY_DIR / HISTORY_SUBDIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def _history_files(project: str) -> list[Path]:
    d = _project_root(project) / HISTORY_DIR / HISTORY_SUBDIR
    if not d.exists():
        return []
    return sorted(d.glob("*.md"), reverse=True)


def _parse_history_file(path: Path) -> dict:
    """Parse a history .md file: extract frontmatter (JSON) and body."""
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {"_file": str(path), "_error": "no valid frontmatter found", "body": text}
    try:
        fm = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        return {"_file": str(path), "_error": f"frontmatter parse error: {e}", "body": text}
    fm["body"] = text[m.end():]
    fm["_file"] = str(path)
    fm["_id"] = path.stem
    return fm


def _make_frontmatter(meta: dict) -> str:
    """Generate YAML-like frontmatter as embedded JSON."""
    return "---\n" + json.dumps(meta, ensure_ascii=False, indent=2) + "\n---\n"


# ── record ────────────────────────────────────────────────────────────

def cmd_record(args):
    project = args.project
    chapter = args.chapter

    # Validate result source
    if not args.result_file and not args.result_text:
        print("error: must provide --result-file or --result-text", file=sys.stderr)
        return 1
    if args.result_file and args.result_text:
        print("error: use --result-file OR --result-text, not both", file=sys.stderr)
        return 1

    # Read result content
    result_content = ""
    if args.result_file:
        rf = Path(args.result_file).expanduser()
        if not rf.exists():
            print(f"error: result file not found: {rf}", file=sys.stderr)
            return 1
        result_content = rf.read_text(encoding="utf-8")
    else:
        result_content = args.result_text or ""

    # Build frontmatter metadata
    now = datetime.now(timezone.utc)
    now_local = now.astimezone()
    ts = now_local.strftime("%Y-%m-%d_%H%M%S")
    iso_ts = now_local.isoformat()

    meta = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": iso_ts,
        "chapter_id": chapter,
        "task_type": args.type,
        "work_mode": args.work_mode or "unknown",
        "purpose": args.purpose or "",
        "model": {
            "provider": args.model_provider or "",
            "name": args.model or "",
            "api": args.model_api or "",
            "base_url": args.model_base_url or "",
            "temperature": args.model_temperature,
            "max_tokens": args.model_max_tokens,
        },
        "stats": {
            "input_chars": args.input_chars,
            "output_chars": args.output_chars or len(result_content),
            "elapsed_seconds": args.elapsed_seconds,
        },
    }
    # Trim None values from model and stats for cleaner output
    meta["model"] = {k: v for k, v in meta["model"].items() if v is not None and v != ""}
    meta["stats"] = {k: v for k, v in meta["stats"].items() if v is not None}

    if args.manifest_path:
        meta["manifest_path"] = args.manifest_path

    # Build filename
    task_type = args.type or "unknown"
    safe_type = task_type.replace("/", "-").replace(" ", "_")
    filename = f"{ts}_{chapter}_{safe_type}_{meta['id']}.md"

    # Build content
    body_parts = []
    body_parts.append(f"# 创作历史：{chapter} - {task_type}\n")
    body_parts.append("## 创作目的/要求\n")
    body_parts.append(args.purpose or "(未记录)")
    body_parts.append("\n")
    body_parts.append("## 生成模型信息\n")
    model_lines = []
    if args.model:
        model_lines.append(f"- **模型名称**: {args.model}")
    if args.model_provider:
        model_lines.append(f"- **Provider**: {args.model_provider}")
    if args.model_api:
        model_lines.append(f"- **API 协议**: {args.model_api}")
    if args.model_base_url:
        model_lines.append(f"- **Base URL**: {args.model_base_url}")
    if args.model_temperature is not None:
        model_lines.append(f"- **Temperature**: {args.model_temperature}")
    if args.model_max_tokens is not None:
        model_lines.append(f"- **Max Tokens**: {args.model_max_tokens}")
    if args.work_mode:
        model_lines.append(f"- **工作模式**: {args.work_mode}")
    if model_lines:
        body_parts.append("\n".join(model_lines))
    else:
        body_parts.append("(未记录模型信息)")
    body_parts.append("\n")
    body_parts.append("## 生成结果\n")
    body_parts.append(result_content)

    full_body = "\n".join(body_parts)
    full_content = _make_frontmatter(meta) + full_body

    # Write file
    hdir = _history_dir(project)
    out_path = hdir / filename
    out_path.write_text(full_content, encoding="utf-8")

    print(f"记录已保存: {out_path}")
    print(f"  ID:       {meta['id']}")
    print(f"  章节:     {chapter}")
    print(f"  类型:     {task_type}")
    print(f"  时间:     {iso_ts}")
    if meta["stats"].get("output_chars"):
        print(f"  输出:     {meta['stats']['output_chars']} 字符")
    return 0


# ── list ──────────────────────────────────────────────────────────────

def cmd_list(args):
    project = args.project
    files = _history_files(project)

    if not files:
        print("(暂无历史记录)")
        return 0

    entries = [_parse_history_file(f) for f in files]

    # Filter by chapter
    if args.chapter:
        entries = [e for e in entries if e.get("chapter_id") == args.chapter]

    # Filter by type
    if args.type:
        entries = [e for e in entries if e.get("task_type") == args.type]

    # Limit recent
    if args.recent and args.recent > 0:
        entries = entries[:args.recent]

    if args.json:
        out = [{k: v for k, v in e.items() if k not in ("body",)} for e in entries]
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    if not entries:
        print("(无匹配的历史记录)")
        return 0

    # Table output
    print(f"📜 创作历史 ({len(entries)} 条)")
    print("─" * 80)
    headers = ["#", "时间", "章节", "类型", "模式", "模型", "输出", "ID"]
    widths = [4, 18, 12, 16, 8, 20, 10, 10]
    header_line = " │ ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("─" * len(header_line))

    for i, e in enumerate(entries, 1):
        ts = e.get("timestamp", "")[:16].replace("T", " ")
        chapter = e.get("chapter_id", "-")
        task_type = e.get("task_type", "-")
        work_mode = e.get("work_mode", "-")
        model_name = e.get("model", {}).get("name", "-") if isinstance(e.get("model"), dict) else "-"
        stats = e.get("stats", {}) or {}
        out_chars = stats.get("output_chars", 0) or 0
        if out_chars >= 1000:
            out_str = f"{out_chars/1000:.1f}k"
        else:
            out_str = str(out_chars)
        hid = e.get("id", e.get("_id", ""))[:8]

        row = [
            str(i), ts[:16] if len(ts) > 16 else ts,
            chapter[:11], task_type[:15], work_mode[:7],
            model_name[:19], out_str[:9], hid[:9],
        ]
        print(" │ ".join(c.ljust(w) for c, w in zip(row, widths)))

    print()
    print(f"💡 使用 `ns_history.py view <project> <id>` 查看详情")
    return 0


# ── view ──────────────────────────────────────────────────────────────

def cmd_view(args):
    project = args.project
    history_id = args.history_id

    hdir = _history_dir(project)
    # Find by ID (filename stem or frontmatter id)
    found = None
    for f in _history_dir(project).glob("*.md"):
        if f.stem == history_id:
            found = f
            break
    if not found:
        # Try match by frontmatter id
        for f in _history_dir(project).glob("*.md"):
            entry = _parse_history_file(f)
            if entry.get("id") == history_id:
                found = f
                break
    if not found:
        print(f"未找到历史记录: {history_id}", file=sys.stderr)
        return 1

    entry = _parse_history_file(found)

    if args.json:
        print(json.dumps({k: v for k, v in entry.items() if k != "_file"}, ensure_ascii=False, indent=2))
        return 0

    # Pretty print
    ts = entry.get("timestamp", "?")
    chapter = entry.get("chapter_id", "?")
    task_type = entry.get("task_type", "?")
    work_mode = entry.get("work_mode", "?")
    purpose = entry.get("purpose", "")
    model_info = entry.get("model", {})

    print("═" * 60)
    print(f"📄 创作历史详情")
    print("═" * 60)
    print(f"  ID:         {entry.get('id', entry.get('_id', '?'))}")
    print(f"  时间:       {ts}")
    print(f"  章节:       {chapter}")
    print(f"  类型:       {task_type}")
    print(f"  工作模式:   {work_mode}")
    print()
    print("─" * 60)
    print("📋 创作目的/要求:")
    print("─" * 60)
    print(purpose or "(未记录)")
    print()
    print("─" * 60)
    print("🤖 生成模型信息:")
    print("─" * 60)
    if model_info:
        for k, v in model_info.items():
            if v is not None:
                print(f"  {k}: {v}")
    else:
        print("  (未记录)")
    print()

    stats = entry.get("stats", {})
    if stats:
        print("─" * 60)
        print("📊 统计:")
        print("─" * 60)
        for k, v in stats.items():
            print(f"  {k}: {v}")
        print()

    body = entry.get("body", "")
    # Find result section
    result_match = re.search(r"## 生成结果\n+(.*)", body, re.DOTALL)
    if result_match:
        result_text = result_match.group(1).strip()
        print("─" * 60)
        print(f"📝 生成结果 ({len(result_text)} 字符):")
        print("─" * 60)
        # Show preview if too long
        max_preview = 5000
        if len(result_text) > max_preview:
            print(result_text[:max_preview])
            print(f"\n... (共 {len(result_text)} 字符，显示前 {max_preview} 字符)")
            print(f"💡 查看完整内容: cat {entry.get('_file', '')}")
        else:
            print(result_text)
    else:
        print("(未找到生成结果)")

    return 0


# ── delete ────────────────────────────────────────────────────────────

def cmd_delete(args):
    project = args.project
    history_id = args.history_id

    hdir = _history_dir(project)
    found = None
    for f in hdir.glob("*.md"):
        if f.stem == history_id:
            found = f
            break
    if not found:
        for f in hdir.glob("*.md"):
            entry = _parse_history_file(f)
            if entry.get("id") == history_id:
                found = f
                break
    if not found:
        print(f"未找到历史记录: {history_id}", file=sys.stderr)
        return 1

    # Confirm
    print(f"将删除: {found.name}")
    found.unlink()
    print("已删除 ✅")
    return 0


# ── main ──────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Novel Studio 创作历史管理")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # record
    p_rec = sub.add_parser("record", help="记录一条创作历史")
    p_rec.add_argument("project", help="项目目录")
    p_rec.add_argument("chapter", help="章节 ID")
    p_rec.add_argument("--type", required=True,
                       help="任务类型: write_chapter, rewrite, humanize, review, outline, settings, style, etc.")
    p_rec.add_argument("--purpose", default="",
                       help="创作目的/要求描述")
    p_rec.add_argument("--result-file", default="",
                       help="生成结果文件路径")
    p_rec.add_argument("--result-text", default="",
                       help="生成结果文本（直接传入）")
    p_rec.add_argument("--model", default="",
                       help="生成模型名称")
    p_rec.add_argument("--model-provider", default="",
                       help="模型 Provider")
    p_rec.add_argument("--model-api", default="",
                       help="API 协议类型")
    p_rec.add_argument("--model-base-url", default="",
                       help="API Base URL")
    p_rec.add_argument("--model-temperature", type=float, default=None,
                       help="Temperature")
    p_rec.add_argument("--model-max-tokens", type=int, default=None,
                       help="Max Tokens")
    p_rec.add_argument("--work-mode", default="",
                       help="工作模式: system / direct")
    p_rec.add_argument("--input-chars", type=int, default=None,
                       help="输入字符数")
    p_rec.add_argument("--output-chars", type=int, default=None,
                       help="输出字符数")
    p_rec.add_argument("--elapsed-seconds", type=float, default=None,
                       help="生成耗时（秒）")
    p_rec.add_argument("--manifest-path", default="",
                       help="Direct API manifest 路径（可选）")

    # list
    p_ls = sub.add_parser("list", help="列出创作历史")
    p_ls.add_argument("project", help="项目目录")
    p_ls.add_argument("--chapter", default="", help="按章节筛选")
    p_ls.add_argument("--type", default="", help="按类型筛选")
    p_ls.add_argument("--recent", type=int, default=0, help="只看最近 N 条")
    p_ls.add_argument("--json", action="store_true", help="JSON 格式输出")

    # view
    p_v = sub.add_parser("view", help="查看一条创作历史")
    p_v.add_argument("project", help="项目目录")
    p_v.add_argument("history_id", help="历史记录 ID 或文件名 stem")
    p_v.add_argument("--json", action="store_true", help="JSON 格式输出")

    # delete
    p_del = sub.add_parser("delete", help="删除一条创作历史")
    p_del.add_argument("project", help="项目目录")
    p_del.add_argument("history_id", help="历史记录 ID 或文件名 stem")

    args = ap.parse_args()

    if args.cmd == "record":
        return cmd_record(args)
    elif args.cmd == "list":
        return cmd_list(args)
    elif args.cmd == "view":
        return cmd_view(args)
    elif args.cmd == "delete":
        return cmd_delete(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

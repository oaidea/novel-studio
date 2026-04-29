#!/usr/bin/env python3
"""
direct_api_writer.py

Novel Studio direct API writing executor.

Builds an isolated OpenAI-compatible chat/completions request from a chapter
input pack and optionally executes it. Default is dry-run: write request preview
and manifest only, no network call.

Usage:
  python3 scripts/direct_api_writer.py <project-dir> <chapter-id> [options]

Environment:
  NOVEL_STUDIO_API_KEY   API key env var used by default
  NOVEL_STUDIO_BASE_URL  e.g. https://api.openai.com/v1
  NOVEL_STUDIO_MODEL     model name
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib import request, error
import argparse
import json
import os
import re
import sys
import time

DEFAULT_API_KEY_ENV = "NOVEL_STUDIO_API_KEY"
DEFAULT_BASE_URL_ENV = "NOVEL_STUDIO_BASE_URL"
DEFAULT_MODEL_ENV = "NOVEL_STUDIO_MODEL"


@dataclass
class IncludedFile:
    rel: str
    chars: int
    content: str


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def project_config_path(root: Path) -> Path:
    return root / ".novel-studio" / "config.json"


def providers_from_config(data: dict) -> dict:
    if "providers" in data and isinstance(data["providers"], dict):
        return data["providers"]
    models = data.get("models")
    if isinstance(models, dict) and isinstance(models.get("providers"), dict):
        return models["providers"]
    return {}


def load_system_model(model_ref: str) -> dict | None:
    config_paths = [
        Path("/root/.openclaw/agents/main/agent/models.json"),
        Path("/root/.openclaw/openclaw.json"),
    ]
    for cfg_path in config_paths:
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        providers = providers_from_config(data)
        for provider_id, provider in providers.items():
            if not isinstance(provider, dict):
                continue
            base_url = provider.get("baseUrl") or provider.get("baseURL") or provider.get("base_url") or ""
            provider_api = provider.get("api") or ""
            for m in provider.get("models") or []:
                if not isinstance(m, dict) or not m.get("id"):
                    continue
                full = f"{provider_id}/{m['id']}"
                if model_ref not in {full, m["id"]}:
                    continue
                return {
                    "provider": provider_id,
                    "model": m["id"],
                    "modelFull": full,
                    "baseUrl": base_url,
                    "api": m.get("api") or provider_api,
                    "maxTokens": m.get("maxTokens"),
                    "source": str(cfg_path),
                }
    return None


def env_name_for(provider: str) -> str:
    safe = "".join(ch if ch.isalnum() else "_" for ch in provider.upper())
    return "NOVEL_STUDIO_API_KEY_" + safe


def read_project_direct_api(root: Path) -> tuple[dict | None, Path]:
    cfg_path = project_config_path(root)
    if not cfg_path.exists():
        return None, cfg_path
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        direct = cfg.get("directApi")
        if isinstance(direct, dict):
            return direct, cfg_path
    except Exception:
        pass
    return None, cfg_path


def safe_rel(root: Path, raw: str) -> Path | None:
    raw = raw.strip().strip("`").strip()
    if not raw or raw.startswith(("http://", "https://")):
        return None
    p = (root / raw).resolve()
    try:
        p.relative_to(root)
    except ValueError:
        return None
    if not p.exists() or not p.is_file():
        return None
    return p


def extract_pack_paths(root: Path, input_pack: Path) -> list[Path]:
    text = read_text(input_pack)
    paths: list[Path] = []
    seen: set[Path] = set()
    for match in re.finditer(r"`([^`]+)`", text):
        p = safe_rel(root, match.group(1))
        if p and p not in seen:
            paths.append(p)
            seen.add(p)
    return paths


def load_included_files(root: Path, paths: list[Path], max_chars_per_file: int, max_total_chars: int) -> list[IncludedFile]:
    included: list[IncludedFile] = []
    total = 0
    for p in paths:
        content = read_text(p)
        if len(content) > max_chars_per_file:
            content = content[:max_chars_per_file] + "\n\n[TRUNCATED by direct_api_writer max_chars_per_file]\n"
        if total + len(content) > max_total_chars:
            remaining = max_total_chars - total
            if remaining <= 0:
                break
            content = content[:remaining] + "\n\n[TRUNCATED by direct_api_writer max_total_chars]\n"
        rel = str(p.relative_to(root))
        included.append(IncludedFile(rel=rel, chars=len(content), content=content))
        total += len(content)
        if total >= max_total_chars:
            break
    return included


def build_messages(chapter_id: str, project_name: str, included: list[IncludedFile], prompt_profile: str, user_instruction: str) -> list[dict]:
    system = f"""你是 Novel Studio 的隔离写作执行模型。\n\n规则：\n- 只使用本次请求中提供的项目资料，不使用任何外部聊天历史或未提供设定。\n- 不擅自改核心设定；缺信息时用最小假设，并在输出末尾用 [待确认] 标注。\n- 写小说正文时，不输出分析过程、任务书或解释，除非用户指令要求。\n- 保持项目风格、人物状态、信息边界和章节 packet 约束。\n- 不把项目管理说明写进正文。\n\n项目：{project_name}\n章节：{chapter_id}\n模式：{prompt_profile}\n"""
    blocks = []
    for item in included:
        blocks.append(f"## FILE: {item.rel}\n\n{item.content}")
    user = f"""# Novel Studio Direct API Input\n\n## Chapter\n{chapter_id}\n\n## User Instruction\n{user_instruction or '请基于以下 input pack 资料，生成本章正文候选稿。'}\n\n## Included Project Files\n\n""" + "\n\n---\n\n".join(blocks) + "\n\n## Output Requirement\n- 默认只输出正文候选稿。\n- 不输出你如何思考。\n- 若资料不足以安全写作，在末尾加 [待确认] 列出缺口。\n"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def chat_completions(base_url: str, api_key: str, payload: dict, timeout: int) -> dict:
    url = base_url.rstrip("/") + "/chat/completions"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body[:2000]}") from e


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir")
    ap.add_argument("chapter_id")
    ap.add_argument("--input-pack", default=None, help="input pack path; default .novel-studio/logs/<chapter>-input-pack.md")
    ap.add_argument("--base-url", default=os.environ.get(DEFAULT_BASE_URL_ENV, ""))
    ap.add_argument("--model", default=os.environ.get(DEFAULT_MODEL_ENV, ""))
    ap.add_argument("--api-key-env", default=DEFAULT_API_KEY_ENV)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-tokens", type=int, default=6000)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--max-chars-per-file", type=int, default=30000)
    ap.add_argument("--max-total-chars", type=int, default=120000)
    ap.add_argument("--prompt-profile", default="draft", choices=["draft", "rewrite", "humanize", "review"])
    ap.add_argument("--instruction", default="")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="write request preview only; default")
    mode.add_argument("--execute", action="store_true", help="perform real API call")
    args = ap.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    chapter_id = args.chapter_id
    input_pack = Path(args.input_pack).expanduser().resolve() if args.input_pack else root / ".novel-studio" / "logs" / f"{chapter_id}-input-pack.md"
    if not input_pack.exists():
        print(f"input pack not found: {input_pack}", file=sys.stderr)
        print(f"hint: run scripts/workflow_runner.py {root} {chapter_id} chapter-full first", file=sys.stderr)
        return 1

    base_url = args.base_url
    model = args.model
    api_key_env = args.api_key_env
    cfg_source = project_config_path(root)
    direct_cfg, cfg_source = read_project_direct_api(root)
    has_project_config = direct_cfg is not None
    if has_project_config:
        configured_model = direct_cfg.get("model") or direct_cfg.get("modelFull")
        if configured_model and not model:
            system_model = load_system_model(configured_model)
            if not system_model:
                print(f"configured model not found in OpenClaw system models: {configured_model}", file=sys.stderr)
                print("hint: run scripts/ns_model_config.py list, then scripts/ns_model_config.py init <project-dir>", file=sys.stderr)
                return 2
            model = system_model["model"]
            base_url = base_url or system_model.get("baseUrl", "")
            if args.max_tokens == 6000 and system_model.get("maxTokens") is not None:
                args.max_tokens = min(int(system_model.get("maxTokens") or 6000), args.max_tokens)
            if args.api_key_env == DEFAULT_API_KEY_ENV:
                api_key_env = direct_cfg.get("apiKeyEnv") or env_name_for(system_model["provider"])
        base_url = base_url or direct_cfg.get("baseUrl", "")
        model = model or direct_cfg.get("model", "")
        api_key_env = args.api_key_env if args.api_key_env != DEFAULT_API_KEY_ENV else direct_cfg.get("apiKeyEnv", api_key_env)
        if args.temperature == 0.7 and direct_cfg.get("temperature") is not None:
            args.temperature = float(direct_cfg.get("temperature"))
        if args.max_tokens == 6000 and direct_cfg.get("maxTokens") is not None:
            args.max_tokens = int(direct_cfg.get("maxTokens"))
    if not model or not base_url:
        print("direct API model is not configured for this project.", file=sys.stderr)
        print(f"hint: run scripts/ns_model_config.py init {root}", file=sys.stderr)
        print("or pass both --model and --base-url explicitly.", file=sys.stderr)
        if has_project_config:
            print(f"config exists but is incomplete: {cfg_source}", file=sys.stderr)
        return 2

    api_key = os.environ.get(api_key_env, "")
    execute = bool(args.execute)

    paths = extract_pack_paths(root, input_pack)
    included = load_included_files(root, paths, args.max_chars_per_file, args.max_total_chars)
    state_path = root / ".novel-studio" / "state.json"
    project_name = root.name
    if state_path.exists():
        try:
            project_name = json.loads(read_text(state_path)).get("project") or project_name
        except Exception:
            pass

    messages = build_messages(chapter_id, project_name, included, args.prompt_profile, args.instruction)
    payload = {
        "model": model,
        "messages": messages,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }

    out_dir = root / ".novel-studio" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = utc_stamp()
    base = out_dir / f"{chapter_id}-direct-api-{stamp}"
    preview_path = base.with_suffix(".request.json")
    manifest_path = base.with_suffix(".manifest.json")
    output_path = base.with_suffix(".md")

    preview_payload = dict(payload)
    preview_path.write_text(json.dumps(preview_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "projectRoot": str(root),
        "project": project_name,
        "chapterId": chapter_id,
        "inputPack": str(input_pack.relative_to(root)),
        "includedFiles": [{"path": item.rel, "chars": item.chars} for item in included],
        "promptProfile": args.prompt_profile,
        "model": payload["model"],
        "baseUrl": base_url.rstrip("/") if base_url else "BASE_URL_NOT_SET",
        "apiKeyEnv": api_key_env,
        "execute": execute,
        "temperature": args.temperature,
        "maxTokens": args.max_tokens,
        "requestPreview": str(preview_path.relative_to(root)),
        "output": str(output_path.relative_to(root)),
        "createdAtUtc": datetime.now(timezone.utc).isoformat(),
    }

    if not execute:
        output_path.write_text("# Direct API dry-run\n\nNo API request was sent. Review the request preview and manifest first.\n", encoding="utf-8")
        manifest["status"] = "dry-run"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"dry-run request written: {preview_path}")
        print(f"manifest written: {manifest_path}")
        print(f"included files: {len(included)}")
        return 0

    if not base_url:
        print(f"missing base url; set --base-url or {DEFAULT_BASE_URL_ENV}", file=sys.stderr)
        return 2
    if not model:
        print(f"missing model; set --model or {DEFAULT_MODEL_ENV}", file=sys.stderr)
        return 2
    if not api_key:
        print(f"missing api key env: {api_key_env}", file=sys.stderr)
        return 2

    started = time.time()
    try:
        response = chat_completions(base_url, api_key, payload, args.timeout)
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content:
            content = json.dumps(response, ensure_ascii=False, indent=2)
        output_path.write_text(content, encoding="utf-8")
        manifest["status"] = "ok"
        manifest["elapsedSeconds"] = round(time.time() - started, 3)
        usage = response.get("usage")
        if usage:
            manifest["usage"] = usage
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"output written: {output_path}")
        print(f"manifest written: {manifest_path}")
        return 0
    except Exception as e:
        manifest["status"] = "error"
        manifest["error"] = str(e)
        manifest["elapsedSeconds"] = round(time.time() - started, 3)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"direct API request failed: {e}", file=sys.stderr)
        print(f"manifest written: {manifest_path}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

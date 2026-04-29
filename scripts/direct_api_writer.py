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
SUPPORTED_API = {"openai-completions", "anthropic-messages"}
API_CALL_LOG_FILE = "api-calls.json"
MAX_LOG_ENTRIES = 100
FULL_DETAIL_KEEP = 10


def skill_root() -> Path:
    """Return the Novel Studio skill root directory."""
    return Path(__file__).resolve().parent.parent


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


def inherited_model_config(provider_id: str, provider: dict, model: dict) -> dict:
    """Return effective model config: provider-level non-secret fields inherited by model."""
    inherited = {
        k: v
        for k, v in provider.items()
        if k not in {"apiKey", "models"}
    }
    inherited["provider"] = provider_id
    inherited.update(model)
    inherited["api"] = model.get("api") or provider.get("api") or inherited.get("api", "")
    inherited["baseUrl"] = (
        model.get("baseUrl")
        or model.get("baseURL")
        or model.get("base_url")
        or provider.get("baseUrl")
        or provider.get("baseURL")
        or provider.get("base_url")
        or inherited.get("baseUrl", "")
    )
    return inherited


def load_system_model(model_ref: str) -> dict | None:
    config_paths = [
        Path("/root/.openclaw/openclaw.json"),
        Path("/root/.openclaw/agents/main/agent/models.json"),
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
                effective_config = inherited_model_config(provider_id, provider, m)
                return {
                    "provider": provider_id,
                    "model": m["id"],
                    "modelFull": full,
                    "baseUrl": effective_config.get("baseUrl", ""),
                    "api": effective_config.get("api", ""),
                    "modelConfig": effective_config,
                    "providerConfig": {k: v for k, v in provider.items() if k not in {"apiKey", "models"}},
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


def redact_secrets(value):
    if isinstance(value, dict):
        return {k: ("***" if k.lower() == "apikey" and v else redact_secrets(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_secrets(v) for v in value]
    return value


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




def anthropic_messages_payload(model: str, messages: list[dict], temperature: float, max_tokens: int) -> dict:
    system = ""
    user_messages = []
    for msg in messages:
        if msg.get("role") == "system":
            system = (system + "\n\n" + msg.get("content", "")).strip()
        else:
            user_messages.append(msg)
    return {
        "model": model,
        "system": system,
        "messages": user_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def anthropic_messages(base_url: str, api_key: str, payload: dict, timeout: int) -> dict:
    url = base_url.rstrip("/") + "/messages"
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
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


def extract_response_text(api: str, response: dict) -> str:
    if api == "openai-completions":
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")
    if api == "anthropic-messages":
        parts = []
        for item in response.get("content", []) or []:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "".join(parts)
    return ""

def build_log_record(
    *,
    project_root: str,
    chapter_id: str,
    model: str,
    api: str,
    base_url: str,
    temperature: float,
    max_tokens: int,
    prompt_profile: str,
    included: list[IncludedFile],
    execute: bool,
    status: str,
    elapsed_seconds: float | None = None,
    output_chars: int | None = None,
    usage: dict | None = None,
    error: str | None = None,
    request_preview: str = "",
    manifest_path: str = "",
    output_path: str = "",
) -> dict:
    """Build a single API call log record (full detail)."""
    input_chars = sum(item.chars for item in included)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "project": project_root,
        "chapterId": chapter_id,
        "model": model,
        "api": api,
        "baseUrl": base_url.rstrip("/") if base_url else "",
        "status": status,
        "temperature": temperature,
        "maxTokens": max_tokens,
        "promptProfile": prompt_profile,
        "inputFiles": [{"path": item.rel, "chars": item.chars} for item in included],
        "inputChars": input_chars,
    }
    if elapsed_seconds is not None:
        record["elapsedSeconds"] = elapsed_seconds
    if output_chars is not None:
        record["outputChars"] = output_chars
    if usage:
        record["usage"] = usage
    if error:
        record["error"] = str(error)[:2000]
    if request_preview:
        record["requestPreview"] = request_preview
    if manifest_path:
        record["manifestPath"] = manifest_path
    if output_path:
        record["outputPath"] = output_path
    return record


def trim_log_record(record: dict) -> dict:
    """Trim a full record down to metadata-only (drop requestPreview/manifestPath/outputPath/inputFiles/error/details)."""
    keep_keys = {
        "timestamp", "chapterId", "model", "api", "baseUrl",
        "status", "temperature", "maxTokens", "promptProfile",
        "inputChars", "outputChars", "elapsedSeconds", "usage",
    }
    return {k: v for k, v in record.items() if k in keep_keys}


def discover_alternative_models(current_model_full: str) -> list[dict]:
    """Scan system OpenClaw config and return direct-API-compatible models,
    excluding the one that just failed."""
    config_paths = [
        Path("/root/.openclaw/openclaw.json"),
        Path("/root/.openclaw/agents/main/agent/models.json"),
    ]
    rows = []
    seen = set()
    for cfg_path in config_paths:
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        providers = providers_from_config(data)
        for provider_id, provider in providers.items():
            if not isinstance(provider, dict):
                continue
            provider_base = provider.get("baseUrl") or provider.get("baseURL") or provider.get("base_url") or ""
            provider_api = provider.get("api") or ""
            provider_key = provider.get("apiKey") or ""
            for m in provider.get("models") or []:
                if not isinstance(m, dict) or not m.get("id"):
                    continue
                # Skip image-generation models
                if "image" in m["id"].lower() or "image" in (m.get("name") or "").lower():
                    continue
                full = f"{provider_id}/{m['id']}"
                if full in seen:
                    continue
                seen.add(full)
                # Skip the model that just failed
                if full == current_model_full or m["id"] == current_model_full:
                    continue
                cfg = inherited_model_config(provider_id, provider, m)
                api = cfg.get("api", "")
                if api not in SUPPORTED_API:
                    continue
                base_url = cfg.get("baseUrl", "") or provider_base
                rows.append({
                    "full": full,
                    "provider": provider_id,
                    "model": m["id"],
                    "name": m.get("name") or m["id"],
                    "api": api,
                    "baseUrl": base_url,
                    "apiKey": provider_key or "",
                    "apiKeyEnv": env_name_for(provider_id),
                    "maxTokens": cfg.get("maxTokens"),
                    "providerConfig": {k: v for k, v in provider.items() if k not in {"apiKey", "models"}},
                    "modelConfig": cfg,
                })
    return rows


def present_error_recovery(
    root: Path,
    error: Exception,
    current_model: str,
    current_api: str,
    current_base_url: str,
    no_recover: bool = False,
) -> dict | None:
    """Show error info and offer model switching.

    Returns a new model dict to retry with, or None to abort.
    If no_recover is True, prints suggestion text and returns None."""
    full_current = current_model
    # Try to build full provider/model ref if short
    if "/" not in full_current and "'system_model'" not in current_model:
        direct_cfg, _ = read_project_direct_api(root)
        if direct_cfg and direct_cfg.get("systemModel"):
            full_current = direct_cfg["systemModel"]

    print("\n" + "═" * 60, file=sys.stderr)
    print("❌ Direct API 调用失败", file=sys.stderr)
    print("═" * 60, file=sys.stderr)
    print(f"  失败模型:  {current_model}", file=sys.stderr)
    print(f"  API 协议:  {current_api}", file=sys.stderr)
    print(f"  Base URL:  {current_base_url}", file=sys.stderr)
    print(f"  错误信息:  {str(error)[:300]}", file=sys.stderr)

    # Try to diagnose
    err_str = str(error).lower()
    suggestions: list[str] = []
    if "401" in err_str or "403" in err_str or "unauthorized" in err_str or "invalid api key" in err_str:
        suggestions.append("💡 API Key 可能无效或过期，请检查环境变量或项目 config.json")
    if "404" in err_str or "not found" in err_str:
        suggestions.append("💡 模型名称或 Base URL 可能不正确")
    if "429" in err_str or "rate" in err_str or "quota" in err_str:
        suggestions.append("💡 触发限流，建议等待后重试或切换模型 / provider")
    if "schema" in err_str or "tool" in err_str or "payload" in err_str:
        suggestions.append("💡 请求格式被 provider 拒绝，可能是 API 协议不匹配")
        suggestions.append("   → 尝试切换到 openai-completions 协议的模型（如 lsj/gpt-5.4）")
    if "timeout" in err_str or "timed out" in err_str:
        suggestions.append("💡 请求超时，可尝试更轻量的模型或减少输入量")
    if not suggestions:
        suggestions.append("💡 可能是临时网络问题，或模型暂时不可用")

    for s in suggestions:
        print(f"  {s}", file=sys.stderr)
    print(file=sys.stderr)

    # Discover alternatives
    alternatives = discover_alternative_models(full_current)

    if no_recover:
        if alternatives:
            print("📋 可切换的模型（去掉 --no-recover 启用交互式恢复）:", file=sys.stderr)
            for i, alt in enumerate(alternatives[:8], 1):
                icon = "🔵" if alt["api"] == "openai-completions" else "🟢"
                print(f"  [{i}] {icon} {alt['full']} ({alt['api']}) — {alt['baseUrl']}", file=sys.stderr)
            print(f"\n  下次调用时加 --model {alternatives[0]['full']} 即可切换", file=sys.stderr)
        return None

    if not alternatives:
        print("⚠️  未找到其他可用模型", file=sys.stderr)
        return None

    print("📋 可选替代模型:", file=sys.stderr)
    for i, alt in enumerate(alternatives[:8], 1):
        icon = "🔵" if alt["api"] == "openai-completions" else "🟢"
        print(f"  [{i}] {icon} {alt['full']:35s} {alt['api']:22s} {alt['baseUrl']}", file=sys.stderr)
    print(f"  [s] 💾 保存当前配置（跳过本次）", file=sys.stderr)
    print(f"  [0] ❌ 放弃", file=sys.stderr)
    print(file=sys.stderr)

    while True:
        try:
            choice = input("👉 选择一个模型编号重试: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(file=sys.stderr)
            return None
        if choice == "0":
            return None
        if choice.lower() == "s":
            return {"__save_config__": True}
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(alternatives):
                return alternatives[idx]
        print(f"  无效选择: {choice}", file=sys.stderr)


def write_direct_api_config(root: Path, model_info: dict) -> Path:
    """Write or update the project's directApi config with a new model selection."""
    ns = root / ".novel-studio"
    ns.mkdir(parents=True, exist_ok=True)
    config_path = project_config_path(root)
    config = {}
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            config = {}
    prev = config.get("directApi") or {}
    config["directApi"] = {
        "systemModel": model_info["full"],
        "model": model_info["model"],
        "api": model_info["api"],
        "baseUrl": model_info["baseUrl"],
        "apiKey": model_info.get("apiKey") or prev.get("apiKey") or "",
        "apiKeyEnv": model_info.get("apiKeyEnv") or prev.get("apiKeyEnv") or env_name_for(model_info["provider"]),
        "temperature": prev.get("temperature", 0.7),
        "maxTokens": prev.get("maxTokens") or model_info.get("maxTokens") or 6000,
        "modelConfig": model_info.get("modelConfig"),
        "providerConfig": model_info.get("providerConfig"),
        "source": model_info.get("source", ""),
    }
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return config_path


def update_api_call_log(record: dict) -> None:
    """Append a record to the API call log, keeping last MAX_LOG_ENTRIES.
    The most recent FULL_DETAIL_KEEP records keep full detail; older ones are trimmed.
    Log file lives under the Novel Studio skill directory, not the novel project."""
    log_dir = skill_root() / ".novel-studio" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / API_CALL_LOG_FILE

    entries: list[dict] = []
    if log_path.exists():
        try:
            entries = json.loads(log_path.read_text(encoding="utf-8"))
            if not isinstance(entries, list):
                entries = []
        except Exception:
            entries = []

    # Append new record (always full detail)
    entries.append(record)

    # Enforce max entries: drop oldest
    while len(entries) > MAX_LOG_ENTRIES:
        entries.pop(0)

    # Trim detail: keep last FULL_DETAIL_KEEP as full, trim the rest
    trim_cutoff = max(0, len(entries) - FULL_DETAIL_KEEP)
    for i in range(trim_cutoff):
        entries[i] = trim_log_record(entries[i])

    log_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    ap.add_argument("--no-recover", action="store_true", help="skip interactive model switching on error")
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
    direct_cfg, cfg_source = read_project_direct_api(root)
    has_project_config = direct_cfg is not None
    system_model = None
    if has_project_config:
        if not direct_cfg.get("systemModel"):
            print(f"direct API config is missing systemModel: {cfg_source}", file=sys.stderr)
            print(f"hint: run scripts/ns_model_config.py init {root}", file=sys.stderr)
            return 2
        if direct_cfg.get("api") not in SUPPORTED_API:
            print(f"configured model is not direct-API compatible: {direct_cfg.get('systemModel')} (api={direct_cfg.get('api')})", file=sys.stderr)
            print(f"hint: run scripts/ns_model_config.py init {root}", file=sys.stderr)
            return 2
        system_model = {
            "provider": (direct_cfg.get("modelConfig") or {}).get("provider", ""),
            "model": direct_cfg.get("model", ""),
            "modelFull": direct_cfg.get("systemModel", ""),
            "baseUrl": direct_cfg.get("baseUrl", ""),
            "api": direct_cfg.get("api", ""),
            "modelConfig": direct_cfg.get("modelConfig"),
            "providerConfig": direct_cfg.get("providerConfig"),
            "source": direct_cfg.get("source"),
        }
        model = model or direct_cfg.get("model", "")
        base_url = base_url or direct_cfg.get("baseUrl", "")
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

    api_key = (direct_cfg or {}).get("apiKey") or os.environ.get(api_key_env, "")
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
    resolved_model_config = system_model.get("modelConfig") if 'system_model' in locals() and system_model else None
    resolved_provider_config = system_model.get("providerConfig") if 'system_model' in locals() and system_model else None
    api = (resolved_model_config or {}).get("api") or (system_model.get("api") if 'system_model' in locals() and system_model else "openai-completions")
    if api == "openai-completions":
        payload = {
            "model": model,
            "messages": messages,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
        }
    elif api == "anthropic-messages":
        payload = anthropic_messages_payload(model, messages, args.temperature, args.max_tokens)
    else:
        print(f"unsupported direct API protocol: {api}", file=sys.stderr)
        return 2

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
        "api": api,
        "configuredSystemModel": direct_cfg.get("systemModel") if isinstance(direct_cfg, dict) else None,
        "configuredModel": direct_cfg.get("model") if isinstance(direct_cfg, dict) else None,
        "resolvedModelConfig": redact_secrets(resolved_model_config),
        "resolvedProviderConfig": redact_secrets(resolved_provider_config),
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
        log_record = build_log_record(
            project_root=str(root),
            chapter_id=chapter_id, model=model, api=api, base_url=base_url,
            temperature=args.temperature, max_tokens=args.max_tokens,
            prompt_profile=args.prompt_profile, included=included,
            execute=False, status="dry-run",
            request_preview=str(preview_path.relative_to(root)),
            manifest_path=str(manifest_path.relative_to(root)),
        )
        update_api_call_log(log_record)
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

    # Retry loop with model recovery on error
    current_model = model
    current_api = api
    current_base_url = base_url
    current_api_key = api_key
    system_model_info = system_model
    attempt = 0

    while True:
        attempt += 1
        if attempt > 1:
            print(f"\n🔄 第 {attempt} 次尝试 — 模型: {current_model}", file=sys.stderr)

        # Build payload for current model
        if current_api == "openai-completions":
            payload = {
                "model": current_model,
                "messages": messages,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
            }
        elif current_api == "anthropic-messages":
            payload = anthropic_messages_payload(current_model, messages, args.temperature, args.max_tokens)
        else:
            print(f"unsupported direct API protocol: {current_api}", file=sys.stderr)
            return 2

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
            "model": current_model,
            "api": current_api,
            "configuredSystemModel": direct_cfg.get("systemModel") if isinstance(direct_cfg, dict) else None,
            "configuredModel": direct_cfg.get("model") if isinstance(direct_cfg, dict) else None,
            "resolvedModelConfig": redact_secrets(system_model_info.get("modelConfig") if system_model_info else None),
            "resolvedProviderConfig": redact_secrets(system_model_info.get("providerConfig") if system_model_info else None),
            "baseUrl": current_base_url.rstrip("/") if current_base_url else "BASE_URL_NOT_SET",
            "apiKeyEnv": api_key_env,
            "execute": True,
            "temperature": args.temperature,
            "maxTokens": args.max_tokens,
            "requestPreview": str(preview_path.relative_to(root)),
            "output": str(output_path.relative_to(root)),
            "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        }

        started = time.time()
        try:
            if current_api == "openai-completions":
                response = chat_completions(current_base_url, current_api_key, payload, args.timeout)
            elif current_api == "anthropic-messages":
                response = anthropic_messages(current_base_url, current_api_key, payload, args.timeout)
            else:
                raise RuntimeError(f"unsupported direct API protocol: {current_api}")
            content = extract_response_text(current_api, response)
            if not content:
                content = json.dumps(response, ensure_ascii=False, indent=2)
            output_path.write_text(content, encoding="utf-8")
            elapsed = round(time.time() - started, 3)
            manifest["status"] = "ok"
            manifest["elapsedSeconds"] = elapsed
            usage = response.get("usage")
            if usage:
                manifest["usage"] = usage
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"output written: {output_path}")
            print(f"manifest written: {manifest_path}")
            log_record = build_log_record(
                project_root=str(root),
                chapter_id=chapter_id, model=current_model, api=current_api, base_url=current_base_url,
                temperature=args.temperature, max_tokens=args.max_tokens,
                prompt_profile=args.prompt_profile, included=included,
                execute=True, status="ok",
                elapsed_seconds=elapsed,
                output_chars=len(content),
                usage=usage,
                request_preview=str(preview_path.relative_to(root)),
                manifest_path=str(manifest_path.relative_to(root)),
                output_path=str(output_path.relative_to(root)),
            )
            update_api_call_log(log_record)
            return 0

        except Exception as e:
            elapsed = round(time.time() - started, 3)
            manifest["status"] = "error"
            manifest["error"] = str(e)
            manifest["elapsedSeconds"] = elapsed
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            log_record = build_log_record(
                project_root=str(root),
                chapter_id=chapter_id, model=current_model, api=current_api, base_url=current_base_url,
                temperature=args.temperature, max_tokens=args.max_tokens,
                prompt_profile=args.prompt_profile, included=included,
                execute=True, status="error",
                elapsed_seconds=elapsed,
                error=str(e),
                request_preview=str(preview_path.relative_to(root)),
                manifest_path=str(manifest_path.relative_to(root)),
            )
            update_api_call_log(log_record)

            # Recovery
            recovery = present_error_recovery(
                root, e, current_model, current_api, current_base_url,
                no_recover=args.no_recover,
            )

            if recovery is None:
                print("❌ 已放弃", file=sys.stderr)
                return 3

            if recovery.get("__save_config__"):
                print(f"💾 已保存当前配置到 {project_config_path(root)}", file=sys.stderr)
                return 3

            # Switch model and retry
            current_model = recovery["model"]
            current_api = recovery["api"]
            current_base_url = recovery["baseUrl"]
            current_api_key = recovery.get("apiKey") or os.environ.get(recovery.get("apiKeyEnv", ""), "")
            system_model_info = recovery
            if not current_api_key:
                print(f"⚠️  新模型缺少 API Key，请设置环境变量 {recovery.get('apiKeyEnv', '')}", file=sys.stderr)
                return 3
            print(f"🔄 切换至 {recovery['full']} 重试中...", file=sys.stderr)
            continue


if __name__ == "__main__":
    raise SystemExit(main())

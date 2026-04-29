#!/usr/bin/env python3
"""
ns_model_config.py

Discover OpenClaw system model config and initialize/select Novel Studio direct
API model settings for a project.

This script stores a verified direct API model snapshot (including apiKey) in
project config plus the system model name used for future sync. Display output redacts secrets.

Usage:
  python3 scripts/ns_model_config.py list [--json]
  python3 scripts/ns_model_config.py init <project-dir> [--select <provider/model|alias|number>] [--non-interactive]
  python3 scripts/ns_model_config.py sync <project-dir>
  python3 scripts/ns_model_config.py show <project-dir>
"""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import sys

DEFAULT_CONFIG_PATHS = [
    Path("/root/.openclaw/openclaw.json"),
    Path("/root/.openclaw/agents/main/agent/models.json"),
]
SUPPORTED_API = {"openai-completions", "anthropic-messages"}
KEY_ENV_PREFIX = "NOVEL_STUDIO_API_KEY_"
GLOBAL_CONFIG_DIR = Path(__file__).resolve().parent.parent / ".novel-studio"
GLOBAL_CONFIG_PATH = GLOBAL_CONFIG_DIR / "global-config.json"


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


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
        if k not in {"models"}
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


def aliases_from_config(data: dict) -> dict:
    out = {}
    agents = data.get("agents") if isinstance(data.get("agents"), dict) else {}
    defaults = agents.get("defaults") if isinstance(agents.get("defaults"), dict) else {}
    models = defaults.get("models") if isinstance(defaults.get("models"), dict) else {}
    for full, meta in models.items():
        if isinstance(meta, dict) and meta.get("alias"):
            out[meta["alias"]] = full
    return out


def discover() -> list[dict]:
    aliases = {}
    configs = [(cfg, load_json(cfg)) for cfg in DEFAULT_CONFIG_PATHS]
    for _, data in configs:
        aliases.update(aliases_from_config(data))
    rows = []
    seen = set()
    for cfg, data in configs:
        providers = providers_from_config(data)
        for provider_id, provider in providers.items():
            if not isinstance(provider, dict):
                continue
            base_url = provider.get("baseUrl") or provider.get("baseURL") or provider.get("base_url") or ""
            provider_api = provider.get("api") or ""
            models = provider.get("models") or []
            for m in models:
                if not isinstance(m, dict):
                    continue
                model_id = m.get("id")
                if not model_id:
                    continue
                effective_config = inherited_model_config(provider_id, provider, m)
                api = effective_config.get("api", "")
                full = f"{provider_id}/{model_id}"
                key = full
                if key in seen:
                    continue
                seen.add(key)
                supported = api in SUPPORTED_API and "image" not in str(model_id).lower()
                rows.append({
                    "full": full,
                    "provider": provider_id,
                    "model": model_id,
                    "name": m.get("name") or model_id,
                    "alias": next((a for a, target in aliases.items() if target == full), ""),
                    "baseUrl": effective_config.get("baseUrl", ""),
                    "api": effective_config.get("api", ""),
                    "supportedDirectApi": supported,
                    "contextWindow": effective_config.get("contextWindow"),
                    "maxTokens": effective_config.get("maxTokens"),
                    "modelConfig": effective_config,
                    "providerConfig": {k: v for k, v in provider.items() if k not in {"models"}},
                    "source": str(cfg),
                })
    # Prefer supported OpenAI-compatible models first, then stable display order.
    rows.sort(key=lambda r: (not r["supportedDirectApi"], r["provider"], r["model"], r["source"]))
    return rows


def print_table(rows: list[dict]) -> None:
    for i, r in enumerate(rows, start=1):
        support = "direct" if r["supportedDirectApi"] else f"api={r['api'] or 'unknown'}"
        alias = f" alias={r['alias']}" if r.get("alias") else ""
        print(f"{i}. {r['full']} ({r['name']}){alias} — {support} — {r['baseUrl'] or 'no baseUrl'}")


def resolve_selection(rows: list[dict], select: str | None) -> dict | None:
    supported = [r for r in rows if r["supportedDirectApi"]]
    if not rows:
        return None
    if not select:
        return supported[0] if supported else rows[0]
    s = select.strip()
    s_lower = s.lower()
    if s.isdigit():
        idx = int(s) - 1
        if 0 <= idx < len(rows):
            return rows[idx]
        return None
    for r in rows:
        candidates = {r["full"], r["model"], r.get("alias", "")}
        if s in candidates or s_lower in {c.lower() for c in candidates if c}:
            return r
    return None


def interactive_select(rows: list[dict]) -> dict | None:
    print_table(rows)
    print("\nChoose a model number/full id/alias. Empty = first direct-compatible model.")
    try:
        choice = input("> ").strip()
    except EOFError:
        choice = ""
    return resolve_selection(rows, choice or None)


def env_name_for(provider: str) -> str:
    safe = "".join(ch if ch.isalnum() else "_" for ch in provider.upper())
    return KEY_ENV_PREFIX + safe


# project_config_path removed — model config is now global only.


# ensure_config_gitignore removed — model config is now global only.


def ensure_supported(row: dict) -> tuple[bool, str]:
    if not row:
        return False, "model not found"
    if not row.get("supportedDirectApi"):
        return False, f"model api is not supported: {row.get('api')}"
    if not row.get("baseUrl"):
        return False, "model has no baseUrl"
    return True, ""


def build_direct_api_config(row: dict, key_env: str | None, previous: dict | None = None) -> dict:
    previous = previous or {}
    provider_cfg = row.get("providerConfig") or {}
    api_key = provider_cfg.get("apiKey") or previous.get("apiKey") or ""
    data = {
        "systemModel": row["full"],
        "model": row["model"],
        "api": row.get("api", ""),
        "baseUrl": row.get("baseUrl", ""),
        "apiKey": api_key,
        "apiKeyEnv": key_env or previous.get("apiKeyEnv") or env_name_for(row["provider"]),
        "temperature": previous.get("temperature", 0.7),
        "maxTokens": previous.get("maxTokens") or row.get("maxTokens"),
        "modelConfig": row.get("modelConfig"),
        "providerConfig": provider_cfg,
        "source": row.get("source"),
    }
    return data


# write_project_config removed — model config is now global only.


def redact_secrets(value):
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k.lower() == "apikey":
                out[k] = "***" if v else ""
            else:
                out[k] = redact_secrets(v)
        return out
    if isinstance(value, list):
        return [redact_secrets(v) for v in value]
    return value


# read_project_config removed — model config is now global only.


# validate_project removed — model config is now global only. Use global show instead.


# sync_project removed — model config is now global only.


# show_project removed — model config is now global only. Use global show instead.


def read_global_config() -> tuple[dict | None, Path]:
    """Read the Novel Studio global config (directApi + workMode)."""
    if GLOBAL_CONFIG_PATH.exists():
        try:
            config = json.loads(GLOBAL_CONFIG_PATH.read_text(encoding="utf-8"))
            return config, GLOBAL_CONFIG_PATH
        except Exception:
            pass
    return None, GLOBAL_CONFIG_PATH


def read_global_direct_api() -> tuple[dict | None, Path]:
    """Read the Novel Studio global direct API config only."""
    config, path = read_global_config()
    if config and isinstance(config.get("directApi"), dict):
        return config["directApi"], path
    return None, path


def read_global_work_mode() -> str:
    """Read the current work mode: 'system' or 'direct'. Default 'direct'."""
    config, _ = read_global_config()
    if config and config.get("workMode") in ("system", "direct"):
        return config["workMode"]
    return "direct"


def write_global_config(config: dict) -> None:
    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    GLOBAL_CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_model_connectivity(row: dict, timeout: int = 15) -> tuple[bool, str]:
    """Attempt a minimal API call to verify the selected model is reachable.
    Returns (ok, message)."""
    from urllib import request, error
    api = row.get("api", "")
    base_url = row.get("baseUrl", "")
    model_id = row.get("model", "")
    provider_cfg = row.get("providerConfig") or {}
    api_key = provider_cfg.get("apiKey") or ""

    if not api_key:
        return False, "无法获取 API Key（providerConfig 中缺少 apiKey）"
    if not base_url:
        return False, "缺少 baseUrl"

    try:
        if api == "openai-completions":
            url = base_url.rstrip("/") + "/chat/completions"
            payload = json.dumps({
                "model": model_id,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 1,
            }, ensure_ascii=False).encode("utf-8")
            req = request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }, method="POST")
        elif api == "anthropic-messages":
            url = base_url.rstrip("/") + "/messages"
            payload = json.dumps({
                "model": model_id,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 1,
            }, ensure_ascii=False).encode("utf-8")
            req = request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            }, method="POST")
        else:
            return False, f"不支持的 API 协议: {api}"

        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return True, f"连接成功 (HTTP {resp.status})"
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        return False, f"HTTP {e.code}: {body}"
    except Exception as e:
        return False, f"连接失败: {str(e)[:200]}"


def set_global(select: str | None, non_interactive: bool, api_key_env: str | None, skip_validate: bool = False) -> int:
    rows = discover()
    if select or non_interactive:
        row = resolve_selection(rows, select)
    else:
        row = interactive_select(rows)
    if not row:
        print("no model selected", file=sys.stderr)
        return 1
    ok, reason = ensure_supported(row)
    if not ok:
        print(f"selected model is not usable for direct API: {row.get('full') if row else ''}; {reason}", file=sys.stderr)
        return 2
    GLOBAL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    existing = {}
    if GLOBAL_CONFIG_PATH.exists():
        try:
            existing = json.loads(GLOBAL_CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

    # --- Validation step ---
    if not skip_validate:
        print(f"🔍 正在验证模型连通性: {row['full']} ...", file=sys.stderr)
        print(f"   baseUrl: {row.get('baseUrl', 'N/A')}", file=sys.stderr)
        valid, vmsg = validate_model_connectivity(row)
        if not valid:
            print(f"❌ 验证失败: {vmsg}", file=sys.stderr)
            print(f"   配置导入已放弃，未保存任何更改。", file=sys.stderr)
            print(f"   提示: 可换一个模型重试，或用 --skip-validate 跳过验证。", file=sys.stderr)
            return 2
        print(f"✅ 验证通过: {vmsg}", file=sys.stderr)
    else:
        print(f"⚠️  已跳过连通性验证 (--skip-validate)", file=sys.stderr)

    existing["directApi"] = build_direct_api_config(row, api_key_env, previous=existing.get("directApi"))
    write_global_config(existing)
    print(f"wrote global direct API config: {GLOBAL_CONFIG_PATH}")
    print(f"selected: {row['full']}")
    print(f"api key env: {api_key_env or env_name_for(row['provider'])}")
    return 0


def show_global() -> int:
    cfg, path = read_global_direct_api()
    full_cfg, _ = read_global_config()
    if not cfg:
        print(f"global direct API config not found: {GLOBAL_CONFIG_PATH}")
        return 1
    result = {"configPath": str(path), "directApi": redact_secrets(cfg)}
    if full_cfg:
        result["workMode"] = full_cfg.get("workMode", "direct")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def remove_global() -> int:
    if GLOBAL_CONFIG_PATH.exists():
        GLOBAL_CONFIG_PATH.unlink()
        print(f"removed: {GLOBAL_CONFIG_PATH}")
    else:
        print(f"no global config to remove: {GLOBAL_CONFIG_PATH}")
    return 0


def workmode_show() -> int:
    mode = read_global_work_mode()
    label = "🔵 直连模式 (direct)" if mode == "direct" else "🟢 系统模型 (system)"
    print(f"当前工作模式: {label}")
    print(f"  direct = 创作/写作/修稿走直连 API")
    print(f"  system = 所有任务走 OpenClaw 系统模型")
    return 0


def workmode_set(mode: str) -> int:
    if mode not in ("system", "direct"):
        print(f"invalid work mode: {mode}. Use 'system' or 'direct'.", file=sys.stderr)
        return 1
    config, _ = read_global_config()
    config = config or {}
    config["workMode"] = mode
    write_global_config(config)
    label = "🔵 直连模式 (direct)" if mode == "direct" else "🟢 系统模型 (system)"
    print(f"工作模式已切换为: {label}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_list = sub.add_parser("list")
    p_list.add_argument("--json", action="store_true")
    # --- deprecated project-level commands (kept for compat messages) ---
    p_init = sub.add_parser("init")
    p_init.add_argument("project_dir")
    p_init.add_argument("--select", default=None)
    p_init.add_argument("--non-interactive", action="store_true")
    p_init.add_argument("--api-key-env", default=None)
    p_show = sub.add_parser("show")
    p_show.add_argument("project_dir")
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("project_dir")
    p_sync = sub.add_parser("sync")
    p_sync.add_argument("project_dir")
    # --- global commands ---
    p_global = sub.add_parser("global")
    p_global_sub = p_global.add_subparsers(dest="global_cmd")
    p_global_set = p_global_sub.add_parser("set")
    p_global_set.add_argument("--select", default=None)
    p_global_set.add_argument("--non-interactive", action="store_true")
    p_global_set.add_argument("--api-key-env", default=None)
    p_global_set.add_argument("--skip-validate", action="store_true",
                              help="skip connectivity validation after selection")
    p_global_sub.add_parser("show")
    p_global_sub.add_parser("remove")
    # --- workmode commands ---
    p_workmode = sub.add_parser("workmode")
    p_workmode_sub = p_workmode.add_subparsers(dest="workmode_cmd")
    p_workmode_sub.add_parser("show")
    p_workmode_set = p_workmode_sub.add_parser("set")
    p_workmode_set.add_argument("mode", choices=["system", "direct"],
                                help="'system' = all tasks use OpenClaw system model; 'direct' = creative tasks use direct API")
    args = ap.parse_args()

    if args.cmd == "global":
        if args.global_cmd == "set":
            return set_global(args.select, args.non_interactive, args.api_key_env,
                            skip_validate=args.skip_validate)
        if args.global_cmd == "show":
            return show_global()
        if args.global_cmd == "remove":
            return remove_global()
        print("usage: ns_model_config.py global {set,show,remove}", file=sys.stderr)
        return 1
    if args.cmd == "workmode":
        if args.workmode_cmd == "show":
            return workmode_show()
        if args.workmode_cmd == "set":
            return workmode_set(args.mode)
        print("usage: ns_model_config.py workmode {show,set}", file=sys.stderr)
        return 1
    if args.cmd == "show":
        print("⚠️  'show <project-dir>' is deprecated. Model config is now global.", file=sys.stderr)
        print("   Use: ns_model_config.py global show", file=sys.stderr)
        return 1
    if args.cmd == "validate":
        print("⚠️  'validate <project-dir>' is deprecated. Model config is now global.", file=sys.stderr)
        print("   Use: ns_model_config.py global show  (to inspect current global config)", file=sys.stderr)
        return 1
    if args.cmd == "sync":
        print("⚠️  'sync <project-dir>' is deprecated. Model config is now global.", file=sys.stderr)
        print("   Use: ns_model_config.py global set  (to re-select the global model)", file=sys.stderr)
        return 1

    rows = discover()
    if args.cmd == "list":
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print_table(rows)
        return 0

    if args.cmd == "init":
        print("⚠️  'init <project-dir>' is deprecated. Model config is now global for all projects.", file=sys.stderr)
        print("   Use: ns_model_config.py global set", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

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


def project_config_path(root: Path) -> Path:
    return root / ".novel-studio" / "config.json"


def ensure_config_gitignore(root: Path) -> None:
    ns = root / ".novel-studio"
    ns.mkdir(parents=True, exist_ok=True)
    ignore = ns / ".gitignore"
    lines = []
    if ignore.exists():
        lines = ignore.read_text(encoding="utf-8").splitlines()
    if "config.json" not in lines:
        lines.append("config.json")
        ignore.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


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


def write_project_config(root: Path, row: dict, key_env: str | None, previous: dict | None = None) -> Path:
    ns = root / ".novel-studio"
    ns.mkdir(parents=True, exist_ok=True)
    ensure_config_gitignore(root)
    config_path = project_config_path(root)
    config = {}
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            config = {}
    config["directApi"] = build_direct_api_config(row, key_env, previous)
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return config_path


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


def read_project_config(root: Path) -> tuple[dict | None, Path]:
    config_path = project_config_path(root)
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            cfg = config.get("directApi")
            if isinstance(cfg, dict):
                return cfg, config_path
        except Exception:
            pass
    return None, config_path


def validate_project(root: Path) -> int:
    cfg, path = read_project_config(root)
    if not cfg or not cfg.get("systemModel"):
        print(f"direct API model is not configured in: {project_config_path(root)}", file=sys.stderr)
        print(f"hint: run scripts/ns_model_config.py init {root}", file=sys.stderr)
        return 2
    model_ref = cfg.get("systemModel")
    rows = discover()
    matched = resolve_selection(rows, model_ref)
    ok, reason = ensure_supported(matched)
    if not ok:
        print(f"configured system model is not usable: {model_ref}; {reason}", file=sys.stderr)
        print("hint: run scripts/ns_model_config.py list", file=sys.stderr)
        print(f"then run scripts/ns_model_config.py init {root}", file=sys.stderr)
        return 2
    print(json.dumps({
        "configPath": str(path),
        "status": "ok",
        "configuredSystemModel": model_ref,
        "resolvedModel": matched["full"],
        "api": matched.get("api", ""),
        "baseUrl": matched.get("baseUrl", ""),
        "modelConfig": redact_secrets(matched.get("modelConfig")),
        "providerConfig": redact_secrets(matched.get("providerConfig")),
    }, ensure_ascii=False, indent=2))
    return 0


def sync_project(root: Path) -> int:
    cfg, path = read_project_config(root)
    if not cfg or not cfg.get("systemModel"):
        print(f"direct API model is not configured in: {project_config_path(root)}", file=sys.stderr)
        print(f"hint: run scripts/ns_model_config.py init {root}", file=sys.stderr)
        return 2
    model_ref = cfg.get("systemModel")
    matched = resolve_selection(discover(), model_ref)
    ok, reason = ensure_supported(matched)
    if not ok:
        print(f"sync failed: configured system model is not usable: {model_ref}; {reason}", file=sys.stderr)
        print("config was not changed", file=sys.stderr)
        return 2
    out = write_project_config(root, matched, cfg.get("apiKeyEnv"), previous=cfg)
    print(json.dumps({
        "status": "synced",
        "configPath": str(out),
        "systemModel": model_ref,
        "api": matched.get("api"),
        "baseUrl": matched.get("baseUrl"),
    }, ensure_ascii=False, indent=2))
    return 0


def show_project(root: Path) -> int:
    cfg, path = read_project_config(root)
    if not cfg:
        print(f"direct API config not found in: {project_config_path(root)}")
        return 1
    print(json.dumps({"configPath": str(path), "directApi": redact_secrets(cfg)}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_list = sub.add_parser("list")
    p_list.add_argument("--json", action="store_true")
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
    args = ap.parse_args()

    if args.cmd == "show":
        return show_project(Path(args.project_dir).expanduser().resolve())
    if args.cmd == "validate":
        return validate_project(Path(args.project_dir).expanduser().resolve())
    if args.cmd == "sync":
        return sync_project(Path(args.project_dir).expanduser().resolve())

    rows = discover()
    if args.cmd == "list":
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print_table(rows)
        return 0

    if args.cmd == "init":
        root = Path(args.project_dir).expanduser().resolve()
        if args.select or args.non_interactive:
            row = resolve_selection(rows, args.select)
        else:
            row = interactive_select(rows)
        if not row:
            print("no model selected", file=sys.stderr)
            return 1
        ok, reason = ensure_supported(row)
        if not ok:
            print(f"selected model is not usable for direct API: {row.get('full') if row else ''}; {reason}", file=sys.stderr)
            return 2
        cfg = write_project_config(root, row, args.api_key_env)
        print(f"wrote direct API config: {cfg}")
        print(f"selected: {row['full']}")
        print(f"api key env: {args.api_key_env or env_name_for(row['provider'])}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

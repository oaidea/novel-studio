#!/usr/bin/env python3
"""
ns_model_config.py

Discover OpenClaw system model config and initialize/select Novel Studio direct
API model settings for a project.

This script does not copy API keys, base URLs, or provider details into project
files. It writes only the selected model reference plus optional local overrides.
direct_api_writer.py resolves provider/baseUrl/api from OpenClaw system config at runtime.

Usage:
  python3 scripts/ns_model_config.py list [--json]
  python3 scripts/ns_model_config.py init <project-dir> [--select <provider/model|alias|number>] [--non-interactive]
  python3 scripts/ns_model_config.py show <project-dir>
"""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import sys

DEFAULT_CONFIG_PATHS = [
    Path("/root/.openclaw/agents/main/agent/models.json"),
    Path("/root/.openclaw/openclaw.json"),
]
SUPPORTED_API = {"openai-completions"}
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
                api = m.get("api") or provider_api
                full = f"{provider_id}/{model_id}"
                key = (full, base_url, api)
                if key in seen:
                    continue
                seen.add(key)
                supported = api in SUPPORTED_API and "image" not in str(model_id).lower()
                model_config = dict(m)
                model_config["api"] = api
                rows.append({
                    "full": full,
                    "provider": provider_id,
                    "model": model_id,
                    "name": m.get("name") or model_id,
                    "alias": next((a for a, target in aliases.items() if target == full), ""),
                    "baseUrl": base_url,
                    "api": api,
                    "supportedDirectApi": supported,
                    "contextWindow": m.get("contextWindow"),
                    "maxTokens": m.get("maxTokens"),
                    "modelConfig": model_config,
                    "providerConfig": {k: v for k, v in provider.items() if k not in {"apiKey", "models"}},
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
    if s.isdigit():
        idx = int(s) - 1
        if 0 <= idx < len(rows):
            return rows[idx]
        return None
    for r in rows:
        if s in {r["full"], r["model"], r.get("alias", "")}:
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


def build_direct_api_config(row: dict, key_env: str | None) -> dict:
    data = {
        "model": row["full"],
        "temperature": 0.7,
        "maxTokens": min(int(row.get("maxTokens") or 6000), 6000),
    }
    if key_env:
        data["apiKeyEnv"] = key_env
    return data


def write_project_config(root: Path, row: dict, key_env: str | None) -> Path:
    ns = root / ".novel-studio"
    ns.mkdir(parents=True, exist_ok=True)
    config_path = project_config_path(root)
    config = {}
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            config = {}
    config["directApi"] = build_direct_api_config(row, key_env)
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return config_path


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
    if not cfg or not cfg.get("model"):
        print(f"direct API model is not configured in: {project_config_path(root)}", file=sys.stderr)
        print(f"hint: run scripts/ns_model_config.py init {root}", file=sys.stderr)
        return 2
    model_ref = cfg.get("model")
    rows = discover()
    matched = resolve_selection(rows, model_ref)
    if not matched:
        print(f"configured model no longer exists in OpenClaw system models: {model_ref}", file=sys.stderr)
        print("hint: run scripts/ns_model_config.py list", file=sys.stderr)
        print(f"then run scripts/ns_model_config.py init {root}", file=sys.stderr)
        return 2
    if not matched.get("supportedDirectApi"):
        print(f"configured model exists but is not direct-API compatible: {model_ref} (api={matched.get('api')})", file=sys.stderr)
        print(f"hint: run scripts/ns_model_config.py init {root}", file=sys.stderr)
        return 2
    print(json.dumps({
        "configPath": str(path),
        "status": "ok",
        "configuredModel": model_ref,
        "resolvedModel": matched["full"],
        "baseUrl": matched.get("baseUrl", ""),
        "api": matched.get("api", ""),
        "modelConfig": matched.get("modelConfig"),
        "providerConfig": matched.get("providerConfig"),
    }, ensure_ascii=False, indent=2))
    return 0


def show_project(root: Path) -> int:
    cfg, path = read_project_config(root)
    if not cfg:
        print(f"direct API config not found in: {project_config_path(root)}")
        return 1
    print(json.dumps({"configPath": str(path), "directApi": cfg}, ensure_ascii=False, indent=2))
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
    args = ap.parse_args()

    if args.cmd == "show":
        return show_project(Path(args.project_dir).expanduser().resolve())
    if args.cmd == "validate":
        return validate_project(Path(args.project_dir).expanduser().resolve())

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
        if not row["supportedDirectApi"]:
            print(f"warning: selected model api '{row['api']}' is not directly supported by direct_api_writer.py", file=sys.stderr)
        cfg = write_project_config(root, row, args.api_key_env)
        print(f"wrote direct API config: {cfg}")
        print(f"selected: {row['full']}")
        print(f"api key env: {args.api_key_env or env_name_for(row['provider'])} (resolved at runtime; not required in config)")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

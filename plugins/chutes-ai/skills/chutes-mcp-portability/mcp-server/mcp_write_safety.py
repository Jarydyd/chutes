"""MCP write-tool gating and response redaction (no FastMCP import)."""

from __future__ import annotations

import os
from typing import Any


def writes_enabled(env_flag: str) -> bool:
    return os.environ.get(env_flag) == "1"


def write_tool_blocked(tool_name: str, env_var: str) -> dict:
    return {
        "error": (
            f"{tool_name} is disabled by default (safe MCP default). "
            f"Set {env_var}=1 in the server environment to enable this write/deploy tool."
        ),
        "enabled": False,
        "required_env": env_var,
    }


def preview_secret_value(value: str) -> str:
    """Return a non-recoverable preview; never log raw secrets."""
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def redact_create_api_key_response(data: Any) -> Any:
    """Hide raw secret material unless explicitly allowed."""
    if os.environ.get("CHUTES_ALLOW_SECRET_OUTPUT") == "1":
        return data
    if not isinstance(data, dict):
        return data
    out = dict(data)
    changed = False
    for key in ("secret_key", "secret", "key", "api_key", "token"):
        val = out.get(key)
        if isinstance(val, str) and val:
            out[key] = preview_secret_value(val)
            changed = True
    if changed:
        out["_note"] = (
            "Raw secret values redacted. Set CHUTES_ALLOW_SECRET_OUTPUT=1 to return full values (unsafe for agents)."
        )
        out["_redacted"] = True
    return out

from pathlib import Path

import pytest

MCP_DIR = Path(__file__).resolve().parents[1] / "plugins" / "chutes-ai" / "skills" / "chutes-mcp-portability" / "mcp-server"


@pytest.fixture()
def mcp_write_safety(monkeypatch):
    """Import policy helpers without loading the FastMCP server."""
    import importlib.util

    path = MCP_DIR / "mcp_write_safety.py"
    spec = importlib.util.spec_from_file_location("mcp_write_safety", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_writes_enabled_requires_exact_one(mcp_write_safety, monkeypatch):
    monkeypatch.delenv("CHUTES_ENABLE_DEPLOY_TOOLS", raising=False)
    assert mcp_write_safety.writes_enabled("CHUTES_ENABLE_DEPLOY_TOOLS") is False
    monkeypatch.setenv("CHUTES_ENABLE_DEPLOY_TOOLS", "1")
    assert mcp_write_safety.writes_enabled("CHUTES_ENABLE_DEPLOY_TOOLS") is True


def test_write_tool_blocked_message_includes_env(mcp_write_safety):
    d = mcp_write_safety.write_tool_blocked("chutes_deploy_vllm", "CHUTES_ENABLE_DEPLOY_TOOLS")
    assert d["enabled"] is False
    assert "CHUTES_ENABLE_DEPLOY_TOOLS" in d["error"]
    assert d["required_env"] == "CHUTES_ENABLE_DEPLOY_TOOLS"


def test_preview_secret_value_masks_long_strings(mcp_write_safety):
    assert mcp_write_safety.preview_secret_value("cpk_abcdefghijklmnopqrst") == "cpk_...qrst"


def test_preview_secret_value_short(mcp_write_safety):
    assert mcp_write_safety.preview_secret_value("short") == "***"


def test_redact_create_api_key_response_default(monkeypatch, mcp_write_safety):
    monkeypatch.delenv("CHUTES_ALLOW_SECRET_OUTPUT", raising=False)
    raw = {"name": "t", "secret_key": "cpk_abcdefghijklmnopqrstuvwxyz"}
    out = mcp_write_safety.redact_create_api_key_response(raw)
    assert out["_redacted"] is True
    assert out["secret_key"] == "cpk_...wxyz"


def test_redact_create_api_key_response_allow_secret_output(monkeypatch, mcp_write_safety):
    monkeypatch.setenv("CHUTES_ALLOW_SECRET_OUTPUT", "1")
    raw = {"secret_key": "cpk_abcdefghijklmnopqrstuvwxyz"}
    out = mcp_write_safety.redact_create_api_key_response(raw)
    assert out == raw

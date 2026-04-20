# Chutes in Cursor (MCP) **[BETA]**

## Install the server

```bash
uv tool install chutes-mcp-server \
  --from plugins/chutes-ai/skills/chutes-mcp-portability/mcp-server
```

`uv tool install` puts `chutes-mcp-server` on your PATH.

## Generate the config

From the repo root:

```bash
python plugins/chutes-ai/skills/chutes-mcp-portability/scripts/generate_agent_config.py \
  --target cursor --out /path/to/your/workspace
```

This writes `.cursor/mcp.json` at the workspace root:

```json
{
  "mcpServers": {
    "chutes": {
      "command": "chutes-mcp-server",
      "env": {
        "CHUTES_API_KEY": "${env:CHUTES_API_KEY}",
        "CHUTES_FINGERPRINT": "${env:CHUTES_FINGERPRINT}"
      }
    }
  }
}
```

## Set the env var for your shell

```bash
export CHUTES_API_KEY=$(python plugins/chutes-ai/skills/chutes-ai/scripts/manage_credentials.py get --field api_key)
```

On Windows PowerShell, from the repo root (dot-source loads into the current session):

```powershell
. .\scripts\export_chutes_env.ps1
```

If you want the MCP server's management tools (`chutes_list_api_keys`, `chutes_get_quota`, etc.) to work, also ensure the credential store contains the account fingerprint or export `CHUTES_FINGERPRINT`.

Do this in the shell profile (`~/.zshrc`, `~/.bashrc`) that Cursor inherits. Cursor reads `${env:CHUTES_API_KEY}` from the environment, not from `.env.local`.

If your Cursor workspace is **not** the `chutes-agent-toolkit` clone (so the MCP server cannot find `manage_credentials.py` via the current working directory), set **`CHUTES_AGENT_TOOLKIT_ROOT`** to the absolute path of that clone in your user environment or in the `env` block of `.cursor/mcp.json` (keep that file out of git if it contains machine-specific paths).

## Persist env for Start-menu Cursor (Windows)

After `manage_credentials.py set-profile`, run once from the repo root:

```powershell
.\scripts\sync_chutes_user_env.ps1
```

This copies `CHUTES_API_KEY`, `CHUTES_FINGERPRINT`, `SSL_CERT_FILE` (Certifi), and `CHUTES_AGENT_TOOLKIT_ROOT` into **User** environment variables so `chutes-mcp-server` works when Cursor is not launched from a shell. **Fully quit Cursor** afterward.

To confirm the same variables Cursor will see, open a **new** PowerShell, load User env into the session, and run `chutes-mcp-server --self-check` (should print `self-check OK`).

## Restart Cursor

File → Restart Window (or kill and relaunch). Cursor discovers MCP servers at startup.

## Verify

In Cursor, open the MCP panel and expand the `chutes` server. You should see the tools from the MCP tool map. Call `chutes_list_models` with `limit=1`; it should return a model id.

## Usable pipeline (day to day)

1. Keep User env vars current (re-run `sync_chutes_user_env.ps1` after rotating keys or moving the repo).
2. Use read tools (`chutes_list_models`, `chutes_get_quota`, etc.) freely; treat **[BETA]** write/deploy tools per [SKILL.md](../SKILL.md) (paid inference via `chutes_chat_complete` is also labeled BETA until verified on your account).
3. Hub routing and account flows: [chutes-ai/SKILL.md](../../chutes-ai/SKILL.md). Live models: `https://llm.chutes.ai/v1/models`.

## Troubleshooting

- **"Command not found: chutes-mcp-server"** — `uv tool` binaries live in `~/.local/bin`; make sure it's on PATH.
- **401 Unauthorized** — `CHUTES_API_KEY` is either empty or the wrong profile's key. Run `manage_credentials.py list-profiles` and `manage_credentials.py get --field api_key` to confirm.
- **Tools show up but one fails** — check `[BETA]` write tools specifically; they require an account with deploy permissions.

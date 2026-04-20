# Goal-Mode Checklist

This checklist defines hard gates for a goal-driven workflow:

1. User provides desired end product
2. Agent proposes plan
3. User approves plan
4. Agent executes
5. Agent verifies
6. Agent reports completion with evidence

Machine-readable source of truth: `docs/goal-mode-checklist.json`.

## Required gates

- `goal_captured`
- `plan_presented`
- `approval_received`
- `eval_pack_valid`
- `execution_completed`
- `verification_completed`
- `final_reported`

## Optional gates

- `mcp_self_check` (recommended for Chutes MCP-enabled projects)

## Usage

Run:

```bash
python scripts/run_goal_gates.py --checklist docs/goal-mode-checklist.json
```

Add `--run-optional` to also execute optional command gates.

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

Conversation semantics live in `docs/goal-mode-checklist.json`. `scripts/run_goal_gates.py` **always** runs built-in checks first:

- **Goal evidence JSON** — validates `--evidence` (default `.agent/evidence/latest.json`) via `scripts/validate_goal_evidence.py`; proves required booleans and summaries were recorded
- **Goal-mode eval coverage** — structural categories present in `evals/evals.json`

Then JSON command gates, typically:

- `goal_captured`, `plan_presented`, `approval_received`, `execution_completed`, `verification_completed`, `final_reported` (conversation-type rows — humans/scripts rely on the evidence file above)
- `eval_pack_valid`

## Optional gates

- `mcp_self_check` (recommended for Chutes MCP-enabled projects)

## Usage

Run:

```bash
python scripts/run_goal_gates.py \
  --checklist docs/goal-mode-checklist.json \
  --evals evals/evals.json \
  --evidence .agent/evidence/latest.json
```

Add `--run-optional` to also execute optional command gates.

Passing means **static / structural checks and evidence validation** succeeded — not that product behavior is correct. Project repos should add their own test/build gates.

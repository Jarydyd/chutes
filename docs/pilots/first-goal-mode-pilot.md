# First Goal-Mode Pilot (Record)

## Goal

Validate that the autonomous workflow enforces:
- plan-first behavior,
- explicit approval gate,
- checklist-gated completion.

## Pilot flow used

1. Kickoff message template:
   - `Goal: <end product>. Follow Goal-Mode contract. Plan first and wait for approval.`
2. Approval message template:
   - `Approved. Execute milestone 1..N.`
3. Gate message template:
   - `Before final answer, show checklist gate results and evidence.`

## Objective checks run

```bash
python scripts/verify_autonomous_workflow.py
```

Result: **PASSED**.

The run validated:
- eval pack structure and IDs (`scripts/run_evals.py --format summary`)
- goal-mode eval coverage and required gates (`scripts/run_goal_gates.py`)

## Observations

- Required gates passed with zero failures.
- Optional `mcp_self_check` gate is skipped unless `--run-optional` is used.

## Tightening actions from pilot

1. Keep `scripts/verify_autonomous_workflow.py` as the mandatory acceptance command.
2. Use `--run-optional` for production-grade checks when Chutes MCP reachability must be asserted.
3. Expand eval coverage if new failure patterns appear in real project runs.

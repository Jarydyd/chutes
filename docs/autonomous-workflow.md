# Autonomous Workflow Playbook (Hermes-first)

Use this playbook to run a goal-driven loop where the agent plans first, waits for approval, executes in milestones, and must pass gates before completion.

## Default contract

- Operator policy: `other-agents/system-prompt/goal-mode-operator.md`
- Pass/fail gates: `docs/goal-mode-checklist.json`
- Gate runner: `scripts/run_goal_gates.py`

## Session protocol

For each task, use these messages in order:

1. `Goal: <end product>. Follow Goal-Mode contract. Plan first and wait for approval.`
2. `Approved. Execute milestone 1..N.`
3. `Before final answer, show checklist gate results and evidence.`

## Required acceptance checks

Run both commands before accepting completion:

```bash
python scripts/run_evals.py --format summary
python scripts/run_goal_gates.py --checklist docs/goal-mode-checklist.json --evals evals/evals.json
```

Single-command wrapper:

```powershell
.\scripts\run_autonomous_workflow.ps1
```

Optional Chutes MCP runtime check:

```bash
python scripts/run_goal_gates.py --checklist docs/goal-mode-checklist.json --evals evals/evals.json --run-optional
```

Wrapper with optional gates:

```powershell
.\scripts\run_autonomous_workflow.ps1 -RunOptional
```

## Interpreting results

- If either command exits non-zero, the task is **blocked**.
- If both pass, the agent can report **delivered** with residual risks.

## Notes

- Keep Hermes as the primary planner/executor for one task at a time.
- Use Cursor + MCP as an evidence/tooling copilot (models/quota/keys checks).

# Autonomous Workflow Playbook (Hermes-first)

Use this playbook to run a goal-driven loop where the agent plans first, waits for approval, executes in milestones, and must pass gates before completion.

## Default contract

- Operator policy: `other-agents/system-prompt/goal-mode-operator.md`
- Pass/fail gates: `docs/goal-mode-checklist.json`
- Gate runner: `scripts/run_goal_gates.py`
- Goal evidence (machine-readable attestation): `.agent/evidence/latest.json` (see `.agent/evidence/schema.json` and `scripts/validate_goal_evidence.py`)

## Session protocol

For each task, use these messages in order:

1. `Goal: <end product>. Follow Goal-Mode contract. Plan first and wait for approval.`
2. `Approved. Execute milestone 1..N.`
3. `Before final answer, show checklist gate results and evidence.`

## Goal evidence file

Before claiming autonomous work is complete, create or update **goal evidence** JSON (for example copy `.agent/evidence/example.json` to `.agent/evidence/latest.json` and edit it for the session). The file records that plan, approval, execution, and verification were documented; it does **not** prove an external system behaved correctly.

Validate evidence alone:

```bash
python scripts/validate_goal_evidence.py --path .agent/evidence/latest.json
```

## Required acceptance checks

Run the workflow verifier (includes eval summary + goal gates + evidence validation):

```bash
python scripts/verify_autonomous_workflow.py --evidence .agent/evidence/latest.json
```

Or step-by-step:

```bash
python scripts/run_evals.py --format summary
python scripts/run_goal_gates.py --checklist docs/goal-mode-checklist.json --evals evals/evals.json --evidence .agent/evidence/latest.json
```

Single-command wrapper (PowerShell; defaults evidence path to `.agent/evidence/latest.json`):

```powershell
.\scripts\run_autonomous_workflow.ps1
```

Optional custom evidence path:

```powershell
.\scripts\run_autonomous_workflow.ps1 -Evidence .agent\evidence\latest.json
```

Optional Chutes MCP runtime check:

```bash
python scripts/run_goal_gates.py --checklist docs/goal-mode-checklist.json --evals evals/evals.json --evidence .agent/evidence/latest.json --run-optional
```

Wrapper with optional gates:

```powershell
.\scripts\run_autonomous_workflow.ps1 -RunOptional
```

## Interpreting results

- If any command exits non-zero, the task is **blocked**.
- When checks pass, they mean **required static checks, eval structure, and evidence validation passed only**. They do **not** prove the implementation is correct, that tests passed in a target app repo, or that production behavior is safe.
- **Project repos should add their own gates** (for example `pytest`, `npm test`, `npm run build`, linters) in addition to this toolkit’s workflow.

## Notes

- Keep Hermes as the primary planner/executor for one task at a time.
- Use Cursor + MCP as an evidence/tooling copilot (models/quota/keys checks).

## Existing repos

If you already have multiple repos, either:

1. Keep this toolkit as shared control-plane and run gates from here, or
2. Copy goal-mode files into each repo:

```powershell
.\scripts\bootstrap_goal_mode_to_repo.ps1 -TargetRepo "C:\path\to\your-repo"
```

Pilot guide: `docs/pilots/existing-repo-pilot-runbook.md`

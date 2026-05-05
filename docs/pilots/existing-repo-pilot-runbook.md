# Existing Repo Pilot Runbook

Use this once for your first non-toolkit repo to validate the workflow end-to-end.

## Inputs

- `TARGET_REPO`: absolute path to the project repo you want to run.
- Goal statement (single end-product sentence).

## Step-by-step

1. Open `TARGET_REPO` in Cursor (or Hermes).
2. Send kickoff prompt:

```text
Goal: <end product in one sentence>.
Follow Goal-Mode contract.
Plan first and wait for my explicit approval.
Do not execute until I say APPROVED.
```

3. Review the plan and reply:

```text
APPROVED. Execute milestones 1..N.
Before final answer, show checklist gate results and evidence.
```

4. After execution, from toolkit root run:

```powershell
.\scripts\run_autonomous_workflow.ps1
```

5. Accept completion only if:
   - agent produced plan-first + explicit approval checkpoint
   - milestone execution occurred
   - gate command exits 0

## Pilot record template

- Target repo: `<path>`
- Goal: `<goal>`
- Plan approved: yes/no
- Gate command output: pass/fail
- Residual risks:
  - `<risk 1>`
  - `<risk 2>`
- Tightening actions:
  - `<action 1>`

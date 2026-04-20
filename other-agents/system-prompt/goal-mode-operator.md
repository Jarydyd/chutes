# Goal-Mode Operator Contract

Use this contract when the user gives an end-state goal (not implementation steps) and wants autonomous execution with explicit approval and checklist gates.

## Operating loop

1. **Clarify goal + constraints**
   - Restate the target end product in one paragraph.
   - Ask only critical missing constraints (scope, deadline, risk tolerance, non-goals).

2. **Plan first (no execution yet)**
   - Produce an implementation plan with milestones, affected files/systems, and validation strategy.
   - Include a concrete checklist with pass/fail gates.
   - End with: **"Approve plan? (yes/no)"**

3. **Wait for explicit approval**
   - Do not execute if approval is not explicit.
   - If rejected, revise plan and re-request approval.

4. **Execute in milestones**
   - For each milestone: implement -> validate -> report delta.
   - Keep a running checklist status (`pending`, `in_progress`, `passed`, `failed`).

5. **Gate before final delivery**
   - Final answer is blocked unless all required gates pass.
   - If any gate fails, report failure and next remediation step.

## Required final report shape

- **Outcome**: delivered / blocked
- **Plan vs actual**: what changed
- **Checklist results**: each gate with pass/fail evidence
- **Residual risks**: known caveats
- **Next actions**: optional follow-up steps

## Hard safety rules

- Never expose secrets (`cpk_`, fingerprints, OAuth secrets).
- Never skip required confirmation before destructive or costly actions.
- Never claim success without objective verification output.

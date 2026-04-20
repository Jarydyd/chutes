#!/usr/bin/env python3
"""Run goal-mode gates and fail on unmet required checks.

This runner executes command-type gates from docs/goal-mode-checklist.json and
performs lightweight structural checks for eval coverage.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_CHECKLIST = Path("docs/goal-mode-checklist.json")
DEFAULT_EVALS = Path("evals/evals.json")


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _validate_checklist(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("Checklist payload must be an object")
    if not isinstance(payload.get("gates"), list) or not payload["gates"]:
        raise ValueError("Checklist must contain a non-empty gates list")
    for gate in payload["gates"]:
        if not isinstance(gate, dict) or "id" not in gate:
            raise ValueError("Each gate must be an object with an id")
        if gate.get("type") == "command":
            if not isinstance(gate.get("command"), str) or not gate["command"].strip():
                raise ValueError(f"Command gate {gate.get('id')} missing command")


def _goal_mode_eval_coverage(evals_payload: dict[str, Any]) -> tuple[bool, str]:
    evals = evals_payload.get("evals")
    if not isinstance(evals, list):
        return False, "evals payload missing evals list"
    categories = {item.get("category") for item in evals if isinstance(item, dict)}
    required = {
        "goal-mode-plan-first",
        "goal-mode-approval-gate",
        "goal-mode-checklist-evidence",
    }
    missing = sorted(required - categories)
    if missing:
        return False, f"missing goal-mode eval categories: {', '.join(missing)}"
    return True, "goal-mode eval coverage present"


def _run_command(command: str) -> tuple[bool, int, str]:
    proc = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, proc.returncode, out.strip()


def main() -> int:
    p = argparse.ArgumentParser(description="Run goal-mode checklist gates")
    p.add_argument("--checklist", default=str(DEFAULT_CHECKLIST), help="Path to checklist JSON")
    p.add_argument("--evals", default=str(DEFAULT_EVALS), help="Path to evals JSON")
    p.add_argument(
        "--run-optional",
        action="store_true",
        help="Run optional command gates as well",
    )
    args = p.parse_args()

    checklist = _load_json(Path(args.checklist))
    evals_payload = _load_json(Path(args.evals))
    _validate_checklist(checklist)

    results: list[dict[str, Any]] = []
    failures = 0

    ok, msg = _goal_mode_eval_coverage(evals_payload)
    results.append({"gate": "goal_mode_eval_coverage", "required": True, "pass": ok, "detail": msg})
    if not ok:
        failures += 1

    for gate in checklist["gates"]:
        if gate.get("type") != "command":
            continue
        required = bool(gate.get("required", False))
        if (not required) and (not args.run_optional):
            results.append(
                {
                    "gate": gate["id"],
                    "required": False,
                    "pass": True,
                    "detail": "skipped optional gate",
                }
            )
            continue
        passed, code, detail = _run_command(gate["command"])
        expected = int(gate.get("expect_exit_code", 0))
        gate_pass = passed and code == expected
        results.append(
            {
                "gate": gate["id"],
                "required": required,
                "pass": gate_pass,
                "detail": detail,
                "exit_code": code,
                "expected_exit_code": expected,
            }
        )
        if required and not gate_pass:
            failures += 1

    print(json.dumps({"failures": failures, "results": results}, indent=2))
    if failures:
        print("\nGoal gates FAILED: required gate(s) did not pass.", file=sys.stderr)
        return 2
    print("\nGoal gates PASSED: all required gates passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run goal-mode gates and fail on unmet required checks.

This runner executes command-type gates from docs/goal-mode-checklist.json and
performs lightweight structural checks for eval coverage and goal evidence JSON.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_CHECKLIST = Path("docs/goal-mode-checklist.json")
DEFAULT_EVALS = Path("evals/evals.json")
DEFAULT_EVIDENCE = Path(".agent/evidence/latest.json")
SCRIPT_DIR = Path(__file__).resolve().parent


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _coerce_command_argv(command: Any) -> list[str]:
    """Build argv for subprocess without shell=True (string commands use shlex.split)."""
    if isinstance(command, str):
        parts = shlex.split(command, posix=os.name != "nt")
        if not parts:
            raise ValueError("command string parsed to an empty argv")
        return parts
    if isinstance(command, list):
        if not command:
            raise ValueError("command list is empty")
        if not all(isinstance(x, str) for x in command):
            raise ValueError("command list must contain only strings")
        return list(command)
    raise ValueError("command must be a string or a list of strings")


def _validate_checklist(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("Checklist payload must be an object")
    if not isinstance(payload.get("gates"), list) or not payload["gates"]:
        raise ValueError("Checklist must contain a non-empty gates list")
    for gate in payload["gates"]:
        if not isinstance(gate, dict) or "id" not in gate:
            raise ValueError("Each gate must be an object with an id")
        if gate.get("type") == "command":
            cmd = gate.get("command")
            try:
                _coerce_command_argv(cmd)
            except ValueError as e:
                raise ValueError(f"Command gate {gate.get('id')}: {e}") from e


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


def _run_command(argv: list[str]) -> tuple[bool, int, str]:
    proc = subprocess.run(
        argv,
        shell=False,
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, proc.returncode, out.strip()


def _run_goal_evidence_validation(evidence_path: Path) -> tuple[bool, str]:
    validate_script = SCRIPT_DIR / "validate_goal_evidence.py"
    if not validate_script.is_file():
        return False, f"validator script missing: {validate_script}"
    proc = subprocess.run(
        [sys.executable, str(validate_script), "--path", str(evidence_path)],
        shell=False,
        capture_output=True,
        text=True,
    )
    detail = ((proc.stdout or "") + (proc.stderr or "")).strip()
    return proc.returncode == 0, detail or f"exit_code={proc.returncode}"


def main() -> int:
    p = argparse.ArgumentParser(description="Run goal-mode checklist gates")
    p.add_argument("--checklist", default=str(DEFAULT_CHECKLIST), help="Path to checklist JSON")
    p.add_argument("--evals", default=str(DEFAULT_EVALS), help="Path to evals JSON")
    p.add_argument(
        "--evidence",
        default=str(DEFAULT_EVIDENCE),
        help="Goal evidence JSON (validated before command gates)",
    )
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

    evidence_path = Path(args.evidence)
    ev_ok, ev_detail = _run_goal_evidence_validation(evidence_path)
    results.append(
        {
            "gate": "goal_evidence_valid",
            "required": True,
            "pass": ev_ok,
            "detail": ev_detail,
            "evidence_path": str(evidence_path),
        }
    )
    if not ev_ok:
        failures += 1

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
        argv = _coerce_command_argv(gate["command"])
        passed, code, detail = _run_command(argv)
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
                "argv": argv,
            }
        )
        if required and not gate_pass:
            failures += 1

    print(json.dumps({"failures": failures, "results": results}, indent=2))
    if failures:
        print("\nGoal gates FAILED: required gate(s) did not pass.", file=sys.stderr)
        return 2
    print(
        "\nStatic workflow and evidence checks PASSED. "
        "This does not prove implementation correctness."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

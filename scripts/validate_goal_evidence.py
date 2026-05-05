#!/usr/bin/env python3
"""Validate a goal-mode evidence JSON file (plan / approval / execution / verification attestation)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_PATH = Path(".agent/evidence/latest.json")

REQUIRED_BOOL_FIELDS = (
    "goal_captured",
    "plan_presented",
    "approval_received",
    "execution_completed",
    "verification_completed",
    "final_reported",
)

REQUIRED_LIST_FIELDS = (
    "changed_files",
    "commands_run",
    "test_results",
    "known_limitations",
)


def _is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_evidence(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    """Return (ok, errors)."""
    errors: list[str] = []

    for key in REQUIRED_BOOL_FIELDS:
        if key not in payload:
            errors.append(f"missing required boolean field: {key}")
            continue
        if payload[key] is not True:
            errors.append(f"required field {key} must be true, got {payload[key]!r}")

    for key in REQUIRED_LIST_FIELDS:
        if key not in payload:
            errors.append(f"missing required list field: {key}")
        elif not isinstance(payload[key], list):
            errors.append(f"field {key} must be a list, got {type(payload[key]).__name__}")

    if not _is_non_empty_str(payload.get("goal")):
        errors.append("goal must be a non-empty string")

    if not _is_non_empty_str(payload.get("approved_plan_summary")):
        errors.append("approved_plan_summary must be a non-empty string")

    return (len(errors) == 0, errors)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--path",
        default=str(DEFAULT_PATH),
        help=f"Evidence JSON file (default: {DEFAULT_PATH})",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON only (stdout).",
    )
    args = p.parse_args()

    path = Path(args.path)
    base_out: dict[str, Any] = {"path": str(path.resolve()), "valid": False}

    if not path.is_file():
        msg = f"evidence file not found: {path}"
        base_out["errors"] = [msg]
        if args.json:
            print(json.dumps(base_out, indent=2))
        else:
            print(msg, file=sys.stderr)
        return 2

    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as e:
        err = f"invalid JSON: {e}"
        base_out["errors"] = [err]
        if args.json:
            print(json.dumps(base_out, indent=2))
        else:
            print(err, file=sys.stderr)
        return 2

    if not isinstance(payload, dict):
        err = "evidence root must be a JSON object"
        base_out["errors"] = [err]
        if args.json:
            print(json.dumps(base_out, indent=2))
        else:
            print(err, file=sys.stderr)
        return 2

    ok, errors = validate_evidence(payload)
    base_out["valid"] = ok
    if errors:
        base_out["errors"] = errors

    if args.json:
        print(json.dumps(base_out, indent=2))
    elif ok:
        print(f"Goal evidence OK: {path}")
    else:
        print(json.dumps(base_out, indent=2), file=sys.stderr)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

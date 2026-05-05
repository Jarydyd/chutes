#!/usr/bin/env python3
"""Require eval summary, goal evidence, and goal gates before accepting completion."""

from __future__ import annotations

import argparse
import subprocess
import sys


def _run(cmd: list[str]) -> int:
    proc = subprocess.run(cmd)
    return proc.returncode


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--run-optional",
        action="store_true",
        help="Include optional command gates (e.g., MCP self-check).",
    )
    p.add_argument(
        "--evidence",
        default=".agent/evidence/latest.json",
        help="Goal evidence JSON passed to run_goal_gates.py",
    )
    args = p.parse_args()

    steps = [
        ["python", "scripts/run_evals.py", "--format", "summary"],
        [
            "python",
            "scripts/run_goal_gates.py",
            "--checklist",
            "docs/goal-mode-checklist.json",
            "--evals",
            "evals/evals.json",
            "--evidence",
            args.evidence,
        ],
    ]
    if args.run_optional:
        steps[1].append("--run-optional")

    for cmd in steps:
        rc = _run(cmd)
        if rc != 0:
            print(f"\nFAILED: {' '.join(cmd)}", file=sys.stderr)
            return rc

    print(
        "\nAutonomous workflow static checks PASSED. "
        "This does not prove the implementation is correct; add project tests/build gates as needed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

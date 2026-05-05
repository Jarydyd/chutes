import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_goal_evidence.py"
EXAMPLE_EVIDENCE = REPO_ROOT / ".agent" / "evidence" / "example.json"


@pytest.fixture()
def validate_goal_evidence_mod():
    spec = importlib.util.spec_from_file_location("validate_goal_evidence", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_example() -> dict:
    with EXAMPLE_EVIDENCE.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_validate_example_evidence_passes(validate_goal_evidence_mod):
    payload = _load_example()
    ok, errors = validate_goal_evidence_mod.validate_evidence(payload)
    assert ok
    assert errors == []


def test_validate_fails_when_approval_false(validate_goal_evidence_mod):
    payload = _load_example()
    payload["approval_received"] = False
    ok, errors = validate_goal_evidence_mod.validate_evidence(payload)
    assert not ok
    assert any("approval_received" in e for e in errors)


def test_validate_fails_when_goal_empty(validate_goal_evidence_mod):
    payload = _load_example()
    payload["goal"] = ""
    ok, errors = validate_goal_evidence_mod.validate_evidence(payload)
    assert not ok


def test_validate_goal_evidence_script_example_json():
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR_PATH), "--path", str(EXAMPLE_EVIDENCE), "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["valid"] is True


def test_run_goal_gates_passes_with_example_evidence():
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "run_goal_gates.py"),
            "--checklist",
            str(REPO_ROOT / "docs" / "goal-mode-checklist.json"),
            "--evals",
            str(REPO_ROOT / "evals" / "evals.json"),
            "--evidence",
            str(EXAMPLE_EVIDENCE),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "Static workflow and evidence checks PASSED" in proc.stdout


def test_run_goal_gates_fails_when_evidence_missing(tmp_path):
    missing = tmp_path / "missing.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "run_goal_gates.py"),
            "--checklist",
            str(REPO_ROOT / "docs" / "goal-mode-checklist.json"),
            "--evals",
            str(REPO_ROOT / "evals" / "evals.json"),
            "--evidence",
            str(missing),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0

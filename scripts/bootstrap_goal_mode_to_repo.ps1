#Requires -Version 5.1
<#
.SYNOPSIS
  Copy goal-mode contract/checklist/runners into another repository.

.DESCRIPTION
  This makes a target repo self-contained so you can run the same
  goal-first + approval + gate workflow without depending on toolkit-relative paths.
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetRepo
)

$ErrorActionPreference = "Stop"
$ToolkitRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Target = (Resolve-Path $TargetRepo).Path

if (-not (Test-Path (Join-Path $Target ".git"))) {
    Write-Error "TargetRepo does not look like a git repo: $Target"
}

$files = @(
    "other-agents/system-prompt/goal-mode-operator.md",
    "docs/goal-mode-checklist.json",
    "docs/goal-mode-checklist.md",
    "scripts/run_goal_gates.py",
    "scripts/verify_autonomous_workflow.py",
    "scripts/run_autonomous_workflow.ps1",
    "scripts/validate_goal_evidence.py",
    ".agent/evidence/schema.json",
    ".agent/evidence/example.json"
)

foreach ($rel in $files) {
    $src = Join-Path $ToolkitRoot $rel
    $dst = Join-Path $Target $rel
    $srcResolved = (Resolve-Path $src).Path
    if (Test-Path $dst) {
        $dstResolved = (Resolve-Path $dst).Path
        if ($srcResolved -eq $dstResolved) {
            Write-Host "Skipped $rel (source and destination are the same file)" -ForegroundColor Yellow
            continue
        }
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $dst -Parent) | Out-Null
    Copy-Item -Force $src $dst
    Write-Host "Copied $rel" -ForegroundColor Green
}

Write-Host "Bootstrap complete. In target repo run: .\\scripts\\run_autonomous_workflow.ps1" -ForegroundColor Cyan

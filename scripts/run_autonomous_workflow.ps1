#Requires -Version 5.1
<#
.SYNOPSIS
  One-command gate runner for goal-driven sessions.

.DESCRIPTION
  Runs the required autonomous workflow checks:
    1) eval pack summary validation
    2) goal gate validation

  Add -RunOptional to include optional gates (e.g. MCP self-check).
#>
param(
    [switch]$RunOptional
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $RepoRoot

$cmd = @("python", "scripts/verify_autonomous_workflow.py")
if ($RunOptional) { $cmd += "--run-optional" }

Write-Host "Running autonomous workflow checks..." -ForegroundColor Cyan
& $cmd[0] $cmd[1..($cmd.Length - 1)]
if ($LASTEXITCODE -ne 0) {
    Write-Error "Autonomous workflow checks failed."
}

Write-Host "Autonomous workflow checks passed." -ForegroundColor Green

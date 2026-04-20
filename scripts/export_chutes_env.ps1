#Requires -Version 5.1
<#
.SYNOPSIS
  Loads CHUTES_API_KEY and CHUTES_FINGERPRINT from manage_credentials.py into the current process (for Hermes, Cursor, or any tool that reads env vars).

.DESCRIPTION
  Dot-source this script so child processes inherit the variables:
    . .\scripts\export_chutes_env.ps1

  Or run without dot-sourcing to print set commands for manual copy:
    .\scripts\export_chutes_env.ps1 -PrintOnly
#>
param(
    [switch]$PrintOnly
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Manage = Join-Path $RepoRoot "plugins\chutes-ai\skills\chutes-ai\scripts\manage_credentials.py"

if (-not (Test-Path $Manage)) {
    Write-Error "manage_credentials.py not found at $Manage"
}

# Prefer Mozilla CA bundle when Windows trust chain fails (urllib + llm.chutes.ai).
if (-not $env:SSL_CERT_FILE) {
    try {
        $certPath = (& py -3.12 -c "import certifi; print(certifi.where())" 2>$null | Out-String).Trim()
        if ($certPath -and (Test-Path $certPath)) {
            $env:SSL_CERT_FILE = $certPath
        }
    } catch { }
}

function Get-CredField([string]$Field) {
    $out = if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.12 $Manage "get" "--field" $Field 2>$null
    } else {
        & python $Manage "get" "--field" $Field 2>$null
    }
    if ($LASTEXITCODE -ne 0) { return $null }
    $t = ($out | Out-String).Trim()
    if ([string]::IsNullOrWhiteSpace($t)) { return $null }
    return $t
}

$key = Get-CredField "api_key"
$fp = Get-CredField "fingerprint"

if ($PrintOnly) {
    if ($key) { Write-Output "# api_key present in store; dot-source this script to load CHUTES_API_KEY without printing it." }
    else { Write-Output "# CHUTES_API_KEY not in credential store; run manage_credentials.py set-profile first" }
    if ($fp) { Write-Output "# fingerprint present; dot-source to load CHUTES_FINGERPRINT." }
    else { Write-Output "# CHUTES_FINGERPRINT optional; needed for some management / MCP tools" }
    return
}

if ($key) {
    $env:CHUTES_API_KEY = $key
    Write-Host "CHUTES_API_KEY set (value not shown)." -ForegroundColor Green
} else {
    Write-Warning "No api_key in credential store. Run: python $Manage set-profile ..."
}

if ($fp) {
    $env:CHUTES_FINGERPRINT = $fp
    Write-Host "CHUTES_FINGERPRINT set." -ForegroundColor Green
} else {
    Write-Warning "No fingerprint stored (optional unless you use management MCP tools)."
}

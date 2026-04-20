#Requires -Version 5.1
<#
.SYNOPSIS
  Writes CHUTES_API_KEY, CHUTES_FINGERPRINT, SSL_CERT_FILE, and CHUTES_AGENT_TOOLKIT_ROOT
  to Windows *User* environment variables so Cursor (and chutes-mcp-server) see them when
  launched from the Start menu — not only from a shell where you dot-sourced export_chutes_env.ps1.

.DESCRIPTION
  Reads secrets from manage_credentials.py (py -3.12) and certifi's cacert.pem path.
  Restarts of Cursor are required after running this.

  Security: User env vars are stored under your Windows user profile (registry). Use only on a machine you trust.
#>
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Manage = Join-Path $RepoRoot "plugins\chutes-ai\skills\chutes-ai\scripts\manage_credentials.py"

if (-not (Test-Path $Manage)) {
    Write-Error "manage_credentials.py not found at $Manage"
}

function Get-CredField([string]$Field) {
    $out = & py -3.12 $Manage "get" "--field" $Field 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    $t = ($out | Out-String).Trim()
    if ([string]::IsNullOrWhiteSpace($t)) { return $null }
    return $t
}

$apiKey = Get-CredField "api_key"
$fingerprint = Get-CredField "fingerprint"

if (-not $apiKey) {
    Write-Error "No api_key in credential store. Run: py -3.12 $Manage set-profile ..."
}

$certPath = (& py -3.12 -c "import certifi; print(certifi.where())" 2>$null | Out-String).Trim()
if (-not $certPath -or -not (Test-Path $certPath)) {
    Write-Error "certifi not found. Run: py -3.12 -m pip install certifi"
}

[Environment]::SetEnvironmentVariable("CHUTES_API_KEY", $apiKey, "User")
if ($fingerprint) {
    [Environment]::SetEnvironmentVariable("CHUTES_FINGERPRINT", $fingerprint, "User")
} else {
    [Environment]::SetEnvironmentVariable("CHUTES_FINGERPRINT", $null, "User")
    Write-Warning "No fingerprint in store; management MCP tools may fail until you set-profile with --fingerprint."
}

[Environment]::SetEnvironmentVariable("SSL_CERT_FILE", $certPath, "User")
[Environment]::SetEnvironmentVariable("CHUTES_AGENT_TOOLKIT_ROOT", $RepoRoot, "User")

Write-Host "User environment variables updated (CHUTES_API_KEY, CHUTES_FINGERPRINT, SSL_CERT_FILE, CHUTES_AGENT_TOOLKIT_ROOT)." -ForegroundColor Green
Write-Host "Fully quit and reopen Cursor so MCP picks up the new values." -ForegroundColor Yellow

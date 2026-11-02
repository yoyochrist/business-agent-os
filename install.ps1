# Business Agent OS — user-level Windows installer
$ErrorActionPreference = "Stop"
$repo = "https://github.com/yoyochrist/business-agent-os"
$workflow = "$repo/actions/workflows/build-desktop.yml"
$installDir = Join-Path $env:LOCALAPPDATA "BusinessAgentOS"
$exe = Join-Path $installDir "BusinessAgentOS.exe"
Write-Host "Business Agent OS installer"
if (-not (Get-Command Invoke-RestMethod -ErrorAction SilentlyContinue)) { throw "PowerShell web requests are required." }
New-Item -ItemType Directory -Force -Path $installDir | Out-Null
# Download source archive from the pinned repository branch. Requires Python.
# Prefer a published release binary; if no release exists, provide build page.
$api = "https://api.github.com/repos/yoyochrist/business-agent-os/releases/latest"
try {
  $release = Invoke-RestMethod -Uri $api -Headers @{ "User-Agent" = "BusinessAgentOS-Installer" }
  $asset = $release.assets | Where-Object { $_.name -eq "BusinessAgentOS-Windows.exe" } | Select-Object -First 1
} catch { $asset = $null }
if (-not $asset) {
  Write-Host "No released Windows executable yet." -ForegroundColor Yellow
  Write-Host "Download the Windows build from: $workflow"
  Write-Host "Or install from source with Python: https://github.com/yoyochrist/business-agent-os"
  exit 1
}
Write-Host "Downloading official GitHub release: $($release.tag_name)"
Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $exe
Write-Host "Installed to $exe"
$start = Join-Path $installDir "Start Business Agent OS.cmd"
Set-Content -LiteralPath $start -Value '@echo off
start "" "%LOCALAPPDATA%\BusinessAgentOS\BusinessAgentOS.exe"' -Encoding ASCII
Write-Host "Checking AI providers..."
if (-not (Get-Command codex -ErrorAction SilentlyContinue) -and -not (Get-Command claude -ErrorAction SilentlyContinue)) {
  Write-Host "Install and sign in to Codex CLI or Claude Code CLI before running AI tasks."
  Write-Host "Codex: https://developers.openai.com/codex/cli/"
  Write-Host "Claude Code: https://code.claude.com/docs/en/overview"
}
Write-Host "Run: & '$exe'"

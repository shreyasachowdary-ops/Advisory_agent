# One-time push to GitHub without Windows Credential Manager (wincredman).
# Prerequisites:
#   1. Create empty repo: https://github.com/shreyasachowdary-ops/Advisory_agent
#   2. Personal Access Token with "repo" scope (classic) or Contents: Read and write (fine-grained)
#
# Usage (PowerShell on the advisor server):
#   $env:GITHUB_TOKEN = "ghp_xxxxxxxx"
#   .\scripts\push-to-github.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

if (-not $env:GITHUB_TOKEN) {
    Write-Error "Set GITHUB_TOKEN to a GitHub PAT with repo access, then run this script again."
}

$remote = "https://github.com/shreyasachowdary-ops/Advisory_agent.git"
$pushUrl = "https://x-access-token:$($env:GITHUB_TOKEN)@github.com/shreyasachowdary-ops/Advisory_agent.git"

git remote set-url origin $remote
git push $pushUrl HEAD:main
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

git branch -M main
git remote set-url origin $remote
Write-Host "Push complete. Remote origin: $remote"

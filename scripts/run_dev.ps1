$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

$backendJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location "$root\backend"
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        & ".venv\Scripts\Activate.ps1"
    }
    uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
} -ArgumentList $Root

$frontendJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location "$root\frontend"
    npm run dev
} -ArgumentList $Root

Write-Host "Backend job ID: $($backendJob.Id)"
Write-Host "Frontend job ID: $($frontendJob.Id)"
Write-Host "Open http://127.0.0.1:43123"
Write-Host "Press Ctrl+C to stop"

try {
    Wait-Job $backendJob, $frontendJob
} finally {
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
}

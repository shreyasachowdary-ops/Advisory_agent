# Apply advisor integration to lnpl_erp_dev_v1
# Usage: .\apply-to-erp.ps1 -ErpRoot "C:\path\to\lnpl_erp_dev_v1"

param(
    [Parameter(Mandatory = $true)]
    [string]$ErpRoot
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Test-Path $ErpRoot)) {
    Write-Error "ERP root not found: $ErpRoot"
}

$pagesDest = Join-Path $ErpRoot "Pages"
$srcPagesDest = Join-Path $ErpRoot "src\Pages"
New-Item -ItemType Directory -Force -Path $pagesDest | Out-Null
New-Item -ItemType Directory -Force -Path $srcPagesDest | Out-Null

Copy-Item (Join-Path $ScriptDir "Pages\AdvisorPage.js") (Join-Path $pagesDest "AdvisorPage.js") -Force
Copy-Item (Join-Path $ScriptDir "src\Pages\AdvisorPage.js") (Join-Path $srcPagesDest "AdvisorPage.js") -Force
Write-Host "Copied AdvisorPage.js"

$appJs = Join-Path $ErpRoot "src\components\App.js"
if (-not (Test-Path $appJs)) { Write-Error "App.js not found" }

$appLines = Get-Content $appJs
if ($appLines -notmatch "AdvisorPage") {
    $newApp = @()
    foreach ($line in $appLines) {
        $newApp += $line
        if ($line -match "import LeaveRegisterPage") {
            $newApp += 'import AdvisorPage from "../Pages/AdvisorPage";'
        }
        if ($line -match 'path="/leaveregister"') {
            $newApp += '              <Route path="/advisor" element={<AdvisorPage />} />'
        }
    }
    Set-Content $appJs $newApp
    Write-Host "Patched App.js"
}

$dashJs = Join-Path $ErpRoot "src\components\Applicant\dashboard_applicant.js"
if ((Test-Path $dashJs) -and ((Get-Content $dashJs -Raw) -notmatch "/advisor")) {
    $dashLines = Get-Content $dashJs
    $newDash = @()
    foreach ($line in $dashLines) {
        $newDash += $line
        if ($line -match 'Lesson Planning') {
            $newDash += '        { to: "/advisor", label: "Parent/Teacher Advisor" },'
        }
    }
    Set-Content $dashJs $newDash
    Write-Host "Patched dashboard sidebar"
}

$configJson = Join-Path $ErpRoot "src\components\contexts\config_web.json"
if (Test-Path $configJson) {
    $raw = Get-Content $configJson -Raw
    if ($raw -notmatch "advisor_base_url") {
        $raw = $raw -replace '"cors_url":\s*"[^"]+"', '"cors_url": "http://106.51.158.20:3000",
        "advisor_base_url": "http://127.0.0.1:8787"'
        Set-Content $configJson $raw
        Write-Host "Patched config_web.json"
    }
}

Write-Host "Integration applied. Restart ERP and advisor backend."

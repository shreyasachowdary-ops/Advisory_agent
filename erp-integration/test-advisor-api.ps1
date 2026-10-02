# Integration test — same API calls AdvisorPage.js makes
param([string]$ApiBase = "http://127.0.0.1:8787")

Write-Host "=== Health ==="
$health = Invoke-RestMethod -Uri "$ApiBase/api/health"
Write-Host "status=$($health.status) ollama=$($health.ollama)"

Write-Host "`n=== Normal chat (drop-off) ==="
$normal = Invoke-RestMethod -Uri "$ApiBase/api/chat" -Method POST -ContentType "application/json" -Body (@{
    message = "My 4-year-old is upset at preschool drop-off."
    audience = "parent"
    age_band = "4_years"
    language = "en"
} | ConvertTo-Json)
Write-Host "risk=$($normal.risk_level) sources=$($normal.sources.Count) answer_len=$($normal.answer.Length)"

Write-Host "`n=== Urgent escalation ==="
$urgent = Invoke-RestMethod -Uri "$ApiBase/api/chat" -Method POST -ContentType "application/json" -Body (@{
    message = "A child told me they want to kill themselves."
    audience = "teacher"
    age_band = "5_years"
    language = "en"
} | ConvertTo-Json)
Write-Host "risk=$($urgent.risk_level) review=$($urgent.requires_human_review)"

if ($normal.risk_level -ne "normal") { exit 1 }
if ($urgent.risk_level -ne "urgent") { exit 1 }
if ($urgent.requires_human_review -ne $true) { exit 1 }

Write-Host "`nAll integration checks passed."

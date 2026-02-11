$ErrorActionPreference = "Stop"

$baseUrl = "http://localhost:8080"
$payloads = Get-Content -Raw -Path "examples/demo_requests.json" | ConvertFrom-Json

foreach ($item in $payloads) {
  Write-Host "Running: $($item.name)"
  $resp = Invoke-RestMethod -Method Post -Uri "$baseUrl/run" -ContentType "application/json" -Body ($item.payload | ConvertTo-Json -Depth 6)
  Write-Host "- run_id: $($resp.run_id)"
  Write-Host "- duration_ms: $($resp.duration_ms)"
  Write-Host "- quality: lint=$($resp.quality_report.lint.status) test=$($resp.quality_report.test.status) coverage=$($resp.quality_report.coverage.status)"
  Write-Host ""
}

Write-Host "Fetching ops data..."
$runs = Invoke-RestMethod -Method Get -Uri "$baseUrl/runs?limit=5"
$stats = Invoke-RestMethod -Method Get -Uri "$baseUrl/runs/stats"
$mem = Invoke-RestMethod -Method Get -Uri "$baseUrl/memory/stats"

Write-Host "Recent runs: $($runs.Count)"
Write-Host "Stats: total_runs=$($stats.total_runs), projects=$($stats.project_count)"
Write-Host "Memory: projects=$($mem.project_count), entries=$($mem.total_entries)"

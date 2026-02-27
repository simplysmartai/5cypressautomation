# Weekly Lighthouse Audit + Monitoring Script
# Purpose: Run Lighthouse on 5cypress.com every week, track scores, alert on regressions
# Run via: PowerShell -ExecutionPolicy Bypass -File audit-lighthouse-weekly.ps1

param(
    [string]$url = "https://5cypress.com",
    [string]$outputDir = "./audits",
    [int]$perfThreshold = 85,
    [int]$a11yThreshold = 90,
    [int]$seoThreshold = 90
)

# Ensure output directory exists
if (!(Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportFile = "$outputDir/lighthouse-$timestamp.json"

Write-Host "🔍 Running Lighthouse audit on $url ..."
Write-Host "Report will be saved to: $reportFile"

# Run Lighthouse via Chrome/Chromium headless
# Uses Lighthouse CLI globally installed
npx lighthouse $url `
    --chrome-flags="--headless --no-sandbox" `
    --output=json `
    --output-path=$reportFile `
    --quiet `
    --only-categories=performance,accessibility,best-practices,seo

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Lighthouse audit failed. Exiting."
    exit 1
}

Write-Host "✅ Audit complete. Loading results..."

# Parse JSON and extract scores
$data = Get-Content $reportFile | ConvertFrom-Json
$scores = @{
    Performance = [math]::Round($data.lighthouseResult.categories.performance.score * 100)
    Accessibility = [math]::Round($data.lighthouseResult.categories.accessibility.score * 100)
    BestPractices = [math]::Round($data.lighthouseResult.categories."best-practices".score * 100)
    SEO = [math]::Round($data.lighthouseResult.categories.seo.score * 100)
}

# Print scores
Write-Host "`n📊 Lighthouse Scores:"
Write-Host "  Performance:      $($scores.Performance)/100"
Write-Host "  Accessibility:    $($scores.Accessibility)/100"
Write-Host "  Best Practices:   $($scores.BestPractices)/100"
Write-Host "  SEO:              $($scores.SEO)/100"

# Check against thresholds
$alerts = @()

if ($scores.Performance -lt $perfThreshold) {
    $alerts += "⚠️  Performance score dropped below $perfThreshold ($($scores.Performance) detected)"
}
if ($scores.Accessibility -lt $a11yThreshold) {
    $alerts += "⚠️  Accessibility score dropped below $a11yThreshold ($($scores.Accessibility) detected)"
}
if ($scores.BestPractices -lt 70) {
    $alerts += "⚠️  Best Practices score dropped below 70 ($($scores.BestPractices) detected)"
}
if ($scores.SEO -lt $seoThreshold) {
    $alerts += "⚠️  SEO score dropped below $seoThreshold ($($scores.SEO) detected)"
}

if ($alerts.Count -gt 0) {
    Write-Host "`n🚨 ALERTS:"
    foreach ($alert in $alerts) {
        Write-Host $alert
    }
    Write-Host "`n→ Review the full report: $reportFile"
    Write-Host "→ Run: npx lighthouse $url --view"
} else {
    Write-Host "`n✅ All scores above thresholds. Site is healthy."
}

# Optional: Save CSV summary for trend tracking
$csvFile = "$outputDir/summary.csv"
$row = "$timestamp,$($scores.Performance),$($scores.Accessibility),$($scores.BestPractices),$($scores.SEO)"

if (!(Test-Path $csvFile)) {
    "Timestamp,Performance,Accessibility,BestPractices,SEO" | Out-File $csvFile
}

$row | Add-Content $csvFile
Write-Host "`n📈 Summary appended to: $csvFile"

# Exit with error code if any critical threshold failed
if ($alerts.Count -gt 0) {
    exit 1
}
exit 0

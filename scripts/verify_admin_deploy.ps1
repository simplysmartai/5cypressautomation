param(
  [Parameter(Mandatory = $true)]
  [string]$BaseUrl,

  [Parameter(Mandatory = $true)]
  [string]$AdminUser,

  [Parameter(Mandatory = $true)]
  [string]$AdminPass,

  [string]$AuditUrl = "https://www.5cypress.com",

  [ValidateSet("mobile", "desktop")]
  [string]$Strategy = "mobile",

  [switch]$TestSeoAudit
)

$ErrorActionPreference = "Stop"

function New-BasicAuthHeader {
  param(
    [string]$User,
    [string]$Pass
  )

  $pair = "$User`:$Pass"
  $token = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
  return @{ Authorization = "Basic $token" }
}

function Test-Endpoint {
  param(
    [string]$Name,
    [string]$Url,
    [hashtable]$Headers = @{}
  )

  try {
    $resp = Invoke-WebRequest -Uri $Url -Headers $Headers -UseBasicParsing -TimeoutSec 60
    [PSCustomObject]@{
      Name = $Name
      Url = $Url
      StatusCode = [int]$resp.StatusCode
      Ok = ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300)
      Message = "OK"
    }
  }
  catch {
    $status = 0
    $message = $_.Exception.Message
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
      $status = [int]$_.Exception.Response.StatusCode
    }

    [PSCustomObject]@{
      Name = $Name
      Url = $Url
      StatusCode = $status
      Ok = $false
      Message = $message
    }
  }
}

$root = $BaseUrl.TrimEnd('/')
$auth = New-BasicAuthHeader -User $AdminUser -Pass $AdminPass

$checks = @(
  @{ Name = "Health"; Url = "$root/health"; Headers = @{} },
  @{ Name = "Admin Home"; Url = "$root/admin/"; Headers = $auth },
  @{ Name = "Admin Clients Page"; Url = "$root/admin/clients"; Headers = $auth },
  @{ Name = "Admin SEO Page"; Url = "$root/admin/seo"; Headers = $auth },
  @{ Name = "Admin Clients API"; Url = "$root/api/admin/clients"; Headers = $auth }
)

if ($TestSeoAudit) {
  $encoded = [Uri]::EscapeDataString($AuditUrl)
  $checks += @{ Name = "Admin SEO API"; Url = "$root/api/admin/seo-audit?url=$encoded&strategy=$Strategy"; Headers = $auth }
}

$results = foreach ($check in $checks) {
  Test-Endpoint -Name $check.Name -Url $check.Url -Headers $check.Headers
}

$results | Format-Table -AutoSize

if ($results.Ok -contains $false) {
  Write-Host "`nVerification failed: one or more endpoints are unhealthy." -ForegroundColor Red
  exit 1
}

Write-Host "`nVerification passed: all tested endpoints returned success." -ForegroundColor Green
exit 0

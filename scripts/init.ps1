# Points the Power BI project at this clone (sets the RepoRoot parameter). UNTESTED: authored without PowerShell.
# Usage:  powershell -ExecutionPolicy Bypass -File scripts\init.ps1 [-Reset]
param([switch]$Reset)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$tmdl = Join-Path $root 'powerbi\Telco Churn Report.SemanticModel\definition\expressions.tmdl'
if ($Reset) { $value = 'C:\telco-churn-analytics' }
else {
  $raw = Join-Path $root 'data\raw\Telco-Customer-Churn.csv'
  if (-not (Test-Path $raw)) { throw "Dataset not found: $raw" }
  $value = (Resolve-Path $root).Path.TrimEnd('\')
}
$text = [System.IO.File]::ReadAllText($tmdl)
$pattern = '(?m)^(expression RepoRoot = ")(.*?)(" meta \[)'
if ($text -notmatch $pattern) { throw 'RepoRoot line not found in expressions.tmdl' }
$new = [regex]::Replace($text, $pattern, { param($m) $m.Groups[1].Value + $value + $m.Groups[3].Value }, 1)
[System.IO.File]::WriteAllText($tmdl, $new, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "RepoRoot set to $value"

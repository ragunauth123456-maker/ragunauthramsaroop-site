param([switch]$DryRun)
$ErrorActionPreference = 'Stop'
$repo = 'C:\AgentSwarm\ragunauth-site'
$remote = 'ragunauth123456-maker/ragunauthramsaroop-site'
$logDir = 'C:\AgentSwarm\qa-logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$log = Join-Path $logDir ("weekly-qa-$stamp.log")
$problems = [System.Collections.Generic.List[string]]::new()
$report = [System.Collections.Generic.List[string]]::new()
$report.Add("RR Free Tools weekly QA: $(Get-Date -Format o)")
$report.Add("Environment: $env:COMPUTERNAME")
try {
  $branch = git -C $repo rev-parse --abbrev-ref HEAD
  $dirty = (git -C $repo status --porcelain --untracked-files=no | Out-String).Trim()
  if ($branch -ne 'main' -or $dirty) {
    $report.Add("Workspace not clean on main; checking existing files (branch=$branch).")
  } else {
    $oldPref = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $pullOutput = & git -C $repo pull --ff-only origin main 2>&1
    $pullExit = $LASTEXITCODE
    $ErrorActionPreference = $oldPref
    if ($pullExit -ne 0) { $problems.Add('GitHub main sync failed: ' + ($pullOutput | Out-String)) }
  }
} catch { $problems.Add("Git sync error: $($_.Exception.Message)") }
try {
  Push-Location $repo
  $output = & python scripts\validate_site.py 2>&1
  $code = $LASTEXITCODE
  Pop-Location
  $report.Add(($output | Out-String).Trim())
  if ($code -ne 0) { $problems.Add("Local site validation failed (exit $code).") }
  foreach ($file in @('tools/assets/tools.js','tools/assets/growth-tools.js','tools/assets/analytics-loader.js')) {
    $output = & node --check (Join-Path $repo $file) 2>&1
    if ($LASTEXITCODE -ne 0) { $problems.Add("JavaScript syntax failed: $file $output") }
  }
} catch { $problems.Add("QA error: $($_.Exception.Message)") }
try {
  $raw = gh api "repos/$remote/pages" 2>&1
  if ($LASTEXITCODE -ne 0) { $problems.Add("GitHub Pages API check failed: $raw") }
  else {
    $p = ($raw | Out-String | ConvertFrom-Json)
    if ($p.status -in @('building','pending')) {
      for ($retry=0; $retry -lt 8 -and $p.status -ne 'built'; $retry++) {
        Start-Sleep -Seconds 12
        $p = (gh api "repos/$remote/pages" | Out-String | ConvertFrom-Json)
      }
    }
    $report.Add("GitHub Pages status=$($p.status) HTTPS=$($p.https_enforced) cert=$($p.https_certificate.state)")
    if ($p.status -ne 'built' -or -not $p.https_enforced -or $p.https_certificate.state -ne 'approved') {
      $problems.Add('GitHub Pages deployment, HTTPS or certificate needs investigation.')
    }
  }
} catch { $problems.Add("Pages check error: $($_.Exception.Message)") }
$title = 'Automated RR Free Tools website QA failure'
if ($problems.Count -eq 0) { $report.Add('OVERALL: PASS') }
else {
  $report.Add('OVERALL: FAIL')
  foreach ($item in $problems) { $report.Add("FAIL: $item") }
}
$report | Set-Content -Path $log -Encoding UTF8
Write-Output ($report -join [Environment]::NewLine)
try {
  $issuesRaw = gh issue list -R $remote --state open --limit 100 --json number,title 2>&1
  $issues = @($issuesRaw | Out-String | ConvertFrom-Json)
  $existing = @($issues | Where-Object { $_.title -eq $title }) | Select-Object -First 1
  if (-not $DryRun -and $problems.Count -gt 0 -and -not $existing) {
    $body = "Weekly QA failed on $(Get-Date -Format o)." + [Environment]::NewLine + ($problems -join [Environment]::NewLine) + [Environment]::NewLine + "Local log: $log"
    gh issue create -R $remote --title $title --body $body 2>&1 | Out-Null
  } elseif (-not $DryRun -and $problems.Count -eq 0 -and $existing) {
    gh issue comment $existing.number -R $remote --body "Latest scheduled check passed. Closing the QA alert." 2>&1 | Out-Null
    gh issue close $existing.number -R $remote 2>&1 | Out-Null
  }
} catch { Add-Content -Path $log -Value "GitHub issue notification problem: $_" }
Get-ChildItem -Path $logDir -Filter 'weekly-qa-*.log' -File |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-90) } |
  Remove-Item -Force -ErrorAction SilentlyContinue
if ($problems.Count) { exit 1 }
exit 0

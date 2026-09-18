# 提交 / 部署前预检
#   用法：pwsh -File tools\preflight.ps1
#   内容：① JS 语法硬校验（不通过立即中止）② 渲染后功能冒烟测试 ③ 移动端 320–1280 版式审计
# 说明：冒烟测试会真正用无头浏览器打开 10 个页面，检查 app.js 是否生效、关键区域是否渲染出内容，
#       能拦住「语法错误导致整站空白」这类只看语法与版式发现不了的问题。

param(
  [switch]$SkipMobile
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$edge = @(
  "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
  "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
  "C:\Program Files\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw "未找到 Edge/Chrome" }
$env:PYTHONIOENCODING = 'utf-8'

Write-Host "`n【1/3】JS 语法校验" -ForegroundColor Cyan
node --check assets\js\app.js
if ($LASTEXITCODE -ne 0) { Write-Host "✗ assets/js/app.js 语法错误，已中止" -ForegroundColor Red; exit 1 }
Get-ChildItem data\*.js | ForEach-Object {
  node --check $_.FullName
  if ($LASTEXITCODE -ne 0) { Write-Host "✗ $($_.Name) 语法错误，已中止" -ForegroundColor Red; exit 1 }
}
Write-Host "✓ app.js 与 data/*.js 语法通过" -ForegroundColor Green

Write-Host "`n【1.5/3】出刊脚本离线回归测试（用假 LLM 跑一遍 main()，不花 API 费用）" -ForegroundColor Cyan
python tools\test_generate_issue.py
if ($LASTEXITCODE -ne 0) {
  Write-Host "✗ 出刊脚本测试未通过，已中止（这类 bug 会让每周自动出刊失败）" -ForegroundColor Red
  exit 1
}

# 预览服务
$site = $null
try { Invoke-WebRequest "http://localhost:8765/" -UseBasicParsing -TimeoutSec 3 | Out-Null }
catch {
  $site = Start-Process python -ArgumentList "-m","http.server","8765","--directory","$root" -PassThru -WindowStyle Hidden
  Start-Sleep -Seconds 2
}

$recv = Start-Process python -ArgumentList "$PSScriptRoot\mobile_report_server.py","8766" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 2

try {
  Write-Host "`n【2/3】渲染后功能冒烟测试" -ForegroundColor Cyan
  Remove-Item "$PSScriptRoot\mobile-report.json" -Force -ErrorAction SilentlyContinue
  $prev = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
  & $edge --headless=new --disable-gpu --no-first-run --user-data-dir="$env:TEMP\preflight-smoke" `
    --window-size=1400,900 --virtual-time-budget=120000 --screenshot="$env:TEMP\preflight-smoke.png" `
    "http://localhost:8765/tools/site-smoke.html?w=375" 2>$null | Out-Null
  $ErrorActionPreference = $prev
  Start-Sleep -Seconds 2
  $smoke = python "$PSScriptRoot\site_smoke_summary.py" 2>&1
  $smoke | ForEach-Object { Write-Host $_ }
  $smokeFail = $LASTEXITCODE -ne 0

  if (-not $SkipMobile) {
    Write-Host "`n【3/3】移动端版式审计" -ForegroundColor Cyan
    & "$PSScriptRoot\mobile-check.ps1"
    $mobileFail = $LASTEXITCODE -ne 0
  } else { $mobileFail = $false }
} finally {
  if ($recv -and -not $recv.HasExited) { Stop-Process -Id $recv.Id -Force }
}

Write-Host ""
if ($smokeFail -or $mobileFail) {
  Write-Host "❌ 预检未通过：冒烟=$(if($smokeFail){'失败'}else{'通过'}) 版式=$(if($mobileFail){'失败'}else{'通过'})" -ForegroundColor Red
  exit 1
}
Write-Host "✅ 预检全部通过，可以提交 / 部署" -ForegroundColor Green

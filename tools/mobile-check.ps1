# 移动端适配一键自检
#   用法：pwsh -File tools\mobile-check.ps1            （默认检测 320 / 375 / 414 / 768 / 1280）
#        pwsh -File tools\mobile-check.ps1 -Widths 390 （自定义视口宽度）
# 原理：起本地预览服务 + 结果接收器，用无头 Edge 以精确 iframe 宽度渲染 9 个页面，
#       逐元素检测横向溢出与触控目标（WCAG 2.5.8 AA = 24px / 44px 推荐），结果落 JSON 后打印。
# 注意：不要用 `msedge --headless --window-size=375`，Windows 下窗口有最小宽度，布局会按更宽渲染再裁切，读数失真。

param(
  [int[]]$Widths = @(320, 375, 414, 768, 1280),
  [int]$SitePort = 8765,
  [int]$ReportPort = 8766
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$edge = @(
  "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
  "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
  "C:\Program Files\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $edge) { throw "未找到 Edge/Chrome，无法进行自动渲染检测" }
Write-Host "浏览器：$edge" -ForegroundColor Cyan

# 预览服务（若未运行则启动）
$site = $null
try { Invoke-WebRequest "http://localhost:$SitePort/" -UseBasicParsing -TimeoutSec 3 | Out-Null; Write-Host "预览服务已在运行：$SitePort" }
catch {
  $site = Start-Process python -ArgumentList "-m","http.server","$SitePort","--directory","$root" -PassThru -WindowStyle Hidden
  Start-Sleep -Seconds 2
  Write-Host "已启动预览服务：http://localhost:$SitePort" -ForegroundColor Cyan
}

# 结果接收器
$recv = Start-Process python -ArgumentList "$PSScriptRoot\mobile_report_server.py","$ReportPort" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 2

$env:PYTHONIOENCODING = 'utf-8'
$report = "$PSScriptRoot\mobile-report.json"
$fail = 0
try {
  foreach ($w in $Widths) {
    Remove-Item $report -Force -ErrorAction SilentlyContinue
    $shot = "$env:TEMP\mobile-check-$w.png"
    # Edge 会往 stderr 写无害日志；在 Stop 策略下会被当成错误中断脚本，故此处临时放宽
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & $edge --headless=new --disable-gpu --no-first-run --user-data-dir="$env:TEMP\mcheck$w" `
      --window-size=1600,900 --virtual-time-budget=120000 --screenshot="$shot" `
      "http://localhost:$SitePort/tools/mobile-audit.html?w=$w" 2>$null | Out-Null
    $ErrorActionPreference = $prevEap
    Start-Sleep -Seconds 2
    Write-Host "`n########## 视口 $w px ##########" -ForegroundColor Yellow
    if (-not (Test-Path $report)) { Write-Host "未收到检测报告" -ForegroundColor Red; $fail++; continue }
    $out = python "$PSScriptRoot\mobile_report_summary.py" 2>&1
    $out | Where-Object { $_ -match '##|AA不达标|溢出元素|横向溢出页面数' }
    if ($out -match '仍需修复') { $fail++ }
  }
} finally {
  if ($recv -and -not $recv.HasExited) { Stop-Process -Id $recv.Id -Force }
  if ($site -and -not $site.HasExited) { Write-Host "`n提示：预览服务仍在后台运行（端口 $SitePort）" }
}

Write-Host ""
if ($fail -eq 0) { Write-Host "✅ 全部视口通过：无横向溢出、无 AA 触控不达标" -ForegroundColor Green }
else { Write-Host "❌ 有 $fail 个视口存在问题，详见上面输出" -ForegroundColor Red; exit 1 }

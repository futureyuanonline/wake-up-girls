# 本地跑一期（内测用）—— 先看内容再决定要不要发布
#
#   用法：
#     pwsh -File tools\run_issue_local.ps1              # 采集 + 成稿 + 繁简同步，只改本地文件，不提交
#     pwsh -File tools\run_issue_local.ps1 -Publish     # 内容满意后再加这个开关：提交并推送（触发线上部署）
#
#   密钥放哪：D:\wake-up-girls\.env.local（已被 .gitignore 忽略），内容形如
#     LLM_API_KEY=sk-xxxxxxxxxxxxxxxx
#     LLM_BASE_URL=https://api.deepseek.com/v1      # 可省略，默认就是 DeepSeek
#     LLM_MODEL=deepseek-chat                       # 可省略

param(
  [switch]$Publish,
  [switch]$SkipFetch          # 跳过采集，直接用现有 drafts/
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$env:PYTHONIOENCODING = 'utf-8'

# ── 1) 载入 .env.local ──
$envFile = Join-Path $root '.env.local'
if (-not (Test-Path $envFile)) {
  Write-Host "✗ 未找到 $envFile" -ForegroundColor Red
  Write-Host "  请新建该文件（记事本即可），写入一行：LLM_API_KEY=你的Key" -ForegroundColor Yellow
  exit 1
}
$loaded = @()
Get-Content $envFile -Encoding UTF8 | ForEach-Object {
  $line = $_.Trim()
  if ($line -eq '' -or $line.StartsWith('#')) { return }
  $i = $line.IndexOf('=')
  if ($i -lt 1) { return }
  $k = $line.Substring(0, $i).Trim()
  $v = $line.Substring($i + 1).Trim().Trim('"').Trim("'")
  [Environment]::SetEnvironmentVariable($k, $v, 'Process')
  $loaded += $k
}
if ($loaded -notcontains 'LLM_API_KEY') {
  Write-Host "✗ .env.local 里没有 LLM_API_KEY" -ForegroundColor Red
  exit 1
}
$keyLen = $env:LLM_API_KEY.Length
Write-Host "✓ 已载入密钥：$($loaded -join ', ')（LLM_API_KEY 长度 $keyLen，结尾 …$($env:LLM_API_KEY.Substring([Math]::Max(0,$keyLen-4)))）" -ForegroundColor Green
Write-Host "  模型：$($env:LLM_BASE_URL) / $($env:LLM_MODEL)"

# ── 2) 采集 ──
if (-not $SkipFetch) {
  Write-Host "`n【1/3】采集全球候选…" -ForegroundColor Cyan
  python tools\fetch_news.py
  if ($LASTEXITCODE -ne 0) { Write-Host "✗ 采集失败" -ForegroundColor Red; exit 1 }
} else {
  Write-Host "`n【1/3】跳过采集（-SkipFetch）" -ForegroundColor DarkGray
}

# ── 3) 成稿（会修改 data/issues.js） ──
Write-Host "`n【2/3】LLM 成稿（含校验，不通过会拒绝）…" -ForegroundColor Cyan
python tools\generate_issue.py
if ($LASTEXITCODE -ne 0) { Write-Host "✗ 成稿失败（校验未通过或接口报错）" -ForegroundColor Red; exit 1 }

# ── 4) 繁简同步 ──
Write-Host "`n【3/3】同步繁体版…" -ForegroundColor Cyan
node build_i18n.mjs
if ($LASTEXITCODE -ne 0) { Write-Host "✗ 繁简同步失败" -ForegroundColor Red; exit 1 }

# ── 5) 摘要 ──
Write-Host "`n=== 本地改动 ===" -ForegroundColor Yellow
git status --short
Write-Host "`n预览：本地服务已在跑的话打开 http://localhost:8765/index.html" -ForegroundColor Yellow
Write-Host "      或运行：pwsh -File tools\viewport-preview.html 说明见 README「本地预览」"

if ($Publish) {
  Write-Host "`n=== 发布：提交并推送（会触发线上自动部署） ===" -ForegroundColor Yellow
  git add -A
  git commit -m "issue: $(Get-Date -Format 'yyyy-MM-dd') 出刊"
  git push
  Write-Host "✓ 已推送，Cloudflare 约 30 秒后自动上线" -ForegroundColor Green
} else {
  Write-Host "`n（未发布）内容满意就运行：pwsh -File tools\run_issue_local.ps1 -Publish -SkipFetch" -ForegroundColor Yellow
}

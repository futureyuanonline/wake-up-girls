# 安全地把 DeepSeek API Key 写进本地 .env.local
#
#   用法（在你自己的 PowerShell 窗口里运行，在项目目录下）：
#     .\tools\set_key.ps1
#
#   特点：
#     * 用 Read-Host -AsSecureString 读取，**输入时不显示、不进入命令历史**
#     * 只写入 .env.local（已被 .gitignore 忽略，永远不会被提交）
#     * 写完立即做一次格式检查（只显示长度与末尾 4 位，不泄露完整 Key）

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root '.env.local'

Write-Host "=== 设置本地出刊密钥 ===" -ForegroundColor Cyan
Write-Host "项目目录：$root"
Write-Host ""
Write-Host "请粘贴 DeepSeek API Key（形如 sk-xxxxxxxx，输入时屏幕不会显示），然后回车：" -ForegroundColor Yellow

$sec = Read-Host -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
try   { $key = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }

$key = $key.Trim()
if ($key.Length -lt 10) {
  Write-Host "✗ 看起来不像有效 Key（长度 $($key.Length)），已中止，未写入任何文件。" -ForegroundColor Red
  exit 1
}

$content = @"
# 本地出刊密钥（本文件已被 .gitignore 忽略，不会入库）
LLM_API_KEY=$key
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
"@

$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($envFile, $content, $utf8NoBom)

Write-Host ""
Write-Host "✓ 已写入 $envFile" -ForegroundColor Green
Write-Host "  Key 长度：$($key.Length)，结尾：…$($key.Substring($key.Length - 4))"
Write-Host "  模型：deepseek-chat @ https://api.deepseek.com/v1"

# 立刻确认 git 不会跟踪它
Push-Location $root
git check-ignore -q $envFile
$ignored = ($LASTEXITCODE -eq 0)
$visible = (git status --short | Select-String -Pattern '\.env\.local')
Pop-Location
if ($ignored -and -not $visible) {
  Write-Host "  ✓ git 已忽略该文件（不会被提交、不会上传到 GitHub）" -ForegroundColor Green
} else {
  Write-Host "  ⚠️ 注意：git 似乎能看到这个文件，请检查 .gitignore" -ForegroundColor Red
}

Write-Host ""
Write-Host "下一步：运行  .\tools\run_issue_local.ps1   本地试跑一期（只改本地文件，不发布）" -ForegroundColor Cyan

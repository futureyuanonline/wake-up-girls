# 每周出刊看门狗 / Wake-up Girls
# 检查线上是否已发本周一期；没有则（有 token 时）自动触发 GitHub Actions，否则弹窗提醒。
# 用法：powershell -NoProfile -ExecutionPolicy Bypass -File D:\wake-up-girls\tools\watchdog_weekly.ps1
# 测试：加 -NoPopup
# Token：把 GitHub PAT（需 Actions: Read and write）写入 D:\wake-up-girls\.github_token（一行，勿提交）

param([switch]$NoPopup)

$ErrorActionPreference = 'Continue'
$Root      = 'D:\wake-up-girls'
$Site      = 'https://yuanxiuzhong.com/data/issues.js'
$Repo      = 'futureyuanonline/wake-up-girls'
$Workflow  = 'weekly-issue.yml'
$LogDir    = Join-Path $Root 'logs'
$Log       = Join-Path $LogDir 'watchdog.log'
$TokenFile = Join-Path $Root '.github_token'
$WorkflowUrl = 'https://github.com/' + $Repo + '/actions/workflows/' + $Workflow

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log([string]$msg) {
    $line = '{0}  {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -Path $Log -Value $line -Encoding UTF8
    Write-Host $line
}

function Notify([string]$title, [string]$msg) {
    if ($NoPopup) {
        Write-Log ('[测试模式] 弹窗 -> ' + $title + ' :: ' + $msg)
        return
    }
    try {
        $sh = New-Object -ComObject WScript.Shell
        $sh.Popup($msg, 60, $title, 64) | Out-Null
    } catch {
        Write-Log ('弹窗失败: ' + $_.Exception.Message)
    }
}

function Get-LiveJson {
    $resp = Invoke-WebRequest -Uri $Site -UseBasicParsing -TimeoutSec 30 -Headers @{ 'User-Agent' = 'Mozilla/5.0'; 'Cache-Control' = 'no-cache' }
    return $resp.Content
}

$today = Get-Date
$offset = ([int]$today.DayOfWeek + 6) % 7
$mon = $today.AddDays(-$offset)
$sun = $mon.AddDays(6)
$want = '{0} – {1}' -f $mon.ToString('yyyy.MM.dd'), $sun.ToString('yyyy.MM.dd')
Write-Log ('检查本周应为: ' + $want)

try {
    $html = Get-LiveJson
} catch {
    Write-Log ('抓取站点失败: ' + $_.Exception.Message)
    Notify '站点抓取失败' ('无法读取 ' + $Site + '，请检查网络或站点状态。')
    exit 1
}

$mp = [regex]::Match($html, '"period"\s*:\s*"([^"]+)"')
$mi = [regex]::Match($html, '"id"\s*:\s*"(\d{3})"')
$latest   = if ($mp.Success) { $mp.Groups[1].Value } else { '未知' }
$latestId = if ($mi.Success) { $mi.Groups[1].Value } else { '?' }
Write-Log ('线上最新: 第 ' + $latestId + ' 期（' + $latest + '）')

if ($latest -eq $want) {
    Write-Log 'OK: 本周已出刊，无需处理'
    exit 0
}

Write-Log 'WARN: 本周尚未出刊'

$dispatched = $false
if (Test-Path $TokenFile) {
    $token = (Get-Content $TokenFile -Raw).Trim()
    if ($token.Length -gt 10) {
        try {
            $headers = @{
                Authorization          = 'Bearer ' + $token
                Accept                 = 'application/vnd.github+json'
                'X-GitHub-Api-Version' = '2022-11-28'
                'User-Agent'           = 'wake-up-girls-watchdog'
            }
            $uri = 'https://api.github.com/repos/' + $Repo + '/actions/workflows/' + $Workflow + '/dispatches'
            Invoke-RestMethod -Method Post -Uri $uri -Headers $headers -Body '{"ref":"main"}' -TimeoutSec 30 | Out-Null
            Write-Log '已自动触发 GitHub Actions'
            $dispatched = $true
            Notify '已自动补发' ('第 ' + $latestId + ' 期仍是旧一期，已自动触发流水线，约 5 分钟后复查。')
        } catch {
            Write-Log ('自动触发失败: ' + $_.Exception.Message)
        }
    }
}

if (-not $dispatched) {
    Notify '本周还没出刊' ('线上最新是第 ' + $latestId + ' 期（' + $latest + '）。本周应为: ' + $want + '。请手动触发: ' + $WorkflowUrl)
    Write-Log '已弹窗提醒（未配置 token，无法自动触发）'
    exit 0
}

Start-Sleep -Seconds 240
try {
    $html2 = Get-LiveJson
    $mp2 = [regex]::Match($html2, '"period"\s*:\s*"([^"]+)"')
    $latest2 = if ($mp2.Success) { $mp2.Groups[1].Value } else { '未知' }
    if ($latest2 -eq $want) {
        Write-Log ('补发成功: ' + $latest2)
        Notify '出刊成功' ('本周一期已上线: ' + $latest2)
    } else {
        Write-Log ('补发后仍未更新（线上 ' + $latest2 + '）')
        Notify '补发后仍未见更新' ('已触发流水线，但线上仍是 ' + $latest2 + '。请检查 Actions 与 Cloudflare 部署。')
    }
} catch {
    Write-Log ('复查失败: ' + $_.Exception.Message)
}

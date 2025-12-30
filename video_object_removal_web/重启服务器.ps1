# 重启Flask服务器脚本

Write-Host "正在停止旧的Python进程..." -ForegroundColor Yellow

# 查找并停止占用5000端口的进程
$port = 5000
$processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

foreach ($pid in $processes) {
    if ($pid) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "已停止进程 PID: $pid" -ForegroundColor Green
        } catch {
            Write-Host "无法停止进程 PID: $pid" -ForegroundColor Red
        }
    }
}

Start-Sleep -Seconds 2

Write-Host "`n正在启动Flask服务器..." -ForegroundColor Cyan
Write-Host "访问地址: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务器`n" -ForegroundColor Yellow

# 切换到脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# 启动Flask服务器
python app.py






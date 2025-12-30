# 启动视频物体删除 Web 应用

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动视频物体删除 Web 应用" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到脚本目录
Set-Location $PSScriptRoot

# 检查依赖
Write-Host "检查依赖..." -ForegroundColor Yellow
$flaskInstalled = pip show Flask 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "正在安装依赖..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host ""
}

Write-Host "启动服务器..." -ForegroundColor Green
Write-Host "访问 http://127.0.0.1:5000 使用前端界面" -ForegroundColor Cyan
Write-Host ""

python app.py









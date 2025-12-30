# 安装 GroundingDINO
# 使用方法：.\install_groundingdino.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装 GroundingDINO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 GroundingDINO 目录是否存在
if (-not (Test-Path "GroundingDINO")) {
    Write-Host "错误: GroundingDINO 目录不存在" -ForegroundColor Red
    Write-Host "请先运行: git clone https://github.com/IDEA-Research/GroundingDINO.git" -ForegroundColor Yellow
    exit 1
}

Write-Host "步骤1: 安装依赖包..." -ForegroundColor Yellow
Set-Location GroundingDINO

# 安装 requirements.txt 中的依赖
if (Test-Path "requirements.txt") {
    Write-Host "安装 requirements.txt 中的依赖..." -ForegroundColor Green
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "警告: 部分依赖安装可能失败，继续安装..." -ForegroundColor Yellow
    }
} else {
    Write-Host "警告: requirements.txt 不存在" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "步骤2: 安装 GroundingDINO 包..." -ForegroundColor Yellow
# 安装 GroundingDINO 包（可编辑模式）
pip install -e .
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: GroundingDINO 安装失败" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "步骤3: 下载模型权重..." -ForegroundColor Yellow

# 创建 weights 目录（如果不存在）
$weightsDir = "weights"
if (-not (Test-Path $weightsDir)) {
    New-Item -ItemType Directory -Path $weightsDir | Out-Null
    Write-Host "创建 weights 目录: $weightsDir" -ForegroundColor Green
}

# 模型文件路径
$modelFile = Join-Path $weightsDir "groundingdino_swinb_cogcoor.pth"
$modelUrl = "https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swinb_cogcoor.pth"

# 检查模型是否已存在
if (Test-Path $modelFile) {
    Write-Host "模型文件已存在: $modelFile" -ForegroundColor Green
    Write-Host "跳过下载" -ForegroundColor Yellow
} else {
    Write-Host "下载模型文件..." -ForegroundColor Green
    Write-Host "URL: $modelUrl" -ForegroundColor Cyan
    Write-Host "保存到: $modelFile" -ForegroundColor Cyan
    
    try {
        # 使用 PowerShell 下载文件
        Invoke-WebRequest -Uri $modelUrl -OutFile $modelFile -UseBasicParsing
        
        if (Test-Path $modelFile) {
            $fileSize = (Get-Item $modelFile).Length / 1MB
            Write-Host "✓ 模型下载成功！文件大小: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
        } else {
            Write-Host "错误: 模型文件下载失败" -ForegroundColor Red
            Write-Host "请手动下载: $modelUrl" -ForegroundColor Yellow
            Write-Host "保存到: $modelFile" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "错误: 下载失败: $_" -ForegroundColor Red
        Write-Host "请手动下载: $modelUrl" -ForegroundColor Yellow
        Write-Host "保存到: $modelFile" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "验证安装:" -ForegroundColor Yellow
Write-Host "  python -c `"from groundingdino.util.inference import load_model; print('GroundingDINO 安装成功！')`"" -ForegroundColor Cyan
Write-Host ""





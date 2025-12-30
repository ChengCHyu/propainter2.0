@echo off
REM 安装 GroundingDINO
REM 使用方法：install_groundingdino.bat

echo ========================================
echo 安装 GroundingDINO
echo ========================================
echo.

REM 检查 GroundingDINO 目录是否存在
if not exist "GroundingDINO" (
    echo 错误: GroundingDINO 目录不存在
    echo 请先运行: git clone https://github.com/IDEA-Research/GroundingDINO.git
    pause
    exit /b 1
)

echo 步骤1: 安装依赖包...
cd GroundingDINO

REM 安装 requirements.txt 中的依赖
if exist "requirements.txt" (
    echo 安装 requirements.txt 中的依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 警告: 部分依赖安装可能失败，继续安装...
    )
) else (
    echo 警告: requirements.txt 不存在
)

echo.
echo 步骤2: 安装 GroundingDINO 包...
REM 安装 GroundingDINO 包（可编辑模式）
pip install -e .
if errorlevel 1 (
    echo 错误: GroundingDINO 安装失败
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo 步骤3: 下载模型权重...

REM 创建 weights 目录（如果不存在）
if not exist "weights" (
    mkdir weights
    echo 创建 weights 目录
)

REM 模型文件路径
set MODEL_FILE=weights\groundingdino_swinb_cogcoor.pth
set MODEL_URL=https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swinb_cogcoor.pth

REM 检查模型是否已存在
if exist "%MODEL_FILE%" (
    echo 模型文件已存在: %MODEL_FILE%
    echo 跳过下载
) else (
    echo 下载模型文件...
    echo URL: %MODEL_URL%
    echo 保存到: %MODEL_FILE%
    echo.
    echo 注意: Windows 批处理文件下载可能不稳定
    echo 如果下载失败，请手动下载:
    echo   %MODEL_URL%
    echo 保存到: %MODEL_FILE%
    echo.
    echo 或者使用 PowerShell 脚本: .\install_groundingdino.ps1
    echo.
    
    REM 尝试使用 PowerShell 下载
    powershell -Command "try { Invoke-WebRequest -Uri '%MODEL_URL%' -OutFile '%MODEL_FILE%' -UseBasicParsing; Write-Host '下载成功' } catch { Write-Host '下载失败，请手动下载' }"
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 验证安装:
echo   python -c "from groundingdino.util.inference import load_model; print('GroundingDINO 安装成功！')"
echo.
pause





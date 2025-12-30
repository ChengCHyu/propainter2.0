@echo off
chcp 65001 >nul
echo ========================================
echo 在E盘创建虚拟环境并安装PyTorch
echo ========================================
echo.

set VENV_PATH=E:\ProPainter_venv

echo 步骤1: 检查E盘空间...
if not exist E:\ (
    echo 错误: E盘不存在！
    pause
    exit /b 1
)

echo.
echo 步骤2: 创建虚拟环境到 E:\ProPainter_venv
echo.
python -m venv %VENV_PATH%

if %ERRORLEVEL% NEQ 0 (
    echo 错误: 创建虚拟环境失败！
    pause
    exit /b 1
)

echo.
echo 虚拟环境创建成功！
echo.
echo 步骤3: 激活虚拟环境并安装PyTorch
echo.

call %VENV_PATH%\Scripts\activate.bat

echo.
echo 当前Python路径: 
where python

echo.
echo 步骤4: 升级pip...
python -m pip install --upgrade pip

echo.
echo 步骤5: 卸载旧版PyTorch（如果存在）...
pip uninstall torch torchvision torchaudio -y

echo.
echo 步骤6: 安装CUDA版本的PyTorch...
echo 这可能需要几分钟，请耐心等待...
echo.
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo ========================================
echo 步骤7: 验证安装
echo ========================================
echo.
python -c "import torch; print('PyTorch版本:', torch.__version__); print('CUDA可用:', torch.cuda.is_available()); print('CUDA版本:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 虚拟环境位置: %VENV_PATH%
echo.
echo 以后使用项目时，需要先激活虚拟环境：
echo   %VENV_PATH%\Scripts\activate.bat
echo.
echo 或者运行项目提供的启动脚本（会自动激活）
echo.
pause








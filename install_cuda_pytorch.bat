@echo off
chcp 65001 >nul
echo ========================================
echo 安装CUDA版本的PyTorch
echo ========================================
echo.
echo 检测到你的CUDA版本: 12.6
echo 将安装支持CUDA 12.1的PyTorch（向后兼容12.6）
echo.
echo 步骤1: 卸载CPU版本的PyTorch...
echo.
pip uninstall torch torchvision torchaudio -y

echo.
echo ========================================
echo 步骤2: 安装CUDA 12.1版本的PyTorch
echo ========================================
echo.
echo 这可能需要几分钟，请耐心等待...
echo.
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo ========================================
echo 步骤3: 验证安装
echo ========================================
echo.
python -c "import torch; print('PyTorch版本:', torch.__version__); print('CUDA可用:', torch.cuda.is_available()); print('CUDA版本:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"

echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo 安装完成！
    echo.
    echo 如果显示 "CUDA可用: True"，说明安装成功
    echo 现在可以运行项目使用GPU加速了
) else (
    echo 安装可能有问题，请检查上面的错误信息
)
echo ========================================
echo.
pause








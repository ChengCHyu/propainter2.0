# 安装CUDA版本的PyTorch

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装CUDA版本的PyTorch" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "检测到你的CUDA版本: 12.6" -ForegroundColor Yellow
Write-Host "将安装支持CUDA 12.1的PyTorch（向后兼容12.6）" -ForegroundColor Yellow
Write-Host ""

Write-Host "步骤1: 卸载CPU版本的PyTorch..." -ForegroundColor Green
Write-Host ""
pip uninstall torch torchvision torchaudio -y

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "步骤2: 安装CUDA 12.1版本的PyTorch" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "这可能需要几分钟，请耐心等待..." -ForegroundColor Yellow
Write-Host ""
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "步骤3: 验证安装" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
python -c "import torch; print('PyTorch版本:', torch.__version__); print('CUDA可用:', torch.cuda.is_available()); print('CUDA版本:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装完成！" -ForegroundColor Green
Write-Host "如果显示 'CUDA可用: True'，说明安装成功" -ForegroundColor Green
Write-Host "现在可以运行项目使用GPU加速了" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan








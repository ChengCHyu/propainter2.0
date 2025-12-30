# PowerShell脚本：安装成员B所需的所有依赖
# 使用方法: .\install_all_deps.ps1

Write-Host "开始安装成员B所需的所有依赖..." -ForegroundColor Green

# 核心依赖
Write-Host "`n[1/6] 安装核心依赖..." -ForegroundColor Yellow
pip install opencv-python numpy pillow scipy

# 视频处理
Write-Host "`n[2/6] 安装视频处理依赖..." -ForegroundColor Yellow
pip install imageio imageio-ffmpeg

# 进度条和工具
Write-Host "`n[3/6] 安装工具依赖..." -ForegroundColor Yellow
pip install tqdm

# PyTorch相关
Write-Host "`n[4/6] 安装PyTorch相关..." -ForegroundColor Yellow
pip install torch torchvision

# Track-Anything相关依赖
Write-Host "`n[5/6] 安装Track-Anything依赖..." -ForegroundColor Yellow
pip install omegaconf
pip install addict
pip install einops
pip install pyyaml

# SAM相关
Write-Host "`n[6/6] 安装SAM相关..." -ForegroundColor Yellow
pip install segment-anything

Write-Host "`n✓ 所有依赖安装完成！" -ForegroundColor Green
Write-Host "`n验证安装..." -ForegroundColor Yellow

# 验证关键模块
python -c "import cv2; print('✓ cv2 (OpenCV)')" 2>$null
python -c "import numpy; print('✓ numpy')" 2>$null
python -c "import torch; print('✓ torch')" 2>$null
python -c "import omegaconf; print('✓ omegaconf')" 2>$null
python -c "from segment_anything import sam_model_registry; print('✓ segment-anything')" 2>$null

Write-Host "`n可以开始使用了！" -ForegroundColor Green



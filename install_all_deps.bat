@echo off
REM Windows批处理脚本：安装成员B所需的所有依赖
REM 使用方法: install_all_deps.bat

echo 开始安装成员B所需的所有依赖...

echo.
echo [1/6] 安装核心依赖...
pip install opencv-python numpy pillow scipy

echo.
echo [2/6] 安装视频处理依赖...
pip install imageio imageio-ffmpeg

echo.
echo [3/6] 安装工具依赖...
pip install tqdm

echo.
echo [4/6] 安装PyTorch相关...
pip install torch torchvision

echo.
echo [5/6] 安装Track-Anything依赖...
pip install omegaconf
pip install addict
pip install einops
pip install pyyaml

echo.
echo [6/6] 安装SAM相关...
pip install segment-anything

echo.
echo ✓ 所有依赖安装完成！
echo.
echo 验证安装...
python -c "import cv2; print('✓ cv2 (OpenCV)')"
python -c "import numpy; print('✓ numpy')"
python -c "import torch; print('✓ torch')"
python -c "import omegaconf; print('✓ omegaconf')"

echo.
echo 可以开始使用了！
pause



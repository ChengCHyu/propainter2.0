# 依赖安装指南

## 🐛 错误：ModuleNotFoundError: No module named 'cv2'

这个错误表示缺少 `opencv-python` 模块。

## ✅ 解决方法

### 方法1：安装所有依赖（推荐）

```powershell
# 安装项目所需的所有依赖
pip install -r requirements.txt

# 如果requirements.txt中没有cv2，单独安装
pip install opencv-python
```

### 方法2：只安装必需的模块

```powershell
# 安装OpenCV
pip install opencv-python

# 安装其他必需的模块
pip install numpy pillow imageio imageio-ffmpeg tqdm torch torchvision
```

### 方法3：使用conda（如果使用conda环境）

```powershell
conda install opencv-python
```

## 📦 完整依赖列表

成员B模块需要以下依赖：

```powershell
# 核心依赖
pip install opencv-python          # cv2模块
pip install numpy                  # 数值计算
pip install pillow                 # 图像处理
pip install scipy                  # 科学计算

# 视频处理
pip install imageio                # 视频/图像IO
pip install imageio-ffmpeg         # 视频编解码

# 工具
pip install tqdm                   # 进度条

# PyTorch相关（如果使用GPU）
pip install torch torchvision

# Track-Anything相关（重要！）
pip install omegaconf              # 配置管理（必需）
pip install addict                 # 字典工具
pip install einops                 # 张量操作
pip install pyyaml                 # YAML解析

# SAM相关
pip install segment-anything

# 其他（可选）
pip install matplotlib             # 可视化
```

### 🚀 一键安装（推荐）

**Windows PowerShell:**
```powershell
.\install_all_deps.ps1
```

**Windows CMD:**
```cmd
install_all_deps.bat
```

**手动安装（如果脚本不可用）:**
```powershell
pip install opencv-python numpy pillow scipy imageio imageio-ffmpeg tqdm torch torchvision omegaconf addict einops pyyaml segment-anything
```

## 🔍 检查安装

安装后检查：

```powershell
python -c "import cv2; print('OpenCV版本:', cv2.__version__)"
python -c "import numpy; print('NumPy版本:', numpy.__version__)"
python -c "import torch; print('PyTorch版本:', torch.__version__)"
```

## 🚀 快速安装脚本

创建 `install_deps.ps1`：

```powershell
# 安装所有依赖
pip install opencv-python numpy pillow imageio imageio-ffmpeg tqdm
pip install torch torchvision
pip install segment-anything
pip install scipy

Write-Host "✓ 依赖安装完成！"
```

然后运行：
```powershell
.\install_deps.ps1
```

## ⚠️ 常见问题

### Q1: pip install 很慢

**A:** 使用国内镜像源：
```powershell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple opencv-python
```

### Q2: 权限错误

**A:** 使用管理员权限运行PowerShell，或添加 `--user`：
```powershell
pip install --user opencv-python
```

### Q3: 版本冲突

**A:** 使用虚拟环境：
```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（PowerShell）
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install opencv-python
```

## 📝 验证安装

运行测试：

```powershell
python -c "from member_b_track_anything import MemberBTrackAnything; print('✓ 模块导入成功')"
```

如果成功，说明所有依赖都已正确安装！


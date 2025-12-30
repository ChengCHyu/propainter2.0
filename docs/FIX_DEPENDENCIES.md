# 🔧 快速修复依赖问题

## ❌ 当前错误

```
ModuleNotFoundError: No module named 'omegaconf'
```

## ✅ 快速解决方法

### 方法1：一键安装脚本（最简单）

**Windows PowerShell:**
```powershell
.\install_all_deps.ps1
```

**Windows CMD:**
```cmd
install_all_deps.bat
```

### 方法2：手动安装缺失的模块

```powershell
# 安装缺失的模块
pip install omegaconf

# 如果还有其他缺失，安装完整依赖
pip install opencv-python numpy pillow scipy imageio imageio-ffmpeg tqdm torch torchvision omegaconf addict einops pyyaml segment-anything
```

### 方法3：使用国内镜像（如果下载慢）

```powershell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple omegaconf
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple opencv-python numpy pillow scipy imageio imageio-ffmpeg tqdm torch torchvision addict einops pyyaml segment-anything
```

## 📋 成员B必需的依赖清单

### 核心模块
- ✅ `opencv-python` (cv2)
- ✅ `numpy`
- ✅ `pillow`
- ✅ `scipy`

### Track-Anything相关（重要！）
- ✅ `omegaconf` ⭐ **当前缺失**
- ✅ `addict`
- ✅ `einops`
- ✅ `pyyaml`

### 视频处理
- ✅ `imageio`
- ✅ `imageio-ffmpeg`

### PyTorch
- ✅ `torch`
- ✅ `torchvision`

### SAM
- ✅ `segment-anything`

### 工具
- ✅ `tqdm`

## 🔍 验证安装

安装后运行验证：

```powershell
python -c "import cv2; print('✓ cv2')"
python -c "import numpy; print('✓ numpy')"
python -c "import torch; print('✓ torch')"
python -c "import omegaconf; print('✓ omegaconf')"
python -c "from segment_anything import sam_model_registry; print('✓ segment-anything')"
```

## 🚀 完整安装命令（复制粘贴）

```powershell
pip install opencv-python numpy pillow scipy imageio imageio-ffmpeg tqdm torch torchvision omegaconf addict einops pyyaml segment-anything
```

## ⚠️ 如果还有错误

如果安装后还有其他 `ModuleNotFoundError`，请：

1. **查看错误信息**，找到缺失的模块名
2. **安装缺失的模块**：`pip install 模块名`
3. **或者运行完整安装**：`pip install -r requirements.txt`

## 💡 建议

**使用虚拟环境（推荐）：**

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（PowerShell）
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install opencv-python numpy pillow scipy imageio imageio-ffmpeg tqdm torch torchvision omegaconf addict einops pyyaml segment-anything
```

这样可以避免与其他项目的依赖冲突！


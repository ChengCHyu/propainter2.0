# 📥 模型下载指南

## ❌ 错误：找不到SAM模型文件

```
FileNotFoundError: [Errno 2] No such file or directory: 'weights/sam_vit_h_4b8939.pth'
```

## ✅ 解决方法

### 方法1：自动下载（推荐）

代码已更新，会自动下载缺失的模型。如果自动下载失败，使用以下方法：

### 方法2：使用下载脚本

```powershell
# 下载所有模型
python download_models.py --all

# 只下载SAM模型
python download_models.py --sam --sam_type vit_h

# 只下载CUTIE模型
python download_models.py --cutie
```

### 方法3：手动下载

#### SAM模型下载链接

- **vit_h (推荐，最大，最准确)**: 
  - URL: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
  - 大小: ~2.4GB
  - 保存到: `weights/sam_vit_h_4b8939.pth`

- **vit_l (中等)**:
  - URL: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
  - 大小: ~1.2GB
  - 保存到: `weights/sam_vit_l_0b3195.pth`

- **vit_b (最小，最快)**:
  - URL: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
  - 大小: ~375MB
  - 保存到: `weights/sam_vit_b_01ec64.pth`

#### CUTIE追踪器模型

- URL: https://github.com/sczhou/ProPainter/releases/download/v0.1.0/cutie-base-mega.pth
- 保存到: `weights/cutie-base-mega.pth`

### 方法4：使用浏览器下载

1. 打开下载链接（见上方）
2. 下载文件到 `weights/` 目录
3. 确保文件名正确

## 📋 完整模型列表

成员B需要的模型：

| 模型 | 文件 | 大小 | 必需 |
|------|------|------|------|
| SAM (vit_h) | `weights/sam_vit_h_4b8939.pth` | ~2.4GB | ✅ |
| CUTIE | `weights/cutie-base-mega.pth` | ~? | ✅ |

## 🚀 快速下载命令

### PowerShell

```powershell
# 创建weights目录
New-Item -ItemType Directory -Force -Path weights

# 下载SAM模型（使用PowerShell）
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth" -OutFile "weights/sam_vit_h_4b8939.pth"

# 下载CUTIE模型
Invoke-WebRequest -Uri "https://github.com/sczhou/ProPainter/releases/download/v0.1.0/cutie-base-mega.pth" -OutFile "weights/cutie-base-mega.pth"
```

### Python脚本（推荐）

```powershell
python download_models.py --all
```

## 🔍 验证下载

下载后检查文件：

```powershell
# 检查文件是否存在
Test-Path weights/sam_vit_h_4b8939.pth
Test-Path weights/cutie-base-mega.pth

# 或使用Python
python -c "import os; print('SAM:', os.path.exists('weights/sam_vit_h_4b8939.pth')); print('CUTIE:', os.path.exists('weights/cutie-base-mega.pth'))"
```

## ⚠️ 注意事项

1. **文件大小**：SAM vit_h模型约2.4GB，下载需要时间
2. **网络**：如果下载慢，可以使用代理或镜像
3. **磁盘空间**：确保有足够的磁盘空间（至少5GB）
4. **文件完整性**：下载后检查文件大小是否正确

## 💡 使用较小的模型（如果下载慢）

如果下载vit_h太慢，可以使用较小的模型：

```python
from member_b_track_anything import MemberBTrackAnything

# 使用vit_b（最小，375MB）
module = MemberBTrackAnything(
    sam_model_type='vit_b',  # 使用较小的模型
    sam_checkpoint='weights/sam_vit_b_01ec64.pth'
)
```

## 🎯 完整步骤

1. **创建weights目录**（如果不存在）
   ```powershell
   mkdir weights
   ```

2. **下载模型**
   ```powershell
   python download_models.py --all
   ```

3. **验证**
   ```powershell
   python -c "import os; print('SAM:', os.path.exists('weights/sam_vit_h_4b8939.pth'))"
   ```

4. **运行**
   ```powershell
   python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox "[[150, 150, 250, 250]]" --output results/test_masks
   ```


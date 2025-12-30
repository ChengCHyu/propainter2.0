# GPU配置说明

## 📋 当前GPU使用情况

本项目默认会自动检测并使用GPU（如果可用），但所有模块都支持通过参数指定设备。

## 🔧 如何强制使用GPU

### 方法1：通过环境变量（推荐）

在运行脚本前设置环境变量：

**Windows PowerShell:**
```powershell
$env:CUDA_VISIBLE_DEVICES = "0"  # 使用第0块GPU
python inference_propainter.py -i video.mp4 -m masks -o output
```

**Windows CMD:**
```cmd
set CUDA_VISIBLE_DEVICES=0
python inference_propainter.py -i video.mp4 -m masks -o output
```

### 方法2：修改代码中的设备设置

#### 1. ProPainter (inference_propainter.py)

当前代码使用 `get_device()` 自动检测，如果需要强制使用GPU，可以修改：

```python
# 在 inference_propainter.py 第179行附近
# 原代码：
device = get_device()

# 改为强制使用GPU：
device = torch.device("cuda:0")  # 或 "cuda:1" 使用第二块GPU
```

#### 2. Member B (member_b_track_anything.py)

在初始化时指定设备：

```python
from member_b.member_b_track_anything import MemberBTrackAnything

# 使用GPU
processor = MemberBTrackAnything(device='cuda:0')
```

#### 3. Web应用 (video_processor.py)

修改 `video_object_removal_web/video_processor.py`：

```python
# 在 VideoProcessor.__init__ 或 process 方法中
proc = self._get_processor()
# 如果 MemberBTrackAnything 支持设备参数，可以这样：
# proc = MemberBTrackAnything(device='cuda:0')
```

### 方法3：检查GPU是否可用

运行以下Python代码检查：

```python
import torch
print(f"CUDA可用: {torch.cuda.is_available()}")
print(f"CUDA版本: {torch.version.cuda}")
print(f"GPU数量: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"当前GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU内存: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
```

## 🚀 性能优化建议

### 1. 使用混合精度（FP16）

ProPainter支持FP16加速，在 `inference_propainter.py` 中：

```python
# 查找 use_half 参数
parser.add_argument('--use_half', action='store_true', help='Use half precision (FP16)')
```

运行时添加 `--use_half` 参数可以显著减少显存占用并加速。

### 2. 批处理大小

如果显存充足，可以增加批处理大小（在相关代码中查找 `batch_size` 参数）。

### 3. 多GPU支持

如果有多个GPU，可以：

1. **指定特定GPU**：
   ```python
   device = torch.device("cuda:1")  # 使用第二块GPU
   ```

2. **使用DataParallel**（需要修改代码）：
   ```python
   model = torch.nn.DataParallel(model, device_ids=[0, 1])
   ```

## ⚠️ 常见问题

### 问题1：CUDA out of memory

**解决方案：**
- 减小视频分辨率（使用 `--resize_ratio` 参数）
- 使用FP16（`--use_half`）
- 减小批处理大小
- 处理更短的视频片段

### 问题2：找不到GPU

**检查步骤：**
1. 确认已安装NVIDIA驱动
2. 确认已安装CUDA版本的PyTorch：
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```
3. 运行 `python -c "import torch; print(torch.cuda.is_available())"` 检查

### 问题3：GPU利用率低

**可能原因：**
- 视频处理是顺序的，无法完全并行化
- I/O瓶颈（读取视频/保存结果）
- 某些步骤（如SAM分割）可能主要在CPU上运行

## 📝 当前项目中的设备配置位置

1. **model/misc.py** (第65-76行): `get_device()` 函数
2. **inference_propainter.py** (第179行): ProPainter的设备设置
3. **member_b/member_b_track_anything.py** (第54-57行): Member B的设备设置
4. **video_object_removal_web/video_processor.py**: 通过MemberBTrackAnything初始化时传递device参数

## 🔍 验证GPU使用

运行处理时，可以通过以下方式验证GPU是否在使用：

1. **nvidia-smi** (在另一个终端窗口):
   ```bash
   nvidia-smi -l 1  # 每秒刷新一次
   ```

2. **Python代码**:
   ```python
   import torch
   x = torch.randn(1000, 1000).cuda()
   # 如果这行不报错，说明GPU可用
   ```

## 💡 推荐配置

对于大多数用户，推荐：

1. **单GPU系统**: 使用默认的 `cuda:0`
2. **多GPU系统**: 可以指定使用性能最好的GPU（通常是 `cuda:0`）
3. **显存不足**: 使用 `--use_half` 和 `--resize_ratio 0.5`


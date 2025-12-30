# 空间占用和GPU配置总结

## 📍 修复后的视频保存位置

### Web应用处理后的视频位置

**完整路径：**
```
video_object_removal_web/outputs/{视频名称}/inpainted/{视频名称}/inpaint_out.mp4
```

**示例：**
- 如果视频名为 `running_car.mp4`
- 输出路径为：`video_object_removal_web/outputs/running_car/inpainted/running_car/inpaint_out.mp4`

**在前端访问：**
- 前端会显示处理后的视频
- 也可以通过浏览器直接访问：`http://127.0.0.1:5000/api/video_output/{相对路径}`

### 命令行处理后的视频位置

如果使用 `complete_pipeline.py` 或 `inference_propainter.py`：
- 默认输出：`results/inpainted/{视频名称}/inpaint_out.mp4`
- 或指定的输出目录

## 💾 空间占用分析

### 当前空间占用情况

根据检查结果：

1. **weights目录** (模型文件): **~2.7 GB**
   - `sam_vit_h_4b8939.pth`: ~2.4 GB
   - `cutie-base-mega.pth`: ~200 MB
   - `recurrent_flow_completion.pth`: ~100 MB
   - `ProPainter.pth`: ~100 MB
   - **这些文件不能删除！**

2. **video_object_removal_web/outputs** (输出文件): **~2.73 MB**
   - 包含处理后的视频和掩码
   - **可以删除**（可以重新生成）

3. **video_object_removal_web/uploads** (上传的视频): **~2.81 MB**
   - 用户上传的原始视频
   - **可以删除**（可以重新上传）

4. **results目录** (测试结果): **较小**
   - 旧的测试结果
   - **可以删除**

5. **__pycache__目录** (Python缓存): **几MB**
   - Python编译缓存
   - **可以删除**（会自动重新生成）

### 如何释放空间

#### 方法1：使用清理脚本（推荐）

```powershell
powershell -ExecutionPolicy Bypass -File cleanup_space.ps1
```

然后选择要清理的内容：
- 选项1：清理输出文件（outputs）
- 选项2：清理上传文件（uploads）
- 选项3：清理结果文件（results）
- 选项4：清理Python缓存（__pycache__）
- 选项5：全部清理

#### 方法2：手动删除

**可以安全删除的目录：**
```powershell
# 删除输出文件
Remove-Item -Path "video_object_removal_web\outputs\*" -Recurse -Force

# 删除上传文件
Remove-Item -Path "video_object_removal_web\uploads\*" -Force

# 删除结果文件
Remove-Item -Path "results\*" -Recurse -Force

# 删除Python缓存
Get-ChildItem -Path "." -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```

**不能删除的目录：**
- ❌ `weights/` - 包含必需的模型文件
- ❌ `model/` - 代码文件
- ❌ `video_object_removal/` - 代码文件

#### 方法3：检查空间占用

运行空间检查脚本：
```powershell
powershell -ExecutionPolicy Bypass -File check_disk_space.ps1
```

## 🚀 GPU配置

### 当前GPU使用情况

项目默认会自动检测并使用GPU（如果可用）。所有模块都通过 `model/misc.py` 中的 `get_device()` 函数来获取设备。

### 如何确保使用GPU

#### 1. 检查GPU是否可用

运行以下Python代码：
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU name: {torch.cuda.get_device_name(0)}")
```

#### 2. 强制使用GPU

**方法A：修改代码（临时）**

在 `inference_propainter.py` 第179行：
```python
# 原代码：
device = get_device()

# 改为：
device = torch.device("cuda:0")  # 强制使用GPU 0
```

**方法B：通过环境变量**

```powershell
$env:CUDA_VISIBLE_DEVICES = "0"
python inference_propainter.py -i video.mp4 -m masks -o output
```

**方法C：在Web应用中指定设备**

修改 `video_object_removal_web/video_processor.py` 第50行：
```python
# 原代码：
self.processor = MemberBTrackAnything()

# 改为：
self.processor = MemberBTrackAnything(device='cuda:0')
```

#### 3. 性能优化

**使用FP16（半精度）加速：**

在运行 `inference_propainter.py` 时添加 `--use_half` 参数：
```bash
python inference_propainter.py -i video.mp4 -m masks -o output --use_half
```

**降低视频分辨率：**

如果显存不足，可以使用 `--resize_ratio` 参数：
```bash
python inference_propainter.py -i video.mp4 -m masks -o output --resize_ratio 0.5
```

### GPU相关问题排查

#### 问题1：CUDA out of memory

**解决方案：**
1. 使用 `--use_half` 启用FP16
2. 使用 `--resize_ratio 0.5` 降低分辨率
3. 处理更短的视频片段

#### 问题2：找不到GPU

**检查步骤：**
1. 确认已安装NVIDIA驱动
2. 确认已安装CUDA版本的PyTorch：
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```
3. 运行 `python -c "import torch; print(torch.cuda.is_available())"`

#### 问题3：GPU利用率低

这是正常的，因为：
- 视频处理是顺序的，无法完全并行化
- I/O操作（读取视频/保存结果）会占用时间
- 某些步骤（如SAM分割）可能主要在CPU上运行

## 📝 快速参考

### 检查空间占用
```powershell
powershell -ExecutionPolicy Bypass -File check_disk_space.ps1
```

### 清理空间
```powershell
powershell -ExecutionPolicy Bypass -File cleanup_space.ps1
```

### 检查GPU
```python
python -c "import torch; print('CUDA:', torch.cuda.is_available(), 'GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

### 查找输出视频
```powershell
Get-ChildItem -Path "video_object_removal_web\outputs" -Recurse -Filter "inpaint_out.mp4"
```

## ⚠️ 重要提示

1. **不要删除 `weights/` 目录** - 包含必需的模型文件
2. **定期清理 `outputs/` 和 `uploads/`** - 这些文件可以重新生成
3. **如果C盘空间不足**，考虑将项目移动到其他盘（如D盘）
4. **GPU不是必需的** - 项目可以在CPU上运行，但会慢很多


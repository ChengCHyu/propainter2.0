# 🔧 修复损坏的模型文件

## ❌ 错误信息

```
RuntimeError: PytorchStreamReader failed reading zip archive: failed finding central directory
```

## 🔍 错误原因

这个错误表示：
- **模型文件下载不完整**（下载中断）
- **模型文件损坏**
- **文件格式不正确**

## ✅ 解决方法

### 方法1：删除并重新下载（推荐）

```powershell
# 1. 删除损坏的文件
Remove-Item weights/sam_vit_h_4b8939.pth -ErrorAction SilentlyContinue

# 2. 重新下载
python download_models.py --sam --sam_type vit_h
```

### 方法2：检查文件完整性

```powershell
# 检查模型文件
python check_model.py
```

这会检查：
- 文件是否存在
- 文件大小是否正确（SAM vit_h应该约2.4GB）
- 文件是否可以正常加载

### 方法3：手动重新下载

#### 步骤1：删除损坏的文件

```powershell
# 删除SAM模型
Remove-Item weights/sam_vit_h_4b8939.pth -ErrorAction SilentlyContinue

# 或删除所有weights目录下的文件（谨慎！）
# Remove-Item weights/*.pth
```

#### 步骤2：重新下载

**使用下载脚本（推荐）：**
```powershell
python download_models.py --sam --sam_type vit_h
```

**或手动下载：**
```powershell
# 使用PowerShell下载
Invoke-WebRequest -Uri "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth" -OutFile "weights/sam_vit_h_4b8939.pth"
```

#### 步骤3：验证下载

```powershell
# 检查文件大小（应该约2.4GB = 2516582400字节）
(Get-Item weights/sam_vit_h_4b8939.pth).Length / 1MB

# 或使用检查脚本
python check_model.py
```

## 📋 完整修复步骤

### 步骤1：检查当前文件

```powershell
python check_model.py
```

### 步骤2：删除损坏的文件

```powershell
# 如果SAM模型损坏
Remove-Item weights/sam_vit_h_4b8939.pth

# 如果CUTIE模型损坏
Remove-Item weights/cutie-base-mega.pth
```

### 步骤3：重新下载

```powershell
# 下载所有模型
python download_models.py --all

# 或只下载SAM
python download_models.py --sam --sam_type vit_h
```

### 步骤4：验证

```powershell
python check_model.py
```

### 步骤5：测试运行

```powershell
python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox "[[150, 150, 250, 250]]" --output results/test_masks
```

## 🔍 文件大小参考

| 模型 | 文件 | 预期大小 |
|------|------|----------|
| SAM vit_h | `sam_vit_h_4b8939.pth` | ~2.4GB (2516582400字节) |
| SAM vit_l | `sam_vit_l_0b3195.pth` | ~1.2GB |
| SAM vit_b | `sam_vit_b_01ec64.pth` | ~375MB |
| CUTIE | `cutie-base-mega.pth` | 根据实际 |

## 💡 预防措施

1. **使用稳定的网络**：确保下载过程中网络稳定
2. **使用下载脚本**：`download_models.py` 有进度显示和错误处理
3. **验证下载**：下载后运行 `check_model.py` 验证
4. **使用较小的模型**：如果网络不稳定，使用 `vit_b`（375MB）

## 🚀 快速修复命令（复制粘贴）

```powershell
# 删除损坏的文件
Remove-Item weights/sam_vit_h_4b8939.pth -ErrorAction SilentlyContinue

# 重新下载
python download_models.py --sam --sam_type vit_h

# 验证
python check_model.py
```

## ⚠️ 如果下载仍然失败

### 使用较小的模型

如果下载vit_h（2.4GB）总是失败，可以使用较小的模型：

```python
from member_b_track_anything import MemberBTrackAnything

# 使用vit_b（375MB，更快）
module = MemberBTrackAnything(
    sam_model_type='vit_b',
    sam_checkpoint='weights/sam_vit_b_01ec64.pth'
)
```

下载vit_b：
```powershell
python download_models.py --sam --sam_type vit_b
```

### 使用浏览器下载

如果命令行下载失败：
1. 打开浏览器
2. 访问: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
3. 下载到 `weights/` 目录
4. 确保文件名正确

## 📝 验证文件完整性

```powershell
# 检查文件大小
$file = Get-Item weights/sam_vit_h_4b8939.pth
Write-Host "文件大小: $([math]::Round($file.Length / 1MB, 2)) MB"

# 应该显示约 2400 MB
```


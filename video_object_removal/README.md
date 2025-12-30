# 视频物体移除项目

基于ProPainter的视频物体移除系统，支持从视频中自动识别和移除指定物体。

**注意**：本项目是完全独立的，不依赖父目录的任何文件。

## 📋 项目概述

本项目实现了从文本描述到视频物体移除的完整流程：

```
文本输入 → 边界框定位 → 掩码生成 → 视频修复 → 最终视频
    ↓           ↓            ↓           ↓           ↓
  成员A      成员A        成员B       成员C       输出
```

### 模块说明

- **成员A**：文本定位模块（使用GroundingDINO）
  - 输入：文本描述（如"删除视频中的汽车"）
  - 输出：边界框列表 `[[x1, y1, x2, y2], ...]`

- **成员B**：分割与追踪模块（使用SAM + CUTIE）
  - 输入：视频 + 边界框
  - 输出：逐帧掩码序列

- **成员C**：视频修复模块（使用ProPainter）
  - 输入：视频 + 掩码
  - 输出：修复后的视频

## 📁 项目结构

```
video_object_removal/
├── src/
│   ├── member_a/          # 成员A：文本定位模块
│   │   ├── __init__.py
│   │   └── text_to_bbox.py
│   │
│   ├── member_b/          # 成员B：分割与追踪模块
│   │   ├── __init__.py
│   │   ├── segment_track.py    # 核心模块
│   │   ├── api.py              # API接口
│   │   └── main.py             # 命令行入口
│   │
│   ├── tools/             # 工具脚本
│   │   ├── find_bbox_tool.py   # 边界框定位工具
│   │   └── debug_mask.py       # 调试工具
│   │
│   ├── dependencies/      # 依赖模块（从ProPainter提取）
│   │   ├── tools/         # Track-Anything工具
│   │   ├── tracker/       # CUTIE追踪器
│   │   └── utils.py       # 工具函数
│   │
│   └── pipeline_end_to_end.py  # 端到端流程
│
├── examples/              # 示例脚本
│   └── test_member_b.py
│
├── requirements.txt       # 依赖列表
└── README.md             # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 或手动安装核心依赖
pip install opencv-python numpy pillow scipy imageio imageio-ffmpeg tqdm torch torchvision omegaconf segment-anything
```

### 2. 下载模型

模型文件会自动下载（如果不存在），或手动下载到 `weights/` 目录：

- **SAM模型**：`weights/sam_vit_h_4b8939.pth`
  - 下载地址：https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
  
- **CUTIE追踪器**：`weights/cutie-base-mega.pth`
  - 下载地址：https://github.com/sczhou/ProPainter/releases/download/v0.1.0/cutie-base-mega.pth

### 3. 使用示例

#### 方式1：Python代码

```python
import sys
import os

# 添加项目路径
sys.path.insert(0, 'src')

from member_b.segment_track import MemberBTrackAnything

# 初始化模块
module = MemberBTrackAnything()

# 处理视频
bboxes = [[180, 60, 285, 181]]  # 边界框 [x1, y1, x2, y2]
mask_path, masks = module.process_video(
    video_path='path/to/video',
    bboxes=bboxes
)

print(f"掩码保存在: {mask_path}")
```

#### 方式2：命令行

```bash
# 在 video_object_removal 目录下运行
python -m src.member_b.main \
    --video path/to/video \
    --bbox "[[180,60,285,181]]" \
    --output results/masks
```

## 📖 详细使用指南

### 成员A：文本定位

```python
from member_a.text_to_bbox import TextToBBox

module = TextToBBox()
bboxes = module.process_video_first_frame(
    video_path='video.mp4',
    text_prompt='car'  # 或 "删除视频中的汽车"
)
```

**注意**：需要安装GroundingDINO（当前为框架，需要实现）

### 成员B：分割与追踪

#### Python使用

```python
from member_b.segment_track import MemberBTrackAnything

module = MemberBTrackAnything()
mask_path, masks = module.process_video(
    video_path='video.mp4',
    bboxes=[[x1, y1, x2, y2]]  # 边界框列表
)
```

#### 命令行使用

```bash
# 基本用法
python -m src.member_b.main \
    --video video.mp4 \
    --bbox "[[x1,y1,x2,y2]]" \
    --output results/masks

# 使用JSON文件
python -m src.member_b.main \
    --video video.mp4 \
    --bbox bboxes.json \
    --output results/masks
```

#### 边界框格式

边界框格式：`[x1, y1, x2, y2]`
- `x1, y1`：左上角坐标
- `x2, y2`：右下角坐标
- 坐标单位：像素

示例：
```json
[[180, 60, 285, 181]]  # 单个物体
[[180, 60, 285, 181], [300, 100, 400, 200]]  # 多个物体
```

### 工具脚本

#### 1. 边界框定位工具

交互式选择边界框：

```bash
python src/tools/find_bbox_tool.py \
    --image path/to/first_frame.jpg \
    --interactive
```

可视化现有边界框：

```bash
python src/tools/find_bbox_tool.py \
    --image path/to/first_frame.jpg \
    --bbox "[180,60,285,181]"
```

#### 2. 调试工具

逐步调试掩码生成过程：

```bash
python src/tools/debug_mask.py \
    --video path/to/video \
    --bbox "[180,60,285,181]" \
    --output debug_output
```

输出文件：
- `debug_output/00_first_frame.jpg` - 原始第一帧
- `debug_output/01_bbox_on_frame.jpg` - 边界框可视化
- `debug_output/02_sam_mask.png` - SAM分割结果（**关键检查点**）
- `debug_output/03_combined_mask.png` - 组合掩码
- `debug_output/04_tracked_mask_frame0.png` - 追踪第一帧结果

### 成员C：视频修复

使用ProPainter修复视频（需要ProPainter项目）：

```bash
python inference_propainter.py \
    -i path/to/video \
    -m results/masks \
    -o results/inpainted
```

## 📥 输入输出格式

### 输入

1. **视频路径**
   - 视频文件：`video.mp4`, `video.avi` 等
   - 或帧文件夹：包含 `00000.jpg`, `00001.jpg` 等

2. **边界框**
   - 格式：`[[x1, y1, x2, y2], ...]`
   - JSON文件或Python列表

### 输出

1. **掩码文件夹**
   ```
   results/masks/
   ├── 00000.png    # 第0帧掩码
   ├── 00001.png    # 第1帧掩码
   ├── ...
   └── mask_video.mp4  # 掩码视频（可视化）
   ```

2. **掩码格式**
   - PNG图像，单通道
   - 0 = 背景（保留）
   - 255 = 前景（要删除）

## 🔧 配置说明

### 设备配置

默认自动检测GPU/CPU，也可手动指定：

```python
module = MemberBTrackAnything(device='cuda:0')  # 或 'cpu'
```

### 模型路径

默认模型路径：
- SAM：`weights/sam_vit_h_4b8939.pth`
- CUTIE：`weights/cutie-base-mega.pth`

自定义路径：

```python
module = MemberBTrackAnything(
    sam_checkpoint='path/to/sam.pth',
    tracker_checkpoint='path/to/cutie.pth'
)
```

## 🐛 常见问题

### 问题1：掩码全黑

**原因**：边界框位置不准确或SAM分割失败

**解决方法**：
1. 使用 `find_bbox_tool.py` 重新确定边界框
2. 使用 `debug_mask.py` 检查SAM分割结果
3. 检查边界框是否包含目标物体

### 问题2：ModuleNotFoundError

**解决方法**：
```bash
pip install -r requirements.txt
```

### 问题3：模型文件不存在

**解决方法**：模型会自动下载，或手动下载到 `weights/` 目录

### 问题4：追踪失败

**解决方法**：
- 检查第一帧掩码质量
- 尝试使用更准确的边界框
- 对于长视频，考虑在中间帧重新初始化

## 📝 完整流程示例

### Python代码

```python
# 步骤1：成员A - 文本→边界框（需要实现GroundingDINO）
from member_a.text_to_bbox import TextToBBox
module_a = TextToBBox()
bboxes = module_a.process_video_first_frame(
    video_path='path/to/video',
    text_prompt='car'
)

# 步骤2：成员B - 边界框→掩码
from member_b.segment_track import MemberBTrackAnything
module_b = MemberBTrackAnything()
mask_path, masks = module_b.process_video(
    video_path='path/to/video',
    bboxes=bboxes
)

# 步骤3：成员C - 掩码→修复视频（需要ProPainter）
# import subprocess
# subprocess.run([
#     'python', 'inference_propainter.py',
#     '-i', 'path/to/video',
#     '-m', mask_path,
#     '-o', 'results/inpainted'
# ])
```

### 命令行

```bash
# 步骤1：确定边界框（交互式）
python src/tools/find_bbox_tool.py \
    --image path/to/first_frame.jpg \
    --interactive

# 步骤2：生成掩码
python -m src.member_b.main \
    --video path/to/video \
    --bbox "[[180,60,285,181]]" \
    --output results/masks

# 步骤3：修复视频（需要ProPainter）
# python inference_propainter.py \
#     -i path/to/video \
#     -m results/masks \
#     -o results/inpainted
```

## 🔗 相关链接

- ProPainter项目：https://github.com/sczhou/ProPainter
- SAM (Segment Anything)：https://github.com/facebookresearch/segment-anything
- CUTIE追踪器：https://github.com/hkchengrex/Cutie
- GroundingDINO：https://github.com/IDEA-Research/GroundingDINO

## 📄 许可证

本项目基于ProPainter，请参考原始项目的许可证。

## 🙏 致谢

- ProPainter：视频修复模型
- Track-Anything：视频追踪框架
- SAM：分割模型
- CUTIE：视频对象分割追踪器

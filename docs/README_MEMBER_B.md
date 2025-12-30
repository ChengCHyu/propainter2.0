# 成员B：分割与追踪模块 - 完整使用指南

## 🎯 你的任务

**输入**：视频 + 边界框（来自成员A）  
**输出**：掩码序列（给成员C）  
**功能**：将边界框转换为像素级掩码，并在整个视频中追踪

## 🔄 完整流程

```
语音输入（成员D）
    ↓ "删除视频中的汽车"
文本（成员D）
    ↓
边界框 [[x1,y1,x2,y2]]（成员A - GroundingDINO）
    ↓ ⭐ 你的输入
掩码序列（成员B - SAM + CUTIE）⭐ 你负责
    ↓ ⭐ 你的输出
修复视频（成员C - ProPainter）
```

## ⚡ 快速开始（3步）

### 步骤1：准备输入

```python
# 来自成员A的边界框
video_path = 'inputs/object_removal/bmx-trees'
bboxes = [[150, 150, 250, 250]]  # [x1, y1, x2, y2]
```

### 步骤2：运行成员B

```python
from member_b_track_anything import MemberBTrackAnything

module = MemberBTrackAnything()
mask_path, masks = module.process_video(video_path, bboxes)
```

### 步骤3：输出给成员C

```bash
python inference_propainter.py -i video_path -m mask_path -o results/inpainted
```

## 📥 输入格式

### 输入1：视频路径
- 视频文件：`video.mp4`
- 或帧文件夹：`frames/`（包含 `00000.jpg`, `00001.jpg` 等）

### 输入2：边界框（来自成员A）
```python
# Python格式
bboxes = [[x1, y1, x2, y2], [x1, y1, x2, y2]]

# JSON格式
[
    [100, 100, 200, 200],
    [300, 300, 400, 400]
]
```

## 📤 输出格式

### 输出：掩码文件夹
```
results/member_b_masks/video_name/
├── 00000.png    # 第0帧掩码
├── 00001.png    # 第1帧掩码
├── ...
└── mask_video.mp4  # 可视化视频
```

**掩码说明**：
- PNG图像，单通道
- `0` = 背景（保留）
- `1, 2, 3...` = 不同物体（删除）

## 💻 使用方法

### 方法1：Python代码（推荐）

```python
from member_b_track_anything import MemberBTrackAnything

# 初始化
module = MemberBTrackAnything()

# 处理
mask_path, masks = module.process_video(
    video_path='inputs/object_removal/bmx-trees',
    bboxes=[[150, 150, 250, 250]]
)

print(f"掩码保存在: {mask_path}")
print(f"共 {len(masks)} 个掩码帧")
```

### 方法2：命令行

**Linux/Mac:**
```bash
# 准备边界框文件
echo '[[150, 150, 250, 250]]' > bboxes.json

# 运行
python member_b_track_anything.py \
    --video inputs/object_removal/bmx-trees \
    --bbox bboxes.json \
    --output results/masks
```

**Windows PowerShell:**
```powershell
# 一行命令（推荐）
python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox "[[150, 150, 250, 250]]" --output results/masks

# 或使用反引号继续行
python member_b_track_anything.py `
    --video inputs/object_removal/bmx-trees `
    --bbox "[[150, 150, 250, 250]]" `
    --output results/masks
```

**Windows CMD:**
```cmd
python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox "[[150, 150, 250, 250]]" --output results/masks
```

### 方法3：API接口

```python
from member_b_api import MemberBAPI

api = MemberBAPI()
result = api.process(
    video_path='inputs/object_removal/bmx-trees',
    bboxes=[[150, 150, 250, 250]]
)

print(f"状态: {result['status']}")
print(f"掩码路径: {result['output_path']}")
```

### 方法4：端到端流程（包含ProPainter）

```python
from pipeline_end_to_end import EndToEndPipeline

pipeline = EndToEndPipeline()
result = pipeline.process(
    video_path='inputs/object_removal/bmx-trees',
    bboxes=[[150, 150, 250, 250]],
    output_dir='results/pipeline'
)

print(f"掩码: {result['mask_path']}")
print(f"修复视频: {result['inpainted_video_path']}")
```

## 🔗 与团队成员的接口

### 接收成员A的输出

成员A提供：
```python
{
    "video_path": "inputs/object_removal/bmx-trees",
    "bboxes": [[100, 100, 200, 200]]
}
```

### 输出给成员C

成员B输出：
```python
{
    "mask_path": "results/member_b_masks/video_name",
    "mask_count": 80,
    "status": "success"
}
```

成员C使用：
```bash
python inference_propainter.py \
    -i inputs/object_removal/bmx-trees \
    -m results/member_b_masks/video_name \
    -o results/inpainted
```

## 📝 完整示例

### 示例1：单个物体

```python
from member_b_track_anything import MemberBTrackAnything

module = MemberBTrackAnything()

# 输入
video = 'inputs/object_removal/bmx-trees'
bbox = [[150, 150, 250, 250]]

# 处理
mask_path, masks = module.process_video(video, bbox)

# 输出
print(f"✓ 成功生成 {len(masks)} 个掩码")
print(f"✓ 掩码路径: {mask_path}")

# 传递给成员C
# python inference_propainter.py -i {video} -m {mask_path}
```

### 示例2：多个物体

```python
module = MemberBTrackAnything()

bboxes = [
    [100, 100, 200, 200],  # 物体1
    [300, 300, 400, 400],  # 物体2
]

mask_path, masks = module.process_video('video.mp4', bboxes)
```

## 🧪 测试

```bash
# 快速测试
python -c "
from member_b_track_anything import MemberBTrackAnything
module = MemberBTrackAnything()
mask_path, masks = module.process_video(
    'inputs/object_removal/bmx-trees',
    [[150, 150, 250, 250]]
)
print(f'✓ 成功生成 {len(masks)} 个掩码')
"
```

## 📚 相关文档

- **快速开始**: [QUICK_START.md](./QUICK_START.md)
- **详细使用**: [MEMBER_B_USAGE.md](./MEMBER_B_USAGE.md)
- **技术方案**: [MEMBER_B_TRACK_ANYTHING.md](./MEMBER_B_TRACK_ANYTHING.md)

## 🎉 总结

**你的工作流程**：
1. ✅ 接收成员A的边界框
2. ✅ 使用SAM分割第一帧
3. ✅ 使用CUTIE追踪整个视频
4. ✅ 输出掩码序列给成员C

**输入输出**：
- **输入**：视频路径 + 边界框列表
- **输出**：掩码文件夹路径

---

**有问题？查看详细文档或联系团队成员！**


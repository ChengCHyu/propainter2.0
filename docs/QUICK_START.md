# 🚀 快速开始指南

## 📋 完整流程概览

```
语音输入 → 文本 → 边界框 → 掩码 → ProPainter修复 → 最终视频
   ↓        ↓       ↓       ↓          ↓              ↓
成员D    成员D   成员A   成员B⭐   成员C         输出
```

## 🎯 成员B的快速使用

### 最简单的使用方式

```python
from member_b_track_anything import MemberBTrackAnything

# 1. 初始化（自动加载模型）
module = MemberBTrackAnything()

# 2. 输入：视频 + 边界框（来自成员A）
video_path = 'inputs/object_removal/bmx-trees'
bboxes = [[150, 150, 250, 250]]  # [x1, y1, x2, y2]

# 3. 处理
output_path, masks = module.process_video(
    video_path=video_path,
    bboxes=bboxes
)

# 4. 输出：掩码文件夹路径
print(f"掩码保存在: {output_path}")
# 结果: results/member_b_masks/bmx-trees/
```

### 命令行使用

**Linux/Mac (Bash):**
```bash
# 1. 准备边界框JSON文件
cat > bboxes.json << EOF
[[150, 150, 250, 250]]
EOF

# 2. 运行
python member_b_track_anything.py \
    --video inputs/object_removal/bmx-trees \
    --bbox bboxes.json \
    --output results/masks
```

**Windows PowerShell:**
```powershell
# 方式1：一行命令
python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox "[[150, 150, 250, 250]]" --output results/masks

# 方式2：使用反引号继续行
python member_b_track_anything.py `
    --video inputs/object_removal/bmx-trees `
    --bbox "[[150, 150, 250, 250]]" `
    --output results/masks

# 方式3：使用JSON文件
# 先创建 bboxes.json 文件，内容: [[150, 150, 250, 250]]
python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox bboxes.json --output results/masks
```

**Windows CMD:**
```cmd
python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox "[[150, 150, 250, 250]]" --output results/masks
```

## 📥 输入说明

### 输入1：视频路径
- 视频文件：`video.mp4`, `video.avi`
- 或帧文件夹：包含 `00000.jpg`, `00001.jpg` 等

### 输入2：边界框（来自成员A）
```python
# 格式：[[x1, y1, x2, y2], ...]
bboxes = [
    [100, 100, 200, 200],  # 物体1的边界框
    [300, 300, 400, 400],  # 物体2的边界框（可选）
]
```

## 📤 输出说明

### 输出：掩码文件夹
```
results/member_b_masks/video_name/
├── 00000.png    # 第0帧掩码
├── 00001.png    # 第1帧掩码
├── 00002.png    # 第2帧掩码
├── ...
└── mask_video.mp4  # 掩码视频（可视化）
```

**掩码格式**：
- PNG图像，单通道
- 0 = 背景（保留）
- 1, 2, 3... = 不同物体（删除）

## 🔗 完整流程示例

### 方式1：分步执行

```python
# 步骤1：成员B生成掩码
from member_b_track_anything import MemberBTrackAnything

module_b = MemberBTrackAnything()
mask_path, masks = module_b.process_video(
    video_path='video.mp4',
    bboxes=[[100, 100, 200, 200]]  # 来自成员A
)

# 步骤2：成员C使用掩码修复视频
# 命令行：
# python inference_propainter.py -i video.mp4 -m mask_path -o results/inpainted
```

### 方式2：端到端执行

```python
from pipeline_end_to_end import EndToEndPipeline

# 一次性完成所有步骤
pipeline = EndToEndPipeline()
result = pipeline.process(
    video_path='video.mp4',
    bboxes=[[100, 100, 200, 200]],  # 来自成员A
    output_dir='results/pipeline'
)

print(f"掩码: {result['mask_path']}")
print(f"修复视频: {result['inpainted_video_path']}")
```

## 📝 实际使用示例

### 示例1：删除单个物体

```python
from member_b_track_anything import MemberBTrackAnything

module = MemberBTrackAnything()

# 输入
video = 'inputs/object_removal/bmx-trees'
bbox = [[150, 150, 250, 250]]  # 要删除的物体边界框

# 处理
mask_path, masks = module.process_video(video, bbox)

# 输出
print(f"✓ 生成 {len(masks)} 个掩码帧")
print(f"✓ 掩码保存在: {mask_path}")

# 下一步：传递给ProPainter
# python inference_propainter.py -i {video} -m {mask_path}
```

### 示例2：删除多个物体

```python
module = MemberBTrackAnything()

# 多个边界框
bboxes = [
    [100, 100, 200, 200],  # 物体1
    [300, 300, 400, 400],  # 物体2
]

mask_path, masks = module.process_video('video.mp4', bboxes)
```

### 示例3：从JSON文件读取边界框

```python
import json

# 读取成员A的输出
with open('member_a_output/bboxes.json', 'r') as f:
    bboxes = json.load(f)

# 处理
module = MemberBTrackAnything()
mask_path, masks = module.process_video('video.mp4', bboxes)
```

## 🔄 与团队成员协作

### 接收成员A的输出

成员A应该提供：
```json
{
    "video_path": "inputs/object_removal/bmx-trees",
    "bboxes": [[100, 100, 200, 200], [300, 300, 400, 400]]
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

## ⚡ 快速测试

```bash
# 1. 测试成员B
python -c "
from member_b_track_anything import MemberBTrackAnything
module = MemberBTrackAnything()
mask_path, masks = module.process_video(
    'inputs/object_removal/bmx-trees',
    [[150, 150, 250, 250]]
)
print(f'✓ 成功生成 {len(masks)} 个掩码')
"

# 2. 测试端到端流程 (Linux/Mac)
python pipeline_end_to_end.py \
    --video inputs/object_removal/bmx-trees \
    --bbox '[[150, 150, 250, 250]]' \
    --output results/test

# Windows PowerShell (一行命令)
python pipeline_end_to_end.py --video inputs/object_removal/bmx-trees --bbox "[[150, 150, 250, 250]]" --output results/test
```

## 📚 更多文档

- **详细使用**: [MEMBER_B_USAGE.md](./MEMBER_B_USAGE.md)
- **技术方案**: [MEMBER_B_TRACK_ANYTHING.md](./MEMBER_B_TRACK_ANYTHING.md)
- **API参考**: `member_b_api.py`

---

**总结**：
1. **输入**：视频路径 + 边界框（来自成员A）
2. **处理**：SAM分割 + CUTIE追踪
3. **输出**：掩码文件夹（给成员C）
4. **下一步**：成员C使用掩码进行ProPainter修复


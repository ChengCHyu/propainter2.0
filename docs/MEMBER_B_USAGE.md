# 成员B：完整使用指南

## 📋 完整流程说明

### 🔄 端到端流程

```
语音输入（成员D）
    ↓
文本："删除视频中的汽车"（成员D）
    ↓
边界框 [[x1,y1,x2,y2], ...]（成员A - GroundingDINO）
    ↓
掩码序列（成员B - SAM + CUTIE）⭐ 你负责的部分
    ↓
修复视频（成员C - ProPainter）
```

## 🎯 成员B的输入输出

### 输入

1. **视频路径**
   - 视频文件：`video.mp4`, `video.avi` 等
   - 或帧文件夹：包含 `00000.jpg`, `00001.jpg` 等

2. **边界框**（来自成员A）
   - 格式：`[[x1, y1, x2, y2], [x1, y1, x2, y2], ...]`
   - 每个边界框代表一个要删除的物体
   - 坐标是像素坐标，相对于第一帧

### 输出

1. **掩码文件夹**
   - 包含逐帧掩码PNG文件：`00000.png`, `00001.png`, ...
   - 掩码格式：单通道PNG，0=背景，1,2,3...=不同物体

2. **掩码视频**（可选）
   - `mask_video.mp4`：可视化掩码的视频

## 🚀 使用方法

### 方法1：直接使用成员B模块（推荐）

```python
from member_b_track_anything import MemberBTrackAnything

# 1. 初始化模块
module = MemberBTrackAnything(
    sam_checkpoint='weights/sam_vit_h_4b8939.pth',
    tracker_checkpoint='weights/cutie-base.pth',
    device='cuda:0'
)

# 2. 准备输入
video_path = 'inputs/object_removal/bmx-trees'
bboxes = [[100, 100, 200, 200]]  # 来自成员A的边界框

# 3. 处理视频
output_path, masks = module.process_video(
    video_path=video_path,
    bboxes=bboxes,
    output_mask_path='results/member_b_output'
)

# 4. 输出结果
print(f"掩码保存在: {output_path}")
print(f"共生成 {len(masks)} 个掩码帧")
```

### 方法2：使用API接口

```python
from member_b_api import MemberBAPI

# 初始化API
api = MemberBAPI()

# 处理视频
result = api.process(
    video_path='inputs/object_removal/bmx-trees',
    bboxes=[[100, 100, 200, 200]],
    output_path='results/member_b_output'
)

if result['status'] == 'success':
    print(f"成功！掩码保存在: {result['output_path']}")
    print(f"掩码数量: {result['mask_count']}")
```

### 方法3：命令行使用

```bash
# 准备边界框JSON文件 bboxes.json
# 内容: [[100, 100, 200, 200]]

python member_b_track_anything.py \
    --video inputs/object_removal/bmx-trees \
    --bbox bboxes.json \
    --output results/member_b_output
```

### 方法4：端到端流程（包含ProPainter）

```python
from pipeline_end_to_end import EndToEndPipeline

# 初始化完整流程
pipeline = EndToEndPipeline()

# 处理（自动调用成员B和成员C）
result = pipeline.process(
    video_path='inputs/object_removal/bmx-trees',
    bboxes=[[100, 100, 200, 200]],  # 来自成员A
    output_dir='results/pipeline'
)

print(f"掩码路径: {result['mask_path']}")
print(f"修复视频: {result['inpainted_video_path']}")
```

## 📝 输入输出示例

### 输入示例1：单个物体

```python
video_path = 'inputs/object_removal/bmx-trees'
bboxes = [[150, 150, 250, 250]]  # 一个边界框
```

### 输入示例2：多个物体

```python
video_path = 'inputs/object_removal/bmx-trees'
bboxes = [
    [100, 100, 200, 200],  # 物体1
    [300, 300, 400, 400],  # 物体2
]
```

### 输入示例3：JSON文件

```json
// bboxes.json
[
    [100, 100, 200, 200],
    [300, 300, 400, 400]
]
```

### 输出示例

```
results/member_b_output/
├── 00000.png          # 第0帧掩码
├── 00001.png          # 第1帧掩码
├── 00002.png          # 第2帧掩码
├── ...
└── mask_video.mp4     # 掩码视频（可选）
```

## 🔗 与成员A和成员C的接口

### 接收成员A的输出

成员A应该提供：
- **视频路径**：字符串
- **边界框**：JSON格式或Python列表
  ```python
  bboxes = [[x1, y1, x2, y2], ...]
  ```

### 输出给成员C

成员B输出：
- **掩码文件夹路径**：字符串
  ```python
  mask_path = 'results/member_b_output'
  ```

成员C可以使用：
```bash
python inference_propainter.py \
    -i inputs/object_removal/bmx-trees \
    -m results/member_b_output \
    -o results/inpainted
```

## 🧪 完整测试流程

### 步骤1：测试成员B单独运行

```python
# test_member_b.py
from member_b_track_anything import MemberBTrackAnything

module = MemberBTrackAnything()
bboxes = [[150, 150, 250, 250]]  # 需要根据实际视频调整

output_path, masks = module.process_video(
    video_path='inputs/object_removal/bmx-trees',
    bboxes=bboxes
)

print(f"✓ 成员B测试通过")
print(f"  掩码路径: {output_path}")
print(f"  掩码数量: {len(masks)}")
```

### 步骤2：测试端到端流程

```bash
# 准备边界框
echo '[[150, 150, 250, 250]]' > bboxes.json

# 运行端到端流程
python pipeline_end_to_end.py \
    --video inputs/object_removal/bmx-trees \
    --bbox bboxes.json \
    --output results/pipeline_test
```

## 📊 输入输出格式详解

### 边界框格式

**格式1：Python列表**
```python
bboxes = [[x1, y1, x2, y2], [x1, y1, x2, y2]]
```

**格式2：JSON文件**
```json
[
    [100, 100, 200, 200],
    [300, 300, 400, 400]
]
```

**格式3：字典（多帧）**
```python
bboxes = {
    0: [[100, 100, 200, 200]],      # 第0帧
    10: [[150, 150, 250, 250]],    # 第10帧（重新初始化）
}
```

### 掩码格式

- **文件格式**：PNG图像
- **通道数**：单通道（灰度）
- **像素值**：
  - `0` = 背景（不删除）
  - `1, 2, 3, ...` = 不同物体（要删除）
- **命名**：`00000.png`, `00001.png`, ...

### ProPainter输入格式

ProPainter需要的掩码格式：
- 文件夹包含逐帧PNG掩码
- 掩码值：0=背景，255=要删除的区域
- 需要转换为ProPainter格式（会自动处理）

## ⚙️ 配置选项

### 环境变量

```bash
export SAM_CHECKPOINT="weights/sam_vit_h_4b8939.pth"
export TRACKER_CHECKPOINT="weights/cutie-base.pth"
export CUDA_VISIBLE_DEVICES=0
```

### 模型路径

如果不指定，会自动使用默认路径：
- SAM: `weights/sam_vit_h_4b8939.pth`
- CUTIE: `weights/cutie-base.pth`

## 🐛 常见问题

### Q1: 如何获取边界框？

**A:** 边界框应该由成员A（GroundingDINO）提供。如果测试，可以手动指定：
```python
# 查看视频第一帧，手动指定边界框
bboxes = [[x1, y1, x2, y2]]  # 根据实际物体位置调整
```

### Q2: 掩码格式不对？

**A:** 成员B输出的掩码格式已经兼容ProPainter。如果遇到问题，检查：
- 掩码文件是否存在
- 掩码值范围是否正确（0-255）
- 文件命名是否正确（00000.png格式）

### Q3: 如何传递给成员C？

**A:** 直接传递掩码文件夹路径：
```python
mask_path = 'results/member_b_output'
# 成员C使用: python inference_propainter.py -i video -m mask_path
```

### Q4: 处理速度慢？

**A:** 
- 使用GPU加速（`device='cuda:0'`）
- 降低视频分辨率
- 使用较小的SAM模型（`vit_b`而不是`vit_h`）

## 📚 相关文件

- `member_b_track_anything.py` - 核心模块
- `member_b_api.py` - API接口
- `pipeline_end_to_end.py` - 端到端流程
- `MEMBER_B_TRACK_ANYTHING.md` - 技术方案说明

## 🎉 快速开始

```bash
# 1. 准备边界框
echo '[[150, 150, 250, 250]]' > bboxes.json

# 2. 运行成员B
python member_b_track_anything.py \
    --video inputs/object_removal/bmx-trees \
    --bbox bboxes.json \
    --output results/member_b_output

# 3. 检查输出
ls results/member_b_output/

# 4. 传递给ProPainter（成员C）
python inference_propainter.py \
    -i inputs/object_removal/bmx-trees \
    -m results/member_b_output \
    -o results/inpainted
```

---

**最后更新**: 2024年
**版本**: 1.0


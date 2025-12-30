# 成员A：文本定位模块

## 📋 模块说明

**成员A负责：文本描述 → 边界框定位**

使用GroundingDINO实现文本到边界框的转换。

## 🎯 功能

- ✅ 接收文本输入（如"删除视频中的汽车"）
- ✅ 使用GroundingDINO检测第一帧中的目标物体
- ✅ 输出边界框列表（给成员B）

## 📦 文件结构

```
member_a/
├── __init__.py           # 模块初始化
├── text_to_bbox.py       # 核心模块：文本到边界框
└── README.md             # 本文件
```

## 🚀 快速开始

### 安装GroundingDINO

```bash
# 方法1：使用pip
pip install groundingdino-py

# 方法2：从源码安装
git clone https://github.com/IDEA-Research/GroundingDINO.git
cd GroundingDINO
pip install -e .
```

### 下载模型

```bash
# 下载GroundingDINO模型
wget https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swinb_cogcoor.pth
mv groundingdino_swinb_cogcoor.pth weights/
```

### 使用示例

```python
from member_a import TextToBBox

# 初始化
module = TextToBBox()

# 处理视频
bboxes = module.process_video_first_frame(
    video_path='video.mp4',
    text_prompt='car'  # 或 "删除视频中的汽车"
)

print(f"检测到 {len(bboxes)} 个目标物体")
for i, bbox in enumerate(bboxes):
    print(f"物体{i+1}: {bbox}")
```

## 📖 命令行使用

```bash
python -m member_a.text_to_bbox \
    --video inputs/object_removal/bmx-trees \
    --text "car" \
    --output results/member_a_bboxes/bboxes.json
```

## 🔗 与其他成员的接口

### 输入（来自成员D）

```python
text_prompt = "删除视频中的汽车"  # 文本描述
```

### 输出（给成员B）

```python
bboxes = [[x1, y1, x2, y2], ...]  # 边界框列表
```

## ⚙️ 依赖

- GroundingDINO：需要单独安装
- 模型文件：`weights/groundingdino_swinb_cogcoor.pth`

## 📝 注意事项

- 当前版本提供框架，需要安装GroundingDINO才能使用
- 如果没有安装，会使用模拟模式（返回示例边界框）
- 参考：https://github.com/IDEA-Research/GroundingDINO



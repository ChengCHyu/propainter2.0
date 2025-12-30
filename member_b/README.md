# 成员B：分割与追踪模块

## 📋 模块说明

**成员B模块是独立的，不依赖ProPainter核心代码！**

本模块只依赖：
- SAM (Segment Anything Model) - 用于分割
- CUTIE追踪器 - 用于视频追踪
- Track-Anything工具模块

## 🎯 功能

- ✅ 接收边界框输入（来自成员A）
- ✅ 使用SAM分割第一帧
- ✅ 使用CUTIE追踪整个视频
- ✅ 输出掩码序列（给成员C）

## 📦 文件结构

```
member_b/
├── __init__.py           # 模块初始化
├── segment_track.py      # 核心模块：分割与追踪
├── api.py                # API接口
├── README.md             # 本文件
└── CODE_EXPLANATION.md   # 代码解读文档
```

## 🚀 快速开始

```python
from member_b import MemberBTrackAnything

# 初始化
module = MemberBTrackAnything()

# 处理视频
bboxes = [[100, 100, 200, 200]]  # 来自成员A的边界框
mask_path, masks = module.process_video(
    video_path='video.mp4',
    bboxes=bboxes
)

print(f"掩码保存在: {mask_path}")
```

## 📖 详细文档

- **代码解读**: [CODE_EXPLANATION.md](./CODE_EXPLANATION.md)
- **使用指南**: 查看项目根目录的 `MEMBER_B_USAGE.md`

## 🔗 与其他成员的接口

### 接收成员A的输出

```python
# 成员A提供边界框
bboxes = [[x1, y1, x2, y2], ...]
```

### 输出给成员C

```python
# 成员B输出掩码文件夹路径
mask_path = "results/member_b_masks/video_name"
```

## ⚙️ 依赖

- SAM模型：`weights/sam_vit_h_4b8939.pth`
- CUTIE模型：`weights/cutie-base-mega.pth`

## 📝 注意事项

- 模块独立，不依赖ProPainter核心代码
- 需要访问 `web-demos/hugging_face/` 中的Track-Anything模块
- 模型文件会自动下载（如果不存在）



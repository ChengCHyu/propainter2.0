# VideoPureVideo - 视频物体删除工具

基于 ProPainter 的视频物体删除项目，支持文本输入和手动框选两种方式选择要删除的物体。

## ✨ 功能特点

- 🎬 **文本输入**：使用自然语言描述要删除的物体（基于 GroundingDINO）
- 🖱️ **手动框选**：在视频上直接拖拽框选物体
- 🎯 **多物体支持**：可以同时删除多个物体
- 🌐 **Web界面**：现代化的Web界面，操作简单直观
- 📦 **完整流程**：自动生成掩码、追踪物体、修复视频

## 🚀 快速开始

### 前置要求

- Python 3.8+
- CUDA（推荐，用于GPU加速）
- 已安装 ProPainter 基础代码

### 安装步骤

1. **克隆仓库**（包含 ProPainter 作为 submodule）：
   ```bash
   git clone --recursive https://github.com/hongdouzza/videopureVideo.git
   cd videopureVideo
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **安装 GroundingDINO**（用于文本输入）：
   ```bash
   cd GroundingDINO
   pip install -r requirements.txt
   pip install -e .
   cd ..
   ```

4. **下载模型权重**：
   - SAM模型：`weights/sam_vit_h_4b8939.pth`
   - CUTIE模型：`weights/cutie-base-mega.pth`
   - ProPainter模型：`weights/ProPainter.pth`
   - RAFT模型：`weights/raft-things.pth`
   - GroundingDINO模型：`weights/groundingdino_swinb_cogcoor.pth`

### 使用方法

#### Web界面（推荐）

```bash
cd video_object_removal_web
python app.py
```

然后访问 `http://127.0.0.1:5000`

#### 命令行

```bash
# 使用文本输入
python complete_pipeline.py --video video.mp4 --text "car"

# 使用边界框
python complete_pipeline.py --video video.mp4 --bbox "[[100, 100, 200, 200]]"
```

## 📁 项目结构

```
videopureVideo/
├── member_a/              # 文本到边界框转换（GroundingDINO）
├── member_b/              # 边界框到掩码（SAM + CUTIE）
├── video_object_removal_web/  # Web前端界面
├── GroundingDINO/         # GroundingDINO源码
└── README.md              # 本文件
```

## 🔗 依赖项目

本项目基于以下开源项目：

- **ProPainter**: https://github.com/sczhou/ProPainter
- **GroundingDINO**: https://github.com/IDEA-Research/GroundingDINO
- **Track-Anything**: 用于物体追踪

## 📝 使用说明

### 文本输入模式

1. 上传视频
2. 选择"文本输入"模式
3. 输入描述，例如："删除视频中的汽车"
4. 点击"生成边界框"
5. 检查并调整边界框
6. 点击"开始处理"

### 手动框选模式

1. 上传视频
2. 选择"手动框选"模式
3. 播放视频，找到要删除的物体
4. 暂停并框选物体
5. 可以框选多个物体
6. 点击"开始处理"

## ⚙️ 技术架构

- **成员A**：文本描述 → 边界框（GroundingDINO）
- **成员B**：边界框 → 掩码序列（SAM分割 + CUTIE追踪）
- **成员C**：掩码 + 视频 → 修复视频（ProPainter）

## 📄 许可证

本项目遵循原项目的许可证要求。

## 🙏 致谢

感谢所有开源项目的贡献者。

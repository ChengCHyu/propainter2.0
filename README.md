# VideoPureVideo - 视频物体删除工具

基于 ProPainter 的视频物体删除工具，支持文本输入和手动框选两种方式选择要删除的物体。

## ✨ 功能特点

- 🎬 **文本输入**：使用自然语言描述要删除的物体（如"删除视频中的汽车"）
- 🖱️ **手动框选**：在视频上直接拖拽框选物体
- 🎯 **多物体支持**：可以同时删除多个物体
- 🌐 **Web界面**：简洁易用的Web界面
- 🚀 **完整流程**：自动生成掩码、追踪物体、修复视频

## 📋 依赖项目

本项目基于以下开源项目：

- [ProPainter](https://github.com/sczhou/ProPainter) - 视频修复核心
- [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO) - 文本到边界框转换
- [Track-Anything](https://github.com/gaomingqi/Track-Anything) - 物体追踪

## 🚀 快速开始

### 1. 克隆仓库（包含子模块）

```bash
git clone --recursive https://github.com/hongdouzza/videopureVideo.git
cd videopureVideo
```

如果已经克隆，需要初始化子模块：

```bash
git submodule update --init --recursive
```

### 2. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装GroundingDINO
cd GroundingDINO
pip install -r requirements.txt
pip install -e .
cd ..
```

### 3. 下载模型权重

模型权重文件较大，需要单独下载到 `weights/` 目录：

- SAM模型：`sam_vit_h_4b8939.pth`
- CUTIE模型：`cutie-base-mega.pth`
- ProPainter模型：`ProPainter.pth`
- RAFT模型：`raft-things.pth`
- 流补全模型：`recurrent_flow_completion.pth`
- GroundingDINO模型：`groundingdino_swinb_cogcoor.pth`

### 4. 运行Web应用

```bash
cd video_object_removal_web
python app.py
```

访问 http://127.0.0.1:5000 使用Web界面。

## 📖 使用方法

### 文本输入模式

1. 上传视频
2. 选择"文本输入"模式
3. 输入描述，例如："删除视频中的汽车"
4. 点击"生成边界框"
5. 系统会自动检测并框选物体
6. 点击"开始处理"

### 手动框选模式

1. 上传视频
2. 选择"手动框选"模式
3. 播放视频，找到要框选的帧
4. 在视频上拖拽框选物体
5. 可以框选多个物体
6. 点击"开始处理"

## 🏗️ 项目结构

```
videopureVideo/
├── member_a/              # 文本到边界框转换（GroundingDINO）
├── member_b/              # 边界框到掩码（SAM + CUTIE）
├── video_object_removal_web/  # Web前端和后端
├── GroundingDINO/         # GroundingDINO源码
└── ProPainter/            # ProPainter子模块（git submodule）
```

## 📝 注意事项

- 需要GPU支持（推荐RTX 4060或更高）
- 模型权重文件需要单独下载（不在仓库中）
- 处理时间取决于视频长度和分辨率

## 📄 许可证

本项目基于ProPainter，遵循相应的开源许可证。

## 🙏 致谢

- [ProPainter](https://github.com/sczhou/ProPainter) - 视频修复核心
- [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO) - 文本定位
- [Track-Anything](https://github.com/gaomingqi/Track-Anything) - 物体追踪

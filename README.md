<<<<<<< HEAD
# VideoPureVideo - AI智能体视频物体删除工具

基于 ProPainter 的视频物体删除工具，支持文本输入和手动框选两种方式选择要删除的物体。内置 **AI智能体** 系统，可自动使用多种修复策略并行处理、评估质量并选取最佳结果。

## ✨ 功能特点

- 🎬 **文本输入**：使用自然语言描述要删除的物体（如"删除视频中的汽车"）
- 🖱️ **手动框选**：在视频上直接拖拽框选物体
- 🎯 **多物体支持**：可以同时删除多个物体
- 🤖 **智能体择优**：自动使用4种修复模型并行处理，通过质量评估选取最佳结果
- 📊 **质量评估**：从时域一致性、空间平滑度、修复区域质量、整体自然度4个维度评分
- 🚀 **GPU加速**：完整支持CUDA加速，默认启用fp16半精度推理
- 🌐 **Web界面**：简洁易用的Web界面，支持结果对比查看

## 📋 依赖项目

本项目基于以下开源项目：

- [ProPainter](https://github.com/sczhou/ProPainter) - 视频修复核心
- [GroundingDINO](https://github.com/IDEA-Research/GroundingDINO) - 文本到边界框转换
- [Track-Anything](https://github.com/gaomingqi/Track-Anything) - 物体追踪

## 🚀 快速开始

### 1. 克隆仓库（包含子模块）

```bash
git clone --recursive <你的仓库地址>
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

| 模型 | 文件 | 下载地址 |
|------|------|----------|
| SAM | `sam_vit_h_4b8939.pth` | https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth |
| CUTIE | `cutie-base-mega.pth` | https://github.com/sczhou/ProPainter/releases/download/v0.1.0/cutie-base-mega.pth |
| ProPainter | `ProPainter.pth` | https://github.com/sczhou/ProPainter/releases/download/v0.1.0/ProPainter.pth |
| RAFT | `raft-things.pth` | https://github.com/sczhou/ProPainter/releases/download/v0.1.0/raft-things.pth |
| 流补全 | `recurrent_flow_completion.pth` | https://github.com/sczhou/ProPainter/releases/download/v0.1.0/recurrent_flow_completion.pth |
| GroundingDINO | `groundingdino_swinb_cogcoor.pth` | 需从GroundingDINO项目获取 |

### 4. 运行Web应用

```bash
cd video_object_removal_web
python app.py
```

访问 http://127.0.0.1:5000 使用Web界面。

## 📖 使用方法

### 选择处理模式

在点击"开始处理"前，可以选择两种模式：

- **单模型快速处理**：使用默认ProPainter配置，速度较快
- **智能体多模型择优**：使用4种不同配置并行处理，评估后选取最佳结果

### 文本输入模式

1. 上传视频
2. 选择"文本输入"模式
3. 输入描述，例如："删除视频中的汽车"
4. 点击"生成边界框"
5. 系统会自动检测并框选物体
6. 选择处理模式，点击"开始处理"

### 手动框选模式

1. 上传视频
2. 选择"手动框选"模式
3. 播放视频，找到要框选的帧
4. 在视频上拖拽框选物体
5. 可以框选多个物体
6. 选择处理模式，点击"开始处理"

### 智能体模式结果解读

智能体处理完成后，会展示：

- **🏆 最佳模型**：综合评分最高的模型结果
- **📊 排名表格**：所有模型的详细评分和耗时
- **🎬 结果对比**：可点击"查看"按钮切换不同模型的结果视频

评估维度说明：

| 维度 | 权重 | 说明 |
|------|------|------|
| 时域一致性 | 30% | 评估相邻帧之间的过渡平滑度 |
| 空间平滑度 | 20% | 评估修复区域是否有伪影或突兀 |
| 修复区域质量 | 35% | 基于PSNR/SSIM评估修复精度 |
| 整体自然度 | 15% | 评估颜色分布和亮度自然程度 |

## 🏗️ 项目结构

```
videopureVideo/
├── member_a/                    # 文本到边界框转换（GroundingDINO）
├── member_b/                    # 边界框到掩码（SAM + CUTIE）
├── video_object_removal_web/    # Web前端和后端
│   ├── app.py                   # Flask后端API
│   ├── video_processor.py       # 视频处理包装器
│   ├── video_agent.py           # 智能体多模型处理模块
│   ├── video_evaluator.py       # 视频质量评估模块
│   └── index.html               # 前端界面
├── GroundingDINO/               # GroundingDINO源码
└── ProPainter/                  # ProPainter子模块（git submodule）
```

## ⚙️ 技术细节

- **掩码生成**：Member B使用SAM分割第一帧，CUTIE追踪器追踪后续帧
- **视频修复**：ProPainter基于光流和Transformer的修复网络
- **智能体系统**：4种不同配置（默认/高质量/快速/保守）+ 综合质量评估 + 自动择优
- **GPU加速**：默认启用cuda和fp16半精度推理，显存需求约4-8GB

## 📝 注意事项

- 需要GPU支持（推荐RTX 4060或更高）
- 模型权重文件需要单独下载（不在仓库中）
- 处理时间取决于视频长度和分辨率
- 智能体模式会运行4次修复，耗时约为单模型模式的3-4倍
- 确保Python版本 >= 3.8

## 📄 许可证

本项目基于ProPainter，遵循相应的开源许可证。
=======
# propainter2.0
>>>>>>> 7e1b5d4df5064770093eff64951d6e843d3b2e4b

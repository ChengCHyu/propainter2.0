# 视频物体删除 Web 应用

一个基于Web的视频物体删除工具，支持在视频中框选要删除的物体，自动生成掩码。

## ✨ 功能特点

- 🎬 **视频播放控制**：支持播放、暂停、逐帧查看
- 🖱️ **可视化框选**：在视频画面上直接拖拽框选物体
- 🎯 **多物体支持**：可以框选多个物体同时删除
- 🎨 **简洁界面**：现代化的Web界面，操作简单直观
- 📦 **干净输出**：隐藏内部实现细节，只显示用户关心的结果

## 📋 前置要求

1. Python 3.8+
2. 已安装项目所需的模型文件：
   - SAM模型：`weights/sam_vit_h_4b8939.pth`
   - CUTIE模型：`weights/cutie-base-mega.pth`
   - ProPainter模型：`weights/ProPainter.pth`
   - RAFT模型：`weights/raft-things.pth`
   - 流补全模型：`weights/recurrent_flow_completion.pth`
3. 父目录中的 `member_b` 模块和 `inference_propainter.py` 可用

## 🚀 快速开始

### 1. 安装依赖

```bash
cd video_object_removal_web
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python app.py
```

### 3. 访问应用

打开浏览器访问：http://127.0.0.1:5000

## 📖 使用说明

1. **上传视频**：点击"选择视频"按钮，选择要处理的视频文件
2. **播放视频**：视频加载后，点击"播放"按钮
3. **暂停到目标帧**：找到要框选物体的帧，点击"暂停"
4. **框选物体**：
   - 按住鼠标左键在视频上拖拽，框选要删除的物体
   - 可以框选多个物体，每个物体会显示不同的颜色
   - 可以点击"删除"按钮移除某个边界框
   - 点击"重置选择"清空所有选择
5. **处理视频**：点击"开始处理"按钮，系统会自动：
   - 生成物体掩码
   - 使用ProPainter删除物体
   - 生成处理后的视频
6. **查看结果**：处理完成后，可以在页面中预览和下载处理后的视频

## 📁 项目结构

```
video_object_removal_web/
├── app.py              # Flask后端服务器
├── index.html          # 前端页面
├── requirements.txt    # Python依赖
├── README.md          # 本文件
├── uploads/           # 上传的视频文件（自动创建）
└── outputs/           # 输出的掩码文件（自动创建）
```

## 🔧 配置

可以在 `app.py` 中修改以下配置：

- `UPLOAD_FOLDER`：上传文件保存目录（默认：`uploads`）
- `OUTPUT_FOLDER`：输出文件保存目录（默认：`outputs`）
- `port`：服务器端口（默认：5000）

## 📝 API 接口

### GET /api/health

健康检查

**响应**：
```json
{
  "status": "ok",
  "module_available": true
}
```

### POST /api/process

处理视频：生成掩码 + ProPainter修复

**请求体**：
```json
{
  "video_path": "视频文件路径",
  "bboxes": [[x1, y1, x2, y2], ...]
}
```

**响应**：
```json
{
  "status": "success",
  "video_path": "处理后的视频相对路径",
  "video_url": "/api/video_output/inpaint_out.mp4",
  "message": "视频处理完成，物体已删除"
}
```

### GET /api/video_output/<filename>

获取处理后的视频文件

## ⚠️ 注意事项

1. **文件路径**：确保父目录中的 `member_b` 模块和 `inference_propainter.py` 可以正常导入
2. **模型文件**：确保已下载所有必需的模型文件（包括ProPainter相关模型）
3. **处理时间**：处理大型视频可能需要较长时间（生成掩码 + ProPainter修复），请耐心等待
4. **多物体删除**：✅ **支持！** 可以框选多个物体，系统会同时删除所有选中的物体
5. **输出视频**：处理完成后，视频会在页面中显示，也可以下载保存

## 🔄 后续改进

- [ ] 实现视频文件上传功能
- [ ] 添加处理进度实时更新
- [ ] 支持预览生成的掩码
- [ ] 添加批量处理功能
- [ ] 优化界面和用户体验

## 📄 许可证

与主项目保持一致


# 视频上传问题排查

## 视频保存位置

视频会保存到本地，具体位置取决于你从哪里启动 `app.py`：

**如果从 `video_object_removal_web/` 目录启动：**
```
D:\XUEXI\ProPainter\video_object_removal_web\uploads\
```

**如果从项目根目录启动：**
```
D:\XUEXI\ProPainter\uploads\
```

## 如何确认上传目录

启动服务器时，终端会显示：
```
上传目录: D:\XUEXI\ProPainter\video_object_removal_web\uploads
输出目录: D:\XUEXI\ProPainter\video_object_removal_web\outputs
```

## 如果一直显示"正在上传视频..."

可能的原因：
1. **文件太大**：视频文件很大，上传需要时间
2. **网络问题**：本地服务器响应慢
3. **文件格式问题**：虽然选择了文件，但可能格式不支持
4. **浏览器问题**：可能需要检查浏览器控制台（F12）查看错误

## 检查方法

1. **检查浏览器控制台**（按F12）：
   - 查看Network标签，看上传请求是否成功
   - 查看Console标签，看是否有错误信息

2. **检查服务器终端**：
   - 看是否有错误信息
   - 看是否有上传请求日志

3. **检查上传目录**：
   - 查看 `video_object_removal_web\uploads\` 目录
   - 看是否有文件正在写入

## 文件大小限制

Flask默认没有文件大小限制，但如果有问题，可能需要配置。









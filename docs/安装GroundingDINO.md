# 安装 GroundingDINO 说明

## 📋 安装步骤

你已经克隆了 GroundingDINO 仓库，现在需要完成安装：

### 方法1：使用安装脚本（推荐）

**PowerShell:**
```powershell
.\install_groundingdino.ps1
```

**CMD:**
```cmd
install_groundingdino.bat
```

### 方法2：手动安装

#### 步骤1：安装依赖

```powershell
cd GroundingDINO
pip install -r requirements.txt
```

#### 步骤2：安装 GroundingDINO 包

```powershell
pip install -e .
```

#### 步骤3：下载模型权重

模型文件需要下载到 `weights/` 目录：

**方法A：使用 PowerShell 下载**
```powershell
cd ..
mkdir weights -ErrorAction SilentlyContinue
cd weights
Invoke-WebRequest -Uri "https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha2/groundingdino_swinb_cogcoor.pth" -OutFile "groundingdino_swinb_cogcoor.pth"
```

**方法B：手动下载**
1. 访问：https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha2/groundingdino_swinb_cogcoor.pth
2. 下载文件
3. 保存到：`weights/groundingdino_swinb_cogcoor.pth`

## ✅ 验证安装

安装完成后，运行以下命令验证：

```python
python -c "from groundingdino.util.inference import load_model; print('GroundingDINO 安装成功！')"
```

如果成功，会显示：`GroundingDINO 安装成功！`

如果失败，会显示错误信息，请根据错误信息排查。

## 🔧 常见问题

### 问题1：编译错误（NameError: name '_C' is not defined）

**原因：** GroundingDINO 需要编译 C++/CUDA 扩展

**解决方案：**
1. 确保已安装 Visual Studio Build Tools（Windows）
2. 确保 CUDA_HOME 环境变量已设置（如果使用 GPU）
3. 重新安装：
   ```powershell
   cd GroundingDINO
   pip uninstall groundingdino -y
   pip install -e . --no-cache-dir
   ```

### 问题2：CUDA 相关错误

**解决方案：**
- 如果使用 CPU，安装时会自动使用 CPU 模式
- 如果使用 GPU，确保 CUDA 版本匹配

### 问题3：依赖包冲突

**解决方案：**
```powershell
pip install --upgrade torch torchvision
pip install -r GroundingDINO/requirements.txt
```

### 问题4：模型文件下载失败

**解决方案：**
1. 检查网络连接
2. 使用浏览器手动下载
3. 或使用下载工具（如 IDM、迅雷等）

## 📝 安装后的使用

安装完成后，文本输入功能会自动使用真实的 GroundingDINO 检测，而不是模拟模式。

### 测试文本输入功能

1. 启动 Web 应用：
   ```powershell
   cd video_object_removal_web
   python app.py
   ```

2. 访问 http://127.0.0.1:5000

3. 上传视频，选择"文本输入"模式

4. 输入描述，例如："删除视频中的汽车"

5. 点击"生成边界框"

如果安装成功，会看到真实的检测结果；如果未安装，会使用模拟模式。

## 🎯 多物体删除

安装 GroundingDINO 后，可以轻松删除多个物体：

1. **文本输入**：输入 "car . person . tree" 会自动检测所有匹配的物体
2. **手动框选**：可以框选多个物体
3. **组合使用**：先用文本输入，再手动调整

详细说明请查看：`docs/多物体删除说明.md`





# 下载ProPainter模型文件

如果遇到网络超时错误，可以手动下载ProPainter所需的模型文件。

## 所需模型文件

ProPainter需要以下模型文件（保存在 `weights/` 目录）：

1. **raft-things.pth** - RAFT流估计模型（通常已下载）
2. **recurrent_flow_completion.pth** - 流补全模型
3. **ProPainter.pth** - ProPainter主模型

## 下载地址

所有模型文件都可以从以下地址下载：

```
https://github.com/sczhou/ProPainter/releases/download/v0.1.0/
```

### 直接下载链接

- **raft-things.pth**: https://github.com/sczhou/ProPainter/releases/download/v0.1.0/raft-things.pth
- **recurrent_flow_completion.pth**: https://github.com/sczhou/ProPainter/releases/download/v0.1.0/recurrent_flow_completion.pth
- **ProPainter.pth**: https://github.com/sczhou/ProPainter/releases/download/v0.1.0/ProPainter.pth

## 下载方法

### 方法1：使用浏览器下载

1. 打开上面的下载链接
2. 下载文件到 `weights/` 目录
3. 确保文件名正确（包括.pth扩展名）

### 方法2：使用wget（如果已安装）

```bash
cd weights
wget https://github.com/sczhou/ProPainter/releases/download/v0.1.0/recurrent_flow_completion.pth
wget https://github.com/sczhou/ProPainter/releases/download/v0.1.0/ProPainter.pth
```

### 方法3：使用PowerShell下载

```powershell
cd weights

# 下载 recurrent_flow_completion.pth
Invoke-WebRequest -Uri "https://github.com/sczhou/ProPainter/releases/download/v0.1.0/recurrent_flow_completion.pth" -OutFile "recurrent_flow_completion.pth"

# 下载 ProPainter.pth
Invoke-WebRequest -Uri "https://github.com/sczhou/ProPainter/releases/download/v0.1.0/ProPainter.pth" -OutFile "ProPainter.pth"
```

### 方法4：使用Python脚本下载

```python
import os
from utils.download_util import load_file_from_url

pretrain_model_url = 'https://github.com/sczhou/ProPainter/releases/download/v0.1.0/'

# 下载 recurrent_flow_completion.pth
print("下载 recurrent_flow_completion.pth...")
load_file_from_url(
    url=f"{pretrain_model_url}recurrent_flow_completion.pth",
    model_dir='weights',
    progress=True,
    file_name='recurrent_flow_completion.pth'
)

# 下载 ProPainter.pth
print("下载 ProPainter.pth...")
load_file_from_url(
    url=f"{pretrain_model_url}ProPainter.pth",
    model_dir='weights',
    progress=True,
    file_name='ProPainter.pth'
)

print("完成！")
```

## 验证下载

下载完成后，检查 `weights/` 目录应该包含以下文件：

```
weights/
├── raft-things.pth
├── recurrent_flow_completion.pth
├── ProPainter.pth
├── sam_vit_h_4b8939.pth
└── cutie-base-mega.pth
```

## 文件大小参考

- **raft-things.pth**: ~20 MB
- **recurrent_flow_completion.pth**: ~30 MB
- **ProPainter.pth**: ~170 MB

如果下载的文件大小明显不对，可能需要重新下载。

## 网络问题解决

如果下载仍然失败，可以尝试：

1. **使用代理**：如果在中国大陆，可能需要使用代理
2. **使用镜像源**：查找是否有国内镜像
3. **稍后重试**：网络问题可能是暂时的
4. **使用下载工具**：使用IDM、迅雷等下载工具

## 临时解决方案

如果无法下载模型，可以：

1. **只生成掩码**：使用 `--skip-inpaint` 参数跳过ProPainter步骤
   ```bash
   python complete_pipeline.py --video inputs/object_removal/bmx-trees --text "car" --skip-inpaint
   ```

2. **稍后再运行ProPainter**：先生成掩码，等网络恢复后再单独运行ProPainter修复



# Windows PowerShell 使用指南

## ⚠️ 重要提示

PowerShell **不支持** `\` 作为行继续符！  
PowerShell 使用 **反引号** `` ` `` 作为行继续符。

## ✅ 正确的PowerShell命令格式

### 方式1：一行命令（推荐）

```powershell
python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox "[[150, 150, 250, 250]]" --output results/masks
```

### 方式2：使用反引号继续行

```powershell
python member_b_track_anything.py `
    --video inputs/object_removal/bmx-trees `
    --bbox "[[150, 150, 250, 250]]" `
    --output results/masks
```

**注意**：
- 反引号 `` ` `` 必须在行尾
- 反引号后面不能有空格
- JSON字符串用双引号 `"..."`

### 方式3：使用JSON文件

```powershell
# 1. 创建JSON文件（使用记事本或PowerShell）
@"
[[150, 150, 250, 250]]
"@ | Out-File -FilePath bboxes.json -Encoding utf8

# 2. 运行
python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox bboxes.json --output results/masks
```

## ❌ 错误的命令格式

```powershell
# ❌ 错误：PowerShell不支持 \ 作为行继续符
python member_b_track_anything.py \
    --video inputs/object_removal/bmx-trees \
    --bbox '[[150, 150, 250, 250]]' \
    --output results/masks
```

## 📝 完整示例

### 示例1：基本使用

```powershell
python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox "[[150, 150, 250, 250]]" --output results/masks
```

### 示例2：多个边界框

```powershell
python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox "[[100, 100, 200, 200], [300, 300, 400, 400]]" --output results/masks
```

### 示例3：使用JSON文件

```powershell
# 创建JSON文件
$bboxes = @"
[
    [100, 100, 200, 200],
    [300, 300, 400, 400]
]
"@
$bboxes | Out-File -FilePath bboxes.json -Encoding utf8

# 运行
python member_b_track_anything.py --video inputs/object_removal/bmx-trees --bbox bboxes.json --output results/masks
```

## 🔧 使用批处理脚本（更简单）

我已经创建了 `run_member_b.bat` 文件，可以直接双击运行！

或者：
```cmd
run_member_b.bat
```

## 🐛 常见问题

### Q1: 提示"无法识别命令"

**A:** 确保Python在PATH中：
```powershell
# 检查Python是否可用
python --version

# 如果不行，使用完整路径
C:\Python39\python.exe member_b_track_anything.py --video ...
```

### Q2: JSON解析错误

**A:** 确保JSON格式正确：
```powershell
# ✅ 正确：使用双引号
--bbox "[[150, 150, 250, 250]]"

# ❌ 错误：使用单引号（PowerShell中单引号是字面量）
--bbox '[[150, 150, 250, 250]]'
```

### Q3: 路径包含空格

**A:** 用引号括起来：
```powershell
python member_b_track_anything.py --video "C:\My Videos\test.mp4" --bbox "[[150, 150, 250, 250]]"
```

## 💡 推荐做法

**最简单的方式：使用Python代码**

创建 `test.py`：
```python
from member_b_track_anything import MemberBTrackAnything

module = MemberBTrackAnything()
mask_path, masks = module.process_video(
    'inputs/object_removal/bmx-trees',
    [[150, 150, 250, 250]]
)
print(f'✓ 成功生成 {len(masks)} 个掩码')
```

然后运行：
```powershell
python test.py
```

这样就不需要处理命令行参数了！


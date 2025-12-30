# 示例代码

## 测试成员B模块

```bash
# 确保在 video_object_removal 目录下
cd video_object_removal

# 修改 examples/test_member_b.py 中的视频路径
# 然后运行
python examples/test_member_b.py
```

## 命令行使用示例

```bash
# 基本用法
python -m src.member_b.main \
    --video inputs/object_removal/bmx-trees \
    --bbox "[[180,60,285,181]]" \
    --output results/masks
```

## 调试示例

```bash
# 使用调试工具
python src/tools/debug_mask.py \
    --video inputs/object_removal/bmx-trees \
    --bbox "[180,60,285,181]" \
    --output debug_output
```


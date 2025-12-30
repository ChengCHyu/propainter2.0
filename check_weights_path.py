import os

# 模拟video_processor.py中的路径计算
# video_processor.py在 video_object_removal_web/ 目录下
video_processor_path = os.path.join('video_object_removal_web', 'video_processor.py')
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(video_processor_path)))
weights_dir = os.path.join(parent_dir, 'weights')

print(f"项目根目录: {parent_dir}")
print(f"weights目录: {weights_dir}")
print()

# 检查需要的文件
required_files = ['recurrent_flow_completion.pth', 'ProPainter.pth']
print("检查模型文件:")
for filename in required_files:
    filepath = os.path.join(weights_dir, filename)
    exists = os.path.exists(filepath)
    status = "✓ 存在" if exists else "✗ 不存在"
    print(f"  {status}: {filename}")
    if exists:
        size = os.path.getsize(filepath) / (1024 * 1024)  # MB
        print(f"    大小: {size:.2f} MB")
    else:
        print(f"    路径: {filepath}")









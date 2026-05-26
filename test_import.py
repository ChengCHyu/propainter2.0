"""
测试导入链 - 找出具体是哪个模块导入失败
"""
import sys
import os

project_root = r"F:\创新实践作业\videopureVideo"
sys.path.insert(0, project_root)

# 清理cv2路径
_cleaned = [p for p in sys.path if not p.replace('\\','/').rstrip('/').endswith('/cv2')]
sys.path = _cleaned

print("=" * 60)
print("测试导入链")
print("=" * 60)

# 测试1: cv2
print("\n[1] 测试 import cv2...")
try:
    import cv2
    print(f"    ✓ cv2 导入成功, 版本: {cv2.__version__}")
except Exception as e:
    print(f"    ✗ cv2 导入失败: {e}")
    sys.exit(1)

# 测试2: torch
print("\n[2] 测试 import torch...")
try:
    import torch
    print(f"    ✓ torch 导入成功, 版本: {torch.__version__}")
except Exception as e:
    print(f"    ✗ torch 导入失败: {e}")
    sys.exit(1)

# 测试3: numpy
print("\n[3] 测试 import numpy...")
try:
    import numpy
    print(f"    ✓ numpy 导入成功, 版本: {numpy.__version__}")
except Exception as e:
    print(f"    ✗ numpy 导入失败: {e}")
    sys.exit(1)

# 测试4: segment_anything
print("\n[4] 测试 from segment_anything import sam_model_registry...")
try:
    from segment_anything import sam_model_registry
    print("    ✓ segment_anything 导入成功")
except Exception as e:
    print(f"    ✗ segment_anything 导入失败: {e}")
    print("    请运行: pip install segment-anything")

# 测试5: omegaconf
print("\n[5] 测试 import omegaconf...")
try:
    from omegaconf import OmegaConf
    print("    ✓ omegaconf 导入成功")
except Exception as e:
    print(f"    ✗ omegaconf 导入失败: {e}")
    print("    请运行: pip install omegaconf")

# 测试6: 依赖模块
print("\n[6] 测试 dependencies 导入...")
deps_path = os.path.join(project_root, 'video_object_removal', 'src', 'dependencies')
if os.path.exists(deps_path):
    sys.path.insert(0, deps_path)
    try:
        from tools.interact_tools import SamControler
        print("    ✓ tools.interact_tools.SamControler 导入成功")
    except Exception as e:
        print(f"    ✗ tools.interact_tools 导入失败: {e}")
    try:
        from tracker.base_tracker import BaseTracker
        print("    ✓ tracker.base_tracker.BaseTracker 导入成功")
    except Exception as e:
        print(f"    ✗ tracker.base_tracker 导入失败: {e}")
else:
    print(f"    ✗ dependencies 目录不存在: {deps_path}")

# 测试7: member_b
print("\n[7] 测试 member_b 导入...")
try:
    from member_b.segment_track import MemberBTrackAnything
    print("    ✓ member_b.segment_track.MemberBTrackAnything 导入成功")
except Exception as e:
    import traceback
    print(f"    ✗ member_b.segment_track 导入失败: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

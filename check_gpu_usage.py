"""
检查GPU使用情况的工具脚本
运行此脚本可以查看当前系统的GPU状态和PyTorch配置
"""

import torch
import os
import sys

print("=" * 60)
print("GPU使用情况检查")
print("=" * 60)
print()

# 1. 检查CUDA是否可用
print("1. PyTorch CUDA支持:")
print(f"   CUDA可用: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   CUDA版本: {torch.version.cuda}")
    print(f"   cuDNN版本: {torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else '不可用'}")
    print(f"   GPU数量: {torch.cuda.device_count()}")
    print()
    
    # 显示每个GPU的信息
    for i in range(torch.cuda.device_count()):
        print(f"   GPU {i}:")
        print(f"     名称: {torch.cuda.get_device_name(i)}")
        props = torch.cuda.get_device_properties(i)
        print(f"     显存: {props.total_memory / 1024**3:.2f} GB")
        print(f"     计算能力: {props.major}.{props.minor}")
        print()
else:
    print("   WARNING: CUDA not available, will use CPU")
    print()

# 2. 检查当前设备
print("2. 默认设备:")
try:
    from model.misc import get_device
    device = get_device()
    print(f"   get_device() 返回: {device}")
except ImportError:
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"   默认设备: {device}")

print()

# 3. 测试GPU计算
print("3. GPU计算测试:")
if torch.cuda.is_available():
    try:
        # 创建一个张量并移到GPU
        x = torch.randn(1000, 1000).cuda()
        y = torch.randn(1000, 1000).cuda()
        z = torch.matmul(x, y)
        print("   OK: GPU computation test successful")
        print(f"   测试张量设备: {z.device}")
        print(f"   当前GPU: {torch.cuda.current_device()}")
    except Exception as e:
        print(f"   ERROR: GPU computation test failed: {e}")
else:
    print("   WARNING: Cannot test (CUDA not available)")

print()

# 4. 检查GPU内存使用
if torch.cuda.is_available():
    print("4. GPU内存使用:")
    for i in range(torch.cuda.device_count()):
        allocated = torch.cuda.memory_allocated(i) / 1024**3
        reserved = torch.cuda.memory_reserved(i) / 1024**3
        total = torch.cuda.get_device_properties(i).total_memory / 1024**3
        print(f"   GPU {i}:")
        print(f"     已分配: {allocated:.2f} GB")
        print(f"     已保留: {reserved:.2f} GB")
        print(f"     总计: {total:.2f} GB")
        print(f"     使用率: {reserved/total*100:.1f}%")
        print()

# 5. 检查环境变量
print("5. Environment variables:")
cuda_visible = os.environ.get('CUDA_VISIBLE_DEVICES', 'Not set')
print(f"   CUDA_VISIBLE_DEVICES: {cuda_visible}")

print()
print("=" * 60)
print("总结:")
if torch.cuda.is_available():
    print("OK: System supports GPU, can use CUDA acceleration")
    print("   If program runs slowly, check if GPU is actually being used")
    print("   Check program output, should show device information")
else:
    print("WARNING: System does not support GPU, will use CPU")
    print("  如果需要使用GPU，请：")
    print("  1. 安装NVIDIA驱动")
    print("  2. 安装CUDA版本的PyTorch")
print("=" * 60)


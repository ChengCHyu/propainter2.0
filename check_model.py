"""
检查模型文件完整性
"""

import os
import sys

def check_file_size(filepath, expected_size_mb=None):
    """检查文件大小"""
    if not os.path.exists(filepath):
        return False, f"文件不存在: {filepath}"
    
    size_bytes = os.path.getsize(filepath)
    size_mb = size_bytes / (1024 * 1024)
    
    if expected_size_mb:
        if abs(size_mb - expected_size_mb) > 10:  # 允许10MB误差
            return False, f"文件大小异常: {size_mb:.2f}MB (期望: {expected_size_mb}MB)"
    
    return True, f"文件大小正常: {size_mb:.2f}MB"


def check_sam_model(filepath='weights/sam_vit_h_4b8939.pth'):
    """检查SAM模型文件"""
    print(f"检查SAM模型: {filepath}")
    
    exists, msg = check_file_size(filepath, expected_size_mb=2400)  # vit_h约2.4GB
    print(f"  {msg}")
    
    if not exists:
        return False
    
    # 尝试加载检查
    try:
        import torch
        print("  尝试加载模型文件...")
        checkpoint = torch.load(filepath, map_location='cpu')
        print("  ✓ 模型文件可以正常加载")
        return True
    except Exception as e:
        print(f"  ✗ 模型文件损坏: {e}")
        return False


def check_cutie_model(filepath='weights/cutie-base-mega.pth'):
    """检查CUTIE模型文件"""
    print(f"检查CUTIE模型: {filepath}")
    
    exists, msg = check_file_size(filepath)
    print(f"  {msg}")
    
    if not exists:
        return False
    
    # 尝试加载检查
    try:
        import torch
        print("  尝试加载模型文件...")
        checkpoint = torch.load(filepath, map_location='cpu')
        print("  ✓ 模型文件可以正常加载")
        return True
    except Exception as e:
        print(f"  ✗ 模型文件损坏: {e}")
        return False


def main():
    print("="*60)
    print("检查模型文件完整性")
    print("="*60)
    
    sam_ok = check_sam_model()
    print()
    cutie_ok = check_cutie_model()
    
    print()
    print("="*60)
    if sam_ok and cutie_ok:
        print("✓ 所有模型文件正常")
    else:
        print("✗ 发现损坏的模型文件")
        print("\n解决方法:")
        if not sam_ok:
            print("  1. 删除损坏的SAM模型文件")
            print("  2. 重新下载: python download_models.py --sam")
        if not cutie_ok:
            print("  1. 删除损坏的CUTIE模型文件")
            print("  2. 重新下载: python download_models.py --cutie")
    print("="*60)


if __name__ == '__main__':
    main()



# 检查GPU状态和显存使用情况

import torch
import subprocess
import sys

print("=" * 60)
print("GPU状态检查")
print("=" * 60)

# 1. PyTorch信息
print("\n1. PyTorch CUDA支持:")
print(f"   PyTorch版本: {torch.__version__}")
print(f"   CUDA可用: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"   CUDA版本: {torch.version.cuda}")
    print(f"   cuDNN版本: {torch.backends.cudnn.version()}")
    print(f"   GPU数量: {torch.cuda.device_count()}")
    
    # GPU详细信息
    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        print(f"\n   GPU {i}:")
        print(f"     名称: {props.name}")
        total_mem = props.total_memory / (1024**3)
        print(f"     总显存: {total_mem:.2f} GB")
        print(f"     计算能力: {props.major}.{props.minor}")
    
    # 显存使用情况
    print("\n2. PyTorch显存使用:")
    for i in range(torch.cuda.device_count()):
        allocated = torch.cuda.memory_allocated(i) / (1024**3)
        reserved = torch.cuda.memory_reserved(i) / (1024**3)
        total = torch.cuda.get_device_properties(i).total_memory / (1024**3)
        print(f"   GPU {i}:")
        print(f"     PyTorch已分配: {allocated:.2f} GB")
        print(f"     PyTorch已保留: {reserved:.2f} GB")
        print(f"     总显存: {total:.2f} GB")
        print(f"     系统占用: {total - allocated:.2f} GB (其他程序)")
    
    # 3. nvidia-smi信息
    print("\n3. nvidia-smi信息:")
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu', 
                                 '--format=csv,noheader,nounits'], 
                               capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for i, line in enumerate(lines):
                parts = line.split(', ')
                if len(parts) >= 3:
                    used = int(parts[0]) / 1024
                    total = int(parts[1]) / 1024
                    util = parts[2].strip()
                    print(f"   GPU {i}:")
                    print(f"     系统显示显存使用: {used:.2f} GB / {total:.2f} GB")
                    print(f"     GPU利用率: {util}")
    except Exception as e:
        print(f"   无法获取nvidia-smi信息: {e}")

print("\n" + "=" * 60)
print("总结:")
if torch.cuda.is_available():
    allocated = torch.cuda.memory_allocated(0) / (1024**3)
    if allocated < 0.1:
        print("OK: PyTorch几乎未使用显存（正常）")
        print("  系统显示的显存占用主要来自：")
        print("  - 系统UI进程（dwm.exe, explorer.exe等）")
        print("  - 浏览器和其他图形应用")
        print("  - 壁纸引擎等应用")
    else:
        print(f"WARNING: PyTorch正在使用 {allocated:.2f} GB 显存")
        print("  可能正在运行模型推理或训练")
else:
    print("ERROR: CUDA不可用，GPU无法使用")

print("=" * 60)






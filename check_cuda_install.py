"""
Check CUDA installation and PyTorch CUDA support
"""

import os
import sys

print("=" * 60)
print("CUDA Installation Check")
print("=" * 60)
print()

# 1. Check environment variables
print("1. Environment Variables:")
cuda_path = os.environ.get('CUDA_PATH', 'Not set')
cuda_home = os.environ.get('CUDA_HOME', 'Not set')
print(f"   CUDA_PATH: {cuda_path}")
print(f"   CUDA_HOME: {cuda_home}")

# Check CUDA paths in PATH
path_env = os.environ.get('PATH', '')
cuda_in_path = [p for p in path_env.split(os.pathsep) if 'cuda' in p.lower() or 'CUDA' in p]
if cuda_in_path:
    print(f"   CUDA paths in PATH:")
    for p in cuda_in_path[:5]:  # Show first 5
        print(f"     - {p}")
else:
    print("   No CUDA paths found in PATH")
print()

# 2. Check common CUDA installation paths
print("2. Checking Common CUDA Installation Paths:")
common_paths = [
    r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA",
    r"C:\Program Files (x86)\NVIDIA GPU Computing Toolkit\CUDA",
    r"E:\CUDA",
    r"E:\NVIDIA\CUDA",
    r"E:\Program Files\NVIDIA GPU Computing Toolkit\CUDA",
    r"E:\Program Files (x86)\NVIDIA GPU Computing Toolkit\CUDA",
    r"E:\NVIDIA",
]

found_cuda = []
for base_path in common_paths:
    if os.path.exists(base_path):
        print(f"   OK: Found {base_path}")
        # List subdirectories (usually version numbers)
        try:
            subdirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
            for subdir in subdirs[:5]:  # Show first 5
                full_path = os.path.join(base_path, subdir)
                bin_path = os.path.join(full_path, 'bin', 'nvcc.exe')
                if os.path.exists(bin_path):
                    print(f"      Version: {subdir} (nvcc.exe exists)")
                    found_cuda.append(full_path)
                elif os.path.isdir(full_path):
                    # Check if it's a version directory
                    if os.path.exists(os.path.join(full_path, 'bin')):
                        print(f"      Directory: {subdir}")
        except Exception as e:
            pass
    else:
        print(f"   Not found: {base_path}")

if not found_cuda:
    print("   No CUDA installation directories found")
print()

# 3. Check PyTorch CUDA support
print("3. PyTorch CUDA Support:")
try:
    import torch
    print(f"   PyTorch version: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"   CUDA version in PyTorch: {torch.version.cuda}")
        print(f"   cuDNN version: {torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else 'Not available'}")
        print(f"   GPU count: {torch.cuda.device_count()}")
        if torch.cuda.device_count() > 0:
            print(f"   GPU name: {torch.cuda.get_device_name(0)}")
    else:
        print("   WARNING: PyTorch cannot use CUDA")
        print("   Reason: PyTorch is CPU-only version (see version: +cpu)")
        print("   Solution: Install CUDA version of PyTorch")
except ImportError:
    print("   ERROR: PyTorch not installed")
print()

# 4. Check nvcc command
print("4. Check nvcc command:")
try:
    import subprocess
    result = subprocess.run(['nvcc', '--version'], 
                          capture_output=True, 
                          text=True, 
                          timeout=5)
    if result.returncode == 0:
        print("   OK: nvcc command is available")
        # Extract version info
        for line in result.stdout.split('\n'):
            if 'release' in line.lower():
                print(f"   {line.strip()}")
    else:
        print("   ERROR: nvcc command failed")
except FileNotFoundError:
    print("   WARNING: nvcc command not found (may not be in PATH)")
except Exception as e:
    print(f"   ERROR: {e}")
print()

# 5. Recommendations
print("=" * 60)
print("Recommendations:")
print("=" * 60)

try:
    import torch
    if not torch.cuda.is_available():
        print("Current PyTorch version: " + torch.__version__)
        print("This is a CPU-only version (indicated by '+cpu' in version)")
        print()
        print("To use GPU, you need to install CUDA version of PyTorch:")
        print()
        print("Step 1: Find your CUDA version")
        print("  - Check the CUDA directories found above")
        print("  - Or run: nvcc --version (if available)")
        print()
        print("Step 2: Install matching PyTorch version:")
        print("  CUDA 11.8: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
        print("  CUDA 12.1: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
        print("  CUDA 12.4: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124")
        print()
        print("Step 3: Verify installation:")
        print("  python -c \"import torch; print('CUDA:', torch.cuda.is_available())\"")
except ImportError:
    print("Need to install PyTorch first")

print("=" * 60)








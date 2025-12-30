"""
工具函数：设备检测和文件下载
不依赖ProPainter核心代码
"""

import torch
import os
from torch.hub import download_url_to_file


def get_device():
    """获取可用设备"""
    return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def load_file_from_url(url, model_dir, progress=True, file_name=None):
    """
    从URL下载文件
    
    Args:
        url: 下载URL
        model_dir: 保存目录
        progress: 是否显示进度
        file_name: 文件名（可选）
    
    Returns:
        filepath: 文件路径
    """
    os.makedirs(model_dir, exist_ok=True)
    filename = file_name or os.path.basename(url)
    filepath = os.path.join(model_dir, filename)
    if not os.path.exists(filepath):
        download_url_to_file(url, filepath, progress=progress)
    return filepath










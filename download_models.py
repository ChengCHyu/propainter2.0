"""
下载成员B所需的模型文件
"""

import os
from utils.download_util import load_file_from_url

def download_sam_model(model_type='vit_h', save_dir='weights'):
    """
    下载SAM模型
    
    Args:
        model_type: 模型类型 ('vit_h', 'vit_l', 'vit_b')
        save_dir: 保存目录
    """
    sam_checkpoint_url_dict = {
        'vit_h': "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
        'vit_l': "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
        'vit_b': "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    }
    
    if model_type not in sam_checkpoint_url_dict:
        raise ValueError(f"不支持的模型类型: {model_type}，支持: {list(sam_checkpoint_url_dict.keys())}")
    
    print(f"下载SAM模型 ({model_type})...")
    url = sam_checkpoint_url_dict[model_type]
    filename = os.path.basename(url)
    
    checkpoint_path = load_file_from_url(
        url=url,
        model_dir=save_dir,
        progress=True,
        file_name=filename
    )
    
    # 验证下载的文件
    if os.path.exists(checkpoint_path):
        file_size_mb = os.path.getsize(checkpoint_path) / (1024 * 1024)
        print(f"✓ SAM模型下载完成: {checkpoint_path}")
        print(f"  文件大小: {file_size_mb:.2f} MB")
        
        # 检查文件大小是否合理
        expected_sizes = {
            'vit_h': 2400,  # ~2.4GB
            'vit_l': 1200,  # ~1.2GB
            'vit_b': 375    # ~375MB
        }
        if model_type in expected_sizes:
            expected = expected_sizes[model_type]
            if abs(file_size_mb - expected) > 50:  # 允许50MB误差
                print(f"  ⚠️  警告: 文件大小异常 (期望约{expected}MB)")
    else:
        raise FileNotFoundError(f"下载失败: {checkpoint_path}")
    
    return checkpoint_path


def download_cutie_model(save_dir='weights'):
    """
    下载CUTIE追踪器模型
    """
    pretrain_model_url = 'https://github.com/sczhou/ProPainter/releases/download/v0.1.0/'
    cutie_url = f"{pretrain_model_url}cutie-base-mega.pth"
    
    print(f"下载CUTIE追踪器模型...")
    checkpoint_path = load_file_from_url(
        url=cutie_url,
        model_dir=save_dir,
        progress=True,
        file_name='cutie-base-mega.pth'
    )
    
    print(f"✓ CUTIE模型下载完成: {checkpoint_path}")
    return checkpoint_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='下载成员B所需的模型文件')
    parser.add_argument('--sam', action='store_true', help='下载SAM模型')
    parser.add_argument('--sam_type', type=str, default='vit_h', choices=['vit_h', 'vit_l', 'vit_b'], help='SAM模型类型')
    parser.add_argument('--cutie', action='store_true', help='下载CUTIE追踪器模型')
    parser.add_argument('--all', action='store_true', help='下载所有模型')
    parser.add_argument('--save_dir', type=str, default='weights', help='保存目录')
    
    args = parser.parse_args()
    
    os.makedirs(args.save_dir, exist_ok=True)
    
    if args.all:
        print("="*60)
        print("下载所有模型...")
        print("="*60)
        download_sam_model(args.sam_type, args.save_dir)
        download_cutie_model(args.save_dir)
        print("="*60)
        print("✓ 所有模型下载完成！")
        print("="*60)
    else:
        if args.sam:
            download_sam_model(args.sam_type, args.save_dir)
        if args.cutie:
            download_cutie_model(args.save_dir)
        
        if not args.sam and not args.cutie:
            print("请指定要下载的模型:")
            print("  --sam     下载SAM模型")
            print("  --cutie   下载CUTIE模型")
            print("  --all     下载所有模型")
            print("\n示例:")
            print("  python download_models.py --all")
            print("  python download_models.py --sam --sam_type vit_h")


if __name__ == '__main__':
    main()


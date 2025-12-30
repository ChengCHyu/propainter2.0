"""
测试成员B模块的示例脚本
"""

import os
import sys

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, os.path.join(project_root, 'src'))

from member_b.segment_track import MemberBTrackAnything


def main():
    """测试成员B模块"""
    print("="*60)
    print("测试成员B：分割与追踪模块")
    print("="*60)
    
    # 初始化模块
    print("\n[1] 初始化模块...")
    module = MemberBTrackAnything()
    
    # 准备输入（需要根据实际路径调整）
    video_path = '../inputs/object_removal/bmx-trees'  # 相对路径
    bboxes = [[180, 60, 285, 181]]  # 示例边界框
    
    print(f"\n[2] 输入:")
    print(f"  视频路径: {video_path}")
    print(f"  边界框: {bboxes}")
    
    # 处理视频
    print(f"\n[3] 处理视频...")
    try:
        output_path, masks = module.process_video(
            video_path=video_path,
            bboxes=bboxes,
            output_mask_path='../results/test_output'
        )
        
        print(f"\n[4] 结果:")
        print(f"  输出路径: {output_path}")
        print(f"  掩码数量: {len(masks)}")
        print("\n✓ 测试成功！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

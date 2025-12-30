"""
成员B的API接口
提供给成员A调用的接口，接收边界框，返回掩码视频
"""

import os
import json
import numpy as np
from typing import List, Dict, Union
# 优先使用基于Track-Anything的实现
try:
    from member_b_track_anything import MemberBTrackAnything as SegmentAndTrackModule
except ImportError:
    # 如果Track-Anything版本不可用，回退到原始实现
    from member_b_segment_track import SegmentAndTrackModule


class MemberBAPI:
    """
    成员B的API接口类
    提供简单的函数接口供其他成员调用
    """
    
    def __init__(self, 
                 sam_checkpoint: str = None,
                 tracker_checkpoint: str = None,
                 device: str = None):
        """
        初始化API
        
        Args:
            sam_checkpoint: SAM模型权重路径
            tracker_checkpoint: 追踪器权重路径
            device: 设备
        """
        self.module = SegmentAndTrackModule(
            sam_checkpoint=sam_checkpoint,
            tracker_checkpoint=tracker_checkpoint,
            device=device
        )
        print("[成员B API] 初始化完成")
    
    def process(self,
                video_path: str,
                bboxes: Union[List[List[float]], Dict[int, List[List[float]]]],
                output_path: str = None) -> Dict:
        """
        处理视频的主要接口
        
        Args:
            video_path: 视频路径
            bboxes: 边界框，格式：
                   - List[List[float]]: 第一帧的边界框列表，每个bbox为 [x1, y1, x2, y2]
                   - Dict[int, List[List[float]]]: 帧索引到边界框列表的映射
            output_path: 输出路径（可选）
        
        Returns:
            result: 结果字典，包含：
                   - 'output_path': 输出路径
                   - 'mask_count': 掩码数量
                   - 'masks': 掩码列表（可选，如果视频很长可能不返回）
                   - 'status': 状态 ('success' 或 'error')
                   - 'message': 消息
        """
        try:
            output_path, masks = self.module.process_video(
                video_path=video_path,
                bboxes=bboxes,
                output_mask_path=output_path,
                save_frames=True
            )
            
            return {
                'status': 'success',
                'output_path': output_path,
                'mask_count': len(masks),
                'message': f'成功生成 {len(masks)} 个掩码帧'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'处理失败: {str(e)}',
                'output_path': None,
                'mask_count': 0
            }
    
    def process_from_json(self,
                         video_path: str,
                         bbox_json_path: str,
                         output_path: str = None) -> Dict:
        """
        从JSON文件读取边界框并处理
        
        Args:
            video_path: 视频路径
            bbox_json_path: 边界框JSON文件路径
            output_path: 输出路径
        
        Returns:
            result: 结果字典
        """
        # 读取JSON文件
        with open(bbox_json_path, 'r', encoding='utf-8') as f:
            bboxes = json.load(f)
        
        return self.process(video_path, bboxes, output_path)
    
    def get_mask_path(self, output_path: str, frame_idx: int) -> str:
        """
        获取指定帧的掩码路径
        
        Args:
            output_path: 输出路径
            frame_idx: 帧索引
        
        Returns:
            mask_path: 掩码文件路径
        """
        return os.path.join(output_path, f"{frame_idx:05d}.png")


# 全局API实例（可选，用于单例模式）
_global_api = None


def get_api(sam_checkpoint: str = None,
            tracker_checkpoint: str = None,
            device: str = None) -> MemberBAPI:
    """
    获取全局API实例（单例模式）
    
    Args:
        sam_checkpoint: SAM模型权重路径
        tracker_checkpoint: 追踪器权重路径
        device: 设备
    
    Returns:
        api: MemberBAPI实例
    """
    global _global_api
    if _global_api is None:
        _global_api = MemberBAPI(
            sam_checkpoint=sam_checkpoint,
            tracker_checkpoint=tracker_checkpoint,
            device=device
        )
    return _global_api


def process_video(video_path: str,
                  bboxes: Union[List[List[float]], Dict[int, List[List[float]]]],
                  output_path: str = None,
                  sam_checkpoint: str = None,
                  tracker_checkpoint: str = None,
                  device: str = None) -> Dict:
    """
    便捷函数：处理视频
    
    Args:
        video_path: 视频路径
        bboxes: 边界框
        output_path: 输出路径
        sam_checkpoint: SAM模型权重路径
        tracker_checkpoint: 追踪器权重路径
        device: 设备
    
    Returns:
        result: 结果字典
    """
    api = MemberBAPI(
        sam_checkpoint=sam_checkpoint,
        tracker_checkpoint=tracker_checkpoint,
        device=device
    )
    return api.process(video_path, bboxes, output_path)


if __name__ == '__main__':
    """
    测试API
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='成员B API测试')
    parser.add_argument('--video', type=str, required=True, help='视频路径')
    parser.add_argument('--bbox', type=str, required=True, help='边界框JSON文件路径')
    parser.add_argument('--output', type=str, default=None, help='输出路径')
    
    args = parser.parse_args()
    
    # 创建API实例
    api = MemberBAPI()
    
    # 处理视频
    result = api.process_from_json(args.video, args.bbox, args.output)
    
    # 打印结果
    print("\n" + "="*50)
    print("处理结果:")
    print(f"状态: {result['status']}")
    print(f"消息: {result['message']}")
    if result['status'] == 'success':
        print(f"输出路径: {result['output_path']}")
        print(f"掩码数量: {result['mask_count']}")
    print("="*50)


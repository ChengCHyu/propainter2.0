"""
成员B模块的命令行入口
"""

import sys
import os

# 添加src目录到路径
src_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, src_root)

from member_b.segment_track import MemberBTrackAnything
import json
import argparse


def main():
    parser = argparse.ArgumentParser(description='成员B：分割与追踪模块')
    parser.add_argument('--video', type=str, required=True, help='输入视频路径（文件或文件夹）')
    parser.add_argument('--bbox', type=str, required=True, help='边界框JSON文件路径或JSON字符串')
    parser.add_argument('--output', type=str, default=None, help='输出掩码文件夹路径')
    parser.add_argument('--sam_checkpoint', type=str, default=None, help='SAM模型权重路径')
    parser.add_argument('--tracker_checkpoint', type=str, default=None, help='追踪器权重路径')
    parser.add_argument('--device', type=str, default=None, help='设备 (cuda:0, cpu等)')
    
    args = parser.parse_args()
    
    # 解析边界框
    if os.path.isfile(args.bbox):
        with open(args.bbox, 'r') as f:
            bboxes = json.load(f)
    else:
        # 尝试直接解析JSON字符串
        bbox_str = args.bbox.strip()
        
        # 处理各种格式
        try:
            # 方法1：标准JSON格式
            bboxes = json.loads(bbox_str)
        except:
            try:
                # 方法2：Python列表格式（去掉引号）
                if bbox_str.startswith('[') and bbox_str.endswith(']'):
                    bboxes = eval(bbox_str)
                else:
                    # 方法3：单个边界框字符串 "[x1,y1,x2,y2]"
                    bbox_str = bbox_str.strip('[]')
                    coords = [float(x.strip()) for x in bbox_str.split(',')]
                    bboxes = [coords]
            except Exception as e:
                raise ValueError(f"无法解析边界框: {args.bbox}\n错误: {e}\n请使用格式: [[x1,y1,x2,y2]] 或 [x1,y1,x2,y2]")
    
    # 验证和规范化边界框格式
    if isinstance(bboxes, list):
        # 如果第一个元素不是列表，说明是单个边界框
        if len(bboxes) > 0 and not isinstance(bboxes[0], list):
            bboxes = [bboxes]
        
        # 验证每个边界框
        normalized_bboxes = []
        for bbox in bboxes:
            if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                normalized_bboxes.append([float(x) for x in bbox])
            else:
                raise ValueError(f"边界框格式错误: {bbox}，应该是 [x1, y1, x2, y2]")
        bboxes = normalized_bboxes
    else:
        raise ValueError(f"边界框应该是列表格式，当前是: {type(bboxes)}")
    
    print(f"[成员B] 解析到 {len(bboxes)} 个边界框: {bboxes}")
    
    # 初始化模块
    module = MemberBTrackAnything(
        sam_checkpoint=args.sam_checkpoint,
        tracker_checkpoint=args.tracker_checkpoint,
        device=args.device
    )
    
    # 处理视频
    output_path, masks = module.process_video(
        video_path=args.video,
        bboxes=bboxes,
        output_mask_path=args.output
    )
    
    print(f"\n[成员B] 处理完成！")
    print(f"输出路径: {output_path}")
    print(f"生成掩码数量: {len(masks)}")


if __name__ == '__main__':
    main()



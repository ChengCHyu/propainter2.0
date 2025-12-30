"""
端到端流程：语音输入 → 文本 → 边界框 → 掩码 → ProPainter修复

完整流程：
1. 成员D：语音输入 → 文本（"删除视频中的汽车"）
2. 成员A：文本 → 边界框（GroundingDINO定位）
3. 成员B：边界框 → 掩码（SAM分割 + CUTIE追踪）
4. 成员C：掩码 + 视频 → 修复视频（ProPainter）

本脚本演示完整流程，成员B可以直接使用
"""

import os
import sys
import json
import cv2
import numpy as np
import argparse
from pathlib import Path

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# 导入成员B模块
from member_b_track_anything import MemberBTrackAnything

# 导入ProPainter（成员C）
try:
    from inference_propainter import read_frame_from_videos, read_mask, resize_frames
    from model.modules.flow_comp_raft import RAFT_bi
    from model.recurrent_flow_completion import RecurrentFlowCompleteNet
    from model.propainter import InpaintGenerator
    from utils.download_util import load_file_from_url
    from core.utils import to_tensors
    from model.misc import get_device
    import torch
    PROPANTER_AVAILABLE = True
except ImportError as e:
    print(f"警告: ProPainter模块导入失败: {e}")
    PROPANTER_AVAILABLE = False


class EndToEndPipeline:
    """
    端到端流程类
    整合所有成员的工作
    """
    
    def __init__(self,
                 sam_checkpoint=None,
                 tracker_checkpoint=None,
                 propainter_checkpoint=None,
                 raft_checkpoint=None,
                 flow_completion_checkpoint=None,
                 device=None):
        """
        初始化端到端流程
        
        Args:
            sam_checkpoint: SAM模型权重路径
            tracker_checkpoint: CUTIE追踪器权重路径
            propainter_checkpoint: ProPainter模型权重路径
            raft_checkpoint: RAFT模型权重路径
            flow_completion_checkpoint: 流补全模型权重路径
            device: 设备
        """
        if device is None:
            device = str(get_device()) if PROPANTER_AVAILABLE else 'cuda:0'
        
        self.device = device
        print(f"[端到端流程] 初始化，设备: {self.device}")
        
        # 初始化成员B（分割与追踪）
        print("\n[步骤1] 初始化成员B：分割与追踪模块")
        self.member_b = MemberBTrackAnything(
            sam_checkpoint=sam_checkpoint,
            tracker_checkpoint=tracker_checkpoint,
            device=device
        )
        
        # 初始化成员C（ProPainter）- 可选
        self.member_c_available = False
        if PROPANTER_AVAILABLE:
            try:
                print("\n[步骤2] 初始化成员C：ProPainter修复模块")
                self._init_propainter(
                    propainter_checkpoint,
                    raft_checkpoint,
                    flow_completion_checkpoint
                )
                self.member_c_available = True
            except Exception as e:
                print(f"警告: ProPainter初始化失败: {e}")
                print("将只执行到掩码生成步骤")
    
    def _init_propainter(self, propainter_checkpoint, raft_checkpoint, flow_completion_checkpoint):
        """初始化ProPainter"""
        pretrain_model_url = 'https://github.com/sczhou/ProPainter/releases/download/v0.1.0/'
        
        # RAFT
        if raft_checkpoint is None:
            raft_checkpoint = load_file_from_url(
                url=os.path.join(pretrain_model_url, 'raft-things.pth'),
                model_dir='weights',
                progress=True,
                file_name=None
            )
        self.raft = RAFT_bi(raft_checkpoint, self.device)
        
        # Flow Completion
        if flow_completion_checkpoint is None:
            flow_completion_checkpoint = load_file_from_url(
                url=os.path.join(pretrain_model_url, 'recurrent_flow_completion.pth'),
                model_dir='weights',
                progress=True,
                file_name=None
            )
        self.flow_complete = RecurrentFlowCompleteNet(flow_completion_checkpoint)
        self.flow_complete.to(self.device)
        self.flow_complete.eval()
        for p in self.flow_complete.parameters():
            p.requires_grad = False
        
        # ProPainter
        if propainter_checkpoint is None:
            propainter_checkpoint = load_file_from_url(
                url=os.path.join(pretrain_model_url, 'ProPainter.pth'),
                model_dir='weights',
                progress=True,
                file_name=None
            )
        self.propainter = InpaintGenerator(model_path=propainter_checkpoint).to(self.device)
        self.propainter.eval()
    
    def process(self,
                video_path: str,
                bboxes: list,  # 来自成员A的边界框
                output_dir: str = None,
                run_inpainting: bool = True) -> dict:
        """
        完整流程处理
        
        Args:
            video_path: 视频路径
            bboxes: 边界框列表 [[x1, y1, x2, y2], ...]
            output_dir: 输出目录
            run_inpainting: 是否运行ProPainter修复
        
        Returns:
            result: 结果字典
        """
        print("\n" + "="*60)
        print("开始端到端处理流程")
        print("="*60)
        
        if output_dir is None:
            video_name = Path(video_path).stem
            output_dir = os.path.join('results', 'pipeline', video_name)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # ========== 成员B：分割与追踪 ==========
        print("\n[成员B] 开始分割与追踪...")
        print(f"  输入: 视频={video_path}, 边界框={bboxes}")
        
        mask_output_dir = os.path.join(output_dir, 'masks')
        mask_path, masks = self.member_b.process_video(
            video_path=video_path,
            bboxes=bboxes,
            output_mask_path=mask_output_dir,
            save_frames=True
        )
        
        print(f"[成员B] 完成！掩码保存在: {mask_path}")
        print(f"  输出: {len(masks)} 个掩码帧")
        
        result = {
            'status': 'success',
            'video_path': video_path,
            'bboxes': bboxes,
            'mask_path': mask_path,
            'mask_count': len(masks),
            'masks': masks,
            'inpainted_video_path': None
        }
        
        # ========== 成员C：ProPainter修复 ==========
        if run_inpainting and self.member_c_available:
            print("\n[成员C] 开始ProPainter修复...")
            print(f"  输入: 视频={video_path}, 掩码={mask_path}")
            
            try:
                inpainted_path = self._run_propainter(
                    video_path=video_path,
                    mask_path=mask_path,
                    output_dir=os.path.join(output_dir, 'inpainted')
                )
                result['inpainted_video_path'] = inpainted_path
                print(f"[成员C] 完成！修复视频保存在: {inpainted_path}")
            except Exception as e:
                print(f"[成员C] 修复失败: {e}")
                result['inpainting_error'] = str(e)
        elif run_inpainting and not self.member_c_available:
            print("\n[成员C] ProPainter不可用，跳过修复步骤")
            print("提示: 可以使用 inference_propainter.py 手动运行修复")
            print(f"命令: python inference_propainter.py -i {video_path} -m {mask_path}")
        
        print("\n" + "="*60)
        print("端到端处理完成！")
        print("="*60)
        print(f"结果保存在: {output_dir}")
        
        return result
    
    def _run_propainter(self, video_path, mask_path, output_dir):
        """
        运行ProPainter修复（简化版本）
        完整版本请参考 inference_propainter.py
        """
        # 这里只是示例，完整实现需要参考 inference_propainter.py
        # 为了简化，我们直接调用 inference_propainter.py
        
        import subprocess
        
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [
            sys.executable,
            'inference_propainter.py',
            '-i', video_path,
            '-m', mask_path,
            '-o', output_dir
        ]
        
        print(f"运行命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        # 返回输出视频路径
        video_name = Path(video_path).stem
        return os.path.join(output_dir, video_name, 'inpaint_out.mp4')


def demo_with_mock_bboxes():
    """
    演示：使用模拟的边界框（实际应该来自成员A）
    """
    print("\n" + "="*60)
    print("演示：端到端流程（使用模拟边界框）")
    print("="*60)
    
    # 初始化流程
    pipeline = EndToEndPipeline(
        sam_checkpoint=None,  # 使用默认路径
        tracker_checkpoint=None,
        propainter_checkpoint=None,
        device=None
    )
    
    # 示例：处理视频
    video_path = 'inputs/object_removal/bmx-trees'
    
    # 模拟成员A的输出：边界框
    # 实际应该从成员A获取
    mock_bboxes = [
        [150, 150, 250, 250],  # 示例边界框，需要根据实际视频调整
    ]
    
    # 处理
    result = pipeline.process(
        video_path=video_path,
        bboxes=mock_bboxes,
        run_inpainting=False  # 先不运行修复，只生成掩码
    )
    
    print("\n处理结果:")
    print(f"  状态: {result['status']}")
    print(f"  掩码路径: {result['mask_path']}")
    print(f"  掩码数量: {result['mask_count']}")


def main():
    """
    主函数：命令行接口
    """
    parser = argparse.ArgumentParser(description='端到端流程：语音输入 → 掩码 → ProPainter')
    parser.add_argument('--video', type=str, required=True, help='输入视频路径')
    parser.add_argument('--bbox', type=str, required=True, 
                       help='边界框JSON文件路径或JSON字符串，格式: [[x1,y1,x2,y2], ...]')
    parser.add_argument('--output', type=str, default=None, help='输出目录')
    parser.add_argument('--no-inpaint', action='store_true', help='不运行ProPainter修复')
    parser.add_argument('--sam_checkpoint', type=str, default=None, help='SAM模型路径')
    parser.add_argument('--tracker_checkpoint', type=str, default=None, help='追踪器模型路径')
    parser.add_argument('--device', type=str, default=None, help='设备')
    
    args = parser.parse_args()
    
    # 解析边界框
    if os.path.isfile(args.bbox):
        with open(args.bbox, 'r') as f:
            bboxes = json.load(f)
    else:
        try:
            bboxes = json.loads(args.bbox)
        except:
            raise ValueError(f"无法解析边界框: {args.bbox}")
    
    # 初始化流程
    pipeline = EndToEndPipeline(
        sam_checkpoint=args.sam_checkpoint,
        tracker_checkpoint=args.tracker_checkpoint,
        device=args.device
    )
    
    # 处理
    result = pipeline.process(
        video_path=args.video,
        bboxes=bboxes,
        output_dir=args.output,
        run_inpainting=not args.no_inpaint
    )
    
    # 打印结果
    print("\n" + "="*60)
    print("处理完成！")
    print("="*60)
    print(f"掩码路径: {result['mask_path']}")
    if result.get('inpainted_video_path'):
        print(f"修复视频: {result['inpainted_video_path']}")
    print("="*60)


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        # 演示模式
        demo_with_mock_bboxes()
    else:
        # 命令行模式
        main()



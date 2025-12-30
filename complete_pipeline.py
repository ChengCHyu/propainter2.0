"""
完整流程：文本输入 → 边界框 → 掩码 → ProPainter修复 → 物体删除

流程步骤：
1. 成员A：文本描述 → 边界框（可选，如果提供边界框则跳过）
2. 成员B：边界框 → 掩码序列（SAM分割 + CUTIE追踪）
3. 成员C：掩码 + 视频 → 修复视频（ProPainter物体删除）
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# 导入成员A和成员B
try:
    from member_a.text_to_bbox import TextToBBox
    MEMBER_A_AVAILABLE = True
except ImportError as e:
    print(f"警告: 成员A模块导入失败: {e}")
    MEMBER_A_AVAILABLE = False

try:
    # 尝试两种导入方式
    try:
        from member_b.member_b_track_anything import MemberBTrackAnything
    except ImportError:
        # 如果失败，尝试直接导入
        sys.path.insert(0, os.path.join(project_root, 'member_b'))
        from member_b_track_anything import MemberBTrackAnything
    MEMBER_B_AVAILABLE = True
except ImportError as e:
    print(f"警告: 成员B模块导入失败: {e}")
    MEMBER_B_AVAILABLE = False


def parse_bbox(bbox_input):
    """
    解析边界框输入（JSON文件路径或JSON字符串）
    """
    if os.path.isfile(bbox_input):
        with open(bbox_input, 'r', encoding='utf-8') as f:
            bboxes = json.load(f)
    else:
        # 尝试解析JSON字符串
        bbox_str = bbox_input.strip()
        try:
            bboxes = json.loads(bbox_str)
        except:
            try:
                # 尝试eval（谨慎使用）
                if bbox_str.startswith('[') and bbox_str.endswith(']'):
                    bboxes = eval(bbox_str)
                else:
                    # 单个边界框 "[x1,y1,x2,y2]"
                    bbox_str = bbox_str.strip('[]')
                    coords = [float(x.strip()) for x in bbox_str.split(',')]
                    bboxes = [coords]
            except Exception as e:
                raise ValueError(f"无法解析边界框: {bbox_input}\n错误: {e}")
    
    # 规范化格式
    if isinstance(bboxes, list):
        if len(bboxes) > 0 and not isinstance(bboxes[0], list):
            bboxes = [bboxes]
        # 验证每个边界框
        normalized_bboxes = []
        for bbox in bboxes:
            if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                normalized_bboxes.append([float(x) for x in bbox])
            else:
                raise ValueError(f"边界框格式错误: {bbox}，应该是 [x1, y1, x2, y2]")
        return normalized_bboxes
    else:
        raise ValueError(f"边界框应该是列表格式，当前是: {type(bboxes)}")


def step1_text_to_bbox(video_path, text_prompt, output_bbox_file=None):
    """
    步骤1：成员A - 文本到边界框
    """
    if not MEMBER_A_AVAILABLE:
        raise RuntimeError("成员A模块不可用，无法执行文本到边界框转换")
    
    print("\n" + "="*60)
    print("步骤1：成员A - 文本到边界框")
    print("="*60)
    print(f"视频路径: {video_path}")
    print(f"文本提示: {text_prompt}")
    
    # 初始化成员A
    module_a = TextToBBox()
    
    # 处理视频第一帧
    bboxes = module_a.process_video_first_frame(
        video_path=video_path,
        text_prompt=text_prompt
    )
    
    if len(bboxes) == 0:
        raise RuntimeError("未检测到任何目标物体，请检查文本提示是否正确")
    
    print(f"\n检测到 {len(bboxes)} 个目标物体:")
    for i, bbox in enumerate(bboxes):
        print(f"  物体{i+1}: {bbox}")
    
    # 保存边界框
    if output_bbox_file:
        os.makedirs(os.path.dirname(output_bbox_file) or '.', exist_ok=True)
        module_a.save_bboxes_json(bboxes, output_bbox_file)
        print(f"\n边界框已保存到: {output_bbox_file}")
    
    return bboxes


def step2_bbox_to_mask(video_path, bboxes, output_mask_dir=None):
    """
    步骤2：成员B - 边界框到掩码
    """
    if not MEMBER_B_AVAILABLE:
        raise RuntimeError("成员B模块不可用，无法执行分割与追踪")
    
    print("\n" + "="*60)
    print("步骤2：成员B - 边界框到掩码")
    print("="*60)
    print(f"视频路径: {video_path}")
    print(f"边界框: {bboxes}")
    
    # 初始化成员B
    module_b = MemberBTrackAnything()
    
    # 处理视频
    mask_path, masks = module_b.process_video(
        video_path=video_path,
        bboxes=bboxes,
        output_mask_path=output_mask_dir,
        save_frames=True
    )
    
    print(f"\n生成 {len(masks)} 个掩码帧")
    print(f"掩码保存在: {mask_path}")
    
    return mask_path, masks


def step3_mask_to_inpaint(video_path, mask_path, output_dir=None, **propainter_args):
    """
    步骤3：成员C - 掩码到修复视频（ProPainter）
    """
    print("\n" + "="*60)
    print("步骤3：成员C - ProPainter修复")
    print("="*60)
    print(f"视频路径: {video_path}")
    print(f"掩码路径: {mask_path}")
    
    # 清理mask目录中的非PNG文件（如mask_video.mp4）
    # ProPainter的read_mask函数会尝试读取目录中的所有文件
    mask_video_path = os.path.join(mask_path, 'mask_video.mp4')
    if os.path.exists(mask_video_path):
        print(f"清理临时文件: {mask_video_path}")
        try:
            os.remove(mask_video_path)
        except Exception as e:
            print(f"警告: 无法删除 {mask_video_path}: {e}")
    
    # 构建ProPainter命令
    cmd = [
        sys.executable,
        'inference_propainter.py',
        '-i', video_path,
        '-m', mask_path,
        '-o', output_dir or 'results/inpainted'
    ]
    
    # 添加可选参数
    if 'resize_ratio' in propainter_args:
        cmd.extend(['--resize_ratio', str(propainter_args['resize_ratio'])])
    if 'mask_dilation' in propainter_args:
        cmd.extend(['--mask_dilation', str(propainter_args['mask_dilation'])])
    if 'save_fps' in propainter_args:
        cmd.extend(['--save_fps', str(propainter_args['save_fps'])])
    if propainter_args.get('save_frames', False):
        cmd.append('--save_frames')
    if propainter_args.get('fp16', False):
        cmd.append('--fp16')
    
    print(f"\n运行命令: {' '.join(cmd)}")
    
    # 执行命令（显示输出以便调试）
    try:
        result = subprocess.run(cmd, check=True)
        
        # 获取输出视频路径
        video_name = Path(video_path).stem
        output_video_path = os.path.join(output_dir or 'results/inpainted', video_name, 'inpaint_out.mp4')
        
        if os.path.exists(output_video_path):
            print(f"\n修复视频已保存到: {output_video_path}")
            return output_video_path
        else:
            print(f"\n警告: 未找到输出视频文件: {output_video_path}")
            print(f"请检查ProPainter输出目录: {os.path.join(output_dir or 'results/inpainted', video_name)}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"\n错误: ProPainter执行失败，退出码: {e.returncode}")
        print(f"\n可能的解决方案：")
        print(f"1. 检查网络连接，然后重新运行")
        print(f"2. 手动下载ProPainter模型文件到 weights/ 目录：")
        print(f"   - recurrent_flow_completion.pth")
        print(f"   - ProPainter.pth")
        print(f"   下载地址: https://github.com/sczhou/ProPainter/releases/download/v0.1.0/")
        print(f"3. 使用 --skip-inpaint 参数跳过ProPainter步骤，只生成掩码")
        raise RuntimeError(f"ProPainter执行失败，退出码: {e.returncode}。请检查上方的错误输出。")


def main():
    """
    主函数：完整流程
    """
    parser = argparse.ArgumentParser(
        description='完整流程：文本/边界框 → 掩码 → ProPainter修复（物体删除）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：

1. 使用文本输入（自动定位）：
   python complete_pipeline.py --video inputs/object_removal/bmx-trees --text "car"

2. 使用边界框（跳过成员A）：
   python complete_pipeline.py --video inputs/object_removal/bmx-trees --bbox "[[180, 60, 285, 181]]"

3. 使用边界框JSON文件：
   python complete_pipeline.py --video inputs/object_removal/bmx-trees --bbox results/member_a_bboxes/bboxes.json

4. 只生成掩码，不运行ProPainter：
   python complete_pipeline.py --video inputs/object_removal/bmx-trees --bbox "[[180, 60, 285, 181]]" --skip-inpaint

5. 使用文本输入并保存中间结果：
   python complete_pipeline.py --video inputs/object_removal/bmx-trees --text "car" --save-intermediate
        """
    )
    
    # 输入参数
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--text', type=str, help='文本提示（如"car", "删除视频中的汽车"）- 会调用成员A')
    input_group.add_argument('--bbox', type=str, help='边界框JSON文件路径或JSON字符串（格式: [[x1,y1,x2,y2], ...]）- 跳过成员A')
    
    parser.add_argument('--video', type=str, required=True, help='输入视频路径（文件或帧文件夹）')
    
    # 输出参数
    parser.add_argument('--output', type=str, default=None, help='输出目录（默认: results/pipeline/<视频名>）')
    parser.add_argument('--save-intermediate', action='store_true', help='保存中间结果（边界框、掩码等）')
    
    # ProPainter参数
    parser.add_argument('--skip-inpaint', action='store_true', help='跳过ProPainter修复步骤（只生成掩码）')
    parser.add_argument('--resize-ratio', type=float, default=1.0, help='ProPainter: 视频缩放比例')
    parser.add_argument('--mask-dilation', type=int, default=4, help='ProPainter: 掩码膨胀像素数')
    parser.add_argument('--save-fps', type=int, default=24, help='ProPainter: 输出视频帧率')
    parser.add_argument('--save-frames', action='store_true', help='ProPainter: 保存输出帧')
    parser.add_argument('--fp16', action='store_true', help='ProPainter: 使用FP16精度（节省显存）')
    
    # 模型路径（可选）
    parser.add_argument('--sam-checkpoint', type=str, default=None, help='SAM模型路径')
    parser.add_argument('--tracker-checkpoint', type=str, default=None, help='追踪器模型路径')
    parser.add_argument('--device', type=str, default=None, help='设备 (cuda:0, cpu等)')
    
    args = parser.parse_args()
    
    # 确定输出目录
    video_name = Path(args.video).stem
    if args.output:
        output_dir = args.output
    else:
        output_dir = os.path.join('results', 'pipeline', video_name)
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print("完整流程：物体删除")
    print("="*60)
    print(f"视频路径: {args.video}")
    print(f"输出目录: {output_dir}")
    print("="*60)
    
    try:
        # ========== 步骤1：文本到边界框（可选）==========
        if args.text:
            # 使用文本输入，调用成员A
            bbox_file = os.path.join(output_dir, 'bboxes.json') if args.save_intermediate else None
            bboxes = step1_text_to_bbox(
                video_path=args.video,
                text_prompt=args.text,
                output_bbox_file=bbox_file
            )
        else:
            # 使用提供的边界框，跳过成员A
            print("\n跳过步骤1（成员A），使用提供的边界框")
            bboxes = parse_bbox(args.bbox)
            print(f"边界框: {bboxes}")
            
            # 保存边界框（如果启用）
            if args.save_intermediate:
                bbox_file = os.path.join(output_dir, 'bboxes.json')
                os.makedirs(os.path.dirname(bbox_file) or '.', exist_ok=True)
                with open(bbox_file, 'w', encoding='utf-8') as f:
                    json.dump(bboxes, f, indent=2)
                print(f"边界框已保存到: {bbox_file}")
        
        # ========== 步骤2：边界框到掩码 ==========
        mask_dir = os.path.join(output_dir, 'masks') if args.save_intermediate else None
        mask_path, masks = step2_bbox_to_mask(
            video_path=args.video,
            bboxes=bboxes,
            output_mask_dir=mask_dir
        )
        
        # ========== 步骤3：掩码到修复视频（可选）==========
        if not args.skip_inpaint:
            propainter_args = {
                'resize_ratio': args.resize_ratio,
                'mask_dilation': args.mask_dilation,
                'save_fps': args.save_fps,
                'save_frames': args.save_frames,
                'fp16': args.fp16
            }
            
            output_video_path = step3_mask_to_inpaint(
                video_path=args.video,
                mask_path=mask_path,
                output_dir=os.path.join(output_dir, 'inpainted'),
                **propainter_args
            )
        else:
            print("\n跳过步骤3（ProPainter修复）")
            output_video_path = None
        
        # ========== 完成 ==========
        print("\n" + "="*60)
        print("完整流程执行成功！")
        print("="*60)
        print(f"输出目录: {output_dir}")
        print(f"掩码路径: {mask_path}")
        if output_video_path:
            print(f"修复视频: {output_video_path}")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"错误: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()


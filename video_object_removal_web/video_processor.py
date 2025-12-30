"""
视频处理API包装器
隐藏内部实现细节，提供干净的接口
包含完整的处理流程：生成掩码 + ProPainter修复
"""

import os
import sys
import subprocess
from contextlib import contextmanager
from io import StringIO
from pathlib import Path

# 添加父目录到路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    from member_b.member_b_track_anything import MemberBTrackAnything
except ImportError:
    try:
        sys.path.insert(0, os.path.join(parent_dir, 'member_b'))
        from member_b_track_anything import MemberBTrackAnything
    except ImportError:
        MemberBTrackAnything = None


class VideoProcessor:
    """
    视频处理器 - 隐藏内部实现细节
    """
    
    def __init__(self, suppress_output=True):
        """
        初始化处理器
        
        Args:
            suppress_output: 是否抑制内部输出信息
        """
        if MemberBTrackAnything is None:
            raise RuntimeError("处理模块不可用，请检查依赖")
        
        self.suppress_output = suppress_output
        self.processor = None
    
    def _get_processor(self):
        """获取或创建处理器实例"""
        if self.processor is None:
            with self._suppress_stdout() if self.suppress_output else self._noop():
                self.processor = MemberBTrackAnything()
            # 打印设备信息（即使suppress_output=True也显示，因为这对用户很重要）
            device_info = self.processor.device if hasattr(self.processor, 'device') else 'unknown'
            print(f"[VideoProcessor] Member B 使用设备: {device_info}")
        return self.processor
    
    @contextmanager
    def _suppress_stdout(self):
        """临时抑制标准输出"""
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            yield
        finally:
            sys.stdout = old_stdout
    
    @contextmanager
    def _noop(self):
        """空上下文管理器"""
        yield
    
    def process(self, video_path, bboxes, output_dir, start_frame=0):
        """
        处理视频：生成掩码 + ProPainter修复
        
        Args:
            video_path: 视频文件路径
            bboxes: 边界框列表 [[x1, y1, x2, y2], ...]
            output_dir: 输出目录
            start_frame: 起始帧索引（默认0，即第一帧）
        
        Returns:
            dict: 处理结果
                - video_path: 修复后的视频路径
                - status: 状态
        """
        try:
            proc = self._get_processor()
            
            # 确保output_dir是绝对路径
            output_dir = os.path.abspath(output_dir)
            os.makedirs(output_dir, exist_ok=True)
            
            # 步骤1：生成掩码
            mask_dir = os.path.join(output_dir, 'masks')
            mask_dir = os.path.abspath(mask_dir)  # 确保是绝对路径
            os.makedirs(mask_dir, exist_ok=True)
            
            # 确保video_path是绝对路径
            video_path = os.path.abspath(video_path)
            
            with self._suppress_stdout() if self.suppress_output else self._noop():
                mask_path, masks = proc.process_video(
                    video_path=video_path,
                    bboxes=bboxes,
                    start_frame=start_frame,
                    output_mask_path=mask_dir,
                    save_frames=True
                )
            
            # 确保mask_path是绝对路径
            mask_path = os.path.abspath(mask_path)
            
            # 清理临时文件
            mask_video_path = os.path.join(mask_path, 'mask_video.mp4')
            if os.path.exists(mask_video_path):
                try:
                    os.remove(mask_video_path)
                except:
                    pass
            
            # 步骤2：运行ProPainter修复
            propainter_output_dir = os.path.join(output_dir, 'inpainted')
            os.makedirs(propainter_output_dir, exist_ok=True)
            
            # 调用ProPainter
            propainter_script = os.path.join(parent_dir, 'inference_propainter.py')
            if not os.path.exists(propainter_script):
                return {
                    'status': 'error',
                    'error': 'ProPainter脚本不存在，请确保inference_propainter.py在项目根目录'
                }
            
            # 确保所有路径都是绝对路径
            abs_video_path = os.path.abspath(video_path)
            abs_mask_path = os.path.abspath(mask_path)
            abs_output_dir = os.path.abspath(propainter_output_dir)
            
            # 构建命令
            video_name = Path(video_path).stem
            cmd = [
                sys.executable,
                propainter_script,
                '-i', abs_video_path,
                '-m', abs_mask_path,
                '-o', abs_output_dir
            ]
            
            # 检查ProPainter模型是否存在
            weights_dir = os.path.join(parent_dir, 'weights')
            required_models = [
                'recurrent_flow_completion.pth',
                'ProPainter.pth'
            ]
            missing_models = []
            for model_name in required_models:
                model_path = os.path.join(weights_dir, model_name)
                if not os.path.exists(model_path):
                    missing_models.append(model_name)
            
            if missing_models:
                model_list = ', '.join(missing_models)
                download_url = 'https://github.com/sczhou/ProPainter/releases/download/v0.1.0/'
                return {
                    'status': 'error',
                    'error': f'缺少ProPainter模型文件: {model_list}\n\n'
                            f'由于网络问题，请手动下载模型文件到 weights/ 目录：\n'
                            f'下载地址: {download_url}\n'
                            f'需要下载的文件：\n'
                            + '\n'.join(f'  - {model}' for model in missing_models) +
                            f'\n\n下载后请重新运行处理。'
                }
            
            # 运行ProPainter
            # 需要在父目录运行，因为ProPainter脚本需要访问项目根目录的资源
            # 注意：ProPainter会输出进度信息，我们让它显示出来，这样用户知道程序还在运行
            current_dir = os.getcwd()
            try:
                os.chdir(parent_dir)  # 切换到项目根目录
                # 不抑制输出，让ProPainter的进度信息显示在终端
                # 这样可以避免用户以为程序卡住了
                result = subprocess.run(cmd, text=True, capture_output=True)
            finally:
                os.chdir(current_dir)  # 恢复原目录
            
            if result.returncode != 0:
                # 检查是否是模型下载失败
                error_output = result.stderr if result.stderr else result.stdout
                if 'RemoteDisconnected' in error_output or 'download' in error_output.lower():
                    return {
                        'status': 'error',
                        'error': f'ProPainter模型下载失败（网络问题）\n\n'
                                f'请手动下载模型文件到 weights/ 目录：\n'
                                f'下载地址: https://github.com/sczhou/ProPainter/releases/download/v0.1.0/\n'
                                f'需要下载：recurrent_flow_completion.pth 和 ProPainter.pth\n\n'
                                f'详细错误信息：\n{error_output[-500:]}'
                    }
                
                return {
                    'status': 'error',
                    'error': f'ProPainter执行失败，退出码: {result.returncode}\n\n错误信息：\n{error_output[-500:]}'
                }
            
            # 查找输出视频
            output_video_path = os.path.join(propainter_output_dir, video_name, 'inpaint_out.mp4')
            if not os.path.exists(output_video_path):
                # 尝试其他可能的路径
                for root, dirs, files in os.walk(propainter_output_dir):
                    for file in files:
                        if file.endswith('.mp4') and 'inpaint' in file.lower():
                            output_video_path = os.path.join(root, file)
                            break
                    if os.path.exists(output_video_path):
                        break
            
            if not os.path.exists(output_video_path):
                return {
                    'status': 'error',
                    'error': f'未找到输出视频文件，请检查ProPainter输出目录: {propainter_output_dir}'
                }
            
            return {
                'video_path': output_video_path,
                'mask_path': mask_path,
                'status': 'success'
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'error': str(e)
            }


"""
成员B：基于Track-Anything的分割与追踪模块
独立模块，不依赖ProPainter核心代码
"""

import os
import sys
import cv2
import numpy as np
import torch
from typing import List, Tuple, Union, Dict
from tqdm import tqdm
import imageio

# 添加项目路径（用于访问dependencies中的Track-Anything）
current_dir = os.path.dirname(os.path.abspath(__file__))
src_root = os.path.dirname(current_dir)
dependencies_path = os.path.join(src_root, 'dependencies')
sys.path.insert(0, dependencies_path)

# 导入Track-Anything相关模块
from tools.interact_tools import SamControler
from tracker.base_tracker import BaseTracker

# 导入工具函数（使用本地依赖）
import sys
sys.path.insert(0, src_root)
from dependencies.utils import get_device, load_file_from_url


class MemberBTrackAnything:
    """
    基于Track-Anything的成员B模块
    
    功能：
    1. 接收边界框输入（来自成员A）
    2. 使用SAM分割第一帧
    3. 使用CUTIE追踪整个视频
    4. 输出掩码序列（给成员C）
    
    依赖：
    - SAM (Segment Anything Model)
    - CUTIE (视频追踪器)
    - Track-Anything工具模块
    
    不依赖：
    - ProPainter核心代码
    """
    
    def __init__(self,
                 sam_checkpoint: str = None,
                 sam_model_type: str = 'vit_h',
                 tracker_checkpoint: str = None,
                 device: str = None):
        """
        初始化模块
        
        Args:
            sam_checkpoint: SAM模型权重路径
            sam_model_type: SAM模型类型 ('vit_b', 'vit_l', 'vit_h')
            tracker_checkpoint: CUTIE追踪器权重路径
            device: 设备 ('cuda:0', 'cpu'等)
        """
        # 设置设备
        if device is None:
            self.device = str(get_device())
        else:
            self.device = device
        
        print(f"[成员B] 初始化Track-Anything模块，设备: {self.device}")
        
        # 初始化SAM控制器
        if sam_checkpoint is None:
            sam_checkpoint = os.environ.get('SAM_CHECKPOINT', 'weights/sam_vit_h_4b8939.pth')
        
        # 如果文件不存在，尝试自动下载
        if not os.path.exists(sam_checkpoint):
            print(f"[成员B] SAM模型文件不存在: {sam_checkpoint}")
            print(f"[成员B] 尝试自动下载...")
            
            # SAM模型下载URL
            sam_checkpoint_url_dict = {
                'vit_h': "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
                'vit_l': "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
                'vit_b': "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
            }
            
            if sam_model_type in sam_checkpoint_url_dict:
                # 确保weights目录存在
                weights_dir = os.path.dirname(sam_checkpoint) if os.path.dirname(sam_checkpoint) else 'weights'
                os.makedirs(weights_dir, exist_ok=True)
                
                # 下载模型
                sam_url = sam_checkpoint_url_dict[sam_model_type]
                print(f"[成员B] 从 {sam_url} 下载SAM模型...")
                sam_checkpoint = load_file_from_url(
                    url=sam_url,
                    model_dir=weights_dir,
                    progress=True,
                    file_name=os.path.basename(sam_checkpoint)
                )
                print(f"[成员B] SAM模型下载完成: {sam_checkpoint}")
            else:
                raise FileNotFoundError(
                    f"SAM模型文件不存在: {sam_checkpoint}\n"
                    f"请手动下载SAM模型:\n"
                    f"  vit_h: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth\n"
                    f"  vit_l: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth\n"
                    f"  vit_b: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth\n"
                    f"保存到: {sam_checkpoint}"
                )
        
        print(f"[成员B] 加载SAM模型: {sam_checkpoint}")
        self.sam_controller = SamControler(sam_checkpoint, sam_model_type, self.device)
        
        # 初始化追踪器
        if tracker_checkpoint is None:
            tracker_checkpoint = os.environ.get('TRACKER_CHECKPOINT', 'weights/cutie-base-mega.pth')
        
        # 如果文件不存在，尝试自动下载
        if not os.path.exists(tracker_checkpoint):
            print(f"[成员B] CUTIE模型文件不存在: {tracker_checkpoint}")
            print(f"[成员B] 尝试自动下载...")
            
            # CUTIE模型下载URL
            pretrain_model_url = 'https://github.com/sczhou/ProPainter/releases/download/v0.1.0/'
            cutie_url = f"{pretrain_model_url}cutie-base-mega.pth"
            
            # 确保weights目录存在
            weights_dir = os.path.dirname(tracker_checkpoint) if os.path.dirname(tracker_checkpoint) else 'weights'
            os.makedirs(weights_dir, exist_ok=True)
            
            # 下载模型
            print(f"[成员B] 从 {cutie_url} 下载CUTIE模型...")
            tracker_checkpoint = load_file_from_url(
                url=cutie_url,
                model_dir=weights_dir,
                progress=True,
                file_name=os.path.basename(tracker_checkpoint)
            )
            print(f"[成员B] CUTIE模型下载完成: {tracker_checkpoint}")
        
        print(f"[成员B] 加载CUTIE追踪器: {tracker_checkpoint}")
        self.tracker = BaseTracker(tracker_checkpoint, self.device)
        
        print(f"[成员B] 模块初始化完成")
    
    def bbox_to_sam_mask(self,
                         image: np.ndarray,
                         bbox: List[float],
                         multimask: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        将边界框转换为SAM掩码
        
        Args:
            image: 输入图像 (H, W, 3) RGB格式
            bbox: 边界框 [x1, y1, x2, y2] 或 [x, y, w, h]
            multimask: 是否返回多个掩码候选
        
        Returns:
            mask: 最佳掩码 (H, W) 二值掩码
            logit: 掩码logit (256, 256)
        """
        # 确保图像格式正确
        if len(image.shape) != 3 or image.shape[2] != 3:
            raise ValueError(f"图像格式错误: {image.shape}")
        
        if image.dtype != np.uint8:
            if image.max() <= 1.0:
                image = (image * 255).astype(np.uint8)
            else:
                image = image.astype(np.uint8)
        
        # 转换bbox格式
        if len(bbox) == 4:
            if bbox[2] > bbox[0] and bbox[3] > bbox[1]:
                # [x1, y1, x2, y2] 格式
                x1, y1, x2, y2 = bbox
            else:
                # [x, y, w, h] 格式
                x, y, w, h = bbox
                x1, y1, x2, y2 = x, y, x + w, y + h
        else:
            raise ValueError(f"边界框格式错误: {bbox}")
        
        # 确保坐标在图像范围内
        h, w = image.shape[:2]
        x1 = max(0, min(w - 1, int(x1)))
        y1 = max(0, min(h - 1, int(y1)))
        x2 = max(0, min(w - 1, int(x2)))
        y2 = max(0, min(h - 1, int(y2)))
        
        # 确保边界框有效
        if x2 <= x1 or y2 <= y1:
            raise ValueError(f"无效的边界框: [{x1}, {y1}, {x2}, {y2}]")
        
        # 设置SAM图像
        self.sam_controller.sam_controler.reset_image()
        self.sam_controller.sam_controler.set_image(image)
        
        # 方法1：尝试直接使用边界框（如果SAM支持）
        try:
            # SAM的predictor支持box输入
            sam_predictor = self.sam_controller.sam_controler.predictor
            box = np.array([x1, y1, x2, y2])
            
            # 使用边界框进行分割（更准确）
            masks, scores, logits = sam_predictor.predict(
                box=box[None, :],  # SAM需要(N, 4)格式
                multimask_output=multimask
            )
            
            # 选择最佳掩码
            best_idx = np.argmax(scores)
            mask = masks[best_idx]
            logit = logits[best_idx]
            
        except Exception as e:
            # 方法2：如果边界框输入失败，使用中心点+多个点
            print(f"[成员B] 使用边界框输入失败，改用多点提示: {e}")
            
            # 使用边界框的多个点作为提示（更准确）
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)
            
            # 使用边界框的四个角点+中心点
            points = np.array([
                [center_x, center_y],      # 中心点
                [x1, y1],                  # 左上角
                [x2, y2],                  # 右下角
                [(x1+x2)//2, y1],         # 上边中点
                [(x1+x2)//2, y2],         # 下边中点
            ])
            labels = np.array([1, 1, 1, 1, 1])  # 都是前景点
            
            # 使用SAM进行分割
            mask, logit, _ = self.sam_controller.first_frame_click(
                image=image,
                points=points,
                labels=labels,
                multimask=multimask
            )
        
        # 将掩码转换为二值掩码
        mask_binary = (mask > 0.5).astype(np.uint8) * 255
        
        return mask_binary, logit
    
    def segment_first_frame(self,
                           first_frame: np.ndarray,
                           bboxes: List[List[float]]) -> Tuple[np.ndarray, Dict]:
        """
        对第一帧进行分割，支持多个边界框（多个物体）
        
        Args:
            first_frame: 第一帧图像 (H, W, 3) RGB
            bboxes: 边界框列表，每个bbox格式为 [x1, y1, x2, y2]
        
        Returns:
            combined_mask: 组合掩码 (H, W)，不同物体用不同值标记 (0=背景, 1,2,3...=物体)
            mask_info: 掩码信息字典
        """
        h, w = first_frame.shape[:2]
        combined_mask = np.zeros((h, w), dtype=np.uint8)
        mask_info = {
            'masks': [],
            'logits': [],
            'bboxes': bboxes
        }
        
        for obj_id, bbox in enumerate(bboxes, start=1):
            # 对每个边界框进行分割
            mask, logit = self.bbox_to_sam_mask(first_frame, bbox, multimask=True)
            
            # 将掩码添加到组合掩码中（使用不同的物体ID）
            # mask是0-255的二值掩码，需要转换为0-1
            mask_binary = (mask > 127).astype(np.uint8)
            combined_mask[mask_binary > 0] = obj_id
            
            # 调试：打印分割结果
            non_zero_count = np.sum(mask_binary > 0)
            print(f"[成员B] 物体{obj_id}分割完成: 边界框={bbox}, 掩码非零像素={non_zero_count}")
            if non_zero_count == 0:
                print(f"  ⚠️  警告：物体{obj_id}的掩码全为0，分割可能失败！")
            
            mask_info['masks'].append(mask)
            mask_info['logits'].append(logit)
        
        return combined_mask, mask_info
    
    def track_video(self,
                   video_frames: List[np.ndarray],
                   first_frame_mask: np.ndarray) -> List[np.ndarray]:
        """
        追踪视频中的所有帧（使用Track-Anything的generator方法）
        
        Args:
            video_frames: 视频帧列表，每个帧为 (H, W, 3) RGB格式
            first_frame_mask: 第一帧的掩码 (H, W)，不同物体用不同值标记
        
        Returns:
            tracked_masks: 追踪后的掩码列表
        """
        print(f"[成员B] 开始追踪视频，共 {len(video_frames)} 帧")
        
        # 清空追踪器内存
        self.tracker.clear_memory()
        
        # 使用Track-Anything的generator方法
        masks, logits, painted_images = self._generator(video_frames, first_frame_mask)
        
        print(f"[成员B] 追踪完成，生成 {len(masks)} 个掩码")
        
        return masks
    
    def _generator(self, images: List[np.ndarray], template_mask: np.ndarray):
        """
        追踪生成器（基于Track-Anything的实现）
        
        Args:
            images: 图像列表
            template_mask: 第一帧掩码
        
        Returns:
            masks: 掩码列表
            logits: logit列表
            painted_images: 可视化图像列表
        """
        masks = []
        logits = []
        painted_images = []
        
        for i in tqdm(range(len(images)), desc="追踪进度"):
            if i == 0:
                # 第一帧：使用提供的掩码
                mask, logit, painted_image = self.tracker.track(images[i], first_frame_annotation=template_mask)
            else:
                # 后续帧：追踪
                mask, logit, painted_image = self.tracker.track(images[i])
            
            masks.append(mask)
            logits.append(logit)
            painted_images.append(painted_image)
        
        return masks, logits, painted_images
    
    def process_video(self,
                     video_path: str,
                     bboxes: Union[List[List[float]], Dict[int, List[List[float]]]],
                     output_mask_path: str = None,
                     save_frames: bool = True) -> Tuple[str, List[np.ndarray]]:
        """
        处理整个视频：分割第一帧 + 追踪所有帧
        
        Args:
            video_path: 视频路径（可以是视频文件或帧文件夹）
            bboxes: 边界框，可以是：
                    - List[List[float]]: 第一帧的边界框列表
                    - Dict[int, List[List[float]]]: 帧索引到边界框列表的映射
            output_mask_path: 输出掩码路径（文件夹）
            save_frames: 是否保存掩码帧
        
        Returns:
            output_path: 输出路径
            masks: 掩码列表
        """
        # 读取视频帧
        frames = self._load_video(video_path)
        print(f"[成员B] 加载视频完成，共 {len(frames)} 帧")
        
        # 处理边界框输入
        if isinstance(bboxes, dict):
            # 如果提供了多帧的边界框，使用第一帧的
            first_frame_bboxes = bboxes.get(0, bboxes.get(list(bboxes.keys())[0]))
        else:
            first_frame_bboxes = bboxes
        
        if len(first_frame_bboxes) == 0:
            raise ValueError("未提供边界框信息")
        
        # 分割第一帧
        print(f"[成员B] 分割第一帧，检测到 {len(first_frame_bboxes)} 个物体")
        first_frame_mask, mask_info = self.segment_first_frame(frames[0], first_frame_bboxes)
        
        # 追踪所有帧
        tracked_masks = self.track_video(frames, first_frame_mask)
        
        # 保存结果
        if output_mask_path is None:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_mask_path = os.path.join('results', 'member_b_masks', video_name)
        
        os.makedirs(output_mask_path, exist_ok=True)
        
        if save_frames:
            print(f"[成员B] 保存掩码到: {output_mask_path}")
            for idx, mask in enumerate(tracked_masks):
                mask_path = os.path.join(output_mask_path, f"{idx:05d}.png")
                
                # 确保掩码格式正确：0=背景，非0=前景（要删除）
                # tracker返回的mask格式：0=背景，1,2,3...=不同物体
                # ProPainter需要：0=背景，非0=前景（255或1都可以）
                if mask.dtype != np.uint8:
                    mask = mask.astype(np.uint8)
                
                # 将非0值转换为255（更清晰）
                mask_output = np.zeros_like(mask, dtype=np.uint8)
                mask_output[mask > 0] = 255
                
                # 保存掩码
                cv2.imwrite(mask_path, mask_output)
                
                # 调试：打印第一帧的掩码统计信息
                if idx == 0:
                    unique_values = np.unique(mask)
                    print(f"[成员B] 第一帧掩码统计: 唯一值={unique_values}, 形状={mask.shape}, 非零像素={np.sum(mask > 0)}")
        
        # 保存掩码视频（可选）
        mask_video_path = os.path.join(output_mask_path, 'mask_video.mp4')
        self._save_mask_video(tracked_masks, mask_video_path, fps=30)
        
        print(f"[成员B] 处理完成！掩码保存在: {output_mask_path}")
        
        return output_mask_path, tracked_masks
    
    def _load_video(self, video_path: str) -> List[np.ndarray]:
        """
        加载视频帧
        
        Args:
            video_path: 视频文件路径或帧文件夹路径
        
        Returns:
            frames: 帧列表，每个帧为 (H, W, 3) RGB格式
        """
        frames = []
        
        if os.path.isfile(video_path) and video_path.endswith(('.mp4', '.avi', '.mov', '.MP4', '.AVI', '.MOV')):
            # 视频文件
            cap = cv2.VideoCapture(video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                else:
                    break
            cap.release()
        elif os.path.isdir(video_path):
            # 帧文件夹
            frame_files = sorted([f for f in os.listdir(video_path) 
                                 if f.endswith(('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'))])
            for frame_file in frame_files:
                frame_path = os.path.join(video_path, frame_file)
                frame = cv2.imread(frame_path)
                if frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
        else:
            raise ValueError(f"无法识别视频路径: {video_path}")
        
        if len(frames) == 0:
            raise ValueError(f"未找到视频帧: {video_path}")
        
        return frames
    
    def _save_mask_video(self, masks: List[np.ndarray], output_path: str, fps: int = 30):
        """
        保存掩码视频
        
        Args:
            masks: 掩码列表
            output_path: 输出路径
            fps: 帧率
        """
        if len(masks) == 0:
            return
        
        # 将掩码转换为3通道用于视频保存
        mask_frames = []
        for mask in masks:
            # 将单通道掩码转换为3通道
            mask_3ch = np.stack([mask] * 3, axis=2)
            mask_frames.append(mask_3ch)
        
        imageio.mimwrite(output_path, mask_frames, fps=fps, quality=8)


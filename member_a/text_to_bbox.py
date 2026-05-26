"""
成员A：文本到边界框转换模块
使用GroundingDINO实现文本描述 → 边界框定位

功能：
1. 接收文本输入（如"删除视频中的汽车"）
2. 使用GroundingDINO检测第一帧中的目标物体
3. 输出边界框列表给成员B
"""

import os
import sys

# 修复：在导入cv2之前清理sys.path，移除可能导致递归导入的cv2目录
_cleaned_paths = []
for p in sys.path:
    normalized = p.replace('\\', '/').rstrip('/')
    if normalized.endswith('/cv2'):
        continue
    _cleaned_paths.append(p)
sys.path = _cleaned_paths

import cv2
import numpy as np
import torch
from typing import List, Tuple, Union, Dict
import json

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

try:
    from model.misc import get_device
except ImportError:
    def get_device():
        return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class TextToBBox:
    """
    成员A：文本到边界框转换模块
    
    使用GroundingDINO实现：
    - 输入：文本描述（如"删除视频中的汽车"）
    - 输出：边界框列表 [[x1, y1, x2, y2], ...]
    """
    
    def __init__(self,
                 groundingdino_checkpoint: str = None,
                 device: str = None):
        """
        初始化模块
        
        Args:
            groundingdino_checkpoint: GroundingDINO模型权重路径
            device: 设备 ('cuda:0', 'cpu'等)
        """
        # 设置设备
        if device is None:
            self.device = str(get_device())
        else:
            self.device = device
        
        print(f"[成员A] 初始化文本定位模块，设备: {self.device}")
        
        # 初始化GroundingDINO
        self.groundingdino = self._init_groundingdino(groundingdino_checkpoint)
        
        print(f"[成员A] 模块初始化完成")
    
    def _init_groundingdino(self, checkpoint_path: str = None):
        """
        初始化GroundingDINO模型
        
        Args:
            checkpoint_path: 模型权重路径
        
        Returns:
            model: GroundingDINO模型
        """
        try:
            # 尝试导入GroundingDINO
            import sys
            groundingdino_path = os.path.join(project_root, 'GroundingDINO')
            if os.path.exists(groundingdino_path):
                sys.path.insert(0, groundingdino_path)
            
            # 尝试导入GroundingDINO模块
            try:
                from groundingdino.util.inference import load_model
            except ImportError:
                print(f"[成员A] 无法导入GroundingDINO，请确保已安装")
                print(f"[成员A] 安装方法: cd GroundingDINO && pip install -e .")
                return None
            
            print(f"[成员A] 加载GroundingDINO模型...")
            
            # 如果checkpoint不存在，尝试使用默认路径
            if checkpoint_path is None:
                checkpoint_path = os.environ.get('GROUNDINGDINO_CHECKPOINT', 
                                                 os.path.join(project_root, 'weights', 'groundingdino_swinb_cogcoor.pth'))
            
            # 如果是相对路径，尝试在项目根目录查找
            if not os.path.isabs(checkpoint_path) and not os.path.exists(checkpoint_path):
                project_weights_path = os.path.join(project_root, checkpoint_path)
                if os.path.exists(project_weights_path):
                    checkpoint_path = project_weights_path
            
            if not os.path.exists(checkpoint_path):
                print(f"[成员A] GroundingDINO模型文件不存在: {checkpoint_path}")
                print(f"[成员A] 请下载GroundingDINO模型:")
                print(f"  https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha2/groundingdino_swinb_cogcoor.pth")
                print(f"  保存到: {checkpoint_path}")
                return None
            
            # 查找配置文件
            config_path = os.path.join(groundingdino_path, 'groundingdino', 'config', 'GroundingDINO_SwinB_cfg.py')
            if not os.path.exists(config_path):
                # 尝试其他可能的配置路径
                alt_config = os.path.join(groundingdino_path, 'groundingdino', 'config', 'GroundingDINO_SwinT_OGC.py')
                if os.path.exists(alt_config):
                    config_path = alt_config
                else:
                    print(f"[成员A] 找不到GroundingDINO配置文件")
                    return None
            
            # 加载模型
            device_str = 'cuda' if 'cuda' in self.device else 'cpu'
            model = load_model(config_path, checkpoint_path, device=device_str)
            model = model.to(self.device)
            model.eval()
            
            print(f"[成员A] GroundingDINO模型加载成功")
            return model
            
        except Exception as e:
            print(f"[成员A] GroundingDINO初始化失败: {e}")
            import traceback
            traceback.print_exc()
            print(f"[成员A] 将使用模拟模式（返回示例边界框）")
            return None
    
    def detect(self,
               image: np.ndarray,
               text_prompt: str,
               box_threshold: float = 0.3,
               text_threshold: float = 0.25) -> List[List[float]]:
        """
        检测图像中的目标物体
        
        Args:
            image: 输入图像 (H, W, 3) RGB格式
            text_prompt: 文本提示（如"car", "person", "删除视频中的汽车"）
            box_threshold: 边界框置信度阈值
            text_threshold: 文本匹配阈值
        
        Returns:
            bboxes: 边界框列表 [[x1, y1, x2, y2], ...]
        """
        if self.groundingdino is None:
            # 模拟模式：返回示例边界框
            print(f"[成员A] 使用模拟模式，文本提示: {text_prompt}")
            print(f"[成员A] 返回示例边界框（需要实际安装GroundingDINO）")
            # 返回图像中心的一个示例边界框
            h, w = image.shape[:2]
            center_x, center_y = w // 2, h // 2
            bbox_size = min(w, h) // 4
            return [[center_x - bbox_size, center_y - bbox_size, 
                    center_x + bbox_size, center_y + bbox_size]]
        
        # 实际GroundingDINO检测代码
        try:
            from groundingdino.util.inference import predict
            from PIL import Image
            import groundingdino.datasets.transforms as T
            from torchvision.ops import box_convert
            
            # 将numpy数组转换为PIL Image
            if isinstance(image, np.ndarray):
                # 确保是RGB格式
                if len(image.shape) == 3 and image.shape[2] == 3:
                    image_pil = Image.fromarray(image.astype(np.uint8))
                else:
                    raise ValueError(f"图像格式错误: {image.shape}")
            else:
                image_pil = image
            
            # 预处理图像（与load_image相同的变换）
            transform = T.Compose([
                T.RandomResize([800], max_size=1333),
                T.ToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ])
            image_transformed, _ = transform(image_pil, None)
            
            # 检测
            boxes, logits, phrases = predict(
                model=self.groundingdino,
                image=image_transformed,
                caption=text_prompt,
                box_threshold=box_threshold,
                text_threshold=text_threshold,
                device=self.device
            )
            
            if len(boxes) == 0:
                print(f"[成员A] 未检测到目标物体")
                return []
            
            # 转换边界框格式（从cxcywh到xyxy，并转换为像素坐标）
            h, w = image.shape[:2]
            boxes_xyxy = box_convert(boxes, in_fmt="cxcywh", out_fmt="xyxy")
            
            # 转换为像素坐标
            bboxes = []
            for box in boxes_xyxy:
                x1, y1, x2, y2 = box.tolist()
                # GroundingDINO返回的是归一化坐标，需要转换为像素坐标
                x1 = int(x1 * w)
                y1 = int(y1 * h)
                x2 = int(x2 * w)
                y2 = int(y2 * h)
                # 确保坐标在图像范围内
                x1 = max(0, min(x1, w))
                y1 = max(0, min(y1, h))
                x2 = max(0, min(x2, w))
                y2 = max(0, min(y2, h))
                if x2 > x1 and y2 > y1:  # 确保是有效的边界框
                    bboxes.append([x1, y1, x2, y2])
            
            print(f"[成员A] 检测到 {len(bboxes)} 个目标物体")
            for i, (bbox, phrase, logit) in enumerate(zip(bboxes, phrases, logits)):
                print(f"  物体{i+1}: {phrase} (置信度: {logit:.3f}) - {bbox}")
            
            return bboxes
            
        except Exception as e:
            print(f"[成员A] GroundingDINO检测失败: {e}")
            import traceback
            traceback.print_exc()
            # 返回空列表，让调用者知道检测失败
            return []
    
    def process_video_first_frame(self,
                                 video_path: str,
                                 text_prompt: str,
                                 box_threshold: float = 0.3,
                                 text_threshold: float = 0.25) -> List[List[float]]:
        """
        处理视频第一帧，检测目标物体
        
        Args:
            video_path: 视频路径（文件或帧文件夹）
            text_prompt: 文本提示（如"car", "删除视频中的汽车"）
            box_threshold: 边界框置信度阈值
            text_threshold: 文本匹配阈值
        
        Returns:
            bboxes: 边界框列表 [[x1, y1, x2, y2], ...]
        """
        # 读取第一帧
        first_frame = self._load_first_frame(video_path)
        
        # 检测
        bboxes = self.detect(first_frame, text_prompt, box_threshold, text_threshold)
        
        print(f"[成员A] 检测到 {len(bboxes)} 个目标物体")
        for i, bbox in enumerate(bboxes):
            print(f"  物体{i+1}: {bbox}")
        
        return bboxes
    
    def _load_first_frame(self, video_path: str) -> np.ndarray:
        """
        加载视频第一帧
        
        Args:
            video_path: 视频路径
        
        Returns:
            frame: 第一帧图像 (H, W, 3) RGB格式
        """
        if os.path.isfile(video_path) and video_path.endswith(('.mp4', '.avi', '.mov')):
            # 视频文件
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                raise ValueError(f"无法读取视频: {video_path}")
        elif os.path.isdir(video_path):
            # 帧文件夹
            frame_files = sorted([f for f in os.listdir(video_path) 
                                 if f.endswith(('.jpg', '.jpeg', '.png'))])
            if len(frame_files) == 0:
                raise ValueError(f"帧文件夹为空: {video_path}")
            frame_path = os.path.join(video_path, frame_files[0])
            frame = cv2.imread(frame_path)
            if frame is not None:
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                raise ValueError(f"无法读取第一帧: {frame_path}")
        else:
            raise ValueError(f"无法识别视频路径: {video_path}")
    
    def save_bboxes_json(self, bboxes: List[List[float]], output_path: str):
        """
        保存边界框到JSON文件
        
        Args:
            bboxes: 边界框列表
            output_path: 输出JSON文件路径
        """
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(bboxes, f, indent=2, ensure_ascii=False)
        print(f"[成员A] 边界框已保存到: {output_path}")


def main():
    """
    测试函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='成员A：文本到边界框转换')
    parser.add_argument('--video', type=str, required=True, help='输入视频路径')
    parser.add_argument('--text', type=str, required=True, help='文本提示（如"car", "删除视频中的汽车"）')
    parser.add_argument('--output', type=str, default=None, help='输出JSON文件路径')
    parser.add_argument('--box_threshold', type=float, default=0.3, help='边界框置信度阈值')
    parser.add_argument('--text_threshold', type=float, default=0.25, help='文本匹配阈值')
    
    args = parser.parse_args()
    
    # 初始化模块
    module = TextToBBox()
    
    # 处理视频
    bboxes = module.process_video_first_frame(
        video_path=args.video,
        text_prompt=args.text,
        box_threshold=args.box_threshold,
        text_threshold=args.text_threshold
    )
    
    # 保存结果
    if args.output is None:
        video_name = os.path.splitext(os.path.basename(args.video))[0]
        args.output = os.path.join('results', 'member_a_bboxes', f'{video_name}_bboxes.json')
    
    module.save_bboxes_json(bboxes, args.output)
    
    print(f"\n[成员A] 处理完成！")
    print(f"边界框数量: {len(bboxes)}")
    print(f"输出路径: {args.output}")


if __name__ == '__main__':
    main()



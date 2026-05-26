"""
视频修复质量评估模块
支持多种评估指标，用于比较不同模型的输出质量
"""

import os
import cv2
import numpy as np
import torch
from pathlib import Path
from typing import List, Dict, Tuple
import imageio


class VideoQualityEvaluator:
    """视频修复质量评估器"""
    
    def __init__(self, device=None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"[评估器] 使用设备: {self.device}")
    
    def evaluate_all(self, video_path: str, mask_dir: str, original_video_path: str) -> Dict:
        """
        综合评估视频修复质量
        
        Args:
            video_path: 修复后的视频路径
            mask_dir: 掩码目录
            original_video_path: 原始视频路径
            
        Returns:
            评估结果字典
        """
        results = {}
        
        # 评估1: 时域一致性
        results['temporal_consistency'] = self.evaluate_temporal_consistency(video_path)
        
        # 评估2: 空间平滑度
        results['spatial_smoothness'] = self.evaluate_spatial_smoothness(video_path)
        
        # 评估3: 修复区域质量（与原始对比）
        results['inpainted_region_quality'] = self.evaluate_inpainted_region(
            video_path, mask_dir, original_video_path
        )
        
        # 评估4: 整体自然度
        results['naturalness'] = self.evaluate_naturalness(video_path)
        
        # 综合评分
        results['overall_score'] = self.compute_overall_score(results)
        
        return results
    
    def evaluate_temporal_consistency(self, video_path: str) -> Dict:
        """评估时域一致性（帧间变化是否平滑）"""
        frames = self._load_video_frames(video_path)
        if len(frames) < 2:
            return {'score': 0, 'detail': '帧数不足'}
        
        # 计算相邻帧差异
        diffs = []
        for i in range(1, len(frames)):
            diff = np.abs(frames[i].astype(float) - frames[i-1].astype(float))
            diffs.append(np.mean(diff))
        
        mean_diff = np.mean(diffs)
        std_diff = np.std(diffs)
        
        # 一致性评分：变化越小越一致（归一化到0-100）
        score = max(0, 100 - mean_diff * 10 - std_diff * 5)
        
        return {
            'score': round(score, 2),
            'mean_frame_diff': round(mean_diff, 2),
            'frame_diff_std': round(std_diff, 2)
        }
    
    def evaluate_spatial_smoothness(self, video_path: str) -> Dict:
        """评估空间平滑度（修复区域是否有伪影）"""
        frames = self._load_video_frames(video_path)
        if len(frames) == 0:
            return {'score': 0, 'detail': '无法加载帧'}
        
        # 采样中间帧
        mid_idx = len(frames) // 2
        frame = frames[mid_idx]
        
        # 计算梯度（边缘强度）
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY).astype(float)
        grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        
        # 平滑度评分
        mean_grad = np.mean(grad_mag)
        score = max(0, 100 - mean_grad * 0.5)
        
        return {
            'score': round(score, 2),
            'mean_gradient': round(mean_grad, 2)
        }
    
    def evaluate_inpainted_region(self, video_path: str, mask_dir: str, 
                                  original_video_path: str) -> Dict:
        """评估修复区域的质量"""
        # 加载掩码
        mask_files = sorted([f for f in os.listdir(mask_dir) if f.endswith(('.png', '.jpg'))])
        if not mask_files:
            return {'score': 50, 'detail': '无掩码文件'}
        
        # 加载原始帧和修复帧
        orig_frames = self._load_video_frames(original_video_path)
        repaired_frames = self._load_video_frames(video_path)
        
        if len(orig_frames) == 0 or len(repaired_frames) == 0:
            return {'score': 0, 'detail': '无法加载视频帧'}
        
        # 采样几帧进行评估
        sample_indices = [0, len(mask_files)//4, len(mask_files)//2, 3*len(mask_files)//4, len(mask_files)-1]
        sample_indices = [i for i in sample_indices if i < len(mask_files)]
        
        psnr_values = []
        ssim_values = []
        
        for idx in sample_indices:
            mask_path = os.path.join(mask_dir, mask_files[idx])
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if mask is None:
                continue
            
            # 调整掩码大小
            if idx < len(repaired_frames):
                repaired = repaired_frames[min(idx, len(repaired_frames)-1)]
                original = orig_frames[min(idx, len(orig_frames)-1)]
                
                if repaired.shape[:2] != original.shape[:2]:
                    original = cv2.resize(original, (repaired.shape[1], repaired.shape[0]))
                
                if mask.shape != repaired.shape[:2]:
                    mask = cv2.resize(mask, (repaired.shape[1], repaired.shape[0]))
                
                # 只在掩码区域计算
                mask_binary = (mask > 127).astype(np.uint8)
                if np.sum(mask_binary) > 0:
                    # 计算PSNR
                    mse = np.mean((repaired[mask_binary > 0].astype(float) - 
                                  original[mask_binary > 0].astype(float))**2)
                    if mse > 0:
                        psnr = 10 * np.log10(255**2 / mse)
                        psnr_values.append(psnr)
                    
                    # 简化的SSIM
                    ssim = self._compute_ssim_region(repaired, original, mask_binary)
                    ssim_values.append(ssim)
        
        avg_psnr = np.mean(psnr_values) if psnr_values else 0
        avg_ssim = np.mean(ssim_values) if ssim_values else 0
        
        # 评分：基于PSNR和SSIM
        score = min(100, (avg_psnr * 2 + avg_ssim * 100) / 2)
        
        return {
            'score': round(score, 2),
            'psnr': round(avg_psnr, 2) if psnr_values else 0,
            'ssim': round(avg_ssim, 4) if ssim_values else 0
        }
    
    def evaluate_naturalness(self, video_path: str) -> Dict:
        """评估视频整体自然度"""
        frames = self._load_video_frames(video_path)
        if len(frames) == 0:
            return {'score': 0}
        
        # 评估颜色分布自然度
        color_scores = []
        for frame in frames[::max(1, len(frames)//10)]:  # 采样10帧
            # 计算颜色直方图
            hist_b = cv2.calcHist([frame], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([frame], [1], None, [256], [0, 256])
            hist_r = cv2.calcHist([frame], [2], None, [256], [0, 256])
            
            # 自然视频的颜色分布应该相对平滑
            for hist in [hist_b, hist_g, hist_r]:
                hist_norm = hist / hist.sum()
                # 计算熵（越高越自然）
                entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-10))
                color_scores.append(min(100, entropy * 20))
        
        avg_color_score = np.mean(color_scores) if color_scores else 50
        
        # 评估亮度分布
        brightness_scores = []
        for frame in frames[::max(1, len(frames)//10)]:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            mean_brightness = np.mean(gray)
            # 适中亮度得分高
            brightness_score = 100 - abs(mean_brightness - 128) * 0.5
            brightness_scores.append(brightness_score)
        
        avg_brightness = np.mean(brightness_scores)
        
        score = (avg_color_score + avg_brightness) / 2
        
        return {
            'score': round(score, 2),
            'color_naturalness': round(avg_color_score, 2),
            'brightness': round(avg_brightness, 2)
        }
    
    def compute_overall_score(self, results: Dict) -> Dict:
        """计算综合评分"""
        weights = {
            'temporal_consistency': 0.30,
            'spatial_smoothness': 0.20,
            'inpainted_region_quality': 0.35,
            'naturalness': 0.15
        }
        
        total_score = 0
        for key, weight in weights.items():
            if key in results and 'score' in results[key]:
                total_score += results[key]['score'] * weight
        
        return {
            'total': round(total_score, 2),
            'weights': weights
        }
    
    def _load_video_frames(self, video_path: str) -> List[np.ndarray]:
        """加载视频帧"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                break
        cap.release()
        return frames
    
    def _compute_ssim_region(self, img1: np.ndarray, img2: np.ndarray, mask: np.ndarray) -> float:
        """简化版SSIM计算"""
        # 只计算掩码区域
        m1 = img1[mask > 0].astype(float)
        m2 = img2[mask > 0].astype(float)
        
        if len(m1) == 0:
            return 0.0
        
        # 均值
        mu1 = np.mean(m1)
        mu2 = np.mean(m2)
        
        # 方差
        sigma1_sq = np.var(m1)
        sigma2_sq = np.var(m2)
        sigma12 = np.mean((m1 - mu1) * (m2 - mu2))
        
        # SSIM参数
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2
        
        ssim = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2))
        
        return max(0, min(1, ssim))

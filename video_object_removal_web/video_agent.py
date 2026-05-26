"""
视频修复智能体 - 多模型并行处理 + 自动评估择优
支持多种修复策略，自动选择最佳结果
"""

import os
import sys
import json
import subprocess
import shutil
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
from io import StringIO


@dataclass
class ModelConfig:
    """单个修复模型的配置"""
    name: str
    description: str
    params: Dict = field(default_factory=dict)
    output_dir: str = ""
    video_path: str = ""
    score: float = 0.0
    evaluation: Dict = field(default_factory=dict)
    processing_time: float = 0.0


class VideoInpaintingAgent:
    """
    视频修复智能体
    
    工作流程：
    1. 配置多个修复模型（使用不同参数配置）
    2. 并行/串行执行修复
    3. 对每个结果进行质量评估
    4. 选择最佳结果返回
    """
    
    def __init__(self, parent_dir: str, suppress_output: bool = True):
        self.parent_dir = parent_dir
        self.suppress_output = suppress_output
        self.propainter_script = self._find_propainter_script()
        
    def _find_propainter_script(self) -> str:
        """查找ProPainter脚本"""
        candidates = [
            os.path.join(self.parent_dir, 'ProPainter', 'inference_propainter.py'),
            os.path.join(self.parent_dir, 'inference_propainter.py'),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return ""
    
    def get_available_models(self, video_path: str, mask_path: str, base_output_dir: str) -> List[ModelConfig]:
        """
        获取可用的修复模型配置
        
        Args:
            video_path: 输入视频路径
            mask_path: 掩码目录路径
            base_output_dir: 基础输出目录
            
        Returns:
            模型配置列表
        """
        models = [
            ModelConfig(
                name="propainter_default",
                description="ProPainter 默认配置\n平衡速度和质量",
                params={
                    'neighbor_length': 10,
                    'ref_stride': 10,
                    'mask_dilation': 4,
                }
            ),
            ModelConfig(
                name="propainter_high_quality",
                description="ProPainter 高质量模式\n更大邻域窗口，更精细修复",
                params={
                    'neighbor_length': 20,
                    'ref_stride': 8,
                    'mask_dilation': 3,
                }
            ),
            ModelConfig(
                name="propainter_fast",
                description="ProPainter 快速模式\n较小邻域窗口，速度更快",
                params={
                    'neighbor_length': 6,
                    'ref_stride': 15,
                    'mask_dilation': 5,
                }
            ),
            ModelConfig(
                name="propainter_conservative",
                description="ProPainter 保守模式\n最小掩码膨胀，保留更多原图内容",
                params={
                    'neighbor_length': 10,
                    'ref_stride': 10,
                    'mask_dilation': 2,
                }
            ),
        ]
        
        # 为每个模型分配输出目录
        for i, model in enumerate(models):
            model.output_dir = os.path.join(base_output_dir, f"model_{i+1}_{model.name}")
            os.makedirs(model.output_dir, exist_ok=True)
        
        return models
    
    def run_single_model(self, model: ModelConfig, video_path: str, mask_path: str) -> Dict:
        """
        运行单个修复模型
        
        Args:
            model: 模型配置
            video_path: 输入视频路径
            mask_path: 掩码目录路径
            
        Returns:
            运行结果
        """
        if not self.propainter_script:
            return {
                'status': 'error',
                'error': 'ProPainter脚本不存在'
            }
        
        # 构建命令
        cmd = [
            sys.executable,
            self.propainter_script,
            '-i', os.path.abspath(video_path),
            '-m', os.path.abspath(mask_path),
            '-o', os.path.abspath(model.output_dir),
            '--neighbor_length', str(model.params.get('neighbor_length', 10)),
            '--ref_stride', str(model.params.get('ref_stride', 10)),
            '--mask_dilation', str(model.params.get('mask_dilation', 4)),
            '--fp16',  # 启用半精度推理加速
        ]
        
        print(f"\n{'='*50}")
        print(f"[Agent] 运行模型: {model.name}")
        print(f"[Agent] 参数: {model.params}")
        print(f"{'='*50}")
        
        start_time = time.time()
        
        try:
            current_dir = os.getcwd()
            try:
                os.chdir(self.parent_dir)
                result = subprocess.run(
                    cmd, 
                    text=True, 
                    capture_output=True,
                    timeout=3600  # 1小时超时
                )
            finally:
                os.chdir(current_dir)
            
            processing_time = time.time() - start_time
            model.processing_time = processing_time
            
            if result.returncode != 0:
                error_output = result.stderr if result.stderr else result.stdout
                return {
                    'status': 'error',
                    'error': f'模型执行失败: {error_output[-500:]}'
                }
            
            # 查找输出视频
            output_video = self._find_output_video(model.output_dir)
            if not output_video:
                return {
                    'status': 'error',
                    'error': '未找到输出视频'
                }
            
            model.video_path = output_video
            
            return {
                'status': 'success',
                'video_path': output_video,
                'processing_time': processing_time
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'error',
                'error': '执行超时（超过1小时）'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def evaluate_result(self, model: ModelConfig, mask_path: str, original_video: str) -> Dict:
        """
        评估单个模型的结果
        
        Args:
            model: 模型配置（需包含video_path）
            mask_path: 掩码目录
            original_video: 原始视频路径
            
        Returns:
            评估结果
        """
        try:
            from video_evaluator import VideoQualityEvaluator
            evaluator = VideoQualityEvaluator()
            
            print(f"\n[评估] 评估模型: {model.name}")
            evaluation = evaluator.evaluate_all(
                video_path=model.video_path,
                mask_dir=mask_path,
                original_video_path=original_video
            )
            
            model.evaluation = evaluation
            model.score = evaluation.get('overall_score', {}).get('total', 0)
            
            return evaluation
            
        except Exception as e:
            print(f"[评估] 评估失败: {e}")
            return {'error': str(e), 'overall_score': {'total': 0}}
    
    def process_with_agent(self, video_path: str, mask_path: str, 
                          output_dir: str, models: Optional[List[ModelConfig]] = None) -> Dict:
        """
        使用Agent模式处理视频：多模型运行 + 评估择优
        
        Args:
            video_path: 输入视频路径
            mask_path: 掩码目录路径
            output_dir: 输出目录
            models: 可选的自定义模型列表
            
        Returns:
            最佳结果
        """
        # 获取模型配置
        if models is None:
            models = self.get_available_models(video_path, mask_path, output_dir)
        
        results = []
        
        print(f"\n{'='*60}")
        print(f"[Agent] 开始多模型修复，共 {len(models)} 个模型")
        print(f"{'='*60}")
        
        # 依次运行每个模型
        for i, model in enumerate(models):
            print(f"\n[Agent] 进度: {i+1}/{len(models)}")
            
            # 运行模型
            run_result = self.run_single_model(model, video_path, mask_path)
            
            if run_result['status'] != 'success':
                print(f"[Agent] 模型 {model.name} 运行失败: {run_result.get('error', '')}")
                results.append({
                    'model': asdict(model),
                    'status': 'error',
                    'error': run_result.get('error', '')
                })
                continue
            
            # 评估结果
            print(f"[Agent] 评估模型 {model.name}...")
            evaluation = self.evaluate_result(model, mask_path, video_path)
            
            results.append({
                'model': asdict(model),
                'status': 'success',
                'evaluation': evaluation
            })
            
            print(f"[Agent] 模型 {model.name} 综合评分: {model.score:.2f}")
        
        # 选择最佳结果
        successful = [r for r in results if r['status'] == 'success']
        
        if not successful:
            return {
                'status': 'error',
                'error': '所有模型均运行失败',
                'all_results': results
            }
        
        # 按评分排序
        successful.sort(key=lambda x: x['model'].get('score', 0), reverse=True)
        best = successful[0]
        
        print(f"\n{'='*60}")
        print(f"[Agent] 最佳模型: {best['model']['name']}")
        print(f"[Agent] 综合评分: {best['model']['score']:.2f}")
        print(f"{'='*60}")
        
        return {
            'status': 'success',
            'best_model': best['model']['name'],
            'best_video_path': best['model']['video_path'],
            'best_score': best['model']['score'],
            'best_evaluation': best['evaluation'],
            'all_results': results,
            'ranking': [
                {
                    'rank': i+1,
                    'name': r['model']['name'],
                    'description': r['model']['description'],
                    'score': r['model'].get('score', 0),
                    'video_path': r['model'].get('video_path', ''),
                    'processing_time': r['model'].get('processing_time', 0)
                }
                for i, r in enumerate(successful)
            ]
        }
    
    def _find_output_video(self, output_dir: str) -> str:
        """查找输出视频文件"""
        # 标准路径
        candidates = [
            os.path.join(output_dir, 'inpaint_out.mp4'),
            os.path.join(output_dir, 'output.mp4'),
        ]
        
        for path in candidates:
            if os.path.exists(path):
                return path
        
        # 搜索子目录
        for root, dirs, files in os.walk(output_dir):
            for f in files:
                if f.endswith('.mp4') and 'inpaint' in f.lower():
                    return os.path.join(root, f)
        
        return ""

"""
视频物体删除Web应用 - 后端API
提供干净的接口，隐藏内部实现细节
"""

import os
import sys
import json
import shutil
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
from pathlib import Path

# 添加父目录到路径，以便导入member_b
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    from video_processor import VideoProcessor
    MODULE_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入处理模块: {e}")
    MODULE_AVAILABLE = False
    VideoProcessor = None

# 导入成员A（文本转边界框）
try:
    from member_a.text_to_bbox import TextToBBox
    MEMBER_A_AVAILABLE = True
except ImportError as e:
    print(f"警告: 成员A模块导入失败: {e}")
    MEMBER_A_AVAILABLE = False
    TextToBBox = None

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置上传文件大小限制（500MB）
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# 配置
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'MOV', 'MP4', 'AVI'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 全局处理器实例（延迟初始化）
processor = None
text_to_bbox_module = None


def get_processor():
    """获取或初始化处理器"""
    global processor
    if processor is None:
        if not MODULE_AVAILABLE or VideoProcessor is None:
            raise RuntimeError("处理模块不可用")
        processor = VideoProcessor(suppress_output=True)  # 抑制内部输出
    return processor


def get_text_to_bbox():
    """获取或初始化文本转边界框模块"""
    global text_to_bbox_module
    if text_to_bbox_module is None:
        if not MEMBER_A_AVAILABLE or TextToBBox is None:
            raise RuntimeError("成员A模块不可用，无法使用文本输入功能")
        text_to_bbox_module = TextToBBox()
    return text_to_bbox_module


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """返回前端页面"""
    return send_from_directory('.', 'index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'module_available': MODULE_AVAILABLE,
        'member_a_available': MEMBER_A_AVAILABLE
    })


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """上传视频文件"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': '未提供视频文件'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # 打印上传信息（用于调试）
            abs_upload_dir = os.path.abspath(UPLOAD_FOLDER)
            abs_filepath = os.path.join(abs_upload_dir, filename)
            print(f"[上传] 收到文件: {filename}")
            print(f"[上传] 保存到: {abs_filepath}")
            
            file.save(filepath)
            
            # 验证文件是否保存成功
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
                print(f"[上传] 上传成功，文件大小: {file_size:.2f} MB")
                return jsonify({
                    'status': 'success',
                    'filename': filename,
                    'path': abs_filepath,  # 返回绝对路径
                    'url': f'/api/video/{filename}',
                    'size_mb': round(file_size, 2)
                })
            else:
                print(f"[上传] 错误: 文件保存失败")
                return jsonify({'error': '文件保存失败'}), 500
        else:
            return jsonify({'error': '不支持的文件格式'}), 400
            
    except Exception as e:
        import traceback
        print(f"[上传] 错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/video/<filename>')
def get_video(filename):
    """获取视频文件"""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/api/text_to_bbox', methods=['POST'])
def text_to_bbox():
    """
    文本转边界框API
    使用成员A模块将自然语言描述转换为边界框
    
    请求格式:
    {
        "video_path": "视频文件路径",
        "text_prompt": "要删除的物体描述，例如：删除视频中的汽车"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        video_path = data.get('video_path')
        text_prompt = data.get('text_prompt', '').strip()
        
        if not video_path:
            return jsonify({'error': '未提供视频路径'}), 400
        
        if not text_prompt:
            return jsonify({'error': '未提供文本描述'}), 400
        
        # 处理视频路径
        if not os.path.isabs(video_path):
            video_path = os.path.abspath(video_path)
        video_path = os.path.normpath(video_path)
        
        if not os.path.exists(video_path):
            return jsonify({'error': f'视频文件不存在: {video_path}'}), 404
        
        # 检查成员A是否可用
        if not MEMBER_A_AVAILABLE:
            return jsonify({
                'error': '文本输入功能不可用，成员A模块未安装或初始化失败'
            }), 503
        
        # 获取文本转边界框模块
        try:
            module_a = get_text_to_bbox()
        except Exception as e:
            return jsonify({
                'error': f'无法初始化文本转边界框模块: {str(e)}'
            }), 500
        
        # 处理视频第一帧，生成边界框
        print(f"[文本转边界框] 视频: {video_path}")
        print(f"[文本转边界框] 文本提示: {text_prompt}")
        
        try:
            bboxes = module_a.process_video_first_frame(
                video_path=video_path,
                text_prompt=text_prompt,
                box_threshold=0.3,
                text_threshold=0.25
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': f'生成边界框失败: {str(e)}'
            }), 500
        
        if not bboxes or len(bboxes) == 0:
            return jsonify({
                'status': 'error',
                'error': '未检测到目标物体。请尝试：\n'
                        '1. 使用更具体的描述（如"红色汽车"而不是"物体"）\n'
                        '2. 确保物体在第一帧中可见\n'
                        '3. 尝试使用手动框选模式'
            }), 400
        
        print(f"[文本转边界框] 检测到 {len(bboxes)} 个边界框")
        
        return jsonify({
            'status': 'success',
            'bboxes': bboxes,
            'count': len(bboxes),
            'message': f'成功检测到 {len(bboxes)} 个目标物体'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/process', methods=['POST'])
def process_video():
    """
    处理视频：生成掩码 + ProPainter修复，返回删除物体后的视频
    
    请求格式:
    {
        "video_path": "视频文件路径（相对于uploads目录或绝对路径）",
        "bboxes": [[x1, y1, x2, y2], ...],  // 边界框列表，支持多个物体
        "start_frame": 0  // 起始帧索引（可选，默认0，即第一帧）
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        video_path = data.get('video_path')
        bboxes = data.get('bboxes', [])
        start_frame = data.get('start_frame', 0)  # 默认从第一帧开始
        
        if not video_path:
            return jsonify({'error': '未提供视频路径'}), 400
        
        if not bboxes:
            return jsonify({'error': '未提供边界框'}), 400
        
        # 验证边界框格式
        if not isinstance(bboxes, list):
            return jsonify({'error': '边界框必须是列表格式'}), 400
        
        for bbox in bboxes:
            if not isinstance(bbox, list) or len(bbox) != 4:
                return jsonify({'error': f'边界框格式错误: {bbox}，应该是 [x1, y1, x2, y2]'}), 400
        
        # 处理视频路径
        # 如果已经是绝对路径，直接使用；否则标准化为绝对路径
        if not os.path.isabs(video_path):
            # 相对路径，标准化为绝对路径
            video_path = os.path.abspath(video_path)
        
        # 标准化路径（处理路径分隔符等）
        video_path = os.path.normpath(video_path)
        
        if not os.path.exists(video_path):
            return jsonify({'error': f'视频文件不存在: {video_path}'}), 404
        
        # 获取处理器
        proc = get_processor()
        
        # 生成输出路径
        video_name = Path(video_path).stem
        output_dir = os.path.join(OUTPUT_FOLDER, video_name)
        
        # 处理视频（使用包装器，隐藏内部细节）
        result = proc.process(video_path, bboxes, output_dir, start_frame=start_frame)
        
        if result['status'] == 'error':
            # 错误信息可能包含多行，保持原样返回
            error_msg = result.get('error', '处理失败')
            return jsonify({
                'status': 'error',
                'error': error_msg
            }), 500
        
        # 返回结果（返回视频路径）
        output_video_path = result['video_path']
        # 计算相对于OUTPUT_FOLDER的路径
        try:
            relative_video_path = os.path.relpath(output_video_path, os.path.abspath(OUTPUT_FOLDER))
        except ValueError:
            # 如果路径不在同一驱动器，使用绝对路径
            relative_video_path = output_video_path
        
        # 使用相对路径作为URL
        # 将路径分隔符统一为/（Web路径）
        web_path = relative_video_path.replace('\\', '/')
        
        return jsonify({
            'status': 'success',
            'video_path': relative_video_path,
            'video_url': f'/api/video_output/{web_path}',
            'message': '视频处理完成，物体已删除'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/process_agent', methods=['POST'])
def process_video_agent():
    """
    使用智能体模式处理视频：多模型并行 + 自动评估择优
    
    请求格式:
    {
        "video_path": "视频文件路径",
        "bboxes": [[x1, y1, x2, y2], ...],
        "start_frame": 0
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请求数据为空'}), 400
        
        video_path = data.get('video_path')
        bboxes = data.get('bboxes', [])
        start_frame = data.get('start_frame', 0)
        
        if not video_path:
            return jsonify({'error': '未提供视频路径'}), 400
        
        if not bboxes:
            return jsonify({'error': '未提供边界框'}), 400
        
        # 处理视频路径
        if not os.path.isabs(video_path):
            video_path = os.path.abspath(video_path)
        video_path = os.path.normpath(video_path)
        
        if not os.path.exists(video_path):
            return jsonify({'error': f'视频文件不存在: {video_path}'}), 404
        
        # 获取处理器
        proc = get_processor()
        
        # 生成输出路径
        video_name = Path(video_path).stem
        output_dir = os.path.join(OUTPUT_FOLDER, f"{video_name}_agent")
        
        print(f"\n{'='*60}")
        print(f"[Agent API] 启动智能体处理模式")
        print(f"[Agent API] 视频: {video_name}")
        print(f"{'='*60}")
        
        # 使用智能体模式处理（多模型 + 评估择优）
        result = proc.process_with_agent(video_path, bboxes, output_dir, start_frame=start_frame)
        
        if result['status'] == 'error':
            error_msg = result.get('error', '处理失败')
            return jsonify({
                'status': 'error',
                'error': error_msg
            }), 500
        
        # 返回结果
        output_video_path = result['video_path']
        try:
            relative_video_path = os.path.relpath(output_video_path, os.path.abspath(OUTPUT_FOLDER))
        except ValueError:
            relative_video_path = output_video_path
        
        web_path = relative_video_path.replace('\\', '/')
        
        return jsonify({
            'status': 'success',
            'video_path': relative_video_path,
            'video_url': f'/api/video_output/{web_path}',
            'best_model': result.get('best_model', ''),
            'best_score': result.get('best_score', 0),
            'best_evaluation': result.get('best_evaluation', {}),
            'ranking': result.get('ranking', []),
            'message': f'智能体处理完成！最佳模型: {result.get("best_model", "")} (评分: {result.get("best_score", 0):.2f})'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/video_output/<path:filepath>')
def get_output_video(filepath):
    """获取处理后的视频文件"""
    # filepath可能是文件名或相对路径
    # 尝试直接在outputs目录下查找
    full_path = os.path.join(OUTPUT_FOLDER, filepath)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename)
    
    # 如果在outputs目录下找不到，尝试在所有子目录中查找
    filename = os.path.basename(filepath)
    for root, dirs, files in os.walk(OUTPUT_FOLDER):
        if filename in files:
            return send_from_directory(root, filename)
    
    return jsonify({'error': f'视频文件不存在: {filepath}'}), 404


@app.route('/api/list_masks/<video_name>')
def list_masks(video_name):
    """列出指定视频的所有掩码文件"""
    mask_dir = os.path.join(OUTPUT_FOLDER, video_name)
    if not os.path.exists(mask_dir):
        return jsonify({'error': '视频不存在'}), 404
    
    mask_files = []
    for file in sorted(os.listdir(mask_dir)):
        if file.endswith('.png'):
            mask_files.append({
                'filename': file,
                'url': f'/api/masks/{video_name}/{file}'
            })
    
    return jsonify({
        'status': 'success',
        'mask_files': mask_files,
        'count': len(mask_files)
    })


if __name__ == '__main__':
    print("=" * 60)
    print("视频物体删除 Web 应用")
    print("=" * 60)
    print(f"处理模块状态: {'可用' if MODULE_AVAILABLE else '不可用'}")
    print(f"文本输入功能: {'可用' if MEMBER_A_AVAILABLE else '不可用'}")
    print(f"上传目录: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"输出目录: {os.path.abspath(OUTPUT_FOLDER)}")
    print("=" * 60)
    print("\n启动服务器...")
    print("访问 http://127.0.0.1:5000 使用前端界面")
    print("\n功能说明：")
    print("  - 文本输入：使用自然语言描述要删除的物体")
    print("  - 手动框选：在视频上直接拖拽框选物体")
    print("  - 单模型处理：使用默认配置快速处理")
    print("  - 🤖智能体模式：4个模型并行处理 + 自动评估择优")
    print("\n提示：处理视频时，ProPainter的进度信息会显示在终端")
    print("     请查看终端输出了解处理进度\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


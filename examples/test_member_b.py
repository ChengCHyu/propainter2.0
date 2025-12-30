"""
成员B模块测试脚本
"""

import os
import sys
import json
import numpy as np

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from member_b_api import MemberBAPI, process_video


def test_single_object():
    """测试单个物体追踪"""
    print("="*60)
    print("测试1: 单个物体追踪")
    print("="*60)
    
    # 使用示例视频
    video_path = os.path.join(project_root, 'inputs', 'object_removal', 'bmx-trees')
    
    if not os.path.exists(video_path):
        print(f"警告: 测试视频不存在: {video_path}")
        print("请确保测试视频存在")
        return False
    
    # 单个边界框（需要根据实际视频调整坐标）
    # 这里使用示例坐标，实际使用时需要从成员A获取
    bboxes = [[150, 150, 250, 250]]
    
    try:
        api = MemberBAPI()
        result = api.process(
            video_path=video_path,
            bboxes=bboxes,
            output_path=os.path.join(project_root, 'results', 'test_member_b_single')
        )
        
        if result['status'] == 'success':
            print(f"✓ 测试通过")
            print(f"  输出路径: {result['output_path']}")
            print(f"  掩码数量: {result['mask_count']}")
            return True
        else:
            print(f"✗ 测试失败: {result['message']}")
            return False
    except Exception as e:
        print(f"✗ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_objects():
    """测试多个物体追踪"""
    print("\n" + "="*60)
    print("测试2: 多个物体追踪")
    print("="*60)
    
    video_path = os.path.join(project_root, 'inputs', 'object_removal', 'bmx-trees')
    
    if not os.path.exists(video_path):
        print(f"警告: 测试视频不存在: {video_path}")
        return False
    
    # 多个边界框
    bboxes = [
        [100, 100, 200, 200],  # 物体1
        [300, 300, 400, 400],  # 物体2
    ]
    
    try:
        api = MemberBAPI()
        result = api.process(
            video_path=video_path,
            bboxes=bboxes,
            output_path=os.path.join(project_root, 'results', 'test_member_b_multi')
        )
        
        if result['status'] == 'success':
            print(f"✓ 测试通过")
            print(f"  输出路径: {result['output_path']}")
            print(f"  掩码数量: {result['mask_count']}")
            return True
        else:
            print(f"✗ 测试失败: {result['message']}")
            return False
    except Exception as e:
        print(f"✗ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_json_input():
    """测试JSON文件输入"""
    print("\n" + "="*60)
    print("测试3: JSON文件输入")
    print("="*60)
    
    video_path = os.path.join(project_root, 'inputs', 'object_removal', 'bmx-trees')
    
    if not os.path.exists(video_path):
        print(f"警告: 测试视频不存在: {video_path}")
        return False
    
    # 创建临时JSON文件
    bbox_json_path = os.path.join(project_root, 'results', 'test_bboxes.json')
    os.makedirs(os.path.dirname(bbox_json_path), exist_ok=True)
    
    bboxes = [[150, 150, 250, 250]]
    with open(bbox_json_path, 'w') as f:
        json.dump(bboxes, f)
    
    try:
        api = MemberBAPI()
        result = api.process_from_json(
            video_path=video_path,
            bbox_json_path=bbox_json_path,
            output_path=os.path.join(project_root, 'results', 'test_member_b_json')
        )
        
        if result['status'] == 'success':
            print(f"✓ 测试通过")
            print(f"  输出路径: {result['output_path']}")
            print(f"  掩码数量: {result['mask_count']}")
            # 清理临时文件
            if os.path.exists(bbox_json_path):
                os.remove(bbox_json_path)
            return True
        else:
            print(f"✗ 测试失败: {result['message']}")
            return False
    except Exception as e:
        print(f"✗ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_bbox_to_mask():
    """测试边界框到掩码转换"""
    print("\n" + "="*60)
    print("测试4: 边界框到掩码转换")
    print("="*60)
    
    try:
        from member_b_segment_track import SegmentAndTrackModule
        import cv2
        
        # 创建测试图像
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # 初始化模块
        module = SegmentAndTrackModule()
        
        # 测试边界框转换
        bbox = [100, 100, 200, 200]
        mask, logit = module.bbox_to_sam_mask(test_image, bbox)
        
        print(f"✓ 测试通过")
        print(f"  掩码形状: {mask.shape}")
        print(f"  Logit形状: {logit.shape}")
        return True
    except Exception as e:
        print(f"✗ 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("成员B模块测试套件")
    print("="*60 + "\n")
    
    results = []
    
    # 运行测试
    results.append(("边界框到掩码转换", test_bbox_to_mask()))
    results.append(("单个物体追踪", test_single_object()))
    results.append(("多个物体追踪", test_multiple_objects()))
    results.append(("JSON文件输入", test_json_input()))
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        return 1


if __name__ == '__main__':
    exit(main())


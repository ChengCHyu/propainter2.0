"""
工具：可视化边界框，帮助确定准确的边界框坐标
"""

import cv2
import numpy as np
import sys
import os

def visualize_bbox(image_path, bbox):
    """
    在图像上绘制边界框，帮助检查位置
    
    Args:
        image_path: 图像路径
        bbox: 边界框 [x1, y1, x2, y2]
    """
    # 读取图像
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图像: {image_path}")
        return
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img_rgb.shape[:2]
    
    print(f"图像尺寸: {w}x{h}")
    print(f"边界框: {bbox}")
    
    # 解析边界框
    x1, y1, x2, y2 = bbox
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    
    # 确保在范围内
    x1 = max(0, min(w - 1, x1))
    y1 = max(0, min(h - 1, y1))
    x2 = max(0, min(w - 1, x2))
    y2 = max(0, min(h - 1, y2))
    
    # 绘制边界框
    img_draw = img.copy()
    cv2.rectangle(img_draw, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    # 绘制中心点
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    cv2.circle(img_draw, (center_x, center_y), 5, (255, 0, 0), -1)
    
    # 显示图像
    cv2.imshow('Boundary Box Visualization', img_draw)
    print("\n按任意键关闭窗口...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # 保存结果
    output_path = 'bbox_visualization.jpg'
    cv2.imwrite(output_path, img_draw)
    print(f"可视化结果已保存到: {output_path}")


def interactive_select_bbox(image_path):
    """
    交互式选择边界框
    
    Args:
        image_path: 图像路径
    
    Returns:
        bbox: 边界框 [x1, y1, x2, y2]
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"无法读取图像: {image_path}")
        return None
    
    h, w = img.shape[:2]
    print(f"图像尺寸: {w}x{h}")
    print("\n使用鼠标拖拽选择边界框...")
    print("按ESC确认，按R重置")
    
    # 鼠标回调函数
    drawing = False
    start_point = None
    end_point = None
    img_copy = img.copy()
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal drawing, start_point, end_point, img_copy
        
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            start_point = (x, y)
            img_copy = img.copy()
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                img_copy = img.copy()
                cv2.rectangle(img_copy, start_point, (x, y), (0, 255, 0), 2)
                cv2.imshow('Select BBox', img_copy)
        
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            end_point = (x, y)
            img_copy = img.copy()
            cv2.rectangle(img_copy, start_point, end_point, (0, 255, 0), 2)
            cv2.imshow('Select BBox', img_copy)
    
    cv2.namedWindow('Select BBox')
    cv2.setMouseCallback('Select BBox', mouse_callback)
    cv2.imshow('Select BBox', img)
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            if start_point and end_point:
                x1 = min(start_point[0], end_point[0])
                y1 = min(start_point[1], end_point[1])
                x2 = max(start_point[0], end_point[0])
                y2 = max(start_point[1], end_point[1])
                bbox = [x1, y1, x2, y2]
                cv2.destroyAllWindows()
                return bbox
        elif key == ord('r'):  # Reset
            start_point = None
            end_point = None
            img_copy = img.copy()
            cv2.imshow('Select BBox', img_copy)
    
    cv2.destroyAllWindows()
    return None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='边界框可视化工具')
    parser.add_argument('--image', type=str, required=True, help='图像路径')
    parser.add_argument('--bbox', type=str, default=None, help='边界框 [x1,y1,x2,y2] 或 "interactive"')
    parser.add_argument('--interactive', action='store_true', help='交互式选择边界框')
    
    args = parser.parse_args()
    
    if args.interactive or args.bbox == 'interactive':
        # 交互式选择
        bbox = interactive_select_bbox(args.image)
        if bbox:
            print(f"\n选择的边界框: {bbox}")
            print(f"格式: [{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}]")
    elif args.bbox:
        # 可视化现有边界框
        import json
        try:
            bbox = json.loads(args.bbox)
        except:
            bbox = eval(args.bbox)
        visualize_bbox(args.image, bbox)
    else:
        print("请指定 --bbox 或 --interactive")
        print("\n示例:")
        print("  python find_bbox_tool.py --image inputs/object_removal/bmx-trees/00000.jpg --bbox '[150,150,250,250]'")
        print("  python find_bbox_tool.py --image inputs/object_removal/bmx-trees/00000.jpg --interactive")


if __name__ == '__main__':
    main()


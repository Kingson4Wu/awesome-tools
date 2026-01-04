#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF封面添加工具
功能：为PDF文件添加封面，保留原有目录导航和书签信息
支持：PDF封面或图片封面（JPG, PNG等）
"""

import sys
import os
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from pathlib import Path
from PIL import Image
import io


def image_to_pdf(image_path):
    """
    将图片转换为PDF

    参数:
        image_path: 图片文件路径
    返回:
        PDF字节流
    """
    try:
        # 打开图片
        img = Image.open(image_path)

        # 转换为RGB模式（PDF需要）
        if img.mode in ('RGBA', 'LA', 'P'):
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # 保存为PDF到内存
        pdf_bytes = io.BytesIO()
        img.save(pdf_bytes, 'PDF', resolution=100.0)
        pdf_bytes.seek(0)

        return pdf_bytes
    except Exception as e:
        raise Exception(f"图片转换PDF失败: {e}")


def add_cover_to_pdf(original_pdf_path, cover_path, output_pdf_path):
    """
    为PDF添加封面，保留所有原始信息

    参数:
        original_pdf_path: 原始PDF文件路径
        cover_path: 封面文件路径（支持PDF或图片）
        output_pdf_path: 输出PDF文件路径
    """
    try:
        # 检查封面文件类型
        cover_ext = Path(cover_path).suffix.lower()
        image_exts = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']

        # 如果是图片，先转换为PDF
        if cover_ext in image_exts:
            print(f"检测到图片格式封面，正在转换为PDF...")
            cover_pdf_bytes = image_to_pdf(cover_path)
            temp_cover_path = cover_pdf_bytes
        else:
            temp_cover_path = cover_path

        # 使用PdfMerger保留元数据和书签
        merger = PdfMerger(strict=False)

        # 添加封面
        if isinstance(temp_cover_path, io.BytesIO):
            merger.append(temp_cover_path)
        else:
            merger.append(temp_cover_path)

        # 添加原始PDF，保留书签
        merger.append(original_pdf_path, import_outline=True)

        # 写入输出文件
        with open(output_pdf_path, 'wb') as f:
            merger.write(f)

        merger.close()

        print(f"✓ 成功添加封面!")
        print(f"  原始文件: {original_pdf_path}")
        print(f"  封面文件: {cover_path}")
        print(f"  输出文件: {output_pdf_path}")

    except FileNotFoundError as e:
        print(f"✗ 错误: 文件未找到 - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    print("=" * 60)
    print("PDF封面添加工具")
    print("=" * 60)

    # 获取用户输入
    if len(sys.argv) == 4:
        original_pdf = sys.argv[1]
        cover_file = sys.argv[2]
        output_pdf = sys.argv[3]
    else:
        print("\n请输入以下信息:")
        original_pdf = input("原始PDF文件路径: ").strip()
        cover_file = input("封面文件路径 (支持PDF/PNG/JPG等): ").strip()
        output_pdf = input("输出PDF文件路径 (留空则自动命名): ").strip()

        # 如果输出路径为空，自动生成
        if not output_pdf:
            original_path = Path(original_pdf)
            output_pdf = str(original_path.parent / f"{original_path.stem}_with_cover.pdf")
            print(f"输出文件将保存为: {output_pdf}")

    # 验证文件存在
    if not Path(original_pdf).exists():
        print(f"✗ 错误: 原始PDF文件不存在: {original_pdf}")
        sys.exit(1)

    if not Path(cover_file).exists():
        print(f"✗ 错误: 封面文件不存在: {cover_file}")
        sys.exit(1)

    # 执行添加封面操作
    print("\n正在处理...")
    add_cover_to_pdf(original_pdf, cover_file, output_pdf)
    print("\n完成!")


if __name__ == "__main__":
    print("依赖库: PyPDF2, Pillow")
    print("安装命令: pip install PyPDF2 Pillow\n")

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)

# python script.py original.pdf cover.pdf output.pdf
# -- coding: utf-8 --

import os
from PIL import Image, ImageDraw, ImageFont


def add_text_to_image(
        image_path,
        output_path,
        text_lines,
        font_path,
        font_size=30,
        text_color="black",
        text_position="bottom",
        spacing=10,
):
    """
    在图片的指定位置添加多行文字，不改变原始图片尺寸。

    :param image_path: 原始图片路径
    :param output_path: 输出图片路径
    :param text_lines: 多行文字的列表
    :param font_path: 字体文件路径（必须是 .ttf 或 .otf）
    :param font_size: 字体大小
    :param text_color: 文字颜色
    :param text_position: 文字位置 (top, bottom, top-left, top-right, bottom-left, bottom-right)
    :param spacing: 每行文字之间的间距
    """
    # 打开原始图片
    image = Image.open(image_path)
    image = image.convert("RGBA")
    img_width, img_height = image.size

    # 加载字体
    font = ImageFont.truetype(font_path, font_size)

    # 创建绘图对象
    draw = ImageDraw.Draw(image)

    # 计算总文字高度
    total_text_height = sum(
        (draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]) + spacing
        for line in text_lines
    ) - spacing

    # 根据位置计算文字起始位置
    if text_position in ["top", "bottom"]:
        text_x = (img_width - max(draw.textbbox((0, 0), line, font=font)[2] for line in text_lines)) // 2
    elif text_position in ["top-left", "bottom-left"]:
        text_x = 10
    elif text_position in ["top-right", "bottom-right"]:
        text_x = img_width - max(draw.textbbox((0, 0), line, font=font)[2] for line in text_lines) - 10

    if text_position in ["top", "top-left", "top-right"]:
        text_y = 10
    elif text_position in ["bottom", "bottom-left", "bottom-right"]:
        text_y = img_height - total_text_height - 10

    # 绘制每行文字
    for line in text_lines:
        line_bbox = draw.textbbox((0, 0), line, font=font)
        line_width = line_bbox[2] - line_bbox[0]
        draw.text((text_x, text_y), line, font=font, fill=text_color)
        text_y += line_bbox[3] - line_bbox[1] + spacing

    # 保存结果
    image.save(output_path)
    print(f"保存成功: {output_path}")


home_path = os.path.expanduser("~")
image_path = home_path + "/Downloads/zj/nnnn.png"  # 替换为你的背景图片路径
output_path = home_path + "/Downloads/output_text.png"  # 输出图片路径

# 示例用法
text_lines = ["Line 1: Hello, World!", "Line 2: This is a test.", "Line 3: Enjoy your day!"]
font_path = "../picture/msyh.ttf"  # 替换为你的字体路径
font_size = 40

add_text_to_image(
    image_path=image_path,
    output_path=output_path,
    text_lines=text_lines,
    font_path=font_path,
    font_size=font_size,
    text_color="red",
    text_position="bottom",  # 替换为其他位置如 bottom, top, top-right 等
    spacing=10
)

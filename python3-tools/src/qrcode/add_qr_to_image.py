# -- coding: utf-8 --
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os

from PIL import Image, ImageDraw, ImageFont
import qrcode


def add_qr_and_text_to_image(
        background_path,
        qr_data,
        output_path,
        text_lines=None,
        text_position="top-left",
        text_font_path=None,
        text_font_size=20,
        text_color="black",
        qr_position="top-right",
        qr_size=150
):
    """
    将二维码和文字添加到图片上

    :param background_path: 背景图片路径
    :param qr_data: 二维码数据
    :param output_path: 输出图片路径
    :param text_lines: 添加的文字列表，每个元素是一行文字
    :param text_position: 文字的位置，目前支持 "top-left"
    :param text_font_path: 字体文件路径，默认使用系统字体
    :param text_font_size: 字体大小
    :param text_color: 文字颜色
    :param qr_position: 二维码的位置（top-right, top-left, bottom-right, bottom-left）
    :param qr_size: 二维码的大小（像素）
    """
    # 打开背景图片
    background = Image.open(background_path)
    background = background.convert("RGBA")  # 确保背景是RGBA格式
    bg_width, bg_height = background.size

    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    # 调整二维码大小
    qr_img = qr_img.resize((qr_size, qr_size))

    # 确定二维码的位置
    if qr_position == "top-right":
        qr_x, qr_y = bg_width - qr_size, 0
    elif qr_position == "top-left":
        qr_x, qr_y = 0, 0
    elif qr_position == "bottom-right":
        qr_x, qr_y = bg_width - qr_size, bg_height - qr_size
    elif qr_position == "bottom-left":
        qr_x, qr_y = 0, bg_height - qr_size
    else:
        raise ValueError("Invalid QR position. Choose from 'top-right', 'top-left', 'bottom-right', 'bottom-left'.")

    # 将二维码粘贴到背景图
    background.paste(qr_img, (qr_x, qr_y), qr_img)

    # 添加文字
    if text_lines:
        draw = ImageDraw.Draw(background)

        # 加载字体（如果未提供字体路径，使用默认字体）
        if text_font_path:
            font = ImageFont.truetype(text_font_path, text_font_size)
        else:
            raise ValueError("text_font_path is required to adjust text_font_size.")  # 提示用户提供字体路径

        # 初始位置（左上角）
        if text_position == "top-left":
            text_x, text_y = 10, 10
        else:
            raise ValueError("Currently, only 'top-left' text position is supported.")

        # 逐行绘制文字
        for line in text_lines:
            draw.text((text_x, text_y), line, font=font, fill=text_color)
            text_y += text_font_size + 5  # 行间距

    # 保存结果
    background.save(output_path)
    print(f"保存成功：{output_path}")


# 示例用法
home_path = os.path.expanduser("~")
background_image_path = home_path + "/Downloads/zj/nnnn.png"  # 替换为你的背景图片路径
output_image_path = home_path + "/Downloads/output_with_qr_and_text.png"  # 输出图片路径
qr_data = "https://example.com"  # 二维码数据
#text_lines = ["Line 1: Hello, World!", "Line 2: QR Code Example", "Line 3: Enjoy!"]  # 多行文字
text_lines = ["Line 1: Hello, World!"]  # 多行文字

add_qr_and_text_to_image(
    background_path=background_image_path,
    qr_data=qr_data,
    output_path=output_image_path,
    text_lines=text_lines,
    text_position="top-left",
    text_font_path="../picture/msyh.ttf",  # 替换为实际字体路径
    text_font_size=30,  # 字体大小
    text_color="red",
    qr_position="top-right",
    qr_size=200
)

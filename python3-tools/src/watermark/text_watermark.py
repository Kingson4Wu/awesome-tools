# -- coding: utf-8 --

import matplotlib.pyplot as plt
import numpy as np
from skimage.color import rgb2hsv
import colorsys


def get_dominant_color(image):
    # 将RGB图像转换为HSV颜色空间
    hsv_image = rgb2hsv(image)
    # 提取色调通道
    hue = hsv_image[:, :, 0]
    # 统计色调值的直方图
    hist, bins = np.histogram(hue, bins=16, range=(0, 1))
    # 找到最大的色调值对应的颜色
    dominant_color_bin = np.argmax(hist)
    # 计算该颜色的中心值作为主要颜色
    dominant_color_hue = (bins[dominant_color_bin] + bins[dominant_color_bin + 1]) / 2
    # 将主要颜色转换为RGB空间
    dominant_color_rgb = colorsys.hsv_to_rgb(dominant_color_hue, 1, 1)
    return dominant_color_rgb


def text_watermark(img_src, dest, text, fontsize=7, alpha=0.5):
    fig = plt.figure()
    # 读取图像
    img = plt.imread(img_src)
    plt.imshow(img)
    # 获取主要颜色
    dominant_color = get_dominant_color(img)
    # 将主要颜色中的黑色通道设置为透明
    dominant_color = [*dominant_color, 1.0]  # 添加透明度通道
    dominant_color = np.array(dominant_color)  # 转换为NumPy数组
    black_pixels = (dominant_color == [0, 0, 0, 1]).all(axis=-1)
    dominant_color[black_pixels] = [0, 0, 0, 0]
    # 添加文字水印
    height, width, _ = img.shape
    plt.text(10, height - 20, text, fontsize=fontsize, alpha=alpha, color=dominant_color, ha='left', va='bottom')
    # 隐藏坐标轴
    plt.axis('off')
    # 保存图像
    plt.savefig(dest, dpi=fig.dpi, bbox_inches='tight', transparent=True)
    plt.close(fig)  # 关闭图形窗口，释放内存


for img in ['Haaland.jpeg', 'Haaland2.jpeg']:
    text_watermark(img_src=img, dest='wm_%s' % img, text='@拉巴力不吃三文鱼')

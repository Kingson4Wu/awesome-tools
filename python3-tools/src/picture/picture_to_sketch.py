# -- coding: utf-8 --
# https://blog.csdn.net/momoda118/article/details/119389177

from PIL import Image
import numpy as np
import tkinter.filedialog
root = tkinter.Tk().withdraw()
filename = tkinter.filedialog.askopenfilename()  # 打开选择文件对话框
try:
    depth = 30  # 0-100,越高，颜色越深
    picture_grad = np.gradient(np.asarray(Image.open(filename).convert('L')).astype('int'))  # 取图像灰度的梯度值
    grad_x, grad_y = picture_grad[0] * depth / 100., picture_grad[1] * depth / 100.  # 将获取的维度梯度值进行深度处理
    base = np.sqrt(grad_x ** 2 + grad_y ** 2 + 1.)  # 降噪基
    _x, _y, _z = grad_x / base, grad_y / base, 1. / base
    sce_z, sce_x = np.pi / 2.1, np.pi / 3  # 光源的俯视角度值和方位角度值
    # 光源对x,y,z 轴的影响
    dx, dy, dz = np.cos(sce_z) * np.cos(sce_x), np.cos(sce_z) * np.sin(sce_x), np.sin(sce_z)
    Normalized = 255 * (dx * _x + dy * _y + dz * _z).clip(0, 255)  # 光源归一化
    im = Image.fromarray(Normalized.astype('uint8'))  # 重构图像
    im.save('转换后的素描图.jpg')  # 保存转换后的图片
    im.show()  # 展示转换后的图片
except Exception:
    print('转换失败！')

# -- coding: utf-8 --

import cv2
from imwatermark import WatermarkDecoder

bgr = cv2.imread('test_wm.bmp')

decoder = WatermarkDecoder('bytes', 256)  # 改这里，位数改大
watermark = decoder.decode(bgr, 'dwtDct')

try:
    print(watermark.decode('utf-8'))
except UnicodeDecodeError:
    print("⚠️ 解码失败，原始字节为:", watermark)

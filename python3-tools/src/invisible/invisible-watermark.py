# -- coding: utf-8 --

import cv2
from imwatermark import WatermarkEncoder

bgr = cv2.imread('IMG_6611.png')
wm = 'labali_20180207'

encoder = WatermarkEncoder()
encoder.set_watermark('bytes', wm.encode('utf-8'))
bgr_encoded = encoder.encode(bgr, 'dwtDct')
cv2.imwrite('test_wm.bmp', bgr_encoded)

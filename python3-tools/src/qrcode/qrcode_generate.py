# -- coding: utf-8 --


# pip install qrcode[pil]

# /usr/local/bin/python3.11
# /usr/local/bin/pip3.11

import qrcode

# 创建二维码
data = "https://example.com"
qr = qrcode.QRCode(
    version=1,  # 控制二维码的大小，1 是最小尺寸
    error_correction=qrcode.constants.ERROR_CORRECT_L,  # 容错等级
    box_size=10,  # 每个点的像素大小
    border=4,  # 边框宽度（单位：点）
)
qr.add_data(data)
qr.make(fit=True)

# 生成图片
img = qr.make_image(fill_color="black", back_color="white")
img.save("qrcode.png")
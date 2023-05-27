# -- coding: utf-8 --

import matplotlib.pyplot as plt


from pylab import mpl

mpl.rcParams["font.sans-serif"] = ["SimHei"]
mpl.rcParams["axes.unicode_minus"] = False


def text_watermark(img_src, dest, text, loc, fontsize=7, alpha=1):
    fig = plt.figure()
    # 读取图像
    plt.imshow(plt.imread(img_src))
    # 添加文字水印
    img = plt.imread(img_src)
    height, width, _ = img.shape

    # bbox_props = dict(boxstyle='round, pad=0.5', edgecolor='black', facecolor='white', alpha=0.7)
    # plt.text(loc[0], height - loc[1], text, fontsize=fontsize, alpha=alpha, color='white', bbox=bbox_props)

    plt.text(loc[0], height - loc[1], text, fontsize=fontsize, alpha=alpha, color='white')
    # 隐藏坐标轴
    plt.axis('off')
    # 保存图像
    plt.savefig(dest, dpi=fig.dpi, bbox_inches='tight')
    return fig


for img in ['Haaland.jpeg', 'Haaland2.jpeg']:
    text_watermark(img_src=img, dest='wm_%s' % img, text='@拉巴力不吃三文鱼', loc=[20, 20])

# -- coding: utf-8 --

import os

from text_watermark import text_watermark


def watermark_recursive(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # 判断文件是否为图片文件
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):

                # 判断文件名是否已经以 "_backup" 结尾
                if file_name.split('.')[0].endswith("_backup"):

                    new_file_name = os.path.join(root, file_name.split('.')[0].replace('_backup', '') + "." +
                                                 file_name.split('.')[1])
                    print(file_path)
                    text_watermark(img_src=file_path, dest=new_file_name, text='@拉巴力不吃三文鱼')


# 指定文件夹路径
folder_path = '/Users/kingsonwu/programming/github/kingson4wu.github.io/source/_posts'

watermark_recursive(folder_path)

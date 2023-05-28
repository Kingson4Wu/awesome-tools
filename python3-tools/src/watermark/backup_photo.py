# -- coding: utf-8 --


import os


def add_backup_suffix_recursive(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # 判断文件是否为图片文件
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):

                # 判断文件名是否已经以 "_backup" 结尾
                if not file_name.split('.')[0].endswith("_backup"):
                    # 构建新文件名
                    new_file_name = file_name.split('.')[0] + '_backup.' + file_name.split('.')[1]
                    new_file_path = os.path.join(root, new_file_name)

                    # 判断新文件名是否已存在
                    if not os.path.exists(new_file_path):
                        # 重命名文件
                        os.rename(file_path, new_file_path)
                        print(f"Renamed: {file_name} -> {new_file_name}")
                    else:
                        print(f"Skipped: {file_name} (File with backup suffix already exists)")


# 指定文件夹路径
folder_path = '/Users/kingsonwu/programming/github/kingson4wu.github.io/source/_posts'

# 调用函数进行重命名
add_backup_suffix_recursive(folder_path)

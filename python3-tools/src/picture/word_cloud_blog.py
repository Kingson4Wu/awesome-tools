from wordcloud import WordCloud
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import jieba
import os


def read_md_files(folder_path):
    # 创建一个空字符串，用于存储所有 Markdown 文件的内容
    all_content = ""

    # 遍历指定文件夹及其子文件夹中的文件
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 检查文件扩展名是否为 .md
            if file.endswith(".md"):
                # 构造 Markdown 文件的完整路径
                file_path = os.path.join(root, file)

                # 读取文件内容
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # 将文件内容添加到 all_content 字符串中
                all_content += content

    return all_content


def read_file_lines(file_path):
    lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            lines.append(line.strip())  # 去掉行尾的换行符并添加到数组中
    return lines


import re


def remove_chinese(text):
    pattern = re.compile(r'[\u4e00-\u9fff]+')  # 匹配中文字符的正则表达式
    result = re.sub(pattern, '', text)  # 替换中文字符为空字符串
    return result

def remove_word(text):
    words_to_remove = ["tag", "title", "tags"]  # 要去掉的单词列表
    for word in words_to_remove:
        pattern = re.compile(r'\b' + re.escape(word) + r'\b')  # 匹配指定单词的正则表达式
        text = re.sub(pattern, '', text)  # 替换指定单词为空字符串
    return text


import re


def remove_links_and_images(text):
    # 去掉链接
    pattern_links = re.compile(r'\[.*?\]\(.*?\)')
    text = re.sub(pattern_links, '', text)

    # 去掉图片
    pattern_images = re.compile(r'\!\[.*?\]\(.*?\)')
    text = re.sub(pattern_images, '', text)

    return text


# 示例Markdown文本
markdown_text = """
# Title

This is some **bold** and *italic* text.

Here is a [link](https://example.com) and an ![image](image.jpg).

## Section

Another paragraph with a [link](https://example.com) and an ![image](image.jpg).
"""

# 去掉链接和图片
# result = remove_links_and_images(markdown_text)


# 指定文件夹路径
folder_path = "/Users/kingsonwu/programming/github/kingson4wu.github.io/source/_posts"

# 调用函数读取所有 Markdown 文件内容
merged_content = read_md_files(folder_path)

# 去掉中文
merged_content = remove_chinese(merged_content)

merged_content = remove_links_and_images(merged_content)

merged_content = remove_word(merged_content)

# 中文分词
text = ' '.join(jieba.cut(merged_content))

# 生成对象
img = Image.open('1685275694886.jpg')  # 打开遮罩图片
mask = np.array(img)  # 将图片转换为数组

# 示例文件路径
file_path = 'stopword.txt'

# 读取文件并按行组成数组
stopwords = read_file_lines(file_path)

stopwords.extend(['中', '做', '时'])
stopwords.extend(['pre', 'status', 'type', 'len', 'TODO', 'String', 'class', 'user', 'list', 'true', 'false'])

# stopwords = ["我","你","她","的","是","了","在","也","和","就","都","这", "可以", "如果", "中", "对", "我们", "需要", "时间", "自己", "一个", "问题", "使用", "工作", "会", "有", "而"]
wc = WordCloud(font_path="msyh.ttf",
               mask=mask,
               width=1000,
               height=700,
               background_color='white',
               max_words=200,
               stopwords=stopwords).generate(text)

# 显示词云
plt.imshow(wc, interpolation='bilinear')  # 用plt显示图片
plt.axis("off")  # 不显示坐标轴
plt.show()  # 显示图片

# 保存到文件
wc.to_file("/Users/kingsonwu/programming/github/kingson4wu.github.io/source/about/index/word_cloud.png")

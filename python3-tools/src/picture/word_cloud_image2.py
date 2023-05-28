
# https://zhuanlan.zhihu.com/p/353795160

# 示例代码
from wordcloud import WordCloud
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import jieba

# 打开文本
with open("comments.txt",encoding="utf-8") as f:
    s = f.read()

# 中文分词
text = ' '.join(jieba.cut(s))

# 生成对象
img = Image.open('1685275694886.jpg') # 打开遮罩图片
mask = np.array(img) #将图片转换为数组

stopwords = ["我","你","她","的","是","了","在","也","和","就","都","这"]
wc = WordCloud(font_path="msyh.ttf",
               mask=mask,
               width = 1000,
               height = 700,
               background_color='white',
               max_words=200,
               stopwords=stopwords).generate(text)

# 显示词云
plt.imshow(wc, interpolation='bilinear')# 用plt显示图片
plt.axis("off")  # 不显示坐标轴
plt.show() # 显示图片

# 保存到文件
wc.to_file("word_image2.png")
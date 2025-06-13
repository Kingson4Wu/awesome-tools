# -- coding: utf-8 --

from lxml import html
import requests
import re


def quark_link(url):
    resp = requests.get(url)
    t = html.fromstring(resp.content)

    # 获取夸克MP3下载链接
    link = t.xpath('//a[h2[contains(text(), "夸克MP3链接下载")]]/@href')
    return "https://www.xmwav.com" + link[0]

def quark_real_page(url):
    response = requests.get(url)

    # 使用正则匹配 window.location.href 的 URL
    match = re.search(r"window.location.href='(.*?)'", response.text)

    if match:
        redirect_url = match.group(1)
        return redirect_url
    else:
        ""


base_url = "https://www.xmwav.com/sgdetail/178.html?id=178&page="

# 获取第一页内容
response = requests.get(base_url + "1")
tree = html.fromstring(response.content)

# 查找最大页码
page_numbers = tree.xpath('//ul[@class="pagination"]/li/a/text()')
# 过滤出数字并找到最大页码
max_page = max(map(int, filter(str.isdigit, page_numbers))) if page_numbers else 1

all_song_links = []

# 遍历所有页码
for page in range(1, max_page + 1):
    url = base_url + str(page)
    response = requests.get(url)
    tree = html.fromstring(response.content)

    # 获取当前页面歌曲链接（主内容区）
    song_links = tree.xpath('//div[@class="list bgb "]//a[contains(@href, "/mscdetail/")]/@href')
    all_song_links.extend(song_links)

# 打印所有歌曲链接（相对路径）
for link in all_song_links:
    #print(link)
    print(quark_real_page(quark_link(link)))

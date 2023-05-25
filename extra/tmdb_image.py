"""从tmdb中爬取图片"""

import requests

# 设置请求参数
poster_size = 'original'

# 获取海报链接
poster_path = 'pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg'
local_path = "./" + poster_path
print(local_path)
poster_url = f'https://image.tmdb.org/t/p/{poster_size}/{poster_path}'

# 下载海报
response = requests.get(poster_url)

# 存储海报
with open(local_path, 'wb') as f:
    f.write(response.content)

import os

if os.path.exists(local_path):
    print('图片已保存到：', local_path)
else:
    print('图片保存失败')




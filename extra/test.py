"""
:Description: 
:Author: lym
:Date: 2023/05/22/15:28
:Version: 1.0
"""
import requests
from bs4 import BeautifulSoup

def process_html_and_request_img(download_status):
    '''解析html，获取海报，电影信息'''

    imdb_search_path = "https://www.imdb.com/title/"
    imdb_id = "tt0115676"

    # UA伪装
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }

    response = requests.get(url= imdb_search_path + imdb_id, headers=headers)

    soup = BeautifulSoup(response.content, 'lxml')

    # 是否下载缩略图
    if download_status == "0":
        # 海报的URL
        # 缩略图，模糊，可以直接下载
        poster_url = soup.find('img', {'class': 'ipc-image'})['src']
    else:
        # 获取的是点开后的详情图
        # https://m.imdb.com/title/tt0115676/mediaviewer/rm2073856513/?ref_=tt_ov_i
        # 拿到的是后半部分/title/tt0115676/mediaviewer/rm2073856513/?ref_=tt_ov_i
        poster_detail_url = soup.find('a', {'class': 'ipc-lockup-overlay'})['href']
        print(poster_detail_url)
        # 拼接再发请求
        poster_detail_response = requests.get(url=("https://m.imdb.com" + poster_detail_url), timeout=10, headers=headers)

        # 详细页面中获取清晰图片
        detail_soup = BeautifulSoup(poster_detail_response.content, 'lxml')
        target_div1 = detail_soup.find('div', {'class': 'media-viewer'})
        # target_div1 = detail_soup.find('div', {'data-testid': 'media-viewer'})
        target_div2 = target_div1.find_all('div')[4]
        poster_url = target_div2.find('img')['src']

    poster_response = requests.get(poster_url)
    return poster_response.content


if __name__ == '__main__':
    status = "1"
    poster_file = process_html_and_request_img(download_status=status)
    # 保存图片
    with open("./hello" + status + ".jpg", "wb") as f:
        f.write(poster_file)



"""从imdb中爬取图片"""
import math

import requests
import os
import json
import sys
import time
import datetime
import logging
import fcntl

import pandas as pd
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread


def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)


class ImdbSpider():

    def __init__(self):
        # 爬取地址
        self.imdb_search_path = "https://www.imdb.com/title/"
        # UA伪装
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        # 选取清晰度 0模糊1清晰
        self.status = "1"
        # 更新标识
        self.update_flag = 0
        # 最大线程数
        self.MAX_THREADS = 3
        # 存储id的队列
        self.queue = Queue()
        # 用于计算获取资源耗时
        self.get_resource_start_time = datetime.datetime.now()
        self.get_resource_end_time = datetime.datetime.now()
        # 用于计算下载资源耗时
        self.download_start_time = datetime.datetime.now()
        self.download_end_time = datetime.datetime.now()
        # 获取当前时间，用于日志
        self.current_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        self.current_time_str = datetime.datetime.now().strftime('%H:%M:%S')

    def get_current_time(self):

        # 获取当前日期和时间
        current_time = datetime.datetime.now()
        # 将当前日期和时间转换为字符串格式
        self.current_date_str = current_time.strftime('%Y-%m-%d')
        self.current_time_str = current_time.strftime('%H:%M:%S')

        return current_time

    def get_response(self, url, imdb_id):
        i = 0
        # 超时重传，最多5次
        while i < 5:
            if i > 0:
                print(f'第{i + 1}次请求')

            self.get_resource_start_time = self.get_current_time()
            try:
                response = requests.get(url,
                                        timeout=20,
                                        headers=self.headers)
                # 获取资源成功
                if response.status_code == 200:
                    # logging.info(f'get {url} success')
                    print(f'{self.current_date_str} {self.current_time_str}  get {url} success 200 OK')
                    # 正常获取，直接返回
                    return response
                # 如果状态码不对，获取失败，返回None，不再尝试
                # logging.error(f'get {url} status_code error: {response.status_code} movie_id is {self.cur_movie_id}')
                print(
                    f'{self.current_date_str} {self.current_time_str}  get {url} status_code error: {response.status_code} id is {imdb_id}')
                return None
            except requests.RequestException:
                # 如果超时
                # logging.error(f'get {url} error, try to restart {i + 1}')
                print(f'{self.current_date_str} {self.current_time_str}  get {url} error, try to restart {i + 1}')
                i += 1
        # 重试5次都失败，返回None
        return None

    def process_html_and_request_img(self, imdb_id):
        '''解析html，获取海报，电影信息'''

        response = self.get_response(url=(self.imdb_search_path + imdb_id),
                                     imdb_id=imdb_id)

        if response is None:
            return None

        soup = BeautifulSoup(response.content, 'lxml')

        # 是否下载缩略图
        if self.status == "0":
            # 海报的URL
            # 获取缩略图，模糊，可以直接获取地址下载
            poster_url = soup.find('img', {'class': 'ipc-image'})['src']
        else:
            # 获取的是点开后的详情图
            # https://m.imdb.com/title/tt0115676/mediaviewer/rm2073856513/?ref_=tt_ov_i
            # 拿到的是后半部分/title/tt0115676/mediaviewer/rm2073856513/?ref_=tt_ov_i
            poster_detail_url = soup.find('a', {'class': 'ipc-lockup-overlay'})['href']
            # 超链接
            print(poster_detail_url)
            # 拼接再发请求
            poster_detail_response = self.get_response(url=("https://m.imdb.com" + poster_detail_url),
                                                       imdb_id=imdb_id)

            if poster_detail_response is None:
                return None

            # 详细页面中获取清晰图片
            try:
                detail_soup = BeautifulSoup(poster_detail_response.content, 'lxml')
                target_div1 = detail_soup.find('div', {'class': 'media-viewer'})
                # target_div1 = detail_soup.find('div', {'data-testid': 'media-viewer'})
                target_div2 = target_div1.find_all('div')[4]
                poster_url = target_div2.find('img')['src']

                current_time = self.get_current_time()
                print(f"{self.current_date_str} {self.current_time_str}  已获取 {imdb_id} 海报地址，准备下载...")
            except Exception as e:
                print(f'{e}: 页面元素查找错误 imdb_id = {imdb_id}')
                return None

        poster_response = requests.get(poster_url)
        return poster_response.content

    # 爬取
    def download_poster_file(self, imdb_id):
        # 拼接本地地址
        local_directory = "./poster/"
        local_file = imdb_id + ".jpg"
        local_path = local_directory + local_file
        # print("local_path: ", local_path)

        # 解析网页，发送请求获取海报文件
        poster_file = self.process_html_and_request_img(imdb_id)

        if poster_file is not None:
            self.get_current_time()
            print(f"{self.current_date_str} {self.current_time_str}  已获取 {imdb_id} 海报，正在下载...")

            # 下载海报
            with open(local_path, "wb") as f:
                f.write(poster_file)
            # try:
            #     with open(local_path, "wb") as f:
            #         try:
            #             # 尝试获取文件锁
            #             fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            #             f.write(poster_file)
            #         except (IOError, BlockingIOError) as e:  # 获取文件锁失败
            #             self.get_current_time()
            #             print(f"{self.current_date_str} {self.current_time_str}  {e}: 无法获取文件锁，请稍后再试")
            #         finally:
            #             # 释放文件锁
            #             fcntl.flock(f, fcntl.LOCK_UN)
            # except Exception as e:
            #     print(f"{self.current_date_str} {self.current_time_str}  {e}: 请稍后再试")

            # 判断图片保存情况
            self.get_resource_end_time = self.get_current_time()
            if os.path.exists(local_path):
                time_diff = (self.get_resource_end_time - self.get_resource_start_time).total_seconds()
                print(f'{self.current_date_str} {self.current_time_str}  图片已保存到：{local_path}，总耗时：{time_diff}s')
                # 保存后删除键值对并存储起来
                del self.id_movie_dict[imdb_id]
            else:
                print(f'{self.current_date_str} {self.current_time_str}  图片保存失败...')
        else:
            # 响应为None
            print("获取不到海报: ", imdb_id)

            # 添加到失败电影中
            try:
                self.bad_movie_dict[imdb_id] = self.id_movie_dict[imdb_id]
                del self.id_movie_dict[imdb_id]
            except Exception:
                # 写入
                self.bad_movie_dict[imdb_id] = ""
                print(f'海报不在id_movie_dict中：imdb_id = {imdb_id}')
            finally:
                print("写入bad_movie_dict.json")
                with open("./bad_movie_dict.json", 'w') as f:
                    json.dump(self.bad_movie_dict, f)

        # print("udpate_flag = ", self.update_flag)
        # self.update_flag += 1
        # if self.update_flag % 10 == 0:
        #     print("udpate_flag = ", self.update_flag)
        #     print("写入一次文件")
        with open("./id_movie_dict.json", 'w') as f:
            json.dump(self.id_movie_dict, f)
        print('还剩 ', len(self.id_movie_dict), " 张海报...")

    # 根据队列中的id进行下载
    def download_poster_from_queue(self):
        while True:
            if not self.queue.empty():
                # 队列不为空，可以取id出来
                imdb_id = str(self.queue.get())
                # 判断电影是否存在
                try:
                    # 判断是不是失败电影
                    if imdb_id in self.bad_movie_dict:
                        print("电影有问题，不能下载该电影")
                        # 不用处理的就删了方便计数
                        if imdb_id in self.id_movie_dict:
                            del self.id_movie_dict[imdb_id]
                        continue

                    # 判断是否下载过
                    # 路径判断
                    if os.path.exists("./poster/" + imdb_id + ".jpg"):
                        print(f"*****路径判断*****imdb_id：{imdb_id} 在之前已下载完毕！")
                        # 不用处理的就删了方便计数
                        if imdb_id in self.id_movie_dict:
                            del self.id_movie_dict[imdb_id]
                        continue

                    # 作废了
                    # 字典判断 路径中文件不存在时起作用
                    # if imdb_id in self.id_movie_dict:
                    #     # 还没下载过
                    #     # self.download_poster_file(imdb_id=imdb_id)
                    #     pass
                    # else:
                    #     # 下载过了但不存在于路径中
                    #     print("*****字典判断*****imdb_id：", imdb_id, " 在之前已下载完毕！")

                    # 路径中不存在文件，下载文件
                    self.download_start_time = self.get_current_time()

                    self.download_poster_file(imdb_id=imdb_id)

                    self.download_end_time = self.get_current_time()
                    download_time_diff = (self.download_end_time - self.download_start_time).total_seconds()
                    print(f'{self.current_date_str} {self.current_time_str}  海报 {imdb_id} 下载总耗时：{download_time_diff}')
                except Exception as e:
                    # 捕获并处理异常
                    print(f"下载海报 {imdb_id} 时出现异常：{e}")
                    # 先放走
                    continue
            else:
                # 队列为空，说明下载完毕
                print("下载完毕！")
                break

    # 启动多个线程进行图片爬取
    def download_images_in_threads(self):
        threads = []
        for i in range(self.MAX_THREADS):
            t = Thread(target=self.download_poster_from_queue)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    # 创建队列
    def create_queue(self, path, col):
        # 读取DataFrame中的id信息，并存储到队列中
        self.movie_data = pd.read_csv(path, low_memory=False)
        for id in self.movie_data[col]:
            self.queue.put(id)

    def get_dict(self):
        # 判断剩余电影字典保存情况
        if os.path.exists("id_movie_dict.json"):
            print("存在id_movie_dict")
            with open('id_movie_dict.json', 'r', encoding='utf-8') as f:
                self.id_movie_dict = json.load(f)
        else:
            print("不存在id_movie_dict")
            # 字典存储
            self.id_movie_dict = dict(zip(self.movie_data['imdb_id'], self.movie_data['movie_id']))
            with open("id_movie_dict.json", 'w') as f:
                json.dump(self.id_movie_dict, f)
            print("创建成功！")

        # 判断失败电影字典保存情况
        if os.path.exists("./bad_movie_dict.json"):
            print("存在bad_movie_dict")
            with open('./bad_movie_dict.json', 'r', encoding='utf-8') as f:
                self.bad_movie_dict = json.load(f)
        else:
            print("不存在bad_movie_dict")
            # 创建
            self.bad_movie_dict = {}
            # 字典存储
            with open("./bad_movie_dict.json", 'w') as f:
                json.dump(self.bad_movie_dict, f)
            print("创建成功！")


# 主函数
if __name__ == '__main__':

    imdb_spider = ImdbSpider()
    # 创建队列
    imdb_spider.create_queue(path="./data/movie.csv", col='imdb_id')
    # 获取字典
    imdb_spider.get_dict()

    # 爬取
    # imdb_spider.download_poster_from_queue()
    # 启动多个线程进行图片爬取
    imdb_spider.download_images_in_threads()

    # while True:
    #     try:
    #         imdb_spider = ImdbSpider()
    #         # 创建队列
    #         imdb_spider.create_queue(path="./data/movie.csv", col='imdb_id')
    #         # 获取字典
    #         imdb_spider.get_dict()
    #
    #         # 爬取
    #         # imdb_spider.download_poster_from_queue()
    #         # 启动多个线程进行图片爬取
    #         imdb_spider.download_images_in_threads()
    #         break
    #     except Exception as e:
    #         # 如果发生异常，打印异常信息
    #         print('An error occurred:', str(e))
    #         restart_program()

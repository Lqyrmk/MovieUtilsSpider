import os
import shutil
import json

source_dir = r"./poster"
target_dir = r"./poster3"

# 如果目标文件夹不存在，则先创建它
if not os.path.exists(target_dir):
    os.mkdir(target_dir)

with open('poster_dict2.json', 'r', encoding='utf-8') as f:
    poster_dict = json.load(f)

# 遍历源文件夹下的所有文件和子文件夹
for root, dirs, files in os.walk(source_dir):
    images = [f for f in files if f.endswith('.jpg')]
    i = 0
    for image in images:
        i = i + 1
        # 当前文件的路径
        file_path = os.path.join(root, image)
        imdb_id = image.split('.')[0]
        print(f"*****第{i}张, imdb id: {imdb_id}")
        # 判断文件是否符合条件
        if imdb_id in poster_dict:
            # 将文件剪切到目标文件夹中
            target_path = os.path.join(target_dir, image)
            print(f"*****移动文件: {image}, 原路径: {file_path}, 目标路径: {target_path}")
            shutil.move(file_path, target_path)
            del poster_dict[imdb_id]
            print(f"*****还有{len(poster_dict)}张")
print("*****转移完毕！")

# 使用列表推导式和字符串操作，筛选出所有的图片文件，并去掉文件后缀 .jpg
images1 = [f for f in os.listdir(source_dir) if f.endswith('.jpg')]
print("poster总共有", len(images1), "个图片文件。")
images2 = [f for f in os.listdir(target_dir) if f.endswith('.jpg')]
print("poster3总共有", len(images2), "个图片文件。")
print("总共有", len(images1) + len(images2), "个图片文件。")
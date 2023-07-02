import csv
import os
from PIL import Image
from PIL import ImageChops
def compare_images(path_one, path_two):
    """
    比较图片
    :param path_one: 第一张图片的路径
    :param path_two: 第二张图片的路径
    :return: 相同返回 success
    """
    image_one = Image.open(path_one)
    image_two = Image.open(path_two)
    try:
        diff = ImageChops.difference(image_one, image_two)

        if diff.getbbox() is None:
            # 图片间没有任何不同则直接退出
            return "success"
        else:
            return "ERROR: 匹配失败！"

    except ValueError as e:
        return "{0}\n{1}".format(e, "图片大小和box对应的宽度不一致!")

with open('instance/test_prompt.csv', "r", encoding="gb18030") as f:
    reader = csv.reader(f)
    flag=0
    for row in reader:
        if flag==0:flag=1
        else:
            need_test,repo_name,model_name,prompt,hash_id=row
            os.system(f"sudo cog run script/download-weights '%s'"%repo_name)
            if need_test==1:
                os.system(f"sudo cog predict %s %s"%(repo_name,prompt))
                output_path='instance/'+repo_name+"out-0.png"
                if compare_images('instance/'+hash_id+'.png',output_path)=='success':
                    os.system('sudo cog push r8.im/buaadh/%s'%model_name)
            else:
                os.system('sudo cog push r8.im/buaadh/%s'%model_name)

import json
import os
from PIL import Image
from app import api, db
from app.models import Z_user, Imgs, Imgds
from . import home
from flask import request, Response
from flask_restful import Resource, fields, marshal_with
import base64

basedir = 'C:/Users/Administrator/PycharmProjects/zishidianpu1/app/static'


@home.route('/')
def index():
    return 'hello world!!'


class Test10(Resource):
    def get(self):
        return 'hello'


api.add_resource(Test10, '/test10', endpoint='test10')



@home.route('/test100',methods = ['post'])
def test():
    x = request.form.get('url')
    if x =='':
        x = {'url':'none'}
    print(x)
    return x

class ProfileView(Resource):
    resourse_fields = {
        'id': fields.String(),
        'imgd_url': fields.String,
        'imgd_name': fields.String,
        'imgd_title': fields.String,
        'imgd_content': fields.String,
    }

    @marshal_with(resourse_fields)
    def post(self):
        data = request.get_data('id')
        # 将bytes类型转换为json数据
        data = str(data)[2:-1]
        data = json.loads(data)
        id = data['id']


        imgds = Imgds.query.get(id)
        return imgds


api.add_resource(ProfileView, '/select', endpoint='test')


class Test_Upload_changed(Resource):
    def post(self):
        img = request.files.get('photo')
        img_title = request.form.get('imgtitle')
        img_content = request.form.get('imgcontent')
        path = basedir + "/images/"
        file_path = path + img.filename
        img.save(file_path)
        with open(file_path, 'rb') as f:
            image = f.read()
        image = base64.b64encode(image)
        image = '{}'.format(image)
        image = image[2:-1]
        return image


api.add_resource(Test_Upload_changed, '/Test_Upload_changed', endpoint='fadfadfd')


class Upload_changed(Resource):
    def post(self):
        img = request.files.get('photo')  # 获取图片
        img_title = request.form.get('imgtitle')
        spot= request.form.get('spot')
        img_content = request.form.get('imgcontent')
        num = request.form.get('num')  # 选择模型
        num = int(num)-1
        print(num)
        img_list = ['img', 'png', 'IMG', 'PNG', 'jpg', 'JPG', 'jpeg', 'JPEG']  # 判断图片格式
        if img.filename[-3:] or img.filename[-4:] in img_list:
            # 保存用户上传图片
            path = basedir + "/images/"
            file_path = path + img.filename  # 原图保存地址
            img.save(file_path)
            img_compress(file_path, file_path)  # 压缩图片
            # 调用模型
            imaged_file = 'C:/www/style_changed/app/static/style_images/'  # 风格图片保存地址
            model_src = 'C:/www/style_changed/app/fast-neural-style-tensorflow-master/model/'  # 模型地址
            model_list = os.listdir(model_src)  # 模型名称
            model_file = model_src + model_list[num]
            image_file = file_path  # 原图地址
            image_name = str(num) + '--' + img.filename[0:-4]  # 风格图名字
            cmd = 'python C:/www/style_changed/app/fast-neural-style-tensorflow-master/eval.py --model_file ' \
                  + model_file + ' --image_file ' \
                  + image_file + ' --image_name ' + image_name + ' --imaged_file ' + imaged_file
            os.system(cmd)
            # 查重并保存到数据库
            imgds = Imgds.query.all()
            url_list = []
            name_list = []
            for i in imgds:
                data_url = i.imgd_url
                data_name = i.imgd_name
                url_list.append(data_url)
                name_list.append(data_name)
            imgd_url = imaged_file + image_name + '.jpg'
            if imgd_url not in url_list:
                imgds = Imgds(
                    imgd_url=imgd_url,
                    imgd_name=image_name,
                    imgd_title=img_title,
                    imgd_content=img_content,
		    scenic=spot
                )
                db.session.add(imgds)
                db.session.commit()
                a = '上传成功'
            print('风格图保存在：', imgd_url)
            # 返回风格图
            with open(imgd_url, 'rb') as f:
                image = f.read()
            image = base64.b64encode(image)
            image = '{}'.format(image)
            image = image[2:-1]
            # pic_url = Response(image, mimetype="image/jpeg")
            url = 'https://www.yujl.top:5050/' + image_name + '.jpg'
            data = Imgds.query.filter_by(imgd_name = image_name).first()
            data.url = url
            db.session.add(data)
            db.session.commit()
            print(url)

        return url


api.add_resource(Upload_changed, '/upload_changed', endpoint='xfadfadfd')


# 获取文件大小（KB）
def get_img_kb(filePath):
    # filePath图片地址（包含图片本身）
    fsize = os.path.getsize(filePath)
    fsize = fsize / float(1024)

    return round(fsize, 2)


# 对图片进行压缩处理,w>512=>512
def img_compress(from_src, save_src):
    # from_src需要压缩的图片地址,save_src压缩后图片的保存地址。（地址中包含图片本身）
    img = Image.open(from_src)
    w, h = img.size
    if w > 512:
        h = h * (512 / w)
        w = w * (512 / w)

    img = img.resize((int(w), int(h)), Image.ANTIALIAS)
    img.save(save_src, optimize=True, quality=85)  # 质量为85效果最好
    if get_img_kb(save_src) > 60:
        img.save(save_src, optimize=True, quality=75)

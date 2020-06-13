import datetime
import os
import uuid

from threading import Thread
from PIL import Image
from flask import request, jsonify

from app import db, app
from app.models import Spotinf, Articles, Userarticle, User, Comment
from app.routes import spotinfprocess
from app.routes.login import Login
from app.routes.createId import IdWorker

from . import home


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    print(datetime.datetime.now().strftime("%Y%m%d"))
    return filename


@home.route('/')
def index():
    return 'hello'


log = Login()


@home.route('/login/', methods=['GET'])
def login():
    res = request.args.to_dict()
    log.set(res['code'])
    openid = log.sent_out()
    try:
        user = User(
            userid=openid['openid'],
            username=res['username'],
            userurl=res['userurl']
        )
        db.session.add(user)
        db.session.commit()
    except:
        pass
    return openid['openid']


#  景点搜索
@home.route('/select/')
def select():
    data = request.args.to_dict()
    data = data['data']
    res = Spotinf.query.filter(Spotinf.spotname.like("%" + data + "%") if data is not None else "").all()
    info = [{"spotid": str(1263028239769669632), "spotname": "其他"}]
    for item in res:
        info.append({"spotid": str(item.spotid), "spotname": item.spotname})

    return jsonify(info)


idworker = IdWorker()


@home.route('/upload/', methods=["GET", "POST"])
def upload():
    img = request.files.get('imgFile')  # 获取图片
    data = request.form.to_dict()  # 获取表单中其他数据
    img_name = change_filename(img.filename)  # 给图片生成名字
    img_url = app.config["UP_DIR"] + 'upload/'  # 将图片保存至转换前的路径
    img.save(img_url + img_name)
    if int(data['num']) != -1:  # 判断是否转换风格
        async_slow_function(img_url, img_name, int(data['num']))  # 调用多线程
        imgurl = 'https://www.yujl.top:5050/' + str(data['num']) + '--' + img_name  # 转换后的地址

    else:
        imgurl = 'https://www.yujl.top:5050/' + img_name
    article_id = idworker.get_id()  # 生成id
    articles = Articles(
        articleid=article_id,
        title=data['title'],
        content=data['content'],
        imgurl=imgurl,
        spotid=data['spotid'],
        username=data['username'],
        good=0,
        time=datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        userid = data['userid']

    )
    db.session.add(articles)
    db.session.commit()



    return jsonify({"code": data['num'], "imgurl": imgurl})


@home.route('/test/')
def test():
    # async_slow_function(app.config['UP_DIR'] + 'upload/before/', '学校背景.jpg', 1, )  # 调用多线程
    # print(app.config["SECRET_KEY"])
    filename = change_filename("daoshdasdasn.jpg")
    return filename


@home.route('/lstzs/')
def lstzs():
    res = [
        {"id": "-1", "name": "不转换", "url": 'https://www.yujl.top:5050/imgs/20151017041702855.jpg'},
        {"id": "0", "name": "模型1", "url": 'https://www.yujl.top:5050/imgs/0--1263450747610206208.jpg'},
        {"id": "1", "name": "模型2", "url": 'https://www.yujl.top:5050/imgs/1--1263450360094265344.jpg'},
        {"id": "2", "name": "模型3", "url": 'https://www.yujl.top:5050/imgs/2--1263450428796964864.jpg'},
        {"id": "3", "name": "模型4", "url": 'https://www.yujl.top:5050/imgs/3--1263450487294922752.jpg'},
        {"id": "4", "name": "模型5", "url": 'https://www.yujl.top:5050/imgs/4--1263450552902225920.jpg'},
        {"id": "5", "name": "模型6", "url": 'https://www.yujl.top:5050/imgs/5--1263450256796946432.jpg'},
        {"id": "6", "name": "模型7", "url": 'https://www.yujl.top:5050/imgs/6--1263450618463391744.jpg'},
    ]
    return jsonify(res)


#  风格迁移
def change(file_path, filename, num):  # 图片地址，图片名称，模型号码
    img_compress(file_path + filename, file_path + filename)  # 压缩图片
    # 调用模型
    model_src = app.config["UP_DIR"] + 'fast-neural-style-tensorflow-master/model/'  # 模型地址
    model_list = os.listdir(model_src)  # 模型名称
    model_file = model_src + model_list[num]
    img_name = str(num) + '--' + filename  # 转换后的风格图名称
    model_url = app.config["UP_DIR"] + 'fast-neural-style-tensorflow-master/eval.py'
    cmd = 'python ' + model_url + ' --model_file ' + model_file + ' --image_file ' + file_path + filename + \
          ' --image_name ' + img_name + ' --imaged_file ' + app.config['UP_DIR'] + 'upload/'
    os.system(cmd)


'''
cmd = 'python C:/www/style_changed/app/fast-neural-style-tensorflow-master/eval.py --model_file ' \
                  + model_file + ' --image_file ' \
                  + image_file + ' --image_name ' + image_name + ' --imaged_file ' + imaged_file

'''

'''
python D:\dev\transferstyle\app\static/fast-neural-style-tensorflow-master/eval.py --model_fileD:\dev\transferstyle\app\static/fast-neural-style-tensorflow-master/model/denoised_starry.ckpt-done --image_fileD:\dev\transferstyle\app\static/upload/ --image_name 1263109410251739136.jpg --imaged_file D:\dev\transferstyle\app\static/upload/after/1--1263358220353802240.jpg



'''


@home.route('/get/articles/')
def get_articles():
    data = request.args.to_dict()
    print(data)
    articles = Articles.query.paginate(page=int(data['page']), per_page=int(data['limit']))
    articles_count = Articles.query.count()
    if articles_count % int(data["limit"]) == 0:
        maxpage = articles_count // int(data["limit"])
    else:
        maxpage = (articles_count // int(data["limit"])) + 1
    articles_list = [{"articleid": article.articleid, "title": article.title, "content": article.content,
                      "imgurl": article.imgurl, "spotid": article.spotid, "good": article.good, "time": article.time,
                      "username": article.username,"userid": article.userid} for article in articles.items]
    info = []
    for i in range(len(articles_list)):
        user = User.query.filter_by(userid=articles_list[i]['userid']).first()
        spotinf = Spotinf.query.filter_by(spotid = articles_list[i]['spotid']).first()
        articles_list[i]["userurl"] = user.userurl
        articles_list[i]["spotname"] = spotinf.spotname
        info.append(articles_list[i])

    return jsonify({
        "info": info,
        "maxpage": maxpage
    })


#  增加景点名字，url为包含景点名字的word文档地址
@home.route('/spotinf/add/')
def spotinfadd():
    url = request.args.to_dict()
    ls = spotinfprocess.opens(url['url'])
    for i in ls:
        spotid = idworker.get_id()
        spotinf = Spotinf(
            spotid=spotid,
            spotname=i,
            userid='1263023717747920896'
        )
        db.session.add(spotinf)
        db.session.commit()
    return jsonify({"code": "1", "msg": "增加成功"})


@home.route('/get/article/')
def get_article():
    data = request.args.to_dict()
    userid = data["userid"]
    articles = Articles.query.filter_by(userid=userid).all()
    info = [{"articleid": article.articleid, "title": article.title, "content": article.content,
                      "imgurl": article.imgurl, "spotid": article.spotid, "good": article.good, "time": article.time,
                      "username": article.username,"userid": article.userid} for article in articles]
    return jsonify({
        "info":info,
        "msg":"根据用户获取文章"
    })


@home.route('/add/comment/')
def add_comment():
    data = request.args.to_dict()
    user = User.query.filter_by(userid = data["userid"]).first()
    comment = Comment(
        articleid = data["articleid"],
        commentitem = data["content"],
        commentid = data["userid"],
        commentname = user.username,
        time=datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({"msg":"添加评论"})

@home.route('/get/comment/')
def get_comment():
    data = request.args.to_dict()
    comment = Comment.query.filter_by(articleid = data['articleid']).all()
    info = [{"articleid":i.articleid,"content":i.commentitem,"userid":i.commentid,"username":i.commentname,"time":i.time} for i in comment]
    return jsonify({
        "info":info,
        "msg":"获取文章的评论"
    })
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


# 多线程
def async_slow_function(file_path, filename, num):
    thr = Thread(target=change, args=[file_path, filename, num])
    thr.start()
    return thr

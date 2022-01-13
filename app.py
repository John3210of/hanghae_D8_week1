import os
import time
from datetime import datetime
from string import ascii_uppercase, digits, ascii_lowercase
import json
from functools import wraps
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash, abort
from bson import ObjectId
from pymongo import MongoClient
from random import random
from bson.json_util import dumps

app = Flask(__name__)

# client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://13.125.81.75', 27017, username="test", password="test")
db = client.d8_server_db

SECRET_KEY = 'SPARTA'

import jwt

# 비밀번호를 암호화하여 DB에 저장
import hashlib


# 로그인 후 권한 부여 (Authority) 함수
def login_required(f):                                      # (1) 함수가 인자로 들어오므로 f를 받음
    @wraps(f)                                               # (2) 데코레이트 함
    def decorated_function(*args, **kwargs):                # (3) 데코레이티드 된 함수라는 표현
        tokenreceive = request.cookies.get('token')
        if tokenreceive is None or tokenreceive == "":      # (4) 실제 작동하는 구간
            return render_template('login.html')            # (5) 현재 사용자의 토큰을 확인하고 없으면 로그인 페이지로 연결
        return f(*args, **kwargs)                           # (6) args는 딕셔너리의 키를 얘기하는거고 kw는 키워드, 벨류 값임!
    return decorated_function


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def jsonify(data):
    return json.loads(json.dumps(data, cls=JSONEncoder))


@app.route('/')
def list_main():
    token_receive = request.cookies.get('token')
    login_status = True if token_receive is not None else False

    cursor = db.gameboard.find().sort('date', -1)  # date 역순(최근)
    result = dumps(list(cursor), cls=JSONEncoder, ensure_ascii=False) # bson -> json
    return render_template('index.html', items=result, login_status=login_status) # jinja 적용


# 최근 날짜부터 보여주기
@app.route('/api/list/dateOrder', methods=['GET'])
def view_list_date_order():
    all_lists = list(db.gameboard.find().sort('date',-1)) # date 역순(최근)
    return jsonify({'all_lists': dumps(all_lists)}) # object id 사용하기 위해 dumps 사용


# 좋아요가 많은 순으로 보여주기
@app.route('/api/list/likeOrder', methods=['GET'])
def view_list_like_order():
    all_lists = list(db.gameboard.find().sort('likes',-1)) # 좋아요 역순(많은 순)
    return jsonify({'all_lists': dumps(all_lists)}) # object id 사용하기 위해 dumps 사용


# 황금밸런스만 보여주기
@app.route('/api/list/goldenBalance', methods=['GET'])
def view_list_golden():
    golden_lists = list(db.gameboard.find().sort('date',-1)) # date 역순(최근)
    return jsonify({'all_lists': dumps(golden_lists)}) # object id 사용하기 위해 dumps 사용


# 이미지를 저장하는 서버경로와 및 저장을 허용하는 확장자를 분류합니다.
# 로컬에서는 절대경로로 "/Users/mac_cloud/Desktop/images" 로 지정하여 사용하였습니다.
# /home/ubuntu/sparta/balancegame/static/img server path

BOARD_IMAGE_PATH = "./static/img/uploadimg"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# 업로드 하는 이미지의 크기를 제한했으며, 최대 15MB까지 가능합니다.
app.config['BOARD_IMAGE_PATH'] = BOARD_IMAGE_PATH
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024

# 만약 저장 경로가 없으면 디렉토리 폴더를 만들어 주어 오류를 방지합니다.
if not os.path.exists(app.config['BOARD_IMAGE_PATH']):
    os.mkdir(app.config['BOARD_IMAGE_PATH'])


# 파일을 받아올 때 확장자를 검사하는 함수입니다.
# 파일 네임을 가장 마지막의 . 단위로 끊고 index[1] 에 있는 확장자를 가져와 ALLOWED_EXTENSIONS에 포함되는지 검사합니다.
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


# 서버에 사진이 저장되었을 때 임의의 문자+숫자 조합으로 파일명을 변경 해 주는 함수입니다.
# 이는 파일명을 통해 터미널의 관리자 권한을 탈취하는 해킹 방법을 막기 위해 사용하였습니다.
def rand_generator(length=8):
    chars = ascii_lowercase + ascii_uppercase + digits
    return ''.join(random.sample(chars, length))


# 이미지 업로드 관련 함수이며, filename을 random.jpg으로 하여 서버에 저장합니다.
# 위에서 작성한 rand_generator 함수를 활용하였습니다.
@app.route("/upload_image", methods=["POST"])
def upload_image():
    if request.method == "POST":
        file = request.files["image"]
        if file and allowed_file(file.filename):
            filename = "{}.jpg".format(rand_generator())
            savefilepath = os.path.join(app.config["BOARD_IMAGE_PATH"], filename)
            file.save(savefilepath)
            return url_for("board_images", filename=filename)


# current_time(datetime)을 우리가 보는 시간으로 바꿔주는 함수
@app.template_filter('format_datetime')
def format_datetime(value):
    if value is None:
        return ""  # 만약 시간값이 없다면 공백을 반환

    now_timestamp = time.time()  # offset = utc time과 한국의 time 시차 (+9:00)
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    value = datetime.fromtimestamp((int(value) / 1000)) + offset
    return value.strftime('%Y-%m-%d %H:%M:%S')


# [게임 작성] (Create)
@app.route('/post', methods=['GET', 'POST'])
@login_required
def list_post():
    if request.method == "POST":
        token = request.cookies.get('token')
        token_data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_idx = db.user.find_one({'id': token_data['id']})
        # print(token)
        if token is not None:
            token_data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_name = request.form.get("user_name"),
            # 사용자의 이름을 보내줍니다.
            # 글 작성 시 작성자의 이름을 바꿀 수 없도록 readonly 속성을 부여하였습니다.
            writer_id = user_idx['_id'],
            # 벨런스 게임을 진행 할 두 사진의 데이터를 받아옵니다.
            img_full_url_left = request.form.get("img_url_left"),
            img_full_url_right = request.form.get("img_url_right"),
            # 벨런스 게임을 진행 할 두 사진의 이름을 받아옵니다.
            # 이 사진의 이름은 제목을 자동으로 생성하는 데 사용 될 것입니다.
            img_title_left = request.form.get("img_title_left"),
            img_title_right = request.form.get("img_title_right"),
            # 사진 또는 벨런스게임에 대한 설명을 추가하는 텍스트를 받아옵니다.
            contents = request.form.get("contents")
            # 게시글이 올라가는 날짜 및 시간을 받아옵니다.
            # 진자에서 사용 할 때는 작성일 : {{post.pubdate|format_datetime}} 형태로 사용하시면 됩니다 !
            current_utc_time = (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-7])

            img_url_left = str(img_full_url_left).replace('"', ',')
            thumbnail_left = img_url_left.split(',')
            img_url_right = str(img_full_url_right).replace('"', ',')
            thumbnail_right = img_url_right.split(',')

            post = {
                "user_name": str(user_name)[2:-3],
                "writer_id": str(writer_id)[2:-3],
                "img_title_left": str(img_title_left)[2:-3],
                "img_title_right": str(img_title_right)[2:-3],
                "img_url_left": str(thumbnail_left[1]),
                "img_url_right": str(thumbnail_right[1]),
                "contents": contents,
                "count_right": 0,
                "count_left": 0,
                "likes": 0,
                "views": 0,
                "date": current_utc_time
            }

            idx = db.gameboard.insert_one(post)

            # mongoDB의 고유 번호(_id)를 주소에 출력합니다.
            # 이는 게시글의 상세페이지 보기와 같으며 게임을 만든 후 상세페이지로 넘겨줍니다.
            return redirect(url_for('list_detail', idx=idx.inserted_id))

    else:
        token = request.cookies.get('token')
        # print(token)
        if token is not None:
            token_data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # print(token_data)
            result_name = db.user.find_one({'id': token_data['id']})
            # print(result_name)
        # 아무런 입력이 없이 GET 방식으로 들어왔을때, 게임 작성 페이지로 전환해줍니다.
        return render_template("post.html", user_name=result_name['name'])


# [게시글 수정] (Update)
@app.route("/edit", methods=["GET", "POST"])
@login_required
def list_edit():
    idx = request.args.get("idx")
    token = request.cookies.get('token')
    data = db.gameboard.find_one({"_id": ObjectId(idx)})

    print(idx)
    print(token)
    print(data)

    if request.method == "GET":
        if data is None:
            return redirect(url_for("list_main"))

        token_data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        result_name = db.user.find_one({'id': token_data['id']})

        if token_data is None:
            return redirect(url_for("list_main"))
        else:
            if token_data['id'] == result_name['id']:
                return render_template("edit.html", idx=idx, data=data)
            else:
                return redirect(url_for("list_main"))
    if request.method == "POST":

        img_title_left = request.form.get("img_title_left"),
        img_title_right = request.form.get("img_title_right"),
        contents = request.form.get("contents")

        db.gameboard.update_one({"_id": ObjectId(idx)}, {
            "$set": {
                "img_title_left": str(img_title_left),
                "img_title_right": str(img_title_right),
                "contents": contents,
            }
        })
        return redirect(url_for("list_detail", idx=idx))

# 상세 페이지 게시글에 관한 데이터 DB에서 받아오기 (코멘트도 포함)
@app.route('/detail')
def list_detail():
    idx_receive = request.args.get('idx')
    post = db.gameboard.find_one({'_id': ObjectId(idx_receive)})
    post['_id'] = str(post['_id'])

    # DB에 문자열로 들어가 있는 writer_id의 값만 추출
    # (ObjectId('61df8243f40ae8e09654d55d'),) -> writer_id가 이런 형태로 들어가 있음
    writer_id_string = post['writer_id']
    writer_id_list = writer_id_string.split("'")
    writer_id_sanitised = writer_id_list[1]  # 61df8243f40ae8e09654d55d -> 추출된 모습

    count_left = post['count_left']
    count_right = post['count_right']

    # 만약 두 아이템 모두 선택한 사람이 0명이라면, 각각의 %값을 0으로 할당한다. (ZeroDivisionError 방지)
    if post['count_left'] == 0 and post['count_right'] == 0:
        percent_left = 0
        percent_right = 0
    # 그렇지 않다면, 각 아이템의 카운트를 두 아이템의 카운트를 더한 값으로 나누고 100을 곱하여 %(선택된 비율)를 구한다.
    else:
        percent_left = round((count_left / (count_left + count_right)) * 100, 1)
        percent_right = round((count_right / (count_left + count_right)) * 100, 1)

    # 두 아이템의 % 차이가 2% 이상이거나, 두 아이템 모두 선택한 사람이 0명인 경우에는 황금밸런스가 아니다.
    # (두 아이템의 % 차이가 2% 미만일 경우에 황금밸런스라고 간주함)
    if abs(percent_left - percent_right) >= 2 or (count_left == 0 and count_right == 0):
        is_gold_balance = False
    else:
        is_gold_balance = True

    # 쿠키에 있는 토큰을 받아옴
    token_receive = request.cookies.get('token')

    # if문 블록 밖에서 isWriter 변수를 사용하기 위해 블록 밖에서 선언해 줌
    isWriter = 0

    # 로그인하지 않은 상태: login_status가 False
    # 로그인을 한 상태: login_status가 True
    if token_receive is None:
        login_status = False
    else:
        login_status = True
        # (토큰이 있을 경우에만) 받아온 토큰을 decode하여 payload를 받아옴
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # payload에 있는 id와 DB에 있는 id를 비교하여 일치하는 유저의 정보를 DB에서 가져옴
        user_info = db.user.find_one({'id': payload['id']})
        user_id_sanitised = str(user_info['_id'])

        # 게시글을 작성한 사람의 id와 로그인한 유저의 아이디가 같으면 isWriter 값이 true로 설정됨
        isWriter = writer_id_sanitised == user_id_sanitised

    # 현재 게시글의 id와 현재 게시글에서 보여질 댓글의 postid가 일치하는 댓글들만 받아옴
    comments = list(db.comments.find({'postid': post['_id']}))
    comments_count = len(comments)

    return render_template('detail.html', post=post, percent_left=percent_left, percent_right=percent_right,
                           comments=comments, comments_count=comments_count, is_gold_balance=is_gold_balance,
                           login_status=login_status, isWriter=isWriter)


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/regist')
def register():
    return render_template('regist.html')


# 상세 페이지 댓글 추가
@app.route('/api/comment', methods=['POST'])
@login_required
def add_comment():
    # 쿠키에 있는 토큰을 받아옴
    token_receive = request.cookies.get('token')

    # 클라이언트로부터 게시글의 아이디를 받아옴
    post_id_receive = request.form['post_id_give']
    try:
        # 받아온 토큰을 decode하여 payload를 받아옴
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # payload에 있는 id와 DB에 있는 id를 비교하여 일치하는 유저의 정보를 DB에서 가져옴
        user_info = db.user.find_one({'id': payload['id']})

        # 클라이언트로부터 받아온 코멘트를 comment_receive 변수에 넣음
        comment_receive = request.form['comment_give']

        # 현재 날짜(=등록 시간)를 생성하여 원하는 포맷으로 변경하여 date_string 변수에 넣음
        date = datetime.now()
        date_string = date.strftime('%Y-%m-%d %H:%M')

        # 가져온 유저의 정보에서 name을 추출해서 DB에 넣어줌(코멘트 내용 & 등록 시간 & 게시글의 id과 함께)
        doc = {
            'name': user_info['name'],
            'contents': comment_receive,
            'posttime': date_string,
            'postid': post_id_receive
        }
        db.comments.insert_one(doc)
        return jsonify({'result': 'success', 'msg': '코멘트 등록 완료!'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for('list_main'))


# 상세 페이지 댓글 삭제
@app.route('/api/comment/<idx>', methods=['DELETE'])
@login_required
def delete_comment(idx):
    db.comments.delete_one({'_id': ObjectId(idx)})
    return jsonify({'msg': '코멘트 삭제 완료!'})


# 상세 페이지에서 선택한 아이템의 카운트 증가
@app.route('/api/count/<idx>', methods=['PUT'])
@login_required
def increase_count(idx):
    position_receive = request.form['position_give']
    title_receive = request.form['title_give']
    target_post = db.gameboard.find_one({'_id': ObjectId(idx)})

    # 왼쪽에 있는 아이템을 선택했을 경우, 왼쪽 아이템의 count 값을 하나 증가시킵니다.
    if position_receive == 'left':
        current_count_left = target_post['count_left']
        new_count_left = current_count_left + 1
        db.gameboard.update_one({'_id': ObjectId(idx)}, {'$set': {'count_left': new_count_left}})
    # 오른쪽에 있는 아이템을 선택했을 경우, 오른쪽 아이템의 count 값을 하나 증가시킵니다.
    else:
        current_count_right = target_post['count_right']
        new_count_right = current_count_right + 1
        db.gameboard.update_one({'_id': ObjectId(idx)}, {'$set': {'count_right': new_count_right}})

    return jsonify({'msg': '당신의 선택은 ' + title_receive + '이군요!'})


# 게시글 좋아요
@app.route('/api/like/<idx>', methods=['PUT'])
@login_required
def like_post(idx):
    target_post = db.gameboard.find_one({'_id': ObjectId(idx)})
    current_like = target_post['likes']
    new_like = current_like + 1
    db.gameboard.update_one({'_id': ObjectId(idx)}, {'$set': {'likes': new_like}})
    return jsonify({'msg': '좋아요 완료👍'})


# 게시글 조회수 증가
@app.route('/api/view/<idx>', methods=['PUT'])
def increase_view(idx):
    increased_receive = request.form['increased_give']
    db.gameboard.update_one({'_id': ObjectId(idx)}, {'$set': {'views': increased_receive}})
    return jsonify({'msg': 'success'})


# 게시글 삭제
@app.route('/api/post/<idx>', methods=['DELETE'])
@login_required
def delete_post(idx):

    db.gameboard.delete_one({'_id': ObjectId(idx)})
    return jsonify({'msg': ' 게시글이 삭제되었습니다.'})


# 회원가입 api
@app.route('/api/regist', methods=['POST'])
def api_regist():
    # input 받기
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    # pw를 암호화
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    # db로 저장
    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'name': name_receive})
    return jsonify({'result': 'success'})


# id 중복확인 api
@app.route('/api/regist/check_dup', methods=['POST'])
def check_dup():
    id_receive = request.form['id_give']
    # 중복 여부에따라 T/F로 return
    exists = bool(db.user.find_one({"id": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 로그인 api
@app.route('/api/login', methods=['POST'])
def api_login():
    # id, pw 받기
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        payload = {
            'id': id_receive,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')  # .decode('utf-8')
        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
    app.secret_key = "**"
    app.debug = True
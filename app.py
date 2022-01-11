from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient

# client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://13.125.81.75', 27017, username="test", password="test")
db = client.dbsparta_d8

SECRET_KEY = 'SPARTA'

import jwt

# 비밀번호를 암호화하여 DB에 저장
import hashlib

from bson import json_util, ObjectId
import json

import datetime

@app.route('/')
def list_main():
    return render_template('index.html')


@app.route('/post')
def list_post():
    return render_template('post.html')

# [상세 페이지 게시글에 관한 데이터 DB에서 받아오기 API]
@app.route('/detail')
def list_detail():
    id_receive = request.args.get('id')
    post = db.posts.find_one({'_id': ObjectId(id_receive)})
    percent_left = round((post['count_left'] / (post['count_left'] + post['count_right'])) * 100, 1)
    percent_right = round((post['count_right'] / (post['count_left'] + post['count_right'])) * 100, 1)

    if abs(percent_left - percent_right) < 2:
        is_gold_balance = True
    else:
        is_gold_balance = False

    comments = list(db.comments.find({}))
    comments_count = len(list(db.comments.find({})))
    return render_template('detail.html', post=post, percent_left=percent_left, percent_right=percent_right, comments=comments, comments_count=comments_count, is_gold_balance=is_gold_balance)

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/regist')
def register():
    return render_template('regist.html')


# [회원가입 API]
# id, pw, name을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/regist', methods=['POST'])
def api_regist():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'name': name_receive})

    return jsonify({'result': 'success'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
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
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# [상세 페이지 댓글 추가 API]
@app.route('/api/comment', methods=['POST'])
def add_comment():
    comment_receive = request.form['comment_give']

    date = datetime.datetime.now()
    date_string = date.strftime('%Y-%m-%d %H:%M')

    doc = {
       "contents": comment_receive,
       "posttime": date_string
    }
    db.comments.insert_one(doc)
    return jsonify({'msg': '코멘트 등록 완료!'})


# [상세 페이지 댓글 삭제 API]
@app.route('/api/comment/<id>', methods=['DELETE'])
def delete_comment(id):
    db.comments.delete_one({'_id': ObjectId(id)})
    return jsonify({'msg': '코멘트 삭제 완료!'})


# [게시글 좋아요 API]
@app.route('/api/like/<id>', methods=['PUT'])
def like_post(id):
    target_post = db.posts.find_one({'_id': ObjectId(id)})
    current_like = target_post['like']
    new_like = current_like + 1
    db.posts.update_one({'_id': ObjectId(id)}, {'$set': {'like': new_like}})
    return jsonify({'msg': '좋아요 완료👍'})


# [상세 페이지에서 선택한 아이템의 카운트 증가 API]
@app.route('/api/count/<id>', methods=['PUT'])
def increase_count(id):
    position_receive = request.form['position_give']
    title_receive = request.form['title_give']
    target_post = db.posts.find_one({'_id': ObjectId(id)})

    # 왼쪽에 있는 아이템을 선택했을 경우, 왼쪽 아이템의 count 값을 하나 증가시킵니다.
    if position_receive == 'left':
        current_count_left = target_post['count_left']
        new_count_left = current_count_left + 1
        db.posts.update_one({'_id': ObjectId(id)}, {'$set': {'count_left': new_count_left}})
    # 오른쪽에 있는 아이템을 선택했을 경우, 오른쪽 아이템의 count 값을 하나 증가시킵니다.
    else:
        current_count_right = target_post['count_right']
        new_count_right = current_count_right + 1
        db.posts.update_one({'_id': ObjectId(id)}, {'$set': {'count_right': new_count_right}})

    return jsonify({'msg': '당신의 선택은 ' + title_receive + '이군요!'})


# [게시글 조회수 증가 API]
@app.route('/api/view/<id>', methods=['PUT'])
def increase_view(id):
    increased_receive = request.form['increased_give']
    db.posts.update_one({'_id': ObjectId(id)}, {'$set': {'view': increased_receive}})
    return jsonify({'msg': 'success'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

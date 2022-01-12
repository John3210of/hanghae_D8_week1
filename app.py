from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)

from bson import ObjectId
from pymongo import MongoClient

# client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://13.125.81.75', 27017, username="test", password="test")
db = client.dbsparta_d8

SECRET_KEY = 'SPARTA'

import jwt

# 비밀번호를 암호화하여 DB에 저장
import hashlib


@app.route('/')
def list_main():
    return render_template('index.html')


@app.route('/post')
def list_post():
    return render_template('post.html')


# 상세 페이지 게시글에 관한 데이터 DB에서 받아오기
@app.route('/detail')
def list_detail():
    idx_receive = request.args.get('idx')
    post = db.gameboard.find_one({'_id': ObjectId(idx_receive)})
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

    comments = list(db.comments.find({}))
    comments_count = len(comments)

    return render_template('detail.html', post=post, percent_left=percent_left, percent_right=percent_right,
                           comments=comments, comments_count=comments_count, is_gold_balance=is_gold_balance)


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/regist')
def register():
    return render_template('regist.html')


# 상세 페이지 댓글 추가
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


# 상세 페이지 댓글 삭제
@app.route('/api/comment/<idx>', methods=['DELETE'])
def delete_comment(idx):
    db.comments.delete_one({'_id': ObjectId(idx)})
    return jsonify({'msg': '코멘트 삭제 완료!'})


# 상세 페이지에서 선택한 아이템의 카운트 증가
@app.route('/api/count/<idx>', methods=['PUT'])
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

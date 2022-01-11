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
    post = db.posts.find_one({'_id': ObjectId(idx_receive)})
    percent_left = round((post['count_left'] / (post['count_left'] + post['count_right'])) * 100, 1)
    percent_right = round((post['count_right'] / (post['count_left'] + post['count_right'])) * 100, 1)

    if abs(percent_left - percent_right) < 2:
        is_gold_balance = True
    else:
        is_gold_balance = False

    comments = list(db.comments.find({}))
    comments_count = len(list(db.comments.find({})))
    return render_template('detail.html', post=post, percent_left=percent_left, percent_right=percent_right,
                           comments=comments, comments_count=comments_count, is_gold_balance=is_gold_balance)


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

#####

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


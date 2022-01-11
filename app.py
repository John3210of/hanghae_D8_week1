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


@app.route('/detail')
def list_detail():
    return render_template('detail.html')


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/regist')
def register():
    return render_template('regist.html')




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
    #중복 여부에따라 T/F로 return
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
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')  #.decode('utf-8')
        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


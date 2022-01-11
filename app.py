from flask import Flask, render_template, jsonify, request, session, redirect, url_for
app = Flask(__name__)
from pymongo import MongoClient

# client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://13.125.81.75', 27017, username="test", password="test")
db = client.dbsparta_d8

SECRET_KEY = 'SPARTA'

import jwt
from bson.json_util import dumps


@app.route('/')
def list_main():
    cursor = db.gameboard.find().sort('date', -1)  # date 역순(최근)
    result = dumps(list(cursor), ensure_ascii=False)
    return render_template('index.html', items=result) # jinja 적용


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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
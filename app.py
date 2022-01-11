import json

from bson.json_util import dumps
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, session

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.list_db
# client = MongoClient('mongodb://test:test@localhost', 27017)
# db = client.list_db

@app.route('/')
def list_main():
    return render_template('index.html')

# class Encode(json.JSONEncoder):
#     def default(self, o):
#         if isinstance(o, ObjectId):
#             return str(o)
#         return json.JSONEncoder.default(self, o)

# 최근 날짜부터 보여주기
@app.route('/api/list/dateOrder', methods=['GET'])
def view_list_date_order():
    all_lists = list(db.goldenBalance.find().sort('date',-1))
    return jsonify({'all_lists': dumps(all_lists)})

# 좋아요가 많은 순으로 보여주기
@app.route('/api/list/likeOrder', methods=['GET'])
def view_list_like_order():
    all_lists = list(db.goldenBalance.find({}, {'_id': False}).sort('likes',-1))
    return jsonify({'all_lists': dumps(all_lists)})

# 황금밸런스만 보여주기
@app.route('/api/list/goldenBalance', methods=['GET'])
def view_list_golden():
    golden_lists = list(db.goldenBalance.find().sort('date',-1))
    # golden_lists = list(db.goldenBalance.find({'$where':"(this.suggestion_right + this.suggersion_left)/(this.suggestion_right - this.suggersion_left)*100 <= 3 "}))
    # pipeline = [
    #     {'$group' : {'_id':'$_id', 'balanced':{'$abs':{'$subtract':['$suggestion_left','$suggestion_right']}}}},
    #     {'$match' : {'balanced' : {'$lte': 3}}}
    # ]
    #
    # golden_lists = list(db.goldenBalance.aggregate(pipeline))
    # print(golden_lists)
    return jsonify({'all_lists': dumps(golden_lists)})

@app.route('/post')
def list_post():
    return render_template('post.html')

@app.route('/detail')
def list_detail():
    return render_template('detail.html')

@app.route('/login')
def list_login():
    return render_template('login.html')

@app.route('/regist')
def list_regist():
    return render_template('regist.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
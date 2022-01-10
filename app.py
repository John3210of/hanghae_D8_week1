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
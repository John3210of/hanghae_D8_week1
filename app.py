from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, session, url_for, redirect, flash, send_from_directory
from bson import json_util, ObjectId
from string import digits, ascii_uppercase, ascii_lowercase
import random
import os


client = MongoClient('mongodb://13.125.81.75', 27017, username="test", password="test")
db = client.dbsparta_d8

SECRET_KEY = 'SPARTA'

app = Flask(__name__)


import datetime


@app.route('/')
def list_main():
    return render_template('post.html')


# 이미지를 저장하는 서버경로와 및 저장을 허용하는 확장자를 분류합니다.
# 로컬에서는 절대경로로 "/Users/mac_cloud/Desktop/images" 로 지정하여 사용하였습니다.
BOARD_IMAGE_PATH = "/Users/mac_cloud/Desktop/images"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])

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


# [게임 작성] (Create)
@app.route('/post', methods=['GET', 'POST'])
def list_post():

    if request.method == "POST":
        # 사용자의 id를 보내줍니다.
        # 글 작성 시 작성자의 이름을 바꿀 수 없도록 readonly 속성을 부여하였습니다.
        user_id = request.form.get("user_id")
        # 벨런스 게임을 진행 할 두 사진의 데이터를 받아옵니다.
        img_url_left = request.form.get("img_url_left"),
        img_url_right = request.form.get("img_url_right"),
        # 벨런스 게임을 진행 할 두 사진의 이름을 받아옵니다.
        # 이 사진의 이름은 제목을 자동으로 생성하는 데 사용 될 것입니다.
        img_title_left = request.form.get("img_title_left"),
        img_title_right = request.form.get("img_title_left"),
        # 사진 또는 벨런스게임에 대한 설명을 추가하는 텍스트를 받아옵니다.
        contents = request.form.get("contents")

        post = {
            "user_id": user_id,
            "img_title_left": img_title_left,
            "img_title_right": img_title_right,
            "img_url_left": img_url_left,
            "img_url_right": img_url_right,
            "contents": contents,
        }

        idx = db.gameboard.insert_one(post)

        # mongoDB의 고유 번호(_id)를 주소에 출력합니다.
        # 이는 게시글의 상세페이지 보기와 같으며 게임을 만든 후 상세페이지로 넘겨줍니다.
        return redirect(url_for('game_detail', idx=idx.inserted_id))
    else:
        # 아무런 입력이 없이 GET 방식으로 들어왔을때, 게임 작성 페이지로 전환해줍니다.
        return render_template("post.html")

# [게시글 수정] (Update)
@app.route("/edit", methods=["PATCH"])
def list_edit():
    idx = request.args.get("idx")

    # 아무런 입력이 없이 GET 방식으로 들어왔을때, 게임의 고유번호(_id)가 DB에 존재하는지 검사합니다.
    # 만약 해당 고유번호가 없다면 게시물이 존재하지 않음을 알려주고
    # 로그인 한 회원의 세션 아이디값과 게시글 작성자의 아이디가 다르다면 권한을 주지 않습니다.
    if request.method == "GET":
        data = db.gameboard.find_one({"_id": ObjectId(idx)})
        if data is None:
            flash("해당 게시물이 존재하지 않습니다.")
            return redirect(url_for("game_lists"))
        else:
            if session.get("id") == data.get("writer_id"):
                return render_template("edit.html", data=data)
            else:
                flash("글 수정 권한이 없습니다.")
                return redirect(url_for("board_lists"))
    else:
        # POST 방식이 이루어졌을 경우, 글쓴이를 제외한 값을 수정할 수 있도록 설정하였습니다.
        # 수정 시 이전에 작성했던 게시글이 사라지지 않도록 가져왔습니다.
        img_title_left = request.form.get("img_title_left"),
        img_title_right = request.form.get("img_title_left"),
        img_url_left = request.form.get("img_url_left"),
        img_url_right = request.form.get("img_url_right"),
        contents = request.form.get("contents")

        data = db.gameboard.find_one({"_id": ObjectId(idx)})

        # 로그인 한 회원의 세션 아이디값과 게시글 작성자의 아이디가 같다면 수정할 수 있도록 합니다.
        if data.get("writer_id") == session.get("id"):
            db.gameboard.update_one({"_id": ObjectId(idx)}, {
                "$set": {
                    "img_title_left": img_title_left,
                    "img_title_right": img_title_right,
                    "img_url_left": img_url_left,
                    "img_url_right": img_url_right,
                    "contents": contents,
                }
            })
            flash("수정되었습니다.")
            return redirect(url_for("list_detail", idx=idx))
        else:
            flash("글 수정 권한이 없습니다.")
            return redirect(url_for("list_main"))

# [게시글 삭제] (Delete)
@app.route("/api/detail", methods=["DELETE"])
def game_delete():
    idx = request.args.get("idx")
    data = db.gameboard.find_one({"_id": ObjectId(idx)})
    if data.get("writer_id") == session.get("id"):
        db.gameboard.delete_one({"_id": ObjectId(idx)})
    else:
        flash("글 삭제 권한이 없습니다.")
    return redirect(url_for("game_lists"))




if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)

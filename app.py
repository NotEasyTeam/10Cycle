from functools import wraps
import hashlib
import json
from re import S
from urllib.parse import parse_qsl
from load_model import predict
from bson import ObjectId
import jwt
from datetime import datetime, timedelta
from flask import Flask, abort, jsonify, redirect, request, render_template, url_for
from flask_cors import CORS
from pymongo import MongoClient
import requests

SECRET_KEY = 'recycle'
KAKAO_REDIRECT_URI = 'http://localhost:5000/redirect'
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
cors = CORS(app, resources={r'*': {'origins': '*'}})
client = MongoClient('localhost', 27017)
db = client.tencycle
client_id = 'eb06aead9054aed0b2c737734a97ace8'
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}


# 데코레이터 유저정보 불러오는 함수
def authorize(f):
    @wraps(f)
    def decorated_function():
        if not 'Authorization' in request.headers:
            abort(401)
        token = request.headers['Authorization']

        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except:
            abort(401)
        return f(user)

    return decorated_function


@app.route('/')
def home():

    # 현재 이용자의 컴퓨터에 저장된 헤더 에서 mytoken 을 가져옵니다.
    token_receive = request.cookies.get('token')
    try:
        # 암호화되어있는 token의 값을 우리가 사용할 수 있도록 디코딩(암호화 풀기)해줍니다!
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"_id": ObjectId(payload['id'])})
        return render_template('mainpage.html', userid=user_info["userid"])

    # 만약 해당 token의 로그인 시간이 만료되었다면, 아래와 같은 코드를 실행합니다.
    except jwt.ExpiredSignatureError:
        return redirect(url_for("go_login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        # 만약 해당 token이 올바르게 디코딩되지 않는다면, 아래와 같은 코드를 실행합니다.
        return redirect(url_for("go_login", msg="로그인 정보가 존재하지 않습니다."))




@app.route('/main')
def go_main():
    return render_template('mainpage.html')

@app.route('/login')
def go_login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/signup')
def go_sign_up():
    return render_template('signup.html')

@app.route('/uploadedmain')
def go_uploaded_main():
    return render_template('uploaded_mainpage.html')


@app.route("/api/signup", methods=["POST"])
def sign_up():
    data = json.loads(request.data)

    password_hash = hashlib.sha256(data['password'].encode('utf-8')).hexdigest()
    user_exists = bool(db.users.find_one({"userid": data.get('userid')}))


    if user_exists == True:
        return jsonify({'result': 'fail', 'msg': '같은 아이디의 유저가 존재합니다.'})
    else:
        doc = {
            'username': data.get('username'),
            'userid': data.get('userid'),
            'password': password_hash,
            'userpoint': '0'
        }

        db.users.insert_one(doc)

        return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다.'})


@app.route("/api/login", methods=["POST"])
def login():
    data = json.loads(request.data)
    print(data)

    userid = data.get("userid")
    password = data.get("password")

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    hashed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest()

    result = db.users.find_one({
        'userid': userid,
        'password': hashed_pw
    })

    if result:

        payload = {
            'id': str(result["_id"]),
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route("/kakaologin", methods=["POST"])
def kakao_Login():
    data = json.loads(request.data)
    print(data)

    doc = {
        'username': data.get('username'),
        'userid': data.get('userid'),
        'userpoint': '0'
    }

    db.users.update_one({"userid": data.get('userid')}, {"$set": doc}, upsert=True)

    return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다.'})


@app.route("/getuserinfo", methods=["GET"])
@authorize
def get_user_info(user):
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    point = len(list(db.recycles.find({'userid': result["userid"]}, {'_id': False})))
    db.users.update_one({'userid': result["userid"]}, {"point": point})
    
    print(result)

    return jsonify({"msg": "success", "name": result["username"], "point": result["userpoint"]})


@app.route("/upload", methods=["POST"])
@authorize
def image_predict(user):
    db_user = db.users.find_one({'_id': ObjectId(user["id"])})
    print(db_user)

    image = request.files['image_give']  # 이미지 파일
    print(image)
    today = datetime.now()  # 현재 시각
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'recycle_img-{mytime}'  # 파일명

    extension = image.filename.split('.')[-1]  # 확장자 빼기

    save_to = f'static/image/{filename}.{extension}' # 저장 장소

    file = f'recycle_img-{mytime}.{extension}'
    image.save(save_to)  # 이미지 저장

    # 예측
    pred = predict(save_to)

    # DB로 결과와 함께 전달
    doc = {
        'userid': db_user["userid"],
        'image': file,
        'category': pred,
        'date': today
    }
    db.recycles.insert_one(doc)

    return jsonify({'msg': '예측 완료!'})


@app.route("/getuploadimage", methods=["GET"])
@authorize
def get_image(user):
    user_info = db.users.find_one({
        '_id': ObjectId(user["id"])
    })
    print(user_info)
    image = list(db.recycles.find({'userid': user_info["userid"]}, {'_id': False}).sort("date", -1).limit(1))
    uploadimage = image[0]['image']

    return jsonify({'img': uploadimage})


@app.route("/getuserpaper", methods=["GET"])
@authorize
def get_user_paper(user):
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    user_paper = list(db.recycles.find({'userid': result["userid"], 'category': 'paper'}, {'_id': False}).limit(9))

    return jsonify({'message': 'success', 'user_paper': user_paper})


@app.route("/getusermetal", methods=["GET"])
@authorize
def get_user_metal(user):
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    user_metal = list(db.recycles.find({'userid': result["userid"], 'category': 'metal'}, {'_id': False}).limit(9))

    return jsonify({'message': 'success', 'user_metal': user_metal})


@app.route("/getuserplastic", methods=["GET"])
@authorize
def get_user_plastic(user):
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    user_plastic = list(db.recycles.find({'userid': result["userid"], 'category': 'plastic'}, {'_id': False}).limit(9))

    return jsonify({'message': 'success', 'user_plastic': user_plastic})


@app.route("/getuserglass", methods=["GET"])
@authorize
def get_user_glass(user):
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    user_glass = list(db.recycles.find({'userid': result["userid"], 'category': 'glass'}, {'_id': False}).limit(9))

    return jsonify({'message': 'success', 'user_glass': user_glass})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
import json
import hashlib
import jwt
from functools import wraps
from bson import ObjectId
from datetime import datetime, timedelta
from flask import Flask, abort, jsonify, redirect, request, render_template, url_for
from flask_cors import CORS
from pymongo import MongoClient

from load_model import predict

SECRET_KEY = 'recycle'
KAKAO_REDIRECT_URI = 'http://localhost:5000/redirect'
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
cors = CORS(app, resources={r'*': {'origins': '*'}})
client = MongoClient('localhost', 27017)
db = client.tencycle
client_id = '' #앱키 암호화 해서 올려야한다.

NUM_LIMIT = 9



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
    token_receive = request.cookies.get('mytoken')
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

    if user_exists:
        return jsonify({'result': 'fail', 'msg': '같은 아이디의 유저가 존재합니다.'})

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

    return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# @app.route("/kakaologin", methods=["POST"])
# def kakao_Login():
#     data = json.loads(request.data)
#
#     doc = {
#         'username': data.get('username'),
#         'userid': data.get('userid'),
#         'userpoint': '0'
#     }
#
#     db.users.update_one({"userid": data.get('userid')}, {"$set": doc}, upsert=True)
#
#     return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다.'})


@app.route("/getuserinfo", methods=["GET"])
@authorize
def get_user_info(user):
    result = db.users.find_one({'_id': ObjectId(user["id"])})

    point = str(len(list(db.recycles.find({'userid': result["userid"]}, {'_id': False}))))

    doc = {
        'username': result["username"],
        'userid': result["userid"],
        'userpoint': point
    }
    db.users.update_one({'userid': result["userid"]}, {"$set": doc}, upsert=True)

    return jsonify({"msg": "success", "name": result["username"], "point": result["userpoint"]})


@app.route("/upload", methods=["POST"])
@authorize
def image_predict(user):
    db_user = db.users.find_one({'_id': ObjectId(user["id"])})
    image = request.files['image_give']  # 이미지 파일
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


@app.route("/uploadimage", methods=["GET"])
@authorize
def get_image(user):
    user_info = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    image = list(db.recycles.find({'userid': user_info["userid"]}, {'_id': False}).sort("date", -1).limit(1))
    uploadimage = image[0]['image']

    return jsonify({'img': uploadimage})


@app.route("/howtorecycle", methods=["GET"])
@authorize
def get_image_info(user):
    user_info = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    image = list(db.recycles.find({'userid': user_info["userid"]}, {'_id': False}).sort("date", -1).limit(1))
    uploadimage_category = image[0]['category']
    result = {
        "paper": ["종이", "스티커와 같은 이물질을 제거해주세요", "납작하게 접어주세요"],
        "metal": ["캔", "안의 이물질을 제거해주세요", "최대한 압축시켜주세요"],
        "plastic": ["플라스틱", "부착 상표 및 뚜껑을 제거해주세요", "최대한 압축시켜주세요"],
        "glass": ["유리", "안의 이물질을 제거해주세요", "뚜껑을 제거해주세요"]
    }

    category = result.get(uploadimage_category)[0]
    message = result.get(uploadimage_category)[1:]

    return jsonify({'category': category, 'how_to_recycle': message})


    # 코드 리펙토링 전 코드

    # message=[]
    # if uploadimage_category=="paper":
    #     uploadimage_category = "종이"
    #     message.append("스티커와 같은 이물질을 제거해주세요")
    #     message.append("납작하게 접어주세요")
    # elif uploadimage_category=="metal":
    #     uploadimage_category = "캔"
    #     message.append("안의 이물질을 제거해주세요")
    #     message.append("최대한 압축시켜주세요")
    # elif uploadimage_category=="plastic":
    #     uploadimage_category = "플라스틱"
    #     message.append("부착 상표 및 뚜껑을 제거해주세요")
    #     message.append("최대한 압축시켜주세요")
    # elif uploadimage_category=="glass":
    #     uploadimage_category = "유리"
    #     message.append("안의 이물질을 제거해주세요")
    #     message.append("뚜껑을 제거해주세요")
    #
    # return jsonify({'category': uploadimage_category, 'how_to_recycle': message})


@app.route("/userpaper", methods=["GET"])
@authorize
def get_user_paper(user):
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    user_paper = list(db.recycles.find({'userid': result["userid"], 'category': 'paper'}, {'_id': False}).limit(NUM_LIMIT))

    return jsonify({'message': 'success', 'user_paper': user_paper})


@app.route("/usermetal", methods=["GET"])
@authorize
def get_user_metal(user):
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    user_metal = list(db.recycles.find({'userid': result["userid"], 'category': 'metal'}, {'_id': False}).limit(NUM_LIMIT))

    return jsonify({'message': 'success', 'user_metal': user_metal})


@app.route("/userplastic", methods=["GET"])
@authorize
def get_user_plastic(user):
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    user_plastic = list(db.recycles.find({'userid': result["userid"], 'category': 'plastic'}, {'_id': False}).limit(NUM_LIMIT))

    return jsonify({'message': 'success', 'user_plastic': user_plastic})


@app.route("/userglass", methods=["GET"])
@authorize
def get_user_glass(user):
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    user_glass = list(db.recycles.find({'userid': result["userid"], 'category': 'glass'}, {'_id': False}).limit(NUM_LIMIT))

    return jsonify({'message': 'success', 'user_glass': user_glass})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
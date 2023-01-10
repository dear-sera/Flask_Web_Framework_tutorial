"""
mini tweet을 만들어서 회원가입, 트윗남기기, 팔로우, 타임라인 남기기 등의 기능 넣기

wsl을 이용해 서버 띄우기 : FLASK_ENV=development FKAS_APP=app.py flask run
"""



# jsonify: dictionary -> JSON 변환
# request: http 요청 가능
from flask import Flask, jsonify, request
from flask.json import JSONEncoder

### default json endocer는 set을 json으로 변환 불가능
### 따라서 커스텀인코더 작성을 통해 set을 list로 변환하여
### JSON 변환가능하게 만들어줘야함
class CustomJSONEncoder(JSONEncoder):
	def default(self, obj):
		if isinstance(obj, set):
			return list(obj)
		return JSONEncoder.default(self, obj)


app = Flask(__name__)
app.id_count = 1
app.users = {}
app.tweets = []
app.json_encoder = CustomJSONEncoder

#회원가입
#필요정보 : id, name, email, password, profile
@app.route("/sign-up", methods=['POST'])
def sign_up():
    new_user                = request.json
    new_user["id"]          = app.id_count
    app.users[app.id_count] = new_user
    app.id_count            = app.id_count + 1

    return jsonify(new_user)

"""
$ http -v POST localhost:5000/sign-up name=홍길동 email=gildong@naver.com password=abcd1234  #회원가입

--->

POST /sign-up HTTP/1.1
Accept: application/json, */*;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 84
Content-Type: application/json
Host: localhost:5000
User-Agent: HTTPie/2.6.0

{
    "email": "gildong@naver.com",
    "name": "홍길동",
    "password": "abcd1234"
}


HTTP/1.0 200 OK
Content-Length: 107
Content-Type: application/json
Date: Mon, 09 Jan 2023 00:59:13 GMT
Server: Werkzeug/2.0.2 Python/3.10.6

{
    "email": "gildong@naver.com",
    "id": 1,
    "name": "홍길동",
    "password": "abcd1234"
}

"""
#트윗 엔드포인트
@app.route("/tweet", methods=['POST'])	
def tweet():
	payload = request.json
	user_id = int(payload['id'])  #id = 사용자 id
	tweet = payload['tweet']      #tweet = 트윗 내용

	if user_id not in app.users:
		return '사용자가 존재하지 않습니다.', 400
	if len(tweet) > 300:
		return '300자를 초과했습니다.', 400
	user_id = int(payload['id'])
	app.tweets.append({
		'user_id' : user_id,
		'tweet' : tweet
	})
	return '', 200

"""
$ http -v POST localhost:5000/tweet id:=1 tweet="This is my first tweet"  # 트윗남기기

--> 

POST /tweet HTTP/1.1
Accept: application/json, */*;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 44
Content-Type: application/json
Host: localhost:5000
User-Agent: HTTPie/2.6.0

{
    "id": 1,
    "tweet": "This is my first tweet"
}


HTTP/1.0 200 OK
Content-Length: 0
Content-Type: text/html; charset=utf-8
Date: Mon, 09 Jan 2023 00:59:14 GMT
Server: Werkzeug/2.0.2 Python/3.10.6

"""

#팔로우&언팔로우 엔드포인트
@app.route("/follow", methods=['POST'])
def follow():
	payload = request.json
	user_id = int(payload['id'])
	user_id_to_follow = int(payload['follow'])

	if user_id not in app.users or user_id_to_follow not in app.users:
		return '사용자가 존재하지 않습니다.', 400
	user = app.users[user_id]
	user.setdefault('follow', set()).add(user_id_to_follow)  #팔로우 항목에 추가
	return jsonify(user)

@app.route("/unfollow", methods=['POST'])
def unfollow():
	payload = request.json
	user_id = int(payload['id'])
	user_id_to_follow = int(payload['unfollow'])

	if user_id not in app.users or user_id_to_follow not in app.users:
		return '사용자가 존재하지 않습니다.', 400

	user = app.users[user_id]
	user.setdefault('follow', set()).descard(user_id_to_follow)   #팔로우 항목에서 user_id 제거

	return jsonify(user)


"""
$ http -v POST localhost:5000/sign-up name=홍길동 email=gildong@naver.com password=abcd1234
$ http -v POST localhost:5000/sign-up name=임꺽정 email=ggukjeong@naver.com password=abcd1233
http -v POST localhost:5000/follow id:=1 follow:=2   # 팔로우 걸기

-->
Accept: application/json, */*;q=0.5
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 22
Content-Type: application/json
Host: localhost:5000
User-Agent: HTTPie/2.6.0

{
    "follow": 2,
    "id": 1
}


HTTP/1.0 200 OK
Content-Length: 133
Content-Type: application/json
Date: Tue, 10 Jan 2023 05:14:43 GMT
Server: Werkzeug/2.0.2 Python/3.10.6

{
    "email": "gildong@naver.com",
    "follow": [
        2
    ],
    "id": 1,
    "name": "홍길동",
    "password": "abcd1234"
}

"""

#트위터 타임라인 엔드포인트
@app.route("/timeline/<int:user_id>", methods=['GET'])
def timeline(user_id):
	if user_id not in app.users:
		return '사용자가 존재하지 않습니다.', 400
	follow_list = app.users[user_id].get('follow', set()) #팔로우 목록에 추가
	follow_list.add(user_id)
	timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]  #각 유저가 서로 맞팔로우라면 타임라인에 각자의 트윗이 노출

	return jsonify({  #유저와 해당 유저의 타임라인을 출력
		'user_id' : user_id,
		'timeline' : timeline
	})

"""
http -v GET localhost:5000/timeline/1   #유저id=1의 타임라인

-->

GET /timeline/1 HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:5000
User-Agent: HTTPie/2.6.0



HTTP/1.0 200 OK
Content-Length: 183
Content-Type: application/json
Date: Tue, 10 Jan 2023 05:23:28 GMT
Server: Werkzeug/2.0.2 Python/3.10.6

{
    "timeline": [
        {
            "tweet": "This is my first tweet",
            "user_id": 1
        },
        {
            "tweet": "Life is valuable",
            "user_id": 2
        }
    ],
    "user_id": 1
}

"""



"""
기능 정리

- 회원가입
$ http -v POST localhost:5000/sign-up name=홍길동 email=gildong@naver.com password=abcd1234
$ http -v POST localhost:5000/sign-up name=임꺽정 email=ggukjeong@naver.com password=abcd1233

- 팔로우
$ http -v POST localhost:5000/follow id:=1 follow:=2
$ http -v POST localhost:5000/follow id:=2 follow:=1

- 트윗 남기기
$ http -v POST localhost:5000/tweet id:=1 tweet="This is my first tweet"
$ http -v POST localhost:5000/tweet id:=2 tweet="Life is valuable"

- 타임라인 출력
http -v GET localhost:5000/timeline/1
http -v GET localhost:5000/timeline/2

"""
# jsonify: dictionary -> JSON 변환
# request: http 요청 가능

#서버 띄우기 : FLASK_ENV=development FKAS_APP=app.py flask run

from flask import Flask, jsonify, request

app = Flask(__name__)
app.id_count = 1
app.users = {}
app.tweets = []
 
@app.route("/ping", methods=['GET'])
def ping():
    return "pong"

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
$ http -v POST localhost:5000/sign-up name=홍길동 email=gildong@naver.com password=abcd1234

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
$ http -v POST localhost:5000/tweet id:=1 tweet="This is my first tweet"

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
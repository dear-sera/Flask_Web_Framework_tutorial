from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/hello_world')   #test api
def hello_world():
    return 'Hello, World!'

@app.route('/echo_call/<param>') #get echo api
def get_echo_call(param):
    return jsonify({"param": param})

@app.route('/echo_call', methods=['POST']) #post echo api
def post_echo_call(param):
    param = request.get_json()
    return jsonify(param)




if __name__ == "__main__":
    app.run()
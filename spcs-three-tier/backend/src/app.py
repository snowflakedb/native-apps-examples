from flask import Flask, jsonify, make_response
import os
from snowpark import snowpark

app = Flask(__name__)
app.register_blueprint(snowpark, url_prefix='/snowpark')

@app.route("/")
def default():
    return make_response(jsonify(result='Nothing to see here'))

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

if __name__ == '__main__':
    api_port=int(os.getenv('API_PORT') or 8081)
    app.run(port=api_port, host='0.0.0.0')

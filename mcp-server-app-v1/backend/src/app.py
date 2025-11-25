from flask import Flask, jsonify, make_response, request
import os

app = Flask(__name__)

@app.route("/")
def default():
    return make_response(jsonify(result='Echo Service is running'))

@app.route("/health")
def health():
    return make_response(jsonify(status='healthy'))

@app.route("/echo", methods=['GET', 'POST'])
def echo():
    if request.method == 'POST':
        # Handle JSON input
        if request.is_json:
            data = request.get_json()
            # Check if this is a Snowflake service function request
            if isinstance(data, dict) and 'data' in data:
                # Service function format: {"data": [[row_num, arg1, ...], ...]}
                # Response format: {"data": [[row_num, result], ...]}
                results = []
                for row in data['data']:
                    row_num = row[0]
                    input_val = row[1] if len(row) > 1 else ''
                    results.append([row_num, f"Echo: {input_val}"])
                return make_response(jsonify(data=results))
            return make_response(jsonify(echo=data))
        # Handle form data
        elif request.form:
            return make_response(jsonify(echo=dict(request.form)))
        # Handle raw text
        else:
            return make_response(jsonify(echo=request.get_data(as_text=True)))
    else:
        # Handle GET with query params
        args = dict(request.args)
        if args:
            return make_response(jsonify(echo=args))
        return make_response(jsonify(echo='Send data via POST or query params'))

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

if __name__ == '__main__':
    api_port = int(os.getenv('API_PORT', 8080))
    app.run(port=api_port, host='0.0.0.0')


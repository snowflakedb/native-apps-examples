from flask import Flask, jsonify, make_response, request
import os
import requests

app = Flask(__name__)

# Snowflake host from environment (set by SPCS)
SNOWFLAKE_HOST = os.environ.get('SNOWFLAKE_HOST', '')

def get_snowflake_token():
    """Read the OAuth token from SPCS token file."""
    try:
        with open('/snowflake/session/token', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def call_cortex_complete(model: str, prompt: str) -> dict:
    """Call the Cortex inference complete API."""
    token = get_snowflake_token()
    if not token:
        return {"error": "No Snowflake token available"}
    
    if not SNOWFLAKE_HOST:
        return {"error": "SNOWFLAKE_HOST not set"}
    
    url = f"https://{SNOWFLAKE_HOST}/api/v2/cortex/inference:complete"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@app.route("/")
def default():
    return make_response(jsonify(result='Cortex API Service is running'))

@app.route("/health")
def health():
    return make_response(jsonify(status='healthy'))

@app.route("/cortex/complete", methods=['GET', 'POST'])
def cortex_complete():
    """
    Call Cortex LLM completion API.
    
    For service function calls, expects: {"data": [[row_num, prompt, model], ...]}
    For direct HTTP calls, expects: {"prompt": "...", "model": "..."}
    """
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            
            # Check if this is a Snowflake service function request
            if isinstance(data, dict) and 'data' in data:
                # Service function format: {"data": [[row_num, arg1, arg2, ...], ...]}
                results = []
                for row in data['data']:
                    row_num = row[0]
                    prompt = row[1] if len(row) > 1 else ''
                    model = row[2] if len(row) > 2 else 'llama3.1-8b'
                    
                    response = call_cortex_complete(model, prompt)
                    
                    # Extract the text response
                    if 'error' in response:
                        result_text = f"Error: {response['error']}"
                    elif 'choices' in response and len(response['choices']) > 0:
                        result_text = response['choices'][0].get('message', {}).get('content', str(response))
                    else:
                        result_text = str(response)
                    
                    results.append([row_num, result_text])
                return make_response(jsonify(data=results))
            
            # Direct HTTP call format
            prompt = data.get('prompt', '')
            model = data.get('model', 'llama3.1-8b')
            response = call_cortex_complete(model, prompt)
            return make_response(jsonify(response))
        
        return make_response(jsonify(error='Invalid request format'), 400)
    
    # GET request - return usage info
    return make_response(jsonify(
        usage="POST with JSON: {\"prompt\": \"your prompt\", \"model\": \"llama3.1-8b\"}",
        available_models=["llama3.1-8b", "llama3.1-70b", "llama3.1-405b", "mistral-large2", "snowflake-arctic"]
    ))

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

if __name__ == '__main__':
    api_port = int(os.getenv('API_PORT', 8080))
    app.run(port=api_port, host='0.0.0.0')


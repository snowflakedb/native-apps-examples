from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

# Hugging Face API Configuration
API_TOKEN = os.getenv("API_TOKEN")
MODEL_ID = os.getenv("MODEL_ID", "gpt2")
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}


# API Endpoint for Text Generation
@app.route("/api/generate", methods=["POST"])
def generate_text():
    data = request.json
    if not data or "data" not in data:
        return jsonify({"error": "Input data not provided"}), 400
    

    user_input = data["data"]
    payload = {"inputs": user_input}
    # user_input = request.data.decode("utf-8").strip()
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        return jsonify({"error": "Failed to generate text", "details": response.json()}), response.status_code

    return jsonify(response.json())


# Front-end Route
@app.route("/", methods=["GET", "POST"])
def home():
    generated_text = None
    error = None

    if request.method == "POST":
        user_input = request.form.get("user_input")
        if user_input:
            payload = {"inputs": user_input}
            response = requests.post(API_URL, headers=HEADERS, json=payload)
            print(response)
            if response.status_code == 200:
                generated_text = response.json()[0]["generated_text"]
            else:
                error = "Failed to generate text. Please try again. details: " + str(response.json())
        else:
            error = "Please provide input text."

    return render_template("index.html", generated_text=generated_text, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
import os
from datetime import datetime, timedelta, timezone

import jwt
from flask import Flask, jsonify, request

app = Flask(__name__)

JWT_SECRET = os.environ["JWT_SECRET"]
AUTH_USERNAME = os.environ["AUTH_USERNAME"]
AUTH_PASSWORD = os.environ["AUTH_PASSWORD"]


@app.route("/")
def home():
    return jsonify({"message": "Student Grade Analytics - Authentication Service"})

@app.route("/health")
def health():
    return jsonify({
        "status": "Healthy"
    }), 200

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON data"}), 400

    username = data.get("username")
    password = data.get("password")

    if username != AUTH_USERNAME or password != AUTH_PASSWORD:
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode(
        {
            "sub": username,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        JWT_SECRET,
        algorithm="HS256"
    )

    return jsonify({"token": token}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
import os
import random
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CARDS = [
    "2c", "2d", "2h", "2s",
    "3c", "3d", "3h", "3s",
    "4c", "4d", "4h", "4s",
    "5c", "5d", "5h", "5s",
    "6c", "6d", "6h", "6s",
    "7c", "7d", "7h", "7s",
    "8c", "8d", "8h", "8s",
    "9c", "9d", "9h", "9s",
    "Tc", "Td", "Th", "Ts",
    "Jc", "Jd", "Jh", "Js",
    "Qc", "Qd", "Qh", "Qs",
    "Kc", "Kd", "Kh", "Ks",
    "Ac", "Ad", "Ah", "As"
]

@app.route("/")
def home():
    return "OK"

@app.route("/api/cards")
def cards():
    random.shuffle(CARDS)
    return jsonify({"cards": CARDS})

# Routes for kubernetes health checks
@app.route("/api/health", methods=["GET"])
def health():
    return "", 200

@app.route("/api/ready", methods=["GET"])
def ready():
    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("FLASK_RUN_PORT", 5001))
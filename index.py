from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")


@socketio.on("connect")
def handle_connect():
    print("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


@socketio.on("message")
def handle_message(message):
    response = model.generate_content(message)
    emit("response", response.text)


@app.route("/open_socket", methods=["POST"])
def open_socket():
    return jsonify({"status": "WebSocket opened and listening on port 8080"})


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8080)

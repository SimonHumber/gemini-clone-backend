from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")
CORS(app)
messageHistory: list[dict[str, str | list[str]]] = []

genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")


@socketio.on("message")
def handle_message(prompt):
    messageHistory.append(prompt)
    response = model.generate_content(messageHistory)
    messageHistory.append({"role": "model", "parts": [response.text]})
    """backend will send response event, frontend should listen to this"""
    emit("response", response.text)


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8080)

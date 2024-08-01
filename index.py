from flask import Flask
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


@socketio.on("message")
def handle_message(prompt):
    response = model.generate_content(prompt)
    emit("response", response.text)


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8080)

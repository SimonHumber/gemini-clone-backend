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
messageHistory = []

genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")


# @socketio.on("message")
def handle_delete():
    for file in genai.list_files():
        genai.delete_file(file.name)
    for file in genai.list_files():
        print(file.name, "could not be deleted")


if __name__ == "__main__":
    handle_delete()
    # socketio.run(app, debug=True, port=8080)

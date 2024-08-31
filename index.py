from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import google.generativeai as genai
import os
import shutil
from dotenv import load_dotenv
import PIL.Image


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")
CORS(app)
messageHistory: list[dict[str, str | list[str]]] = []
app.config["UPLOAD_FOLDER"] = "uploads/"
file_storage = None


genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

"""instead of accept object that mimics gemini api, create own api """


@socketio.on("message")
def handle_message(prompt):
    global file_storage
    if prompt["hasFiles"]:
        prompt["parts"] = prompt["parts"] + [
            PIL.Image.open("./uploads/" + file_storage.filename)
        ]
        file_storage = None
    del prompt["hasFiles"]
    messageHistory.append(prompt)
    response = model.generate_content(messageHistory)
    messageHistory.append({"role": "model", "parts": [response.text]})
    """backend will send response event, frontend should listen to this"""
    emit("response", response.text)


@app.route("/upload", methods=["POST"])
def handle_upload():
    # Ensure the upload folder exists
    if os.path.exists(app.config["UPLOAD_FOLDER"]):
        shutil.rmtree(app.config["UPLOAD_FOLDER"])
        os.makedirs(app.config["UPLOAD_FOLDER"])
    else:
        os.makedirs(app.config["UPLOAD_FOLDER"])
    global file_storage
    file = request.files["file"]
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
    file_storage = file
    return "File uploaded successfully", 200


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8080)

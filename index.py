from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import google.generativeai as genai
import os
import shutil
from dotenv import load_dotenv
import time


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")
CORS(app)
messageHistory: list[dict[str, str | list[str]]] = []
app.config["UPLOAD_FOLDER"] = "uploads/"
files = []


genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash", tools="code_execution")

"""instead of accept object that mimics gemini api, create own api """


@socketio.on("message")
# TODO exception handling for when generate content fails
def handle_message(prompt):
    global files
    if prompt["hasFiles"]:
        for file in files:
            while genai.get_file(file.name).state.name == "PROCESSING":
                print(genai.get_file(file.name).state.name)
                time.sleep(1)
        prompt["parts"] = prompt["parts"] + files
        files = []
    prompt_api = {"role": "user", "parts": prompt["parts"]}
    messageHistory.append(prompt_api)
    response = model.generate_content(messageHistory)
    print(response)
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
    global files
    files = []
    for file in request.files.getlist("file"):
        assert isinstance(file.filename, str)  # not necessary, just for lsp
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        uploaded_file = genai.upload_file(path=file_path)
        files.append(uploaded_file)
    return "File uploaded successfully", 200


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8080)

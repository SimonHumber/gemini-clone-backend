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
file_location: str = ""


genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

"""instead of accept object that mimics gemini api, create own api """


@socketio.on("message")
# TODO exception handling for when generate content fails
def handle_message(prompt):
    global file_location
    if prompt["hasFiles"]:
        files = genai.upload_file(path=file_location)
        while files.state.name == "PROCESSING":
            print("processing...")
            time.sleep(10)
        if files.state.name == "FAILED":
            pass  # TODO throw exception maybe not necessary since it errors anyways
        prompt["parts"] = prompt["parts"] + [files]
        file_location = ""
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
    global file_location
    file = request.files["file"]
    assert isinstance(file.filename, str)  # not necessary, just for lsp
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
    file_location = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    return "File uploaded successfully", 200


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8080)

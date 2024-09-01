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
file_locations: list[str] = []


genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

"""instead of accept object that mimics gemini api, create own api """


@socketio.on("message")
# TODO exception handling for when generate content fails
def handle_message(prompt):
    global file_locations
    if prompt["hasFiles"]:
        # should probably move all of this into another function
        uploaded_files = []
        for file in file_locations:
            uploaded_file = genai.upload_file(path=file)
            uploaded_files.append(uploaded_file)
            while genai.get_file(uploaded_file.name).state.name == "PROCESSING":
                print(genai.get_file(uploaded_file.name).state.name)
                time.sleep(1)
            if uploaded_file.state.name == "FAILED":
                pass  # TODO throw exception maybe not necessary since it errors anyways
        prompt["parts"] = prompt["parts"] + uploaded_files
        file_locations = []
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
    global file_locations
    for file in request.files.getlist("file"):
        assert isinstance(file.filename, str)  # not necessary, just for lsp
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)
        file_locations.append(file_path)
    return "File uploaded successfully", 200


if __name__ == "__main__":
    socketio.run(app, debug=True, port=8080)

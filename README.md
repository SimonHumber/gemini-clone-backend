# Getting Started with Create React App

Clone this repo, then create venv and activate it.

You will need a .env file for the external API calls to work. Create a .env file and put this in it:

```
API_KEY=<your-api-key-here>
SECRET_KEY=PutWhateverYouWantHereButYouShouldChangeThis
GRPC_VERBOSITY=ERROR
GLOG_minloglevel=2
```
`GRPC_VERBOSITY` and `GLOG_minloglevel` are to disable warnings generated before each response.

Then, install the dependencies

`pip install -r requirements.txt`

Finally, run it
`python3 index.py`
on Mac

`python index.py`
on other OS

If you uploaded any files, they will be stored in gemini api for up to 2 days.
You can delete them by running the `delete-files.py` script.

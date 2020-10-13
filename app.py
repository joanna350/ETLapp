import os
from flask import Flask

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/downloads/'
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

app.secret_key = os.urandom(24)
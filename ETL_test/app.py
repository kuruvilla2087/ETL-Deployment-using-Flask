from flask import Flask
import sys

UPLOAD_FOLDER = sys.argv[1]

app = Flask(__name__)
app.secret_key = "2550"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

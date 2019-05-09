from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config.from_object(Config)
db=SQLAlchemy(app)
migrate=Migrate(app,db)
login=LoginManager(app)
login.login_view='login'

Bootstrap(app)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

from app import routes, models
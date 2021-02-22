import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_sslify import SSLify
from secret import secret_key

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    sslify = SSLify(app)
    app.config['SECRET_KEY'] = secret_key

from app import routes
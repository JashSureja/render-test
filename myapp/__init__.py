import os

from flask import Flask 

from .extensions import db
from .routes import main

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    # app.config["DROPBOX_ACCESS_TOKEN"] = os.getenv("DROPBOX_TOKEN")
    db.init_app(app)

    app.register_blueprint(main)

    return app
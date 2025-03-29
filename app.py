from flask import Flask
from main_bp import main_bp 
import json 
import os


def create_app():
    app = Flask(__name__)
    config_data = json.loads(open("config.json").read())
    config_data = config_data.get(os.environ["environment"])
    SECRET_KEY = config_data.get("app_secret") 
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['mod_id'] = config_data.get("mod_id") 
    app.register_blueprint(main_bp)  # Register the blueprint

    return app
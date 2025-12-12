import os
from flask import Flask
from flask_cors import CORS
from config import Config          # FIXED
from app.api import api_bp          # FIXED

def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    
    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["EXPORT_FOLDER"], exist_ok=True)

    app.register_blueprint(api_bp, url_prefix="/api")
    return app

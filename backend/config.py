# config.py — load environment values
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # Get absolute path of the backend directory (where config.py resides)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite configuration (simpler than MySQL, no service required)
    DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "gradehub.db"))
    
    SECRET_KEY = os.environ.get("FLASK_SECRET", "change_this")
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", os.path.join(BASE_DIR, "uploads"))
    EXPORT_FOLDER = os.environ.get("EXPORT_FOLDER", os.path.join(BASE_DIR, "exports"))
    ALLOWED_EXT = {"pdf"}
    PAGES_TO_SCAN_FOR_METADATA = 3
    MAX_PAGES_FOR_TABLE_EXTRACTION = 20  # Limit pages for table extraction to improve performance
    MAX_PREVIEW_ROWS = 10


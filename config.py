import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-me")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE", "10").replace("MB", ""))
    ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "png,jpg,jpeg,gif,webp").split(","))
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "statics", "uploads")
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

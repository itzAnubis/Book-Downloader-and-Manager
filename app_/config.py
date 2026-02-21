import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_ID = int(os.getenv("APP_API_ID"))
    API_HASH = os.getenv("APP_API_HASH")
    CHANNEL_NAME = os.getenv("CHANNEL_NAME")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "glm-ocr:latest")
    SESSION_NAME = os.getenv("SESSION_NAME", "book_scanner_session")
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    COVERS_DIR = os.path.join(BASE_DIR, "covers")
    DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
    CSV_PATH = os.path.join(BASE_DIR, "books_inventory.csv")
    DB_PATH = os.path.join(BASE_DIR, "books.db")
    
# Ensure directories exist
os.makedirs(Config.COVERS_DIR, exist_ok=True)
os.makedirs(Config.DOWNLOADS_DIR, exist_ok=True)    
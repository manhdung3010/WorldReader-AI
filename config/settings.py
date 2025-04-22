import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
    DB_NAME = os.getenv('DB_NAME', 'world_reader')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Cấu hình mô hình
    EMBEDDING_SIZE = 200
    DEFAULT_K = 5
    
    # Cấu hình API
    API_HOST = "0.0.0.0"
    API_PORT = 5000
    DEBUG_MODE = True

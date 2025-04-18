class Config:
    # Cấu hình cơ sở dữ liệu
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASSWORD = "123456"
    DB_NAME = "world_reader"
    DB_PORT = 3306
    
    # Cấu hình mô hình
    EMBEDDING_SIZE = 200
    DEFAULT_K = 5
    
    # Cấu hình API
    API_HOST = "0.0.0.0"
    API_PORT = 5000
    DEBUG_MODE = True

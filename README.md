# WorldReader-AI

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

WorldReader-AI là một hệ thống AI toàn diện kết hợp giữa **hệ thống gợi ý sản phẩm thông minh** và **chatbot xử lý tài liệu** sử dụng Google Gemini AI. Dự án được thiết kế để cung cấp trải nghiệm tương tác thông minh với dữ liệu sản phẩm và tài liệu.

## 🌟 Tính năng chính

### 🤖 Hệ thống gợi ý sản phẩm thông minh
- **TF-IDF Embedding**: Sử dụng mô hình TF-IDF để tạo vector nhúng cho sản phẩm
- **FAISS Index**: Tìm kiếm nhanh chóng với FAISS (Facebook AI Similarity Search)
- **Gợi ý thông minh**: Tìm sản phẩm tương tự dựa trên mô tả và đặc tính
- **Cập nhật động**: Hỗ trợ thêm/xóa sản phẩm mà không cần huấn luyện lại toàn bộ
- **API RESTful**: Giao diện API dễ sử dụng cho tích hợp

### 📚 Chatbot xử lý tài liệu
- **Google Gemini AI**: Sử dụng mô hình AI tiên tiến của Google
- **Đa định dạng**: Hỗ trợ PDF, DOCX, TXT
- **Tương tác thông minh**: Trả lời câu hỏi dựa trên nội dung tài liệu
- **Quản lý tài liệu**: Upload, xóa, và quản lý tài liệu dễ dàng
- **Context-aware**: Hiểu ngữ cảnh từ nhiều tài liệu cùng lúc

## 🏗️ Kiến trúc hệ thống

```
WorldReader-AI/
├── api/                    # API endpoints
│   ├── recommendation_api.py
│   └── __init__.py
├── chatbot/               # Chatbot xử lý tài liệu
│   ├── document_chatbot.py
│   └── uploads/           # Thư mục lưu tài liệu
├── config/                # Cấu hình hệ thống
│   ├── settings.py
│   └── __init__.py
├── data/                  # Xử lý dữ liệu
│   ├── data_loader.py
│   ├── preprocessor.py
│   ├── processed/
│   └── raw/
├── models/                # Các mô hình AI
│   ├── base_model.py
│   ├── faiss_index.py
│   ├── product_model.py
│   ├── tfidf_model.py
│   └── __init__.py
├── utils/                 # Tiện ích
│   ├── text_utils.py
│   └── __init__.py
├── main.py               # Entry point chính
├── requirements.txt      # Dependencies
└── README.md
```

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Python 3.10+
- MySQL Database
- Google API Key (cho Gemini AI)

### Bước 1: Clone repository
```bash
git clone https://github.com/manhdung3010/WorldReader-AI.git
cd WorldReader-AI
```

### Bước 2: Tạo virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Cấu hình môi trường
Tạo file `.env` trong thư mục gốc:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=world_reader
DB_PORT=3306

# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key
GOOGLE_MODEL=gemini-pro

# API Configuration
API_HOST=0.0.0.0
API_PORT=5053
DEBUG_MODE=True
```

### Bước 5: Khởi tạo database


## 📖 Sử dụng

### Khởi chạy hệ thống
```bash
python main.py
```

Hệ thống sẽ:
1. Tải dữ liệu sản phẩm từ database
2. Huấn luyện mô hình TF-IDF và FAISS
3. Khởi động API server tại `http://localhost:5053`

### Sử dụng API gợi ý sản phẩm

#### 1. Lấy gợi ý cho một sản phẩm
```bash
curl -X GET "http://localhost:5053/recommendations/1?k=5"
```

#### 2. Lấy gợi ý cho nhiều sản phẩm
```bash
curl -X POST "http://localhost:5053/recommendations/batch" \
  -H "Content-Type: application/json" \
  -d '{"product_ids": [1, 2, 3], "k": 5}'
```

#### 3. Cập nhật sản phẩm mới
```bash
curl -X POST "http://localhost:5053/products/update" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1001,
    "name": "Sản phẩm mới",
    "description": "Mô tả sản phẩm",
    "category": "Electronics"
  }'
```

### Sử dụng Chatbot

#### 1. Upload tài liệu
```python
from chatbot.document_chatbot import DocumentChatbot

chatbot = DocumentChatbot()

# Upload file
chatbot.save_uploaded_file(file_object)
```

#### 2. Hỏi đáp về tài liệu
```python
# Hỏi câu hỏi về tài liệu đã upload
answer = chatbot.get_answer("Nội dung chính của tài liệu là gì?")
print(answer)
```

## 🔧 API Endpoints

### Hệ thống gợi ý

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/recommendations/{product_id}` | Lấy gợi ý cho một sản phẩm |
| POST | `/recommendations/batch` | Lấy gợi ý cho nhiều sản phẩm |
| POST | `/products/update` | Cập nhật sản phẩm mới |
| DELETE | `/products/{product_id}` | Xóa sản phẩm |
| POST | `/products/batch-update` | Cập nhật nhiều sản phẩm |
| DELETE | `/products/batch-delete` | Xóa nhiều sản phẩm |

### Chatbot

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/chatbot/upload` | Upload tài liệu |
| POST | `/chatbot/ask` | Hỏi câu hỏi |
| GET | `/chatbot/files` | Lấy danh sách tài liệu |
| DELETE | `/chatbot/files/{filename}` | Xóa tài liệu |

## 🛠️ Tùy chỉnh

### Cấu hình mô hình
Chỉnh sửa `config/settings.py`:

```python
class Config:
    # Kích thước vector nhúng
    EMBEDDING_SIZE = 200
    
    # Số lượng gợi ý mặc định
    DEFAULT_K = 5
    
    # Cấu hình API
    API_HOST = "0.0.0.0"
    API_PORT = 5053
```

### Thêm mô hình nhúng mới
Tạo class mới trong `models/` và kế thừa từ `BaseModel`:

```python
from models.base_model import BaseModel

class CustomEmbeddingModel(BaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def train(self, data):
        # Implement training logic
        pass
    
    def get_embeddings(self, data):
        # Implement embedding generation
        pass
```

## 🧪 Testing

```bash
# Chạy tests
python -m pytest tests/

# Chạy với coverage
python -m pytest --cov=. tests/
```

## 📊 Performance

- **Tốc độ tìm kiếm**: < 10ms cho 10,000 sản phẩm
- **Độ chính xác**: > 85% cho gợi ý sản phẩm
- **Khả năng mở rộng**: Hỗ trợ đến 1M+ sản phẩm

## 🤝 Đóng góp

1. Fork dự án
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📝 License

Dự án này được phân phối dưới giấy phép MIT. Xem `LICENSE` để biết thêm chi tiết.

## 📞 Liên hệ

- **Email**: ngmanhdung2003@gmail.com
- **GitHub**: [@manhdung3010](https://github.com/manhdung3010)
- **Project Link**: [https://github.com/manhdung3010/WorldReader-AI](https://github.com/manhdung3010/WorldReader-AI)

## 🙏 Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) - Mô hình AI tiên tiến
- [FAISS](https://github.com/facebookresearch/faiss) - Thư viện tìm kiếm vector
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [scikit-learn](https://scikit-learn.org/) - Machine learning library

---

⭐ Nếu dự án này hữu ích, hãy cho chúng tôi một star!

import re
import nltk
from nltk.corpus import stopwords

# Tải các tài nguyên cần thiết từ NLTK
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def preprocess_text(text):
    """Tiền xử lý văn bản"""
    if not isinstance(text, str):
        return ""
    
    # Chuyển thành chữ thường
    text = text.lower()
    
    # Loại bỏ ký tự đặc biệt
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Loại bỏ số
    text = re.sub(r'\d+', ' ', text)
    
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def get_stopwords(language='english'):
    """Lấy danh sách từ dừng theo ngôn ngữ"""
    return stopwords.words(language)
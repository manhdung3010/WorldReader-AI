import re
import nltk
from nltk.corpus import stopwords
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tải các tài nguyên cần thiết từ NLTK
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def get_stopwords(language='english'):
    """Lấy danh sách stop words cho ngôn ngữ được chỉ định"""
    try:
        return set(stopwords.words(language))
    except:
        logger.warning(f"Không tìm thấy stop words cho ngôn ngữ {language}, sử dụng tiếng Anh")
        return set(stopwords.words('english'))

def preprocess_text(text, language='english'):
    """Tiền xử lý văn bản"""
    if not isinstance(text, str):
        logger.warning(f"Input không phải chuỗi: {type(text)}")
        return ""
    
    # Lưu text gốc để debug
    original_text = text
    
    # Chuyển thành chữ thường
    text = text.lower()
    
    # Loại bỏ ký tự đặc biệt nhưng giữ lại dấu gạch ngang
    text = re.sub(r'[^\w\s-]', ' ', text)
    
    # Loại bỏ số nhưng giữ lại số trong từ (ví dụ: iphone15)
    text = re.sub(r'\b\d+\b', ' ', text)
    
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Lấy stop words
    stop_words = get_stopwords(language)
    
    # Tách từ và loại bỏ stop words
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    
    # Nếu không còn từ nào sau khi lọc, giữ lại text gốc đã xử lý
    if not filtered_words:
        logger.warning(f"Không còn từ nào sau khi lọc stop words. Text gốc: {original_text}")
        return text
    
    result = ' '.join(filtered_words)
    
    # Log kết quả nếu text thay đổi nhiều
    if len(result) < len(original_text) * 0.5:
        logger.info(f"Text bị rút gọn nhiều: {original_text} -> {result}")
    
    return result
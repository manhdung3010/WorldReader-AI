from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from models.base_model import BaseRecommendationModel
from utils.text_utils import get_stopwords

class TfidfEmbeddingModel(BaseRecommendationModel):
    """Mô hình tạo vector nhúng TF-IDF cho sản phẩm"""
    
    def __init__(self, max_features=200, ngram_range=(1, 2), language='english'):
        super().__init__()
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.language = language
        self.vectorizer = None
        self.embeddings = None
        self.data = None
    
    def train(self, data):
        """Huấn luyện mô hình TF-IDF với dữ liệu đã cho"""
        if 'combined_features' not in data.columns:
            raise ValueError("Dữ liệu không có cột 'combined_features'")
        
        self.data = data
        
        # Lấy danh sách stop words
        stop_words = list(get_stopwords(self.language))
        
        # Khởi tạo TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            stop_words=stop_words,
            ngram_range=self.ngram_range,
            min_df=2,  # Từ phải xuất hiện ít nhất 2 lần
            max_df=0.95  # Từ không được xuất hiện trong 95% tài liệu
        )
        
        # Tạo ma trận TF-IDF
        self.embeddings = self.vectorizer.fit_transform(data['combined_features']).toarray()
        self.is_trained = True
        
        print(f"✅ Đã tạo embeddings với kích thước: {self.embeddings.shape}")
        return self.embeddings
    
    def update(self, new_data):
        """Cập nhật mô hình với dữ liệu mới mà không cần huấn luyện lại từ đầu"""
        if not self.is_trained:
            # Nếu chưa huấn luyện trước đó, gọi phương thức train
            return self.train(new_data)
        
        if 'combined_features' not in new_data.columns:
            raise ValueError("Dữ liệu mới không có cột 'combined_features'")
        
        # Chuyển đổi dữ liệu mới bằng vectorizer đã được huấn luyện
        new_embeddings = self.vectorizer.transform(new_data['combined_features']).toarray()
        
        # Cập nhật DataFrame dữ liệu gốc sử dụng pd.concat thay vì append
        import pandas as pd
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        
        # Cập nhật ma trận embeddings
        self.embeddings = np.vstack((self.embeddings, new_embeddings))
        
        print(f"✅ Đã cập nhật embeddings với kích thước mới: {self.embeddings.shape}")
        return self.embeddings
    
    def get_embeddings(self):
        """Trả về các vector nhúng đã được tạo"""
        if not self.is_trained:
            raise ValueError("Mô hình chưa được huấn luyện")
        return self.embeddings
    
    def transform_text(self, text):
        """Chuyển đổi văn bản mới thành vector nhúng"""
        if not self.is_trained:
            raise ValueError("Mô hình chưa được huấn luyện")
        return self.vectorizer.transform([text]).toarray()
    
    def get_recommendations(self, item_id, k=5):
        """Phương thức yêu cầu nhưng không thực hiện - cần FAISS"""
        raise NotImplementedError("Mô hình TF-IDF không hỗ trợ đề xuất trực tiếp, cần sử dụng với FaissIndexModel")
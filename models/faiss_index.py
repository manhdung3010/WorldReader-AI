import faiss
import numpy as np
from models.base_model import BaseRecommendationModel

class FaissIndexModel(BaseRecommendationModel):
    """Mô hình chỉ mục FAISS để tìm kiếm nhanh các sản phẩm tương tự"""
    
    def __init__(self, embedding_model=None):
        super().__init__()
        self.embedding_model = embedding_model
        self.index = None
        self.data = None
    
    def train(self, data=None):
        """Xây dựng chỉ mục FAISS từ các vector nhúng"""
        if self.embedding_model is None:
            raise ValueError("Cần cung cấp mô hình embedding trước khi xây dựng chỉ mục FAISS")
        
        if not self.embedding_model.is_ready():
            raise ValueError("Mô hình embedding chưa được huấn luyện")
        
        # Lưu dữ liệu để truy vấn sau này
        self.data = self.embedding_model.data if data is None else data
        
        # Lấy các vector nhúng
        embeddings = self.embedding_model.get_embeddings()
        
        # Chuyển đổi sang float32 (yêu cầu của FAISS)
        embeddings = embeddings.astype('float32')
        
        # Số chiều của vector
        dimension = embeddings.shape[1]
        
        # Khởi tạo chỉ mục FAISS (IndexFlatL2: chỉ mục đơn giản với khoảng cách Euclid)
        self.index = faiss.IndexFlatL2(dimension)
        
        # Thêm vector vào chỉ mục
        self.index.add(embeddings)
        
        self.is_trained = True
        
        print(f"✅ Đã xây dựng chỉ mục FAISS với {self.index.ntotal} vector")
        return self.index
    
    def update(self, new_data=None):
        """Cập nhật chỉ mục FAISS với các vector nhúng mới"""
        if self.embedding_model is None:
            raise ValueError("Cần cung cấp mô hình embedding trước khi cập nhật chỉ mục FAISS")
        
        if not self.is_trained:
            return self.train(new_data)
        
        # Cập nhật dữ liệu để truy vấn sau này
        if new_data is not None:
            import pandas as pd
            self.data = pd.concat([self.data, new_data], ignore_index=True)
        else:
            self.data = self.embedding_model.data
        
        # Lấy tất cả các vector nhúng từ mô hình embedding đã cập nhật
        embeddings = self.embedding_model.get_embeddings()
        
        # Nhận kích thước cũ của chỉ mục
        old_size = self.index.ntotal
        
        # Nếu chúng ta có vector mới (kích thước embeddings > kích thước cũ của chỉ mục)
        if embeddings.shape[0] > old_size:
            # Lấy chỉ những vector mới
            new_embeddings = embeddings[old_size:].astype('float32')
            
            # Thêm vector mới vào chỉ mục
            self.index.add(new_embeddings)
            
            print(f"✅ Đã cập nhật chỉ mục FAISS từ {old_size} thành {self.index.ntotal} vector")
        else:
            print("ℹ️ Không có vector mới để cập nhật chỉ mục FAISS")
    
        return self.index
    
    def get_recommendations(self, item_id, k=5):
        """Tìm k sản phẩm tương tự với sản phẩm có ID đã cho"""
        if not self.is_trained:
            raise ValueError("Mô hình chưa được huấn luyện")
        
        if self.data is None:
            raise ValueError("Không có dữ liệu sản phẩm")
        
        # Tìm vị trí của sản phẩm trong DataFrame
        try:
            product_idx = self.data.index[self.data['id'] == item_id].tolist()[0]
        except (IndexError, KeyError):
            print(f"❌ Không tìm thấy sản phẩm có ID: {item_id}")
            return []
        
        # Lấy vector nhúng của sản phẩm từ mô hình embedding
        query_vector = self.embedding_model.get_embeddings()[product_idx].reshape(1, -1).astype('float32')
        
        # Tìm kiếm k+1 sản phẩm gần nhất (bao gồm cả sản phẩm hiện tại)
        distances, indices = self.index.search(query_vector, k+1)
        
        # Loại bỏ sản phẩm hiện tại khỏi kết quả
        similar_indices = [idx for idx in indices[0] if idx != product_idx][:k]
        
        # Lấy thông tin sản phẩm tương tự
        similar_products = self.data.iloc[similar_indices][['id', 'name', 'description']].to_dict('records')
        
        return similar_products
    
    def get_recommendations_batch(self, item_ids, k=5):
        """Lấy đề xuất cho nhiều sản phẩm cùng lúc"""
        result = {}
        for item_id in item_ids:
            result[item_id] = self.get_recommendations(item_id, k)
        return result

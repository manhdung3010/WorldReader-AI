from abc import ABC, abstractmethod

class BaseRecommendationModel(ABC):
    """Lớp cơ sở cho các mô hình đề xuất"""
    
    def __init__(self):
        self.is_trained = False
    
    @abstractmethod
    def train(self, data):
        """Huấn luyện mô hình với dữ liệu đã cho"""
        pass
    
    @abstractmethod
    def get_recommendations(self, item_id, k=5):
        """Lấy k đề xuất cho một mục đã cho"""
        pass
    
    def is_ready(self):
        """Kiểm tra xem mô hình đã được huấn luyện chưa"""
        return self.is_trained
# main.py
from api.recommendation_api import RecommendationAPI
from data.data_loader import DataLoader
from data.preprocessor import DataPreprocessor
from models.tfidf_model import TfidfEmbeddingModel
from models.faiss_index import FaissIndexModel
from config.settings import Config
import pandas as pd

# Hệ thống gợi ý chính
class ProductRecommendationSystem:
    """Hệ thống gợi ý sản phẩm tổng thể kết hợp tất cả các thành phần"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.preprocessor = DataPreprocessor()
        self.embedding_model = None
        self.index_model = None
        self.products_df = None
        self.processed_df = None
        self.is_trained = False
    
    def load_data(self, source='database', **kwargs):
        """Tải dữ liệu từ nguồn được chỉ định"""
        if source == 'database':
            limit = kwargs.get('limit', 1000)
            self.products_df = self.data_loader.load_from_database(limit=limit)
        elif source == 'csv':
            file_path = kwargs.get('file_path')
            if not file_path:
                raise ValueError("Cần chỉ định file_path cho nguồn CSV")
            self.products_df = self.data_loader.load_from_csv(file_path)
        else:
            raise ValueError(f"Nguồn dữ liệu không được hỗ trợ: {source}")
        
        print(f"🔍 Đã tải {len(self.products_df)} sản phẩm từ {source}")
        return self.products_df
    
    def load_product_by_id(self, product_id):
        """Tải sản phẩm theo ID"""
        product = self.data_loader.load_by_ids([product_id])
        if product.empty:
            print(f"❌ Không tìm thấy sản phẩm có ID: {product_id}")
            return None
        return product
    
    def preprocess_data(self, data=None):
        """Tiền xử lý dữ liệu sản phẩm"""
        df_to_process = data if data is not None else self.products_df
        
        if df_to_process is None:
            raise ValueError("Chưa tải dữ liệu sản phẩm")
        
        processed = self.preprocessor.prepare_product_data(df_to_process)
        
        if data is None:
            self.processed_df = processed
            print(f"✅ Đã xử lý {len(self.processed_df)} sản phẩm")
        
        return processed
    
    def build_embedding_model(self, model_type='tfidf', **kwargs):
        """Xây dựng mô hình nhúng"""
        if model_type == 'tfidf':
            max_features = kwargs.get('max_features', Config.EMBEDDING_SIZE)
            ngram_range = kwargs.get('ngram_range', (1, 2))
            language = kwargs.get('language', 'english')
            
            self.embedding_model = TfidfEmbeddingModel(
                max_features=max_features,
                ngram_range=ngram_range,
                language=language
            )
        else:
            raise ValueError(f"Loại mô hình nhúng không được hỗ trợ: {model_type}")
        
        return self.embedding_model
    
    def build_index_model(self, index_type='faiss'):
        """Xây dựng mô hình chỉ mục"""
        if index_type == 'faiss':
            self.index_model = FaissIndexModel(embedding_model=self.embedding_model)
        else:
            raise ValueError(f"Loại mô hình chỉ mục không được hỗ trợ: {index_type}")
        
        return self.index_model
    
    def train(self, **kwargs):
        """Huấn luyện toàn bộ hệ thống gợi ý"""
        print("🚀 Bắt đầu huấn luyện hệ thống gợi ý sản phẩm...")
        
        # Tham số huấn luyện
        source = kwargs.get('source', 'database')
        limit = kwargs.get('limit', 1000)
        model_type = kwargs.get('model_type', 'tfidf')
        index_type = kwargs.get('index_type', 'faiss')
        max_features = kwargs.get('max_features', Config.EMBEDDING_SIZE)
        
        # 1. Tải dữ liệu
        self.load_data(source=source, limit=limit)
        
        # 2. Tiền xử lý dữ liệu
        self.preprocess_data()
        
        # 3. Xây dựng và huấn luyện mô hình nhúng
        self.build_embedding_model(
            model_type=model_type, 
            max_features=max_features
        )
        self.embedding_model.train(self.processed_df)
        
        # 4. Xây dựng và huấn luyện mô hình chỉ mục
        self.build_index_model(index_type=index_type)
        self.index_model.train()
        
        self.is_trained = True
        print("✅ Đã hoàn thành huấn luyện hệ thống!")
        return self
    
    def update_with_product(self, product_data):
        """Cập nhật hệ thống với một sản phẩm mới hoặc đã được cập nhật"""
        # Kiểm tra xem hệ thống đã được huấn luyện chưa
        if not self.is_trained:
            print("❓ Hệ thống chưa được huấn luyện. Đang khởi tạo huấn luyện...")
            return self.train()
        
        product_id = product_data.iloc[0]['id'] if isinstance(product_data, pd.DataFrame) else product_data['id']
        print(f"🔄 Cập nhật hệ thống với sản phẩm ID: {product_id}")
        
        # Chuyển đổi sang DataFrame nếu cần
        if not isinstance(product_data, pd.DataFrame):
            product_data = pd.DataFrame([product_data])
        
        # Tiền xử lý sản phẩm mới
        processed_product = self.preprocess_data(product_data)
        
        # Cập nhật mô hình nhúng với sản phẩm mới
        self.embedding_model.update(processed_product)
        
        # Cập nhật mô hình chỉ mục
        self.index_model.update()
        
        print(f"✅ Đã cập nhật hệ thống với sản phẩm ID: {product_id}")
        return True
    
    def update_with_products_batch(self, products_df):
        """Cập nhật hệ thống với nhiều sản phẩm cùng lúc"""
        # Kiểm tra xem hệ thống đã được huấn luyện chưa
        if not self.is_trained:
            print("❓ Hệ thống chưa được huấn luyện. Đang khởi tạo huấn luyện...")
            return self.train()
        
        print(f"🔄 Cập nhật hệ thống với {len(products_df)} sản phẩm mới")
        
        # Tiền xử lý các sản phẩm mới
        processed_products = self.preprocess_data(products_df)
        
        # Cập nhật mô hình nhúng với các sản phẩm mới
        self.embedding_model.update(processed_products)
        
        # Cập nhật mô hình chỉ mục
        self.index_model.update()
        
        print(f"✅ Đã cập nhật hệ thống với {len(products_df)} sản phẩm mới")
        return True
    
    def delete_product(self, product_id):
        """Xóa một sản phẩm khỏi hệ thống gợi ý"""
        if not self.is_trained:
            raise ValueError("Hệ thống chưa được huấn luyện")
        
        try:
            print(f"🔄 Đang xóa sản phẩm ID: {product_id} khỏi hệ thống gợi ý")
            
            # Lọc bỏ sản phẩm khỏi DataFrame
            self.products_df = self.products_df[self.products_df['id'] != product_id]
            
            # Tiền xử lý lại dữ liệu
            self.processed_df = self.preprocess_data()
            
            # Huấn luyện lại mô hình với dữ liệu đã cập nhật
            self.embedding_model.train(self.processed_df)
            self.index_model.train()
            
            print(f"✅ Đã cập nhật hệ thống sau khi xóa sản phẩm ID: {product_id}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật hệ thống sau khi xóa sản phẩm {product_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def delete_products_batch(self, product_ids):
        """Xóa nhiều sản phẩm cùng lúc"""
        if not self.is_trained:
            raise ValueError("Hệ thống chưa được huấn luyện")
        
        try:
            # Xóa từ DataFrame
            self.products_df = self.products_df[~self.products_df['id'].isin(product_ids)]
            
            # Cập nhật lại mô hình nhúng và chỉ mục
            self.train()
            
            return True
        except Exception as e:
            print(f"❌ Lỗi khi xóa sản phẩm hàng loạt: {e}")
            return False
    
    def get_recommendations(self, product_id, k=None):
        """Lấy các sản phẩm tương tự cho một sản phẩm"""
        if not self.is_trained:
            raise ValueError("Hệ thống chưa được huấn luyện")
        
        k = k or Config.DEFAULT_K
        return self.index_model.get_recommendations(product_id, k)
    
    def get_recommendations_batch(self, product_ids, k=None):
        """Lấy đề xuất cho nhiều sản phẩm cùng lúc"""
        if not self.is_trained:
            raise ValueError("Hệ thống chưa được huấn luyện")
        
        k = k or Config.DEFAULT_K
        return self.index_model.get_recommendations_batch(product_ids, k)
    
    def merge_recommendations(self, recommendations_dict, k=5):
        """
        Gộp và sắp xếp các gợi ý từ nhiều sản phẩm yêu thích
        
        Args:
            recommendations_dict (dict): Dictionary chứa các gợi ý theo product_id
            k (int): Số lượng gợi ý muốn trả về
            
        Returns:
            list: Danh sách các sản phẩm được gợi ý đã được gộp và sắp xếp
        """
        # Dictionary để theo dõi điểm số tích lũy cho mỗi sản phẩm
        merged_scores = {}
        
        # Duyệt qua các gợi ý của từng sản phẩm
        for favorite_id, recommendations in recommendations_dict.items():
            for product in recommendations:
                product_id = product['id']
                
                # Bỏ qua nếu sản phẩm nằm trong danh sách yêu thích
                if str(product_id) in str(recommendations_dict.keys()):
                    continue
                    
                # Tính điểm số dựa trên thông tin có sẵn
                # Có thể điều chỉnh cách tính điểm tùy theo yêu cầu
                if 'score' in product:
                    score = product['score']
                else:
                    score = 1.0  # Điểm mặc định nếu không có score
                    
                # Cộng dồn điểm số
                if product_id in merged_scores:
                    merged_scores[product_id]['score'] += score
                    merged_scores[product_id]['count'] += 1
                else:
                    merged_scores[product_id] = {
                        'id': product_id,
                        'name': product.get('name', ''),
                        'description': product.get('description', ''),
                        'score': score,
                        'count': 1
                    }
        
        # Tính điểm trung bình và tạo danh sách kết quả
        results = []
        for product_id, data in merged_scores.items():
            avg_score = data['score'] / data['count']
            results.append({
                'id': data['id'],
                'name': data['name'],
                'description': data['description'],
                'score': avg_score,
                'frequency': data['count']
            })
        
        # Sắp xếp theo điểm số và lấy k kết quả đầu tiên
        results.sort(key=lambda x: (x['score'], x['frequency']), reverse=True)
        return results[:k]
    
def main():
    """Hàm chính để khởi chạy hệ thống"""
    # Khởi tạo hệ thống gợi ý
    recommendation_system = ProductRecommendationSystem()
    
    # Huấn luyện hệ thống
    recommendation_system.train(limit=5000)
    
    # Khởi tạo và chạy API
    api = RecommendationAPI(recommendation_system)
    api.run()

if __name__ == "__main__":
    main()
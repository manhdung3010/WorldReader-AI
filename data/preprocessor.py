import pandas as pd
from utils.text_utils import preprocess_text

class DataPreprocessor:
    """Lớp xử lý và chuẩn bị dữ liệu cho mô hình"""
    
    @staticmethod
    def prepare_product_data(df):
        """Chuẩn bị dữ liệu sản phẩm cho việc tạo vector nhúng"""
        if df is None or len(df) == 0:
            return pd.DataFrame(columns=['id', 'name', 'description', 'combined_features'])
        
        # Tạo bản sao để không thay đổi dữ liệu gốc
        processed_df = df.copy()
        
        # Tiền xử lý tên sản phẩm
        processed_df['name_processed'] = processed_df['name'].apply(preprocess_text)
        
        # Tiền xử lý mô tả sản phẩm
        processed_df['description_processed'] = processed_df['description'].apply(preprocess_text)
        
        # Kết hợp tên (trọng số cao hơn) và mô tả
        processed_df['combined_features'] = (
            processed_df['name_processed'] + " " + 
            processed_df['name_processed'] + " " + 
            processed_df['description_processed']
        )
        
        return processed_df
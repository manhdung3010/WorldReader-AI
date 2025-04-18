from flask import Flask, request, jsonify
from config.settings import Config

class RecommendationAPI:
    """API cho hệ thống gợi ý sản phẩm"""
    
    def __init__(self, recommendation_system):
        self.app = Flask(__name__)
        self.recommendation_system = recommendation_system
        self.setup_routes()
    
    def setup_routes(self):
        """Thiết lập các route cho API"""
        
        @self.app.route('/api/recommend', methods=['GET'])
        def recommend():
            """API endpoint để lấy các sản phẩm tương tự"""
            product_id = request.args.get('product_id', type=int)
            k = request.args.get('k', default=Config.DEFAULT_K, type=int)
            
            if not product_id:
                return jsonify({"error": "Thiếu product_id"}), 400
            
            try:
                similar_products = self.recommendation_system.get_recommendations(product_id, k)
                return jsonify({
                    "success": True,
                    "product_id": product_id,
                    "recommendations": similar_products
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/recommend/batch', methods=['POST'])
        def recommend_batch():
            """API endpoint để lấy đề xuất cho nhiều sản phẩm cùng lúc"""
            data = request.get_json()
            
            if not data or 'product_ids' not in data:
                return jsonify({"error": "Thiếu danh sách product_ids"}), 400
            
            product_ids = data['product_ids']
            k = data.get('k', Config.DEFAULT_K)
            
            try:
                recommendations = self.recommendation_system.get_recommendations_batch(product_ids, k)
                return jsonify({
                    "success": True,
                    "recommendations": recommendations
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/update', methods=['POST'])
        def update_model():
            """API endpoint để cập nhật mô hình với sản phẩm mới"""
            data = request.get_json()
            
            if not data:
                return jsonify({"error": "Không có dữ liệu sản phẩm được cung cấp"}), 400
            
            try:
                # Import pandas nội bộ để tránh import thừa ở các module khác
                import pandas as pd
                
                # Kiểm tra nếu có nhiều sản phẩm hoặc chỉ một sản phẩm
                if isinstance(data, list):
                    # Nhiều sản phẩm
                    products_df = pd.DataFrame(data)
                    result = self.recommendation_system.update_with_products_batch(products_df)
                else:
                    # Một sản phẩm - truyền trực tiếp object
                    result = self.recommendation_system.update_with_product(data)
                
                return jsonify({
                    "success": result,
                    "message": "Đã cập nhật mô hình thành công"
                })
            except Exception as e:
                import traceback
                traceback.print_exc()  # In stack trace để debug
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Kiểm tra trạng thái của API"""
            return jsonify({
                "status": "ok",
                "system_trained": self.recommendation_system.is_trained
            })
    
    def run(self, host=None, port=None, debug=None):
        """Khởi chạy API server"""
        self.app.run(
            host=host or Config.API_HOST,
            port=port or Config.API_PORT,
            debug=debug or Config.DEBUG_MODE
        )

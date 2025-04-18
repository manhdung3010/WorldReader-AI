from flask import Flask, request, jsonify
from config.settings import Config
from chatbot.document_chatbot import DocumentChatbot
import os

class RecommendationAPI:
    """API cho hệ thống gợi ý sản phẩm"""
    
    def __init__(self, recommendation_system):
        self.app = Flask(__name__)
        self.recommendation_system = recommendation_system
        self.chatbot = DocumentChatbot()
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
        
        @self.app.route('/api/chatbot/load-document', methods=['POST'])
        def load_document():
            """API endpoint để tải tài liệu vào chatbot"""
            if 'file' not in request.files:
                return jsonify({"success": False, "error": "Không tìm thấy file"}), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({"success": False, "error": "Không có file được chọn"}), 400
                
            try:
                # Sử dụng phương thức save_uploaded_file của chatbot
                file_path = self.chatbot.save_uploaded_file(file)
                
                if file_path:
                    # Lấy danh sách file đã tải
                    loaded_files = self.chatbot.get_loaded_files()
                    
                    return jsonify({
                        "success": True,
                        "message": "Đã tải tài liệu thành công",
                        "filename": os.path.basename(file_path),
                        "loaded_files": loaded_files
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": "Không thể đọc hoặc lưu tài liệu"
                    }), 500
                        
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ Lỗi khi tải tài liệu: {e}")
                print(error_trace)
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route('/api/chatbot/files', methods=['GET'])
        def get_files():
            """API endpoint để lấy danh sách các file đã tải"""
            try:
                loaded_files = self.chatbot.get_loaded_files()
                return jsonify({
                    "success": True,
                    "files": loaded_files
                })
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ Lỗi khi lấy danh sách file: {e}")
                print(error_trace)
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route('/api/chatbot/files/<filename>', methods=['DELETE'])
        def delete_file(filename):
            """API endpoint để xóa một file cụ thể"""
            try:
                success = self.chatbot.delete_file(filename)
                if success:
                    return jsonify({
                        "success": True,
                        "message": f"Đã xóa file {filename}",
                        "loaded_files": self.chatbot.get_loaded_files()
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": f"Không thể xóa file {filename}"
                    }), 400
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ Lỗi khi xóa file: {e}")
                print(error_trace)
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route('/api/chatbot/files', methods=['DELETE'])
        def delete_all_files():
            """API endpoint để xóa tất cả file đã tải"""
            try:
                success = self.chatbot.delete_all_files()
                if success:
                    return jsonify({
                        "success": True,
                        "message": "Đã xóa tất cả file"
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": "Có lỗi khi xóa một số file"
                    }), 500
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ Lỗi khi xóa tất cả file: {e}")
                print(error_trace)
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route('/api/chatbot/ask', methods=['POST'])
        async def ask_question():
            """API endpoint để hỏi chatbot"""
            data = request.get_json()
            
            if not data or 'question' not in data:
                return jsonify({"error": "Thiếu câu hỏi"}), 400
                
            try:
                result = await self.chatbot.get_answer(data['question'])
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/api/chatbot/upload', methods=['POST'])
        def upload_file():
            """API endpoint để upload file"""
            if 'file' not in request.files:
                return jsonify({"error": "Không tìm thấy file"}), 400
                
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "Không có file được chọn"}), 400
                
            file_path = self.chatbot.save_uploaded_file(file)
            if file_path:
                return jsonify({
                    "success": True,
                    "message": "Upload thành công",
                    "file_path": file_path
                })
            return jsonify({
                "error": "Không thể upload file"
            }), 500

        @self.app.route('/api/chatbot/chat', methods=['POST'])
        def chat():
            """API endpoint để chat với bot"""
            data = request.get_json()
            
            if not data or 'question' not in data:
                return jsonify({"error": "Thiếu câu hỏi"}), 400
                
            # Lấy lịch sử chat từ request
            history = data.get('history', None)
            
            try:
                # Tạo session mới và trả lời câu hỏi
                result = self.chatbot.get_answer(data['question'], history)
                return jsonify(result)
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"❌ Lỗi khi chat: {e}")
                print(error_trace)
                return jsonify({"error": str(e)}), 500
    
    def run(self, host=None, port=None, debug=None):
        """Khởi chạy API server"""
        self.app.run(
            host=host or Config.API_HOST,
            port=port or Config.API_PORT,
            debug=debug or Config.DEBUG_MODE
        )

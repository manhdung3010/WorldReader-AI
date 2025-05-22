import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from datetime import datetime
from models.product_model import Product

class DocumentChatbot:
    """Chatbot sử dụng Gemini để trả lời câu hỏi về tài liệu và sản phẩm"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Khởi tạo Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel(os.getenv('GOOGLE_MODEL'))
        
        # Khởi tạo biến để lưu trữ nội dung tài liệu và danh sách file đã tải
        self.document_contents = {}  # Dictionary để lưu nội dung của từng file
        self.loaded_files = []
        self.document_context = ""  # Thêm biến mới để cache context
        
        # Khởi tạo Product model
        self.product_model = Product()
        
        # Xác định thư mục gốc của dự án và thư mục uploads
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
        except:
            current_dir = os.getcwd()
            project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Thư mục uploads nằm trong thư mục chatbot
        self.upload_folder = os.path.join(current_dir, "uploads")
        
        # Tạo thư mục uploads nếu chưa tồn tại
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
            print(f"✅ Đã tạo thư mục uploads tại: {self.upload_folder}")
        else:  
            print(f"✅ Thư mục uploads đã tồn tại tại: {self.upload_folder}")

        # Tự động load lại tất cả documents khi khởi tạo
        print("🔄 Đang load lại tất cả tài liệu...")
        self.reload_all_documents()

    def reload_all_documents(self):
        """Load lại tất cả tài liệu từ thư mục uploads"""
        try:
            self.document_contents = {}  # Reset trước khi tải lại
            self.loaded_files = []
            self.document_context = ""  # Reset context
            
            if not os.path.exists(self.upload_folder):
                print(f"❌ Thư mục uploads không tồn tại: {self.upload_folder}")
                return
                
            all_files = os.listdir(self.upload_folder)
            for filename in all_files:
                file_path = os.path.join(self.upload_folder, filename)
                if os.path.isfile(file_path):  # Chỉ xử lý file, bỏ qua thư mục
                    if filename.lower().endswith('.pdf'):
                        self.load_pdf(file_path)
                    elif filename.lower().endswith('.txt'):
                        self.load_text(file_path)
                    elif filename.lower().endswith(('.doc', '.docx')):
                        self.load_word(file_path)
            
            # Cập nhật document_context sau khi load xong
            self._update_document_context()
            print(f"✅ Đã load {len(self.loaded_files)} tài liệu và cập nhật context")
        except Exception as e:
            print(f"❌ Lỗi khi load lại tài liệu: {e}")

    def _update_document_context(self):
        """Private method để cập nhật document context"""
        context = "Dưới đây là nội dung tài liệu tham khảo:\n\n"
        for idx, (file_path, content) in enumerate(self.document_contents.items()):
            file_name = os.path.basename(file_path)
            context += f"\n\n--- DOCUMENT {idx+1}: {file_name} ---\n\n{content}"
        self.document_context = context

    def save_uploaded_file(self, file):
        """Lưu file upload vào thư mục"""
        try:
            # Tạo thư mục uploads nếu chưa tồn tại
            if not os.path.exists(self.upload_folder):
                os.makedirs(self.upload_folder)
                print(f"✅ Đã tạo thư mục uploads: {self.upload_folder}")
                
            # Tạo tên file với timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(self.upload_folder, filename)
            
            # Lưu file
            print(f"Đang lưu file tại: {file_path}")
            file.save(file_path)
            
            # Kiểm tra xem file đã được lưu thành công chưa
            if not os.path.exists(file_path):
                print(f"❌ Không thể lưu file tại: {file_path}")
                return None
                
            print(f"✅ Đã lưu file: {filename}")
            
            # Load nội dung file
            success = False
            if file.filename.lower().endswith('.pdf'):
                success = self.load_pdf(file_path)
            elif file.filename.lower().endswith('.txt'):
                success = self.load_text(file_path)
            elif file.filename.lower().endswith(('.doc', '.docx')):
                success = self.load_word(file_path)
                
            if success:
                # Cập nhật context sau khi thêm file mới
                self._update_document_context()
                return file_path
            else:
                # Nếu không load được, xóa file
                if os.path.exists(file_path):
                    os.remove(file_path)
                return None
                
        except Exception as e:
            print(f"❌ Lỗi khi lưu file: {e}")
            import traceback
            traceback.print_exc()
            return None

    def load_pdf(self, pdf_path):
        """Đọc nội dung từ file PDF"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:  # Chỉ thêm nếu có text
                    text += page_text + "\n"
            
            # Lưu nội dung vào dictionary với key là đường dẫn file
            self.document_contents[pdf_path] = text
            if pdf_path not in self.loaded_files:
                self.loaded_files.append(pdf_path)
            print(f"✅ Đã load file PDF: {os.path.basename(pdf_path)}")
            return True
        except Exception as e:
            print(f"❌ Lỗi khi đọc file PDF {os.path.basename(pdf_path)}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_text(self, text_path):
        """Đọc nội dung từ file text"""
        try:
            with open(text_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Lưu nội dung vào dictionary với key là đường dẫn file
            self.document_contents[text_path] = content
            if text_path not in self.loaded_files:
                self.loaded_files.append(text_path)
            print(f"✅ Đã load file text: {os.path.basename(text_path)}")
            return True
        except UnicodeDecodeError:
            # Thử lại với encoding khác
            try:
                with open(text_path, 'r', encoding='latin-1') as file:
                    content = file.read()
                self.document_contents[text_path] = content
                if text_path not in self.loaded_files:
                    self.loaded_files.append(text_path)
                print(f"✅ Đã load file text (latin-1): {os.path.basename(text_path)}")
                return True
            except Exception as e:
                print(f"❌ Lỗi khi đọc file text {os.path.basename(text_path)}: {e}")
                return False
        except Exception as e:
            print(f"❌ Lỗi khi đọc file text {os.path.basename(text_path)}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def load_word(self, doc_path):
        """Đọc nội dung từ file Word (.doc, .docx)"""
        try:
            import textract
            
            # Đọc nội dung file bằng textract
            text = textract.process(doc_path).decode('utf-8')
            
            # Lưu nội dung vào dictionary
            self.document_contents[doc_path] = text
            if doc_path not in self.loaded_files:
                self.loaded_files.append(doc_path)
            print(f"✅ Đã load file Word: {os.path.basename(doc_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi khi đọc file Word {os.path.basename(doc_path)}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_loaded_files(self):
        """Lấy danh sách các file đã tải"""
        return [os.path.basename(file_path) for file_path in self.loaded_files]

    def delete_file(self, file_name):
        """Xóa một file cụ thể dựa trên tên file"""
        try:
            # Tìm đường dẫn đầy đủ từ tên file
            full_path = None
            for path in self.loaded_files:
                if os.path.basename(path) == file_name:
                    full_path = path
                    break
            
            if not full_path:
                print(f"❌ Không tìm thấy file: {file_name}")
                return False
            
            # Xóa file và loại bỏ khỏi danh sách
            if os.path.exists(full_path):
                os.remove(full_path)
                
            if full_path in self.document_contents:
                del self.document_contents[full_path]
                
            if full_path in self.loaded_files:
                self.loaded_files.remove(full_path)
                
            # Cập nhật context sau khi xóa file
            self._update_document_context()
            print(f"✅ Đã xóa file: {file_name}")
            return True
        except Exception as e:
            print(f"❌ Lỗi khi xóa file {file_name}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def delete_all_files(self):
        """Xóa tất cả các file đã tải"""
        success = True
        for file_path in self.loaded_files[:]:  # Create a copy to iterate
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
                if file_path in self.document_contents:
                    del self.document_contents[file_path]
                    
                self.loaded_files.remove(file_path)
            except Exception as e:
                print(f"❌ Lỗi khi xóa file {os.path.basename(file_path)}: {e}")
                success = False
        
        self.document_contents = {}
        self.loaded_files = []
        self.document_context = ""  # Reset context
        
        if success:
            print("✅ Đã xóa tất cả các file")
        return success

    def add_document_context(self):
        """Thêm context từ tất cả tài liệu vào chat"""
        if not self.document_contents:
            return "Không có tài liệu nào được load"
        
        # Sử dụng context đã được cache
        response = self.chat.send_message(self.document_context)
        return response.text

    def get_chat_history(self):
        """Lấy lịch sử chat"""
        return self.chat_history

    def add_to_history(self, role, content):
        """Thêm message vào lịch sử chat"""
        self.chat_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_answer(self, question, history=None):
        """Answer questions with chat history from client"""
        try:
            chat = self.model.start_chat(history=[])
            
            # Kiểm tra xem câu hỏi có liên quan đến sản phẩm không
            product_results = self.product_model.search_products(question)
            product_context = ""
            if product_results:
                product_context = "\n\nThông tin sản phẩm liên quan:\n"
                for product in product_results:
                    product_context += f"- {product.get('name')}: {product.get('description')}\n"
            
            if not self.document_contents and not product_results:
                return {
                    "success": False,
                    "error": "I apologize, but I don't have any information to answer this question."
                }
            
            # System prompt in English
            system_prompt = """You are WorldReader AI, a friendly and knowledgeable book assistant. Your role is to help users discover and understand books while providing insights from their uploaded documents and product information.

                Core Functions:
                1. Provide engaging book descriptions and recommendations
                2. Share interesting facts about authors and their works
                3. Help users find books that match their interests
                4. Answer questions about uploaded documents
                5. Provide information about available products

                Response Style:
                - Keep answers friendly and conversational
                - Be concise but informative
                - Use simple, clear language
                - Include interesting details that make books come alive
                - Share personal reading insights when relevant
                - Include relevant product information when appropriate
                - Provide direct answers without phrases like "According to the document" or "Based on the information provided"
                - Start responses naturally and conversationally

                For Book Queries:
                - Give a brief, engaging summary
                - Mention key themes and why people love the book
                - Share interesting author background
                - Suggest similar books readers might enjoy

                For Document Queries:
                - Focus on the most relevant information
                - Make complex topics easy to understand
                - Use examples to illustrate points
                - Keep responses clear and to the point
                - Provide information directly without referencing the source document

                For Product Queries:
                - Provide accurate product information
                - Highlight key features and benefits
                - Make relevant product recommendations
                - Keep product descriptions clear and engaging

                Remember to:
                - Be warm and encouraging
                - Share your enthusiasm for books
                - Make recommendations personal and relevant
                - Help users discover their next great read
                - Provide helpful product information
                - Give direct answers without unnecessary qualifiers"""
                            
            chat.send_message(system_prompt)
            chat.send_message(self.document_context)
            if product_context:
                chat.send_message(product_context)
            
            if history and len(history) > 0:
                context = "Based on the previous conversation:\n\n"
                for msg in history:
                    context += f"{msg['role']}: {msg['content']}\n"
                context += f"\nRegarding the question: {question}\nPlease respond professionally and warmly."
                response = chat.send_message(context)
            else:
                response = chat.send_message(question)
                
            return {
                "success": True,
                "answer": response.text
            }
        except Exception as e:
            print(f"❌ Error while answering question: {e}")
            return {
                "success": False, 
                "error": "Sorry, an error occurred. Please try again later."
            }
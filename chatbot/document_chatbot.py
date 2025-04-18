import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from datetime import datetime

class DocumentChatbot:
    """Chatbot sử dụng Gemini để trả lời câu hỏi về tài liệu"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Khởi tạo Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel(os.getenv('GOOGLE_MODEL'))
        
        # Khởi tạo biến để lưu trữ nội dung tài liệu và danh sách file đã tải
        self.document_contents = {}  # Dictionary để lưu nội dung của từng file
        self.loaded_files = []
        
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
                        print(f"⚠️ Chưa hỗ trợ đầy đủ file Word: {filename}")
                        # Tạm thời coi như đã loaded để không xóa file
                        self.loaded_files.append(file_path)
            print(f"✅ Đã load {len(self.loaded_files)} tài liệu")
        except Exception as e:
            print(f"❌ Lỗi khi load lại tài liệu: {e}")

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
                print(f"⚠️ Chưa hỗ trợ đầy đủ file Word: {filename}")
                # Tạm thời coi như đã loaded để không xóa file
                self.loaded_files.append(file_path)
                success = True
                
            if success:
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
        
        if success:
            print("✅ Đã xóa tất cả các file")
        return success

    def add_document_context(self):
        """Thêm context từ tất cả tài liệu vào chat"""
        if not self.document_contents:
            return "Không có tài liệu nào được load"
        
        # Kết hợp nội dung của tất cả tài liệu với phân tách rõ ràng
        combined_content = ""
        for idx, (file_path, content) in enumerate(self.document_contents.items()):
            file_name = os.path.basename(file_path)
            combined_content += f"\n\n--- DOCUMENT {idx+1}: {file_name} ---\n\n{content}"
        
        context_prompt = f"""
        Dưới đây là nội dung tài liệu mà tôi muốn bạn tham khảo để trả lời câu hỏi:
        
        {combined_content}
        
        Hãy sử dụng thông tin từ tài liệu trên để trả lời các câu hỏi tiếp theo.
        """
        response = self.chat.send_message(context_prompt)
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
        """Trả lời câu hỏi với lịch sử chat từ client"""
        try:
            # Tạo chat session mới cho mỗi request
            chat = self.model.start_chat(history=[])
            
            # Thêm context từ tài liệu
            if not self.document_contents:
                return {
                    "success": False,
                    "error": "Không có tài liệu nào được load. Vui lòng tải tài liệu trước khi hỏi."
                }
                
            # Add document context
            context = "Dưới đây là nội dung tài liệu tham khảo:\n\n"
            for idx, (file_path, content) in enumerate(self.document_contents.items()):
                file_name = os.path.basename(file_path)
                context += f"\n\n--- DOCUMENT {idx+1}: {file_name} ---\n\n{content}"
            chat.send_message(context)
            
            # Process history and question
            if history and len(history) > 0:
                context = "Dựa vào cuộc hội thoại sau:\n\n"
                for msg in history:
                    context += f"{msg['role']}: {msg['content']}\n"
                context += f"\nVà câu hỏi hiện tại: {question}\n\nHãy trả lời dựa trên nội dung tài liệu và cuộc hội thoại."
                response = chat.send_message(context)
            else:
                response = chat.send_message(question)
                
            return {
                "success": True,
                "answer": response.text
            }
        except Exception as e:
            print(f"❌ Lỗi khi trả lời câu hỏi: {e}")
            return {
                "success": False, 
                "error": str(e)
            }
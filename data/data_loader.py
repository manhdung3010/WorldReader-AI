import pandas as pd
import pymysql
from config.settings import Config
import os

class DataLoader:
    """Lớp tải dữ liệu từ nhiều nguồn khác nhau"""

    @staticmethod
    def load_from_database(ids=None, limit=1000):
        """Tải dữ liệu sản phẩm từ cơ sở dữ liệu MySQL"""
        conn = None
        try:
            conn = pymysql.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor
            )

            with conn.cursor() as cursor:
                if ids:
                    if not isinstance(ids, (list, tuple)) or not ids:
                        print("⚠️ Danh sách ID không hợp lệ hoặc rỗng.")
                        return pd.DataFrame(columns=['id', 'name', 'description', 'price', 'categories', 'keywords', 'information'])

                    placeholders = ','.join(['%s'] * len(ids))
                    query = f"""
                        SELECT 
                            p.id, 
                            p.name, 
                            p.description,
                            p.price,
                            GROUP_CONCAT(DISTINCT c.name) as categories,
                            GROUP_CONCAT(DISTINCT k.name) as keywords,
                            GROUP_CONCAT(DISTINCT CONCAT(i.name, ':', i.info_value)) as information
                        FROM product p
                        LEFT JOIN product_categories pc ON p.id = pc.product_id
                        LEFT JOIN categories c ON pc.category_id = c.id
                        LEFT JOIN product_keywords pk ON p.id = pk.product_id
                        LEFT JOIN keyword k ON pk.keyword_id = k.id
                        LEFT JOIN info_product i ON p.id = i.product_id
                        WHERE p.id IN ({placeholders})
                        GROUP BY p.id
                    """
                    cursor.execute(query, tuple(ids))
                else:
                    query = """
                        SELECT 
                            p.id, 
                            p.name, 
                            p.description,
                            p.price,
                            GROUP_CONCAT(DISTINCT c.name) as categories,
                            GROUP_CONCAT(DISTINCT k.name) as keywords,
                            GROUP_CONCAT(DISTINCT CONCAT(i.name, ':', i.content)) as information
                        FROM product p
                        LEFT JOIN product_categories pc ON p.id = pc.product_id
                        LEFT JOIN categories c ON pc.category_id = c.id
                        LEFT JOIN product_keywords pk ON p.id = pk.product_id
                        LEFT JOIN keyword k ON pk.keyword_id = k.id
                        LEFT JOIN info_product i ON p.id = i.productId
                        GROUP BY p.id
                        LIMIT %s
                    """
                    cursor.execute(query, (limit,))

                records = cursor.fetchall()
                
           
            df = pd.DataFrame.from_records(records)
            if df.empty:
                print("⚠️ Không có dữ liệu nào được trả về từ database.")
                return pd.DataFrame(columns=['id', 'name', 'description', 'price', 'categories', 'keywords', 'information'])

            # Xử lý dữ liệu null
            df['categories'] = df['categories'].fillna('')
            df['keywords'] = df['keywords'].fillna('')
            df['information'] = df['information'].fillna('')
            df['price'] = df['price'].fillna(0)

            return df
        
        except pymysql.err.OperationalError as e:
            print(f"❌ Lỗi kết nối CSDL: {e}")
        except Exception as e:
            print(f"❌ Lỗi tải dữ liệu: {e}")
        finally:
            if conn and conn.open:
                conn.close()

        return pd.DataFrame(columns=['id', 'name', 'description', 'price', 'categories', 'keywords', 'information'])

    @staticmethod
    def load_by_ids(ids):
        """Tải sản phẩm theo danh sách ID"""
        return DataLoader.load_from_database(ids=ids)

    @staticmethod
    def load_from_csv(file_path):
        """Tải dữ liệu từ tệp CSV"""
        try: 
            df = pd.read_csv(file_path)
            required = ['id', 'name', 'description', 'price', 'categories', 'keywords', 'information']
            if not all(col in df.columns for col in required):
                print(f"❌ Tệp CSV thiếu cột bắt buộc: {required}")
                return pd.DataFrame(columns=required)

            # Xử lý dữ liệu null
            df['categories'] = df['categories'].fillna('')
            df['keywords'] = df['keywords'].fillna('')
            df['information'] = df['information'].fillna('')
            df['price'] = df['price'].fillna(0)

            return df[required]

        except FileNotFoundError:
            print(f"❌ Không tìm thấy tệp: {file_path}")
        except Exception as e:
            print(f"❌ Lỗi đọc tệp CSV: {e}")

        return pd.DataFrame(columns=['id', 'name', 'description', 'price', 'categories', 'keywords', 'information'])

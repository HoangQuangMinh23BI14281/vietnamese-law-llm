import weaviate
import json

# Kết nối Weaviate (Nếu chạy từ máy local thì dùng localhost, nếu trong docker thì dùng tên service)
client = weaviate.Client("http://localhost:8080") 

CLASS_NAME = "LegalDocument" # <--- Tên class phải khớp với weaviate_client.py

def check_data():
    try:
        # 1. Kiểm tra Schema xem đã có Class này chưa
        schema = client.schema.get()
        classes = [c['class'] for c in schema['classes']]
        print(f"📂 Các Class hiện có trong DB: {classes}")

        if CLASS_NAME not in classes:
            print(f"❌ LỖI: Chưa có class '{CLASS_NAME}'. Bạn chưa chạy service hoặc code tạo schema bị lỗi.")
            return

        # 2. Đếm số lượng object
        count = client.query.aggregate(CLASS_NAME).with_meta_count().do()
        num_objects = count['data']['Aggregate'][CLASS_NAME][0]['meta']['count']
        
        print(f"📊 Số lượng chunk trong '{CLASS_NAME}': {num_objects}")
        
        if num_objects == 0:
            print("⚠️ CẢNH BÁO: Database rỗng! Hãy upload file PDF lại.")
        else:
            # 3. Lấy thử 1 dòng xem nội dung
            result = client.query.get(CLASS_NAME, ["text", "source", "chunk_id"]).with_limit(1).do()
            print("✅ Dữ liệu mẫu (1 dòng):")
            print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ Không kết nối được Weaviate: {e}")

if __name__ == "__main__":
    check_data()
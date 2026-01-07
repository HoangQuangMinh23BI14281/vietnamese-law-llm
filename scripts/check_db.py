import weaviate
import json

# Kết nối Weaviate
client = weaviate.Client("http://localhost:8080")

class_name = "LegalDocument"

try:
    # 1. Kiểm tra tổng số lượng bản ghi
    count_result = (
        client.query
        .aggregate(class_name)
        .with_meta_count()
        .do()
    )
    count = count_result['data']['Aggregate'][class_name][0]['meta']['count']
    print(f"📊 Tổng số chunk trong DB: {count}")

    if count > 0:
        # 2. Lấy thử 1 bản ghi kèm Vector
        result = (
            client.query
            .get(class_name, ["text", "chapter", "article"])
            .with_additional(["vector"])  # Quan trọng: Yêu cầu trả về vector
            .with_limit(1)
            .do()
        )
        
        item = result['data']['Get'][class_name][0]
        vector = item['_additional']['vector']
        
        print("\n✅ MẪU DỮ LIỆU ĐẦU TIÊN:")
        print(f"- Chương: {item.get('chapter')}")
        print(f"- Điều: {item.get('article')}")
        print(f"- Nội dung (50 ký tự đầu): {item.get('text')[:50]}...")
        
        print("\n✅ KIỂM TRA VECTOR:")
        if vector:
            print(f"- Trạng thái: ĐÃ CÓ VECTOR")
            print(f"- Kích thước (Dimension): {len(vector)}") # Model bạn dùng thường là 768
            print(f"- Mẫu vector: {vector[:3]} ...")
        else:
            print("❌ Cảnh báo: Chunk này KHÔNG có vector!")
    else:
        print("⚠️ Database đang trống. Hãy upload file PDF vào Indexing Service trước.")

except Exception as e:
    print(f"❌ Lỗi kết nối Weaviate: {e}")
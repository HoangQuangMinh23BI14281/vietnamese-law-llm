import streamlit as st
import requests
import os

# --- CẤU HÌNH ---
# Dùng rstrip('/') để đảm bảo không bị thừa dấu / ở cuối URL
LLM_GATEWAY = os.getenv("LLM_GATEWAY_URL", "http://llm-gateway:8001").rstrip('/')
INDEXING_SERVICE = os.getenv("INDEXING_SERVICE_URL", "http://indexing-service:5000").rstrip('/')

st.set_page_config(page_title="Vietnam Legal AI", page_icon="⚖️", layout="wide")

st.title("⚖️ Hệ thống Tư vấn Pháp luật Thông minh")
st.markdown("---")

# Tạo Tabs
tab1, tab2 = st.tabs(["📚 Nạp Kiến Thức (Indexing)", "🤖 Hỏi Đáp Pháp Lý (Chat)"])

# ==========================================
# TAB 1: NẠP DỮ LIỆU
# ==========================================
with tab1:
    st.header("Nạp văn bản luật mới")
    st.info("💡 Hệ thống sử dụng Docling để đọc PDF (giữ bảng biểu) và Neo4j để xây dựng đồ thị liên kết.")
    
    # Thêm key để có thể reset uploader nếu cần
    uploaded_file = st.file_uploader("Tải file PDF luật (Ví dụ: Luật Đất đai 2024)", type=['pdf'])
    
    if uploaded_file and st.button("🚀 Bắt đầu xử lý", type="primary"):
        with st.spinner("⏳ Đang gửi file sang Indexing Service (vui lòng đợi)..."):
            try:
                # [FIX 1] Dùng .getvalue() để lấy bytes an toàn
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                }
                
                # [FIX 2] URL nối chuẩn
                api_url = f"{INDEXING_SERVICE}/process-file-upload"
                
                # Timeout 600s (10 phút) vì Docling xử lý OCR khá lâu
                res = requests.post(api_url, files=files, timeout=600)
                
                if res.status_code == 200:
                    st.success(f"✅ Đã xử lý xong! File: {uploaded_file.name}")
                    # Hiển thị kết quả JSON đẹp hơn
                    with st.expander("Xem chi tiết kết quả xử lý"):
                        st.json(res.json())
                else:
                    st.error(f"❌ Lỗi Server ({res.status_code}): {res.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error(f"🔌 Không thể kết nối tới Indexing Service tại: {INDEXING_SERVICE}")
                st.caption("Gợi ý: Kiểm tra xem container 'indexing-service' có đang chạy không?")
            except Exception as e:
                st.error(f"❌ Lỗi không xác định: {e}")

# ==========================================
# TAB 2: CHAT BOT
# ==========================================
with tab2:
    st.header("Trợ lý Luật sư AI")
    
    # 1. Khởi tạo lịch sử chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 2. Render lại lịch sử chat cũ
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. Xử lý Input mới
    if prompt := st.chat_input("Hãy hỏi về luật (VD: Điều kiện tách thửa đất ở Hà Nội?)"):
        # Hiển thị câu hỏi User ngay lập tức
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gọi Backend
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🔄 _Đang tra cứu Vector DB và Knowledge Graph..._")
            
            try:
                api_url = f"{LLM_GATEWAY}/chat"
                res = requests.post(api_url, json={"query": prompt}, timeout=60)
                
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "Không có câu trả lời.")
                    sources = data.get("sources", [])
                    
                    # Format câu trả lời kèm nguồn 
                    full_response = answer
                    if sources:
                        full_response += "\n\n---\n**📚 Nguồn tham khảo:**\n" + "\n".join([f"- {s}" for s in sources])
                    
                    # Cập nhật UI
                    message_placeholder.markdown(full_response)
                    
                    # Lưu vào Session State
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    error_msg = f"⚠️ Lỗi từ hệ thống AI ({res.status_code})"
                    message_placeholder.error(error_msg)
            
            except requests.exceptions.ConnectionError:
                message_placeholder.error(f"🔌 Không thể kết nối tới LLM Gateway tại: {LLM_GATEWAY}")
            except Exception as e:
                message_placeholder.error(f"❌ Lỗi kết nối: {e}")
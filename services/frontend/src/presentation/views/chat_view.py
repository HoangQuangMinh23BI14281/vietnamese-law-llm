import streamlit as st
from src.application.chat_service import ChatService

def render_chat_view(service: ChatService):
    st.header("🤖 Trợ lý Luật sư")

    # 1. Khởi tạo lịch sử chat nếu chưa có
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 2. Hiển thị toàn bộ lịch sử chat cũ
    # (Dùng container để gom nhóm tin nhắn, giúp layout ổn định hơn)
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 3. Xử lý Input mới (Thanh chat luôn ghim ở dưới cùng)
    if prompt := st.chat_input("Nhập câu hỏi pháp lý của bạn..."):
        
        # A. Hiển thị ngay câu hỏi của user lên màn hình
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        # Lưu câu hỏi vào session ngay lập tức
        st.session_state.messages.append({"role": "user", "content": prompt})

        # B. Hiển thị trạng thái đang trả lời
        with chat_container:
            with st.chat_message("assistant"):
                # Tạo một placeholder để streaming text hoặc hiện loading
                message_placeholder = st.empty()
                message_placeholder.markdown("🔄 _Đang tra cứu văn bản luật..._")
                
                try:
                    # Gọi Service lấy câu trả lời
                    response_text = service.send_message(prompt)
                    
                    # Cập nhật câu trả lời chính thức vào placeholder
                    message_placeholder.markdown(response_text)
                    
                    # Lưu câu trả lời vào session
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    error_msg = f"⚠️ Có lỗi xảy ra: {str(e)}"
                    message_placeholder.error(error_msg)

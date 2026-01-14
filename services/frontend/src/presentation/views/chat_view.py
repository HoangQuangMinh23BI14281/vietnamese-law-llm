import streamlit as st
from src.application.chat_service import ChatService

def render_chat_view(service: ChatService):
    st.header("Trợ lý Luật sư")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_container = st.container()
    
    is_ready = service.is_service_ready()
    if not is_ready:
        st.info("Hệ thống đang tải mô hình ngôn ngữ (Qwen)... Ô chat sẽ khả dụng khi tải xong.")
        if st.button("Kiểm tra lại"):
            st.rerun()

    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if prompt := st.chat_input("Nhập câu hỏi pháp lý của bạn...", disabled=not is_ready):
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
        
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("_Đang tra cứu văn bản luật..._")
                
                try:
                    response_text = service.send_message(prompt)
                    message_placeholder.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    error_msg = f"Có lỗi xảy ra: {str(e)}"
                    message_placeholder.error(error_msg)

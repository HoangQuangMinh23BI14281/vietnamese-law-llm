import streamlit as st
import time
from src.application.upload_service import UploadService

def render_upload_view(service: UploadService):
    st.header("Nạp văn bản luật")
    st.markdown("---")
    
    file = st.file_uploader("Chọn file PDF văn bản luật", type=['pdf'])
    
    if file is not None:
        col1, col2 = st.columns([1, 4])
        with col1:
            start_btn = st.button("Bắt đầu Xử lý", type="primary", use_container_width=True)
            
        if start_btn:
            start_time = time.time()
            
            with st.spinner(f"Đang đọc file '{file.name}', chia nhỏ và vector hóa... Vui lòng đợi."):
                try:
                    result = service.process_upload(file)
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    if result.success:
                        st.success(f"Xử lý thành công trong {duration:.2f} giây!")
                        with st.expander("Xem chi tiết kết quả"):
                            st.write(result.message)
                    else:
                        st.error(f"Thất bại: {result.message}")
                        
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {str(e)}")
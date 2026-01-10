import streamlit as st
import time  # <--- Thêm thư viện này để đo thời gian
from src.application.upload_service import UploadService

def render_upload_view(service: UploadService):
    st.header("Nạp văn bản luật")
    st.markdown("---")
    
    # Khu vực upload file
    file = st.file_uploader("Chọn file PDF văn bản luật", type=['pdf'])
    
    # Chỉ hiện nút xử lý khi đã chọn file
    if file is not None:
        # Dùng col để nút bấm nhỏ gọn hơn
        col1, col2 = st.columns([1, 4])
        with col1:
            start_btn = st.button(" Bắt đầu Xử lý", type="primary", use_container_width=True)
            
        if start_btn:
            # 1. Bắt đầu bấm giờ
            start_time = time.time()
            
            # 2. Hiển thị Loading (Spinner)
            # Lưu ý: Backend phải xử lý đồng bộ thì cái này mới xoay đúng thời gian thực
            with st.spinner(f" Đang đọc file '{file.name}', chia nhỏ và vector hóa... Vui lòng đợi."):
                try:
                    # Gọi service xử lý
                    result = service.process_upload(file)
                    
                    # 3. Kết thúc bấm giờ
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    # 4. Hiển thị kết quả chi tiết
                    if result.success:
                        st.success(f" Xử lý thành công trong {duration:.2f} giây!")
                        with st.expander("Xem chi tiết kết quả"):
                            st.write(result.message)
                    else:
                        st.error(f"Thất bại: {result.message}")
                        
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {str(e)}")
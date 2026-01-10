#!/bin/bash

# Đường dẫn tới thư mục models (mặc định là thư mục hiện tại)
MODEL_DIR="./models"

echo "--- Đang thiết lập quyền cho thư mục models ---"

# 1. Kiểm tra xem thư mục có tồn tại không
if [ -d "$MODEL_DIR" ]; then
    echo "Phát hiện thư mục: $MODEL_DIR"
    
    # 2. Thực hiện chmod
    echo "Đang thực hiện chmod -R 755 $MODEL_DIR..."
    chmod -R 755 "$MODEL_DIR"
    
    # 3. Kiểm tra kết quả
    if [ $? -eq 0 ]; then
        echo "Thành công: Đã cập nhật quyền truy cập."
        echo "Chi tiết: "
        ls -ld "$MODEL_DIR"
    else
        echo "Lỗi: Không thể thay đổi quyền. Thử chạy với 'sudo'."
    fi
else
    echo "Cảnh báo: Thư mục '$MODEL_DIR' không tồn tại."
    echo "Vui lòng tạo thư mục và copy model vào trước khi chạy script này."
fi

echo "------------------------------------------------"
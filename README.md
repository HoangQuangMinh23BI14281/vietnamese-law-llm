frontend/
├── requirements.txt
├── Dockerfile
└── src/
    ├── domain/               # [DATA] Định nghĩa dữ liệu (Models/Schemas)
    │   └── schemas.py
    │
    ├── infrastructure/       # [IO] Code thực hiện gọi API (Requests)
    │   ├── gateway_api.py
    │   └── indexing_api.py
    │
    ├── application/          # [LOGIC] Cầu nối, xử lý nghiệp vụ trước khi vẽ
    │   ├── chat_service.py
    │   └── upload_service.py
    │
    ├── presentation/         # [UI] Chỉ chứa code vẽ giao diện (Streamlit)
    │   ├── components/       # Các widget nhỏ dùng chung (Header, Footer...)
    │   ├── views/            # Các màn hình chính (Tabs)
    │   │   ├── chat_view.py
    │   │   └── upload_view.py
    │   └── layout.py         # Cấu hình trang (Page config)
    │
    └── main.py               # [ROOT] Nơi khởi tạo và nối các lớp
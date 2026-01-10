import streamlit as st
import os
import sys

# Fix path import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Infrastructure
from src.infrastructure.indexing_api import IndexingAPI
from src.infrastructure.gateway_api import GatewayAPI

# Import Application
from src.application.upload_service import UploadService
from src.application.chat_service import ChatService

# Import Presentation
from src.presentation.views.upload_view import render_upload_view
from src.presentation.views.chat_view import render_chat_view

# --- CONFIG ---
LLM_GATEWAY_URL = os.getenv("LLM_GATEWAY_URL", "http://localhost:8001")
INDEXING_SERVICE_URL = os.getenv("INDEXING_SERVICE_URL", "http://localhost:5001")

# --- SETUP PAGE ---
st.set_page_config(page_title="Vietnam Legal AI", layout="wide")
st.title(" Hệ thống Tư vấn Pháp luật Thông minh")

# --- DEPENDENCY INJECTION (Lắp ráp) ---
# 1. Tạo Clients
indexing_api = IndexingAPI(INDEXING_SERVICE_URL)
gateway_api = GatewayAPI(LLM_GATEWAY_URL)

# 2. Tạo Services (Nhét Client vào Service)
upload_service = UploadService(indexing_api)
chat_service = ChatService(gateway_api)

# --- RENDER UI ---
tab1, tab2 = st.tabs([" Nạp Kiến Thức", " Hỏi Đáp"])

with tab1:
    render_upload_view(upload_service)

with tab2:
    render_chat_view(chat_service)
import sys
import os

# Thêm thư mục gốc vào system path để nhận diện các package core/ và views/
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from core.cipher_engine import build_custom_key, load_massive_symbol_pool
from views.home import render_home
from views.workspace import render_workspace
from views.chat_rooms import render_chat_rooms
from views.challenges import render_challenges
from views.academy import render_academy
from views.about import render_about

# 1. Cấu hình giao diện trang chính
st.set_page_config(
    page_title="Ultimate Global Cipher Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Thanh cấu hình toàn cục ở Sidebar (Cố định quy luật nhóm)
SYMBOLS_POOL = load_massive_symbol_pool()

with st.sidebar:
    st.markdown("## 🛡️ Cipher Control Panel")
    st.caption("Configure group rules below. Changes apply instantly across all pages.")

    secret_seed = st.text_input("🔑 Group Secret Passphrase:", type="password", placeholder="e.g. Nexus2026")
    shift_step = st.number_input("🔢 Shift Offset (0-200):", min_value=0, max_value=200, value=0)
    
    pattern_list = st.multiselect(
        f"🎨 Symbol Vault ({len(SYMBOLS_POOL)}+ icons):",
        options=SYMBOLS_POOL,
        default=SYMBOLS_POOL[:3]
    )
    
    custom_pairs = st.text_input("🔀 Custom Pairs (Optional):", placeholder="e.g. a=@, e=3")
    reverse_rule = st.checkbox("🔄 Reverse Structure", value=False)

    st.divider()
    
    # 3. Thanh Menu Điều hướng Đa lớp (Multi-Level Navigation)
    st.markdown("### 🧭 Navigation Menu")
    main_menu = st.selectbox(
        "Select Module:",
        [
            "🏠 1. Home Dashboard",
            "🔐 2. Cipher Workspace",
            "💬 3. Secret Chat Rooms",
            "🕹️ 4. Crypto Challenges (CTF)",
            "📚 5. Security Academy",
            "🛠️ 6. Utilities & About"
        ]
    )

    sub_mode = None
    if "2. Cipher Workspace" in main_menu:
        sub_mode = st.radio(
            "Workspace Tools:",
            [
                "Text Cipher & Time-Lock",
                "English Camouflage Studio",
                "Image Steganography Lab"
            ]
        )

# Đóng gói cấu hình nhóm thành dictionary
group_config = {
    "secret_seed": secret_seed,
    "shift_step": shift_step,
    "pattern_list": pattern_list,
    "custom_pairs": custom_pairs,
    "reverse_rule": reverse_rule
}

# Tạo khóa nhóm nếu đã nhập mật khẩu
group_key = []
if secret_seed:
    group_key = build_custom_key(secret_seed, pattern_list, shift_step, custom_pairs)

# 4. Router điều hướng đến các trang trong thư mục views/ tương ứng
if "1. Home Dashboard" in main_menu:
    render_home(group_config)
elif "2. Cipher Workspace" in main_menu:
    render_workspace(group_config, group_key, sub_mode)
elif "3. Secret Chat Rooms" in main_menu:
    render_chat_rooms(group_config, group_key)
elif "4. Crypto Challenges" in main_menu:
    render_challenges()
elif "5. Security Academy" in main_menu:
    render_academy(group_config, group_key)
elif "6. Utilities & About" in main_menu:
    render_about(group_config)

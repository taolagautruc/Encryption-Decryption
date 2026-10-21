import streamlit as st
from core.cipher_engine import load_massive_symbol_pool, calculate_key_entropy, BASE_CHARS
from core.chat_storage import load_all_rooms
from datetime import datetime, timezone

st.set_page_config(
    page_title="Ultimate Global Cipher Suite",
    page_icon="🛡️",
    layout="wide"
)

st.subheader("🌐 Global Cryptography Suite — Executive Dashboard")
st.markdown(
    "Welcome to the **Multi-Layer Secret Communication Platform**. "
    "Designed for zero-trust group messaging, linguistic camouflage, and pixel-level steganography."
)

symbols_count = len(load_massive_symbol_pool())
rooms_count = len(load_all_rooms())
utc_now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Base Character Set", f"{len(BASE_CHARS)} chars", "Global + VN")
col2.metric("Unicode Symbol Vault", f"{symbols_count}+", "Dynamic Pool")
col3.metric("Active Secret Rooms", f"{rooms_count} rooms", "SHA-256 Protected")
col4.metric("Universal Clock", utc_now, "Timezone-Free")

st.divider()
st.info("💡 **Hệ thống đã hoạt động ổn định!** Bạn có thể chọn các trang chức năng khác ở thanh menu bên trái (Sidebar) của Streamlit.")

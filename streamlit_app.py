import sys
import os

# Đảm bảo nhận diện đúng đường dẫn core/
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from core.cipher_engine import build_custom_key, load_massive_symbol_pool, encrypt_core, decrypt_core
from core.camouflage import encode_english_camouflage, decode_english_camouflage
from core.steganography import encode_image_lsb, decode_image_lsb
from PIL import Image
import io
import time

st.set_page_config(
    page_title="Ultimate Global Cipher Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Thanh Sidebar cấu hình toàn cục
SYMBOLS_POOL = load_massive_symbol_pool()

with st.sidebar:
    st.markdown("## 🛡️ Cipher Control Panel")
    st.caption("Configure group rules below. Changes apply instantly.")

    secret_seed = st.text_input("🔑 Group Secret Passphrase:", type="password", placeholder="e.g. Nexus2026")
    shift_step = st.number_input("🔢 Shift Offset (0-200):", min_value=0, max_value=200, value=0)
    
    pattern_list = st.multiselect(
        f"🎨 Symbol Vault ({len(SYMBOLS_POOL)}+ icons):",
        options=SYMBOLS_POOL,
        default=SYMBOLS_POOL[:3] if len(SYMBOLS_POOL) >= 3 else []
    )
    
    custom_pairs = st.text_input("🔀 Custom Pairs (Optional):", placeholder="e.g. a=@, e=3")
    reverse_rule = st.checkbox("🔄 Reverse Structure", value=False)

    st.divider()
    main_menu = st.radio(
        "🧭 Navigation Menu:",
        [
            "🏠 Home Dashboard",
            "🔐 Cipher Workspace",
            "🎭 English Camouflage",
            "🖼️ Image Steganography"
        ]
    )

# Tạo khóa nhóm
group_key = []
if secret_seed:
    group_key = build_custom_key(secret_seed, pattern_list, shift_step, custom_pairs)

# 2. Nội dung hiển thị theo menu
if "Home Dashboard" in main_menu:
    st.subheader("🌐 Global Cryptography Suite — Control Center")
    st.markdown("Welcome! Use the **Sidebar on the left** to set your Group Passphrase and switch between tools.")
    if not secret_seed:
        st.warning("⚠️ Please enter a **Group Secret Passphrase** in the sidebar to begin encrypting/decrypting messages.")
    else:
        st.success("✅ Group cipher rules are active and ready!")

elif "Cipher Workspace" in main_menu:
    st.subheader("🔐 Multi-Layer Text Cipher & Time-Lock")
    if not secret_seed:
        st.warning("⚠️ Please enter a **Group Secret Passphrase** in the sidebar first!")
    else:
        tab_enc, tab_dec = st.tabs(["📤 Encrypt Message", "📥 Decrypt Message"])
        with tab_enc:
            msg_in = st.text_area("Enter secret message:")
            if st.button("🔒 Generate Ciphertext", type="primary"):
                if msg_in.strip():
                    res = encrypt_core(msg_in, group_key, reverse_rule, "NONE", 0)
                    st.success("Encrypted Output:")
                    st.code(res, language=None)
                else:
                    st.error("Please enter a message!")
        with tab_dec:
            cyph_in = st.text_area("Paste ciphertext to decode:")
            if st.button("🔓 Decode", type="primary"):
                if cyph_in.strip():
                    ok, res = decrypt_core(cyph_in.strip(), group_key, reverse_rule)
                    if ok:
                        st.success(f"Decoded: {res}")
                    else:
                        st.error(res)
                else:
                    st.error("Please paste ciphertext!")

elif "English Camouflage" in main_menu:
    st.subheader("🎭 Dynamic English Camouflage Studio")
    if not secret_seed:
        st.warning("⚠️ Please enter a **Group Secret Passphrase** in the sidebar first!")
    else:
        camo_text = st.text_input("Enter message to disguise into English prose:")
        if st.button("🎭 Convert to Camouflage", type="primary"):
            if camo_text.strip():
                cyph = encrypt_core(camo_text, group_key, reverse_rule, "NONE", 0)
                disguised = encode_english_camouflage(cyph)
                st.success("Disguised English Text:")
                st.code(disguised, language=None)
            else:
                st.error("Please enter a message!")

elif "Image Steganography" in main_menu:
    st.subheader("🖼️ LSB Image Steganography Lab")
    if not secret_seed:
        st.warning("⚠️ Please enter a **Group Secret Passphrase** in the sidebar first!")
    else:
        up_img = st.file_uploader("Upload Image (PNG):", type=["png", "jpg"])
        hidden_msg = st.text_input("Secret message to hide in pixels:")
        if st.button("🖼️ Embed & Download PNG", type="primary"):
            if up_img and hidden_msg:
                img_obj = Image.open(up_img)
                cyph = encrypt_core(hidden_msg, group_key, reverse_rule, "NONE", 0)
                stego_img = encode_image_lsb(img_obj, cyph)
                buf = io.BytesIO()
                stego_img.save(buf, format="PNG")
                st.download_button("⬇️ Download Stego PNG", data=buf.getvalue(), file_name="stego.png", mime="image/png")
            else:
                st.warning("Please upload an image and type a message!")

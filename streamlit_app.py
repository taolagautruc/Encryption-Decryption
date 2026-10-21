import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
from core.cipher_engine import build_custom_key, load_massive_symbol_pool, encrypt_core, decrypt_core, BASE_CHARS
from core.camouflage import encode_english_camouflage, decode_english_camouflage, inspect_camouflage_structure
from core.steganography import encode_image_lsb, decode_image_lsb, inspect_pixel_lsb
from core.chat_storage import load_all_rooms, create_room, get_room_messages, add_message_to_room
from PIL import Image, ImageDraw
import io
import time
from datetime import datetime, timezone

st.set_page_config(
    page_title="Ultimate Global Cipher Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. THANH ĐIỀU KHIỂN TOÀN CỤC (SIDEBAR) ---
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
            "🏠 1. Home Dashboard",
            "🔐 2. Cipher Workspace",
            "💬 3. Secret Chat Rooms",
            "🕹️ 4. Crypto Challenges (CTF)",
            "📚 5. Security Academy",
            "🛠️ 6. Utilities & About"
        ]
    )

# Xây dựng khóa nhóm
group_key = []
if secret_seed:
    group_key = build_custom_key(secret_seed, pattern_list, shift_step, custom_pairs)

group_config = {
    "secret_seed": secret_seed,
    "shift_step": shift_step,
    "pattern_list": pattern_list,
    "custom_pairs": custom_pairs,
    "reverse_rule": reverse_rule
}


# --- 2. ĐIỀU HƯỚNG CÁC TÍNH NĂNG ---

if "1. Home Dashboard" in main_menu:
    st.subheader("🌐 Global Cryptography Suite — Executive Dashboard")
    st.markdown("Welcome to the **Multi-Layer Secret Communication Platform**. Designed for zero-trust group messaging, linguistic camouflage, and pixel-level steganography.")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Base Character Set", f"{len(BASE_CHARS)} chars", "Global + VN")
    c2.metric("Unicode Symbol Vault", f"{len(SYMBOLS_POOL)}+", "Dynamic Pool")
    c3.metric("Active Secret Rooms", f"{len(load_all_rooms())} rooms", "SHA-256 Protected")
    c4.metric("Universal Clock", datetime.now(timezone.utc).strftime("%H:%M:%S UTC"), "Timezone-Free")
    
    st.divider()
    if not secret_seed:
        st.warning("⚠️ Please enter a **Group Secret Passphrase** in the sidebar to unlock all encryption and chat tools!")
    else:
        st.success("🎉 Group cipher rules are fully active and synchronized across all modules!")

elif "2. Cipher Workspace" in main_menu:
    st.subheader("🔐 Multi-Layer Text Cipher, Time-Lock & Steganography")
    if not secret_seed:
        st.warning("⚠️ Please enter a **Group Secret Passphrase** in the sidebar first!")
    else:
        tab_t, tab_c, tab_i = st.tabs(["📤 Text Cipher & Time-Lock", "🎭 English Camouflage", "🖼️ Image Steganography"])
        
        with tab_t:
            sub_t1, sub_t2 = st.tabs(["Encrypt", "Decrypt"])
            with sub_t1:
                p_in = st.text_area("Enter secret message:")
                t_mode = st.selectbox("Time Mode (UTC):", ["No Time Limit", "🔥 Self-Destruct", "⏳ Time-Capsule"])
                mins = st.number_input("Minutes:", 1, 10080, 20) if t_mode != "No Time Limit" else 20
                if st.button("🔒 Encrypt Text", type="primary"):
                    if p_in.strip():
                        mode = "EXPIRE" if "Self-Destruct" in t_mode else ("WAIT" if "Time-Capsule" in t_mode else "NONE")
                        ts = int(time.time()) + (mins * 60) if mode != "NONE" else 0
                        res = encrypt_core(p_in, group_key, reverse_rule, mode, ts)
                        st.success("Encrypted Ciphertext:")
                        st.code(res, language=None)
            with sub_t2:
                c_in = st.text_area("Paste ciphertext:")
                if st.button("🔓 Decode Text", type="primary"):
                    if c_in.strip():
                        ok, res = decrypt_core(c_in.strip(), group_key, reverse_rule)
                        if ok: st.success(res)
                        else: st.error(res)

        with tab_c:
            c_text = st.text_input("Enter text to disguise into English prose:")
            if st.button("🎭 Convert to Camouflage", type="primary"):
                if c_text.strip():
                    cyph = encrypt_core(c_text, group_key, reverse_rule, "NONE", 0)
                    st.code(encode_english_camouflage(cyph), language=None)

        with tab_i:
            img_mode = st.radio("Mode:", ["Hide", "Extract"], horizontal=True)
            if img_mode == "Hide":
                up = st.file_uploader("Upload Image (PNG):", type=["png", "jpg"])
                s_msg = st.text_input("Secret message to hide:")
                if st.button("🖼️ Embed into Pixels", type="primary") and up and s_msg:
                    img = Image.open(up)
                    cyph = encrypt_core(s_msg, group_key, reverse_rule, "NONE", 0)
                    stego = encode_image_lsb(img, cyph)
                    buf = io.BytesIO()
                    stego.save(buf, format="PNG")
                    st.download_button("⬇️ Download Stego PNG", buf.getvalue(), "stego.png", "image/png")
            else:
                stego_up = st.file_uploader("Upload Stego PNG:", type=["png"])
                if st.button("🔍 Extract from Pixels", type="primary") and stego_up:
                    img = Image.open(stego_up)
                    extracted = decode_image_lsb(img)
                    ok, res = decrypt_core(extracted, group_key, reverse_rule)
                    if ok: st.success(res)
                    else: st.error(res)

elif "3. Secret Chat Rooms" in main_menu:
    st.subheader("💬 Encrypted Persistent Chat Rooms")
    if not secret_seed:
        st.warning("⚠️ Please enter a **Group Secret Passphrase** in the sidebar first!")
    else:
        rooms = load_all_rooms()
        r_choice = st.selectbox("Select or Create Room:", ["-- Create New Room --"] + list(rooms.keys()))
        if r_choice == "-- Create New Room --":
            new_r = st.text_input("New Room Name:")
            if st.button("Create Room") and new_r.strip():
                create_room(new_r.strip(), secret_seed)
                st.success(f"Room '{new_r}' created!")
                st.rerun()
        else:
            st.markdown(f"### Active Room: `{r_choice}`")
            msgs = get_room_messages(r_choice)
            for m in msgs:
                st.markdown(f"**{m['sender']}** ({m['timestamp']}): `{m['ciphertext']}`")
            
            chat_msg = st.text_input("Type encrypted message:")
            if st.button("Send Message", type="primary") and chat_msg.strip():
                cyph = encrypt_core(chat_msg.strip(), group_key, reverse_rule, "NONE", 0)
                add_message_to_room(r_choice, "Agent", cyph)
                st.rerun()

elif "4. Crypto Challenges (CTF)" in main_menu:
    st.subheader("🕹️ Crypto Challenges & CTF Arena")
    st.write("Test your cryptanalysis skills across missions. Decode the flags using the rules specified in each level!")
    st.info("💡 Go to **Cipher Workspace** to decode incoming CTF intercepts.")
    st.markdown("- **Level 1:** Passphrase `ALPHA`, Shift `5`, No Symbols.\n- **Level 2:** Passphrase `SHADOW`, Camouflage Mode.\n- **Level 3:** Passphrase `PIXEL`, Shift `10`, LSB Steganography.")

elif "5. Security Academy" in main_menu:
    st.subheader("📚 Security Academy & Algorithm X-Ray")
    st.write("Understand how bits, pixels, and linguistic matrices protect your secret data.")
    sample = st.text_input("Test string for X-ray:", value="Hi")
    if sample:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Original Pixel LSB Sample:**")
            st.table(inspect_pixel_lsb(Image.new("RGB", (30,30), color=(100,150,200)), 3))
        with c2:
            st.markdown("**Camouflage Breakdown:**")
            cyph = encrypt_core(sample, group_key, reverse_rule, "NONE", 0) if group_key else sample
            st.table(inspect_camouflage_structure(encode_english_camouflage(cyph)))

elif "6. Utilities & About" in main_menu:
    st.subheader("🛠️ Utilities & Developer Profile")
    st.markdown(
        """
        - **Project:** Ultimate Secret Messenger & Multi-Layer Cryptography Suite.
        - **Tech Stack:** Python, Streamlit, Pillow (PIL), Custom Substitution & LSB Steganography.
        - **Author:** Student at Faculty of Information Technology, University of Science, VNU-HCM (HCMUS).
        """
    )
    st.info("💡 *“Security is not a product, but a process.”* — Bruce Schneier")

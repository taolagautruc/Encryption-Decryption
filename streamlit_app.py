import streamlit as st
import random
import string
import time
import json
import os
from PIL import Image, ImageDraw
import io
from datetime import datetime, timezone

st.set_page_config(
    page_title="Ultimate Global Cipher Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. CORE CIPHER & STORAGE LOGIC ---
VIETNAMESE_CHARS = (
    "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổổơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"
)
BASE_CHARS = list(" " + string.punctuation + string.digits + string.ascii_letters + VIETNAMESE_CHARS)

@st.cache_data
def load_massive_symbol_pool() -> list:
    pool = []
    for code_range in [(0x1F300, 0x1F5FF), (0x1F600, 0x1F64F), (0x1F680, 0x1F6FF), (0x1F900, 0x1F9FF), (0x2600, 0x26FF)]:
        for code in range(code_range[0], code_range[1] + 1):
            try:
                pool.append(chr(code))
            except ValueError:
                continue
    return pool

def build_custom_key(secret_seed: str, pattern_list: list, shift_step: int, custom_pairs: str) -> list:
    key = BASE_CHARS.copy()
    rng = random.Random(f"{secret_seed}_{''.join(pattern_list)}")
    rng.shuffle(key)
    if shift_step > 0:
        shift = shift_step % len(key)
        key = key[shift:] + key[:shift]
    if custom_pairs.strip():
        for pair in custom_pairs.split(","):
            if "=" in pair:
                a, b = pair.split("=", 1)
                if a.strip() in BASE_CHARS and b.strip() in key:
                    ia, ib = BASE_CHARS.index(a.strip()), key.index(b.strip())
                    key[ia], key[ib] = key[ib], key[ia]
    return key

def encrypt_core(plain_text: str, key: list, reverse_rule: bool, mode: str = "NONE", target_ts: int = 0) -> str:
    payload = f"TMODE:{mode}:{target_ts}|{plain_text}"
    res = "".join(key[BASE_CHARS.index(c)] if c in BASE_CHARS else c for c in payload)
    return res[::-1] if reverse_rule else res

def decrypt_core(cypher_text: str, key: list, reverse_rule: bool) -> tuple[bool, str]:
    txt = cypher_text[::-1] if reverse_rule else cypher_text
    raw = "".join(BASE_CHARS[key.index(c)] if c in key else c for c in txt)
    if not raw.startswith("TMODE:") or "|" not in raw:
        return False, "❌ Decryption Failed: Incorrect Group Passphrase or Rules!"
    header, actual_msg = raw.split("|", 1)
    parts = header.split(":")
    if len(parts) != 3:
        return False, "❌ Corrupted timestamp header!"
    mode, target_ts = parts[1], int(parts[2])
    now_ts = int(time.time())
    if mode == "EXPIRE" and target_ts > 0 and now_ts > target_ts:
        return False, "💥 MESSAGE EXPIRED AND SELF-DESTRUCTED!"
    if mode == "WAIT" and target_ts > 0 and now_ts < target_ts:
        return False, "⏳ TIME-CAPSULE LOCKED! Please wait until target time."
    return True, actual_msg

# Xử lý lưu trữ chat an toàn
DB_FILE = "chat_rooms_db.json"
def load_all_rooms():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_all_rooms(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_msg(room_name, sender, ciphertext):
    rooms = load_all_rooms()
    if room_name not in rooms:
        rooms[room_name] = {"messages": []}
    rooms[room_name]["messages"].append({
        "sender": sender,
        "ciphertext": ciphertext,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    })
    save_all_rooms(rooms)


# --- 2. GIAO DIỆN ĐIỀU KHIỂN & THANH BÊN ---
SYMBOLS_POOL = load_massive_symbol_pool()

with st.sidebar:
    st.markdown("## 🛡️ Cipher Control Panel")
    secret_seed = st.text_input("🔑 Group Secret Passphrase:", type="password", placeholder="e.g. Nexus2026")
    shift_step = st.number_input("🔢 Shift Offset (0-200):", min_value=0, max_value=200, value=0)
    pattern_list = st.multiselect(f"🎨 Symbol Vault:", options=SYMBOLS_POOL, default=SYMBOLS_POOL[:3] if SYMBOLS_POOL else [])
    custom_pairs = st.text_input("🔀 Custom Pairs (Optional):", placeholder="e.g. a=@, e=3")
    reverse_rule = st.checkbox("🔄 Reverse Structure", value=False)
    
    st.divider()
    main_menu = st.radio(
        "🧭 Navigation Menu:",
        [
            "🏠 1. Home Dashboard",
            "🔐 2. Cipher Workspace",
            "💬 3. Secret Chat Rooms",
            "🕹️ 4. Crypto Challenges",
            "📚 5. Security Academy",
            "🛠️ 6. Utilities & About"
        ]
    )

group_key = build_custom_key(secret_seed, pattern_list, shift_step, custom_pairs) if secret_seed else []


# --- 3. ĐIỀU HƯỚNG HIỂN THỊ CÁC TRANG ---
if "1. Home Dashboard" in main_menu:
    st.subheader("🌐 Global Cryptography Suite — Executive Dashboard")
    st.markdown("Welcome! Use the sidebar to set your **Group Passphrase** and explore encrypted chat rooms and tools.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Base Chars", f"{len(BASE_CHARS)}", "Global + VN")
    c2.metric("Symbol Vault", f"{len(SYMBOLS_POOL)}+", "Icons")
    c3.metric("Chat Rooms", f"{len(load_all_rooms())}", "Persistent DB")
    c4.metric("Universal Clock", datetime.now(timezone.utc).strftime("%H:%M:%S UTC"), "UTC")

elif "2. Cipher Workspace" in main_menu:
    st.subheader("🔐 Multi-Layer Text Cipher & Time-Lock")
    if not secret_seed:
        st.warning("⚠️ Please enter a **Group Secret Passphrase** in the sidebar first!")
    else:
        tab1, tab2 = st.tabs(["📤 Encrypt", "📥 Decrypt"])
        with tab1:
            msg = st.text_area("Secret message:")
            mode_opt = st.selectbox("Mode:", ["Normal", "Self-Destruct", "Time-Capsule"])
            mins = st.number_input("Minutes:", 1, 1440, 10) if mode_opt != "Normal" else 0
            if st.button("🔒 Encrypt", type="primary") and msg.strip():
                mode = "EXPIRE" if mode_opt == "Self-Destruct" else ("WAIT" if mode_opt == "Time-Capsule" else "NONE")
                ts = int(time.time()) + (mins * 60) if mode != "NONE" else 0
                res = encrypt_core(msg, group_key, reverse_rule, mode, ts)
                st.success("Ciphertext:")
                st.code(res)
        with tab2:
            cyph = st.text_area("Ciphertext:")
            if st.button("🔓 Decrypt", type="primary") and cyph.strip():
                ok, res = decrypt_core(cyph.strip(), group_key, reverse_rule)
                if ok: st.success(res)
                else: st.error(res)

elif "3. Secret Chat Rooms" in main_menu:
    st.subheader("💬 Encrypted Persistent Chat Rooms")
    if not secret_seed:
        st.warning("⚠️ Please enter a **Group Secret Passphrase** in the sidebar first!")
    else:
        rooms = load_all_rooms()
        r_name = st.selectbox("Select Room:", ["-- Create New Room --"] + list(rooms.keys()))
        if r_name == "-- Create New Room --":
            new_r = st.text_input("New Room Name:")
            if st.button("Create") and new_r.strip():
                save_all_rooms({**rooms, new_r.strip(): {"messages": []}})
                st.success(f"Room '{new_r}' created!")
                st.rerun()
        else:
            st.markdown(f"### Room: `{r_name}`")
            msgs = rooms.get(r_name, {}).get("messages", [])
            for m in msgs:
                st.markdown(f"**{m['sender']}** ({m['timestamp']}): `{m['ciphertext']}`")
            chat_in = st.text_input("Message:")
            if st.button("Send", type="primary") and chat_in.strip():
                c_out = encrypt_core(chat_in.strip(), group_key, reverse_rule, "NONE", 0)
                add_msg(r_name, "Agent", c_out)
                st.rerun()

elif "4. Crypto Challenges" in main_menu:
    st.subheader("🕹️ Crypto Challenges & CTF Arena")
    st.write("Test your cryptanalysis skills! Use the **Cipher Workspace** to decode messages based on group rules.")
    st.info("💡 Level 1: Passphrase `ALPHA`, Shift `5`. Level 2: Passphrase `SHADOW`.")

elif "5. Security Academy" in main_menu:
    st.subheader("📚 Security Academy & Algorithm X-Ray")
    st.write("Understand how substitution tables, shifting, and UTC time locks protect messages.")

elif "6. Utilities & About" in main_menu:
    st.subheader("🛠️ Utilities & Developer Profile")
    st.markdown("- **Project:** Ultimate Secret Messenger & Multi-Layer Cryptography Suite.\n- **Author:** Student at HCMUS.")
    st.info("💡 *“Security is not a product, but a process.”* — Bruce Schneier")

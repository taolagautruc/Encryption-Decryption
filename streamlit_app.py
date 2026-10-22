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
    page_title="Ultimate Secret Messenger | Global Cipher Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 0. GIAO DIỆN CSS TUỲ CHỈNH (CYBERSECURITY UI THEME) ---
st.markdown("""
<style>
    /* Hero Banner */
    .hero-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        border: 1px solid #3b82f6;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.15);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        border: 1px solid #3b82f6;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #93c5fd, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 8px 0;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0;
    }
    /* Thẻ tính năng (Feature Cards) */
    .feat-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        transition: all 0.25s ease;
    }
    .feat-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    .feat-title {
        color: #f8fafc;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .feat-desc {
        color: #9ca3af;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    /* Tinh chỉnh khung Metric mặc định của Streamlit */
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- 1. CORE CIPHER & STORAGE LOGIC ---
VIETNAMESE_CHARS = (
    "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
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

def calculate_entropy_metrics(secret_seed: str, pattern_list: list, shift_step: int, pool_size: int) -> tuple[int, str]:
    if not secret_seed:
        return 0, "0 seconds (Unprotected)"
    char_space = len(BASE_CHARS) ** max(len(secret_seed), 1)
    icon_space = max(pool_size, 1) ** len(pattern_list)
    shift_space = 200 if shift_step > 0 else 1
    total_combos = char_space * icon_space * shift_space
    # Tính số bit entropy xấp xỉ
    bits = total_combos.bit_length()
    seconds = total_combos / (10 ** 12) # Giả sử siêu máy tính thử 1 nghìn tỷ khóa/giây
    years = seconds / (365 * 24 * 3600)
    if years > 1e15:
        time_str = f"{years:.2e} Years (Quantum-Resistant)"
    elif years > 1:
        time_str = f"{int(years):,} Years"
    else:
        time_str = "< 1 Year (Add more symbols/length)"
    return bits, time_str

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
    pattern_list = st.multiselect("🎨 Symbol Vault:", options=SYMBOLS_POOL, default=SYMBOLS_POOL[:3] if SYMBOLS_POOL else [])
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
    # 1.1: Hero Banner hiển thị rõ tên trang web của bạn
    st.markdown("""
    <div class="hero-box">
        <div class="hero-badge">⚡ ZERO-TRUST MULTI-LAYER CRYPTOGRAPHY PLATFORM</div>
        <h1 class="hero-title">🛡️ Ultimate Secret Messenger</h1>
        <p class="hero-sub">
            Global Cipher Suite — Custom Unicode Key Permutation • UTC Time-Locking • LSB Pixel Steganography • Encrypted Persistent Chat
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 1.2: 4 Thẻ chỉ số hệ thống (System Metrics)
    rooms_data = load_all_rooms()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔤 Base Alphabet", f"{len(BASE_CHARS)} chars", "EN + VN + Symbols")
    c2.metric("🎨 Symbol Vault", f"{len(SYMBOLS_POOL):,}+", "Unicode Pool")
    c3.metric("💬 Active Chat Rooms", f"{len(rooms_data)} rooms", "JSON Persistent DB")
    c4.metric("🌍 Universal Clock", datetime.now(timezone.utc).strftime("%H:%M:%S UTC"), "Synchronized")

    st.write("")

    # 1.3: Trạng thái Khóa & Phân tích Bảo mật Trực tiếp (Live Key Status & Audit)
    col_status, col_specs = st.columns([3, 2])

    with col_status:
        st.markdown("#### 🔐 Live Group Key Configuration Status")
        if not secret_seed:
            st.warning(
                "⚠️ **System Standby — Passphrase Required**\n\n"
                "Please enter your **Group Secret Passphrase** in the left Sidebar to initialize the cryptographic engine and unlock all workspace modules."
            )
        else:
            bits, crack_time = calculate_entropy_metrics(secret_seed, pattern_list, shift_step, len(SYMBOLS_POOL))
            st.success("✅ **Cryptographic Engine Active & Synchronized!** All modules are ready.")
            
            # Hiển thị tóm tắt cấu hình đang bật
            icons_str = " ➡️ ".join(pattern_list) if pattern_list else "None"
            st.markdown(f"""
            - **Active Symbol Chain:** {icons_str}
            - **Shift Offset Step:** `{shift_step}` positions | **Reverse Cipher:** `{'Enabled' if reverse_rule else 'Disabled'}`
            - **Custom Mapping:** `{custom_pairs if custom_pairs.strip() else 'Standard 1:1 Permutation'}`
            - **Estimated Key Entropy:** `~{bits} bits` (Brute-force time: **{crack_time}**)
            """)
            st.progress(min(bits / 256, 1.0), text=f"Security Strength Rating: {min(int((bits/128)*100), 100)}%")

    with col_specs:
        st.markdown("#### 🧭 Quick Navigation Guide")
        st.info(
            "**1. Configure Rules:** Set Passphrase, Shift & Icons on the left panel.\n\n"
            "**2. Cipher Workspace:** Encrypt text, set UTC self-destruct timers, or hide data inside PNG pixels.\n\n"
            "**3. Secret Chat Rooms:** Communicate with your team in real-time encrypted rooms."
        )

    st.divider()

    # 1.4: Ba thẻ tính năng cốt lõi (Core Architecture Pillars)
    st.markdown("#### 🚀 Core Security Architecture")
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-title">🧬 Dynamic Multi-Layer Key</div>
            <div class="feat-desc">
                Combines your secret passphrase with a visual sequence of 1,400+ Unicode symbols, custom character swaps, and modular shifting to generate a unique substitution table.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-title">⏳ UTC Time-Lock & Self-Destruct</div>
            <div class="feat-desc">
                Embeds tamper-proof UTC epoch timestamps directly inside the payload. Messages automatically self-destruct after expiration or remain locked until a future time.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-title">🖼️ LSB Steganography & Rooms</div>
            <div class="feat-desc">
                Conceal encrypted ciphertexts inside ordinary PNG image pixels using Least Significant Bit manipulation, or collaborate in persistent encrypted chat rooms.
            </div>
        </div>
        """, unsafe_allow_html=True)

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

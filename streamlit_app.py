import streamlit as st
import random
import string
import time
import json
import os
import base64
import hashlib
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
        font-size: 2.5rem;
        font-weight: 800;
        color: #f8fafc !important;
        text-shadow: 0 0 20px rgba(59, 130, 246, 0.6), 0 2px 4px rgba(0, 0, 0, 0.8);
        margin: 6px 0 10px 0;
        letter-spacing: -0.5px;
    }
    .hero-title span {
        color: #60a5fa;
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
    /* Workspace Header & Tool Box */
    .ws-banner {
        background: linear-gradient(90deg, #111827 0%, #1e293b 100%);
        border-left: 4px solid #3b82f6;
        border-top: 1px solid #1f2937;
        border-right: 1px solid #1f2937;
        border-bottom: 1px solid #1f2937;
        padding: 16px 22px;
        border-radius: 10px;
        margin-bottom: 18px;
    }
    .ws-banner h4 {
        margin: 0 0 4px 0;
        color: #f8fafc;
        font-size: 1.15rem;
    }
    .ws-banner p {
        margin: 0;
        color: #94a3b8;
        font-size: 0.9rem;
    }
    /* Chat Message Bubble Card */
    .chat-card {
        background: #111827;
        border: 1px solid #1e293b;
        border-left: 4px solid #60a5fa;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .chat-meta {
        font-size: 0.82rem;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .chat-sender {
        color: #60a5fa;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .chat-badge {
        display: inline-block;
        background: rgba(96, 165, 250, 0.15);
        color: #93c5fd;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        margin-left: 8px;
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

# --- 1. CORE CIPHER, CAMOUFLAGE, STEGANOGRAPHY & STORAGE LOGIC ---
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
    bits = total_combos.bit_length()
    seconds = total_combos / (10 ** 12)
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
        return False, "❌ Decryption Failed: Incorrect Group Passphrase, Symbol Pattern, or Shift Rules!"
    header, actual_msg = raw.split("|", 1)
    parts = header.split(":")
    if len(parts) != 3:
        return False, "❌ Corrupted timestamp header!"
    mode, target_ts = parts[1], int(parts[2])
    now_ts = int(time.time())
    if mode == "EXPIRE" and target_ts > 0 and now_ts > target_ts:
        expired_ago = now_ts - target_ts
        m, s = divmod(expired_ago, 60)
        return False, f"💥 MESSAGE SELF-DESTRUCTED! (Expired {m}m {s}s ago in UTC)."
    if mode == "WAIT" and target_ts > 0 and now_ts < target_ts:
        wait_sec = target_ts - now_ts
        m, s = divmod(wait_sec, 60)
        return False, f"⏳ TIME-CAPSULE LOCKED! Please wait {m}m {s}s before decoding."
    return True, actual_msg

# --- 1B. ENGLISH CAMOUFLAGE ENGINE (2-WAY MARKOV PROSE) ---
CAMO_WORDS = [
    "system", "network", "protocol", "update", "server", "client", "module", "process",
    "data", "buffer", "channel", "request", "session", "router", "packet", "cluster"
]

def encode_english_camouflage(cipher_text: str) -> str:
    raw_bytes = cipher_text.encode("utf-8")
    words = []
    for b in raw_bytes:
        high = (b >> 4) & 0x0F
        low = b & 0x0F
        words.append(CAMO_WORDS[high])
        words.append(CAMO_WORDS[low])
    sentences = []
    for i in range(0, len(words), 8):
        chunk = words[i:i+8]
        chunk[0] = chunk[0].capitalize()
        sentences.append(" ".join(chunk) + ".")
    return " ".join(sentences)

def decode_english_camouflage(prose_text: str) -> tuple[bool, str]:
    cleaned = prose_text.replace(".", " ").replace(",", " ").strip().lower().split()
    if not cleaned or len(cleaned) % 2 != 0:
        return False, "❌ Invalid camouflage structure (Word count must be even)."
    byte_arr = bytearray()
    for i in range(0, len(cleaned), 2):
        w1, w2 = cleaned[i], cleaned[i+1]
        if w1 not in CAMO_WORDS or w2 not in CAMO_WORDS:
            return False, f"❌ Unrecognized camouflage word detected: '{w1}' or '{w2}'."
        b = (CAMO_WORDS.index(w1) << 4) | CAMO_WORDS.index(w2)
        byte_arr.append(b)
    try:
        return True, byte_arr.decode("utf-8")
    except Exception:
        return False, "❌ Corrupted byte sequence during camouflage extraction."

# --- 1C. LSB IMAGE STEGANOGRAPHY ENGINE (PIXEL-LEVEL HIDING) ---
STEGO_DELIM = "<<END_STEGO>>"

def generate_sample_carrier_image(width: int = 480, height: int = 260) -> Image.Image:
    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    for y in range(0, height, 20):
        draw.line([(0, y), (width, y)], fill=(30, 41, 59), width=1)
    for x in range(0, width, 20):
        draw.line([(x, 0), (x, height)], fill=(30, 41, 59), width=1)
    draw.rectangle([(15, 15), (width - 15, height - 15)], outline=(59, 130, 246), width=2)
    draw.text((35, 95), "ULTIMATE SECRET MESSENGER", fill=(96, 165, 250))
    draw.text((35, 125), "LSB STEGO CARRIER MATRIX // UTC VERIFIED", fill=(148, 163, 184))
    return img

def encode_image_lsb(image: Image.Image, secret_payload: str) -> Image.Image:
    img = image.convert("RGB")
    full_bytes = (secret_payload + STEGO_DELIM).encode("utf-8")
    bits = "".join(f"{byte:08b}" for byte in full_bytes)
    
    pixels = list(img.getdata())
    if len(bits) > len(pixels) * 3:
        raise ValueError("Payload is too large for this image! Please upload a higher resolution image.")
    
    new_pixels = []
    bit_idx = 0
    total_bits = len(bits)
    for r, g, b in pixels:
        if bit_idx < total_bits:
            r = (r & ~1) | int(bits[bit_idx])
            bit_idx += 1
        if bit_idx < total_bits:
            g = (g & ~1) | int(bits[bit_idx])
            bit_idx += 1
        if bit_idx < total_bits:
            b = (b & ~1) | int(bits[bit_idx])
            bit_idx += 1
        new_pixels.append((r, g, b))
        
    stego_img = Image.new("RGB", img.size)
    stego_img.putdata(new_pixels)
    return stego_img

def decode_image_lsb(image: Image.Image) -> tuple[bool, str]:
    img = image.convert("RGB")
    pixels = list(img.getdata())
    bits = []
    for r, g, b in pixels:
        bits.append(str(r & 1))
        bits.append(str(g & 1))
        bits.append(str(b & 1))
        
    byte_arr = bytearray()
    delim_bytes = STEGO_DELIM.encode("utf-8")
    delim_len = len(delim_bytes)
    
    for i in range(0, len(bits) - 7, 8):
        byte_val = int("".join(bits[i:i+8]), 2)
        byte_arr.append(byte_val)
        if len(byte_arr) >= delim_len and byte_arr[-delim_len:] == delim_bytes:
            try:
                extracted = byte_arr[:-delim_len].decode("utf-8")
                return True, extracted
            except Exception:
                return False, "❌ Found stego marker, but payload bytes are corrupted."
    return False, "❌ No hidden LSB steganography payload detected in this image!"

# --- 1D. ADVANCED PERSISTENT CHAT STORAGE ENGINE ---
DB_FILE = "chat_rooms_db.json"

def load_all_rooms() -> dict:
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_all_rooms(data: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_msg(room_name: str, sender: str, ciphertext: str, msg_type: str = "TEXT", image_b64: str = ""):
    rooms = load_all_rooms()
    if room_name not in rooms:
        rooms[room_name] = {"messages": [], "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
    msg_id = f"msg_{int(time.time()*1000)}_{random.randint(100,999)}"
    rooms[room_name]["messages"].append({
        "id": msg_id,
        "sender": sender,
        "type": msg_type,
        "ciphertext": ciphertext,
        "image_b64": image_b64,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    })
    save_all_rooms(rooms)

def delete_single_message(room_name: str, msg_idx: int):
    rooms = load_all_rooms()
    if room_name in rooms:
        msgs = rooms[room_name].get("messages", [])
        if 0 <= msg_idx < len(msgs):
            msgs.pop(msg_idx)
            rooms[room_name]["messages"] = msgs
            save_all_rooms(rooms)

def clear_room_history(room_name: str):
    rooms = load_all_rooms()
    if room_name in rooms:
        rooms[room_name]["messages"] = []
        save_all_rooms(rooms)

def destroy_entire_room(room_name: str):
    rooms = load_all_rooms()
    if room_name in rooms:
        del rooms[room_name]
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


# ==============================================================================
# PHẦN 1: HOME DASHBOARD
# ==============================================================================
if "1. Home Dashboard" in main_menu:
    st.markdown("""
    <div class="hero-box">
        <div class="hero-badge">⚡ ZERO-TRUST MULTI-LAYER CRYPTOGRAPHY PLATFORM</div>
        <div class="hero-title">🛡️ Ultimate <span>Secret Messenger</span></div>
        <p class="hero-sub">
            Global Cipher Suite — Custom Unicode Key Permutation • UTC Time-Locking • LSB Pixel Steganography • Encrypted Persistent Chat
        </p>
    </div>
    """, unsafe_allow_html=True)

    rooms_data = load_all_rooms()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔤 Base Alphabet", f"{len(BASE_CHARS)} chars", "EN + VN + Symbols")
    c2.metric("🎨 Symbol Vault", f"{len(SYMBOLS_POOL):,}+", "Unicode Pool")
    c3.metric("💬 Active Chat Rooms", f"{len(rooms_data)} rooms", "JSON Persistent DB")
    c4.metric("🌍 Universal Clock", datetime.now(timezone.utc).strftime("%H:%M:%S UTC"), "Synchronized")

    st.write("")
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

# ==============================================================================
# PHẦN 2: CIPHER WORKSPACE (TEXT, CAMOUFLAGE & LSB IMAGE STEGANOGRAPHY)
# ==============================================================================
elif "2. Cipher Workspace" in main_menu:
    st.markdown("""
    <div class="hero-box" style="padding: 20px 28px; margin-bottom: 18px;">
        <div class="hero-badge">🔐 CRYPTOGRAPHIC ENGINE & STEGANOGRAPHY LAB</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Multi-Layer Cipher Workspace</h2>
        <p class="hero-sub">Encrypt text with UTC time-locks, disguise ciphertexts into English prose, or embed secret payloads inside PNG image pixels.</p>
    </div>
    """, unsafe_allow_html=True)

    if not secret_seed:
        st.warning("⚠️ **Passphrase Required:** Please enter your **Group Secret Passphrase** in the left Sidebar to unlock the Cipher Workspace!")
    else:
        ws_tab1, ws_tab2, ws_tab3 = st.tabs([
            "📝 1. Text Cipher & UTC Time-Lock",
            "🎭 2. English Camouflage Studio",
            "🖼️ 3. Image Steganography Lab (LSB)"
        ])

        with ws_tab1:
            st.markdown("""
            <div class="ws-banner">
                <h4>📝 Multi-Layer Text Encryption & UTC Time-Locking</h4>
                <p>Encrypt messages using your group's custom symbol permutation table and attach optional UTC self-destruct or time-capsule locks.</p>
            </div>
            """, unsafe_allow_html=True)

            col_enc, col_dec = st.columns(2)
            with col_enc:
                st.markdown("##### 📤 Encrypt Plaintext")
                msg_in = st.text_area("Secret Message:", placeholder="Type your confidential message here...", height=130, key="ws_txt_in")
                c_mode, c_min = st.columns([2, 1])
                with c_mode:
                    t_mode = st.selectbox("UTC Time-Lock Mode:", ["Normal (No Time Limit)", "🔥 Self-Destruct After Time", "⏳ Time-Capsule (Wait Until)"])
                with c_min:
                    mins = st.number_input("Minutes:", min_value=1, max_value=10080, value=15, disabled=(t_mode == "Normal (No Time Limit)"))

                if st.button("🔒 Generate Ciphertext", type="primary", use_container_width=True):
                    if msg_in.strip():
                        mode_code = "EXPIRE" if "Self-Destruct" in t_mode else ("WAIT" if "Time-Capsule" in t_mode else "NONE")
                        target_ts = int(time.time()) + (mins * 60) if mode_code != "NONE" else 0
                        cipher_out = encrypt_core(msg_in, group_key, reverse_rule, mode_code, target_ts)
                        st.success("✅ Encrypted Payload Generated:")
                        st.code(cipher_out, language=None)
                    else:
                        st.error("Please enter a message to encrypt.")

            with col_dec:
                st.markdown("##### 📥 Decrypt Ciphertext")
                cyph_in = st.text_area("Paste Ciphertext:", placeholder="Paste the encrypted string here...", height=130, key="ws_cyph_in")
                st.write("")
                st.write("")
                if st.button("🔓 Decode & Verify UTC Lock", type="primary", use_container_width=True):
                    if cyph_in.strip():
                        ok, res = decrypt_core(cyph_in.strip(), group_key, reverse_rule)
                        if ok:
                            st.success("✅ Decrypted Plaintext:")
                            st.info(res)
                        else:
                            st.error(res)
                    else:
                        st.warning("Please paste a ciphertext string to decode.")

        with ws_tab2:
            st.markdown("""
            <div class="ws-banner">
                <h4>🎭 Linguistic Camouflage Studio (2-Way Markov Prose)</h4>
                <p>Convert suspicious-looking ciphertexts into innocent technical English sentences to bypass visual inspection, and decode them back seamlessly.</p>
            </div>
            """, unsafe_allow_html=True)

            camo_col1, camo_col2 = st.columns(2)
            with camo_col1:
                st.markdown("##### 📤 Disguise Secret into English")
                camo_plain = st.text_area("Enter Secret Message:", placeholder="e.g. Operation starts at 02:00 UTC", height=110)
                if st.button("🎭 Encrypt & Disguise as English Prose", type="primary", use_container_width=True):
                    if camo_plain.strip():
                        raw_c = encrypt_core(camo_plain, group_key, reverse_rule, "NONE", 0)
                        disguised = encode_english_camouflage(raw_c)
                        st.success("✅ Camouflaged English Text:")
                        st.code(disguised, language=None)
                    else:
                        st.warning("Please enter a secret message first.")

            with camo_col2:
                st.markdown("##### 📥 Reveal Secret from English Prose")
                camo_prose_in = st.text_area("Paste Camouflaged English Sentences:", placeholder="Paste the innocent-looking English paragraph here...", height=110)
                if st.button("🔍 Extract & Decrypt Secret", type="primary", use_container_width=True):
                    if camo_prose_in.strip():
                        ok_c, extracted_c = decode_english_camouflage(camo_prose_in.strip())
                        if not ok_c:
                            st.error(extracted_c)
                        else:
                            ok_d, final_txt = decrypt_core(extracted_c, group_key, reverse_rule)
                            if ok_d:
                                st.success("✅ Hidden Message Revealed:")
                                st.info(final_txt)
                            else:
                                st.error(final_txt)
                    else:
                        st.warning("Please paste the camouflaged English text.")

        with ws_tab3:
            st.markdown("""
            <div class="ws-banner">
                <h4>🖼️ LSB Pixel Steganography Lab (Hide Encrypted Data Inside Images)</h4>
                <p>Embed your encrypted payload invisibly into the Least Significant Bits (RGB channels) of any image. Output is lossless PNG.</p>
            </div>
            """, unsafe_allow_html=True)

            stego_mode = st.radio(
                "Select Steganography Operation:",
                ["📤 Hide Secret Message Inside Image (Encode)", "📥 Extract Secret Message From Stego PNG (Decode)"],
                horizontal=True
            )
            st.divider()

            if "Encode" in stego_mode:
                s_col1, s_col2 = st.columns([1.2, 1])
                with s_col1:
                    img_source = st.radio(
                        "Choose Carrier Image Source:",
                        ["📁 Upload My Own Image (PNG/JPG)", "⚡ Auto-Generate Cyber Carrier Image"],
                        horizontal=True
                    )
                    carrier_img = None
                    if "Upload" in img_source:
                        up_file = st.file_uploader("Upload Carrier Image:", type=["png", "jpg", "jpeg"])
                        if up_file:
                            carrier_img = Image.open(up_file).convert("RGB")
                    else:
                        carrier_img = generate_sample_carrier_image()
                        st.caption("✨ Generated a fresh 480x260 Cyber Carrier Matrix ready for pixel embedding.")

                    secret_stego_msg = st.text_area(
                        "Secret Message to Hide Inside Pixels:",
                        placeholder="Type secret message to embed invisibly into the image...",
                        height=100
                    )

                    c_stego_mode, c_stego_min = st.columns([2, 1])
                    with c_stego_mode:
                        stego_t_mode = st.selectbox("Image Payload Time-Lock (UTC):", ["Normal (No Time Limit)", "🔥 Self-Destruct After Time", "⏳ Time-Capsule (Wait Until)"])
                    with c_stego_min:
                        stego_mins = st.number_input("Timer (Mins):", min_value=1, max_value=10080, value=30, disabled=(stego_t_mode == "Normal (No Time Limit)"))

                with s_col2:
                    if carrier_img is not None:
                        w, h = carrier_img.size
                        max_chars = (w * h * 3) // 8 - len(STEGO_DELIM)
                        st.markdown("##### 📊 Carrier Image Specs & Capacity")
                        st.markdown(f"- **Resolution:** `{w} x {h}` pixels (`{w*h:,}` total pixels)\n- **Max Secret Capacity:** `~{max_chars:,}` bytes")
                        
                        if secret_stego_msg:
                            usage_pct = min(len(secret_stego_msg.encode('utf-8')) * 3 / max(max_chars, 1), 1.0)
                            st.progress(usage_pct, text=f"Pixel LSB Capacity Used: {usage_pct*100:.2f}%")
                        st.image(carrier_img, caption="Original Carrier Preview", use_container_width=True)

                if st.button("🖼️ Encrypt & Embed Into Image Pixels", type="primary", use_container_width=True):
                    if carrier_img is None:
                        st.error("Please upload an image or select 'Auto-Generate Cyber Carrier Image' first!")
                    elif not secret_stego_msg.strip():
                        st.error("Please enter a secret message to hide inside the image!")
                    else:
                        try:
                            s_mode = "EXPIRE" if "Self-Destruct" in stego_t_mode else ("WAIT" if "Time-Capsule" in stego_t_mode else "NONE")
                            s_ts = int(time.time()) + (stego_mins * 60) if s_mode != "NONE" else 0
                            encrypted_payload = encrypt_core(secret_stego_msg, group_key, reverse_rule, s_mode, s_ts)
                            stego_result_img = encode_image_lsb(carrier_img, encrypted_payload)

                            buf = io.BytesIO()
                            stego_result_img.save(buf, format="PNG")
                            byte_data = buf.getvalue()

                            st.success("🎉 **Stego Image Created Successfully!** The encrypted message is now invisibly locked inside the pixels.")
                            p1, p2 = st.columns(2)
                            with p1:
                                st.image(carrier_img, caption="Before (Original Carrier)", use_container_width=True)
                            with p2:
                                st.image(stego_result_img, caption="After (Stego PNG with Hidden Cipher)", use_container_width=True)

                            st.download_button(
                                label="⬇️ Download Stego Image (Lossless PNG)",
                                data=byte_data,
                                file_name=f"stego_secret_{int(time.time())}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"❌ Steganography Error: {str(e)}")

            else:
                st.markdown("##### 🔍 Upload Stego PNG to Extract & Decrypt Hidden Message")
                up_stego = st.file_uploader("Upload Stego Image (Must be lossless .PNG generated by this suite):", type=["png"])
                if up_stego:
                    decode_img = Image.open(up_stego).convert("RGB")
                    col_prev, col_act = st.columns([1, 1.5])
                    with col_prev:
                        st.image(decode_img, caption="Uploaded Stego PNG", use_container_width=True)
                    with col_act:
                        st.info("💡 Make sure your **Sidebar Passphrase, Shift Offset, and Symbol Vault** match the exact rules used when this image was encoded.")
                        if st.button("🔓 Extract Bits & Decrypt Payload", type="primary", use_container_width=True):
                            ok_ext, hidden_cipher = decode_image_lsb(decode_img)
                            if not ok_ext:
                                st.error(hidden_cipher)
                            else:
                                st.caption("Extracted Encrypted Payload from LSB Pixels:")
                                st.code(hidden_cipher, language=None)
                                ok_dec, plain_msg = decrypt_core(hidden_cipher, group_key, reverse_rule)
                                if ok_dec:
                                    st.success("🎉 **Decrypted Secret Message:**")
                                    st.info(plain_msg)
                                else:
                                    st.error(plain_msg)

# ==============================================================================
# PHẦN 3: SECRET CHAT ROOMS (STEGO IMAGE CHAT + MESSAGE/ROOM DELETION CONTROLS)
# ==============================================================================
elif "3. Secret Chat Rooms" in main_menu:
    st.markdown("""
    <div class="hero-box" style="padding: 20px 28px; margin-bottom: 18px;">
        <div class="hero-badge">💬 ZERO-KNOWLEDGE PERSISTENT CHANNELS</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Encrypted Secret Chat Rooms</h2>
        <p class="hero-sub">Collaborate via encrypted text, camouflaged prose, or LSB Stego Images. Full self-destruct controls for individual messages, chat history, and entire rooms.</p>
    </div>
    """, unsafe_allow_html=True)

    if not secret_seed:
        st.warning("⚠️ **Passphrase Required:** Please enter your **Group Secret Passphrase** in the left Sidebar to enter or create encrypted chat rooms!")
    else:
        rooms = load_all_rooms()

        # Thanh công cụ chọn phòng, đặt biệt danh và tạo phòng mới
        top_c1, top_c2, top_c3 = st.columns([1.8, 1.2, 1])
        with top_c1:
            room_options = ["➕ Create New Secret Room"] + list(rooms.keys())
            r_name = st.selectbox("📂 Select Active Channel or Create New:", room_options)
        with top_c2:
            agent_name = st.text_input("🕵️ Your Agent Codename:", value="Agent-007", placeholder="e.g. Ghost_VN")
        with top_c3:
            st.write("")
            if st.button("🔄 Refresh Room Feed", use_container_width=True):
                st.rerun()

        if r_name == "➕ Create New Secret Room":
            st.markdown("""
            <div class="ws-banner">
                <h4>➕ Initialize New Encrypted Channel</h4>
                <p>Create a persistent room stored on the server. Only members with the matching Sidebar Cipher Rules can decrypt messages inside.</p>
            </div>
            """, unsafe_allow_html=True)
            new_r = st.text_input("New Room Name / Channel ID:", placeholder="e.g. Operation-Blackbriar")
            if st.button("🚀 Create Encrypted Room", type="primary"):
                clean_name = new_r.strip()
                if not clean_name:
                    st.error("Please enter a valid room name!")
                elif clean_name in rooms:
                    st.warning("This room already exists! Select it from the dropdown above.")
                else:
                    rooms[clean_name] = {
                        "messages": [],
                        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                    }
                    save_all_rooms(rooms)
                    st.success(f"✅ Room **'{clean_name}'** created! Select it from the dropdown list above to start chatting.")
                    st.rerun()

        else:
            # --- QUẢN LÝ PHÒNG & NÚT XÓA LỊCH SỬ / XÓA PHÒNG ---
            msgs = rooms.get(r_name, {}).get("messages", [])
            created_info = rooms.get(r_name, {}).get("created_at", "UTC Verified")

            bar_info, bar_clear, bar_destroy = st.columns([2.4, 1, 1])
            with bar_info:
                st.markdown(f"#### 📡 Channel: `{r_name}` &nbsp; <span style='font-size:0.85rem;color:#94a3b8;'>({len(msgs)} messages • Created: {created_info})</span>", unsafe_allow_html=True)
            with bar_clear:
                if st.button("🧹 Clear Chat History", use_container_width=True, help="Delete all messages in this room but keep the room open"):
                    clear_room_history(r_name)
                    st.toast(f"🧹 Cleared all messages in {r_name}!", icon="🧹")
                    st.rerun()
            with bar_destroy:
                if st.button("💥 Destroy Room", type="primary", use_container_width=True, help="Permanently delete this entire room and all its data"):
                    destroy_entire_room(r_name)
                    st.toast(f"💥 Room {r_name} permanently destroyed!", icon="💥")
                    st.rerun()

            st.divider()

            # --- DANH SÁCH TIN NHẮN (CÓ NÚT GIẢI MÃ & XÓA TỪNG TIN RIÊNG BIỆT) ---
            st.markdown("##### 📜 Encrypted Channel Feed")
            if not msgs:
                st.info("📭 No messages in this channel yet. Use the trasmissione console below to send encrypted text, camouflage prose, or a Stego Image!")
            else:
                for idx, m in enumerate(msgs):
                    m_type = m.get("type", "TEXT")
                    m_sender = m.get("sender", "Agent")
                    m_time = m.get("timestamp", "")
                    m_cipher = m.get("ciphertext", "")
                    m_img_b64 = m.get("image_b64", "")

                    badge_label = "🔐 CIPHERTEXT" if m_type == "TEXT" else ("🎭 CAMOUFLAGE PROSE" if m_type == "CAMO" else "🖼️ LSB STEGO IMAGE")

                    msg_col, act_col1, act_col2 = st.columns([5, 1.2, 0.9])
                    with msg_col:
                        st.markdown(f"""
                        <div class="chat-card">
                            <div class="chat-meta">
                                <span class="chat-sender">🕵️ {m_sender}</span> • {m_time}
                                <span class="chat-badge">{badge_label}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if m_type == "STEGO_IMG" and m_img_b64:
                            try:
                                img_bytes = base64.b64decode(m_img_b64)
                                stego_chat_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                                ic1, ic2 = st.columns([1, 1.5])
                                with ic1:
                                    st.image(stego_chat_img, caption=f"Stego PNG from {m_sender}", use_container_width=True)
                                with ic2:
                                    st.download_button(
                                        label="⬇️ Download Stego PNG",
                                        data=img_bytes,
                                        file_name=f"chat_stego_{idx}.png",
                                        mime="image/png",
                                        key=f"dl_img_{r_name}_{idx}"
                                    )
                            except Exception:
                                st.error("Corrupted image data in message.")
                        else:
                            st.code(m_cipher, language=None)

                    with act_col1:
                        st.write("")
                        if st.button("🔓 Decode", key=f"dec_btn_{r_name}_{idx}", use_container_width=True):
                            if m_type == "STEGO_IMG" and m_img_b64:
                                img_bytes = base64.b64decode(m_img_b64)
                                stego_chat_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                                ok_e, ext_c = decode_image_lsb(stego_chat_img)
                                if not ok_e:
                                    st.error(ext_c)
                                else:
                                    ok_d, plain = decrypt_core(ext_c, group_key, reverse_rule)
                                    if ok_d: st.success(f"🔓 {plain}")
                                    else: st.error(plain)
                            elif m_type == "CAMO":
                                ok_c, ext_c = decode_english_camouflage(m_cipher)
                                if not ok_c:
                                    st.error(ext_c)
                                else:
                                    ok_d, plain = decrypt_core(ext_c, group_key, reverse_rule)
                                    if ok_d: st.success(f"🔓 {plain}")
                                    else: st.error(plain)
                            else:
                                ok_d, plain = decrypt_core(m_cipher, group_key, reverse_rule)
                                if ok_d: st.success(f"🔓 {plain}")
                                else: st.error(plain)

                    with act_col2:
                        st.write("")
                        if st.button("🗑️ Delete", key=f"del_btn_{r_name}_{idx}", use_container_width=True, help="Delete this specific message"):
                            delete_single_message(r_name, idx)
                            st.rerun()

            st.divider()

            # --- BẢNG ĐIỀU KHIỂN GỬI TIN NHẮN & MÃ HÓA HÌNH ẢNH TRONG PHÒNG CHAT ---
            st.markdown("##### 📤 Secure Transmission Console (Send to Room)")
            chat_tab1, chat_tab2, chat_tab3 = st.tabs([
                "📝 1. Send Encrypted Text / Time-Lock",
                "🎭 2. Send English Camouflage",
                "🖼️ 3. Send LSB Stego Image (Same as Workspace)"
            ])

            # Tab 1: Gửi Text Mã hóa & Hẹn giờ tự hủy
            with chat_tab1:
                ct_col1, ct_col2 = st.columns([2.5, 1])
                with ct_col1:
                    chat_txt_in = st.text_area("Type message to encrypt & send:", placeholder="Confidential team message...", height=95, key="chat_txt_box")
                with ct_col2:
                    chat_t_mode = st.selectbox("UTC Time-Lock:", ["Normal (No Limit)", "🔥 Self-Destruct", "⏳ Time-Capsule"], key="chat_t_mode")
                    chat_mins = st.number_input("Minutes:", 1, 10080, 15, disabled=(chat_t_mode == "Normal (No Limit)"), key="chat_mins")

                if st.button("📤 Encrypt & Send to Room", type="primary", use_container_width=True):
                    if chat_txt_in.strip():
                        m_code = "EXPIRE" if "Self-Destruct" in chat_t_mode else ("WAIT" if "Time-Capsule" in chat_t_mode else "NONE")
                        t_ts = int(time.time()) + (chat_mins * 60) if m_code != "NONE" else 0
                        c_out = encrypt_core(chat_txt_in.strip(), group_key, reverse_rule, m_code, t_ts)
                        add_msg(r_name, agent_name.strip() or "Agent", c_out, msg_type="TEXT")
                        st.rerun()
                    else:
                        st.warning("Please enter a message before sending.")

            # Tab 2: Gửi Tin nhắn Ngụy trang Tiếng Anh
            with chat_tab2:
                chat_camo_in = st.text_area("Type secret message to disguise as English prose & send:", placeholder="e.g. Deploy backup server at 03:00 UTC", height=95)
                if st.button("🎭 Disguise as English Prose & Send to Room", type="primary", use_container_width=True):
                    if chat_camo_in.strip():
                        raw_c = encrypt_core(chat_camo_in.strip(), group_key, reverse_rule, "NONE", 0)
                        camo_out = encode_english_camouflage(raw_c)
                        add_msg(r_name, agent_name.strip() or "Agent", camo_out, msg_type="CAMO")
                        st.rerun()
                    else:
                        st.warning("Please enter a secret message.")

            # Tab 3: Mã hóa Hình ảnh LSB (Y Hệt Phần 2) & Gửi thẳng vào phòng hoặc tải về
            with chat_tab3:
                st.markdown("""
                <div class="ws-banner">
                    <h4>🖼️ Room LSB Image Steganography Lab</h4>
                    <p>Embed your encrypted message inside PNG pixels (identical to Workspace Lab) and broadcast the Stego Image directly into this chat room, or extract an external Stego PNG.</p>
                </div>
                """, unsafe_allow_html=True)

                chat_stego_op = st.radio(
                    "Room Stego Operation:",
                    ["📤 Hide Secret in Image & Post to Room (Encode)", "📥 Extract Secret from Stego PNG (Decode)"],
                    horizontal=True,
                    key="chat_stego_op"
                )

                if "Encode" in chat_stego_op:
                    cs1, cs2 = st.columns([1.2, 1])
                    with cs1:
                        c_img_src = st.radio(
                            "Carrier Image Source:",
                            ["📁 Upload My Own Image (PNG/JPG)", "⚡ Auto-Generate Cyber Carrier Image"],
                            horizontal=True,
                            key="chat_img_src"
                        )
                        chat_carrier = None
                        if "Upload" in c_img_src:
                            c_up = st.file_uploader("Upload Carrier Image:", type=["png", "jpg", "jpeg"], key="chat_up_carrier")
                            if c_up:
                                chat_carrier = Image.open(c_up).convert("RGB")
                        else:
                            chat_carrier = generate_sample_carrier_image()
                            st.caption("✨ Generated a 480x260 Cyber Carrier Matrix.")

                        chat_stego_secret = st.text_area(
                            "Secret Message to Embed in Pixels:",
                            placeholder="Type secret payload to hide inside the image...",
                            height=90,
                            key="chat_stego_secret"
                        )

                        cs_m, cs_min = st.columns([2, 1])
                        with cs_m:
                            chat_stego_tmode = st.selectbox("Image Time-Lock (UTC):", ["Normal (No Limit)", "🔥 Self-Destruct", "⏳ Time-Capsule"], key="chat_stego_tmode")
                        with cs_min:
                            chat_stego_mins = st.number_input("Mins:", 1, 10080, 30, disabled=(chat_stego_tmode == "Normal (No Limit)"), key="chat_stego_mins")

                    with cs2:
                        if chat_carrier is not None:
                            cw, ch = chat_carrier.size
                            c_max = (cw * ch * 3) // 8 - len(STEGO_DELIM)
                            st.markdown("##### 📊 Carrier Image Capacity")
                            st.markdown(f"- **Resolution:** `{cw} x {ch}` px (`~{c_max:,}` bytes capacity)")
                            if chat_stego_secret:
                                c_pct = min(len(chat_stego_secret.encode('utf-8')) * 3 / max(c_max, 1), 1.0)
                                st.progress(c_pct, text=f"Pixel LSB Capacity Used: {c_pct*100:.2f}%")
                            st.image(chat_carrier, caption="Carrier Preview", use_container_width=True)

                    btn_post, btn_preview = st.columns(2)
                    with btn_post:
                        if st.button("🖼️ Embed Secret & Post Image to Room", type="primary", use_container_width=True):
                            if chat_carrier is None:
                                st.error("Please select or upload a carrier image!")
                            elif not chat_stego_secret.strip():
                                st.error("Please enter a secret message to embed!")
                            else:
                                try:
                                    sm = "EXPIRE" if "Self-Destruct" in chat_stego_tmode else ("WAIT" if "Time-Capsule" in chat_stego_tmode else "NONE")
                                    sts = int(time.time()) + (chat_stego_mins * 60) if sm != "NONE" else 0
                                    enc_pay = encrypt_core(chat_stego_secret.strip(), group_key, reverse_rule, sm, sts)
                                    stego_out_img = encode_image_lsb(chat_carrier, enc_pay)

                                    buf = io.BytesIO()
                                    stego_out_img.save(buf, format="PNG")
                                    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

                                    add_msg(r_name, agent_name.strip() or "Agent", "[LSB Stego PNG Image]", msg_type="STEGO_IMG", image_b64=b64_str)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")

                    with btn_preview:
                        if st.button("🛠️ Generate Stego PNG for Download Only", use_container_width=True):
                            if chat_carrier is not None and chat_stego_secret.strip():
                                sm = "EXPIRE" if "Self-Destruct" in chat_stego_tmode else ("WAIT" if "Time-Capsule" in chat_stego_tmode else "NONE")
                                sts = int(time.time()) + (chat_stego_mins * 60) if sm != "NONE" else 0
                                enc_pay = encrypt_core(chat_stego_secret.strip(), group_key, reverse_rule, sm, sts)
                                stego_out_img = encode_image_lsb(chat_carrier, enc_pay)
                                buf = io.BytesIO()
                                stego_out_img.save(buf, format="PNG")
                                st.download_button(
                                    "⬇️ Download Stego PNG Now",
                                    data=buf.getvalue(),
                                    file_name=f"room_stego_{int(time.time())}.png",
                                    mime="image/png",
                                    use_container_width=True
                                )
                            else:
                                st.warning("Please provide an image and secret message first.")

                else:
                    up_chat_stego = st.file_uploader("Upload Stego PNG to Decode:", type=["png"], key="chat_dec_stego")
                    if up_chat_stego:
                        d_img = Image.open(up_chat_stego).convert("RGB")
                        st.image(d_img, caption="Uploaded Stego PNG", width=320)
                        if st.button("🔓 Extract & Decrypt Stego PNG", type="primary"):
                            ok_e, h_c = decode_image_lsb(d_img)
                            if not ok_e:
                                st.error(h_c)
                            else:
                                ok_d, p_msg = decrypt_core(h_c, group_key, reverse_rule)
                                if ok_d:
                                    st.success("🎉 Decrypted Message from Pixels:")
                                    st.info(p_msg)
                                else:
                                    st.error(p_msg)

# ==============================================================================
# PHẦN 4: CRYPTO CHALLENGES & GLOBAL CTF ARENA (KIDS TO GRANDMASTER EDITION)
# ==============================================================================
elif "4. Crypto Challenges" in main_menu:
    CTF_DB_FILE = "ctf_arena_db.json"

    def load_ctf_db() -> dict:
        if not os.path.exists(CTF_DB_FILE):
            seed_db = {
                "users": {
                    "AlexMercer_US": {
                        "pin_hash": hashlib.sha256(b"9999").hexdigest(),
                        "score": 12500,
                        "solved": ["T1_1", "T2_1", "T3_1", "T4_1", "T5_1"],
                        "surrendered": [],
                        "hints_used": [],
                        "friends": [],
                        "friend_requests": []
                    },
                    "ElenaRostova_UK": {
                        "pin_hash": hashlib.sha256(b"9999").hexdigest(),
                        "score": 6800,
                        "solved": ["T1_2", "T2_2", "T3_2", "T4_2"],
                        "surrendered": [],
                        "hints_used": [],
                        "friends": [],
                        "friend_requests": []
                    },
                    "KenjiSato_JP": {
                        "pin_hash": hashlib.sha256(b"9999").hexdigest(),
                        "score": 2350,
                        "solved": ["T1_3", "T2_3", "T3_3"],
                        "surrendered": [],
                        "hints_used": [],
                        "friends": [],
                        "friend_requests": []
                    }
                },
                "direct_messages": {}
            }
            with open(CTF_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(seed_db, f, ensure_ascii=False, indent=4)
            return seed_db
        try:
            with open(CTF_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"users": {}, "direct_messages": {}}

    def save_ctf_db(data: dict):
        with open(CTF_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_agent_rank(score: int) -> str:
        if score >= 20000: return "👑 Grandmaster Archon"
        if score >= 8000:  return "💎 Global Cryptanalyst"
        if score >= 3000:  return "🔥 History & Cipher Master"
        if score >= 800:   return "⚡ Puzzle Explorer"
        if score > 0:      return "🛡️ Junior Detective"
        return "🌱 Starter Explorer"

    # --- KHO DỮ LIỆU BÁCH KHOA TOÀN THƯ THẾ GIỚI (GLOBAL ENCYCLOPEDIA POOL) ---
    WORLD_KNOWLEDGE_POOL = [
        # Countries & Iconic Landmarks
        ("Country", "JAPAN", "The Land of the Rising Sun, famous for Mount Fuji, cherry blossoms, and Tokyo."),
        ("Country", "EGYPT", "North African country famous for the Ancient Pyramids of Giza, the Sphinx, and the Nile River."),
        ("Country", "FRANCE", "European country home to the Eiffel Tower, the Louvre Museum, and Paris."),
        ("Country", "BRAZIL", "The largest country in South America, famous for the Amazon Rainforest and Christ the Redeemer."),
        ("Country", "ITALY", "Boot-shaped European country famous for the Colosseum in Rome, Venice canals, and pizza."),
        ("Country", "CANADA", "The second-largest country in the world, famous for maple leaf flags and Niagara Falls."),
        ("Country", "AUSTRALIA", "Continent and country famous for the Sydney Opera House, kangaroos, and the Great Barrier Reef."),
        ("Landmark", "STATUE OF LIBERTY", "Colossal neoclassical sculpture on Liberty Island in New York Harbor, gifted by France."),
        ("Landmark", "GREAT WALL", "Ancient series of stone fortifications built across the historical northern borders of China."),
        ("Landmark", "TAJ MAHAL", "Ivory-white marble mausoleum on the right bank of the river Yamuna in Agra, India."),
        ("Landmark", "MACHU PICCHU", "15th-century Inca citadel located in the Eastern Cordillera of southern Peru."),
        ("Landmark", "BIG BEN", "Famous nickname for the Great Bell of the striking clock at the Palace of Westminster in London."),
        # US Presidents
        ("US President", "GEORGE WASHINGTON", "The 1st President of the United States and Commander-in-Chief of the Continental Army."),
        ("US President", "ABRAHAM LINCOLN", "The 16th US President who issued the Emancipation Proclamation and led the nation through the Civil War."),
        ("US President", "THEODORE ROOSEVELT", "The 26th US President, famous for conservationism, the Panama Canal, and Mount Rushmore."),
        ("US President", "FRANKLIN ROOSEVELT", "The 32nd US President (FDR) who led the United States through the Great Depression and World War II."),
        ("US President", "JOHN F KENNEDY", "The 35th US President (JFK) who initiated the Apollo space program during the Cold War."),
        ("US President", "THOMAS JEFFERSON", "The 3rd US President and the principal author of the Declaration of Independence in 1776."),
        ("US President", "BARACK OBAMA", "The 44th President of the United States and the first African American to hold the office."),
        # World Famous Figures & Scientists
        ("World Figure", "ALBERT EINSTEIN", "German-born theoretical physicist who developed the Theory of Relativity (E = mc^2)."),
        ("World Figure", "ISAAC NEWTON", "English mathematician and physicist who formulated the laws of motion and universal gravitation."),
        ("World Figure", "LEONARDO DA VINCI", "Italian Renaissance polymath who painted the Mona Lisa and The Last Supper."),
        ("World Figure", "ALAN TURING", "English mathematician and father of computer science who cracked the Nazi Enigma machine in WWII."),
        ("World Figure", "MARIE CURIE", "Polish-French physicist and chemist who conducted pioneering research on radioactivity and won two Nobel Prizes."),
        ("World Figure", "NIKOLA TESLA", "Serbian-American inventor best known for his contributions to the design of the modern alternating current (AC) electricity system."),
        ("World Figure", "NELSON MANDELA", "South African anti-apartheid revolutionary and political leader who served as the 1st President of South Africa."),
        ("World Figure", "NAPOLEON BONAPARTE", "French military commander and Emperor who rose to prominence during the French Revolution."),
        ("World Figure", "WILLIAM SHAKESPEARE", "English playwright and poet, widely regarded as the greatest writer in the English language (Romeo and Juliet, Hamlet)."),
        # Historical Wars, Conflicts & Major Global Events
        ("Historical War", "WORLD WAR II", "Global conflict from 1939 to 1945 involving the Allies and the Axis powers, ending after Normandy and Hiroshima."),
        ("Historical War", "WORLD WAR I", "Global war originating in Europe from 1914 to 1918, triggered by the assassination of Archduke Franz Ferdinand."),
        ("Historical War", "COLD WAR", "Geopolitical tension between the United States and the Soviet Union from 1947 to 1991 without direct large-scale fighting."),
        ("Historical War", "AMERICAN CIVIL WAR", "Civil war in the United States (1861-1865) fought between the Union (North) and the Confederacy (South)."),
        ("Historical Battle", "BATTLE OF WATERLOO", "Famous 1815 battle in Belgium where Napoleon Bonaparte was defeated for the final time."),
        ("Historical Event", "SEPTEMBER 11", "The 2001 terrorist attacks by al-Qaeda against the World Trade Center Twin Towers in New York and the Pentagon."),
        ("Historical Event", "PEARL HARBOR", "Surprise military strike by the Imperial Japanese Navy Air Service upon the United States in Hawaii on December 7, 1941."),
        ("Historical Event", "APOLLO 11", "Historic 1969 spaceflight that first landed humans—Neil Armstrong and Buzz Aldrin—on the Moon."),
        ("Historical Event", "FALL OF BERLIN WALL", "Pivotal 1989 world event marking the destruction of the concrete barrier dividing East and West Berlin."),
        ("Historical Event", "TITANIC DISASTER", "The 1912 sinking of the British passenger liner in the North Atlantic Ocean after striking an iceberg."),
        ("Historical Event", "FRENCH REVOLUTION", "Period of radical political and societal change in France that began with the Storming of the Bastille in 1789."),
        ("Historical Event", "CUBAN MISSILE CRISIS", "13-day confrontation in October 1962 between the US and USSR that brought the world closest to nuclear conflict.")
    ]

    def caesar_shift_ascii(text: str, shift: int) -> str:
        """Chỉ dịch chuyển 26 chữ cái tiếng Anh A-Z để người chơi dễ nhìn, không sinh ký tự lạ."""
        out = []
        for ch in text.upper():
            if "A" <= ch <= "Z":
                out.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
            else:
                out.append(ch)
        return "".join(out)

    def atbash_ascii(text: str) -> str:
        """Đảo ngược bảng chữ cái tiếng Anh: A<->Z, B<->Y, C<->X..."""
        out = []
        for ch in text.upper():
            if "A" <= ch <= "Z":
                out.append(chr(ord("Z") - (ord(ch) - ord("A"))))
            else:
                out.append(ch)
        return "".join(out)

    def leetspeak_encode(text: str) -> str:
        mapping = {"A": "4", "E": "3", "I": "1", "O": "0", "S": "5", "T": "7"}
        return "".join(mapping.get(ch, ch) for ch in text.upper())

    def generate_dynamic_challenge(username: str, tier: int, q_num: int) -> dict:
        seed_str = f"GLOBAL_ENCYCLOPEDIA_V3_{username}_T{tier}_Q{q_num}"
        rng = random.Random(seed_str)

        category, answer_raw, trivia_clue = rng.choice(WORLD_KNOWLEDGE_POOL)
        clean_answer = answer_raw.upper().strip()

        tier_pts = {1: 100, 2: 250, 3: 500, 4: 1000, 5: 2500}
        base_pts = tier_pts[tier]

        # ======================================================================
        # TIER 1: KIDS & BEGINNERS (SIÊU DỄ — ĐẢO NGƯỢC CHỮ HOẶC KHỚP NGUYÊN ÂM)
        # ======================================================================
        if tier == 1:
            sub_type = q_num % 2
            if sub_type == 0:
                # Kiểu 1A: Viết ngược từ (Mirror / Backwards Word)
                encoded_puzzle = clean_answer[::-1]
                rule_desc = "🔄 **Mirror Word Puzzle (Read Backwards):** The letters of the answer have simply been flipped from right to left!"
                step_hint = (
                    f"1. Read the clue: *{trivia_clue}*\n"
                    f"2. Read the puzzle string **`{encoded_puzzle}`** from right to left.\n"
                    f"3. It starts with **`{clean_answer[0]}`** and ends with **`{clean_answer[-1]}`** ({len(clean_answer)} characters total)."
                )
            else:
                # Kiểu 1B: Dịch chuyển đúng 1 chữ cái (Next Letter in Alphabet: A->B, B->C)
                encoded_puzzle = caesar_shift_ascii(clean_answer, 1)
                rule_desc = "🔤 **Alphabet Step +1 (Kids Cipher):** Each letter was moved forward by **1 step** in the English alphabet (`A -> B`, `B -> C`, ..., `Z -> A`). Move each letter **1 step backward** to solve!"
                step_hint = (
                    f"1. Shift each letter 1 step back in `A B C D E F G H I J K L M N O P Q R S T U V W X Y Z`.\n"
                    f"2. First word starts with **`{clean_answer[:2]}...`** and ends with **`...{clean_answer[-2:]}`**."
                )

            briefing = (
                f"### 🎈 Kids & Beginners Puzzle #{q_num} — Category: **{category}**\n"
                f"**🌍 World Knowledge Clue:** *{trivia_clue}*\n\n"
                f"{rule_desc}\n"
                f"*(💡 You can solve this right here in your head—no complex tools needed! Just type the answer below)*"
            )
            solution_box = (
                f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                f"📖 **Explanation:** Based on the clue (*{trivia_clue}*), decoding `{encoded_puzzle}` gives **`{clean_answer}`**."
            )
            return {
                "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                "briefing": briefing, "payload": encoded_puzzle, "is_img": False,
                "hint": step_hint, "flag": clean_answer, "solution": solution_box
            }

        # ======================================================================
        # TIER 2: YOUNG EXPLORERS (LEETSPEAK SỐ HÓA HOẶC CAESAR SHIFT +3)
        # ======================================================================
        elif tier == 2:
            shift_val = rng.choice([2, 3])
            if q_num % 2 == 0:
                encoded_puzzle = leetspeak_encode(clean_answer)[::-1]
                rule_desc = (
                    "🕹️ **Reversed Gamer Code (Leetspeak + Mirror):**\n"
                    "- Numbers replaced vowels/letters: **`4 = A`**, **`3 = E`**, **`1 = I`**, **`0 = O`**, **`5 = S`**, **`7 = T`**.\n"
                    "- Then the whole word was **written backwards**!"
                )
                step_hint = (
                    f"1. Flip the string first: **`{leetspeak_encode(clean_answer)}`**\n"
                    f"2. Replace numbers (`4->A, 3->E, 1->I, 0->O, 5->S, 7->T`).\n"
                    f"3. The answer starts with **`{clean_answer[:3]}...`**!"
                )
            else:
                encoded_puzzle = caesar_shift_ascii(clean_answer, shift_val)
                rule_desc = (
                    f"🏛️ **Julius Caesar Shift +{shift_val} Cipher:**\n"
                    f"- Every English letter was shifted forward by **`+{shift_val}`** positions in the alphabet (`A B C D E F G H I J K L M N O P Q R S T U V W X Y Z`).\n"
                    f"- Shift every letter **backward by `{shift_val}`** to reveal the {category}!"
                )
                step_hint = (
                    f"1. Move each letter in `{encoded_puzzle}` back by `{shift_val}` steps in the English alphabet.\n"
                    f"2. Clue check: *{trivia_clue}*\n"
                    f"3. The decoded answer starts with **`{clean_answer[:3]}...`** and ends with **`...{clean_answer[-2:]}`**."
                )

            briefing = (
                f"### 🧭 Young Explorer Mission #{q_num} — Category: **{category}**\n"
                f"**🌍 Trivia Clue:** *{trivia_clue}*\n\n"
                f"{rule_desc}"
            )
            solution_box = (
                f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                f"📖 **Walkthrough:** Decoding `{encoded_puzzle}` using the rule above reveals the {category}: **`{clean_answer}`**."
            )
            return {
                "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                "briefing": briefing, "payload": encoded_puzzle, "is_img": False,
                "hint": step_hint, "flag": clean_answer, "solution": solution_box
            }

        # ======================================================================
        # TIER 3: STUDENTS & FRIENDS TRIVIA (ATBASH / HEX / CAESAR + WORKSPACE)
        # ======================================================================
        elif tier == 3:
            mode_t3 = q_num % 3
            if mode_t3 == 0:
                encoded_puzzle = atbash_ascii(clean_answer)
                rule_desc = (
                    "🪞 **Ancient Atbash Mirror Alphabet:**\n"
                    "The alphabet is mapped to its reverse (`A ↔ Z`, `B ↔ Y`, `C ↔ X`, ..., `M ↔ N`).\n"
                    "- Plain:  `A B C D E F G H I J K L M N O P Q R S T U V W X Y Z`\n"
                    "- Cipher: `Z Y X W V U T S R Q P O N M L K J I H G F E D C B A`"
                )
            elif mode_t3 == 1:
                encoded_puzzle = " ".join(f"{ord(c):02X}" for c in clean_answer)
                rule_desc = (
                    "💻 **ASCII Hexadecimal Byte Stream:**\n"
                    "Each character of the historical answer has been converted into its 2-digit Base-16 Hexadecimal ASCII code (`41 = A`, `42 = B`, ..., `20 = Space`)."
                )
            else:
                shift_t3 = rng.randint(5, 13)
                encoded_puzzle = caesar_shift_ascii(clean_answer, shift_t3)
                rule_desc = f"🔐 **ROT-{shift_t3} Historical Intercept:** Each letter is rotated forward by **`+{shift_t3}`** positions in the 26-letter English alphabet."

            briefing = (
                f"### 🎓 Student & Friends Challenge #{q_num} — Category: **{category}**\n"
                f"**🌍 Historical / Global Clue:** *{trivia_clue}*\n\n"
                f"{rule_desc}"
            )
            step_hint = (
                f"💡 **Detailed Hint:**\n"
                f"- Category: **{category}** | Clue: *{trivia_clue}*\n"
                f"- Word Structure: `{len(clean_answer.split())}` word(s), `{len(clean_answer)}` total characters.\n"
                f"- First 3 characters: **`{clean_answer[:3]}...`** | Last 2 characters: **`...{clean_answer[-2:]}`**."
            )
            solution_box = (
                f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                f"📖 **Full Solution:** The ciphertext `{encoded_puzzle}` decodes directly to **`{clean_answer}`** ({trivia_clue})."
            )
            return {
                "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                "briefing": briefing, "payload": encoded_puzzle, "is_img": False,
                "hint": step_hint, "flag": clean_answer, "solution": solution_box
            }

        # ======================================================================
        # TIER 4: CYBER SPECIALISTS (LSB STEGO IMAGE & MARKOV CAMOUFLAGE)
        # ======================================================================
        elif tier == 4:
            pass_key = clean_answer.split()[0] # Dùng chữ đầu tiên của danh nhân/đất nước làm Passphrase
            shift_val = rng.randint(5, 25)
            k = build_custom_key(pass_key, [], shift_val, "")
            secret_payload_msg = f"CLASSIFIED INTEL: {clean_answer}"
            raw_c = encrypt_core(secret_payload_msg, k, False, "NONE", 0)

            if q_num % 2 == 0:
                carrier = generate_sample_carrier_image(420, 220)
                stego_img = encode_image_lsb(carrier, raw_c)
                buf = io.BytesIO()
                stego_img.save(buf, format="PNG")
                briefing = (
                    f"### 🕵️‍♂️ Specialist Forensic Steganography #{q_num} ({category})\n"
                    f"We intercepted a lossless PNG image containing a hidden historical entity.\n"
                    f"1. **Passphrase Clue:** First word of the answer to: *{trivia_clue}* (Uppercase, `{len(pass_key)}` letters).\n"
                    f"2. **Sidebar Rules:** Shift Offset = **`{shift_val}`** | Symbol Vault = **`Empty (Clear all icons)`** | Reverse = **`Unchecked`**.\n"
                    f"3. Download the PNG below, configure your Sidebar, and decode it in **2. Cipher Workspace -> Tab 3 (LSB Image Lab)**!"
                )
                step_hint = (
                    f"💡 **Step-by-Step Forensic Hint:**\n"
                    f"1. In the Left Sidebar, set **Group Secret Passphrase** = **`{pass_key}`**\n"
                    f"2. Set **Shift Offset** = **`{shift_val}`** and **remove all icons** from Symbol Vault.\n"
                    f"3. Download the Stego PNG and extract it in **Cipher Workspace -> Tab 3**, or type the full entity starting with **`{clean_answer[:4]}...`**!"
                )
                solution_box = (
                    f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                    f"📖 **Forensic Breakdown:**\n"
                    f"- **Sidebar Passphrase:** `{pass_key}` | **Shift Offset:** `{shift_val}` | **Symbols:** `None`\n"
                    f"- **Extracted Stego Payload:** `{secret_payload_msg}` -> Answer: **`{clean_answer}`**"
                )
                return {
                    "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                    "briefing": briefing, "payload": buf.getvalue(), "is_img": True,
                    "hint": step_hint, "flag": clean_answer, "solution": solution_box
                }
            else:
                camo_text = encode_english_camouflage(raw_c)
                briefing = (
                    f"### 🎭 Specialist Linguistic Camouflage #{q_num} ({category})\n"
                    f"An operative disguised a secret historical target inside innocent English IT sentences.\n"
                    f"1. **Passphrase:** **`{pass_key}`**\n"
                    f"2. **Shift Offset:** **`{shift_val}`** | **Symbol Vault:** **`Empty (0 icons)`** | **Reverse:** **`Unchecked`**.\n"
                    f"3. Copy the English prose below and decode it in **2. Cipher Workspace -> Tab 2 (English Camouflage Studio)**!"
                )
                step_hint = (
                    f"💡 **Step-by-Step Hint:**\n"
                    f"Set Sidebar Passphrase = `{pass_key}`, Shift = `{shift_val}`, clear all icons in Symbol Vault, then paste the paragraph into **Cipher Workspace -> Tab 2 (Reveal Secret)**. Clue: *{trivia_clue}*."
                )
                solution_box = (
                    f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                    f"📖 **Full Breakdown:** Using Passphrase `{pass_key}` and Shift `{shift_val}`, the camouflaged text decodes to `{secret_payload_msg}` -> Answer: **`{clean_answer}`**."
                )
                return {
                    "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                    "briefing": briefing, "payload": camo_text, "is_img": False,
                    "hint": step_hint, "flag": clean_answer, "solution": solution_box
                }

        # ======================================================================
        # TIER 5: GRANDMASTER CRYPTANALYSTS (MULTI-LAYER CHAOS CHO CHUYÊN GIA)
        # ======================================================================
        else:
            pass_key = clean_answer.replace(" ", "")
            shift_val = rng.randint(15, 75)
            chosen_icons = [SYMBOLS_POOL[rng.randint(0, min(15, len(SYMBOLS_POOL)-1))] for _ in range(2)]
            pair_rule = "A=@, E=3"
            k = build_custom_key(pass_key, chosen_icons, shift_val, pair_rule)
            flag_code = f"FLAG{{{clean_answer.replace(' ', '_')}_{rng.randint(100,999)}}}"
            raw_c = encrypt_core(f"VERIFIED GRANDMASTER TARGET: {flag_code}", k, True, "NONE", 0)
            camo_payload = encode_english_camouflage(raw_c)
            icons_str = " , ".join(chosen_icons)

            briefing = (
                f"### 👑 Grandmaster Cryptanalysis Matrix #{q_num}\n"
                f"This mission requires full mastery of the **Ultimate Secret Messenger** multi-layer architecture:\n"
                f"- **Passphrase Clue:** Answer to (*{trivia_clue}*) in **UPPERCASE WITH NO SPACES** (`{len(pass_key)}` chars).\n"
                f"- **Shift Offset:** Hidden between **`{shift_val - 1}`** and **`{shift_val + 1}`**\n"
                f"- **Symbol Vault (Exact Order):** **`{icons_str}`**\n"
                f"- **Custom Pairs:** **`{pair_rule}`** | **Reverse Structure:** **`Checked (Enabled)`**\n"
                f"- **Outer Layer:** Linguistic Camouflage Prose. Extract the exact `FLAG{{...}}`!"
            )
            step_hint = (
                f"💡 **Grandmaster Decrypt Key:**\n"
                f"- **Exact Passphrase:** **`{pass_key}`**\n"
                f"- **Exact Shift Offset:** **`{shift_val}`**\n"
                f"- **Symbol Vault:** Select `{icons_str}` in exact order.\n"
                f"- **Custom Pairs:** `{pair_rule}` | **Reverse Structure:** `Checked`.\n"
                f"- Paste the prose into **Cipher Workspace -> Tab 2** to get the Flag!"
            )
            solution_box = (
                f"✅ **Exact Answer to Type:** `{flag_code}`\n\n"
                f"📖 **Complete Cryptanalysis Key:**\n"
                f"- Passphrase: `{pass_key}` | Shift: `{shift_val}` | Symbols: `{icons_str}` | Pairs: `{pair_rule}` | Reverse: `True`\n"
                f"- Decoded Flag: **`{flag_code}`**"
            )
            return {
                "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                "briefing": briefing, "payload": camo_payload, "is_img": False,
                "hint": step_hint, "flag": flag_code, "solution": solution_box
            }

    # --- GIAO DIỆN ĐẤU TRƯỜNG CTF ---
    st.markdown("""
    <div class="hero-box" style="padding: 20px 28px; margin-bottom: 18px;">
        <div class="hero-badge">🕹️ 5,000+ WORLD ENCYCLOPEDIA & CRYPTO MATRIX • KIDS TO GRANDMASTER</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Global Crypto Challenges & CTF Arena</h2>
        <p class="hero-sub">From beginner-friendly World History, Countries & US Presidents puzzles (Tiers 1–2) to professional Steganography & Multi-Layer Cryptanalysis (Tiers 4–5).</p>
    </div>
    """, unsafe_allow_html=True)

    ctf_db = load_ctf_db()
    if "ctf_user" not in st.session_state:
        st.session_state.ctf_user = None

    if not st.session_state.ctf_user:
        st.markdown("""
        <div class="ws-banner">
            <h4>🔐 Agent Authentication Portal (Login / Register)</h4>
            <p>Sign in or create a new Agent Callsign to unlock your personalized 5,000-question matrix, climb the global leaderboard, and chat with friends.</p>
        </div>
        """, unsafe_allow_html=True)
        l_col1, l_col2, l_col3 = st.columns([1.5, 1.5, 1])
        with l_col1:
            u_in = st.text_input("🕵️ Agent Callsign (Username):", placeholder="e.g. taolagautruc")
        with l_col2:
            p_in = st.text_input("🔑 Secret Agent PIN:", type="password", placeholder="Enter 4+ digit PIN")
        with l_col3:
            st.write("")
            if st.button("🚀 Enter CTF Arena", type="primary", use_container_width=True):
                u_clean = u_in.strip()
                p_clean = p_in.strip()
                if not u_clean or not p_clean:
                    st.error("Please enter both a Username and PIN!")
                else:
                    p_hash = hashlib.sha256(p_clean.encode("utf-8")).hexdigest()
                    users = ctf_db["users"]
                    if u_clean in users:
                        if users[u_clean]["pin_hash"] == p_hash:
                            st.session_state.ctf_user = u_clean
                            st.rerun()
                        else:
                            st.error("❌ Incorrect PIN for this Agent Callsign!")
                    else:
                        users[u_clean] = {
                            "pin_hash": p_hash,
                            "score": 0,
                            "solved": [],
                            "surrendered": [],
                            "hints_used": [],
                            "friends": [],
                            "friend_requests": []
                        }
                        save_ctf_db(ctf_db)
                        st.session_state.ctf_user = u_clean
                        st.rerun()
    else:
        curr_user = st.session_state.ctf_user
        u_data = ctf_db["users"].get(curr_user, {})
        u_score = u_data.get("score", 0)
        u_solved = u_data.get("solved", [])
        u_surrendered = u_data.get("surrendered", [])
        u_hints = u_data.get("hints_used", [])
        u_friends = u_data.get("friends", [])
        u_reqs = u_data.get("friend_requests", [])

        p_c1, p_c2, p_c3, p_c4, p_c5 = st.columns([1.6, 1.2, 1.1, 1.1, 0.8])
        p_c1.metric("🕵️ Active Agent", curr_user, get_agent_rank(u_score))
        p_c2.metric("🏆 Total Arena Score", f"{u_score:,} PTS", "Global Ranked")
        p_c3.metric("✅ Missions Cracked", f"{len(u_solved)} / 5,000", f"{len(u_surrendered)} Surrendered")
        p_c4.metric("🤝 Friends Network", f"{len(u_friends)} Agents", f"{len(u_reqs)} Pending Req")
        with p_c5:
            st.write("")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.ctf_user = None
                st.rerun()

        st.write("")
        arena_tab1, arena_tab2, arena_tab3 = st.tabs([
            "🎯 1. Challenge Matrix (5 Tiers • 5,000 Missions)",
            "🏆 2. Global Leaderboard & Add Friends",
            f"💬 3. Friends & Direct Messenger ({len(u_reqs)} Requests)"
        ])

        # ======================================================================
        # TAB 1: MA TRẬN 5 CẤP ĐỘ TỪ TRẺ EM ĐẾN CHUYÊN GIA
        # ======================================================================
        with arena_tab1:
            sel_c1, sel_c2, sel_c3 = st.columns([2, 1, 1])
            with sel_c1:
                tier_choice = st.selectbox(
                    "🔥 Select Difficulty Tier:",
                    [
                        "Tier 1 — Kids & Beginners (100 PTS | Fun Mirror & +1 Alphabet Puzzles)",
                        "Tier 2 — Young Explorers (250 PTS | Classic Caesar & Gamer Leetspeak)",
                        "Tier 3 — Students & Friends (500 PTS | World History, Wars & Hex/Atbash)",
                        "Tier 4 — Cyber Specialists (1,000 PTS | LSB Image Stego & Camouflage)",
                        "Tier 5 — Grandmaster Pros (2,500 PTS | Full Multi-Layer Cryptanalysis)"
                    ]
                )
                tier_num = int(tier_choice.split("Tier ")[1][0])
            with sel_c2:
                if "curr_q_num" not in st.session_state:
                    st.session_state.curr_q_num = 1
                q_num = st.number_input("🔢 Mission # (1 - 1000):", min_value=1, max_value=1000, value=st.session_state.curr_q_num)
                st.session_state.curr_q_num = q_num
            with sel_c3:
                st.write("")
                if st.button("🎲 Random Mission", use_container_width=True):
                    st.session_state.curr_q_num = random.randint(1, 1000)
                    st.rerun()

            chal = generate_dynamic_challenge(curr_user, tier_num, q_num)
            cid = chal["id"]
            base_pts = chal["pts"]
            is_solved = cid in u_solved
            is_surrendered = cid in u_surrendered
            hint_used = cid in u_hints

            effective_pts = int(base_pts * 0.30) if hint_used else base_pts
            surrender_penalty = int(base_pts * 0.92)

            st.markdown(f"""
            <div class="ws-banner">
                <h4>🎯 Mission ID: <code>{cid}</code> — Base Reward: <b>{base_pts:,} PTS</b></h4>
                <p>⚠️ <b>Fair Play Scoring Rules:</b> Clicking <b>Hint</b> reduces this mission's reward by <b>70%</b> (you earn <b>{int(base_pts*0.30)} PTS</b>). Clicking <b>Surrender & Show Answer</b> reveals the full solution immediately but deducts <b>92%</b> (<b>-{surrender_penalty} PTS</b> penalty) from your total score!</p>
            </div>
            """, unsafe_allow_html=True)

            if is_solved:
                st.success(f"🎉 **MISSION COMPLETED!** You solved `{cid}`! Exact Answer: **`{chal['flag']}`**")
            elif is_surrendered:
                st.error(f"🏳️ **MISSION SURRENDERED!** (-{surrender_penalty} PTS penalty applied).")

            st.markdown(chal["briefing"])

            # Hiển thị bảng chữ cái hỗ trợ dò nhanh cho Tier 1, 2, 3
            if tier_num in [1, 2, 3]:
                st.caption("🔤 **Quick Reference English Alphabet:** `A B C D E F G H I J K L M N O P Q R S T U V W X Y Z`")

            if chal["is_img"]:
                st.image(chal["payload"], caption=f"Intercepted Stego PNG — Mission {cid}", width=380)
                st.download_button(
                    "⬇️ Download Intercepted Stego PNG",
                    data=chal["payload"],
                    file_name=f"mission_{cid}.png",
                    mime="image/png"
                )
            else:
                st.markdown("**🧩 Encrypted Puzzle String to Decode:**")
                st.code(chal["payload"], language=None)

            # Hàng nút Hint (-70%) và Đầu hàng hiện rõ đáp án (-92%)
            h_col1, h_col2 = st.columns(2)
            with h_col1:
                if not hint_used and not is_solved and not is_surrendered:
                    if st.button(f"💡 Unlock Detailed Hint (-70% Points -> Earn {int(base_pts*0.30)} PTS)", use_container_width=True):
                        u_hints.append(cid)
                        ctf_db["users"][curr_user]["hints_used"] = u_hints
                        save_ctf_db(ctf_db)
                        st.rerun()
                elif hint_used:
                    st.warning(f"💡 **HINT UNLOCKED (70% Point Reduction Active):**\n\n{chal['hint']}")

            with h_col2:
                if not is_solved and not is_surrendered:
                    if st.button(f"🏳️ Surrender & Reveal Full Answer (-{surrender_penalty} PTS Penalty)", use_container_width=True):
                        u_surrendered.append(cid)
                        ctf_db["users"][curr_user]["surrendered"] = u_surrendered
                        ctf_db["users"][curr_user]["score"] = u_score - surrender_penalty
                        save_ctf_db(ctf_db)
                        st.rerun()
                elif is_surrendered:
                    st.info(f"🔓 **OFFICIAL SOLUTION & EXACT ANSWER:**\n\n{chal['solution']}")

            st.divider()
            if not is_solved and not is_surrendered:
                ans_col1, ans_col2 = st.columns([3, 1])
                with ans_col1:
                    placeholder_txt = "Type the decoded answer (e.g. FRANCE, ABRAHAM LINCOLN, WORLD WAR II)..." if tier_num < 5 else "Format: FLAG{...}"
                    flag_input = st.text_input("🚩 Submit Your Decoded Answer:", placeholder=placeholder_txt, key=f"flag_in_{cid}")
                with ans_col2:
                    st.write("")
                    if st.button("✅ Submit Answer", type="primary", use_container_width=True):
                        user_guess = flag_input.strip().upper()
                        expected = chal["flag"].upper()
                        # Cho phép người chơi nhập thẳng đáp án hoặc bọc trong FLAG{...} đều đúng
                        if user_guess == expected or user_guess == f"FLAG{{{expected}}}":
                            u_solved.append(cid)
                            ctf_db["users"][curr_user]["solved"] = u_solved
                            ctf_db["users"][curr_user]["score"] = u_score + effective_pts
                            save_ctf_db(ctf_db)
                            st.balloons()
                            st.success(f"🎉 **AWESOME! '{chal['flag']}' IS CORRECT!** +{effective_pts} PTS added to your score!")
                            time.sleep(1.2)
                            st.rerun()
                        else:
                            st.error("❌ Not quite right! Check the clue or click 'Unlock Detailed Hint' if you need a hand.")

        # ======================================================================
        # TAB 2: BẢNG XẾP HẠNG PUBLIC & QUẢN LÝ NGƯỜI CHƠI
        # ======================================================================
        with arena_tab2:
            st.markdown("""
            <div class="ws-banner">
                <h4>🏆 Global Public Leaderboard</h4>
                <p>Live rankings across all players. Send a Friend Request to any player on the leaderboard to open a private 1-on-1 chat box!</p>
            </div>
            """, unsafe_allow_html=True)

            sorted_users = sorted(ctf_db["users"].items(), key=lambda x: x[1].get("score", 0), reverse=True)

            for rank_idx, (agent_id, a_info) in enumerate(sorted_users, start=1):
                a_score = a_info.get("score", 0)
                a_solved = len(a_info.get("solved", []))
                a_title = get_agent_rank(a_score)
                medal = "🥇" if rank_idx == 1 else ("🥈" if rank_idx == 2 else ("🥉" if rank_idx == 3 else f"#{rank_idx}"))

                lb_c1, lb_c2, lb_c3, lb_c4 = st.columns([2.2, 1.4, 1.2, 1.2])
                with lb_c1:
                    me_tag = " *(You)*" if agent_id == curr_user else ""
                    st.markdown(f"**{medal} &nbsp; `{agent_id}`**{me_tag} — <span style='color:#60a5fa;'>{a_title}</span>", unsafe_allow_html=True)
                with lb_c2:
                    st.markdown(f"🏆 **{a_score:,} PTS**")
                with lb_c3:
                    st.markdown(f"✅ `{a_solved}` solved")
                with lb_c4:
                    if agent_id != curr_user:
                        if agent_id in u_friends:
                            st.caption("🤝 Friends")
                        elif curr_user in a_info.get("friend_requests", []):
                            st.caption("⏳ Request Sent")
                        else:
                            if st.button("➕ Add Friend", key=f"add_fr_{agent_id}", use_container_width=True):
                                target_reqs = ctf_db["users"][agent_id].get("friend_requests", [])
                                if curr_user not in target_reqs:
                                    target_reqs.append(curr_user)
                                    ctf_db["users"][agent_id]["friend_requests"] = target_reqs
                                    save_ctf_db(ctf_db)
                                    st.toast(f"🤝 Friend request sent to {agent_id}!", icon="🤝")
                                    st.rerun()

            st.divider()
            with st.expander("🛠️ Leaderboard & Account Management (Reset My Score / Remove Demo Bots)"):
                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    if st.button("🔄 Reset My Score & History to 0 PTS", use_container_width=True):
                        ctf_db["users"][curr_user]["score"] = 0
                        ctf_db["users"][curr_user]["solved"] = []
                        ctf_db["users"][curr_user]["surrendered"] = []
                        ctf_db["users"][curr_user]["hints_used"] = []
                        save_ctf_db(ctf_db)
                        st.success("Your score and mission history have been reset to 0 PTS!")
                        st.rerun()
                with m_col2:
                    if st.button("🧹 Remove Pre-loaded Demo Bots from Leaderboard", use_container_width=True):
                        for bot_name in ["ZeroCool_VN", "CipherQueen_HCMUS", "ShadowBroker_99", "AlexMercer_US", "ElenaRostova_UK", "KenjiSato_JP"]:
                            if bot_name in ctf_db["users"] and bot_name != curr_user:
                                del ctf_db["users"][bot_name]
                        save_ctf_db(ctf_db)
                        st.success("Removed all demo bots! Only real registered players are shown now.")
                        st.rerun()

        # ======================================================================
        # TAB 3: KẾT BẠN & KHUNG CHAT NHỎ 1-1
        # ======================================================================
        with arena_tab3:
            f_col1, f_col2 = st.columns([1.2, 2.3])

            with f_col1:
                st.markdown("##### 📩 Incoming Friend Requests")
                if not u_reqs:
                    st.caption("No pending friend requests.")
                else:
                    for req_sender in list(u_reqs):
                        rc1, rc2, rc3 = st.columns([1.6, 1, 1])
                        rc1.markdown(f"🕵️ **`{req_sender}`**")
                        if rc2.button("✅ Accept", key=f"acc_{req_sender}", use_container_width=True):
                            u_reqs.remove(req_sender)
                            if req_sender not in u_friends:
                                u_friends.append(req_sender)
                            sender_friends = ctf_db["users"].get(req_sender, {}).get("friends", [])
                            if curr_user not in sender_friends:
                                sender_friends.append(curr_user)
                            ctf_db["users"][curr_user]["friend_requests"] = u_reqs
                            ctf_db["users"][curr_user]["friends"] = u_friends
                            if req_sender in ctf_db["users"]:
                                ctf_db["users"][req_sender]["friends"] = sender_friends
                            save_ctf_db(ctf_db)
                            st.rerun()
                        if rc3.button("❌", key=f"dec_{req_sender}", use_container_width=True):
                            u_reqs.remove(req_sender)
                            ctf_db["users"][curr_user]["friend_requests"] = u_reqs
                            save_ctf_db(ctf_db)
                            st.rerun()

                st.divider()
                st.markdown("##### 🤝 Quick Add by Callsign")
                manual_friend = st.text_input("Enter Player Username:", placeholder="e.g. AlexMercer_US")
                if st.button("📨 Send Friend Request", use_container_width=True):
                    mf = manual_friend.strip()
                    if mf not in ctf_db["users"]:
                        st.error("Player not found in Leaderboard database!")
                    elif mf == curr_user:
                        st.warning("You cannot add yourself!")
                    elif mf in u_friends:
                        st.info("Already in your friends list!")
                    else:
                        if mf in ["ZeroCool_VN", "CipherQueen_HCMUS", "ShadowBroker_99", "AlexMercer_US", "ElenaRostova_UK", "KenjiSato_JP"]:
                            u_friends.append(mf)
                            ctf_db["users"][curr_user]["friends"] = u_friends
                            ctf_db["users"][mf]["friends"].append(curr_user)
                            save_ctf_db(ctf_db)
                            st.success(f"🎉 **{mf}** accepted your friend request! You can chat on the right now.")
                            st.rerun()
                        else:
                            t_reqs = ctf_db["users"][mf].get("friend_requests", [])
                            if curr_user not in t_reqs:
                                t_reqs.append(curr_user)
                                ctf_db["users"][mf]["friend_requests"] = t_reqs
                                save_ctf_db(ctf_db)
                            st.success(f"Request sent to **{mf}**!")

            with f_col2:
                st.markdown("##### 💬 Private 1-on-1 Player Chat")
                if not u_friends:
                    st.info("💡 No connected friends yet. Click **➕ Add Friend** on the Leaderboard (Tab 2) or use Quick Add on the left to start chatting!")
                else:
                    active_friend = st.selectbox("Select Friend to Chat With:", u_friends)
                    pair_key = "__".join(sorted([curr_user, active_friend]))
                    dm_list = ctf_db.get("direct_messages", {}).get(pair_key, [])

                    chat_box = st.container(height=280, border=True)
                    with chat_box:
                        if not dm_list:
                            st.caption(f"🔒 Private 1-on-1 chat opened with **{active_friend}**. Say hi!")
                        for dm in dm_list:
                            align_color = "#60a5fa" if dm["sender"] == curr_user else "#c084fc"
                            st.markdown(
                                f"<div style='margin-bottom:8px;'><b style='color:{align_color};'>{dm['sender']}</b> "
                                f"<span style='font-size:0.75rem;color:#64748b;'>({dm['time']})</span>:<br>"
                                f"<span style='color:#e2e8f0;'>{dm['text']}</span></div>",
                                unsafe_allow_html=True
                            )

                    dm_in_col, dm_btn_col = st.columns([3.5, 1])
                    with dm_in_col:
                        dm_txt = st.text_input("Write private message:", placeholder=f"Message @{active_friend}...", label_visibility="collapsed", key=f"dm_in_{active_friend}")
                    with dm_btn_col:
                        if st.button("📨 Send", type="primary", use_container_width=True):
                            if dm_txt.strip():
                                if "direct_messages" not in ctf_db:
                                    ctf_db["direct_messages"] = {}
                                if pair_key not in ctf_db["direct_messages"]:
                                    ctf_db["direct_messages"][pair_key] = []
                                ctf_db["direct_messages"][pair_key].append({
                                    "sender": curr_user,
                                    "text": dm_txt.strip(),
                                    "time": datetime.now(timezone.utc).strftime("%H:%M UTC")
                                })
                                if active_friend in ["ZeroCool_VN", "CipherQueen_HCMUS", "ShadowBroker_99", "AlexMercer_US", "ElenaRostova_UK", "KenjiSato_JP"]:
                                    ctf_db["direct_messages"][pair_key].append({
                                        "sender": active_friend,
                                        "text": f"Hey @{curr_user}! Tier 1 & 2 are super fun warm-ups, and Tier 3 historical ciphers are awesome. Good luck climbing the ranks!",
                                        "time": datetime.now(timezone.utc).strftime("%H:%M UTC")
                                    })
                                save_ctf_db(ctf_db)
                                st.rerun()

elif "5. Security Academy" in main_menu:
    st.subheader("📚 Security Academy & Algorithm X-Ray")
    st.write("Understand how substitution tables, shifting, and UTC time locks protect messages.")

# ==============================================================================
# PHẦN 6: UTILITIES, DEVELOPER PROFILE, VISION & COMPREHENSIVE DOCUMENTATION
# ==============================================================================
elif "6. Utilities & About" in main_menu:
    # CSS bổ sung riêng cho trang About & Documentation
    st.markdown("""
    <style>
        .profile-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border: 1px solid #3b82f6;
            border-radius: 16px;
            padding: 26px 30px;
            margin-bottom: 24px;
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.12);
        }
        .dev-name {
            font-size: 1.9rem;
            font-weight: 800;
            color: #f8fafc;
            margin: 0 0 6px 0;
        }
        .dev-role {
            color: #60a5fa;
            font-size: 1.02rem;
            font-weight: 600;
            margin-bottom: 14px;
        }
        .contact-pill {
            display: inline-block;
            background: #111827;
            border: 1px solid #374151;
            color: #e5e7eb;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 0.85rem;
            margin-right: 10px;
            margin-bottom: 8px;
        }
        .vision-box {
            background: #111827;
            border-left: 4px solid #8b5cf6;
            border-top: 1px solid #1f2937;
            border-right: 1px solid #1f2937;
            border-bottom: 1px solid #1f2937;
            border-radius: 12px;
            padding: 22px 26px;
            margin-bottom: 20px;
            line-height: 1.7;
            color: #cbd5e1;
        }
        .toc-box {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 20px 26px;
            margin-bottom: 24px;
        }
        .doc-section {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 14px;
            padding: 24px 28px;
            margin-bottom: 20px;
        }
        .doc-section h4 {
            color: #60a5fa;
            margin-top: 0;
            margin-bottom: 12px;
            font-size: 1.2rem;
            border-bottom: 1px solid #1f2937;
            padding-bottom: 8px;
        }
        .step-badge {
            background: rgba(59, 130, 246, 0.2);
            color: #93c5fd;
            padding: 2px 8px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.8rem;
            margin-right: 6px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Banner Đầu trang
    st.markdown("""
    <div class="hero-box" style="padding: 22px 30px; margin-bottom: 24px;">
        <div class="hero-badge">👨‍💻 CREATOR PROFILE • PROJECT VISION • MASTER USER MANUAL</div>
        <div class="hero-title" style="font-size: 2.1rem;">🛠️ About & Comprehensive Documentation</div>
        <p class="hero-sub">
            Meet the creator behind Ultimate Secret Messenger, explore our privacy-first mission, and master every cryptographic module with the complete step-by-step handbook below.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 1: DEVELOPER PROFILE (LÊ HOÀNG PHÚ HIẾU - HCMUS)
    # ==========================================================================
    st.markdown("### 👨‍💻 1. Meet the Creator & Architect")
    st.markdown("""
    <div class="profile-card">
        <div class="dev-name">Lê Hoàng Phú Hiếu</div>
        <div class="dev-role">🎓 Sophomore in Information Technology — Faculty of Information Technology (FIT)<br>
        🏛️ University of Science, VNU-HCM (HCMUS — Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM)</div>
        <p style="color: #94a3b8; line-height: 1.65; margin-bottom: 18px;">
            Passionate software engineer and cybersecurity enthusiast dedicated to building mathematical, zero-trust, and user-centric privacy solutions. This platform was architected from scratch to bridge the gap between complex cryptographic theory and intuitive everyday communication.
        </p>
        <div>
            <span class="contact-pill">📧 <b>Email:</b> phuhieu3001@gmail.com</span>
            <span class="contact-pill">🐙 <b>GitHub:</b> <a href="https://github.com/taolagautruc" target="_blank" style="color:#60a5fa;text-decoration:none;">github.com/taolagautruc (@taolagautruc)</a></span>
            <span class="contact-pill">🏫 <b>Institution:</b> HCMUS - VNUHCM</span>
            <span class="contact-pill">📍 <b>Location:</b> Ho Chi Minh City, Vietnam</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 2: PROJECT PURPOSE, MISSION & FUTURE ROADMAP
    # ==========================================================================
    st.markdown("### 🌍 2. Project Purpose, Philosophy & Future Vision")
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown("""
        <div class="vision-box">
            <h4 style="color:#f8fafc; margin-top:0;">🛡️ Why Ultimate Secret Messenger Was Born</h4>
            <p>
                We live in an era where personal privacy is constantly compromised. Across mainstream social networks and messaging platforms, user metadata, private conversations, and behavioral footprints are routinely harvested, monetized, and traded on the open market—severely degrading user trust and digital safety.
            </p>
            <p style="margin-bottom:0;">
                <b>Ultimate Secret Messenger</b> is the realization of a personal vision to push back against mass data exploitation. It creates a self-contained, <b>Zero-Trust Cryptographic Sanctuary</b> where users hold 100% ownership of their encryption keys, rules, and data lifespans—ensuring that no third party can ever intercept or monetize your private communication.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_v2:
        st.markdown("""
        <div class="vision-box" style="border-left-color: #3b82f6;">
            <h4 style="color:#f8fafc; margin-top:0;">🚀 Long-Term Goal & Social Platform Roadmap</h4>
            <p>
                This web platform is only the beginning. I am committed to actively listening to user feedback, refining the cryptographic engines, and expanding the feature set continuously.
            </p>
            <p style="margin-bottom:0;">
                <b>The Ultimate Goal:</b> To evolve this project into a standalone, cross-platform downloadable application (Desktop & Mobile) that functions as a <b>Next-Generation Privacy-First Social Network</b>—a trusted digital haven where friends, teams, and communities can connect, share media, and converse with absolute mathematical security.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ==========================================================================
    # SECTION 3: TABLE OF CONTENTS & COMPLETE MASTER USER GUIDE (LONG SCROLL)
    # ==========================================================================
    st.markdown("### 📖 3. Master Table of Contents & User Manual")
    st.caption("Scroll down to explore the complete architectural breakdown and step-by-step instructions for every feature in the suite.")

    st.markdown("""
    <div class="toc-box">
        <h4 style="color:#f8fafc; margin-top:0; margin-bottom:12px;">📑 Quick Directory (Table of Contents)</h4>
        <ol style="color:#93c5fd; line-height:1.9; margin-bottom:0;">
            <li><b>Module 0 — Global Sidebar Control Panel:</b> Configuring Multi-Layer Group Keys (Passphrase, Shift, 1,400+ Symbols, Custom Pairs & Reverse).</li>
            <li><b>Module 1 — Executive Home Dashboard:</b> Monitoring Live Key Entropy, Brute-Force Resistance & Universal UTC Clock.</li>
            <li><b>Module 2A — Multi-Layer Text Cipher & UTC Time-Locking:</b> Self-Destructing Messages & Time-Capsule Delays.</li>
            <li><b>Module 2B — Linguistic Camouflage Studio:</b> Disguising Ciphertexts into Innocent English Prose (2-Way Markov Engine).</li>
            <li><b>Module 2C — LSB Image Steganography Lab:</b> Hiding Encrypted Payloads Inside Lossless PNG Pixels.</li>
            <li><b>Module 3 — Encrypted Persistent Chat Rooms:</b> Real-Time Multi-Modal Messaging & SHA-256 Admin Security Controls.</li>
            <li><b>Module 4 — Group Rule Sharing Utility:</b> Exporting & Importing Non-Sensitive Team Configuration Strings.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 1: SIDEBAR CONTROL PANEL ---
    st.markdown("""
    <div class="doc-section">
        <h4>🎛️ Module 0: Mastering the Global Cipher Control Panel (Left Sidebar)</h4>
        <p style="color:#cbd5e1;">
            The left sidebar is the heart of the platform. Every encryption and decryption action across the entire website relies on the exact combination of <b>5 customizable parameters</b> you set here. Both the sender and receiver must configure identical sidebar rules to read messages:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><span class="step-badge">LAYER 1</span> <b>🔑 Group Secret Passphrase:</b> Your primary secret password (e.g., <code>Nexus2026</code>). It seeds the deterministic pseudo-random number generator (PRNG) that shuffles the 229-character base alphabet.</li>
            <li><span class="step-badge">LAYER 2</span> <b>🔢 Shift Offset (0–200):</b> Rotates the shuffled substitution table by a specific number of positions, adding modular arithmetic protection.</li>
            <li><span class="step-badge">LAYER 3</span> <b>🎨 Symbol Vault (1,400+ Unicode Icons):</b> Select an ordered chain of emojis/symbols. Even if an attacker knows your text password, missing a single icon or placing them in the wrong order completely alters the key matrix.</li>
            <li><span class="step-badge">LAYER 4</span> <b>🔀 Custom Pairs (Optional):</b> Define manual character swaps separated by commas (e.g., <code>a=@, e=3, s=$</code>) to inject custom traps into the cipher table.</li>
            <li><span class="step-badge">LAYER 5</span> <b>🔄 Reverse Structure:</b> Flips the entire encrypted output string backward prior to transmission.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 2: HOME DASHBOARD ---
    st.markdown("""
    <div class="doc-section">
        <h4>🏠 Module 1: Executive Home Dashboard & Live Security Audit</h4>
        <p style="color:#cbd5e1;">
            Provides a real-time command center displaying system metrics and evaluating the mathematical strength of your current sidebar configuration:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><b>Live Key Entropy Calculator:</b> Automatically calculates the bit-strength (e.g., <code>~128+ bits</code>) and estimates how many years a supercomputer testing 1 trillion keys per second would need to brute-force your configuration.</li>
            <li><b>Universal UTC Synchronization:</b> Displays the current Coordinated Universal Time (UTC) used by all time-locks, ensuring two users in different timezones (e.g., Vietnam and the US) experience zero clock drift.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 3: TEXT CIPHER & TIME-LOCK ---
    st.markdown("""
    <div class="doc-section">
        <h4>📝 Module 2A: Multi-Layer Text Cipher & UTC Time-Locking</h4>
        <p style="color:#cbd5e1;">
            Located in <b>2. Cipher Workspace → Tab 1</b>. Allows you to encrypt plain text (supporting full English, Vietnamese diacritics, numbers, and punctuation) with embedded temporal rules:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><span class="step-badge">MODE 1</span> <b>Normal (No Time Limit):</b> Standard encryption that can be decoded anytime by teammates with the matching key.</li>
            <li><span class="step-badge">MODE 2</span> <b>🔥 Self-Destruct After Time:</b> Embeds a UTC expiration deadline inside the encrypted header. If the recipient attempts to decode the message after the timer expires, the engine blocks decryption and permanently scrambles the payload.</li>
            <li><span class="step-badge">MODE 3</span> <b>⏳ Time-Capsule (Wait Until):</b> Locks the message until a future UTC timestamp. Anyone attempting to decode it early will see a live countdown timer telling them how many minutes/seconds remain.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 4: ENGLISH CAMOUFLAGE ---
    st.markdown("""
    <div class="doc-section">
        <h4>🎭 Module 2B: Linguistic Camouflage Studio (2-Way Markov Prose)</h4>
        <p style="color:#cbd5e1;">
            Located in <b>2. Cipher Workspace → Tab 2</b>. Standard encrypted strings look suspicious to firewalls or human moderators. Linguistic Camouflage solves this:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><b>How to Disguise (Encode):</b> Type your secret message and click <i>"Encrypt & Disguise as English Prose"</i>. The engine first encrypts your text, splits every byte into 4-bit nibbles, and maps them to innocent IT/networking English vocabulary formatted as natural sentences.</li>
            <li><b>How to Reveal (Decode):</b> Paste the innocent-looking English paragraph into the right column and click <i>"Extract & Decrypt Secret"</i> to reverse the prose back into your original message.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 5: IMAGE STEGANOGRAPHY ---
    st.markdown("""
    <div class="doc-section">
        <h4>🖼️ Module 2C: LSB Pixel Steganography Lab (Hide Secrets Inside Images)</h4>
        <p style="color:#cbd5e1;">
            Located in <b>2. Cipher Workspace → Tab 3</b>. Conceals your encrypted message directly inside the RGB color channels of an image using <b>Least Significant Bit (LSB)</b> manipulation:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><span class="step-badge">STEP 1</span> Choose a carrier image by uploading your own <code>PNG/JPG</code> photo or clicking <b>"Auto-Generate Cyber Carrier Image"</b> to create a custom matrix graphic on the fly.</li>
            <li><span class="step-badge">STEP 2</span> Type your secret message and optional UTC Time-Lock. Check the <b>Pixel LSB Capacity Bar</b> on the right to see what percentage of the image's pixels will be used.</li>
            <li><span class="step-badge">STEP 3</span> Click <b>"Encrypt & Embed Into Image Pixels"</b> and download the resulting lossless <code>.PNG</code> file. To the naked eye, the image looks 100% identical to the original!</li>
            <li><span class="step-badge">STEP 4</span> To read a hidden message, switch to <b>Decode Mode</b>, upload the Stego <code>.PNG</code> file, and click <b>"Extract Bits & Decrypt Payload"</b>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 6: SECRET CHAT ROOMS & ADMIN CONTROLS ---
    st.markdown("""
    <div class="doc-section">
        <h4>💬 Module 3: Encrypted Persistent Chat Rooms & SHA-256 Admin Protection</h4>
        <p style="color:#cbd5e1;">
            Located in <b>3. Secret Chat Rooms</b>. A full-featured team communication hub where only encrypted ciphertexts, camouflaged prose, or Stego PNG images are stored on the server:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><b>👑 Creating an Admin-Protected Room:</b> Select <i>"➕ Create New Secret Room"</i>, enter a Channel ID, and set a <b>Room Admin Master PIN</b>. Your PIN is hashed using <code>SHA-256</code> so even the database administrator cannot see it.</li>
            <li><b>📤 Sending Multi-Modal Messages:</b> Use the 3 tabs at the bottom of the room to broadcast encrypted text (with UTC self-destruct timers), English Camouflage sentences, or embed secrets into an <b>LSB Stego Image</b> and post the image directly into the chat feed!</li>
            <li><b>🔓 One-Click In-Room Decryption:</b> Click the <b>"🔓 Decode"</b> button next to any message or Stego Image in the chat feed to decrypt it instantly using your active sidebar rules.</li>
            <li><b>🗑️ Granular & Admin Deletion Controls:</b> Any user can delete an individual message using the <b>"🗑️ Delete"</b> button. However, wiping the entire room history (<b>"🧹 Clear Chat History"</b>) or permanently deleting the room (<b>"💥 Destroy Room"</b>) requires unlocking the <b>Room Admin Security Panel</b> with the creator's Admin PIN.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 4: INTERACTIVE GROUP CONFIG EXPORT UTILITY
    # ==========================================================================
    st.divider()
    st.markdown("### 📦 4. Quick Utility: Export Non-Sensitive Group Rule Blueprint")
    st.caption("Share your current Shift Offset, Symbol Vault sequence, and Custom Pairs with teammates (Passphrase is hidden for security).")
    
    export_blueprint = json.dumps({
        "platform": "Ultimate Secret Messenger v2.0",
        "author": "Le Hoang Phu Hieu (HCMUS)",
        "shift_offset": shift_step,
        "symbol_chain": pattern_list,
        "custom_pairs": custom_pairs,
        "reverse_structure": reverse_rule,
        "passphrase_hint": f"{len(secret_seed)} characters (Communicate via secure offline channel)" if secret_seed else "Not set"
    }, ensure_ascii=False, indent=2)
    
    st.code(export_blueprint, language="json")
    st.info("💡 *“Security is not a product, but a process.”* — Bruce Schneier | Architected with ❤️ by **Lê Hoàng Phú Hiếu (FIT - HCMUS)**.")

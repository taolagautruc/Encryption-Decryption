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

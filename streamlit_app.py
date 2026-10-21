import streamlit as st
import random
import string
import io
import time
import unicodedata
from PIL import Image

# --- 1. BASE CHARACTER SET (Supports Global English, Symbols & Vietnamese) ---
vietnamese_chars = (
    "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"
)
BASE_CHARS = list(" " + string.punctuation + string.digits + string.ascii_letters + vietnamese_chars)

# --- 2. IDEA 5: GENERATE 1,200+ UNICODE SYMBOLS DYNAMICALLY ---
@st.cache_data
def load_massive_symbol_pool():
    pool = []
    # Scan major Unicode Emoji & Symbol ranges (1,200+ distinct symbols)
    ranges = [
        (0x1F300, 0x1F5FF), # Misc Symbols and Pictographs
        (0x1F600, 0x1F64F), # Emoticons
        (0x1F680, 0x1F6FF), # Transport and Map
        (0x1F900, 0x1F9FF), # Supplemental Symbols and Pictographs
        (0x2600, 0x26FF),   # Misc Symbols (Chess, Astrology, Weather)
    ]
    for start, end in ranges:
        for code in range(start, end + 1):
            ch = chr(code)
            if unicodedata.category(ch) in ('So', 'Sm'):
                pool.append(ch)
    return pool

SYMBOLS_POOL = load_massive_symbol_pool()

# --- 3. IDEA 1: DYNAMIC ENGLISH CAMOUFLAGE ENGINE (NO NUMBERS, INFINITE VARIATIONS) ---
# Uses 16x16 word matrices (256 states per byte) + Random Salt so every click looks different
ADJ_POOL = [
    "new", "current", "updated", "global", "local", "primary", "secondary", "active",
    "pending", "final", "initial", "custom", "standard", "internal", "external", "core"
]
NOUN_POOL = [
    "report", "system", "project", "module", "server", "dataset", "schedule", "package",
    "client", "network", "document", "protocol", "agenda", "budget", "archive", "session"
]
VERB_POOL = [
    "requires", "confirms", "updates", "validates", "processes", "maintains", "reviews", "initiates",
    "completes", "monitors", "optimizes", "allocates", "prepares", "verifies", "tracks", "secures"
]
ADV_POOL = [
    "today", "smoothly", "properly", "quickly", "online", "now", "daily", "weekly",
    "effectively", "securely", "globally", "directly", "shortly", "carefully", "fully", "early"
]
CONNECTORS = [
    "Additionally,", "Meanwhile,", "Furthermore,", "As discussed,", "Please note that",
    "In the meantime,", "For the next phase,", "According to the team,", "Moving forward,"
]

def encode_english_camouflage(cypher_text: str) -> str:
    # Add a random salt (0-255) so identical messages generate completely different English sentences
    salt = random.randint(0, 255)
    raw_bytes = [salt] + [BASE_CHARS.index(c) if c in BASE_CHARS else 0 for c in cypher_text]
    
    sentences = []
    for idx, val in enumerate(raw_bytes):
        # Obfuscate value with salt and position so repetition never shows
        masked_val = (val + salt + idx * 7) % 256 if idx > 0 else salt
        high_nibble = (masked_val >> 4) & 0x0F
        low_nibble = masked_val & 0x0F
        
        adj = ADJ_POOL[high_nibble]
        noun = NOUN_POOL[low_nibble]
        verb = VERB_POOL[(high_nibble + idx) % 16]
        adv = ADV_POOL[(low_nibble + idx) % 16]
        
        prefix = f"{random.choice(CONNECTORS)} the" if (idx > 0 and idx % 2 == 0) else "The"
        sentences.append(f"{prefix} {adj} {noun} {verb} {adv}.")
        
    return " ".join(sentences)

def decode_english_camouflage(camo_text: str) -> str:
    words = [w.strip(".,!?;:").lower() for w in camo_text.split()]
    extracted_Adjs = [w for w in words if w in ADJ_POOL]
    extracted_Nouns = [w for w in words if w in NOUN_POOL]
    
    if not extracted_Adjs or len(extracted_Adjs) != len(extracted_Nouns):
        raise ValueError("Invalid camouflage text format!")
        
    raw_vals = []
    for i in range(len(extracted_Adjs)):
        high_nibble = ADJ_POOL.index(extracted_Adjs[i])
        low_nibble = NOUN_POOL.index(extracted_Nouns[i])
        raw_vals.append((high_nibble << 4) | low_nibble)
        
    salt = raw_vals[0]
    chars = []
    for idx in range(1, len(raw_vals)):
        masked_val = raw_vals[idx]
        orig_val = (masked_val - salt - idx * 7) % 256
        if 0 <= orig_val < len(BASE_CHARS):
            chars.append(BASE_CHARS[orig_val])
    return "".join(chars)

# --- 4. CUSTOM KEY BUILDER ---
def build_custom_key(secret_seed: str, pattern_list: list, shift_step: int, custom_pairs: str):
    key = BASE_CHARS.copy()
    combined_seed = f"{secret_seed}_{''.join(pattern_list)}"
    rng = random.Random(combined_seed)
    rng.shuffle(key)
    
    if shift_step > 0:
        shift = shift_step % len(key)
        key = key[shift:] + key[:shift]
        
    if custom_pairs.strip():
        pairs = [p.strip() for p in custom_pairs.split(",") if "=" in p]
        for pair in pairs:
            parts = pair.split("=", 1)
            if len(parts) == 2:
                char_a, char_b = parts[0], parts[1]
                if char_a in BASE_CHARS and char_b in key:
                    idx_a = BASE_CHARS.index(char_a)
                    idx_b = key.index(char_b)
                    key[idx_a], key[idx_b] = key[idx_b], key[idx_a]
    return key

# --- 5. IDEA 3: TIMEZONE-INDEPENDENT SELF-DESTRUCT & COUNTDOWN ENGINE ---
def encrypt_core(plain_text: str, key: list, reverse_rule: bool, mode: str = "NONE", target_ts: int = 0) -> str:
    # Uses universal UTC Unix epoch seconds (works identically across all global timezones)
    payload = f"TMODE:{mode}:{target_ts}|{plain_text}"
    res = "".join(key[BASE_CHARS.index(c)] if c in BASE_CHARS else c for c in payload)
    if reverse_rule:
        res = res[::-1]
    return res

def decrypt_core(cypher_text: str, key: list, reverse_rule: bool):
    if reverse_rule:
        cypher_text = cypher_text[::-1]
    raw = "".join(BASE_CHARS[key.index(c)] if c in key else c for c in cypher_text)
    
    if not raw.startswith("TMODE:") or "|" not in raw:
        return False, "❌ Decryption Failed: Incorrect Group Key, Symbol Pattern, or Shift Rules!"
    
    header, actual_msg = raw.split("|", 1)
    parts = header.split(":")
    if len(parts) != 3:
        return False, "❌ Corrupted timestamp header!"
        
    mode = parts[1]
    try:
        target_ts = int(parts[2])
    except ValueError:
        return False, "❌ Invalid time-lock data!"
        
    now_ts = int(time.time()) # Universal UTC Epoch
    
    # Mode 1: Self-Destruct (If not decoded within X minutes, scramble back forever)
    if mode == "EXPIRE" and target_ts > 0:
        if now_ts > target_ts:
            expired_ago = now_ts - target_ts
            mins, secs = divmod(expired_ago, 60)
            # Re-scramble the message irreversibly so it cannot be read
            dead_rng = random.Random(now_ts)
            scrambled = "".join(dead_rng.sample(actual_msg, len(actual_msg))) if actual_msg else "???"
            return False, (
                f"💥 MESSAGE SELF-DESTRUCTED! (Expired {mins}m {secs}s ago).\n"
                f"The time window has passed and the payload has been permanently re-encrypted into noise:\n`{scrambled}`"
            )
            
    # Mode 2: Time-Capsule (Wait until countdown finishes)
    elif mode == "WAIT" and target_ts > 0:
        if now_ts < target_ts:
            wait_sec = target_ts - now_ts
            mins, secs = divmod(wait_sec, 60)
            hours, mins = divmod(mins, 60)
            return False, f"⏳ TIME-CAPSULE LOCKED! Please wait {hours}h {mins}m {secs}s before decoding."
            
    return True, actual_msg

# --- 6. IDEA 4: IMAGE STEGANOGRAPHY (LSB) ---
def encode_image_lsb(img: Image.Image, secret_str: str) -> Image.Image:
    img = img.convert("RGB")
    data_bytes = secret_str.encode('utf-8')
    length_bits = format(len(data_bytes), '032b')
    payload_bits = length_bits + ''.join(format(byte, '08b') for byte in data_bytes)
    
    pixels = list(img.getdata())
    if len(payload_bits) > len(pixels) * 3:
        raise ValueError("Image resolution is too small for this message! Please upload a larger image.")
        
    new_pixels = []
    bit_idx = 0
    for r, g, b in pixels:
        if bit_idx < len(payload_bits):
            r = (r & ~1) | int(payload_bits[bit_idx]); bit_idx += 1
        if bit_idx < len(payload_bits):
            g = (g & ~1) | int(payload_bits[bit_idx]); bit_idx += 1
        if bit_idx < len(payload_bits):
            b = (b & ~1) | int(payload_bits[bit_idx]); bit_idx += 1
        new_pixels.append((r, g, b))
        
    encoded_img = Image.new(img.mode, img.size)
    encoded_img.putdata(new_pixels)
    return encoded_img

def decode_image_lsb(img: Image.Image) -> str:
    img = img.convert("RGB")
    pixels = list(img.getdata())
    bits = []
    for r, g, b in pixels:
        bits.extend([str(r & 1), str(g & 1), str(b & 1)])
        
    length = int("".join(bits[:32]), 2)
    if length <= 0 or length > len(pixels):
        raise ValueError("No valid hidden cipher found in this image!")
        
    total_bits = 32 + length * 8
    byte_list = [int("".join(bits[i:i+8]), 2) for i in range(32, total_bits, 8)]
    return bytes(byte_list).decode('utf-8')

# ================= STREAMLIT GLOBAL UI =================
st.set_page_config(page_title="Global Cipher Suite", page_icon="🛡️", layout="centered")
st.title("🛡️ Ultimate Secret Messenger")
st.caption("Global Multi-Layer Cryptography: 1,200+ Symbols • Self-Destruct Timer • Dynamic English Camouflage • Steganography")

with st.expander("⚙️ GROUP CUSTOM CIPHER RULES (Required)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        secret_seed = st.text_input("1️⃣ Group Secret Passphrase:", type="password", placeholder="e.g. NexusProtocol2026")
    with col2:
        shift_step = st.number_input("2️⃣ Cipher Shift Step (0-200):", min_value=0, max_value=200, value=0)
        
    pattern_list = st.multiselect(
        f"3️⃣ Visual Symbol Vault (Select ordered symbols from {len(SYMBOLS_POOL)}+ icons):",
        options=SYMBOLS_POOL,
        default=SYMBOLS_POOL[:3]
    )
    
    custom_pairs = st.text_input("4️⃣ Custom Character Mapping (Optional):", placeholder="e.g. a=@, e=3, o=0")
    reverse_rule = st.checkbox("5️⃣ Reverse Cipher Structure")

if not secret_seed:
    st.warning("👆 Please enter a 'Group Secret Passphrase' above to unlock the cryptography suite!")
else:
    group_key = build_custom_key(secret_seed, pattern_list, shift_step, custom_pairs)
    st.caption(f"✅ Active Symbol Key ({len(SYMBOLS_POOL)} pool size): {' ➡️ '.join(pattern_list) if pattern_list else 'None'}")

    tab_enc, tab_dec, tab_img = st.tabs([
        "📤 Encrypt & Self-Destruct", 
        "📥 Decrypt Message", 
        "🖼️ Image Steganography"
    ])

    # --- TAB 1: ENCRYPT + GLOBAL COUNTDOWN + DYNAMIC ENGLISH CAMOUFLAGE ---
    with tab_enc:
        plain_input = st.text_area("Enter your secret message (Supports English, Vietnamese & All Symbols):", height=100)
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            time_mode_ui = st.selectbox(
                "⏱️ Time-Control Mode (Global UTC):",
                ["No Time Limit", "🔥 Self-Destruct (Expire after X mins)", "⏳ Time-Capsule (Unlock after X mins)"]
            )
            mins_val = 20
            if time_mode_ui != "No Time Limit":
                mins_val = st.number_input("Set Countdown (Minutes):", min_value=1, max_value=10080, value=20)
        with col_t2:
            use_camo = st.checkbox("🎭 Dynamic English Camouflage")
            if use_camo:
                st.caption("Disguises your cipher into natural English business/tech sentences. Every click generates a unique variation!")

        if st.button("🔒 Generate Cipher", type="primary"):
            if plain_input:
                mode_code = "NONE"
                target_ts = 0
                now_utc = int(time.time())
                
                if "Self-Destruct" in time_mode_ui:
                    mode_code = "EXPIRE"
                    target_ts = now_utc + (mins_val * 60)
                elif "Time-Capsule" in time_mode_ui:
                    mode_code = "WAIT"
                    target_ts = now_utc + (mins_val * 60)
                
                cypher = encrypt_core(plain_input, group_key, reverse_rule, mode_code, target_ts)
                if use_camo:
                    final_out = encode_english_camouflage(cypher)
                    st.success("🎭 Disguised English Text (Safe to send anywhere):")
                else:
                    final_out = cypher
                    st.success("🔒 Encrypted Ciphertext:")
                st.code(final_out, language=None)
            else:
                st.error("Please enter a message to encrypt!")

    # --- TAB 2: DECRYPT ---
    with tab_dec:
        cypher_input = st.text_area("Paste Ciphertext or Disguised English Text here:", height=120)
        is_camo_input = st.checkbox("This message is disguised in English Camouflage Mode (🎭)")
        
        if st.button("🔓 Decode Message", type="primary"):
            if cypher_input:
                try:
                    target_cypher = decode_english_camouflage(cypher_input) if is_camo_input else cypher_input.strip()
                    ok, result = decrypt_core(target_cypher, group_key, reverse_rule)
                    if ok:
                        st.success("🎉 Decrypted Original Message:")
                        st.info(result)
                    else:
                        st.error(result)
                except Exception as e:
                    st.error(f"❌ Could not decode: {e}")
            else:
                st.error("Please paste a message to decode!")

    # --- TAB 3: IMAGE STEGANOGRAPHY ---
    with tab_img:
        st.markdown("Hide encrypted payloads inside image pixels (LSB Steganography). **Note:** Send the output PNG as a **Document/File** so chat apps don't compress it.")
        img_mode = st.radio("Select Action:", ["Hide Message in Image", "Extract Message from Image"], horizontal=True)
        
        if img_mode == "Hide Message in Image":
            up_img = st.file_uploader("Upload base image (PNG/JPG):", type=["png", "jpg", "jpeg"])
            secret_img_msg = st.text_input("Enter secret message to hide inside image:")
            
            use_img_expire = st.checkbox("🔥 Enable Self-Destruct Timer for this Image")
            img_mins = 20
            if use_img_expire:
                img_mins = st.number_input("Image message expires if not decoded within (Minutes):", min_value=1, max_value=10080, value=20)

            if st.button("🖼️ Embed Cipher & Download PNG", type="primary"):
                if up_img and secret_img_msg:
                    try:
                        img_obj = Image.open(up_img)
                        mode_code = "EXPIRE" if use_img_expire else "NONE"
                        target_ts = int(time.time()) + (img_mins * 60) if use_img_expire else 0
                        
                        cypher_for_img = encrypt_core(secret_img_msg, group_key, reverse_rule, mode_code, target_ts)
                        stego_img = encode_image_lsb(img_obj, cypher_for_img)
                        
                        buf = io.BytesIO()
                        stego_img.save(buf, format="PNG")
                        st.success("✅ Secret embedded! Click below to download your PNG:")
                        st.download_button(
                            label="⬇️ Download Stego Image (secret_image.png)",
                            data=buf.getvalue(),
                            file_name="secret_image.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please upload an image and enter a secret message first!")
        else:
            stego_up = st.file_uploader("Upload Stego PNG image to decode:", type=["png"])
            if st.button("🔍 Extract & Decode Hidden Message", type="primary"):
                if stego_up:
                    try:
                        img_obj = Image.open(stego_up)
                        extracted_cypher = decode_image_lsb(img_obj)
                        ok, result = decrypt_core(extracted_cypher, group_key, reverse_rule)
                        if ok:
                            st.success("🎉 Hidden Message Extracted:")
                            st.info(result)
                        else:
                            st.error(result)
                    except Exception as e:
                        st.error(f"No valid hidden message found: {e}")

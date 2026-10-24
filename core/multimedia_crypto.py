import streamlit as st
import math
import wave
import struct
import io
import base64
import random
from collections import Counter
from PIL import Image, ImageDraw

# ==============================================================================
# 1. AUDIO CRYPTOGRAPHY & 16-BIT PCM WAV LSB STEGANOGRAPHY ENGINE
# ==============================================================================
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', ' ': '/'
}

AUDIO_DELIM = "<<END_AUDIO>>"

def text_to_morse(text: str) -> str:
    return " ".join(MORSE_CODE_DICT.get(c, "") for c in text.upper() if c in MORSE_CODE_DICT)

def generate_morse_wav_bytes(text: str, freq: int = 750, sample_rate: int = 22050) -> bytes:
    """Sinh file âm thanh .WAV phát tín hiệu Morse (Bíp ngắn = Dot, Bíp dài = Dash)."""
    morse_str = text_to_morse(text)
    dot_dur = 0.07  # 70ms cho 1 chấm (.)
    samples = []

    def append_tone(duration_sec: float, is_sound: bool):
        n_samples = int(sample_rate * duration_sec)
        for i in range(n_samples):
            if is_sound:
                val = int(16000.0 * math.sin(2.0 * math.pi * freq * (i / sample_rate)))
            else:
                val = 0
            samples.append(val)

    for ch in morse_str:
        if ch == '.':
            append_tone(dot_dur, True)
            append_tone(dot_dur, False)
        elif ch == '-':
            append_tone(dot_dur * 3, True)
            append_tone(dot_dur, False)
        elif ch == ' ':
            append_tone(dot_dur * 2, False)
        elif ch == '/':
            append_tone(dot_dur * 4, False)

    if not samples:
        append_tone(0.5, False)

    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
    return buf.getvalue()

def encode_audio_lsb_wav(secret_payload: str, duration_sec: float = 3.5, sample_rate: int = 22050) -> bytes:
    """
    Tạo một đoạn âm thanh sóng mang (Cyber Ambient Chord) và giấu từng bit mật mã
    vào Least Significant Bit (LSB) của mẫu âm thanh 16-bit PCM.
    """
    full_bytes = (secret_payload + AUDIO_DELIM).encode("utf-8")
    bits = "".join(f"{b:08b}" for b in full_bytes)

    total_samples = max(int(sample_rate * duration_sec), len(bits) + 1000)
    samples = []

    for i in range(total_samples):
        t = i / sample_rate
        # Tạo âm thanh hợp âm êm dịu (440Hz + 554Hz) làm sóng mang
        carrier_val = int(8000 * math.sin(2 * math.pi * 440 * t) + 6000 * math.sin(2 * math.pi * 554.37 * t))
        if i < len(bits):
            bit_val = int(bits[i])
            carrier_val = (carrier_val & ~1) | bit_val
        samples.append(max(-32767, min(32767, carrier_val)))

    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
    return buf.getvalue()

def decode_audio_lsb_wav(wav_bytes: bytes) -> tuple[bool, str]:
    """Trích xuất các bit LSB từ file âm thanh .WAV 16-bit PCM."""
    try:
        buf = io.BytesIO(wav_bytes)
        with wave.open(buf, 'rb') as wf:
            n_frames = wf.getnframes()
            raw_frames = wf.readframes(n_frames)
            samples = struct.unpack('<' + 'h' * (len(raw_frames) // 2), raw_frames)

        bits = [str(s & 1) for s in samples]
        byte_arr = bytearray()
        delim_bytes = AUDIO_DELIM.encode("utf-8")
        delim_len = len(delim_bytes)

        for i in range(0, len(bits) - 7, 8):
            b_val = int("".join(bits[i:i+8]), 2)
            byte_arr.append(b_val)
            if len(byte_arr) >= delim_len and byte_arr[-delim_len:] == delim_bytes:
                return True, byte_arr[:-delim_len].decode("utf-8")
        return False, "❌ No hidden LSB audio payload detected in this .WAV file!"
    except Exception as e:
        return False, f"❌ Audio decoding error: {str(e)}"


# ==============================================================================
# 2. VISUAL CRYPTOGRAPHY ENGINE (NAOR-SHAMIR 2-SHARE PIXEL SPLITTING)
# ==============================================================================
def generate_visual_crypto_shares(secret_code: str) -> tuple[Image.Image, Image.Image, Image.Image]:
    """
    Thuật toán Mật mã Thị giác của Naor-Shamir:
    Tách 1 ảnh đen trắng chứa chữ bí mật thành 2 tấm ảnh nhiễu hạt (Share 1 & Share 2).
    Nhìn từng tấm riêng lẻ chỉ thấy nhiễu ngẫu nhiên 50/50, nhưng khi xếp chồng lên nhau sẽ hiện rõ chữ!
    """
    clean_txt = secret_code.strip().upper()[:8] or "SECRET"
    base_w, base_h = 130, 42

    # Vẽ chữ gốc lên khung trắng đen
    src_img = Image.new("1", (base_w, base_h), 1)  # 1 = Trắng, 0 = Đen
    draw = ImageDraw.Draw(src_img)
    draw.rectangle([(2, 2), (base_w - 3, base_h - 3)], outline=0)
    draw.text((16, 15), clean_txt, fill=0)

    # Mỗi điểm ảnh gốc được mở rộng thành khối 2x2 sub-pixels (kích thước x2)
    out_w, out_h = base_w * 2, base_h * 2
    share1 = Image.new("RGB", (out_w, out_h), (255, 255, 255))
    share2 = Image.new("RGB", (out_w, out_h), (255, 255, 255))
    overlay = Image.new("RGB", (out_w, out_h), (255, 255, 255))

    s1_px = share1.load()
    s2_px = share2.load()
    ov_px = overlay.load()

    # Các mẫu khối 2x2 chuẩn (2 điểm đen, 2 điểm trắng)
    patterns = [
        [(0, 1), (1, 0)],
        [(1, 0), (0, 1)],
        [(0, 0), (1, 1)],
        [(1, 1), (0, 0)],
        [(0, 1), (0, 1)],
        [(1, 0), (1, 0)]
    ]

    for y in range(base_h):
        for x in range(base_w):
            pixel = src_img.getpixel((x, y))
            pat1 = random.choice(patterns)
            if pixel == 1:
                # Nếu điểm gốc là Trắng: Share 2 giống hệt Share 1
                pat2 = pat1
            else:
                # Nếu điểm gốc là Đen (Chữ): Share 2 là bản đảo ngược của Share 1 -> Khi chồng lên nhau sẽ đen đặc 100%!
                pat2 = [[1 - pat1[0][0], 1 - pat1[0][1]], [1 - pat1[1][0], 1 - pat1[1][1]]]

            for dy in range(2):
                for dx in range(2):
                    b1 = pat1[dy][dx]
                    b2 = pat2[dy][dx]
                    # Chồng 2 tấm phim: chỉ trắng khi cả 2 cùng trắng (b1 & b2 == 1)
                    b_ov = 1 if (b1 == 1 and b2 == 1) else 0

                    c1 = (240, 249, 255) if b1 == 1 else (15, 23, 42)
                    c2 = (240, 249, 255) if b2 == 1 else (15, 23, 42)
                    c_ov = (240, 249, 255) if b_ov == 1 else (220, 38, 38)  # Chữ hiện lên màu Đỏ Đậm nổi bật

                    s1_px[x * 2 + dx, y * 2 + dy] = c1
                    s2_px[x * 2 + dx, y * 2 + dy] = c2
                    ov_px[x * 2 + dx, y * 2 + dy] = c_ov

    # Phóng to x2 bằng Nearest Neighbor để nhìn rõ từng hạt pixel sắc nét trên màn hình
    return (
        share1.resize((out_w * 2, out_h * 2), Image.NEAREST),
        share2.resize((out_w * 2, out_h * 2), Image.NEAREST),
        overlay.resize((out_w * 2, out_h * 2), Image.NEAREST)
    )


# ==============================================================================
# 3. AUTOMATED FORENSIC CIPHER IDENTIFIER & CRYPTANALYSIS ENGINE
# ==============================================================================
def calculate_shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())

def calculate_ioc(s: str) -> float:
    """Tính chỉ số trùng khớp (Index of Coincidence) để phân biệt ngôn ngữ tự nhiên và mật mã đa bảng."""
    letters = [c.upper() for c in s if "A" <= c.upper() <= "Z"]
    n = len(letters)
    if n <= 1:
        return 0.0
    counts = Counter(letters)
    num = sum(v * (v - 1) for v in counts.values())
    return num / (n * (n - 1))

def auto_crack_unknown_cipher(mystery_text: str) -> list[tuple[str, str]]:
    """Tự động thử nghiệm giải mã qua Base64, Hex, Binary, Atbash, Reverse và 25 khóa Caesar."""
    txt = mystery_text.strip()
    results = []

    # 1. Thử Base64
    try:
        if len(txt) % 4 == 0 and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r" for c in txt):
            b64_dec = base64.b64decode(txt).decode("utf-8")
            if b64_dec.isprintable():
                results.append(("🎯 Base64 Decoded", b64_dec))
    except Exception:
        pass

    # 2. Thử Hexadecimal
    try:
        clean_hex = txt.replace(" ", "").replace("0x", "")
        if len(clean_hex) >= 4 and len(clean_hex) % 2 == 0 and all(c in "0123456789abcdefABCDEF" for c in clean_hex):
            hex_dec = bytes.fromhex(clean_hex).decode("utf-8")
            if hex_dec.isprintable():
                results.append(("🎯 Hexadecimal Byte Stream", hex_dec))
    except Exception:
        pass

    # 3. Thử Binary 8-bit
    try:
        clean_bin = txt.replace(" ", "")
        if len(clean_bin) >= 8 and len(clean_bin) % 8 == 0 and set(clean_bin).issubset({"0", "1"}):
            chars = [chr(int(clean_bin[i:i+8], 2)) for i in range(0, len(clean_bin), 8)]
            bin_dec = "".join(chars)
            if bin_dec.isprintable():
                results.append(("🎯 8-Bit ASCII Binary", bin_dec))
    except Exception:
        pass

    # 4. Thử Reverse (Đảo ngược chuỗi)
    results.append(("🔄 Reversed String (Right-to-Left)", txt[::-1]))

    # 5. Thử Atbash Mirror Alphabet
    atbash_out = []
    for ch in txt:
        if "A" <= ch <= "Z":
            atbash_out.append(chr(ord("Z") - (ord(ch) - ord("A"))))
        elif "a" <= ch <= "z":
            atbash_out.append(chr(ord("z") - (ord(ch) - ord("a"))))
        else:
            atbash_out.append(ch)
    results.append(("🪞 Atbash Mirror Alphabet", "".join(atbash_out)))

    # 6. Quét toàn bộ 25 bước dịch chuyển Caesar (Chấm điểm dựa trên từ vựng phổ biến)
    common_words = {"THE", "AND", "ARE", "YOU", "FOR", "NOT", "WITH", "SECRET", "FLAG", "MEET", "ATTACK", "SAFE", "CODE", "HELLO", "WORLD"}
    caesar_candidates = []
    for s in range(1, 26):
        shifted = []
        for ch in txt:
            if "A" <= ch <= "Z":
                shifted.append(chr((ord(ch) - 65 - s) % 26 + 65))
            elif "a" <= ch <= "z":
                shifted.append(chr((ord(ch) - 97 - s) % 26 + 97))
            else:
                shifted.append(ch)
        cand_str = "".join(shifted)
        upper_words = set(cand_str.upper().split())
        hits = len(upper_words.intersection(common_words))
        caesar_candidates.append((hits, s, cand_str))

    caesar_candidates.sort(key=lambda x: x[0], reverse=True)
    for hits, s, cand_str in caesar_candidates[:5]:
        tag = f"🔥 Caesar Shift -{s} (High Confidence Match!)" if hits > 0 else f"🔤 Caesar Shift -{s} (ROT-{s})"
        results.append((tag, cand_str))

    return results


# ==============================================================================
# GIAO DIỆN HIỂN THỊ 3 PHÒNG LAB CỦA TRỤ CỘT 2
# ==============================================================================
def render_pillar2_multimedia_labs(encrypt_core_fn, decrypt_core_fn, group_key: list, reverse_rule: bool):
    p2_tab1, p2_tab2, p2_tab3 = st.tabs([
        "🎵 4. Audio Steganography & Morse Lab (.WAV)",
        "👁️ 5. Visual Cryptography (2-Share Split)",
        "🤖 6. AI / Auto Forensic Cipher Identifier"
    ])

    # --- TAB 4: AUDIO STEGANOGRAPHY & MORSE GENERATOR ---
    with p2_tab1:
        st.markdown("""
        <div class="ws-banner">
            <h4>🎵 Audio Steganography (16-Bit PCM WAV LSB) & Morse Wave Synthesizer</h4>
            <p>Convert secret messages into playable Morse Code audio waves, or hide encrypted payloads invisibly inside the Least Significant Bits of a .WAV audio file!</p>
        </div>
        """, unsafe_allow_html=True)

        aud_mode = st.radio(
            "Select Audio Lab Operation:",
            [
                "📻 1. Generate Playable Morse Code Audio (.WAV)",
                "🎙️ 2. Hide Encrypted Payload Inside Audio Samples (WAV LSB Encode)",
                "🎧 3. Extract & Decrypt Secret From Audio File (WAV LSB Decode)"
            ],
            horizontal=True
        )
        st.divider()

        if "1. Generate" in aud_mode:
            c_m1, c_m2 = st.columns([2, 1])
            with c_m1:
                morse_in = st.text_input("Enter Plaintext for Morse Audio Transmission:", value="SOS MEET AT MIDNIGHT")
            with c_m2:
                tone_hz = st.slider("Radio Carrier Frequency (Hz):", 400, 1200, 750, step=50)

            if st.button("📻 Synthesize Morse Code Radio Wave (.WAV)", type="primary"):
                if morse_in.strip():
                    morse_dots = text_to_morse(morse_in.strip())
                    wav_data = generate_morse_wav_bytes(morse_in.strip(), freq=tone_hz)
                    st.success("✅ **Morse Audio Wave Synthesized!** Listen directly below or download:")
                    st.code(morse_dots, language=None)
                    st.audio(wav_data, format="audio/wav")
                    st.download_button("⬇️ Download Morse Audio (.WAV)", data=wav_data, file_name="morse_transmission.wav", mime="audio/wav")

        elif "2. Hide" in aud_mode:
            aud_secret = st.text_area("Secret Message to Hide Inside .WAV Audio Samples:", placeholder="Type confidential message...")
            if st.button("🎙️ Encrypt & Embed Into 16-Bit PCM Audio (.WAV)", type="primary"):
                if aud_secret.strip():
                    enc_str = encrypt_core_fn(aud_secret.strip(), group_key, reverse_rule, "NONE", 0)
                    stego_wav = encode_audio_lsb_wav(enc_str)
                    st.success("🎉 **Stego Audio Created!** To human ears, it sounds like a normal ambient synth chord, but your encrypted message is locked inside the 16-bit audio samples!")
                    st.audio(stego_wav, format="audio/wav")
                    st.download_button("⬇️ Download Stego Audio (.WAV)", data=stego_wav, file_name="stego_carrier_audio.wav", mime="audio/wav")
                else:
                    st.warning("Please enter a secret message first.")

        else:
            up_wav = st.file_uploader("Upload Stego .WAV File:", type=["wav"])
            if up_wav and st.button("🎧 Extract Bits & Decrypt Audio Payload", type="primary"):
                ok_w, ext_c = decode_audio_lsb_wav(up_wav.getvalue())
                if not ok_w:
                    st.error(ext_c)
                else:
                    st.caption("Extracted Encrypted Payload from Audio Samples:")
                    st.code(ext_c, language=None)
                    ok_d, final_m = decrypt_core_fn(ext_c, group_key, reverse_rule)
                    if ok_d:
                        st.success("🎉 **Decrypted Secret Message from Audio:**")
                        st.info(final_m)
                    else:
                        st.error(final_m)

    # --- TAB 5: VISUAL CRYPTOGRAPHY (2-SHARE IMAGE SPLITTING) ---
    with p2_tab2:
        st.markdown("""
        <div class="ws-banner">
            <h4>👁️ Naor-Shamir Visual Cryptography (2-Out-Of-2 Secret Image Sharing)</h4>
            <p>Splits a secret code into <b>2 independent random noise transparencies (Share 1 & Share 2)</b>. Neither share reveals any clue alone, but stacking them together reveals the secret to the human eye!</p>
        </div>
        """, unsafe_allow_html=True)

        vc_col1, vc_col2 = st.columns([2, 1])
        with vc_col1:
            vc_secret = st.text_input("Enter Short Secret Code / Password (Max 8 chars):", value="HCMUS26", max_chars=8)
        with vc_col2:
            st.write("")
            gen_vc = st.button("👁️ Split Into 2 Visual Noise Shares", type="primary", use_container_width=True)

        if gen_vc or "vc_shares" not in st.session_state:
            s1_img, s2_img, ov_img = generate_visual_crypto_shares(vc_secret)
            st.session_state.vc_shares = (s1_img, s2_img, ov_img)

        s1_img, s2_img, ov_img = st.session_state.vc_shares
        v1, v2, v3 = st.columns(3)
        with v1:
            st.markdown("##### 🧩 Share #1 (Send to Agent A)")
            st.image(s1_img, caption="100% Random Subpixel Noise Alone", use_container_width=True)
        with v2:
            st.markdown("##### 🧩 Share #2 (Send to Agent B)")
            st.image(s2_img, caption="100% Random Subpixel Noise Alone", use_container_width=True)
        with v3:
            st.markdown("##### 🔓 Stacked Overlay (Share 1 + 2)")
            if st.checkbox("🔍 Stack & Align Both Shares Together", value=True):
                st.image(ov_img, caption="Secret Revealed by Optical Overlay!", use_container_width=True)
            else:
                st.info("Check the box above to simulate stacking Share 1 on top of Share 2.")

    # --- TAB 6: AUTOMATED FORENSIC CIPHER IDENTIFIER & CRACKER ---
    with p2_tab3:
        st.markdown("""
        <div class="ws-banner">
            <h4>🤖 Automated Forensic Cryptanalysis & Cipher Identifier</h4>
            <p>Paste any unknown ciphertext, encoded string, or intercepted message. The forensic engine measures Shannon Entropy, Index of Coincidence (IoC), and auto-cracks 30+ transformations!</p>
        </div>
        """, unsafe_allow_html=True)

        mystery_in = st.text_area(
            "📋 Paste Unknown Ciphertext / Encoded String to Analyze:",
            value="Wkh vhfuhw phhwlqj lv dw plgqljkw lq Sdulv",
            height=95
        )
        if st.button("🔍 Run Automated Forensic Cryptanalysis", type="primary", use_container_width=True):
            if mystery_in.strip():
                ent = calculate_shannon_entropy(mystery_in.strip())
                ioc = calculate_ioc(mystery_in.strip())

                f_c1, f_c2, f_c3 = st.columns(3)
                f_c1.metric("📊 Length", f"{len(mystery_in.strip())} chars", "Intercepted Sample")
                f_c2.metric("🎲 Shannon Entropy", f"{ent:.2f} bits/char", "High (>4.5) = Compressed/Encrypted")
                f_c3.metric("📐 Index of Coincidence (IoC)", f"{ioc:.4f}", "~0.067 = English / Monoalphabetic")

                st.markdown("##### 🔓 Automated Decryption & Brute-Force Candidates:")
                candidates = auto_crack_unknown_cipher(mystery_in)
                for method_name, decoded_out in candidates:
                    with st.expander(f"{method_name}  ➡️  {decoded_out[:65]}...", expanded=("High Confidence" in method_name or "🎯" in method_name)):
                        st.code(decoded_out, language=None)

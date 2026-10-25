import streamlit as st
import json
import os
import re
import html
import base64
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from PIL import Image
import io

AI_MEMORY_FILE = "ai_mentor_memory_db.json"

# ==============================================================================
# 1. KHO TRI THỨC NỀN TẢNG (4 TRỤ CỘT ENCODING, NHỊ PHÂN, MẬT MÃ & 20 BÀI HỌC)
# ==============================================================================
CORE_KNOWLEDGE_BASE = [
    {
        "id": "KB_CHAR_ENC",
        "keywords": ["character encoding", "mã hóa ký tự", "utf-8", "utf8", "utf-16", "utf-32", "ascii", "unicode", "7-bit"],
        "vi": (
            "🔤 **1. Mã hóa ký tự (Character Encoding):**\n"
            "Dùng để biểu diễn các ký tự văn bản thành dạng dữ liệu nhị phân (bits/bytes) mà máy tính hiểu được:\n"
            "- **UTF-8:** Kiểu mã hóa ký tự phổ biến và thống trị nhất trên web hiện nay (chiếm gần 90% các trang web). Hỗ trợ đa ngôn ngữ (1 đến 4 bytes/ký tự) và tương thích ngược hoàn hảo với ASCII.\n"
            "- **UTF-16 / UTF-32:** Dùng từ 2 đến 4 byte cho mỗi ký tự, thường dùng trong lưu trữ nội bộ của hệ điều hành (như Windows/Java) hoặc các ứng dụng lập trình.\n"
            "- **ASCII:** Bộ mã hóa 7-bit cơ bản gồm 128 ký tự (0–127) dành cho chữ cái tiếng Anh (`A-Z` = 65–90, `a-z` = 97–122), chữ số (`0-9` = 48–57) và ký tự điều khiển."
        ),
        "en": (
            "🔤 **1. Character Encoding:**\n"
            "Used to represent text characters as binary data that computers can process:\n"
            "- **UTF-8:** The dominant character encoding on the web (~90% of all websites). Supports all global languages (1 to 4 bytes per char) and is 100% backward-compatible with ASCII.\n"
            "- **UTF-16 / UTF-32:** Uses 2 to 4 bytes per character, commonly used in internal OS memory and programming runtimes.\n"
            "- **ASCII:** Foundational 7-bit encoding with 128 characters (0–127) for English letters (`A=65`, `a=97`), digits (`0=48`), and punctuation."
        )
    },
    {
        "id": "KB_DATA_BIN_ENC",
        "keywords": ["base64", "url encode", "percent encoding", "html encode", "xss", "entity", "%20", "jwt", "data uri", "nhị phân sang văn bản", "binary encoding"],
        "vi": (
            "🔄 **2. Mã hóa dữ liệu / Nhị phân sang văn bản (Data & Binary Encoding):**\n"
            "Dùng để chuyển đổi dữ liệu nhị phân (như file, hình ảnh) sang dạng chuỗi ký tự an toàn khi truyền tải:\n"
            "- **Base64:** Gom mỗi 3 bytes (24 bits) thành 4 nhóm 6-bit (64 ký tự ASCII). Thường dùng để đính kèm hình ảnh trực tiếp vào HTML (`Data URI`), gửi file qua Email (MIME) hoặc định dạng token xác thực (`JWT`).\n"
            "- **URL Encode (Percent Encoding):** Chuyển các ký tự đặc biệt hoặc dấu cách trong đường dẫn URL sang dạng `%XX` an toàn với trình duyệt (ví dụ: dấu cách chuyển thành `%20`).\n"
            "- **HTML Encode:** Chuyển đổi các ký tự cú pháp HTML đặc biệt như `<`, `>`, `&` thành thực thể (`&lt;`, `&gt;`, `&amp;`) để tránh lỗi hiển thị và **chống tấn công XSS (Cross-Site Scripting)** trên website."
        ),
        "en": (
            "🔄 **2. Data & Binary-to-Text Encoding:**\n"
            "Converts raw binary data (files, images) into safe printable text characters for transmission:\n"
            "- **Base64:** Groups 3 bytes (24 bits) into four 6-bit ASCII characters. Widely used for HTML Data URIs, email attachments, and JWT authentication tokens.\n"
            "- **URL Encode (Percent Encoding):** Converts spaces and special URL characters into safe `%XX` hex format (e.g., space becomes `%20`).\n"
            "- **HTML Encode:** Converts `<`, `>`, `&` into HTML entities (`&lt;`, `&gt;`, `&amp;`) to prevent rendering bugs and block **XSS (Cross-Site Scripting)** attacks."
        )
    },
    {
        "id": "KB_MULTIMEDIA_ENC",
        "keywords": ["multimedia encoding", "mã hóa đa phương tiện", "codec", "h.264", "h.265", "hevc", "avc", "vp9", "av1", "mp4", "mkv", "mp3", "aac", "flac", "ogg", "video", "audio"],
        "vi": (
            "🎬 **3. Mã hóa đa phương tiện (Multimedia Encoding):**\n"
            "Dùng để nén và chuyển đổi định dạng âm thanh, hình ảnh, video nhằm giảm dung lượng và tăng tốc độ phát/truyền tải:\n"
            "- **Video Codecs & Containers:** Gồm các chuẩn phổ biến như `H.264 (AVC)`, `H.265 (HEVC)`, `VP9`, `AV1`, đóng gói trong định dạng `MP4`, `MKV`.\n"
            "- **Âm thanh (Audio Codecs):** Gồm các chuẩn nén có hao hụt (`MP3`, `AAC`, `OGG`) và nén bảo toàn không mất dữ liệu (`FLAC`, `WAV PCM`).\n"
            "- 💡 *Lưu ý bảo mật (Steganography):* Khi giấu tin LSB vào ảnh hoặc âm thanh trên web của chúng ta, ta phải dùng chuẩn **Lossless (`PNG`, `WAV`)** vì chuẩn nén Lossy (`JPG`, `MP3`) sẽ làm biến đổi các bit LSB!"
        ),
        "en": (
            "🎬 **3. Multimedia Encoding (Video & Audio Codecs):**\n"
            "Compresses and converts media formats to reduce file size and speed up streaming:\n"
            "- **Video:** Popular codecs/containers include `H.264 (AVC)`, `H.265 (HEVC)`, `VP9`, `AV1`, `MP4`, and `MKV`.\n"
            "- **Audio:** Popular standards include `MP3`, `AAC`, `FLAC` (lossless), `OGG`, and uncompressed `WAV PCM`.\n"
            "- 💡 *Steganography Note:* Always use lossless formats (`PNG`, `WAV`) for LSB bit-hiding because lossy compression (`JPG`, `MP3`) destroys the least significant bits!"
        )
    },
    {
        "id": "KB_ML_ENC",
        "keywords": ["categorical encoding", "machine learning", "khoa học dữ liệu", "one-hot", "one hot", "label encoding", "ordinal encoding", "target encoding", "học máy"],
        "vi": (
            "🤖 **4. Mã hóa trong Khoa học dữ liệu / Machine Learning (Categorical Encoding):**\n"
            "Dùng để chuyển đổi dữ liệu dạng chữ (categorical) thành dạng số (numerical) để đưa vào huấn luyện mô hình học máy (AI/ML):\n"
            "- **One-Hot Encoding:** Tạo ra các cột nhị phân (`0` hoặc `1`) tương ứng với từng giá trị danh mục (ví dụ: Màu `[Đỏ, Xanh]` -> `[1, 0]` và `[0, 1]`).\n"
            "- **Label / Ordinal Encoding:** Gán mỗi giá trị chữ bằng một số nguyên cố định (`0, 1, 2...`), rất phù hợp cho dữ liệu có thứ bậc (như `Thấp=0, Vừa=1, Cao=2`).\n"
            "- **Target Encoding:** Thay thế giá trị danh mục bằng giá trị trung bình của biến mục tiêu (target) tương ứng với danh mục đó."
        ),
        "en": (
            "🤖 **4. Machine Learning / Data Science Categorical Encoding:**\n"
            "Transforms text/categorical features into numerical vectors for AI/ML algorithms:\n"
            "- **One-Hot Encoding:** Creates binary (`0` or `1`) columns for each category.\n"
            "- **Label / Ordinal Encoding:** Assigns a unique integer (`0, 1, 2...`) to each category.\n"
            "- **Target Encoding:** Replaces a categorical value with the mean of the target variable for that category."
        )
    },
    {
        "id": "KB_BINARY_BITS",
        "keywords": ["nhị phân", "binary", "bit", "nibble", "byte", "hex", "hexadecimal", "bù 2", "two's complement", "bitwise", "xor", "and", "shift", "dịch bit", "endian", "little-endian"],
        "vi": (
            "💻 **Kiến thức Cốt lõi về Hệ Nhị Phân (Binary), Bits & Kiến trúc Máy tính (Track 2 - Bài 04 đến 09):**\n"
            "- **1 Bit:** Đơn vị nhỏ nhất (`0` hoặc `1`).\n"
            "- **1 Nibble (4 bits):** Biểu diễn 16 giá trị (`0..15`), tương ứng chính xác với **1 chữ số Hexadecimal (`0..F`)**.\n"
            "- **1 Byte (8 bits):** Biểu diễn $2^8 = 256$ giá trị (`0..255`). Vị trí các bit từ trái qua phải có trọng số: `128, 64, 32, 16, 8, 4, 2, 1`.\n"
            "- **Số nguyên có dấu Bù 2 (Two's Complement):** Bit ngoài cùng bên trái có trọng số âm (`-128`). Để đổi $+X \\rightarrow -X$: **Đảo toàn bộ các bit (`~X`) rồi cộng thêm `1`**.\n"
            "- **Phép toán Bitwise:** `AND (&)` dùng để lọc bit (ví dụ `R & 1` lấy bit cuối LSB); `OR (|)` để bật bit; `XOR (^)` dùng trong mật mã dòng (vì `A ^ K ^ K = A`); Dịch trái `X << k` là nhân với $2^k$, dịch phải `X >> k` là chia nguyên cho $2^k$."
        ),
        "en": (
            "💻 **Core Binary, Bits & Computer Systems (Track 2 - Lessons 04 to 09):**\n"
            "- **1 Bit:** `0` or `1` | **1 Nibble (4 bits):** `0..15` (1 Hex digit `0..F`) | **1 Byte (8 bits):** $2^8 = 256$ values (`0..255`) with weights `128, 64, 32, 16, 8, 4, 2, 1`.\n"
            "- **Two's Complement (Signed Integers):** To negate $+X \\rightarrow -X$, invert all bits (`~X`) and add `1`.\n"
            "- **Bitwise Ops:** `AND (&)` masks bits (`R & 1` extracts LSB), `XOR (^)` is reversible (`(P ^ K) ^ K = P`), Left Shift `X << k` multiplies by $2^k$, Right Shift `X >> k` divides by $2^k$."
        )
    },
    {
        "id": "KB_CRYPTO_SUITE",
        "keywords": ["caesar", "affine", "vigenere", "atbash", "rail-fence", "aes", "rsa", "sha-256", "sha256", "quantum", "shor", "grover", "steganography", "lsb", "one-time pad", "otp", "mật mã"],
        "vi": (
            "🔐 **Tổng hợp các Thuật toán Mật mã & Giấu tin trên Hệ thống (Bài 01–03 & 10–20):**\n"
            "- **Encoding vs. Encryption vs. Hashing:** Encoding (Base64, UTF-8, Morse) không dùng khóa; Encryption (AES, RSA, Caesar) cần khóa bí mật để giải mã ngược; Hashing (SHA-256) là hàm băm 1 chiều không thể dịch ngược.\n"
            "- **Mật mã Cổ điển:** *Caesar* ($C = (P + K) \\bmod 26$), *Affine* ($C = (aP + b) \\bmod 26$ với $\\gcd(a,26)=1$), *Atbash* (đối xứng gương `A↔Z`), *Vigenère* (đa bảng theo từ khóa).\n"
            "- **Giấu tin (Steganography):** Giấu sự tồn tại của bản mã vào bit cuối LSB của ảnh `.PNG` hoặc mẫu âm thanh `.WAV` 16-bit.\n"
            "- **Mật mã Hiện đại & Lượng tử:** *AES-256* (khối 128-bit = 16 bytes, 14 vòng lặp), *RSA* ($C = M^e \\bmod N$, $M = C^d \\bmod N$), *Thuật toán Shor* (phá RSA/ECC) và *Grover* (giảm một nửa số bit an toàn khóa đối xứng)."
        ),
        "en": (
            "🔐 **Cryptography & Steganography Suite Summary (Lessons 01–03 & 10–20):**\n"
            "- **Encoding vs. Encryption vs. Hashing:** Encoding uses no key; Encryption requires a Secret Key to reverse; Hashing (SHA-256) is strictly one-way.\n"
            "- **Classical Ciphers:** Caesar `(P + K) mod 26`, Affine `(aP + b) mod 26` with `gcd(a,26)=1`, Atbash mirror `A↔Z`, Rail-Fence transposition, and Vigenère.\n"
            "- **Modern & Post-Quantum:** AES-256 (16-byte blocks, 14 rounds), RSA public-key trapdoor, Shor's algorithm, Grover's algorithm, and Lattice PQC."
        )
    }
]

# Từ khóa để kiểm tra câu hỏi có liên quan đến chủ đề học tập / mật mã / CNTT của web hay không
ALLOWED_DOMAIN_KEYWORDS = {
    "mật mã", "mã hóa", "giải mã", "cipher", "crypto", "cryptography", "encode", "encoding", "decode",
    "utf", "ascii", "unicode", "base64", "url", "html", "xss", "percent", "multimedia", "video", "audio",
    "h.264", "h.265", "hevc", "av1", "vp9", "mp3", "MP4", "flac", "wav", "png", "lsb", "steganography", "giấu tin",
    "one-hot", "onehot", "label", "ordinal", "target", "machine learning", "học máy", "data", "dữ liệu",
    "nhị phân", "binary", "bit", "bits", "byte", "bytes", "nibble", "hex", "hexadecimal", "decimal", "thập phân",
    "bù 2", "complement", "overflow", "bitwise", "xor", "and", "shift", "dịch", "assembly", "rax", "mov", "shl", "shr",
    "endian", "little-endian", "big-endian", "caesar", "rot13", "atbash", "affine", "vigenere", "rail-fence", "transposition",
    "modulo", "mod", "inverse", "nghịch đảo", "coprime", "frequency", "tần suất", "otp", "one-time pad", "shannon", "entropy",
    "sha", "sha-256", "hash", "băm", "salt", "rainbow", "aes", "ecb", "gcm", "cbc", "rsa", "diffie", "public key", "private key",
    "prime", "totient", "phi", "quantum", "lượng tử", "qubit", "shor", "grover", "lattice", "kyber",
    "bài", "lesson", "module", "track", "lab", "quiz", "câu hỏi", "đáp án", "hint", "gợi ý", "sudoku", "ctf", "web", "app",
    "camouflage", "ngụy trang", "morse", "visual", "pháp y", "forensic", "password", "mật khẩu", "key", "khóa", "security", "bảo mật",
    "hiếu", "hcmus", "hello", "hi", "xin chào", "chào", "help", "giúp", "hướng dẫn", "explain", "giải thích", "là gì", "what is", "how"
}

OFF_TOPIC_KEYWORDS = {
    "nấu ăn", "công thức nấu", "phở", "bún bò", "bóng đá", "ngoại hạng anh", "world cup", "messi", "ronaldo",
    "thời tiết", "mưa", "nắng", "xổ số", "lô đề", "tử vi", "bói toán", "cung hoàng đạo", "người yêu", "tình yêu", "thất tình",
    "recipe", "cooking", "football", "soccer", "weather", "horoscope", "astrology", "dating", "boyfriend", "girlfriend"
}


def load_ai_memory() -> dict:
    if not os.path.exists(AI_MEMORY_FILE):
        default_mem = {
            "learned_facts": [
                {
                    "topic": "Xu hướng AI & Mật mã 2026 (Post-Quantum & AI Security)",
                    "keywords": ["xu hướng", "trend", "2026", "ai security", "ml-kem", "post-quantum"],
                    "content": "Trong năm 2026, xu hướng bảo mật quan trọng nhất là chuyển đổi sang Mật mã Hậu Lượng Tử (NIST ML-KEM / Kyber và ML-DSA) kết hợp với AI Tự động Phát hiện Xâm nhập (AI-Driven Threat Hunting) và Bảo mật Mô hình Ngôn ngữ Lớn (LLM Guardrails chống Prompt Injection).",
                    "taught_by": "System_Core",
                    "timestamp": "2026-10-25 UTC"
                }
            ],
            "user_feedback": []
        }
        with open(AI_MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(default_mem, f, ensure_ascii=False, indent=4)
        return default_mem
    try:
        with open(AI_MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"learned_facts": [], "user_feedback": []}


def save_ai_memory(data: dict):
    with open(AI_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def detect_user_language(text: str) -> str:
    """Tự động nhận diện người dùng đang hỏi bằng Tiếng Việt hay Tiếng Anh."""
    vn_chars = set("àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ")
    low = text.lower()
    if any(c in vn_chars for c in low):
        return "vi"
    vn_words = ["là gì", "như thế nào", "giải thích", "cho tôi", "tại sao", "mã hóa", "nhị phân", "bài học", "giúp", "cách"]
    if any(w in low for w in vn_words):
        return "vi"
    return "en"


def is_query_on_topic(query: str, mem_db: dict) -> bool:
    """Kiểm tra câu hỏi có nằm trong phạm vi Bài học / Mật mã / Encoding / Khoa học máy tính không."""
    low = query.lower()
    if any(bad in low for bad in OFF_TOPIC_KEYWORDS):
        return False
    if any(good in low for good in ALLOWED_DOMAIN_KEYWORDS):
        return True
    # Kiểm tra xem có khớp với kiến thức mới mà người dùng đã dạy cho AI không
    for fact in mem_db.get("learned_facts", []):
        if any(kw.lower() in low for kw in fact.get("keywords", [])):
            return True
    # Kiểm tra nếu có chứa số nhị phân, hex, hoặc phép toán
    if re.search(r'\b[01]{4,}\b|\b0x[0-9a-f]+\b|\bmod\b|<<|>>', low):
        return True
    return False


def try_live_computation(query: str, lang: str) -> str:
    """Thực hiện chuyển đổi / giải mã trực tiếp nếu người dùng đưa số hoặc chuỗi vào hỏi."""
    q_clean = query.strip()
    low = q_clean.lower()

    # 1. Chuyển đổi số thập phân sang Nhị phân & Hex (VD: "binary 42", "đổi 42 sang nhị phân")
    nums = re.findall(r'\b\d+\b', q_clean)
    if nums and any(k in low for k in ["binary", "nhị phân", "hex", "bù 2", "complement", "bit"]):
        n = int(nums[0])
        if 0 <= n <= 255:
            twos = f"{(256 - n) & 0xFF:08b}" if n > 0 else "00000000"
            if lang == "vi":
                return (
                    f"🧮 **Kết quả tính toán trực tiếp cho số `{n}`:**\n"
                    f"- **Nhị phân 8-bit (Unsigned):** `{n:08b}` (High nibble: `{n>>4:04b}`, Low nibble: `{n&15:04b}`)\n"
                    f"- **Hệ thập lục phân (Hexadecimal):** `0x{n:02X}`\n"
                    f"- **Biểu diễn số âm `-{n}` (Bù 2 - Two's Complement):** `{twos}`"
                )
            else:
                return (
                    f"🧮 **Live Binary & Hex Computation for `{n}`:**\n"
                    f"- **8-Bit Binary:** `{n:08b}` (High nibble: `{n>>4:04b}`, Low nibble: `{n&15:04b}`)\n"
                    f"- **Hexadecimal:** `0x{n:02X}`\n"
                    f"- **Two's Complement of `-{n}`:** `{twos}`"
                )

    # 2. Chuyển đổi chuỗi sang Base64, URL Encode, HTML Encode, UTF-8 Bytes
    quote_match = re.findall(r'["\']([^"\']+)["\']', q_clean)
    if quote_match and any(k in low for k in ["encode", "mã hóa", "base64", "url", "html", "utf-8", "ascii"]):
        sample = quote_match[0]
        b64 = base64.b64encode(sample.encode("utf-8")).decode("utf-8")
        url_e = urllib.parse.quote(sample)
        html_e = html.escape(sample)
        utf8_hex = " ".join(f"{b:02X}" for b in sample.encode("utf-8"))
        if lang == "vi":
            return (
                f"⚡ **Kết quả Encode trực tiếp cho chuỗi `'{sample}'`:**\n"
                f"- **UTF-8 Hex Bytes:** `{utf8_hex}` ({len(sample.encode('utf-8'))} bytes)\n"
                f"- **Base64 Encode:** `{b64}`\n"
                f"- **URL Encode (Percent Encoding):** `{url_e}`\n"
                f"- **HTML Encode (Chống XSS):** `{html_e}`"
            )
        else:
            return (
                f"⚡ **Live Encoding Results for `'{sample}'`:**\n"
                f"- **UTF-8 Hex Bytes:** `{utf8_hex}` ({len(sample.encode('utf-8'))} bytes)\n"
                f"- **Base64 Encode:** `{b64}`\n"
                f"- **URL Encode:** `{url_e}`\n"
                f"- **HTML Encode (XSS Safe):** `{html_e}`"
            )
    return ""


def generate_ai_mentor_response(
    query: str,
    current_lesson: dict,
    mem_db: dict,
    decode_lsb_fn=None
) -> str:
    """Bộ não phản hồi đa ngôn ngữ, kiểm tra lạc đề, tự học và tra cứu toàn bộ 20 bài học."""
    lang = detect_user_language(query)
    low = query.lower().strip()

    # 1. Cú pháp tự học trực tiếp qua khung chat: "Học: [Chủ đề] => [Nội dung]" hoặc "Learn: [Topic] => [Content]"
    if low.startswith("học:") or low.startswith("learn:") or low.startswith("update:"):
        raw_body = query.split(":", 1)[1].strip()
        if "=>" in raw_body or "=" in raw_body:
            sep = "=>" if "=>" in raw_body else "="
            t_part, c_part = raw_body.split(sep, 1)
            kws = [w.strip().lower() for w in re.split(r'[,;\s]+', t_part) if len(w.strip()) >= 2]
            mem_db["learned_facts"].insert(0, {
                "topic": t_part.strip(),
                "keywords": kws,
                "content": c_part.strip(),
                "taught_by": st.session_state.get("ctf_user") or "User",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            })
            save_ai_memory(mem_db)
            if lang == "vi":
                return f"🧠 **AI Đã Tự Học & Cập Nhật Bộ Nhớ Thành Công!**\n- **Chủ đề mới:** `{t_part.strip()}`\n- **Từ khóa ghi nhớ:** `{', '.join(kws)}`\nTừ giờ bất kỳ ai hỏi về chủ đề này, tôi sẽ sử dụng kiến thức mới này để trả lời!"
            return f"🧠 **Self-Learning Memory Updated!**\n- **New Topic:** `{t_part.strip()}`\nI have permanently indexed this knowledge for future questions!"

    # 2. Kiểm tra Lạc Đề (Domain Guardrail)
    if not is_query_on_topic(query, mem_db):
        if lang == "vi":
            return (
                "⚠️ **Nhắc nhở từ AI Cyber Mentor:**\n"
                "Câu hỏi của bạn có vẻ nằm ngoài phạm vi bài học và chủ đề của hệ thống. "
                "Tôi được huấn luyện chuyên sâu để hỗ trợ bạn về:\n"
                "- **4 Trụ cột Encoding:** Mã hóa ký tự (`UTF-8, UTF-16, ASCII`), Mã hóa dữ liệu (`Base64, URL Encode %20, HTML Encode`), Đa phương tiện (`H.264, HEVC, FLAC, MP3`) & Học máy (`One-Hot, Label, Target Encoding`).\n"
                "- **Hệ thống Máy tính & Nhị phân:** `Bits, Nibbles, Bytes, Hex, Số bù 2 (Two's Complement), Bitwise, Assembly`.\n"
                "- **20 Bài học trong Security Academy, Mật mã học (Caesar, Affine, AES, RSA, SHA-256, Steganography) & Giải đố.**\n\n"
                "👉 *Hãy đặt câu hỏi xoay quanh bài học hiện tại hoặc các chủ đề mật mã/máy tính ở trên nhé!*"
            )
        else:
            return (
                "⚠️ **Gentle Reminder from AI Cyber Mentor:**\n"
                "Your question appears to be unrelated to our curriculum. Please keep questions focused on **Cryptography, Character/Data/Multimedia/ML Encoding (UTF-8, Base64, URL/HTML Encode, One-Hot), Binary & Bits, Steganography, or the 20 Security Academy Lessons**!"
            )

    # 3. Kiểm tra trong Bộ Nhớ Tự Học (Self-Learning Memory) trước tiên
    matched_learned = []
    for fact in mem_db.get("learned_facts", []):
        if any(kw in low for kw in fact.get("keywords", [])) or fact["topic"].lower() in low:
            matched_learned.append(f"🧠 **[Kiến thức AI Tự Cập Nhật — {fact['topic']}]:**\n{fact['content']}")

    # 4. Kiểm tra Tính toán Trực tiếp (Live Binary / Encoding Solver)
    live_calc = try_live_computation(query, lang)

    # 5. Kiểm tra nếu người dùng hỏi về Bài Học Đang Mở (Current Lesson Context)
    lesson_context_reply = ""
    if current_lesson and any(k in low for k in ["bài này", "bài hiện tại", "this lesson", "quiz", "lab", "đáp án", "gợi ý", "hint", "tóm tắt", "summary"]):
        lid = current_lesson.get("id", "L01")
        ltitle = current_lesson.get("title", "")
        if lang == "vi":
            lesson_context_reply = (
                f"📘 **Hướng dẫn trực tiếp cho Bài học đang mở ({lid} — {ltitle}):**\n"
                f"- **Tóm tắt cốt lõi:** {current_lesson.get('overview', '')[:280]}...\n"
                f"- **Gợi ý Quiz 1:** Đáp án đúng là `{current_lesson.get('q1_ans', '')}`.\n"
                f"- **Gợi ý Quiz 2:** Đáp án đúng là `{current_lesson.get('q2_ans', '')}`.\n"
                f"- **Hướng dẫn Lab 1:** {current_lesson.get('lab1_q', '')} $\\rightarrow$ Đáp án: **`{current_lesson.get('lab1_ans', '')}`**.\n"
                f"- **Hướng dẫn Lab 2:** {current_lesson.get('lab2_q', '')} $\\rightarrow$ Đáp án: **`{current_lesson.get('lab2_ans', '')}`**."
            )
        else:
            lesson_context_reply = (
                f"📘 **Walkthrough for Active Module ({lid} — {ltitle}):**\n"
                f"- **Core Concept:** {current_lesson.get('overview', '')[:280]}...\n"
                f"- **Quiz 1 Key:** `{current_lesson.get('q1_ans', '')}` | **Quiz 2 Key:** `{current_lesson.get('q2_ans', '')}`\n"
                f"- **Lab 1 Solution:** **`{current_lesson.get('lab1_ans', '')}`** | **Lab 2 Solution:** **`{current_lesson.get('lab2_ans', '')}`**."
            )

    # 6. Tra cứu Kho Tri Thức Cốt Lõi (4 Nhóm Encoding, Nhị phân, Mật mã)
    kb_matches = []
    for item in CORE_KNOWLEDGE_BASE:
        if any(kw in low for kw in item["keywords"]):
            kb_matches.append(item[lang])

    # Tổng hợp câu trả lời
    parts = [p for p in (matched_learned + ([live_calc] if live_calc else []) + ([lesson_context_reply] if lesson_context_reply else []) + kb_matches) if p]

    if parts:
        return "\n\n---\n\n".join(parts[:3])

    # Nếu là câu chào hoặc câu hỏi chung về bài học hiện tại
    lid = current_lesson.get("id", "L01") if current_lesson else "L01"
    ltitle = current_lesson.get("title", "Security Academy") if current_lesson else "Security Academy"
    if lang == "vi":
        return (
            f"👋 Chào bạn! Tôi là **AI Cyber Mentor** đang đồng hành cùng bạn tại **{lid}: {ltitle}**.\n\n"
            f"Bạn có thể hỏi tôi bằng Tiếng Việt hoặc Tiếng Anh về:\n"
            f"1. **Giải thích bài học đang mở**, gợi ý giải **Quiz 1, Quiz 2, Lab 1, Lab 2** (chỉ cần gõ *'Gợi ý bài này'*).\n"
            f"2. **4 Nhóm Encoding phổ biến:** `UTF-8 / ASCII`, `Base64 / URL Encode (%20) / HTML Encode`, `Video/Audio Codec (H.264, FLAC)`, và `Machine Learning Encoding (One-Hot, Label, Target)`.\n"
            f"3. **Chuyển đổi trực tiếp:** Gõ *'Đổi 42 sang nhị phân'* hoặc *'Encode \"Hello HCMUS\"'*.\n"
            f"4. **Gửi File / Hình ảnh** ở mục đính kèm bên dưới để tôi quét phân tích byte và giấu tin LSB!"
        )
    else:
        return (
            f"👋 Hello! I am your **AI Cyber Mentor** currently tracking **{lid}: {ltitle}**.\n\n"
            f"Ask me anything in English or Vietnamese about:\n"
            f"1. **This lesson's concepts, Quizzes, or Labs** (type *'Explain this lesson'* or *'Hint'*).\n"
            f"2. **The 4 Encoding Pillars:** Character (`UTF-8, ASCII`), Binary-to-Text (`Base64, URL %20, HTML`), Multimedia (`H.264, FLAC`), and ML (`One-Hot, Label, Target`).\n"
            f"3. **Live Binary/Hex Math:** Type *'Binary 42'* or *'Encode \"Secret\"'*.\n"
            f"4. **Attach an Image or File** below for instant forensic byte & LSB steganography analysis!"
        )


def analyze_uploaded_file_or_image(uploaded_file, decode_lsb_fn=None, decode_audio_fn=None) -> str:
    """Phân tích trực tiếp Hình ảnh hoặc File mà người dùng gửi cho AI."""
    fname = uploaded_file.name
    raw_bytes = uploaded_file.getvalue()
    fsize = len(raw_bytes)
    ext = fname.split(".")[-1].lower() if "." in fname else ""

    report = [f"📎 **Báo cáo Phân tích File Pháp y của AI cho `{fname}` ({fsize:,} bytes):**"]

    # 1. Nếu là Hình ảnh (PNG / JPG)
    if ext in ["png", "jpg", "jpeg"]:
        try:
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            w, h = img.size
            max_lsb_bytes = (w * h * 3) // 8 - 13
            report.append(f"- 🖼️ **Định dạng Ảnh:** `{ext.upper()}` | Độ phân giải: `{w} x {h}` pixels (`{w*h:,}` tổng pixels).")
            report.append(f"- 📊 **Sức chứa Giấu tin LSB tối đa:** `~{max_lsb_bytes:,} bytes`.")
            if decode_lsb_fn and ext == "png":
                ok_lsb, hidden_pay = decode_lsb_fn(img)
                if ok_lsb:
                    report.append(f"- 🎯 **PHÁT HIỆN MẬT MÃ GIẤU TRONG ẢNH (LSB Payload):** `{hidden_pay}`")
                else:
                    report.append("- 🔍 **Quét LSB:** Không phát hiện chuỗi đánh dấu `<<END_STEGO>>` ẩn trong bức ảnh này.")
        except Exception as e:
            report.append(f"- ❌ Lỗi đọc ảnh: {str(e)}")

    # 2. Nếu là File Âm thanh (.WAV)
    elif ext == "wav":
        report.append("- 🎵 **Định dạng Âm thanh:** `16-bit PCM WAV Audio`.")
        if decode_audio_fn:
            ok_aud, aud_pay = decode_audio_fn(raw_bytes)
            if ok_aud:
                report.append(f"- 🎯 **PHÁT HIỆN MẬT MÃ TRONG SÓNG ÂM (.WAV LSB):** `{aud_pay}`")
            else:
                report.append("- 🔍 **Quét WAV LSB:** Không phát hiện mật mã ẩn trong mẫu âm thanh này.")

    # 3. Nếu là File Văn bản / Code / Dữ liệu (.txt, .json, .csv, .py, .md)
    else:
        first_16_hex = " ".join(f"{b:02X}" for b in raw_bytes[:16])
        first_4_bin = " ".join(f"{b:08b}" for b in raw_bytes[:4])
        report.append(f"- 💻 **16 Hex Bytes đầu tiên:** `{first_16_hex}`")
        report.append(f"- 🔢 **4 Bytes Nhị phân đầu tiên (32 bits):** `{first_4_bin}`")
        try:
            txt_content = raw_bytes.decode("utf-8")
            is_ascii = all(ord(c) < 128 for c in txt_content)
            enc_type = "Standard 7-Bit ASCII (Tương thích UTF-8)" if is_ascii else "Multi-Byte UTF-8 Unicode (Có dấu / Emoji)"
            report.append(f"- 🔤 **Chuẩn Mã hóa Ký tự:** `{enc_type}` ({len(txt_content)} ký tự).")
            preview = txt_content[:200].replace("\n", " ")
            report.append(f"- 📄 **Trích xuất nội dung:** `{preview}...`")
        except Exception:
            b64_preview = base64.b64encode(raw_bytes[:45]).decode("utf-8")
            report.append(f"- 📦 **Dữ liệu Nhị phân thuần (Raw Binary) -> Base64:** `{b64_preview}...`")

    return "\n".join(report)


def render_ai_cyber_mentor_widget(current_lesson: dict = None, decode_lsb_fn=None, decode_audio_fn=None, widget_key: str = "acad_ai"):
    """
    Hiển thị Khung Chat AI nhỏ gọn nằm ở Cột Bên Phải của trang web,
    tích hợp Gửi File/Ảnh và Tự Học (Self-Learning Memory).
    """
    mem_db = load_ai_memory()

    st.markdown("""
    <style>
        .ai-mentor-header {
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #0f172a 100%);
            border: 1.5px solid #6366f1;
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 10px;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.25);
        }
        .ai-mentor-badge {
            background: rgba(99, 102, 241, 0.25);
            color: #a5b4fc;
            border: 1px solid #6366f1;
            padding: 2px 8px;
            border-radius: 99px;
            font-size: 0.7rem;
            font-weight: 700;
        }
    </style>
    """, unsafe_allow_html=True)

    active_lid = current_lesson.get("id", "All") if current_lesson else "Global"
    learned_cnt = len(mem_db.get("learned_facts", []))

    st.markdown(f"""
    <div class="ai-mentor-header">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="ai-mentor-badge">🤖 AI CYBER MENTOR • MODULE {active_lid}</span>
            <span style="font-size:0.72rem; color:#34d399; font-weight:700;">🧠 Memory: {learned_cnt} Topics</span>
        </div>
        <div style="font-size:1.08rem; font-weight:800; color:#f8fafc; margin-top:6px;">Gia Sư AI Mật Mã & Máy Tính</div>
        <div style="font-size:0.78rem; color:#94a3b8; margin-top:2px;">Hỏi bằng Tiếng Việt hoặc Tiếng Anh • Tự động nhắc nếu lạc đề • Hỗ trợ quét Ảnh/File</div>
    </div>
    """, unsafe_allow_html=True)

    chat_hist_key = f"ai_mentor_history_{widget_key}"
    if chat_hist_key not in st.session_state:
        st.session_state[chat_hist_key] = [
            {
                "role": "assistant",
                "content": (
                    "👋 **Xin chào / Hello!** Tôi là **AI Cyber Mentor**.\n"
                    "- Tôi nắm rõ toàn bộ **20 Bài học**, **Hệ nhị phân (Bits/Bytes)**, và **4 nhóm Encoding** (`UTF-8/ASCII`, `Base64/URL/HTML`, `Video/Audio Codecs`, `One-Hot/Label/Target ML`).\n"
                    "- Bạn hỏi ngôn ngữ nào tôi trả lời ngôn ngữ đó, hoặc bấm các nút gợi ý nhanh bên dưới nhé!"
                )
            }
        ]

    tab_chat, tab_attach, tab_train = st.tabs([
        "💬 Chat AI",
        "📎 Gửi Ảnh/File",
        "🧠 Dạy AI Học"
    ])

    with tab_chat:
        # 4 nút hỏi nhanh bám sát yêu cầu của người học
        q_c1, q_c2 = st.columns(2)
        with q_c1:
            if st.button("📘 Gợi ý bài đang học", key=f"q_les_{widget_key}", use_container_width=True):
                ans = generate_ai_mentor_response("Gợi ý bài hiện tại", current_lesson, mem_db, decode_lsb_fn)
                st.session_state[chat_hist_key].append({"role": "user", "content": "📘 Gợi ý & tóm tắt bài học đang mở"})
                st.session_state[chat_hist_key].append({"role": "assistant", "content": ans})
                st.rerun()
        with q_c2:
            if st.button("🔤 4 Nhóm Encoding", key=f"q_enc_{widget_key}", use_container_width=True):
                ans = generate_ai_mentor_response("Giải thích UTF-8, Base64, URL Encode, Multimedia và One-Hot Encoding", current_lesson, mem_db, decode_lsb_fn)
                st.session_state[chat_hist_key].append({"role": "user", "content": "🔤 Tóm tắt 4 nhóm Encoding quan trọng"})
                st.session_state[chat_hist_key].append({"role": "assistant", "content": ans})
                st.rerun()

        # Khung hiển thị lịch sử hội thoại với AI
        msg_box = st.container(height=350, border=True)
        with msg_box:
            for msg in st.session_state[chat_hist_key]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Thanh nhập câu hỏi cho AI
        user_q = st.chat_input("Hỏi AI về bài học, nhị phân, UTF-8, Base64...", key=f"in_ai_{widget_key}")
        if user_q and user_q.strip():
            st.session_state[chat_hist_key].append({"role": "user", "content": user_q.strip()})
            ai_reply = generate_ai_mentor_response(user_q.strip(), current_lesson, mem_db, decode_lsb_fn)
            st.session_state[chat_hist_key].append({"role": "assistant", "content": ai_reply})
            st.rerun()

        if len(st.session_state[chat_hist_key]) > 2:
            if st.button("🧹 Xóa lịch sử chat AI", key=f"clr_ai_{widget_key}", use_container_width=True):
                st.session_state[chat_hist_key] = st.session_state[chat_hist_key][:1]
                st.rerun()

    # --- TAB 2: GỬI HÌNH ẢNH HOẶC FILE CHO AI PHÂN TÍCH ---
    with tab_attach:
        st.caption("📎 Tải lên hình ảnh (`.png, .jpg`), âm thanh (`.wav`) hoặc file dữ liệu (`.txt, .json, .csv, .py`) để AI kiểm tra byte nhị phân, mã ký tự UTF-8/ASCII và quét tìm mật mã ẩn:")
        up_file = st.file_uploader(
            "Chọn Ảnh hoặc File gửi cho AI:",
            type=["png", "jpg", "jpeg", "wav", "txt", "json", "csv", "py", "md"],
            key=f"up_ai_{widget_key}"
        )
        if up_file:
            if ext_type := up_file.name.split(".")[-1].lower() in ["png", "jpg", "jpeg"]:
                st.image(up_file, caption=f"Ảnh đính kèm: {up_file.name}", use_container_width=True)
            if st.button("🔍 Yêu cầu AI Phân tích File này", type="primary", key=f"btn_anl_{widget_key}", use_container_width=True):
                file_report = analyze_uploaded_file_or_image(up_file, decode_lsb_fn, decode_audio_fn)
                st.session_state[chat_hist_key].append({"role": "user", "content": f"📎 *[Đã gửi file `{up_file.name}`]* Hãy phân tích file này giúp tôi!"})
                st.session_state[chat_hist_key].append({"role": "assistant", "content": file_report})
                st.success("✅ AI đã phân tích xong! Chuyển sang tab **💬 Chat AI** để xem chi tiết báo cáo.")

    # --- TAB 3: TỰ HỌC, CẬP NHẬT XU HƯỚNG MỚI & TIẾP THU Ý KIẾN NGƯỜI DÙNG ---
    with tab_train:
        st.caption("🧠 **Huấn luyện & Cập nhật Kiến thức Mới cho AI:** Dạy cho AI các xu hướng công nghệ mới hoặc đóng góp ý kiến để AI tự hoàn thiện.")
        t_topic = st.text_input("📌 Chủ đề / Khái niệm mới:", placeholder="VD: Mã hóa đồng cấu (Homomorphic Encryption)", key=f"tr_top_{widget_key}")
        t_kws = st.text_input("🔑 Từ khóa nhận diện (cách nhau dấu phẩy):", placeholder="VD: homomorphic, đồng cấu, fhe", key=f"tr_kw_{widget_key}")
        t_content = st.text_area("📖 Nội dung kiến thức / Ý kiến đóng góp:", placeholder="Nhập định nghĩa, công thức hoặc góp ý cho AI...", height=90, key=f"tr_cnt_{widget_key}")

        if st.button("🧠 Lưu vào Bộ Nhớ Tự Học của AI", type="primary", key=f"btn_tr_{widget_key}", use_container_width=True):
            if t_topic.strip() and t_content.strip():
                kw_list = [k.strip().lower() for k in t_kws.split(",") if k.strip()] or [w.lower() for w in t_topic.split() if len(w) > 2]
                mem_db["learned_facts"].insert(0, {
                    "topic": t_topic.strip(),
                    "keywords": kw_list,
                    "content": t_content.strip(),
                    "taught_by": st.session_state.get("ctf_user") or "User",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                })
                save_ai_memory(mem_db)
                st.balloons()
                st.success(f"🎉 Đã huấn luyện thành công chủ đề **`{t_topic.strip()}`**! Hãy thử hỏi lại bên tab Chat AI!")
            else:
                st.warning("Vui lòng nhập cả Chủ đề và Nội dung kiến thức!")

        with st.expander(f"📚 Xem {len(mem_db.get('learned_facts', []))} kiến thức AI đã tự học"):
            for idx, f_item in enumerate(mem_db.get("learned_facts", [])):
                st.markdown(f"**{idx+1}. {f_item['topic']}** *(bởi `{f_item.get('taught_by', 'User')}`)*")
                st.caption(f_item["content"])

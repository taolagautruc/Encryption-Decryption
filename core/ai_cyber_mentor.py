import streamlit as st
import json
import os
import re
import html
import base64
import hashlib
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from PIL import Image
import io

AI_MEMORY_FILE = "ai_mentor_memory_db.json"

# Mật khẩu Admin mặc định là "HCMUS3001" (Lưu dưới dạng băm SHA-256 an toàn)
DEFAULT_ADMIN_PIN_HASH = hashlib.sha256(b"HCMUS3001").hexdigest()

# ==============================================================================
# 1. KHO TRI THỨC NỀN TẢNG ĐA NGÔN NGỮ (ENGLISH DEFAULT + VIETNAMESE)
# ==============================================================================
CORE_KNOWLEDGE_BASE = [
    {
        "id": "KB_CHAR_ENC",
        "keywords": ["character encoding", "mã hóa ký tự", "utf-8", "utf8", "utf-16", "utf-32", "ascii", "unicode", "7-bit"],
        "en": (
            "🔤 **1. Character Encoding (Text-to-Binary Representation):**\n"
            "- **UTF-8:** The dominant character encoding across the web (~90% of all websites). It uses 1 to 4 bytes per character, supports all global languages, and is 100% backward-compatible with ASCII.\n"
            "- **UTF-16 / UTF-32:** Uses 2 to 4 bytes per character, widely used in internal OS memory and runtime environments.\n"
            "- **ASCII:** Foundational 7-bit encoding standard (128 characters, `0–127`) representing English letters (`A=65`, `a=97`), digits (`0=48`), and control symbols."
        ),
        "vi": (
            "🔤 **1. Mã hóa ký tự (Character Encoding):**\n"
            "- **UTF-8:** Kiểu mã hóa ký tự phổ biến nhất trên web (~90% trang web). Hỗ trợ đa ngôn ngữ (1–4 bytes/ký tự) và tương thích ngược hoàn hảo với ASCII.\n"
            "- **UTF-16 / UTF-32:** Dùng 2 đến 4 byte cho mỗi ký tự, thường dùng trong lưu trữ nội bộ hệ điều hành hoặc ứng dụng lập trình.\n"
            "- **ASCII:** Bộ mã hóa 7-bit cơ bản gồm 128 ký tự (`0–127`) cho chữ cái tiếng Anh (`A=65`, `a=97`), chữ số (`0=48`) và ký tự đặc biệt."
        )
    },
    {
        "id": "KB_DATA_BIN_ENC",
        "keywords": ["base64", "url encode", "percent encoding", "html encode", "xss", "entity", "%20", "jwt", "data uri", "nhị phân sang văn bản", "binary encoding"],
        "en": (
            "🔄 **2. Data & Binary-to-Text Encoding:**\n"
            "- **Base64:** Converts raw binary data (3 bytes = 24 bits) into 4 safe ASCII characters (6 bits each). Used for HTML `Data URIs`, email attachments (MIME), and `JWT` tokens.\n"
            "- **URL Encode (Percent Encoding):** Converts spaces and unsafe URL characters into `%XX` hexadecimal format (e.g., space becomes `%20`).\n"
            "- **HTML Encode:** Converts special HTML syntax characters (`<`, `>`, `&`) into entities (`&lt;`, `&gt;`, `&amp;`) to prevent rendering errors and block **XSS (Cross-Site Scripting)** attacks."
        ),
        "vi": (
            "🔄 **2. Mã hóa dữ liệu / Nhị phân sang văn bản (Data & Binary Encoding):**\n"
            "- **Base64:** Chuyển đổi dữ liệu nhị phân (3 bytes = 24 bits) thành 4 ký tự ASCII (6-bit). Thường dùng đính kèm ảnh vào HTML (`Data URI`), gửi Email hoặc `JWT` token.\n"
            "- **URL Encode (Percent Encoding):** Chuyển ký tự đặc biệt hoặc dấu cách trong URL sang dạng an toàn (ví dụ: dấu cách thành `%20`).\n"
            "- **HTML Encode:** Chuyển `<`, `>`, `&` thành thực thể (`&lt;`, `&gt;`, `&amp;`) để chống lỗi hiển thị và ngăn chặn tấn công **XSS**."
        )
    },
    {
        "id": "KB_MULTIMEDIA_ENC",
        "keywords": ["multimedia encoding", "mã hóa đa phương tiện", "codec", "h.264", "h.265", "hevc", "avc", "vp9", "av1", "mp4", "mkv", "mp3", "aac", "flac", "ogg", "video", "audio"],
        "en": (
            "🎬 **3. Multimedia Encoding (Video & Audio Codecs):**\n"
            "- **Video Codecs & Containers:** `H.264 (AVC)`, `H.265 (HEVC)`, `VP9`, `AV1`, packaged inside `MP4` or `MKV` containers.\n"
            "- **Audio Formats:** Lossy compression (`MP3`, `AAC`, `OGG`) vs. Lossless compression (`FLAC`, `WAV PCM`).\n"
            "- 💡 *Steganography Rule:* Always use **Lossless formats (`PNG`, `WAV`)** for LSB bit-hiding because lossy codecs (`JPG`, `MP3`) alter pixel/sample values and destroy hidden payloads!"
        ),
        "vi": (
            "🎬 **3. Mã hóa đa phương tiện (Multimedia Encoding):**\n"
            "- **Video:** Các codec/định dạng phổ biến gồm `H.264 (AVC)`, `H.265 (HEVC)`, `VP9`, `AV1`, `MP4`, `MKV`.\n"
            "- **Âm thanh:** Các chuẩn phổ biến gồm `MP3`, `AAC`, `FLAC` (nén bảo toàn), `OGG`, `WAV`.\n"
            "- 💡 *Quy tắc Giấu tin (Steganography):* Luôn dùng định dạng không nén hao hụt (`PNG`, `WAV`) khi giấu bit LSB vì `JPG` hay `MP3` sẽ làm hỏng các bit cuối!"
        )
    },
    {
        "id": "KB_ML_ENC",
        "keywords": ["categorical encoding", "machine learning", "khoa học dữ liệu", "one-hot", "one hot", "label encoding", "ordinal encoding", "target encoding", "học máy"],
        "en": (
            "🤖 **4. Machine Learning / Data Science Categorical Encoding:**\n"
            "- **One-Hot Encoding:** Creates binary (`0` or `1`) vector columns for each distinct category.\n"
            "- **Label / Ordinal Encoding:** Maps each text category to a fixed integer (`0, 1, 2...`), preserving order for ordinal data.\n"
            "- **Target Encoding:** Replaces a categorical value with the statistical mean of the target variable corresponding to that category."
        ),
        "vi": (
            "🤖 **4. Mã hóa trong Khoa học dữ liệu / Machine Learning (Categorical Encoding):**\n"
            "- **One-Hot Encoding:** Tạo ra các cột nhị phân (`0` hoặc `1`) tương ứng với từng giá trị danh mục.\n"
            "- **Label / Ordinal Encoding:** Gán mỗi giá trị chữ bằng một số nguyên cố định (`0, 1, 2...`).\n"
            "- **Target Encoding:** Thay thế giá trị danh mục bằng giá trị trung bình của biến mục tiêu (target) tương ứng."
        )
    },
    {
        "id": "KB_BINARY_BITS",
        "keywords": ["nhị phân", "binary", "bit", "nibble", "byte", "hex", "hexadecimal", "bù 2", "two's complement", "bitwise", "xor", "and", "shift", "dịch bit", "endian", "little-endian"],
        "en": (
            "💻 **Core Binary, Bits & Computer Architecture (Lessons 04–09):**\n"
            "- **1 Bit:** `0` or `1` | **1 Nibble (4 bits):** `0..15` (1 Hex digit `0..F`) | **1 Byte (8 bits):** $2^8 = 256$ values (`0..255`) with bit weights `128, 64, 32, 16, 8, 4, 2, 1`.\n"
            "- **Two's Complement (Signed Integers):** The MSB has weight `-128`. To negate $+X \\rightarrow -X$: invert all bits (`~X`) and add `1`.\n"
            "- **Bitwise Operations:** `AND (&)` masks bits (`R & 1` extracts LSB), `XOR (^)` is self-inverting (`(P ^ K) ^ K = P`), `X << k` multiplies by $2^k$, `X >> k` divides by $2^k$."
        ),
        "vi": (
            "💻 **Kiến thức Cốt lõi về Hệ Nhị Phân (Binary), Bits & Kiến trúc Máy tính (Bài 04–09):**\n"
            "- **1 Bit:** `0` hoặc `1` | **1 Nibble (4 bits):** `0..15` (1 chữ số Hex `0..F`) | **1 Byte (8 bits):** $2^8 = 256$ giá trị (`0..255`) với trọng số `128, 64, 32, 16, 8, 4, 2, 1`.\n"
            "- **Số nguyên có dấu Bù 2 (Two's Complement):** Để đổi $+X \\rightarrow -X$, đảo toàn bộ các bit (`~X`) rồi cộng thêm `1`.\n"
            "- **Phép toán Bitwise:** `AND (&)` lọc bit (`R & 1` lấy LSB); `XOR (^)` khả nghịch (`A ^ K ^ K = A`); Dịch trái `X << k` nhân với $2^k$, dịch phải `X >> k` chia nguyên cho $2^k$."
        )
    },
    {
        "id": "KB_CRYPTO_SUITE",
        "keywords": ["caesar", "affine", "vigenere", "atbash", "rail-fence", "aes", "rsa", "sha-256", "sha256", "quantum", "shor", "grover", "steganography", "lsb", "one-time pad", "otp", "mật mã"],
        "en": (
            "🔐 **Cryptography & Steganography Suite (Lessons 01–03 & 10–20):**\n"
            "- **Encoding vs. Encryption vs. Hashing:** Encoding (UTF-8, Base64) uses no secret key; Encryption (AES, RSA) requires a key to decrypt; Hashing (SHA-256) is strictly one-way.\n"
            "- **Classical Ciphers:** Caesar `(P + K) mod 26`, Affine `(aP + b) mod 26` with `gcd(a,26)=1`, Atbash mirror `A↔Z`, Rail-Fence, and Vigenère.\n"
            "- **Modern & Quantum:** AES-256 (128-bit blocks, 14 rounds), RSA (`C = M^e mod N`), Shor's algorithm (breaks RSA/ECC), and Grover's algorithm (quadratic speedup)."
        ),
        "vi": (
            "🔐 **Tổng hợp Thuật toán Mật mã & Giấu tin (Bài 01–03 & 10–20):**\n"
            "- **Encoding vs. Encryption vs. Hashing:** Encoding không dùng khóa; Encryption cần khóa bí mật để giải mã; Hashing (SHA-256) là hàm băm 1 chiều.\n"
            "- **Mật mã Cổ điển:** Caesar `(P + K) mod 26`, Affine `(aP + b) mod 26`, Atbash `A↔Z`, Rail-Fence và Vigenère.\n"
            "- **Hiện đại & Lượng tử:** AES-256 (khối 16 bytes, 14 vòng), RSA (`C = M^e mod N`), thuật toán Shor và Grover."
        )
    }
]

ALLOWED_DOMAIN_KEYWORDS = {
    "mật mã", "mã hóa", "giải mã", "cipher", "crypto", "cryptography", "encode", "encoding", "decode",
    "utf", "ascii", "unicode", "base64", "url", "html", "xss", "percent", "multimedia", "video", "audio",
    "h.264", "h.265", "hevc", "av1", "vp9", "mp3", "mp4", "flac", "wav", "png", "lsb", "steganography", "giấu tin",
    "one-hot", "onehot", "label", "ordinal", "target", "machine learning", "học máy", "data", "dữ liệu",
    "nhị phân", "binary", "bit", "bits", "byte", "bytes", "nibble", "hex", "hexadecimal", "decimal", "thập phân",
    "bù 2", "complement", "overflow", "bitwise", "xor", "and", "shift", "dịch", "assembly", "rax", "mov", "shl", "shr",
    "endian", "little-endian", "big-endian", "caesar", "rot13", "atbash", "affine", "vigenere", "rail-fence", "transposition",
    "modulo", "mod", "inverse", "nghịch đảo", "coprime", "frequency", "tần suất", "otp", "one-time pad", "shannon", "entropy",
    "sha", "sha-256", "hash", "băm", "salt", "rainbow", "aes", "ecb", "gcm", "cbc", "rsa", "diffie", "public key", "private key",
    "prime", "totient", "phi", "quantum", "lượng tử", "qubit", "shor", "grover", "lattice", "kyber", "enigma", "elliptic", "ecc",
    "zero-knowledge", "zkp", "homomorphic", "block cipher", "stream cipher", "kerckhoffs", "hmac", "digital signature", "tls", "ssl",
    "bài", "lesson", "module", "track", "lab", "quiz", "câu hỏi", "đáp án", "hint", "gợi ý", "sudoku", "ctf", "web", "app",
    "camouflage", "ngụy trang", "morse", "visual", "pháp y", "forensic", "password", "mật khẩu", "key", "khóa", "security", "bảo mật",
    "hello", "hi", "xin chào", "chào", "help", "giúp", "hướng dẫn", "explain", "giải thích", "là gì", "what", "how", "why",
    "was ist", "qu'est-ce", "qué es", "kryptographie", "chiffrement", "cifrado"
}

OFF_TOPIC_KEYWORDS = {
    "nấu ăn", "công thức nấu", "phở", "bún bò", "bóng đá", "ngoại hạng anh", "world cup", "messi", "ronaldo",
    "thời tiết", "xổ số", "lô đề", "tử vi", "bói toán", "cung hoàng đạo", "người yêu", "tình yêu", "thất tình",
    "recipe", "cooking", "football", "soccer", "weather", "horoscope", "astrology", "dating", "boyfriend", "girlfriend"
}

# Danh sách các chủ đề Mật mã học chuẩn Quốc tế để Admin bấm 1 nút là AI tự động thu thập từ Wikipedia
AUTO_HARVEST_TOPICS = [
    ("Enigma machine", ["enigma", "rotor", "turing"]),
    ("Elliptic-curve cryptography", ["ecc", "elliptic", "curve"]),
    ("Diffie–Hellman key exchange", ["diffie", "hellman", "dh", "key exchange"]),
    ("Homomorphic encryption", ["homomorphic", "fhe", "đồng cấu"]),
    ("Zero-knowledge proof", ["zkp", "zero-knowledge", "zero knowledge"]),
    ("Digital signature", ["digital signature", "chữ ký số", "ecdsa"]),
    ("Block cipher mode of operation", ["cbc", "gcm", "ctr", "ecb", "block mode"]),
    ("Cryptographic hash function", ["md5", "sha-1", "sha-3", "keccak", "collision"]),
    ("Public-key cryptography", ["asymmetric", "public key", "private key", "bất đối xứng"]),
    ("Post-quantum cryptography", ["post-quantum", "pqc", "kyber", "dilithium", "lattice"])
]


def load_ai_memory() -> dict:
    if not os.path.exists(AI_MEMORY_FILE):
        default_mem = {
            "admin_pin_hash": DEFAULT_ADMIN_PIN_HASH,
            "gemini_api_key": "",
            "learned_facts": [
                {
                    "topic": "Post-Quantum Cryptography & AI Security (2026 Standard)",
                    "keywords": ["trend", "2026", "ai security", "ml-kem", "post-quantum", "xu hướng"],
                    "content": "Modern cryptographic infrastructure is migrating to NIST Post-Quantum standards (ML-KEM / CRYSTALS-Kyber for key encapsulation and ML-DSA for digital signatures) combined with AI-driven anomaly detection and strict Anti-Data-Poisoning guardrails.",
                    "taught_by": "Admin_Core",
                    "timestamp": "2026-10-25 UTC"
                }
            ],
            "pending_suggestions": []
        }
        with open(AI_MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(default_mem, f, ensure_ascii=False, indent=4)
        return default_mem
    try:
        with open(AI_MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "admin_pin_hash" not in data:
                data["admin_pin_hash"] = DEFAULT_ADMIN_PIN_HASH
            if "pending_suggestions" not in data:
                data["pending_suggestions"] = []
            return data
    except Exception:
        return {"admin_pin_hash": DEFAULT_ADMIN_PIN_HASH, "learned_facts": [], "pending_suggestions": []}


def save_ai_memory(data: dict):
    with open(AI_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def detect_user_language(text: str) -> str:
    """
    Nhận diện ngôn ngữ người dùng:
    - Nếu có ký tự/từ Tiếng Việt -> 'vi'
    - Nếu có tiếng Đức/Pháp/Tây Ban Nha/Nhật/Hàn -> mã ngôn ngữ tương ứng
    - Mặc định toàn cầu -> 'en' (Tiếng Anh Quốc tế)
    """
    low = text.lower()
    vn_chars = set("àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ")
    if any(c in vn_chars for c in low) or any(w in low for w in ["là gì", "như thế nào", "giải thích", "bài học", "nhị phân", "mã hóa", "gợi ý"]):
        return "vi"
    if any(w in low for w in ["was ist", "wie funktioniert", "verschlüsselung", "erkläre"]):
        return "de"
    if any(w in low for w in ["qu'est-ce", "chiffrement", "expliquer", "comment"]):
        return "fr"
    if any(w in low for w in ["qué es", "cifrado", "explicar", "cómo"]):
        return "es"
    return "en"


def fetch_wikipedia_crypto_summary(query_term: str, lang_code: str = "en") -> tuple[bool, str, str]:
    """
    Tự động tra cứu Bách khoa toàn thư Wikipedia REST API theo đúng ngôn ngữ người dùng hỏi
    để AI tự học kiến thức mới mà Admin không cần gõ tay.
    """
    clean_q = re.sub(
        r'^(what is|what are|explain|define|how does|tell me about|là gì|giải thích|khái niệm|was ist|qu\'est-ce que|qué es)\s+',
        '', query_term.strip(), flags=re.IGNORECASE
    ).strip(" ?!.,")
    if len(clean_q) < 2:
        return False, "", ""

    wiki_lang = lang_code if lang_code in ["en", "vi", "de", "fr", "es"] else "en"
    search_url = f"https://{wiki_lang}.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(clean_q)}&limit=1&namespace=0&format=json"

    try:
        req = urllib.request.Request(search_url, headers={"User-Agent": "USM-CyberMentor/2.0 (HCMUS Educational Suite)"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            search_data = json.loads(resp.read().decode("utf-8"))
            if not search_data or len(search_data) < 2 or not search_data[1]:
                if wiki_lang != "en":
                    return fetch_wikipedia_crypto_summary(clean_q, "en")
                return False, "", ""
            best_title = search_data[1][0]

        sum_url = f"https://{wiki_lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(best_title.replace(' ', '_'))}"
        req_sum = urllib.request.Request(sum_url, headers={"User-Agent": "USM-CyberMentor/2.0 (HCMUS Educational Suite)"})
        with urllib.request.urlopen(req_sum, timeout=4) as resp2:
            sum_data = json.loads(resp2.read().decode("utf-8"))
            extract = sum_data.get("extract", "").strip()
            if len(extract) > 40:
                return True, best_title, extract
    except Exception:
        pass
    return False, "", ""


def call_optional_gemini_llm(query: str, current_lesson: dict, api_key: str) -> str:
    """Nếu Admin có nhập Gemini API Key, gọi trực tiếp mô hình đa ngôn ngữ (100+ thứ tiếng)."""
    if not api_key:
        return ""
    les_info = f"Current Lesson: {current_lesson.get('id')} - {current_lesson.get('title')}. Overview: {current_lesson.get('overview')}" if current_lesson else "Global Security Academy"
    sys_prompt = (
        "You are AI Cyber Mentor for the Ultimate Secret Messenger & Security Academy platform created by Le Hoang Phu Hieu (FIT-HCMUS). "
        "CRITICAL RULES:\n"
        "1. ALWAYS reply in the EXACT SAME LANGUAGE that the user used in their question (e.g., if asked in English, reply in English; if German, reply in German; if Vietnamese, reply in Vietnamese).\n"
        "2. If the user asks about something unrelated to Cryptography, Character/Data/Multimedia/ML Encoding (UTF-8, Base64, URL/HTML Encode, One-Hot), Binary/Bits, Computer Architecture, or the Security Academy lessons, politely refuse and remind them to stay on topic.\n"
        f"3. Context: {les_info}"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key.strip()}"
    payload = {
        "contents": [{"parts": [{"text": f"{sys_prompt}\n\nUser Question: {query}"}]}]
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return ""


def is_query_on_topic(query: str, mem_db: dict) -> bool:
    low = query.lower()
    if any(bad in low for bad in OFF_TOPIC_KEYWORDS):
        return False
    if any(good in low for good in ALLOWED_DOMAIN_KEYWORDS):
        return True
    for fact in mem_db.get("learned_facts", []):
        if any(kw.lower() in low for kw in fact.get("keywords", [])):
            return True
    if re.search(r'\b[01]{4,}\b|\b0x[0-9a-f]+\b|\bmod\b|<<|>>', low):
        return True
    return False


def try_live_computation(query: str, lang: str) -> str:
    q_clean = query.strip()
    low = q_clean.lower()

    nums = re.findall(r'\b\d+\b', q_clean)
    if nums and any(k in low for k in ["binary", "nhị phân", "hex", "bù 2", "complement", "bit"]):
        n = int(nums[0])
        if 0 <= n <= 255:
            twos = f"{(256 - n) & 0xFF:08b}" if n > 0 else "00000000"
            if lang == "vi":
                return (
                    f"🧮 **Kết quả tính toán trực tiếp cho số `{n}`:**\n"
                    f"- **Nhị phân 8-bit (Unsigned):** `{n:08b}` (High nibble: `{n>>4:04b}`, Low nibble: `{n&15:04b}`)\n"
                    f"- **Hexadecimal:** `0x{n:02X}` | **Số âm `-{n}` (Bù 2):** `{twos}`"
                )
            return (
                f"🧮 **Live Binary & Hex Computation for `{n}`:**\n"
                f"- **8-Bit Binary:** `{n:08b}` (High nibble: `{n>>4:04b}`, Low nibble: `{n&15:04b}`)\n"
                f"- **Hexadecimal:** `0x{n:02X}` | **Two's Complement (`-{n}`):** `{twos}`"
            )

    quote_match = re.findall(r'["\']([^"\']+)["\']', q_clean)
    if quote_match and any(k in low for k in ["encode", "mã hóa", "base64", "url", "html", "utf-8", "ascii"]):
        sample = quote_match[0]
        b64 = base64.b64encode(sample.encode("utf-8")).decode("utf-8")
        url_e = urllib.parse.quote(sample)
        html_e = html.escape(sample)
        utf8_hex = " ".join(f"{b:02X}" for b in sample.encode("utf-8"))
        if lang == "vi":
            return (
                f"⚡ **Kết quả Encode trực tiếp cho `'{sample}'`:**\n"
                f"- **UTF-8 Hex Bytes:** `{utf8_hex}` ({len(sample.encode('utf-8'))} bytes)\n"
                f"- **Base64:** `{b64}` | **URL Encode:** `{url_e}` | **HTML Encode:** `{html_e}`"
            )
        return (
            f"⚡ **Live Encoding Results for `'{sample}'`:**\n"
            f"- **UTF-8 Hex Bytes:** `{utf8_hex}` ({len(sample.encode('utf-8'))} bytes)\n"
            f"- **Base64:** `{b64}` | **URL Encode:** `{url_e}` | **HTML Encode:** `{html_e}`"
        )
    return ""


def generate_ai_mentor_response(query: str, current_lesson: dict, mem_db: dict) -> str:
    lang = detect_user_language(query)
    kb_lang = "vi" if lang == "vi" else "en"
    low = query.lower().strip()

    # 1. Kiểm tra Lạc Đề (Strict Domain Guardrail)
    if not is_query_on_topic(query, mem_db):
        if lang == "vi":
            return (
                "⚠️ **Nhắc nhở từ AI Cyber Mentor:** Câu hỏi của bạn nằm ngoài phạm vi bài học. "
                "Vui lòng chỉ hỏi các chủ đề liên quan đến **Mật mã học, 4 Trụ cột Encoding (UTF-8, Base64, URL/HTML Encode, Multimedia, One-Hot ML), Hệ Nhị Phân (Bits/Bytes) và 20 Bài học trong Security Academy**!"
            )
        return (
            "⚠️ **Topic Reminder from AI Cyber Mentor:** Your question appears to be off-topic. "
            "I am strictly trained to assist you with **Cryptography, the 4 Encoding Pillars (UTF-8/ASCII, Base64/URL/HTML, Multimedia Codecs, ML Categorical Encoding), Binary/Bits, Steganography, and the 20 Security Academy Modules**. Please ask a question related to these topics!"
        )

    # 2. Nếu Admin đã kết nối Gemini API Key -> Trả lời đa ngôn ngữ bằng LLM
    api_key = mem_db.get("gemini_api_key", "")
    try:
        if not api_key and "GEMINI_API_KEY" in st.secrets:
            api_key = str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
    if api_key:
        llm_ans = call_optional_gemini_llm(query, current_lesson, api_key)
        if llm_ans:
            return llm_ans

    # 3. Kiểm tra Bộ Nhớ Đã Kiểm Duyệt của Admin
    matched_learned = []
    for fact in mem_db.get("learned_facts", []):
        if any(kw in low for kw in fact.get("keywords", [])) or fact["topic"].lower() in low:
            matched_learned.append(f"🧠 **[{fact['topic']}]:**\n{fact['content']}")

    # 4. Kiểm tra Tính toán Trực tiếp (Binary / Hex / Encoding)
    live_calc = try_live_computation(query, kb_lang)

    # 5. Kiểm tra Bài học đang mở (Current Lesson Walkthrough)
    lesson_context_reply = ""
    if current_lesson and any(k in low for k in ["this lesson", "current lesson", "bài này", "bài hiện tại", "quiz", "lab", "hint", "gợi ý", "đáp án", "summary", "explain lesson"]):
        lid = current_lesson.get("id", "L01")
        ltitle = current_lesson.get("title", "")
        if kb_lang == "vi":
            lesson_context_reply = (
                f"📘 **Hướng dẫn Bài học đang mở ({lid} — {ltitle}):**\n"
                f"- **Trọng tâm:** {current_lesson.get('overview', '')}\n"
                f"- **Đáp án Quiz 1:** `{current_lesson.get('q1_ans', '')}` | **Quiz 2:** `{current_lesson.get('q2_ans', '')}`\n"
                f"- **Hướng dẫn Lab 1:** {current_lesson.get('lab1_q', '')} $\\rightarrow$ **`{current_lesson.get('lab1_ans', '')}`**\n"
                f"- **Hướng dẫn Lab 2:** {current_lesson.get('lab2_q', '')} $\\rightarrow$ **`{current_lesson.get('lab2_ans', '')}`**"
            )
        else:
            lesson_context_reply = (
                f"📘 **Active Module Guide ({lid} — {ltitle}):**\n"
                f"- **Core Concept:** {current_lesson.get('overview', '')}\n"
                f"- **Quiz 1 Key:** `{current_lesson.get('q1_ans', '')}` | **Quiz 2 Key:** `{current_lesson.get('q2_ans', '')}`\n"
                f"- **Lab 1 Solution:** {current_lesson.get('lab1_q', '')} $\\rightarrow$ **`{current_lesson.get('lab1_ans', '')}`**\n"
                f"- **Lab 2 Solution:** {current_lesson.get('lab2_q', '')} $\\rightarrow$ **`{current_lesson.get('lab2_ans', '')}`**"
            )

    # 6. Tra cứu Kho Tri Thức Cốt Lõi
    kb_matches = [item[kb_lang] for item in CORE_KNOWLEDGE_BASE if any(kw in low for kw in item["keywords"])]

    parts = [p for p in (matched_learned + ([live_calc] if live_calc else []) + ([lesson_context_reply] if lesson_context_reply else []) + kb_matches) if p]
    if parts:
        return "\n\n---\n\n".join(parts[:3])

    # 7. TỰ ĐỘNG TRA CỨU & TỰ HỌC TỪ WIKIPEDIA QUỐC TẾ NẾU CHỦ ĐỀ CHƯA CÓ TRONG BỘ NHỚ
    ok_wiki, wiki_title, wiki_extract = fetch_wikipedia_crypto_summary(query, lang)
    if ok_wiki:
        # Tự động lưu vào bộ nhớ đã xác thực từ Wikipedia
        kws_auto = [w.lower() for w in re.split(r'\W+', wiki_title) if len(w) >= 3]
        mem_db["learned_facts"].insert(0, {
            "topic": f"{wiki_title} (Verified Encyclopedia)",
            "keywords": kws_auto or [wiki_title.lower()],
            "content": wiki_extract,
            "taught_by": f"Auto_Wiki_{lang.upper()}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        })
        save_ai_memory(mem_db)
        return f"🌐 **[{wiki_title} — Autonomous Encyclopedia Lookup & Learned]:**\n\n{wiki_extract}"

    # 8. Phản hồi mặc định theo ngôn ngữ người hỏi
    lid = current_lesson.get("id", "L01") if current_lesson else "Global"
    ltitle = current_lesson.get("title", "Security Academy") if current_lesson else "Security Academy"
    if kb_lang == "vi":
        return (
            f"👋 Xin chào! Tôi là **AI Cyber Mentor** (Đang theo dõi: **{lid} — {ltitle}**).\n"
            f"- Hãy gõ **'Explain this lesson'** hoặc **'Gợi ý bài này'** để xem hướng dẫn Quiz & Lab.\n"
            f"- Hỏi bất kỳ thuật ngữ nào về **UTF-8, Base64, URL/HTML Encode, One-Hot, Binary/Bits, AES, RSA, Enigma...** bằng Tiếng Anh hoặc Tiếng Việt!"
        )
    return (
        f"👋 Hello! I am your **AI Cyber Mentor** (Tracking: **{lid} — {ltitle}**).\n"
        f"- Type **'Explain this lesson'** or **'Hint'** for step-by-step Quiz & Lab guidance.\n"
        f"- Ask me in **English** (or your native language) about **Character/Data/Multimedia/ML Encoding (`UTF-8`, `Base64`, `URL %20`, `One-Hot`), Binary & Bits, AES, RSA, Steganography**, or any cryptography topic!"
    )


def analyze_uploaded_file_or_image(uploaded_file, decode_lsb_fn=None, decode_audio_fn=None) -> str:
    fname = uploaded_file.name
    raw_bytes = uploaded_file.getvalue()
    fsize = len(raw_bytes)
    ext = fname.split(".")[-1].lower() if "." in fname else ""

    report = [f"📎 **AI Forensic File Analysis for `{fname}` ({fsize:,} bytes):**"]

    if ext in ["png", "jpg", "jpeg"]:
        try:
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            w, h = img.size
            max_lsb_bytes = (w * h * 3) // 8 - 13
            report.append(f"- 🖼️ **Image Format:** `{ext.upper()}` | Resolution: `{w} x {h}` px (`{w*h:,}` pixels).")
            report.append(f"- 📊 **Max LSB Stego Capacity:** `~{max_lsb_bytes:,} bytes`.")
            if decode_lsb_fn and ext == "png":
                ok_lsb, hidden_pay = decode_lsb_fn(img)
                if ok_lsb:
                    report.append(f"- 🎯 **HIDDEN LSB PAYLOAD DETECTED:** `{hidden_pay}`")
                else:
                    report.append("- 🔍 **LSB Scan:** No `<<END_STEGO>>` hidden payload found in this image.")
        except Exception as e:
            report.append(f"- ❌ Image read error: {str(e)}")
    elif ext == "wav":
        report.append("- 🎵 **Audio Format:** `16-bit PCM WAV Audio`.")
        if decode_audio_fn:
            ok_aud, aud_pay = decode_audio_fn(raw_bytes)
            if ok_aud:
                report.append(f"- 🎯 **HIDDEN AUDIO LSB PAYLOAD DETECTED:** `{aud_pay}`")
            else:
                report.append("- 🔍 **WAV LSB Scan:** No hidden payload detected.")
    else:
        first_16_hex = " ".join(f"{b:02X}" for b in raw_bytes[:16])
        first_4_bin = " ".join(f"{b:08b}" for b in raw_bytes[:4])
        report.append(f"- 💻 **First 16 Hex Bytes:** `{first_16_hex}`")
        report.append(f"- 🔢 **First 4 Binary Bytes (32 bits):** `{first_4_bin}`")
        try:
            txt_content = raw_bytes.decode("utf-8")
            is_ascii = all(ord(c) < 128 for c in txt_content)
            enc_type = "7-Bit ASCII (UTF-8 Compatible)" if is_ascii else "Multi-Byte UTF-8 Unicode"
            report.append(f"- 🔤 **Character Encoding:** `{enc_type}` ({len(txt_content)} chars).")
            report.append(f"- 📄 **Text Preview:** `{txt_content[:180].replace(chr(10), ' ')}...`")
        except Exception:
            b64_preview = base64.b64encode(raw_bytes[:45]).decode("utf-8")
            report.append(f"- 📦 **Raw Binary -> Base64 Preview:** `{b64_preview}...`")

    return "\n".join(report)


def render_ai_cyber_mentor_widget(current_lesson: dict = None, decode_lsb_fn=None, decode_audio_fn=None, widget_key: str = "acad_ai"):
    """
    Giao diện Quốc tế hóa 100% Tiếng Anh (International UI):
    - Trả lời theo đúng ngôn ngữ người hỏi (English Default / Multilingual Wiki / Vietnamese).
    - Khóa tính năng Train AI bằng mật khẩu Admin (Người dùng thường chỉ được gửi đề xuất vào hàng đợi duyệt).
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

    active_lid = current_lesson.get("id", "Global") if current_lesson else "Global"
    learned_cnt = len(mem_db.get("learned_facts", []))

    st.markdown(f"""
    <div class="ai-mentor-header">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="ai-mentor-badge">🤖 AI CYBER MENTOR • MODULE {active_lid}</span>
            <span style="font-size:0.72rem; color:#34d399; font-weight:700;">🧠 Verified KB: {learned_cnt} Topics</span>
        </div>
        <div style="font-size:1.06rem; font-weight:800; color:#f8fafc; margin-top:6px;">Multilingual Cryptography & CS Tutor</div>
        <div style="font-size:0.77rem; color:#94a3b8; margin-top:2px;">Ask in English or your native language • Auto-Encyclopedia Lookup • File/Image Scanner</div>
    </div>
    """, unsafe_allow_html=True)

    chat_hist_key = f"ai_mentor_history_{widget_key}"
    if chat_hist_key not in st.session_state:
        st.session_state[chat_hist_key] = [
            {
                "role": "assistant",
                "content": (
                    "👋 **Welcome! I am your AI Cyber Mentor.**\n"
                    "- Ask me in **English** (or your native language) about **the active lesson**, **Binary & Bits**, or **the 4 Encoding Pillars** (`UTF-8/ASCII`, `Base64/URL/HTML`, `Video/Audio Codecs`, `One-Hot/Label ML`).\n"
                    "- I also automatically look up verified cryptography concepts from international encyclopedias!"
                )
            }
        ]

    tab_chat, tab_attach, tab_admin = st.tabs([
        "💬 Ask AI",
        "📎 Scan File/Image",
        "🔐 Admin & Feedback"
    ])

    # ==========================================================================
    # TAB 1: MULTILINGUAL AI CHAT
    # ==========================================================================
    with tab_chat:
        q_c1, q_c2 = st.columns(2)
        with q_c1:
            if st.button("📘 Lesson Guide & Hints", key=f"q_les_{widget_key}", use_container_width=True):
                ans = generate_ai_mentor_response("Explain this lesson and give quiz/lab hints", current_lesson, mem_db)
                st.session_state[chat_hist_key].append({"role": "user", "content": "📘 Explain this lesson & show hints"})
                st.session_state[chat_hist_key].append({"role": "assistant", "content": ans})
                st.rerun()
        with q_c2:
            if st.button("🔤 4 Encoding Pillars", key=f"q_enc_{widget_key}", use_container_width=True):
                ans = generate_ai_mentor_response("Explain Character Encoding UTF-8, Base64 URL HTML, Multimedia, and One-Hot ML Encoding", current_lesson, mem_db)
                st.session_state[chat_hist_key].append({"role": "user", "content": "🔤 Summarize the 4 Encoding Pillars"})
                st.session_state[chat_hist_key].append({"role": "assistant", "content": ans})
                st.rerun()

        msg_box = st.container(height=340, border=True)
        with msg_box:
            for msg in st.session_state[chat_hist_key]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_q = st.chat_input("Ask in English or your language (e.g. 'What is Base64?', 'Binary 42')...", key=f"in_ai_{widget_key}")
        if user_q and user_q.strip():
            st.session_state[chat_hist_key].append({"role": "user", "content": user_q.strip()})
            ai_reply = generate_ai_mentor_response(user_q.strip(), current_lesson, mem_db)
            st.session_state[chat_hist_key].append({"role": "assistant", "content": ai_reply})
            st.rerun()

        if len(st.session_state[chat_hist_key]) > 2:
            if st.button("🧹 Clear AI Chat", key=f"clr_ai_{widget_key}", use_container_width=True):
                st.session_state[chat_hist_key] = st.session_state[chat_hist_key][:1]
                st.rerun()

    # ==========================================================================
    # TAB 2: FORENSIC FILE & IMAGE SCANNER
    # ==========================================================================
    with tab_attach:
        st.caption("📎 Upload an image (`.png, .jpg`), audio (`.wav`), or document (`.txt, .json, .csv, .py`) for AI binary byte inspection, UTF-8/ASCII verification, and hidden LSB steganography scanning:")
        up_file = st.file_uploader(
            "Select File or Image for AI Analysis:",
            type=["png", "jpg", "jpeg", "wav", "txt", "json", "csv", "py", "md"],
            key=f"up_ai_{widget_key}"
        )
        if up_file:
            if up_file.name.split(".")[-1].lower() in ["png", "jpg", "jpeg"]:
                st.image(up_file, caption=f"Attached: {up_file.name}", use_container_width=True)
            if st.button("🔍 Run AI Forensic File Analysis", type="primary", key=f"btn_anl_{widget_key}", use_container_width=True):
                file_report = analyze_uploaded_file_or_image(up_file, decode_lsb_fn, decode_audio_fn)
                st.session_state[chat_hist_key].append({"role": "user", "content": f"📎 *[Attached `{up_file.name}`]* Analyze this file!"})
                st.session_state[chat_hist_key].append({"role": "assistant", "content": file_report})
                st.success("✅ Analysis complete! Switch to the **💬 Ask AI** tab to view the full report.")

    # ==========================================================================
    # TAB 3: ADMIN-ONLY TRAINING LOCK & USER SUGGESTION MODERATION QUEUE
    # ==========================================================================
    with tab_admin:
        st.markdown("##### 💡 For Students/Users: Suggest a Topic or Feedback")
        st.caption("🔒 To prevent unverified data poisoning, user submissions are sent to the **Admin Moderation Queue** and only enter the AI's memory after the Admin approves them.")

        sug_topic = st.text_input("📌 Suggested Topic / Question:", placeholder="e.g. ChaCha20-Poly1305 cipher", key=f"sug_t_{widget_key}")
        sug_note = st.text_area("📝 Details or Feedback for Admin:", placeholder="Write your suggestion or feedback...", height=68, key=f"sug_n_{widget_key}")
        if st.button("📨 Submit to Admin Review Queue", key=f"btn_sug_{widget_key}", use_container_width=True):
            if sug_topic.strip() and sug_note.strip():
                mem_db.setdefault("pending_suggestions", []).append({
                    "topic": sug_topic.strip(),
                    "note": sug_note.strip(),
                    "user": st.session_state.get("ctf_user") or "Anonymous_Student",
                    "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                })
                save_ai_memory(mem_db)
                st.success("✅ Thank you! Your suggestion has been sent to the Admin review queue.")
            else:
                st.warning("Please fill in both fields.")

        st.divider()
        st.markdown("##### 👑 Admin Training Studio (Creator Only — Lê Hoàng Phú Hiếu)")
        admin_pin_in = st.text_input(
            "🔑 Enter Admin Master PIN to Unlock AI Training:",
            type="password",
            placeholder="Enter Admin PIN...",
            key=f"adm_pin_{widget_key}"
        )

        is_admin_unlocked = (
            hashlib.sha256(admin_pin_in.strip().encode("utf-8")).hexdigest() == mem_db.get("admin_pin_hash", DEFAULT_ADMIN_PIN_HASH)
        ) if admin_pin_in else False

        if not is_admin_unlocked:
            st.info("🔒 **Locked:** Only the platform creator can train the AI, trigger autonomous encyclopedia harvesting, or approve user suggestions.")
        else:
            st.success("🔓 **Admin Verified!** Full AI Training & Autonomous Harvester Unlocked.")

            # 1. Nút cho AI tự động học hàng loạt chủ đề Mật mã học chuẩn từ Wikipedia Quốc tế
            st.markdown("**🌐 1. Autonomous Encyclopedia Harvester (1-Click Auto-Learn):**")
            if st.button("🚀 Auto-Harvest Core Cryptography Topics from Wikipedia", type="primary", key=f"btn_harv_{widget_key}", use_container_width=True):
                existing_topics = {f["topic"].lower() for f in mem_db.get("learned_facts", [])}
                added_count = 0
                for t_name, t_kws in AUTO_HARVEST_TOPICS:
                    if t_name.lower() not in existing_topics:
                        ok_w, w_title, w_ext = fetch_wikipedia_crypto_summary(t_name, "en")
                        if ok_w:
                            mem_db["learned_facts"].insert(0, {
                                "topic": w_title,
                                "keywords": t_kws,
                                "content": w_ext,
                                "taught_by": "Admin_Auto_Harvester",
                                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                            })
                            added_count += 1
                save_ai_memory(mem_db)
                st.balloons()
                st.success(f"🎉 Autonomous Harvester fetched and indexed **{added_count} verified cryptography topics** from Wikipedia!")

            st.divider()
            # 2. Huấn luyện thủ công bởi Admin
            st.markdown("**✍️ 2. Train Custom Verified Knowledge (Admin Direct Input):**")
            t_topic = st.text_input("Topic Name:", key=f"tr_top_{widget_key}")
            t_kws = st.text_input("Trigger Keywords (comma-separated):", key=f"tr_kw_{widget_key}")
            t_content = st.text_area("Verified Explanation:", height=80, key=f"tr_cnt_{widget_key}")
            if st.button("🧠 Save to Verified AI Memory", key=f"btn_tr_{widget_key}", use_container_width=True):
                if t_topic.strip() and t_content.strip():
                    kw_list = [k.strip().lower() for k in t_kws.split(",") if k.strip()] or [w.lower() for w in t_topic.split() if len(w) > 2]
                    mem_db["learned_facts"].insert(0, {
                        "topic": t_topic.strip(),
                        "keywords": kw_list,
                        "content": t_content.strip(),
                        "taught_by": "Admin_PhuHieu",
                        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                    })
                    save_ai_memory(mem_db)
                    st.success(f"✅ Trained topic `{t_topic.strip()}`!")

            st.divider()
            # 3. Duyệt đề xuất của người dùng (Moderation Queue)
            pending = mem_db.get("pending_suggestions", [])
            st.markdown(f"**📋 3. Pending User Suggestions Queue ({len(pending)} items):**")
            if not pending:
                st.caption("No pending suggestions from users.")
            else:
                for p_idx, p_item in enumerate(pending):
                    with st.container(border=True):
                        st.markdown(f"**{p_item['topic']}** *(by `{p_item['user']}`)*")
                        st.caption(p_item["note"])
                        ac1, ac2 = st.columns(2)
                        if ac1.button("✅ Approve & Train", key=f"ap_{widget_key}_{p_idx}", use_container_width=True):
                            kws = [w.lower() for w in p_item["topic"].split() if len(w) >= 2]
                            mem_db["learned_facts"].insert(0, {
                                "topic": p_item["topic"],
                                "keywords": kws,
                                "content": p_item["note"],
                                "taught_by": f"Approved({p_item['user']})",
                                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                            })
                            mem_db["pending_suggestions"].pop(p_idx)
                            save_ai_memory(mem_db)
                            st.rerun()
                        if ac2.button("🗑️ Reject", key=f"rj_{widget_key}_{p_idx}", use_container_width=True):
                            mem_db["pending_suggestions"].pop(p_idx)
                            save_ai_memory(mem_db)
                            st.rerun()

            st.divider()
            # 4. Tùy chọn gắn Gemini API Key để mở khóa 100+ ngôn ngữ LLM
            st.markdown("**🌐 4. Optional Cloud LLM Key (Google Gemini API for 100+ Languages):**")
            gem_key = st.text_input("Gemini API Key (Optional):", value=mem_db.get("gemini_api_key", ""), type="password", key=f"gem_k_{widget_key}")
            if st.button("💾 Save API Key", key=f"btn_gem_{widget_key}", use_container_width=True):
                mem_db["gemini_api_key"] = gem_key.strip()
                save_ai_memory(mem_db)
                st.success("✅ Saved Gemini API Key!")

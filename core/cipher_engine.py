import random
import string
import time
import unicodedata
import streamlit as st

# 1. Bộ ký tự cơ sở (Hỗ trợ Tiếng Anh, Tiếng Việt, Số & Ký tự đặc biệt)
VIETNAMESE_CHARS = (
    "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"
)
BASE_CHARS = list(" " + string.punctuation + string.digits + string.ascii_letters + VIETNAMESE_CHARS)


# 2. Bộ nạp hơn 1.200 Biểu tượng Unicode tự động
@st.cache_data
def load_massive_symbol_pool() -> list:
    """Quét các dải Unicode để lấy danh sách hơn 1.200 biểu tượng khác nhau."""
    pool = []
    ranges = [
        (0x1F300, 0x1F5FF),  # Biểu tượng tự nhiên, vật phẩm, thời tiết
        (0x1F600, 0x1F64F),  # Biểu cảm khuôn mặt
        (0x1F680, 0x1F6FF),  # Phương tiện, bản đồ, ký hiệu
        (0x1F900, 0x1F9FF),  # Động vật, thực phẩm, biểu tượng bổ sung
        (0x2600, 0x26FF),    # Cờ vua, chiêm tinh, ký hiệu cổ điển
    ]
    for start, end in ranges:
        for code in range(start, end + 1):
            ch = chr(code)
            if unicodedata.category(ch) in ('So', 'Sm'):
                pool.append(ch)
    return pool


# 3. Hàm xây dựng Bảng khóa riêng biệt cho từng nhóm
def build_custom_key(secret_seed: str, pattern_list: list, shift_step: int, custom_pairs: str) -> list:
    """Tạo bảng mã hóa 1-1 dựa trên Mật khẩu, Chuỗi Icon, Bước nhảy và Cặp gán riêng."""
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


# 4. Hàm tính độ mạnh của Khóa (Phục vụ cho trang Security Academy & Dashboard)
def calculate_key_entropy(secret_seed: str, pattern_list: list, shift_step: int, custom_pairs: str) -> dict:
    """Ước tính số lượng tổ hợp và thời gian cần thiết để vét cạn (Brute-force)."""
    pool_size = len(load_massive_symbol_pool())
    num_icons = len(pattern_list)
    
    # Số tổ hợp từ mật khẩu chữ + số tổ hợp chọn icon + bước nhảy
    char_combinations = max(len(BASE_CHARS) ** len(secret_seed), 1)
    icon_combinations = max(pool_size ** num_icons, 1)
    shift_combinations = 200 if shift_step > 0 else 1
    
    total_combinations = char_combinations * icon_combinations * shift_combinations
    # Giả sử siêu máy tính thử được 10 tỷ (10^10) phép thử mỗi giây
    seconds_to_crack = total_combinations / (10 ** 10)
    years_to_crack = seconds_to_crack / (60 * 60 * 24 * 365)
    
    return {
        "icon_pool": pool_size,
        "selected_icons": num_icons,
        "years_to_crack": years_to_crack
    }


# 5. Mã hóa & Giải mã lõi (Tích hợp chuẩn giờ Quốc tế UTC & Tự hủy)
def encrypt_core(plain_text: str, key: list, reverse_rule: bool, mode: str = "NONE", target_ts: int = 0) -> str:
    payload = f"TMODE:{mode}:{target_ts}|{plain_text}"
    res = "".join(key[BASE_CHARS.index(c)] if c in BASE_CHARS else c for c in payload)
    if reverse_rule:
        res = res[::-1]
    return res


def decrypt_core(cypher_text: str, key: list, reverse_rule: bool) -> tuple[bool, str]:
    if reverse_rule:
        cypher_text = cypher_text[::-1]
    raw = "".join(BASE_CHARS[key.index(c)] if c in key else c for c in cypher_text)
    
    if not raw.startswith("TMODE:") or "|" not in raw:
        return False, "❌ Decryption Failed: Incorrect Group Passphrase, Symbol Pattern, or Shift Rules!"
    
    header, actual_msg = raw.split("|", 1)
    parts = header.split(":")
    if len(parts) != 3:
        return False, "❌ Corrupted timestamp header!"
        
    mode = parts[1]
    try:
        target_ts = int(parts[2])
    except ValueError:
        return False, "❌ Invalid time-lock data!"
        
    now_ts = int(time.time())  # Chuẩn giờ Quốc tế UTC Epoch
    
    # Chế độ 1: Tự hủy (Self-Destruct) nếu quá thời gian quy định
    if mode == "EXPIRE" and target_ts > 0:
        if now_ts > target_ts:
            expired_ago = now_ts - target_ts
            mins, secs = divmod(expired_ago, 60)
            dead_rng = random.Random(now_ts)
            scrambled = "".join(dead_rng.sample(actual_msg, len(actual_msg))) if actual_msg else "???"
            return False, (
                f"💥 MESSAGE SELF-DESTRUCTED! (Expired {mins}m {secs}s ago).\n"
                f"The time window has passed and the payload has been permanently scrambled into noise:\n`{scrambled}`"
            )
            
    # Chế độ 2: Hẹn giờ mở trong tương lai (Time-Capsule)
    elif mode == "WAIT" and target_ts > 0:
        if now_ts < target_ts:
            wait_sec = target_ts - now_ts
            mins, secs = divmod(wait_sec, 60)
            hours, mins = divmod(mins, 60)
            return False, f"⏳ TIME-CAPSULE LOCKED! Please wait {hours}h {mins}m {secs}s before decoding."
            
    return True, actual_msg

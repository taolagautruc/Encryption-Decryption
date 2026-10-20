import streamlit as st
import random
import string

# Bộ ký tự gốc (Tiếng Anh, Số, Ký tự đặc biệt, Tiếng Việt)
vietnamese_chars = (
    "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"
)
BASE_CHARS = list(" " + string.punctuation + string.digits + string.ascii_letters + vietnamese_chars)

def build_custom_key(secret_seed: str, shift_step: int, custom_pairs: str):
    """Tạo bảng mã độc nhất dựa trên toàn bộ quy luật do nhóm tự thiết lập"""
    key = BASE_CHARS.copy()
    
    # 1. Xáo trộn theo Từ khóa bí mật của nhóm
    rng = random.Random(secret_seed)
    rng.shuffle(key)
    
    # 2. Dịch chuyển vị trí theo Bước nhảy (Shift) của nhóm
    if shift_step > 0:
        shift = shift_step % len(key)
        key = key[shift:] + key[:shift]
        
    # 3. Áp dụng quy tắc hoán đổi ký tự thủ công (nếu nhóm có cài đặt)
    # Ví dụ: a=@, b=#
    if custom_pairs.strip():
        pairs = [p.strip() for p in custom_pairs.split(",") if "=" in p]
        for pair in pairs:
            parts = pair.split("=", 1)
            if len(parts) == 2:
                char_a, char_b = parts[0], parts[1]
                if char_a in BASE_CHARS and char_b in key:
                    idx_a = BASE_CHARS.index(char_a)
                    idx_b = key.index(char_b)
                    # Hoán đổi vị trí để đảm bảo giải mã 2 chiều không bị trùng
                    key[idx_a], key[idx_b] = key[idx_b], key[idx_a]
    return key

def encrypt_msg(plain_text: str, key: list, reverse_rule: bool) -> str:
    res = "".join(key[BASE_CHARS.index(c)] if c in BASE_CHARS else c for c in plain_text)
    if reverse_rule:
        res = res[::-1]
    return res

def decrypt_msg(cypher_text: str, key: list, reverse_rule: bool) -> str:
    if reverse_rule:
        cypher_text = cypher_text[::-1]
    return "".join(BASE_CHARS[key.index(c)] if c in key else c for c in cypher_text)

# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="Custom Cipher Messenger", page_icon="🛡️", layout="centered")
st.title("🛡️ Secret Group Messenger")
st.caption("Thiết lập quy luật mã hóa độc quyền cho nhóm của bạn")

# Khung thiết lập quy luật riêng của nhóm
with st.expander("⚙️ THIẾT LẬP QUY LUẬT MÃ HÓA CỦA NHÓM (Bắt buộc)", expanded=True):
    st.markdown("*Chỉ những ai thiết lập **đúng toàn bộ thông số dưới đây** mới có thể giải mã được tin nhắn của nhau.*")
    
    col1, col2 = st.columns(2)
    with col1:
        secret_seed = st.text_input("1️⃣ Mật khẩu gốc của nhóm:", type="password", placeholder="VD: HcmusIT2026")
    with col2:
        shift_step = st.number_input("2️⃣ Số bước dịch chuyển (0 - 200):", min_value=0, max_value=200, value=0, step=1)
        
    custom_pairs = st.text_input(
        "3️⃣ Tự gán ký tự riêng (Tùy chọn - cách nhau bằng dấu phẩy):",
        placeholder="Ví dụ: a=@, e=3, o=0, s=$"
    )
    reverse_rule = st.checkbox("4️⃣ Đảo ngược toàn bộ cấu trúc câu sau khi mã hóa")

if not secret_seed:
    st.warning("👆 Hãy nhập ít nhất 'Mật khẩu gốc của nhóm' ở mục Thiết lập bên trên để kích hoạt bộ mã hóa!")
else:
    # Tạo bảng key dựa trên công thức riêng của nhóm
    group_key = build_custom_key(secret_seed, shift_step, custom_pairs)
    
    # Cho phép nhóm xem thử bảng quy luật của mình (nếu muốn kiểm chứng)
    with st.expander("🔍 Xem thử quy luật biến đổi của nhóm bạn"):
        sample_chars = ['a', 'b', 'c', '1', '2', '3', 'A', 'B', 'C']
        preview = " | ".join([f"'{c}' ➡️ '{group_key[BASE_CHARS.index(c)]}'" for c in sample_chars])
        st.code(f"Mẫu biến đổi hiện tại:\n{preview}\n(Và {len(BASE_CHARS)-9} ký tự khác đã được khóa theo quy luật riêng)")

    tab1, tab2 = st.tabs(["📤 Mã hóa tin nhắn (Encrypt)", "📥 Giải mã tin nhắn (Decrypt)"])

    with tab1:
        plain_input = st.text_area("Nhập tin nhắn cần bảo mật:", height=120)
        if st.button("🔒 Mã hóa theo quy luật nhóm", type="primary"):
            if plain_input:
                encrypted = encrypt_msg(plain_input, group_key, reverse_rule)
                st.success("Tin nhắn đã mã hóa! Hãy copy đoạn dưới đây gửi cho bạn bè:")
                st.code(encrypted, language=None)
            else:
                st.error("Vui lòng nhập nội dung tin nhắn!")

    with tab2:
        cypher_input = st.text_area("Dán đoạn mật mã nhận được vào đây:", height=120)
        if st.button("🔓 Giải mã tin nhắn", type="primary"):
            if cypher_input:
                decrypted = decrypt_msg(cypher_input, group_key, reverse_rule)
                st.info("Nội dung gốc:")
                st.success(decrypted)
            else:
                st.error("Vui lòng dán mật mã cần giải mã!")
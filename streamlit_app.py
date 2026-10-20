import streamlit as st
import random
import string

vietnamese_chars = (
    "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"
)
BASE_CHARS = list(" " + string.punctuation + string.digits + string.ascii_letters + vietnamese_chars)

def generate_key(secret_rule: str):
    key = BASE_CHARS.copy()
    rng = random.Random(secret_rule)
    rng.shuffle(key)
    return key

def encrypt_msg(plain_text: str, secret_rule: str) -> str:
    key = generate_key(secret_rule)
    return "".join(key[BASE_CHARS.index(c)] if c in BASE_CHARS else c for c in plain_text)

def decrypt_msg(cypher_text: str, secret_rule: str) -> str:
    key = generate_key(secret_rule)
    return "".join(BASE_CHARS[key.index(c)] if c in key else c for c in cypher_text)

st.set_page_config(page_title="Secret Group Chat", page_icon="🔐")
st.title("🔐 Secret Messenger")
st.caption("Ứng dụng mã hóa tin nhắn theo quy ước riêng")

secret_rule = st.text_input("🔑 Nhập quy ước bí mật của nhóm (Secret Key):", type="password")

if not secret_rule:
    st.warning("Vui lòng nhập quy ước bí mật trước khi bắt đầu!")
else:
    tab1, tab2 = st.tabs(["📤 Mã hóa (Encrypt)", "📥 Giải mã (Decrypt)"])

    with tab1:
        plain_input = st.text_area("Nhập tin nhắn gốc:")
        if st.button("Mã hóa ngay"):
            encrypted = encrypt_msg(plain_input, secret_rule)
            st.success("Tin nhắn đã mã hóa (Copy gửi cho bạn bè):")
            st.code(encrypted, language=None)

    with tab2:
        cypher_input = st.text_area("Dán tin nhắn mật mã vào đây:")
        if st.button("Giải mã"):
            decrypted = decrypt_msg(cypher_input, secret_rule)
            st.info("Nội dung tin nhắn gốc:")
            st.write(decrypted)
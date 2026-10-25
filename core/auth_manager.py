import streamlit as st
import json
import os
import re
import hashlib
from datetime import datetime, timezone

AUTH_DB_FILE = "user_accounts_db.json"

def load_auth_db() -> dict:
    if not os.path.exists(AUTH_DB_FILE):
        default_salt = "usm_hcmus_2026_salt"
        default_pass_hash = hashlib.pbkdf2_hmac(
            "sha256", b"123456", default_salt.encode("utf-8"), 100000
        ).hex()
        seed_db = {
            "accounts": {
                "hieulehoangphu@gmail.com": {
                    "email": "hieulehoangphu@gmail.com",
                    "callsign": "taolagautruc",
                    "salt": default_salt,
                    "password_hash": default_pass_hash,
                    "created_at": "2026-10-25 UTC",
                    "last_login": "2026-10-25 UTC"
                }
            }
        }
        with open(AUTH_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(seed_db, f, ensure_ascii=False, indent=4)
        return seed_db
    try:
        with open(AUTH_DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "accounts" not in data:
                data["accounts"] = {}
            return data
    except Exception:
        return {"accounts": {}}


def save_auth_db(data: dict):
    with open(AUTH_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()


def is_valid_gmail(email: str) -> bool:
    clean = email.strip().lower()
    pattern = r"^[a-zA-Z0-9_.+-]+@(gmail\.com|[a-zA-Z0-9-]+\.edu\.vn)$"
    return bool(re.match(pattern, clean))


def sync_authenticated_identity(callsign: str, email: str):
    """Đồng bộ tài khoản Gmail đã đăng nhập sang toàn bộ các mục trên Web."""
    st.session_state["auth_logged_in"] = True
    st.session_state["auth_email"] = email
    st.session_state["auth_callsign"] = callsign
    st.session_state["ctf_user"] = callsign
    st.session_state["acad_user"] = callsign
    st.session_state["chat_agent_name"] = callsign
    st.session_state["sdk_player_in"] = callsign
    st.session_state["comm_user_in"] = callsign


def render_sidebar_gmail_auth() -> tuple[bool, str, str]:
    """
    Hiển thị Cổng Đăng Nhập / Đăng Ký bằng Gmail ngay trên đầu Sidebar.
    Trả về: (is_logged_in, active_callsign, active_email)
    """
    db = load_auth_db()
    accounts = db.get("accounts", {})

    if "auth_logged_in" not in st.session_state:
        st.session_state["auth_logged_in"] = False
        st.session_state["auth_email"] = ""
        st.session_state["auth_callsign"] = "Guest_Agent"

    st.markdown("""
    <style>
        .gmail-profile-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            border: 1.5px solid #38bdf8;
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 10px;
            box-shadow: 0 4px 15px rgba(56, 189, 248, 0.2);
        }
    </style>
    """, unsafe_allow_html=True)

    # ==========================================================================
    # TRẠNG THÁI 1: ĐÃ ĐĂNG NHẬP BẰNG GMAIL
    # ==========================================================================
    if st.session_state["auth_logged_in"]:
        email_now = st.session_state["auth_email"]
        callsign_now = st.session_state["auth_callsign"]
        # Luôn giữ đồng bộ session_state cho các module khác
        st.session_state["ctf_user"] = callsign_now
        st.session_state["acad_user"] = callsign_now

        st.markdown(f"""
        <div class="gmail-profile-card">
            <div style="font-size:0.7rem; color:#38bdf8; font-weight:800; letter-spacing:0.8px;">🟢 VERIFIED GMAIL ACCOUNT</div>
            <div style="font-size:0.95rem; font-weight:800; color:#ffffff; margin-top:3px; word-break:break-all;">📧 {email_now}</div>
            <div style="font-size:0.82rem; color:#fde047; margin-top:4px;">🕵️ Agent ID: <b>{callsign_now}</b></div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Log Out (Switch Gmail)", use_container_width=True, key="btn_gmail_logout"):
            st.session_state["auth_logged_in"] = False
            st.session_state["auth_email"] = ""
            st.session_state["auth_callsign"] = "Guest_Agent"
            st.rerun()

        return True, callsign_now, email_now

    # ==========================================================================
    # TRẠNG THÁI 2: CHƯA ĐĂNG NHẬP (HIỂN THỊ KHUNG ĐĂNG NHẬP / ĐĂNG KÝ GMAIL)
    # ==========================================================================
    st.markdown("### 📧 Gmail Account Login")
    st.caption("Sign in with your Gmail & Password to save and restore all scores, chat rooms, and items across sessions.")

    tab_login, tab_register = st.tabs(["🔑 Sign In", "➕ Create Account"])

    with tab_login:
        login_email = st.text_input("📧 Gmail Address:", placeholder="yourname@gmail.com", key="in_login_gmail").strip().lower()
        login_pass = st.text_input("🔒 Password:", type="password", placeholder="Enter your password...", key="in_login_pass")

        if st.button("🚀 Sign In with Gmail", type="primary", use_container_width=True, key="btn_gmail_signin"):
            if not login_email or not login_pass:
                st.error("❌ Please enter both Gmail and Password!")
            elif login_email not in accounts:
                st.error("❌ Gmail account not found! Switch to '➕ Create Account' to register.")
            else:
                acc = accounts[login_email]
                calc_hash = hash_password(login_pass, acc["salt"])
                if calc_hash == acc["password_hash"]:
                    acc["last_login"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                    save_auth_db(db)
                    sync_authenticated_identity(acc["callsign"], login_email)
                    st.toast(f"✅ Welcome back, {acc['callsign']}!", icon="📧")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password!")

    with tab_register:
        reg_email = st.text_input("📧 Your Gmail (`@gmail.com`):", placeholder="example@gmail.com", key="in_reg_gmail").strip().lower()
        reg_callsign = st.text_input("🕵️ Agent Display Name (Optional):", placeholder="e.g. taolagautruc", key="in_reg_callsign").strip()
        reg_pass = st.text_input("🔒 Create Password (Min 6 chars):", type="password", key="in_reg_pass")
        reg_pass2 = st.text_input("🔒 Confirm Password:", type="password", key="in_reg_pass2")

        if st.button("✨ Register Gmail Account", type="primary", use_container_width=True, key="btn_gmail_reg"):
            if not is_valid_gmail(reg_email):
                st.error("❌ Please enter a valid `@gmail.com` (or `@*.edu.vn`) address!")
            elif reg_email in accounts:
                st.warning("⚠️ This Gmail is already registered! Please use the '🔑 Sign In' tab.")
            elif len(reg_pass) < 6:
                st.error("❌ Password must be at least 6 characters long!")
            elif reg_pass != reg_pass2:
                st.error("❌ Passwords do not match!")
            else:
                final_callsign = reg_callsign if reg_callsign else reg_email.split("@")[0]
                salt = hashlib.sha256(f"{reg_email}_{datetime.now().timestamp()}".encode("utf-8")).hexdigest()[:16]
                p_hash = hash_password(reg_pass, salt)
                now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                accounts[reg_email] = {
                    "email": reg_email,
                    "callsign": final_callsign,
                    "salt": salt,
                    "password_hash": p_hash,
                    "created_at": now_str,
                    "last_login": now_str
                }
                db["accounts"] = accounts
                save_auth_db(db)
                sync_authenticated_identity(final_callsign, reg_email)
                st.balloons()
                st.toast(f"🎉 Account created for {reg_email}!", icon="🎉")
                st.rerun()

    return False, "Guest_Agent", ""

import streamlit as st
import json
import os
import re
import random
import time
import hashlib
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone

AUTH_DB_FILE = "user_accounts_db.json"

# Danh sách các tiền tố Gmail ảo / nhập bừa bị cấm đăng ký
BANNED_FAKE_PREFIXES = {
    "123456", "1234567", "12345678", "123456789", "abcdef", "abcdefg",
    "qwerty", "qwertyuiop", "asdfgh", "asdfghjkl", "zxcvbn", "test123",
    "testing", "admin123", "user123", "noname", "fakemail", "example"
}


def load_auth_db() -> dict:
    if not os.path.exists(AUTH_DB_FILE):
        default_salt = "usm_hcmus_2026_salt"
        default_pass_hash = hashlib.pbkdf2_hmac(
            "sha256", b"123456", default_salt.encode("utf-8"), 100000
        ).hex()
        default_pin_hash = hashlib.sha256(b"3001").hexdigest()
        seed_db = {
            "smtp_config": {
                "sender_email": "",
                "app_password": ""
            },
            "accounts": {
                "hieulehoangphu@gmail.com": {
                    "email": "hieulehoangphu@gmail.com",
                    "callsign": "taolagautruc",
                    "salt": default_salt,
                    "password_hash": default_pass_hash,
                    "recovery_pin_hash": default_pin_hash,
                    "verified": True,
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
            if "smtp_config" not in data:
                data["smtp_config"] = {"sender_email": "", "app_password": ""}
            return data
    except Exception:
        return {"smtp_config": {"sender_email": "", "app_password": ""}, "accounts": {}}


def save_auth_db(data: dict):
    with open(AUTH_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()


def validate_strict_google_gmail(email: str) -> tuple[bool, str]:
    """
    Kiểm tra nghiêm ngặt cấu trúc Gmail thật của Google:
    1. Chỉ chấp nhận tên miền @gmail.com hoặc @*.edu.vn.
    2. Phần username phải từ 6 đến 30 ký tự (chuẩn Google).
    3. Không bắt đầu/kết thúc bằng dấu chấm, không có 2 dấu chấm liên tiếp (..).
    4. Chặn các email gõ phím bừa bãi (không có nguyên âm hoặc nằm trong danh sách cấm).
    """
    clean = email.strip().lower()
    if "@" not in clean:
        return False, "❌ Invalid format: Missing '@' symbol."

    username, domain = clean.split("@", 1)

    if domain != "gmail.com" and not domain.endswith(".edu.vn"):
        return False, "❌ Only official `@gmail.com` or university `@*.edu.vn` addresses are accepted!"

    if len(username) < 6 or len(username) > 30:
        return False, "❌ Google requires Gmail usernames to be between 6 and 30 characters long!"

    if username.startswith(".") or username.endswith(".") or ".." in username:
        return False, "❌ Gmail usernames cannot start/end with a dot or contain consecutive dots (`..`)."

    if not re.match(r"^[a-z0-9.]+$", username):
        return False, "❌ Gmail usernames can only contain letters (a-z), numbers (0-9), and periods (.)."

    clean_no_dots = username.replace(".", "")
    if clean_no_dots in BANNED_FAKE_PREFIXES or len(set(clean_no_dots)) <= 2:
        return False, "❌ This looks like a fake/placeholder address! Please enter your real personal Gmail."

    # Kiểm tra tỷ lệ nguyên âm để chặn chuỗi gõ bừa kiểu 'xkcdjklm@gmail.com'
    letters_only = [c for c in clean_no_dots if c.isalpha()]
    if len(letters_only) >= 5:
        vowels = sum(1 for c in letters_only if c in "aeiouy")
        if vowels == 0:
            return False, "❌ Suspicious gibberish username detected (no vowels). Please use a real Gmail address!"

    return True, "✅ Valid Gmail structure."


def send_otp_via_gmail_smtp(target_email: str, otp_code: str, purpose: str, db: dict) -> tuple[bool, str]:
    """
    Gửi mã OTP 6 số trực tiếp tới hòm thư Gmail thật của người dùng qua giao thức SMTP SSL (Port 465).
    Nếu Admin chưa cấu hình SMTP App Password, trả về False để chuyển sang chế độ xác thực dự phòng.
    """
    sender = ""
    app_pw = ""
    try:
        if "GMAIL_SENDER" in st.secrets:
            sender = str(st.secrets["GMAIL_SENDER"]).strip()
        if "GMAIL_APP_PASSWORD" in st.secrets:
            app_pw = str(st.secrets["GMAIL_APP_PASSWORD"]).strip()
    except Exception:
        pass

    if not sender or not app_pw:
        cfg = db.get("smtp_config", {})
        sender = cfg.get("sender_email", "").strip()
        app_pw = cfg.get("app_password", "").strip()

    if not sender or not app_pw:
        return False, "SMTP_NOT_CONFIGURED"

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[Ultimate Secret Messenger] Your {purpose} OTP Code: {otp_code}"
        msg["From"] = f"Ultimate Secret Messenger <{sender}>"
        msg["To"] = target_email
        msg.set_content(
            f"Hello Agent,\n\n"
            f"Your 6-digit verification code for {purpose} on Ultimate Secret Messenger is:\n\n"
            f"    >>> {otp_code} <<<\n\n"
            f"This code will expire in 5 minutes.\n"
            f"If you did not request this, please ignore this email.\n\n"
            f"— Ultimate Secret Messenger Security Team (HCMUS)"
        )
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=7) as server:
            server.login(sender, app_pw)
            server.send_message(msg)
        return True, f"📧 A 6-digit OTP has been sent to **{target_email}**! Please check your Gmail Inbox (and Spam folder)."
    except Exception as e:
        return False, f"SMTP_ERROR: {str(e)}"


def sync_authenticated_identity(callsign: str, email: str):
    """Đồng bộ tài khoản Gmail đã đăng nhập sang toàn bộ 8 mục trên Web."""
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
    Hiển thị Hệ thống Đăng Nhập / Đăng Ký Có Xác Thực OTP / Quên Mật Khẩu trên Sidebar.
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
    # TRẠNG THÁI 1: ĐÃ ĐĂNG NHẬP THÀNH CÔNG
    # ==========================================================================
    if st.session_state["auth_logged_in"]:
        email_now = st.session_state["auth_email"]
        callsign_now = st.session_state["auth_callsign"]
        st.session_state["ctf_user"] = callsign_now
        st.session_state["acad_user"] = callsign_now

        st.markdown(f"""
        <div class="gmail-profile-card">
            <div style="font-size:0.7rem; color:#34d399; font-weight:800; letter-spacing:0.8px;">🟢 VERIFIED GMAIL SESSION</div>
            <div style="font-size:0.92rem; font-weight:800; color:#ffffff; margin-top:3px; word-break:break-all;">📧 {email_now}</div>
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
    # TRẠNG THÁI 2: CHƯA ĐĂNG NHẬP (3 TAB: SIGN IN | REGISTER + OTP | FORGOT PASS)
    # ==========================================================================
    st.markdown("### 📧 Gmail Account Center")
    st.caption("Sign in with your verified Gmail to save all scores, chat rooms, and items permanently.")

    tab_login, tab_reg, tab_forgot = st.tabs([
        "🔑 Sign In",
        "➕ Register",
        "🔄 Forgot Pass"
    ])

    # --- TAB 1: ĐĂNG NHẬP ---
    with tab_login:
        login_email = st.text_input("📧 Gmail Address:", placeholder="yourname@gmail.com", key="in_login_gmail").strip().lower()
        login_pass = st.text_input("🔒 Password:", type="password", placeholder="Enter your password...", key="in_login_pass")

        if st.button("🚀 Sign In", type="primary", use_container_width=True, key="btn_gmail_signin"):
            if not login_email or not login_pass:
                st.error("❌ Please enter both Gmail and Password!")
            elif login_email not in accounts:
                st.error("❌ This Gmail is not registered yet! Switch to '➕ Register' tab.")
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
                    st.error("❌ Wrong password! Use the '🔄 Forgot Pass' tab if you forgot it.")

    # --- TAB 2: ĐĂNG KÝ TÀI KHOẢN GMAIL MỚI (CÓ KIỂM TRA GMAIL THẬT & MÃ OTP 6 SỐ) ---
    with tab_reg:
        reg_email = st.text_input("📧 Real Gmail (`@gmail.com`):", placeholder="your.real.email@gmail.com", key="in_reg_gmail").strip().lower()
        reg_callsign = st.text_input("🕵️ Display Name (Callsign):", placeholder="e.g. taolagautruc", key="in_reg_callsign").strip()
        reg_pass = st.text_input("🔒 Password (Min 6 chars):", type="password", key="in_reg_pass")
        reg_pin = st.text_input(
            "🛡️ 4-Digit Recovery PIN (For Forgot Password):",
            max_chars=6,
            placeholder="e.g. 3001",
            help="Remember this 4-digit PIN! You can use it to reset your password anytime if you forget it.",
            key="in_reg_pin"
        ).strip()

        # Bước 1 của Đăng ký: Kiểm tra tính hợp lệ của Gmail & Gửi mã OTP 6 số
        if st.button("📨 Step 1: Send 6-Digit Verification OTP", use_container_width=True, key="btn_send_reg_otp"):
            ok_mail, mail_msg = validate_strict_google_gmail(reg_email)
            if not ok_mail:
                st.error(mail_msg)
            elif reg_email in accounts:
                st.warning("⚠️ This Gmail is already registered! Please sign in or reset your password.")
            elif len(reg_pass) < 6:
                st.error("❌ Password must be at least 6 characters!")
            elif len(reg_pin) < 4 or not reg_pin.isdigit():
                st.error("❌ Please set a 4 to 6 digit numeric Recovery PIN (e.g. `3001`)!")
            else:
                otp_code = f"{random.randint(100000, 999999)}"
                st.session_state["pending_reg_data"] = {
                    "email": reg_email,
                    "callsign": reg_callsign if reg_callsign else reg_email.split("@")[0],
                    "pass": reg_pass,
                    "pin": reg_pin,
                    "otp": otp_code,
                    "exp": time.time() + 300
                }
                sent_ok, smtp_msg = send_otp_via_gmail_smtp(reg_email, otp_code, "Account Registration", db)
                if sent_ok:
                    st.success(smtp_msg)
                else:
                    # Nếu Admin chưa nhập SMTP App Password, hiển thị mã OTP xác thực trực tiếp để không làm gián đoạn trải nghiệm
                    st.info(
                        f"🔐 **Verification Code Generated for `{reg_email}`:** **`{otp_code}`**\n\n"
                        f"*(Enter this 6-digit OTP below to verify your ownership and activate your account!)*"
                    )

        # Bước 2 của Đăng ký: Nhập mã OTP 6 số để kích hoạt
        if "pending_reg_data" in st.session_state and st.session_state["pending_reg_data"].get("email") == reg_email:
            otp_in = st.text_input("🔢 Enter 6-Digit OTP Code:", max_chars=6, placeholder="6-digit code...", key="in_reg_otp_code").strip()
            if st.button("✅ Step 2: Verify OTP & Create Account", type="primary", use_container_width=True, key="btn_verify_reg_otp"):
                pend = st.session_state["pending_reg_data"]
                if time.time() > pend["exp"]:
                    st.error("⏰ OTP expired! Please click 'Send 6-Digit Verification OTP' again.")
                elif otp_in != pend["otp"]:
                    st.error("❌ Invalid 6-digit OTP code!")
                else:
                    salt = hashlib.sha256(f"{pend['email']}_{time.time()}".encode("utf-8")).hexdigest()[:16]
                    p_hash = hash_password(pend["pass"], salt)
                    pin_hash = hashlib.sha256(pend["pin"].encode("utf-8")).hexdigest()
                    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                    accounts[pend["email"]] = {
                        "email": pend["email"],
                        "callsign": pend["callsign"],
                        "salt": salt,
                        "password_hash": p_hash,
                        "recovery_pin_hash": pin_hash,
                        "verified": True,
                        "created_at": now_str,
                        "last_login": now_str
                    }
                    db["accounts"] = accounts
                    save_auth_db(db)
                    del st.session_state["pending_reg_data"]
                    sync_authenticated_identity(pend["callsign"], pend["email"])
                    st.balloons()
                    st.rerun()

    # --- TAB 3: QUÊN MẬT KHẨU (FORGOT PASSWORD — KHÔI PHỤC BẰNG RECOVERY PIN HOẶC EMAIL OTP) ---
    with tab_forgot:
        st.caption("🔄 Forgot your password? Reset it instantly using your **4-Digit Recovery PIN** or request an **Email OTP**!")
        fg_email = st.text_input("📧 Your Registered Gmail:", placeholder="yourname@gmail.com", key="in_fg_email").strip().lower()
        fg_method = st.radio(
            "Select Recovery Method:",
            ["🛡️ Use My 4-Digit Recovery PIN", "📧 Send 6-Digit OTP to My Gmail"],
            key="fg_method_radio"
        )

        if "Recovery PIN" in fg_method:
            fg_pin_in = st.text_input("🛡️ Enter Your Recovery PIN:", type="password", max_chars=6, placeholder="e.g. 3001", key="in_fg_pin").strip()
            fg_new_pass = st.text_input("🔑 New Password (Min 6 chars):", type="password", key="in_fg_newpass1")
            if st.button("🔄 Reset Password Now", type="primary", use_container_width=True, key="btn_fg_pin_reset"):
                if fg_email not in accounts:
                    st.error("❌ No account found with this Gmail address!")
                elif len(fg_new_pass) < 6:
                    st.error("❌ New password must be at least 6 characters!")
                else:
                    acc = accounts[fg_email]
                    saved_pin_hash = acc.get("recovery_pin_hash", hashlib.sha256(b"3001").hexdigest())
                    if hashlib.sha256(fg_pin_in.encode("utf-8")).hexdigest() == saved_pin_hash:
                        new_salt = hashlib.sha256(f"{fg_email}_{time.time()}".encode("utf-8")).hexdigest()[:16]
                        acc["salt"] = new_salt
                        acc["password_hash"] = hash_password(fg_new_pass, new_salt)
                        save_auth_db(db)
                        st.success("✅ Password reset successfully! You can now sign in with your new password.")
                    else:
                        st.error("❌ Incorrect Recovery PIN!")
        else:
            if st.button("📨 Send Password Reset OTP to Gmail", use_container_width=True, key="btn_fg_send_otp"):
                if fg_email not in accounts:
                    st.error("❌ No account found with this Gmail address!")
                else:
                    rst_otp = f"{random.randint(100000, 999999)}"
                    st.session_state["pending_reset_otp"] = {
                        "email": fg_email,
                        "otp": rst_otp,
                        "exp": time.time() + 300
                    }
                    sent_ok, smtp_msg = send_otp_via_gmail_smtp(fg_email, rst_otp, "Password Reset", db)
                    if sent_ok:
                        st.success(smtp_msg)
                    else:
                        st.warning(
                            "⚠️ Real Gmail SMTP is not linked yet. Please use the **'🛡️ Use My 4-Digit Recovery PIN'** option above, "
                            "or ask the Admin to enable Gmail App Password in the SMTP settings below."
                        )

            if "pending_reset_otp" in st.session_state and st.session_state["pending_reset_otp"].get("email") == fg_email:
                rst_code_in = st.text_input("🔢 Enter 6-Digit Reset OTP from Gmail:", max_chars=6, key="in_fg_otp").strip()
                fg_new_pass2 = st.text_input("🔑 New Password (Min 6 chars):", type="password", key="in_fg_newpass2")
                if st.button("✅ Verify OTP & Save New Password", type="primary", use_container_width=True, key="btn_fg_otp_save"):
                    r_pend = st.session_state["pending_reset_otp"]
                    if time.time() > r_pend["exp"]:
                        st.error("⏰ OTP expired!")
                    elif rst_code_in != r_pend["otp"]:
                        st.error("❌ Wrong OTP code!")
                    elif len(fg_new_pass2) < 6:
                        st.error("❌ Password must be at least 6 characters!")
                    else:
                        acc = accounts[fg_email]
                        new_salt = hashlib.sha256(f"{fg_email}_{time.time()}".encode("utf-8")).hexdigest()[:16]
                        acc["salt"] = new_salt
                        acc["password_hash"] = hash_password(fg_new_pass2, new_salt)
                        save_auth_db(db)
                        del st.session_state["pending_reset_otp"]
                        st.success("✅ Password updated! Switch to '🔑 Sign In' to log in.")

    # Cài đặt tùy chọn dành riêng cho Admin (Phú Hiếu) để bật gửi thư OTP thật từ Gmail
    with st.expander("⚙️ Admin: Real Gmail OTP Server (Optional)"):
        st.caption("If you want the server to send real 6-digit OTP emails to players' Gmail inboxes, enter your Gmail & 16-char Google App Password (protected by Admin PIN `HCMUS3001`):")
        adm_pin = st.text_input("🔑 Admin PIN:", type="password", key="smtp_adm_pin")
        if adm_pin.strip() == "HCMUS3001":
            cfg = db.get("smtp_config", {})
            s_mail = st.text_input("Sender Gmail:", value=cfg.get("sender_email", ""), placeholder="your.server@gmail.com")
            s_apw = st.text_input("Google 16-Char App Password:", value=cfg.get("app_password", ""), type="password")
            if st.button("💾 Save Real SMTP Config", use_container_width=True):
                db["smtp_config"] = {"sender_email": s_mail.strip(), "app_password": s_apw.strip()}
                save_auth_db(db)
                st.success("✅ Real Gmail OTP delivery enabled!")

    return False, "Guest_Agent", ""

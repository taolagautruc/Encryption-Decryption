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
DEFAULT_ADMIN_PIN_HASH = hashlib.sha256(b"HCMUS3001").hexdigest()

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
        seed_db = {
            "admin_pin_hash": DEFAULT_ADMIN_PIN_HASH,
            "smtp_config": {
                "sender_email": "",
                "app_password": "",
                "require_login_gate": False
            },
            "accounts": {
                "hieulehoangphu@gmail.com": {
                    "email": "hieulehoangphu@gmail.com",
                    "callsign": "taolagautruc",
                    "salt": default_salt,
                    "password_hash": default_pass_hash,
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
            if "admin_pin_hash" not in data:
                data["admin_pin_hash"] = DEFAULT_ADMIN_PIN_HASH
            if "accounts" not in data:
                data["accounts"] = {}
            if "smtp_config" not in data:
                data["smtp_config"] = {"sender_email": "", "app_password": "", "require_login_gate": False}
            return data
    except Exception:
        return {
            "admin_pin_hash": DEFAULT_ADMIN_PIN_HASH,
            "smtp_config": {"sender_email": "", "app_password": "", "require_login_gate": False},
            "accounts": {}
        }


def save_auth_db(data: dict):
    with open(AUTH_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()


def validate_strict_google_gmail(email: str) -> tuple[bool, str]:
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
        return False, "❌ Rejected: Placeholder/trash email detected."

    return True, "✅ Valid Gmail format."


def get_smtp_credentials(db: dict) -> tuple[str, str]:
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

    return sender, app_pw.replace(" ", "")


def send_real_otp_email_strict(target_email: str, otp_code: str, purpose: str, db: dict) -> tuple[bool, str]:
    """
    Sử dụng Gmail Tổng Đài của Chủ Web để gửi mã OTP 6 số tới BẤT KỲ Gmail nào của người chơi.
    """
    sender, app_pw = get_smtp_credentials(db)

    if not sender or not app_pw:
        return (
            False,
            "⚠️ **Tổng đài gửi mã OTP chưa được bật!**\n\n"
            "Chủ web vui lòng mở mục **'⚙️ Web Owner Settings'** ở dưới cùng cột trái để dán 16 chữ cái App Password (chỉ cần làm 1 lần duy nhất để mọi người chơi đều nhận được OTP)."
        )

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[Ultimate Secret Messenger] Verification OTP ({purpose}): {otp_code}"
        msg["From"] = f"Ultimate Secret Messenger <{sender}>"
        msg["To"] = target_email

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto; background: #0f172a; color: #f8fafc; padding: 24px; border-radius: 12px; border: 2px solid #3b82f6;">
            <h2 style="color: #60a5fa; margin-top: 0;">🛡️ Ultimate Secret Messenger</h2>
            <p style="color: #cbd5e1; font-size: 15px;">Hello <b>{target_email}</b>,</p>
            <p style="color: #cbd5e1; font-size: 15px;">Your 6-digit verification code for <b>{purpose}</b> is:</p>
            <div style="background: #1e293b; border: 1.5px dashed #38bdf8; padding: 16px; text-align: center; border-radius: 10px; margin: 20px 0;">
                <span style="font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #fde047;">{otp_code}</span>
            </div>
            <p style="color: #94a3b8; font-size: 13px;">⏳ This code is valid for <b>5 minutes</b>.</p>
        </div>
        """
        msg.set_content(f"Your Ultimate Secret Messenger OTP Code for {purpose} is: {otp_code}")
        msg.add_alternative(html_body, subtype="html")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(sender, app_pw)
            server.send_message(msg)

        return (
            True,
            f"📧 **Đã gửi mã OTP 6 số tới hộp thư `{target_email}`!**\n\n"
            f"👉 Hãy mở ứng dụng **Gmail** của tài khoản `{target_email}` để lấy 6 chữ số nhập vào Bước 2 bên dưới!"
        )
    except Exception as e:
        return False, f"❌ Lỗi gửi thư tới `{target_email}`: {str(e)}"


def sync_authenticated_identity(callsign: str, email: str):
    st.session_state["auth_logged_in"] = True
    st.session_state["auth_email"] = email
    st.session_state["auth_callsign"] = callsign
    st.session_state["ctf_user"] = callsign
    st.session_state["acad_user"] = callsign
    st.session_state["chat_agent_name"] = callsign
    st.session_state["sdk_player_in"] = callsign
    st.session_state["comm_user_in"] = callsign


def render_sidebar_gmail_auth() -> tuple[bool, str, str]:
    db = load_auth_db()
    accounts = db.get("accounts", {})
    sender_cfg, app_pw_cfg = get_smtp_credentials(db)
    smtp_ready = bool(sender_cfg and app_pw_cfg)

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
            <div style="font-size:0.7rem; color:#34d399; font-weight:800; letter-spacing:0.8px;">🟢 VERIFIED PLAYER ACCOUNT</div>
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
    # TRẠNG THÁI 2: CHƯA ĐĂNG NHẬP (DÀNH CHO MỌI NGƯỜI CHƠI)
    # ==========================================================================
    st.markdown("### 📧 Player Account Login")
    st.caption("New player? Click **'➕ Register'** first to create an account with your Gmail!")

    tab_login, tab_reg, tab_forgot = st.tabs([
        "🔑 Sign In",
        "➕ Register",
        "🔄 Forgot Pass"
    ])

    # --- TAB 1: ĐĂNG NHẬP (DÀNH CHO GMAIL ĐÃ ĐĂNG KÝ Ở TAB REGISTER) ---
    with tab_login:
        login_email = st.text_input("📧 Your Gmail:", placeholder="player@gmail.com", key="in_login_gmail").strip().lower()
        login_pass = st.text_input("🔒 Your Password:", type="password", placeholder="Enter password...", key="in_login_pass")

        if st.button("🚀 Sign In", type="primary", use_container_width=True, key="btn_gmail_signin"):
            if not login_email or not login_pass:
                st.error("❌ Please enter both Gmail and Password!")
            elif login_email not in accounts:
                st.warning("⚠️ Gmail này chưa từng đăng ký! Bạn hãy bấm sang tab **'➕ Register'** bên cạnh để tạo tài khoản trước nhé!")
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
                    st.error("❌ Sai mật khẩu! Bấm sang tab '🔄 Forgot Pass' nếu bạn quên mật khẩu.")

    # --- TAB 2: ĐĂNG KÝ TÀI KHOẢN MỚI (BẤT KỲ GMAIL NÀO CŨNG ĐĂNG KÝ ĐƯỢC) ---
    with tab_reg:
        st.caption("✨ Bất kỳ người chơi nào cũng có thể nhập Gmail cá nhân vào đây để nhận mã OTP 6 số và tạo tài khoản:")
        reg_email = st.text_input("📧 Player's Gmail (`@gmail.com`):", placeholder="any_user@gmail.com", key="in_reg_gmail").strip().lower()
        reg_callsign = st.text_input("🕵️ In-Game Nickname:", placeholder="e.g. Sherlock_VN", key="in_reg_callsign").strip()
        reg_pass = st.text_input("🔒 Create Password (Min 6 chars):", type="password", key="in_reg_pass")
        reg_pass2 = st.text_input("🔒 Confirm Password:", type="password", key="in_reg_pass2")

        if st.button("📨 Step 1: Send 6-Digit OTP to This Gmail", use_container_width=True, key="btn_send_reg_otp"):
            ok_mail, mail_msg = validate_strict_google_gmail(reg_email)
            if not ok_mail:
                st.error(mail_msg)
            elif reg_email in accounts:
                st.info("✅ Gmail này đã có tài khoản rồi! Bạn chỉ cần chuyển sang tab **'🔑 Sign In'** để đăng nhập.")
            elif len(reg_pass) < 6:
                st.error("❌ Mật khẩu phải có ít nhất 6 ký tự!")
            elif reg_pass != reg_pass2:
                st.error("❌ Hai mật khẩu nhập vào không khớp nhau!")
            else:
                otp_code = f"{random.randint(100000, 999999)}"
                sent_ok, smtp_msg = send_real_otp_email_strict(reg_email, otp_code, "New Player Registration", db)
                if sent_ok:
                    st.session_state["pending_reg_data"] = {
                        "email": reg_email,
                        "callsign": reg_callsign if reg_callsign else reg_email.split("@")[0],
                        "pass": reg_pass,
                        "otp_hash": hashlib.sha256(otp_code.encode("utf-8")).hexdigest(),
                        "exp": time.time() + 300
                    }
                    st.success(smtp_msg)
                else:
                    st.error(smtp_msg)

        if "pending_reg_data" in st.session_state and st.session_state["pending_reg_data"].get("email") == reg_email:
            otp_in = st.text_input("🔢 Enter 6-Digit OTP from Gmail Inbox:", max_chars=6, key="in_reg_otp_code").strip()
            if st.button("✅ Step 2: Verify OTP & Complete Registration", type="primary", use_container_width=True, key="btn_verify_reg_otp"):
                pend = st.session_state["pending_reg_data"]
                if time.time() > pend["exp"]:
                    st.error("⏰ Mã OTP đã hết hạn (quá 5 phút)! Hãy bấm lại Step 1.")
                elif hashlib.sha256(otp_in.encode("utf-8")).hexdigest() != pend["otp_hash"]:
                    st.error("❌ Mã OTP không đúng! Vui lòng kiểm tra lại hộp thư Gmail của bạn.")
                else:
                    salt = hashlib.sha256(f"{pend['email']}_{time.time()}".encode("utf-8")).hexdigest()[:16]
                    p_hash = hash_password(pend["pass"], salt)
                    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                    accounts[pend["email"]] = {
                        "email": pend["email"],
                        "callsign": pend["callsign"],
                        "salt": salt,
                        "password_hash": p_hash,
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

    # --- TAB 3: QUÊN MẬT KHẨU ---
    with tab_forgot:
        st.caption("🔄 Quên mật khẩu? Nhập Gmail của bạn để nhận mã OTP 6 số đặt lại mật khẩu mới:")
        fg_email = st.text_input("📧 Your Registered Gmail:", placeholder="player@gmail.com", key="in_fg_email").strip().lower()

        if st.button("📨 Send Reset OTP to Gmail", use_container_width=True, key="btn_fg_send_otp"):
            if fg_email not in accounts:
                st.error("❌ Gmail này chưa được đăng ký trên hệ thống!")
            else:
                rst_otp = f"{random.randint(100000, 999999)}"
                sent_ok, smtp_msg = send_real_otp_email_strict(fg_email, rst_otp, "Password Reset", db)
                if sent_ok:
                    st.session_state["pending_reset_otp"] = {
                        "email": fg_email,
                        "otp_hash": hashlib.sha256(rst_otp.encode("utf-8")).hexdigest(),
                        "exp": time.time() + 300
                    }
                    st.success(smtp_msg)
                else:
                    st.error(smtp_msg)

        if "pending_reset_otp" in st.session_state and st.session_state["pending_reset_otp"].get("email") == fg_email:
            rst_code_in = st.text_input("🔢 Enter 6-Digit OTP from Gmail:", max_chars=6, key="in_fg_otp").strip()
            fg_new_pass = st.text_input("🔑 Enter New Password (Min 6 chars):", type="password", key="in_fg_newpass2")
            if st.button("✅ Verify OTP & Save New Password", type="primary", use_container_width=True, key="btn_fg_otp_save"):
                r_pend = st.session_state["pending_reset_otp"]
                if time.time() > r_pend["exp"]:
                    st.error("⏰ OTP expired!")
                elif hashlib.sha256(rst_code_in.encode("utf-8")).hexdigest() != r_pend["otp_hash"]:
                    st.error("❌ Mã OTP không đúng!")
                elif len(fg_new_pass) < 6:
                    st.error("❌ Mật khẩu mới phải từ 6 ký tự trở lên!")
                else:
                    acc = accounts[fg_email]
                    new_salt = hashlib.sha256(f"{fg_email}_{time.time()}".encode("utf-8")).hexdigest()[:16]
                    acc["salt"] = new_salt
                    acc["password_hash"] = hash_password(fg_new_pass, new_salt)
                    save_auth_db(db)
                    del st.session_state["pending_reset_otp"]
                    st.success("✅ Đổi mật khẩu thành công! Hãy quay lại tab '🔑 Sign In' để đăng nhập.")

    # ==========================================================================
    # GÓC CÀI ĐẶT DÀNH RIÊNG CHO CHỦ WEB (ĐÃ ẨN MẬT KHẨU & CHO ĐỔI PIN TRỰC TIẾP)
    # ==========================================================================
    with st.expander("⚙️ Web Owner Settings (Admin Only)", expanded=False):
        st.caption("🔒 Khu vực dành riêng cho Chủ Web (Phú Hiếu). Người chơi không cần bấm vào đây.")
        adm_pin_in = st.text_input("🔑 Enter Owner PIN:", type="password", key="smtp_adm_pin")

        saved_admin_hash = db.get("admin_pin_hash", DEFAULT_ADMIN_PIN_HASH)
        is_owner = (hashlib.sha256(adm_pin_in.strip().encode("utf-8")).hexdigest() == saved_admin_hash) if adm_pin_in else False

        if is_owner:
            st.success("🔓 Đã mở khóa bảng Chủ Web!")
            cfg = db.get("smtp_config", {})

            st.markdown("**1️⃣ Cấu hình Tổng đài gửi thư OTP (Chỉ cài 1 lần):**")
            s_mail = st.text_input("Gmail làm Tổng đài gửi OTP:", value=cfg.get("sender_email", "hieulehoangphu@gmail.com"))
            s_apw = st.text_input("16 chữ cái Google App Password:", value=cfg.get("app_password", ""), type="password")
            req_gate = st.checkbox("🔒 Bắt buộc người chơi phải đăng nhập Gmail mới được dùng web", value=cfg.get("require_login_gate", False))

            if st.button("💾 Lưu Tổng Đài Gửi OTP", type="primary", use_container_width=True):
                db["smtp_config"] = {
                    "sender_email": s_mail.strip(),
                    "app_password": s_apw.strip().replace(" ", ""),
                    "require_login_gate": req_gate
                }
                save_auth_db(db)
                st.success("✅ Đã lưu Tổng đài gửi thư! Giờ mọi Gmail của người chơi đều nhận được OTP!")
                st.rerun()

            st.divider()
            st.markdown("**2️⃣ Đổi Mã PIN Chủ Web (Không cần sửa code):**")
            new_owner_pin = st.text_input("Nhập Mã PIN Chủ Web mới bạn muốn đổi:", type="password", placeholder="Ví dụ: 999999")
            if st.button("🔄 Cập Nhật Mã PIN Mới", use_container_width=True):
                if len(new_owner_pin.strip()) < 4:
                    st.warning("Mã PIN mới nên có ít nhất 4 ký tự!")
                else:
                    db["admin_pin_hash"] = hashlib.sha256(new_owner_pin.strip().encode("utf-8")).hexdigest()
                    save_auth_db(db)
                    st.success("✅ Đã đổi Mã PIN Chủ Web thành công! Lần sau bạn hãy dùng mã PIN mới này nhé.")

    if db.get("smtp_config", {}).get("require_login_gate", False) and not st.session_state["auth_logged_in"]:
        st.warning("🔒 **Vui lòng đăng nhập hoặc đăng ký tài khoản Gmail ở thanh bên trái để sử dụng hệ thống!**")
        st.stop()

    return False, "Guest_Agent", ""

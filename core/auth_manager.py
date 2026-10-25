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
            if "accounts" not in data:
                data["accounts"] = {}
            if "smtp_config" not in data:
                data["smtp_config"] = {"sender_email": "", "app_password": "", "require_login_gate": False}
            return data
    except Exception:
        return {"smtp_config": {"sender_email": "", "app_password": "", "require_login_gate": False}, "accounts": {}}


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
    """Lấy thông tin Gmail SMTP từ Streamlit Secrets hoặc từ cấu hình Admin."""
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

    # Loại bỏ khoảng trắng thừa trong mật khẩu ứng dụng 16 ký tự của Google
    app_pw_clean = app_pw.replace(" ", "")
    return sender, app_pw_clean


def send_real_otp_email_strict(target_email: str, otp_code: str, purpose: str, db: dict) -> tuple[bool, str]:
    """
    Gửi mã OTP 6 số ĐỘC QUYỀN qua máy chủ smtp.gmail.com (Cổng 465 SSL).
    TUYỆT ĐỐI KHÔNG BAO GIỜ HIỂN THỊ MÃ OTP LÊN MÀN HÌNH WEB!
    Nếu người dùng nhập Gmail ảo/không có thật, họ sẽ không bao giờ có mã OTP để vào.
    """
    sender, app_pw = get_smtp_credentials(db)

    if not sender or not app_pw:
        return (
            False,
            "⚠️ **Máy chủ gửi thư Gmail chưa được liên kết!**\n\n"
            "Chủ web (Admin) vui lòng mở mục **'⚙️ Admin: Real Gmail OTP Server'** ngay bên dưới, "
            "nhập mã PIN `HCMUS3001` và điền **Sender Gmail + Google 16-Char App Password** (hoặc dán vào Streamlit `Secrets`) "
            "để hệ thống gửi mã OTP thật về hộp thư Gmail!"
        )

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[Ultimate Secret Messenger] Mã xác thực OTP ({purpose}): {otp_code}"
        msg["From"] = f"Ultimate Secret Messenger <{sender}>"
        msg["To"] = target_email

        html_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto; background: #0f172a; color: #f8fafc; padding: 24px; border-radius: 12px; border: 2px solid #3b82f6;">
            <h2 style="color: #60a5fa; margin-top: 0;">🛡️ Ultimate Secret Messenger</h2>
            <p style="color: #cbd5e1; font-size: 15px;">Xin chào / Hello,</p>
            <p style="color: #cbd5e1; font-size: 15px;">Bạn vừa yêu cầu mã xác thực OTP cho thao tác: <b>{purpose}</b>.</p>
            <div style="background: #1e293b; border: 1.5px dashed #38bdf8; padding: 16px; text-align: center; border-radius: 10px; margin: 20px 0;">
                <span style="font-size: 13px; color: #94a3b8; display: block; margin-bottom: 6px;">MÃ XÁC THỰC 6 SỐ CỦA BẠN (6-DIGIT OTP):</span>
                <span style="font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #fde047;">{otp_code}</span>
            </div>
            <p style="color: #94a3b8; font-size: 13px;">⏳ Mã này có hiệu lực trong vòng <b>5 phút</b>. Tuyệt đối không chia sẻ mã này cho người khác.</p>
            <hr style="border: 0; border-top: 1px solid #334155; margin: 16px 0;">
            <p style="color: #64748b; font-size: 12px; margin-bottom: 0;">Ultimate Secret Messenger • Security & Cryptography Platform by Lê Hoàng Phú Hiếu (FIT - VNUHCM-US)</p>
        </div>
        """
        msg.set_content(f"Your Ultimate Secret Messenger OTP Code for {purpose} is: {otp_code} (Valid for 5 minutes).")
        msg.add_alternative(html_body, subtype="html")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(sender, app_pw)
            server.send_message(msg)

        return (
            True,
            f"📧 **Đã gửi mã OTP 6 số tới hộp thư `{target_email}`!**\n\n"
            f"👉 Hãy mở ứng dụng **Gmail** của bạn (kiểm tra cả Hộp thư đến và thư mục Quảng cáo/Spam) để lấy mã 6 số nhập vào ô bên dưới!"
        )
    except smtplib.SMTPAuthenticationError:
        return (
            False,
            "❌ **Lỗi xác thực Google SMTP:** Mật khẩu ứng dụng (App Password) chưa đúng! "
            "Lưu ý: Bạn phải dùng **Mật khẩu ứng dụng 16 ký tự** tạo tại `myaccount.google.com/apppasswords` chứ không phải mật khẩu đăng nhập Gmail thông thường."
        )
    except Exception as e:
        return False, f"❌ Không thể gửi email tới `{target_email}`: {str(e)}"


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
    # TRẠNG THÁI 1: ĐÃ ĐĂNG NHẬP BẰNG GMAIL THẬT
    # ==========================================================================
    if st.session_state["auth_logged_in"]:
        email_now = st.session_state["auth_email"]
        callsign_now = st.session_state["auth_callsign"]
        st.session_state["ctf_user"] = callsign_now
        st.session_state["acad_user"] = callsign_now

        st.markdown(f"""
        <div class="gmail-profile-card">
            <div style="font-size:0.7rem; color:#34d399; font-weight:800; letter-spacing:0.8px;">🟢 VERIFIED GMAIL ACCOUNT</div>
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
    # TRẠNG THÁI 2: CHƯA ĐĂNG NHẬP
    # ==========================================================================
    st.markdown("### 📧 Gmail Account Center")
    if smtp_ready:
        st.caption(f"🟢 **Real Gmail OTP Active** (`{sender_cfg}`) — Fake emails cannot register!")
    else:
        st.caption("🟠 **Waiting for Admin SMTP Link** — Open the Admin box below to link your Google App Password.")

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
                st.error("❌ Account not found! Switch to '➕ Register' to verify your Gmail via OTP.")
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
                    st.error("❌ Incorrect password! Use '🔄 Forgot Pass' to receive a reset OTP via Gmail.")

    # --- TAB 2: ĐĂNG KÝ (BẮT BUỘC NHẬN MÃ OTP QUA HỘP THƯ GMAIL THẬT 100%) ---
    with tab_reg:
        st.caption("🔒 A 6-digit OTP will be sent directly to your Gmail inbox. Fake/non-existent Gmails cannot receive the code!")
        reg_email = st.text_input("📧 Your Real Gmail (`@gmail.com`):", placeholder="your.real.email@gmail.com", key="in_reg_gmail").strip().lower()
        reg_callsign = st.text_input("🕵️ Agent Display Name:", placeholder="e.g. taolagautruc", key="in_reg_callsign").strip()
        reg_pass = st.text_input("🔒 Create Password (Min 6 chars):", type="password", key="in_reg_pass")
        reg_pass2 = st.text_input("🔒 Confirm Password:", type="password", key="in_reg_pass2")

        if st.button("📨 Step 1: Send OTP to My Gmail Inbox", use_container_width=True, key="btn_send_reg_otp"):
            ok_mail, mail_msg = validate_strict_google_gmail(reg_email)
            if not ok_mail:
                st.error(mail_msg)
            elif reg_email in accounts:
                st.warning("⚠️ This Gmail is already registered! Please sign in or use '🔄 Forgot Pass'.")
            elif len(reg_pass) < 6:
                st.error("❌ Password must be at least 6 characters!")
            elif reg_pass != reg_pass2:
                st.error("❌ Passwords do not match!")
            else:
                otp_code = f"{random.randint(100000, 999999)}"
                sent_ok, smtp_msg = send_real_otp_email_strict(reg_email, otp_code, "Account Registration", db)
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
            otp_in = st.text_input("🔢 Enter 6-Digit OTP from Your Gmail Inbox:", max_chars=6, placeholder="Check your Gmail...", key="in_reg_otp_code").strip()
            if st.button("✅ Step 2: Verify OTP & Activate Account", type="primary", use_container_width=True, key="btn_verify_reg_otp"):
                pend = st.session_state["pending_reg_data"]
                if time.time() > pend["exp"]:
                    st.error("⏰ OTP expired (5 minutes limit)! Please click Step 1 to send a new OTP.")
                elif hashlib.sha256(otp_in.encode("utf-8")).hexdigest() != pend["otp_hash"]:
                    st.error("❌ Incorrect OTP code! Please check the exact 6 digits sent to your Gmail inbox.")
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

    # --- TAB 3: QUÊN MẬT KHẨU (GỬI MÃ OTP KHÔI PHỤC TỚI HỘP THƯ GMAIL THẬT 100%) ---
    with tab_forgot:
        st.caption("🔄 Enter your registered Gmail. We will send a 6-digit Password Reset OTP directly to your Gmail inbox!")
        fg_email = st.text_input("📧 Your Registered Gmail:", placeholder="yourname@gmail.com", key="in_fg_email").strip().lower()

        if st.button("📨 Send 6-Digit Reset OTP to Gmail", use_container_width=True, key="btn_fg_send_otp"):
            if fg_email not in accounts:
                st.error("❌ No registered account found with this Gmail address!")
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
            rst_code_in = st.text_input("🔢 Enter 6-Digit OTP from Your Gmail:", max_chars=6, key="in_fg_otp").strip()
            fg_new_pass = st.text_input("🔑 Enter New Password (Min 6 chars):", type="password", key="in_fg_newpass2")
            if st.button("✅ Verify OTP & Save New Password", type="primary", use_container_width=True, key="btn_fg_otp_save"):
                r_pend = st.session_state["pending_reset_otp"]
                if time.time() > r_pend["exp"]:
                    st.error("⏰ OTP expired!")
                elif hashlib.sha256(rst_code_in.encode("utf-8")).hexdigest() != r_pend["otp_hash"]:
                    st.error("❌ Incorrect OTP code!")
                elif len(fg_new_pass) < 6:
                    st.error("❌ Password must be at least 6 characters!")
                else:
                    acc = accounts[fg_email]
                    new_salt = hashlib.sha256(f"{fg_email}_{time.time()}".encode("utf-8")).hexdigest()[:16]
                    acc["salt"] = new_salt
                    acc["password_hash"] = hash_password(fg_new_pass, new_salt)
                    save_auth_db(db)
                    del st.session_state["pending_reset_otp"]
                    st.success("✅ Password reset successfully! Switch to '🔑 Sign In' to log in.")

    # ==========================================================================
    # BẢNG CẤU HÌNH MÁY CHỦ GMAIL OTP DÀNH RIÊNG CHO CHỦ WEB (ADMIN)
    # ==========================================================================
    with st.expander("⚙️ Admin: Real Gmail OTP Server", expanded=not smtp_ready):
        st.caption("🔑 Enter Admin PIN (`HCMUS3001`) to link your Gmail & 16-char Google App Password (`myaccount.google.com/apppasswords`):")
        adm_pin = st.text_input("Admin PIN:", type="password", key="smtp_adm_pin")
        if adm_pin.strip() == "HCMUS3001":
            cfg = db.get("smtp_config", {})
            s_mail = st.text_input("1. Admin Sender Gmail:", value=cfg.get("sender_email", "hieulehoangphu@gmail.com"))
            s_apw = st.text_input("2. Google 16-Char App Password:", value=cfg.get("app_password", ""), type="password", placeholder="xxxx xxxx xxxx xxxx")
            req_gate = st.checkbox("🔒 Lock entire web app until user signs in with verified Gmail", value=cfg.get("require_login_gate", False))

            c_adm1, c_adm2 = st.columns(2)
            with c_adm1:
                if st.button("💾 Save SMTP Link", type="primary", use_container_width=True):
                    db["smtp_config"] = {
                        "sender_email": s_mail.strip(),
                        "app_password": s_apw.strip().replace(" ", ""),
                        "require_login_gate": req_gate
                    }
                    save_auth_db(db)
                    st.success("✅ Linked Gmail SMTP Server!")
                    st.rerun()
            with c_adm2:
                if st.button("📨 Test Send Email", use_container_width=True):
                    db["smtp_config"] = {
                        "sender_email": s_mail.strip(),
                        "app_password": s_apw.strip().replace(" ", ""),
                        "require_login_gate": req_gate
                    }
                    save_auth_db(db)
                    ok_t, msg_t = send_real_otp_email_strict(s_mail.strip(), "888999", "SMTP Server Test", db)
                    if ok_t:
                        st.success("✅ Sent test email! Check your inbox!")
                    else:
                        st.error(msg_t)

    # Nếu Admin bật chế độ bắt buộc đăng nhập mới được dùng web (Strict Login Gate)
    if db.get("smtp_config", {}).get("require_login_gate", False) and not st.session_state["auth_logged_in"]:
        st.warning("🔒 **Authentication Required:** Please sign in with your verified Gmail account on the left Sidebar to access the platform!")
        st.stop()

    return False, "Guest_Agent", ""

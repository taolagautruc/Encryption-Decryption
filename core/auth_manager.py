import streamlit as st
import json
import os
import re
import random
import time
import hashlib
import socket
import ssl
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
                "sender_email": "phuhieu3001@gmail.com",
                "app_password": "",
                "require_login_gate": False
            },
            "accounts": {
                "phuhieu3001@gmail.com": {
                    "email": "phuhieu3001@gmail.com",
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
                data["smtp_config"] = {
                    "sender_email": "phuhieu3001@gmail.com",
                    "app_password": "",
                    "require_login_gate": False
                }
            return data
    except Exception:
        return {
            "admin_pin_hash": DEFAULT_ADMIN_PIN_HASH,
            "smtp_config": {"sender_email": "phuhieu3001@gmail.com", "app_password": "", "require_login_gate": False},
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
        return False, "❌ Rejected: Placeholder or disposable email detected. Please use a real Gmail address."

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

    if sender and "@" not in sender:
        sender = f"{sender}@gmail.com"

    clean_pw = "".join(ch for ch in app_pw if ch.isalnum())
    return sender.lower(), clean_pw


def send_real_otp_email_strict(target_email: str, otp_code: str, purpose: str, db: dict) -> tuple[bool, str]:
    sender, app_pw = get_smtp_credentials(db)

    if not sender or not app_pw:
        return (
            False,
            "⚠️ **SMTP Server Not Linked Yet!**\n\n"
            "The Administrator must open **'⚙️ Web Owner Settings (Admin Only)'** below, enter the Owner PIN, "
            "and save the **Sender Gmail + 16-Character Google App Password**."
        )

    if len(app_pw) != 16:
        return (
            False,
            f"⚠️ **Invalid App Password Length: Currently `{len(app_pw)}` characters (Must be exactly 16 letters)!**\n\n"
            f"Please open **'⚙️ Web Owner Settings'** below and paste all 16 letters of your Google App Password."
        )

    msg = EmailMessage()
    msg["Subject"] = f"[Ultimate Secret Messenger] Verification OTP ({purpose}): {otp_code}"
    msg["From"] = f"Ultimate Secret Messenger <{sender}>"
    msg["To"] = target_email

    html_body = (
        f"<div style='font-family:Arial,sans-serif;max-width:520px;margin:0 auto;background:#0f172a;color:#f8fafc;padding:24px;border-radius:12px;border:2px solid #3b82f6;'>"
        f"<h2 style='color:#60a5fa;margin-top:0;'>🛡️ Ultimate Secret Messenger</h2>"
        f"<p style='color:#cbd5e1;font-size:15px;'>Hello <b>{target_email}</b>,</p>"
        f"<p style='color:#cbd5e1;font-size:15px;'>Your 6-digit verification code for <b>{purpose}</b> is:</p>"
        f"<div style='background:#1e293b;border:1.5px dashed #38bdf8;padding:16px;text-align:center;border-radius:10px;margin:20px 0;'>"
        f"<span style='font-size:12px;color:#94a3b8;display:block;margin-bottom:6px;'>YOUR 6-DIGIT VERIFICATION CODE:</span>"
        f"<span style='font-size:32px;font-weight:800;letter-spacing:6px;color:#fde047;'>{otp_code}</span>"
        f"</div>"
        f"<p style='color:#94a3b8;font-size:13px;'>⏳ This code expires in <b>5 minutes</b>.</p>"
        f"</div>"
    )
    msg.set_content(f"Your Ultimate Secret Messenger 6-digit OTP Code for {purpose} is: {otp_code} (Valid for 5 minutes).")
    msg.add_alternative(html_body, subtype="html")

    try:
        smtp_ipv4 = socket.gethostbyname("smtp.gmail.com")
    except Exception:
        smtp_ipv4 = "smtp.gmail.com"

    ssl_ctx = ssl.create_default_context()

    try:
        with smtplib.SMTP(smtp_ipv4, 587, local_hostname="localhost", timeout=15) as server:
            server.ehlo("localhost")
            server.starttls(context=ssl_ctx)
            server.ehlo("localhost")
            server.login(sender, app_pw)
            server.send_message(msg)
        return (
            True,
            f"📧 **6-Digit OTP sent to `{target_email}`!**\n\n"
            f"👉 Please open your **`{target_email}`** Gmail inbox (check Inbox & Spam) and enter the 6-digit code in Step 2 below!"
        )
    except smtplib.SMTPAuthenticationError:
        return (
            False,
            f"❌ **Google SMTP Authentication Failed for `{sender}`!**\n\n"
            f"Please verify in **Web Owner Settings** that `{sender}` is the exact Gmail account that generated the 16-letter App Password."
        )
    except Exception as err_587:
        try:
            with smtplib.SMTP_SSL(smtp_ipv4, 465, local_hostname="localhost", context=ssl_ctx, timeout=15) as server:
                server.ehlo("localhost")
                server.login(sender, app_pw)
                server.send_message(msg)
            return (
                True,
                f"📧 **6-Digit OTP sent to `{target_email}`!**\n\n"
                f"👉 Please open your **`{target_email}`** Gmail inbox and enter the 6-digit code in Step 2 below!"
            )
        except Exception as err_465:
            return False, f"❌ Failed to send email to `{target_email}` ({err_587} / {err_465})."


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
    smtp_ready = bool(sender_cfg and len(app_pw_cfg) == 16)

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

    if st.session_state["auth_logged_in"]:
        email_now = st.session_state["auth_email"]
        callsign_now = st.session_state["auth_callsign"]
        st.session_state["ctf_user"] = callsign_now
        st.session_state["acad_user"] = callsign_now
        st.session_state["chat_agent_name"] = callsign_now

        st.markdown(f"""
        <div class="gmail-profile-card">
            <div style="font-size:0.7rem; color:#34d399; font-weight:800; letter-spacing:0.8px;">🟢 VERIFIED GMAIL ACCOUNT</div>
            <div style="font-size:1.05rem; font-weight:800; color:#fde047; margin-top:4px;">🕵️ {callsign_now}</div>
            <div style="font-size:0.8rem; color:#cbd5e1; margin-top:2px; word-break:break-all;">📧 {email_now}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sign Out (Switch Account)", use_container_width=True, key="btn_gmail_logout"):
            st.session_state["auth_logged_in"] = False
            st.session_state["auth_email"] = ""
            st.session_state["auth_callsign"] = "Guest_Agent"
            st.rerun()

        return True, callsign_now, email_now

    st.markdown("### 🛡️ Account Sign In / Register")
    if smtp_ready:
        st.caption(f"🟢 **Live Gmail OTP Active** (`{sender_cfg}`)")
    else:
        st.caption(f"🟠 **SMTP App Password Status:** `{len(app_pw_cfg)}/16` chars configured in Web Owner Settings.")

    tab_login, tab_reg, tab_forgot = st.tabs([
        "🔑 Sign In",
        "➕ Register",
        "🔄 Reset Pass"
    ])

    with tab_login:
        login_id = st.text_input("📧 Gmail or Username:", placeholder="yourname@gmail.com", key="in_login_gmail").strip()
        login_pass = st.text_input("🔒 Password:", type="password", placeholder="Enter password...", key="in_login_pass")

        if st.button("🚀 Sign In to Platform", type="primary", use_container_width=True, key="btn_gmail_signin"):
            if not login_id or not login_pass:
                st.error("❌ Please enter both your Gmail/Username and Password!")
            else:
                matched_email = None
                if login_id.lower() in accounts:
                    matched_email = login_id.lower()
                else:
                    for em_k, acc_v in accounts.items():
                        if acc_v.get("callsign", "").lower() == login_id.lower():
                            matched_email = em_k
                            break

                if not matched_email:
                    st.warning("⚠️ Account not found! Please switch to the **'➕ Register'** tab to verify your Gmail via OTP first.")
                else:
                    acc = accounts[matched_email]
                    calc_hash = hash_password(login_pass, acc["salt"])
                    if calc_hash == acc["password_hash"]:
                        acc["last_login"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                        save_auth_db(db)
                        sync_authenticated_identity(acc["callsign"], matched_email)
                        st.toast(f"✅ Welcome back, {acc['callsign']}!", icon="🎉")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password! Use the '🔄 Reset Pass' tab if you forgot it.")

    with tab_reg:
        st.caption("📋 **3-Step Verification:** Verify your real Gmail via 6-digit OTP first -> Then set your Username & Password!")

        st.markdown("**Step 1: Verify Your Real Gmail**")
        reg_email = st.text_input(
            "📧 Your Gmail Address (`@gmail.com`):",
            placeholder="yourname@gmail.com",
            key="in_reg_gmail"
        ).strip().lower()

        if st.button("📨 Send 6-Digit OTP to This Gmail", use_container_width=True, key="btn_send_reg_otp"):
            ok_mail, mail_msg = validate_strict_google_gmail(reg_email)
            if not ok_mail:
                st.error(mail_msg)
            elif reg_email in accounts:
                st.info("✅ This Gmail is already registered! Please switch to the **'🔑 Sign In'** tab.")
            else:
                otp_code = f"{random.randint(100000, 999999)}"
                sent_ok, smtp_msg = send_real_otp_email_strict(reg_email, otp_code, "New Account Registration", db)
                if sent_ok:
                    st.session_state["reg_step1_otp"] = {
                        "email": reg_email,
                        "otp_hash": hashlib.sha256(otp_code.encode("utf-8")).hexdigest(),
                        "exp": time.time() + 300,
                        "otp_verified": False
                    }
                    st.success(smtp_msg)
                else:
                    st.error(smtp_msg)

        pend_reg = st.session_state.get("reg_step1_otp")
        if pend_reg and pend_reg.get("email") == reg_email:
            st.divider()
            if not pend_reg.get("otp_verified", False):
                st.markdown("**Step 2: Enter 6-Digit OTP from Gmail**")
                otp_in = st.text_input("🔢 6-Digit OTP Code:", max_chars=6, placeholder="Check your Gmail inbox...", key="in_reg_otp_code").strip()
                if st.button("✅ Verify OTP Code", type="primary", use_container_width=True, key="btn_verify_otp_step2"):
                    if time.time() > pend_reg["exp"]:
                        st.error("⏰ OTP expired (5-minute limit)! Please click Step 1 to resend.")
                    elif hashlib.sha256(otp_in.encode("utf-8")).hexdigest() != pend_reg["otp_hash"]:
                        st.error("❌ Invalid OTP code! Please check the exact 6 digits in your Gmail inbox.")
                    else:
                        st.session_state["reg_step1_otp"]["otp_verified"] = True
                        st.rerun()
            else:
                st.success(f"🎉 Gmail **`{reg_email}`** verified! Now create your profile:")
                st.markdown("**Step 3: Create Username & Password**")
                reg_callsign = st.text_input("🕵️ Display Username (Callsign):", placeholder="e.g. hieu3001", key="in_reg_callsign").strip()
                reg_pass = st.text_input("🔒 Create Password (Min 6 chars):", type="password", key="in_reg_pass")
                reg_pass2 = st.text_input("🔒 Confirm Password:", type="password", key="in_reg_pass2")

                if st.button("🚀 Complete Registration & Enter App", type="primary", use_container_width=True, key="btn_finish_step3"):
                    if len(reg_callsign) < 2:
                        st.error("❌ Please enter a Display Username (at least 2 characters)!")
                    elif any(acc_v.get("callsign", "").lower() == reg_callsign.lower() for acc_v in accounts.values()):
                        st.error("❌ This Username is already taken! Please choose another one.")
                    elif len(reg_pass) < 6:
                        st.error("❌ Password must be at least 6 characters long!")
                    elif reg_pass != reg_pass2:
                        st.error("❌ Passwords do not match!")
                    else:
                        salt = hashlib.sha256(f"{reg_email}_{time.time()}".encode("utf-8")).hexdigest()[:16]
                        p_hash = hash_password(reg_pass, salt)
                        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                        accounts[reg_email] = {
                            "email": reg_email,
                            "callsign": reg_callsign,
                            "salt": salt,
                            "password_hash": p_hash,
                            "verified": True,
                            "created_at": now_str,
                            "last_login": now_str
                        }
                        db["accounts"] = accounts
                        save_auth_db(db)
                        del st.session_state["reg_step1_otp"]
                        sync_authenticated_identity(reg_callsign, reg_email)
                        st.balloons()
                        st.rerun()

    with tab_forgot:
        st.caption("🔄 Enter your registered Gmail to receive a 6-digit Password Reset OTP:")
        fg_email = st.text_input("📧 Registered Gmail:", placeholder="yourname@gmail.com", key="in_fg_email").strip().lower()

        if st.button("📨 Send Password Reset OTP", use_container_width=True, key="btn_fg_send_otp"):
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
            rst_code_in = st.text_input("🔢 Enter 6-Digit OTP from Gmail:", max_chars=6, key="in_fg_otp").strip()
            fg_new_pass = st.text_input("🔑 Enter New Password (Min 6 chars):", type="password", key="in_fg_newpass2")
            if st.button("✅ Verify OTP & Save New Password", type="primary", use_container_width=True, key="btn_fg_otp_save"):
                r_pend = st.session_state["pending_reset_otp"]
                if time.time() > r_pend["exp"]:
                    st.error("⏰ OTP expired!")
                elif hashlib.sha256(rst_code_in.encode("utf-8")).hexdigest() != r_pend["otp_hash"]:
                    st.error("❌ Incorrect OTP code!")
                elif len(fg_new_pass) < 6:
                    st.error("❌ New password must be at least 6 characters!")
                else:
                    acc = accounts[fg_email]
                    new_salt = hashlib.sha256(f"{fg_email}_{time.time()}".encode("utf-8")).hexdigest()[:16]
                    acc["salt"] = new_salt
                    acc["password_hash"] = hash_password(fg_new_pass, new_salt)
                    save_auth_db(db)
                    del st.session_state["pending_reset_otp"]
                    st.success("✅ Password reset successfully! Switch to '🔑 Sign In' to log in.")

    with st.expander("⚙️ Web Owner Settings (Admin Only)", expanded=False):
        st.caption("🔒 Restricted to Platform Architect (Le Hoang Phu Hieu).")
        adm_pin_in = st.text_input("🔑 Enter Owner PIN:", type="password", key="smtp_adm_pin")

        saved_admin_hash = db.get("admin_pin_hash", DEFAULT_ADMIN_PIN_HASH)
        is_owner = (hashlib.sha256(adm_pin_in.strip().encode("utf-8")).hexdigest() == saved_admin_hash) if adm_pin_in else False

        if is_owner:
            st.success("🔓 Web Owner Console Unlocked!")
            cfg = db.get("smtp_config", {})

            s_mail = st.text_input("1. Official OTP Sender Gmail:", value=cfg.get("sender_email", "phuhieu3001@gmail.com"))
            s_apw = st.text_input("2. Google 16-Character App Password:", value=cfg.get("app_password", ""), type="password")
            clean_apw_len = len("".join(ch for ch in s_apw if ch.isalnum()))
            st.caption(f"📏 Current App Password Length: **`{clean_apw_len} / 16` characters** {'✅' if clean_apw_len == 16 else '⚠️ (Must be exactly 16 letters!)'}")

            req_gate = st.checkbox("🔒 Require Gmail Login before accessing platform", value=cfg.get("require_login_gate", False))

            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if st.button("💾 Save SMTP Config", type="primary", use_container_width=True):
                    clean_sender = s_mail.strip().lower()
                    if clean_sender and "@" not in clean_sender:
                        clean_sender += "@gmail.com"
                    db["smtp_config"] = {
                        "sender_email": clean_sender,
                        "app_password": "".join(ch for ch in s_apw if ch.isalnum()),
                        "require_login_gate": req_gate
                    }
                    save_auth_db(db)
                    st.success("✅ Saved SMTP Server Config!")
                    st.rerun()
            with c_b2:
                if st.button("📨 Test Send OTP", use_container_width=True):
                    clean_sender = s_mail.strip().lower()
                    if clean_sender and "@" not in clean_sender:
                        clean_sender += "@gmail.com"
                    db["smtp_config"] = {
                        "sender_email": clean_sender,
                        "app_password": "".join(ch for ch in s_apw if ch.isalnum()),
                        "require_login_gate": req_gate
                    }
                    save_auth_db(db)
                    ok_t, msg_t = send_real_otp_email_strict(clean_sender, "888999", "SMTP Connection Test", db)
                    if ok_t:
                        st.success("✅ Test email sent! Check your inbox!")
                    else:
                        st.error(msg_t)

            st.divider()
            new_owner_pin = st.text_input("Change Owner PIN (Min 4 chars):", type="password", placeholder="Enter new PIN...")
            if st.button("🔄 Update Owner PIN", use_container_width=True):
                if len(new_owner_pin.strip()) < 4:
                    st.warning("PIN must be at least 4 characters!")
                else:
                    db["admin_pin_hash"] = hashlib.sha256(new_owner_pin.strip().encode("utf-8")).hexdigest()
                    save_auth_db(db)
                    st.success("✅ Owner PIN updated successfully!")

    return False, "Guest_Agent", ""

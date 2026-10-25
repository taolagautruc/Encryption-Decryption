import streamlit as st
import json
import os
import re
import time
import hashlib
from datetime import datetime, timezone

AUTH_DB_FILE = "user_accounts_db.json"


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()


def load_auth_db() -> dict:
    default_salt = "usm_hcmus_2026_salt"
    default_pass_hash = hash_password("123456", default_salt)
    default_pin_hash = hashlib.sha256(b"3001").hexdigest()

    if not os.path.exists(AUTH_DB_FILE):
        seed_db = {
            "users": {
                "taolagautruc": {
                    "username": "taolagautruc",
                    "salt": default_salt,
                    "password_hash": default_pass_hash,
                    "recovery_pin_hash": default_pin_hash,
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
            if "users" not in data:
                data["users"] = {
                    "taolagautruc": {
                        "username": "taolagautruc",
                        "salt": default_salt,
                        "password_hash": default_pass_hash,
                        "recovery_pin_hash": default_pin_hash,
                        "created_at": "2026-10-25 UTC",
                        "last_login": "2026-10-25 UTC"
                    }
                }
                save_auth_db(data)
            return data
    except Exception:
        return {"users": {}}


def save_auth_db(data: dict):
    with open(AUTH_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def sync_authenticated_identity(username: str):
    """Synchronize the logged-in Username across all 8 modules & games on the platform."""
    st.session_state["auth_logged_in"] = True
    st.session_state["auth_callsign"] = username
    st.session_state["auth_email"] = username
    st.session_state["ctf_user"] = username
    st.session_state["acad_user"] = username
    st.session_state["chat_agent_name"] = username
    st.session_state["sdk_player_in"] = username
    st.session_state["comm_user_in"] = username


def render_sidebar_gmail_auth() -> tuple[bool, str, str]:
    """
    Renders a clean, fast Username + Password Authentication Center on the Sidebar (100% English UI).
    Keeps function name 'render_sidebar_gmail_auth' for 100% compatibility with streamlit_app.py.
    """
    db = load_auth_db()
    users = db.get("users", {})

    if "auth_logged_in" not in st.session_state:
        st.session_state["auth_logged_in"] = False
        st.session_state["auth_callsign"] = "Guest_Agent"

    st.markdown("""
    <style>
        .agent-profile-card {
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
    # STATE 1: LOGGED IN
    # ==========================================================================
    if st.session_state["auth_logged_in"]:
        active_user = st.session_state["auth_callsign"]
        st.session_state["ctf_user"] = active_user
        st.session_state["acad_user"] = active_user
        st.session_state["chat_agent_name"] = active_user

        st.markdown(f"""
        <div class="agent-profile-card">
            <div style="font-size:0.7rem; color:#34d399; font-weight:800; letter-spacing:0.8px;">🟢 ACTIVE PLAYER ACCOUNT</div>
            <div style="font-size:1.08rem; font-weight:800; color:#fde047; margin-top:4px;">🕵️ {active_user}</div>
            <div style="font-size:0.76rem; color:#94a3b8; margin-top:2px;">All scores, progress & items synced</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Log Out (Switch Account)", use_container_width=True, key="btn_acc_logout"):
            st.session_state["auth_logged_in"] = False
            st.session_state["auth_callsign"] = "Guest_Agent"
            st.rerun()

        return True, active_user, active_user

    # ==========================================================================
    # STATE 2: NOT LOGGED IN (USERNAME + PASSWORD)
    # ==========================================================================
    st.markdown("### 🛡️ Player Account Center")
    st.caption("Sign in with your Username & Password to save and restore all scores, chat rooms, and items.")

    tab_login, tab_reg, tab_reset = st.tabs([
        "🔑 Sign In",
        "➕ Create Account",
        "🔄 Reset Pass"
    ])

    # --- TAB 1: SIGN IN ---
    with tab_login:
        login_user = st.text_input("🕵️ Username:", placeholder="e.g. taolagautruc", key="in_login_user").strip()
        login_pass = st.text_input("🔒 Password:", type="password", placeholder="Enter password...", key="in_login_pass")

        if st.button("🚀 Sign In", type="primary", use_container_width=True, key="btn_user_signin"):
            if not login_user or not login_pass:
                st.error("❌ Please enter both Username and Password!")
            else:
                matched_key = None
                for u_k in users.keys():
                    if u_k.lower() == login_user.lower():
                        matched_key = u_k
                        break

                if not matched_key:
                    st.warning("⚠️ Username not found! Switch to the **'➕ Create Account'** tab to register.")
                else:
                    acc = users[matched_key]
                    calc_hash = hash_password(login_pass, acc["salt"])
                    if calc_hash == acc["password_hash"]:
                        acc["last_login"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                        save_auth_db(db)
                        sync_authenticated_identity(acc["username"])
                        st.toast(f"✅ Welcome back, {acc['username']}!", icon="🎉")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password! Use '🔄 Reset Pass' if you forgot it.")

    # --- TAB 2: CREATE NEW ACCOUNT ---
    with tab_reg:
        reg_user = st.text_input("🕵️ Choose Username (3–20 chars):", placeholder="e.g. hieu3001", key="in_reg_user").strip()
        reg_pass = st.text_input("🔒 Create Password (Min 4 chars):", type="password", key="in_reg_pass")
        reg_pass2 = st.text_input("🔒 Confirm Password:", type="password", key="in_reg_pass2")
        reg_pin = st.text_input(
            "🛡️ 4-Digit Recovery PIN (For Password Reset):",
            max_chars=6,
            placeholder="e.g. 3001",
            key="in_reg_pin"
        ).strip()

        if st.button("✨ Create Account & Start Playing", type="primary", use_container_width=True, key="btn_user_reg"):
            if len(reg_user) < 3 or len(reg_user) > 20:
                st.error("❌ Username must be between 3 and 20 characters!")
            elif not re.match(r"^[a-zA-Z0-9_.-]+$", reg_user):
                st.error("❌ Username can only contain letters, numbers, `_`, `.`, or `-`!")
            elif any(u_k.lower() == reg_user.lower() for u_k in users.keys()):
                st.warning("⚠️ This Username is already taken! Please sign in or pick another name.")
            elif len(reg_pass) < 4:
                st.error("❌ Password must be at least 4 characters!")
            elif reg_pass != reg_pass2:
                st.error("❌ Passwords do not match!")
            elif len(reg_pin) < 4 or not reg_pin.isdigit():
                st.error("❌ Please enter a 4 to 6 digit numeric Recovery PIN (e.g. `3001`)!")
            else:
                salt = hashlib.sha256(f"{reg_user}_{time.time()}".encode("utf-8")).hexdigest()[:16]
                p_hash = hash_password(reg_pass, salt)
                pin_hash = hashlib.sha256(reg_pin.encode("utf-8")).hexdigest()
                now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

                users[reg_user] = {
                    "username": reg_user,
                    "salt": salt,
                    "password_hash": p_hash,
                    "recovery_pin_hash": pin_hash,
                    "created_at": now_str,
                    "last_login": now_str
                }
                db["users"] = users
                save_auth_db(db)
                sync_authenticated_identity(reg_user)
                st.balloons()
                st.toast(f"🎉 Account '{reg_user}' created!", icon="🎉")
                st.rerun()

    # --- TAB 3: RESET FORGOTTEN PASSWORD ---
    with tab_reset:
        st.caption("🔄 Forgot your password? Enter your Username and Recovery PIN to set a new password:")
        rst_user = st.text_input("🕵️ Your Username:", placeholder="e.g. hieu3001", key="in_rst_user").strip()
        rst_pin = st.text_input("🛡️ Your Recovery PIN:", type="password", max_chars=6, placeholder="e.g. 3001", key="in_rst_pin").strip()
        rst_new_pass = st.text_input("🔑 New Password (Min 4 chars):", type="password", key="in_rst_newpass")

        if st.button("🔄 Reset Password Now", type="primary", use_container_width=True, key="btn_user_rst"):
            matched_key = None
            for u_k in users.keys():
                if u_k.lower() == rst_user.lower():
                    matched_key = u_k
                    break

            if not matched_key:
                st.error("❌ Username not found!")
            elif len(rst_new_pass) < 4:
                st.error("❌ New password must be at least 4 characters!")
            else:
                acc = users[matched_key]
                saved_pin_hash = acc.get("recovery_pin_hash", hashlib.sha256(b"3001").hexdigest())
                if hashlib.sha256(rst_pin.encode("utf-8")).hexdigest() == saved_pin_hash:
                    new_salt = hashlib.sha256(f"{matched_key}_{time.time()}".encode("utf-8")).hexdigest()[:16]
                    acc["salt"] = new_salt
                    acc["password_hash"] = hash_password(rst_new_pass, new_salt)
                    save_auth_db(db)
                    st.success("✅ Password updated! Switch to '🔑 Sign In' to log in.")
                else:
                    st.error("❌ Incorrect Recovery PIN!")

    return False, "Guest_Agent", ""

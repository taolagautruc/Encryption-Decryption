import streamlit as st
import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

ECOSYSTEM_DB_FILES = {
    "chat_rooms": "chat_rooms_db.json",
    "ctf_arena": "ctf_arena_db.json",
    "academy_lms": "academy_lms_db.json",
    "sudoku_arena": "sudoku_arena_db.json",
    "community_hub": "community_hub_db.json"
}

CLOUD_CONFIG_FILE = "cloud_sync_config.json"

def inject_mobile_app_viewport_css():
    st.markdown("""
    <style>
        html, body, [class*="css"] {
            -webkit-tap-highlight-color: transparent !important;
            touch-action: manipulation !important;
            -webkit-overflow-scrolling: touch !important;
        }
        @media screen and (max-width: 768px) {
            input, select, textarea {
                font-size: 16px !important;
            }
            .hero-title {
                font-size: 1.75rem !important;
            }
            .hero-box {
                padding: 16px 18px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def load_local_ecosystem_bundle() -> dict:
    bundle = {
        "meta": {
            "platform": "Ultimate Secret Messenger Ecosystem",
            "author": "Le Hoang Phu Hieu (HCMUS)",
            "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        },
        "databases": {}
    }
    for key, filename in ECOSYSTEM_DB_FILES.items():
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    bundle["databases"][key] = json.load(f)
            except Exception:
                bundle["databases"][key] = {}
        else:
            bundle["databases"][key] = {}
    return bundle

def restore_local_ecosystem_bundle(bundle: dict) -> tuple[bool, str]:
    if not isinstance(bundle, dict) or "databases" not in bundle:
        return False, "❌ Invalid backup bundle format (missing 'databases' key)."
    dbs = bundle["databases"]
    restored_count = 0
    for key, filename in ECOSYSTEM_DB_FILES.items():
        if key in dbs and isinstance(dbs[key], dict):
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(dbs[key], f, ensure_ascii=False, indent=4)
            restored_count += 1
    return True, f"✅ Successfully synchronized & restored {restored_count}/5 databases!"

def get_cloud_credentials() -> tuple[str, str]:
    url, secret = "", ""
    try:
        if "CLOUD_DB_URL" in st.secrets:
            url = str(st.secrets["CLOUD_DB_URL"]).strip()
        if "CLOUD_DB_SECRET" in st.secrets:
            secret = str(st.secrets["CLOUD_DB_SECRET"]).strip()
    except Exception:
        pass
    if not url and os.path.exists(CLOUD_CONFIG_FILE):
        try:
            with open(CLOUD_CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                url = cfg.get("url", "")
                secret = cfg.get("secret", "")
        except Exception:
            pass
    return url, secret

def push_bundle_to_cloud(cloud_url: str, cloud_secret: str = "") -> tuple[bool, str]:
    clean_url = cloud_url.strip().rstrip("/")
    if not clean_url.startswith("http"):
        return False, "❌ Cloud URL must start with https://"
    if not clean_url.endswith(".json"):
        clean_url += "/usm_ecosystem_master.json"
    if cloud_secret.strip():
        sep = "&" if "?" in clean_url else "?"
        clean_url += f"{sep}auth={cloud_secret.strip()}"
    bundle = load_local_ecosystem_bundle()
    payload_bytes = json.dumps(bundle, ensure_ascii=False).encode("utf-8")
    try:
        req = urllib.request.Request(clean_url, data=payload_bytes, headers={"Content-Type": "application/json"}, method="PUT")
        with urllib.request.urlopen(req, timeout=8) as resp:
            if 200 <= resp.status < 300:
                return True, f"☁️ Pushed all 5 databases to Cloud successfully at {bundle['meta']['exported_at']}!"
            return False, f"❌ Cloud server returned status {resp.status}"
    except Exception as e:
        return False, f"❌ Cloud Push Error: {str(e)}"

def pull_bundle_from_cloud(cloud_url: str, cloud_secret: str = "") -> tuple[bool, str]:
    clean_url = cloud_url.strip().rstrip("/")
    if not clean_url.startswith("http"):
        return False, "❌ Cloud URL must start with https://"
    if not clean_url.endswith(".json"):
        clean_url += "/usm_ecosystem_master.json"
    if cloud_secret.strip():
        sep = "&" if "?" in clean_url else "?"
        clean_url += f"{sep}auth={cloud_secret.strip()}"
    try:
        req = urllib.request.Request(clean_url, headers={"Accept": "application/json"}, method="GET")
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw_data = resp.read().decode("utf-8")
            if not raw_data or raw_data == "null":
                return False, "⚠️ Cloud database is currently empty. Click 'Push Local Data to Cloud' first!"
            bundle = json.loads(raw_data)
            return restore_local_ecosystem_bundle(bundle)
    except Exception as e:
        return False, f"❌ Cloud Pull Error: {str(e)}"

def auto_boot_cloud_sync():
    inject_mobile_app_viewport_css()
    if "cloud_boot_synced" not in st.session_state:
        st.session_state.cloud_boot_synced = True
        c_url, c_sec = get_cloud_credentials()
        if c_url:
            pull_bundle_from_cloud(c_url, c_sec)

def render_cloud_and_mobile_studio():
    st.markdown("""
    <div class="hero-box" style="padding: 22px 30px; margin-bottom: 18px; background: linear-gradient(135deg, #090d16 0%, #064e3b 50%, #0f172a 100%); border: 1px solid #10b981;">
        <div class="hero-badge" style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border-color: #10b981;">📲 INSTALL ON PHONE • SAVE YOUR PROGRESS • ADMIN CLOUD STUDIO</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Mobile App Guide & Account Backup Center</h2>
        <p class="hero-sub">
            <b>What is this section for?</b><br>
            1️⃣ <b>For Players:</b> Learn how to install this web app onto your iPhone, iPad, or Android home screen in 10 seconds, and download a backup copy of your scores/account.<br>
            2️⃣ <b>For Server Admin (Developer):</b> Connect the server to Firebase Cloud so player accounts are never lost when the server restarts.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================================================
    # PHẦN 1: DÀNH CHO MỌI NGƯỜI CHƠI (CÀI APP LÊN ĐIỆN THOẠI & LƯU TÀI KHOẢN)
    # ==========================================================================
    st.markdown("### 📱 Part 1: Install as a Mobile App on Your Phone / Tablet (For All Users)")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown("""
        <div class="feat-card" style="border-color:#3b82f6;">
            <div class="feat-title">🍎 How to Install on iPhone & iPad (iOS Safari)</div>
            <div class="feat-desc">
                1. Open <b>encryption-decryption3001.streamlit.app</b> in <b>Safari</b>.<br>
                2. Tap the <b>Share button</b> (the square with an upward arrow <code>⬆️</code> at the bottom/top bar).<br>
                3. Scroll down and tap <b>"Add to Home Screen" (Thêm vào Màn hình chính)</b>.<br>
                4. Tap <b>Add</b>! The 🛡️ app icon will appear on your iPhone/iPad just like a native App Store game!
            </div>
        </div>
        """, unsafe_allow_html=True)
    with p_col2:
        st.markdown("""
        <div class="feat-card" style="border-color:#10b981;">
            <div class="feat-title">🤖 How to Install on Android Phones (Chrome)</div>
            <div class="feat-desc">
                1. Open this website in <b>Google Chrome</b> on your Android phone.<br>
                2. Tap the <b>Three Dots menu (<code>⋮</code>)</b> in the top-right corner.<br>
                3. Tap <b>"Install App"</b> or <b>"Add to Home Screen" (Cài đặt ứng dụng)</b>.<br>
                4. Launch the app directly from your phone screen in full-screen mode!
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("### 💾 Part 2: Backup & Restore Server Progress (Prevent Data Loss)")
    st.info(
        "💡 **Why is this important?** Because this web app runs on a free cloud server, the server goes to sleep when inactive and resets local files. "
        "Before closing the tab after a long gaming session, you can **Download the Save File (.JSON)** below, and **Upload** it next time to restore all scores, chat rooms, and badges in 1 second!"
    )

    bundle_now = load_local_ecosystem_bundle()
    dbs_now = bundle_now["databases"]

    bk_col1, bk_col2 = st.columns(2)
    with bk_col1:
        json_str = json.dumps(bundle_now, ensure_ascii=False, indent=2)
        st.download_button(
            label="⬇️ Step A: Download Current Progress Backup (.JSON)",
            data=json_str.encode("utf-8"),
            file_name=f"usm_save_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            type="primary",
            use_container_width=True
        )
    with bk_col2:
        up_bk = st.file_uploader("⬆️ Step B: Upload Save File (.JSON) to Restore Progress:", type=["json"], label_visibility="collapsed")
        if up_bk and st.button("🔄 Restore All Scores, Rooms & Accounts Now", type="primary", use_container_width=True):
            try:
                loaded_bundle = json.loads(up_bk.getvalue().decode("utf-8"))
                ok, msg = restore_local_ecosystem_bundle(loaded_bundle)
                if ok:
                    st.balloons()
                    st.success(msg)
                    time.sleep(1.0)
                    st.rerun()
                else:
                    st.error(msg)
            except Exception as e:
                st.error(f"❌ Corrupted JSON file: {str(e)}")

    st.divider()

    # ==========================================================================
    # PHẦN 2: DÀNH RIÊNG CHO NHÀ PHÁT TRIỂN (ADMIN CONSOLE ĐƯỢC THU GỌN)
    # ==========================================================================
    with st.expander("🔐 Part 3: Developer & Server Admin Console (Firebase Cloud Sync & Xcode/Android Studio Builder)"):
        st.caption("🛠️ This advanced section is for the project architect (**Lê Hoàng Phú Hiếu**) to configure automatic Firebase Cloud storage and export native mobile source code packages.")

        n_rooms = len(dbs_now.get("chat_rooms", {}))
        n_ctf_users = len(dbs_now.get("ctf_arena", {}).get("users", {}))
        n_students = len(dbs_now.get("academy_lms", {}).get("students", {}))
        n_sudoku = len(dbs_now.get("sudoku_arena", {}).get("leaderboard", {}))
        n_ugc = len(dbs_now.get("community_hub", {}).get("ugc_puzzles", []))

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("💬 Chat Rooms", f"{n_rooms}")
        m2.metric("🕹️ CTF Agents", f"{n_ctf_users}")
        m3.metric("🎓 Students", f"{n_students}")
        m4.metric("🧩 Sudoku Players", f"{n_sudoku}")
        m5.metric("🌍 UGC Puzzles", f"{n_ugc}")

        adm_tab1, adm_tab2 = st.tabs([
            "☁️ Automatic Firebase Realtime DB Sync",
            "📦 Xcode (iOS) & Android Studio Config Generator"
        ])

        with adm_tab1:
            saved_url, saved_sec = get_cloud_credentials()
            in_url = st.text_input("🌐 Firebase Realtime Database URL:", value=saved_url, placeholder="https://your-project-default-rtdb.firebaseio.com")
            in_sec = st.text_input("🔑 Firebase Database Secret (Optional):", value=saved_sec, type="password")
            b1, b2, b3 = st.columns(3)
            if b1.button("💾 Save Cloud URL", use_container_width=True):
                with open(CLOUD_CONFIG_FILE, "w", encoding="utf-8") as f:
                    json.dump({"url": in_url.strip(), "secret": in_sec.strip()}, f)
                st.success("✅ Saved!")
            if b2.button("☁️⬆️ Push Server Data to Firebase", type="primary", use_container_width=True):
                ok, msg = push_bundle_to_cloud(in_url, in_sec)
                if ok: st.success(msg)
                else: st.error(msg)
            if b3.button("☁️⬇️ Pull Data from Firebase", use_container_width=True):
                ok, msg = pull_bundle_from_cloud(in_url, in_sec)
                if ok:
                    st.success(msg)
                    st.rerun()
                else: st.error(msg)

        with adm_tab2:
            st.write("Download these files when compiling the native mobile app in Xcode or Android Studio using Ionic Capacitor:")
            cap_config = json.dumps({
                "appId": "com.hcmus.phuhieu.secretmessenger",
                "appName": "Ultimate Secret Messenger",
                "webDir": "www",
                "server": {"url": "https://encryption-decryption3001.streamlit.app", "cleartext": False}
            }, indent=2)
            st.code(cap_config, language="json")

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
    """
    Tối ưu hóa giao diện cảm ứng cho Điện thoại & iPad (iOS Safari / Android Chrome):
    - Ngăn Safari trên iPhone tự động zoom (phóng to) màn hình khi người dùng chạm vào ô nhập liệu.
    - Loại bỏ độ trễ cảm ứng 300ms (touch-action: manipulation) và làm mượt thao tác cuộn.
    """
    st.markdown("""
    <style>
        html, body, [class*="css"] {
            -webkit-tap-highlight-color: transparent !important;
            touch-action: manipulation !important;
            -webkit-overflow-scrolling: touch !important;
        }
        /* Ngăn iOS Safari tự động zoom khi chạm vào ô input trên điện thoại */
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
    """Đọc toàn bộ 5 file .json trong hệ sinh thái và đóng gói thành 1 gói dữ liệu thống nhất."""
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
    """Khôi phục dữ liệu từ gói bundle (hoặc từ Cloud) xuống cả 5 file .json cục bộ."""
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
    """Lấy URL và Secret Key của Cloud Database từ st.secrets hoặc từ cấu hình phiên."""
    url = ""
    secret = ""
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
    """Đẩy toàn bộ 5 cơ sở dữ liệu lên Cloud Realtime Database (Firebase REST / Custom JSON Endpoint)."""
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
        req = urllib.request.Request(
            clean_url,
            data=payload_bytes,
            headers={"Content-Type": "application/json"},
            method="PUT"
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            if 200 <= resp.status < 300:
                return True, f"☁️ Pushed all 5 databases to Cloud successfully at {bundle['meta']['exported_at']}!"
            return False, f"❌ Cloud server returned status {resp.status}"
    except Exception as e:
        return False, f"❌ Cloud Push Error: {str(e)}"

def pull_bundle_from_cloud(cloud_url: str, cloud_secret: str = "") -> tuple[bool, str]:
    """Tải toàn bộ 5 cơ sở dữ liệu từ Cloud Realtime Database về máy chủ Streamlit."""
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
    """Tự động khôi phục dữ liệu từ Cloud ngay khi máy chủ Streamlit vừa khởi động lại."""
    inject_mobile_app_viewport_css()
    if "cloud_boot_synced" not in st.session_state:
        st.session_state.cloud_boot_synced = True
        c_url, c_sec = get_cloud_credentials()
        if c_url:
            pull_bundle_from_cloud(c_url, c_sec)

def render_cloud_and_mobile_studio():
    st.markdown("""
    <div class="hero-box" style="padding: 22px 30px; margin-bottom: 18px; background: linear-gradient(135deg, #090d16 0%, #064e3b 50%, #0f172a 100%); border: 1px solid #10b981;">
        <div class="hero-badge" style="background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border-color: #10b981;">☁️📱 PILLAR 4 INFRASTRUCTURE • CLOUD REALTIME DB • APP STORE & GOOGLE PLAY BUILDER</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Cloud Database Sync & Mobile App Packaging Studio</h2>
        <p class="hero-sub">
            Connect your ecosystem to a permanent Cloud Realtime Database, backup/restore all 5 JSON databases in 1 click, and generate ready-to-compile iOS (App Store) & Android (Google Play) mobile app packages!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Thống kê trực tiếp dung lượng và trạng thái của 5 Database trong hệ sinh thái
    bundle_now = load_local_ecosystem_bundle()
    dbs_now = bundle_now["databases"]

    n_rooms = len(dbs_now.get("chat_rooms", {}))
    n_ctf_users = len(dbs_now.get("ctf_arena", {}).get("users", {}))
    n_students = len(dbs_now.get("academy_lms", {}).get("students", {}))
    n_sudoku = len(dbs_now.get("sudoku_arena", {}).get("leaderboard", {}))
    n_ugc = len(dbs_now.get("community_hub", {}).get("ugc_puzzles", []))

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("💬 Chat Rooms DB", f"{n_rooms} Rooms", "chat_rooms_db.json")
    m2.metric("🕹️ CTF Arena DB", f"{n_ctf_users} Agents", "ctf_arena_db.json")
    m3.metric("🎓 Academy LMS DB", f"{n_students} Students", "academy_lms_db.json")
    m4.metric("🧩 Sudoku Arena DB", f"{n_sudoku} Players", "sudoku_arena_db.json")
    m5.metric("🌍 Community UGC DB", f"{n_ugc} Puzzles", "community_hub_db.json")

    st.write("")
    tab_cloud, tab_backup, tab_mobile, tab_store_guide = st.tabs([
        "☁️ 1. Cloud Realtime DB Sync (Firebase / REST)",
        "💾 2. 1-Click Master Snapshot Backup & Restore",
        "📱 3. Mobile App Package Generator (Capacitor / PWA)",
        "🚀 4. App Store & Google Play Publishing Checklist"
    ])

    # ==========================================================================
    # TAB 1: KẾT NỐI ĐÁM MÂY FIREBASE / SUPABASE REST
    # ==========================================================================
    with tab_cloud:
        st.markdown("""
        <div class="ws-banner">
            <h4>☁️ Permanent Cloud Database Connector (Zero-Dependency REST Engine)</h4>
            <p>
                Connect your app to a free <b>Google Firebase Realtime Database</b> (or any JSON REST endpoint) so your players' scores, chat rooms, and UGC puzzles are stored permanently in the cloud and never reset when Streamlit restarts!
            </p>
        </div>
        """, unsafe_allow_html=True)

        saved_url, saved_sec = get_cloud_credentials()

        c_col1, c_col2 = st.columns([1.6, 1.4])
        with c_col1:
            in_url = st.text_input(
                "🌐 Cloud Realtime Database URL (e.g. Firebase Realtime DB URL):",
                value=saved_url,
                placeholder="https://your-project-id-default-rtdb.asia-southeast1.firebasedatabase.app"
            )
            in_sec = st.text_input(
                "🔑 Database Secret / Auth Token (Optional if rules are public during testing):",
                value=saved_sec,
                type="password",
                placeholder="Paste Firebase Database Secret or Auth Token..."
            )

            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("💾 Save Cloud Config", use_container_width=True):
                    with open(CLOUD_CONFIG_FILE, "w", encoding="utf-8") as f:
                        json.dump({"url": in_url.strip(), "secret": in_sec.strip()}, f)
                    st.success("✅ Saved Cloud configuration!")
            with b2:
                if st.button("☁️⬆️ Push All 5 DBs to Cloud", type="primary", use_container_width=True):
                    ok, msg = push_bundle_to_cloud(in_url, in_sec)
                    if ok:
                        st.balloons()
                        st.success(msg)
                    else:
                        st.error(msg)
            with b3:
                if st.button("☁️⬇️ Pull & Restore from Cloud", use_container_width=True):
                    ok, msg = pull_bundle_from_cloud(in_url, in_sec)
                    if ok:
                        st.success(msg)
                        time.sleep(1.0)
                        st.rerun()
                    else:
                        st.error(msg)

        with c_col2:
            st.markdown("##### 📖 How to Get a Free Cloud URL in 60 Seconds:")
            st.info(
                "1. Go to [console.firebase.google.com](https://console.firebase.google.com/) and click **Create a project** (100% Free Spark Plan).\n"
                "2. In the left menu, click **Build → Realtime Database → Create Database**.\n"
                "3. Copy your database URL (e.g., `https://usm-cipher-default-rtdb.firebaseio.com/`) and paste it on the left!\n"
                "4. **Pro Tip for Streamlit Cloud:** Open your app settings on Streamlit Cloud → **Secrets**, and add:\n"
                "```toml\n"
                'CLOUD_DB_URL = "[https://your-db.firebaseio.com](https://your-db.firebaseio.com)"\n'
                'CLOUD_DB_SECRET = "your_secret_token"\n'
                "```\n"
                "Your app will automatically sync with the cloud on every boot!"
            )

    # ==========================================================================
    # TAB 2: SAO LƯU & KHÔI PHỤC TOÀN BỘ 5 DATABASE BẰNG 1 CLICK
    # ==========================================================================
    with tab_backup:
        st.markdown("""
        <div class="ws-banner">
            <h4>💾 1-Click Master Ecosystem Snapshot (Export & Import All 5 Databases)</h4>
            <p>Download all 5 JSON databases (Chat Rooms, CTF Arena, Academy XP, Sudoku Leaderboard, and Community Puzzles) into a single unified file, or upload a snapshot to restore everything instantly.</p>
        </div>
        """, unsafe_allow_html=True)

        bk_col1, bk_col2 = st.columns(2)
        with bk_col1:
            st.markdown("##### ⬇️ Export Master Snapshot")
            json_str = json.dumps(bundle_now, ensure_ascii=False, indent=2)
            st.download_button(
                label="⬇️ Download Master Ecosystem Backup (.JSON)",
                data=json_str.encode("utf-8"),
                file_name=f"usm_master_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                type="primary",
                use_container_width=True
            )
            with st.expander("🔍 Preview Live Ecosystem JSON Tree"):
                st.code(json_str[:1500] + "\n... [Truncated for preview]", language="json")

        with bk_col2:
            st.markdown("##### ⬆️ Restore from Master Snapshot")
            up_bk = st.file_uploader("Upload Master Backup (.JSON):", type=["json"])
            if up_bk and st.button("🔄 Restore All 5 Databases Now", type="primary", use_container_width=True):
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

    # ==========================================================================
    # TAB 3: BỘ PHÁT SINH MÃ NGUỒN ĐÓNG GÓI MOBILE APP (CAPACITOR / PWA)
    # ==========================================================================
    with tab_mobile:
        st.markdown("""
        <div class="ws-banner">
            <h4>📱 Cross-Platform Mobile App Generator (iOS App Store & Google Play Store)</h4>
            <p>Generate customized configuration files to wrap your live platform into a native iOS (`.ipa` via Xcode) and Android (`.apk / .aab` via Android Studio) application using <b>Ionic Capacitor</b> or install it directly as a <b>PWA</b>!</p>
        </div>
        """, unsafe_allow_html=True)

        app_col1, app_col2 = st.columns(2)
        with app_col1:
            app_name = st.text_input("📱 Mobile App Display Name:", value="Ultimate Secret Messenger")
            app_id = st.text_input("🆔 Bundle ID / Package Name (Reverse Domain):", value="com.hcmus.phuhieu.secretmessenger")
        with app_col2:
            prod_url = st.text_input("🌐 Production Server URL:", value="https://encryption-decryption3001.streamlit.app")
            app_ver = st.text_input("🔢 Release Version:", value="2.0.0")

        cap_config = json.dumps({
            "appId": app_id.strip(),
            "appName": app_name.strip(),
            "webDir": "www",
            "bundledWebRuntime": False,
            "server": {
                "url": prod_url.strip(),
                "cleartext": False,
                "allowNavigation": ["*.streamlit.app"]
            },
            "ios": {
                "contentInset": "always",
                "backgroundColor": "#0f172a"
            },
            "android": {
                "backgroundColor": "#0f172a",
                "allowMixedContent": False
            }
        }, indent=2)

        pkg_json = json.dumps({
            "name": "ultimate-secret-messenger-mobile",
            "version": app_ver.strip(),
            "description": "Zero-Trust Cryptography, Steganography & Mind Arcade Suite by Le Hoang Phu Hieu (HCMUS)",
            "author": "Le Hoang Phu Hieu <phuhieu3001@gmail.com>",
            "scripts": {
                "init:mobile": "npx cap add android && npx cap add ios",
                "sync": "npx cap sync",
                "open:android": "npx cap open android",
                "open:ios": "npx cap open ios"
            },
            "dependencies": {
                "@capacitor/core": "^6.0.0",
                "@capacitor/ios": "^6.0.0",
                "@capacitor/android": "^6.0.0",
                "@capacitor/splash-screen": "^6.0.0",
                "@capacitor/status-bar": "^6.0.0"
            },
            "devDependencies": {
                "@capacitor/cli": "^6.0.0"
            }
        }, indent=2)

        pwa_manifest = json.dumps({
            "name": app_name.strip(),
            "short_name": "SecretMsg",
            "start_url": prod_url.strip(),
            "display": "standalone",
            "background_color": "#0f172a",
            "theme_color": "#3b82f6",
            "orientation": "portrait-primary"
        }, indent=2)

        c_f1, c_f2, c_f3 = st.columns(3)
        with c_f1:
            st.markdown("##### 1️⃣ `capacitor.config.json`")
            st.code(cap_config, language="json")
            st.download_button("⬇️ Download capacitor.config.json", data=cap_config, file_name="capacitor.config.json", mime="application/json", use_container_width=True)
        with c_f2:
            st.markdown("##### 2️⃣ `package.json`")
            st.code(pkg_json, language="json")
            st.download_button("⬇️ Download package.json", data=pkg_json, file_name="package.json", mime="application/json", use_container_width=True)
        with c_f3:
            st.markdown("##### 3️⃣ `manifest.json` (PWA)")
            st.code(pwa_manifest, language="json")
            st.download_button("⬇️ Download manifest.json", data=pwa_manifest, file_name="manifest.json", mime="application/json", use_container_width=True)

    # ==========================================================================
    # TAB 4: HƯỚNG DẪN ĐƯA APP LÊN GOOGLE PLAY & APPLE APP STORE
    # ==========================================================================
    with tab_store_guide:
        st.markdown("""
        <div class="ws-banner">
            <h4>🚀 Step-by-Step Commercial Deployment Guide (Google Play & Apple App Store)</h4>
            <p>Follow this exact engineering roadmap to compile and publish your project onto mobile app stores.</p>
        </div>
        """, unsafe_allow_html=True)

        g1, g2 = st.columns(2)
        with g1:
            st.markdown("""
            #### 🤖 Path A: Publishing to Google Play Store (Android `.aab`)
            1. **Install Node.js & Android Studio** on your MacBook.
            2. Create a new folder `usm-mobile`, place the downloaded `package.json` and `capacitor.config.json` inside it, and create an empty `www/index.html` file.
            3. Open Terminal in that folder and run:
               ```bash
               npm install
               npx cap add android
               npx cap open android
               ```
            4. In **Android Studio**, go to **Build → Generate Signed Bundle / APK → Android App Bundle (`.aab`)**.
            5. Register a **Google Play Console** account ($25 one-time fee), create a new app, upload your `.aab` file, fill in the Privacy Policy (Zero-Trust Encryption), and submit for review!
            """)
        with g2:
            st.markdown("""
            #### 🍎 Path B: Publishing to Apple App Store (iOS via Xcode on macOS)
            1. Since you are already using **macOS**, install **Xcode** from the Mac App Store.
            2. In your `usm-mobile` terminal folder, run:
               ```bash
               npx cap add ios
               npx cap open ios
               ```
            3. In **Xcode**, select your Team Signing Certificate (Apple Developer Program — $99/year, or free Apple ID for testing directly on your own iPhone/iPad via USB cable!).
            4. **Passing Apple App Store Review (Guideline 4.2):**
               - Apple requires apps to feel native and offer rich interactive value. Because your platform includes an **Offline-ready 9x9 Sudoku Engine, Audio/Visual Steganography Labs, 20-Module University LMS, and Agent ID Cards**, it provides massive utility!
               - Add Capacitor's `@capacitor/local-notifications` or Biometric FaceID lock in Xcode before submitting to App Store Connect.
            """)

import time
from datetime import datetime, timezone
import streamlit as st
from core.cipher_engine import load_massive_symbol_pool, calculate_key_entropy, BASE_CHARS
from core.chat_storage import load_all_rooms


def render_home(group_config: dict):
    """Hiển thị giao diện Trang chủ (Dashboard & System Status)."""
    st.subheader("🌐 Global Cryptography Suite — Executive Dashboard")
    st.markdown(
        "Welcome to the **Multi-Layer Secret Communication Platform**. "
        "Designed for zero-trust group messaging, linguistic camouflage, and pixel-level steganography."
    )

    # 1. Hàng chỉ số thống kê hệ thống (System Metrics)
    symbols_count = len(load_massive_symbol_pool())
    rooms_count = len(load_all_rooms())
    utc_now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Base Character Set", f"{len(BASE_CHARS)} chars", "Global + VN")
    col2.metric("Unicode Symbol Vault", f"{symbols_count}+", "Dynamic Pool")
    col3.metric("Active Secret Rooms", f"{rooms_count} rooms", "SHA-256 Protected")
    col4.metric("Universal Clock", utc_now, "Timezone-Free")

    st.divider()

    # 2. Máy đo độ an toàn của Quy luật Nhóm hiện tại (Live Security Analyzer)
    st.markdown("### 🛡️ Live Group Key Strength Analyzer")
    if not group_config.get("secret_seed"):
        st.info("💡 Enter your **Group Secret Passphrase** in the top configuration bar to measure your key's brute-force resistance.")
    else:
        stats = calculate_key_entropy(
            group_config["secret_seed"],
            group_config["pattern_list"],
            group_config["shift_step"],
            group_config["custom_pairs"]
        )
        years = stats["years_to_crack"]
        years_str = f"{years:.2e} years" if years > 1e6 else f"{years:,.1f} years"

        c1, c2 = st.columns([2, 1])
        with c1:
            st.success(f"** Active Protection:** Your custom rule combines a passphrase with **{stats['selected_icons']} Unicode symbols**.")
            st.write(f"At **10 Billion guesses/second**, a supercomputer would need approximately **{years_str}** to brute-force this group's configuration.")
        with c2:
            st.code(
                f"Passphrase Length : {len(group_config['secret_seed'])}\n"
                f"Symbol Pattern    : {' '.join(group_config['pattern_list']) or 'None'}\n"
                f"Shift Offset      : +{group_config['shift_step']}\n"
                f"Reverse Structure : {group_config['reverse_rule']}"
            )

    st.divider()

    # 3. Sơ đồ kiến trúc các phân khu trên Website
    st.markdown("### 🧭 Platform Modules Overview")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("#### 🔐 Cipher Workspace\n- **Text Cipher:** Multi-layer encryption with UTC Self-Destruct & Time-Capsule.\n- **Camouflage Studio:** Disguise ciphertexts as natural English emails.\n- **Steganography Lab:** Hide secrets inside PNG pixels.")
    with m2:
        st.markdown("#### 💬 Secret Chat Rooms\n- **Password-Protected Rooms:** Create persistent rooms with SHA-256 locks.\n- **Hybrid Messaging:** Send plain text, raw ciphers, or disguised sentences.\n- **1-Click Decrypt:** Decode individual messages or the entire chat history.")
    with m3:
        st.markdown("#### 🕹️ CTF & Academy\n- **Crypto Challenges:** Test your skills with multi-level cipher puzzles.\n- **Visual Academy:** Inspect LSB pixel bits and English camouflage byte matrices in real time.")

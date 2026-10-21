import io
import streamlit as st
from PIL import Image, ImageDraw
from core.cipher_engine import build_custom_key, encrypt_core
from core.camouflage import encode_english_camouflage
from core.steganography import encode_image_lsb


@st.cache_data
def _generate_challenge_data():
    """Tạo dữ liệu mật thư tự động cho 3 cấp độ CTF."""
    # Level 1: Basic Cipher (Passphrase: "ALPHA", No symbols, Shift: 5)
    key_lv1 = build_custom_key("ALPHA", [], 5, "")
    flag_lv1 = "FLAG{SHIFT_MASTER_2026}"
    cipher_lv1 = encrypt_core(flag_lv1, key_lv1, False, "NONE", 0)

    # Level 2: English Camouflage (Passphrase: "SHADOW", No symbols, Shift: 0)
    key_lv2 = build_custom_key("SHADOW", [], 0, "")
    flag_lv2 = "FLAG{LINGUISTIC_GHOST}"
    cipher_lv2 = encrypt_core(flag_lv2, key_lv2, True, "NONE", 0)
    camo_lv2 = encode_english_camouflage(cipher_lv2)

    # Level 3: Image Steganography (Passphrase: "PIXEL", No symbols, Shift: 10)
    key_lv3 = build_custom_key("PIXEL", [], 10, "")
    flag_lv3 = "FLAG{LSB_FORENSIC_PRO}"
    cipher_lv3 = encrypt_core(flag_lv3, key_lv3, False, "NONE", 0)

    # Tạo một bức ảnh PNG mẫu chứa mật thư cho Level 3
    img = Image.new("RGB", (320, 120), color=(25, 35, 60))
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 310, 110], outline=(0, 200, 255), width=2)
    draw.text((35, 50), "TOP SECRET EVIDENCE #03", fill=(255, 255, 255))
    stego_img = encode_image_lsb(img, cipher_lv3)
    buf = io.BytesIO()
    stego_img.save(buf, format="PNG")

    return {
        "lv1": {"cipher": cipher_lv1, "flag": flag_lv1},
        "lv2": {"camo": camo_lv2, "flag": flag_lv2},
        "lv3": {"img_bytes": buf.getvalue(), "flag": flag_lv3}
    }


def render_challenges():
    """Giao diện Đấu trường Giải đố Mật thư (Capture The Flag - CTF)."""
    st.subheader("🕹️ Crypto Challenges & CTF Arena")
    st.caption(
        "Test your cryptanalysis skills! Use the **Cipher Workspace** tools to crack these 3 missions and capture the flags."
    )

    if "solved_levels" not in st.session_state:
        st.session_state.solved_levels = set()

    data = _generate_challenge_data()
    solved_count = len(st.session_state.solved_levels)

    # Thanh tiến độ điểm số
    c1, c2, c3 = st.columns(3)
    c1.metric("Completed Missions", f"{solved_count} / 3")
    c2.metric("Current Score", f"{solved_count * 100} PTS")
    rank = "🏆 Grandmaster Cryptanalyst" if solved_count == 3 else ("🕵️‍♂️ Field Agent" if solved_count > 0 else "🌱 Rookie")
    c3.metric("Agent Rank", rank)

    st.progress(solved_count / 3)
    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "🟢 Level 1: The Shifted Intercept",
        "🟡 Level 2: The Disguised Email",
        "🔴 Level 3: Hidden in the Pixels"
    ])

    # --- LEVEL 1 ---
    with tab1:
        st.markdown("#### Mission 1: Intercepted Transmission (100 PTS)")
        st.write(
            "Our intelligence intercepted the following raw ciphertext. "
            "Informants report the group used **no symbols**, passphrase **`ALPHA`**, and a **Shift Step of `5`**."
        )
        st.code(data["lv1"]["cipher"], language=None)
        st.info("💡 **Hint:** Configure the top bar with Passphrase `ALPHA`, clear all Symbols, set Shift Step to `5`, and decode in **Cipher Workspace**.")

        ans1 = st.text_input("Submit Flag for Level 1:", placeholder="FLAG{...}", key="in_lv1")
        if st.button("🚩 Verify Flag #1", type="primary"):
            if ans1.strip() == data["lv1"]["flag"]:
                st.session_state.solved_levels.add(1)
                st.balloons()
                st.success("🎉 Correct Flag! Level 1 Completed (+100 PTS).")
                st.rerun()
            else:
                st.error("❌ Incorrect flag! Check your Group Cipher Rules and try again.")

    # --- LEVEL 2 ---
    with tab2:
        st.markdown("#### Mission 2: Corporate Espionage (100 PTS)")
        st.write(
            "A suspect sent this seemingly normal business update. "
            "We know they used **English Camouflage Mode**, passphrase **`SHADOW`**, **No Symbols**, **Shift `0`**, and checked **Reverse Cipher Structure**."
        )
        st.code(data["lv2"]["camo"], language=None)

        ans2 = st.text_input("Submit Flag for Level 2:", placeholder="FLAG{...}", key="in_lv2")
        if st.button("🚩 Verify Flag #2", type="primary"):
            if ans2.strip() == data["lv2"]["flag"]:
                st.session_state.solved_levels.add(2)
                st.balloons()
                st.success("🎉 Awesome! You cracked the Linguistic Camouflage (+100 PTS).")
                st.rerun()
            else:
                st.error("❌ Incorrect flag! Make sure 'Reverse Cipher Structure' and 'Camouflage Mode' are enabled when decoding.")

    # --- LEVEL 3 ---
    with tab3:
        st.markdown("#### Mission 3: Digital Forensics (100 PTS)")
        st.write(
            "This PNG badge was recovered from a secure server. "
            "Extract the hidden LSB payload using Passphrase **`PIXEL`**, **No Symbols**, and **Shift Step `10`**."
        )
        st.image(data["lv3"]["img_bytes"], caption="Suspect Carrier Image (PNG)")
        st.download_button(
            label="⬇️ Download Evidence Image (evidence_lv3.png)",
            data=data["lv3"]["img_bytes"],
            file_name="evidence_lv3.png",
            mime="image/png"
        )

        ans3 = st.text_input("Submit Flag for Level 3:", placeholder="FLAG{...}", key="in_lv3")
        if st.button("🚩 Verify Flag #3", type="primary"):
            if ans3.strip() == data["lv3"]["flag"]:
                st.session_state.solved_levels.add(3)
                st.balloons()
                st.success("🏆 Masterpiece! You extracted the hidden pixel payload (+100 PTS).")
                st.rerun()
            else:
                st.error("❌ Incorrect flag! Download the PNG and extract it in the Image Steganography Lab.")

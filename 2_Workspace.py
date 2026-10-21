import io
import time
import streamlit as st
from PIL import Image
from core.cipher_engine import encrypt_core, decrypt_core
from core.camouflage import encode_english_camouflage, decode_english_camouflage
from core.steganography import encode_image_lsb, decode_image_lsb


def render_workspace(group_config: dict, group_key: list, sub_mode: str = "Text Cipher & Time-Lock"):
    """Giao diện khu vực Công cụ Mã hóa, Ngụy trang và Giấu tin trong ảnh."""
    if not group_config.get("secret_seed"):
        st.warning("⚠️ Please enter a **Group Secret Passphrase** in the top configuration bar to unlock the Cipher Workspace!")
        return

    # --- CHẾ ĐỘ 1: MÃ HÓA VĂN BẢN, TỰ HỦY & NGỤY TRANG ---
    if sub_mode in ["Text Cipher & Time-Lock", "English Camouflage Studio"]:
        st.subheader("🔐 Multi-Layer Text Cipher & Camouflage Studio")
        st.caption("Encrypt messages with UTC Self-Destruct timers or disguise them as natural English emails.")

        tab_enc, tab_dec = st.tabs(["📤 Encrypt & Disguise", "📥 Decrypt & Restore"])

        with tab_enc:
            plain_input = st.text_area(
                "Enter your secret message (Supports Global English, Vietnamese & Symbols):",
                height=110
            )
            col1, col2 = st.columns(2)
            with col1:
                time_mode_ui = st.selectbox(
                    "⏱️ Time-Control Mode (Global UTC):",
                    [
                        "No Time Limit",
                        "🔥 Self-Destruct (Expire after X mins)",
                        "⏳ Time-Capsule (Unlock after X mins)"
                    ]
                )
                mins_val = 20
                if time_mode_ui != "No Time Limit":
                    mins_val = st.number_input("Set Countdown (Minutes):", min_value=1, max_value=10080, value=20)
            with col2:
                default_camo = (sub_mode == "English Camouflage Studio")
                use_camo = st.checkbox("🎭 Dynamic English Camouflage", value=default_camo)
                st.caption("Generates unique English business sentences on every click using random salt.")

            if st.button("🔒 Generate Output", type="primary"):
                if plain_input.strip():
                    mode_code = "NONE"
                    target_ts = 0
                    now_utc = int(time.time())

                    if "Self-Destruct" in time_mode_ui:
                        mode_code = "EXPIRE"
                        target_ts = now_utc + (mins_val * 60)
                    elif "Time-Capsule" in time_mode_ui:
                        mode_code = "WAIT"
                        target_ts = now_utc + (mins_val * 60)

                    cypher = encrypt_core(plain_input, group_key, group_config["reverse_rule"], mode_code, target_ts)
                    if use_camo:
                        final_out = encode_english_camouflage(cypher)
                        st.success("🎭 Disguised English Text (Safe to send anywhere):")
                    else:
                        final_out = cypher
                        st.success("🔒 Encrypted Ciphertext:")
                    st.code(final_out, language=None)
                else:
                    st.error("Please enter a message to encrypt!")

        with tab_dec:
            cypher_input = st.text_area("Paste Ciphertext or Disguised English Text here:", height=110)
            is_camo_input = st.checkbox(
                "This message is disguised in English Camouflage Mode (🎭)",
                value=(sub_mode == "English Camouflage Studio")
            )

            if st.button("🔓 Decode Message", type="primary"):
                if cypher_input.strip():
                    try:
                        target_cypher = (
                            decode_english_camouflage(cypher_input)
                            if is_camo_input else cypher_input.strip()
                        )
                        ok, result = decrypt_core(target_cypher, group_key, group_config["reverse_rule"])
                        if ok:
                            st.success("🎉 Decrypted Original Message:")
                            st.info(result)
                        else:
                            st.error(result)
                    except Exception as e:
                        st.error(f"❌ Could not decode: {e}")
                else:
                    st.error("Please paste a message to decode!")

    # --- CHẾ ĐỘ 2: GIẤU TIN TRONG ẢNH (LSB STEGANOGRAPHY) ---
    else:
        st.subheader("🖼️ Image Steganography Lab (LSB Pixel Embedding)")
        st.markdown(
            "Embed encrypted payloads directly into the Least Significant Bits (LSB) of RGB pixels. "
            "**Tip:** Always send the output PNG as a **File/Document** so chat apps don't compress the pixels."
        )

        img_mode = st.radio(
            "Select Operation:",
            ["Hide Secret in Image", "Extract Secret from Image"],
            horizontal=True
        )

        if img_mode == "Hide Secret in Image":
            up_img = st.file_uploader("Upload Carrier Image (PNG/JPG):", type=["png", "jpg", "jpeg"])
            secret_img_msg = st.text_input("Enter secret message to embed inside image:")

            use_img_expire = st.checkbox("🔥 Enable Self-Destruct Timer for this Image")
            img_mins = 20
            if use_img_expire:
                img_mins = st.number_input("Expire if not extracted within (Minutes):", min_value=1, max_value=10080, value=20)

            if st.button("🖼️ Embed Cipher & Generate PNG", type="primary"):
                if up_img and secret_img_msg:
                    try:
                        img_obj = Image.open(up_img)
                        mode_code = "EXPIRE" if use_img_expire else "NONE"
                        target_ts = int(time.time()) + (img_mins * 60) if use_img_expire else 0

                        cypher_for_img = encrypt_core(
                            secret_img_msg, group_key, group_config["reverse_rule"], mode_code, target_ts
                        )
                        stego_img = encode_image_lsb(img_obj, cypher_for_img)

                        buf = io.BytesIO()
                        stego_img.save(buf, format="PNG")
                        st.success("✅ Secret embedded into image pixels! Download your lossless PNG below:")
                        st.download_button(
                            label="⬇️ Download Stego Image (secret_image.png)",
                            data=buf.getvalue(),
                            file_name="secret_image.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please upload an image and enter a secret message first!")
        else:
            stego_up = st.file_uploader("Upload Stego PNG Image to decode:", type=["png"])
            if st.button("🔍 Extract & Decode Hidden Message", type="primary"):
                if stego_up:
                    try:
                        img_obj = Image.open(stego_up)
                        extracted_cypher = decode_image_lsb(img_obj)
                        ok, result = decrypt_core(extracted_cypher, group_key, group_config["reverse_rule"])
                        if ok:
                            st.success("🎉 Hidden Message Extracted from Pixels:")
                            st.info(result)
                        else:
                            st.error(result)
                    except Exception as e:
                        st.error(f"No valid hidden message found: {e}")

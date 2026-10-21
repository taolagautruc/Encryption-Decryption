import streamlit as st
from PIL import Image
from core.cipher_engine import BASE_CHARS, encrypt_core
from core.camouflage import encode_english_camouflage, inspect_camouflage_structure
from core.steganography import encode_image_lsb, inspect_pixel_lsb


def render_academy(group_config: dict, group_key: list):
    """Giao diện Học viện Mật mã Trực quan (Interactive Cryptography Visualizer)."""
    st.subheader("📚 Security Academy & Algorithm X-Ray")
    st.caption(
        "Interactive visualizers showing how your messages are transformed into bits, pixels, and linguistic matrices."
    )

    tab1, tab2, tab3 = st.tabs([
        "🔬 1. LSB Pixel X-Ray",
        "🎭 2. Camouflage Matrix Inspector",
        "⚙️ 3. Multi-Layer Cipher Blueprint"
    ])

    # --- TAB 1: SOI BIT NHỊ PHÂN ĐIỂM ẢNH ---
    with tab1:
        st.markdown("#### 🔬 Least Significant Bit (LSB) Steganography Inspector")
        st.write(
            "When hiding a message inside an image, our engine modifies only the **8th bit (Least Significant Bit)** "
            "of each Red, Green, and Blue channel. A change of `±1` in RGB value (0–255) is completely invisible to the human eye."
        )

        sample_secret = st.text_input("Enter a short test string to embed into pixels:", value="OK")
        up_test_img = st.file_uploader(
            "Optional: Upload an image to inspect (or leave blank to use a generated test swatch):",
            type=["png", "jpg", "jpeg"]
        )

        if up_test_img:
            orig_img = Image.open(up_test_img).convert("RGB")
        else:
            orig_img = Image.new("RGB", (60, 60), color=(120, 180, 210))

        stego_img = encode_image_lsb(orig_img, sample_secret)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Original Pixels (Before Embedding)**")
            st.table(inspect_pixel_lsb(orig_img, num_pixels=4))
        with c2:
            st.markdown("**Modified Pixels (After Embedding `[LSB]`)**")
            st.table(inspect_pixel_lsb(stego_img, num_pixels=4))

    # --- TAB 2: PHÂN TÍCH MA TRẬN NGỤY TRANG TIẾNG ANH ---
    with tab2:
        st.markdown("#### 🎭 Linguistic Steganography (4-Bit Nibble Mapping)")
        st.write(
            "Instead of outputting suspicious random symbols, the Camouflage Engine adds a **Random Salt (0–255)** "
            "and splits each character byte into two **4-bit nibbles** (`0000` to `1111`), mapping them to a 16×16 English vocabulary matrix."
        )

        demo_word = st.text_input("Type a short word to inspect its English transformation:", value="Hi")
        if demo_word:
            demo_cypher = encrypt_core(demo_word, group_key, group_config.get("reverse_rule", False), "NONE", 0) if group_config.get("secret_seed") else demo_word
            camo_sentence = encode_english_camouflage(demo_cypher)
            st.success("Generated Disguised Output:")
            st.code(camo_sentence, language=None)

            st.markdown("**Byte-to-Word Breakdown (First 6 Tokens):**")
            breakdown = inspect_camouflage_structure(camo_sentence)
            st.table(breakdown)

    # --- TAB 3: KIẾN TRÚC BẢO MẬT ĐA TẦNG ---
    with tab3:
        st.markdown("#### ⚙️ How Our 5-Layer Encryption Pipeline Works")
        st.markdown(
            """
            1. **Layer 1 — Dynamic Seed & Symbol Vault:** Combines your text passphrase with an ordered sequence selected from **1,200+ Unicode symbols** to seed a deterministic Pseudo-Random Number Generator (`PRNG`).
            2. **Layer 2 — Poly-Alphabetic Permutation:** Shuffles all **229 base characters** (English, Vietnamese diacritics, digits, and punctuation) into a unique bijection table.
            3. **Layer 3 — Modular Caesar Shift & Custom Swaps:** Rotates the shuffled key ring by $N$ positions and applies manual user-defined character swaps.
            4. **Layer 4 — Universal UTC Time-Control Header:** Embeds an encrypted Unix Epoch timestamp (`TMODE:EXPIRE` or `TMODE:WAIT`) that works identically across all global timezones without relying on local system clocks.
            5. **Layer 5 — Structural Reversal & Stego Wrapping:** Optionally flips the ciphertext vector before wrapping it into English prose or PNG pixel bits.
            """
        )

        if group_config.get("secret_seed"):
            st.markdown("##### 🔍 Your Current Active Substitution Sample (First 12 Characters)")
            sample_chars = BASE_CHARS[10:22]
            mapping_preview = {
                "Original Char": sample_chars,
                "Mapped Cipher Char": [group_key[BASE_CHARS.index(c)] for c in sample_chars]
            }
            st.dataframe(mapping_preview, use_container_width=True)

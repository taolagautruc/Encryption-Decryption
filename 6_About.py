import streamlit as st

def render_about():
    st.subheader("🛠️ Utilities & Developer Profile")
    st.caption("Export group configurations, inspect system specs, and view author portfolio.")

    tab1, tab2 = st.tabs(["📦 Group Config Sharing", "👨‍💻 Author & Project Info"])

    with tab1:
        st.markdown("#### 📋 Export / Import Group Cipher Rules")
        st.write(
            "To share your custom rule set with teammates without sending the secret passphrase, "
            "you can export the configuration parameters."
        )
        st.text_area("Copy this config string for your team:", value="--- ULTIMATE CIPHER GROUP CONFIG ---", height=130)

    with tab2:
        st.markdown("#### 🎓 Developer Portfolio")
        st.markdown(
            """
            - **Author:** Student at Faculty of Information Technology, University of Science, VNU-HCM (HCMUS).
            - **Project:** Ultimate Secret Messenger & Multi-Layer Cryptography Suite.
            - **Tech Stack:** Python, Streamlit, Pillow (PIL), Cryptographic Permutation & LSB Steganography.
            """
        )
        st.info("💡 *“Security is not a product, but a process.”* — Bruce Schneier")

render_about()

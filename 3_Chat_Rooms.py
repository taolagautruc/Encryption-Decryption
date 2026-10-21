from datetime import datetime, timezone
import streamlit as st
from core.chat_storage import (
    create_or_join_room,
    add_message,
    get_room_messages,
    clear_room_history
)
from core.cipher_engine import encrypt_core, decrypt_core
from core.camouflage import encode_english_camouflage, decode_english_camouflage


def render_chat_rooms(group_config: dict, group_key: list):
    """Giao diện Phòng Chat Bí Mật có mật khẩu bảo vệ và lưu trữ lịch sử."""
    st.subheader("💬 Persistent Secret Chat Rooms")
    st.caption(
        "Password-protected rooms • Persistent history even after everyone leaves • "
        "Mix plain text & encrypted messages • 1-Click individual or full-chat decryption"
    )

    # Khởi tạo trạng thái đăng nhập phòng trong phiên làm việc
    if "active_room" not in st.session_state:
        st.session_state.active_room = None
    if "chat_nickname" not in st.session_state:
        st.session_state.chat_nickname = "Agent_01"
    if "decrypted_msg_ids" not in st.session_state:
        st.session_state.decrypted_msg_ids = set()
    if "decrypt_all_mode" not in st.session_state:
        st.session_state.decrypt_all_mode = False

    # --- KHU VỰC 1: ĐĂNG NHẬP / TẠO PHÒNG CHAT ---
    if not st.session_state.active_room:
        with st.container(border=True):
            st.markdown("#### 🔑 Enter or Create a Secret Room")
            st.info("If the Room ID does not exist yet, the system will automatically create it with your password.")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                room_id_input = st.text_input("Room ID:", placeholder="e.g. Room_Alpha")
            with c2:
                room_pass_input = st.text_input("Room Password:", type="password", placeholder="Room access password")
            with c3:
                nickname_input = st.text_input("Your Display Name:", value=st.session_state.chat_nickname)

            if st.button("🚪 Join / Create Room", type="primary"):
                ok, msg = create_or_join_room(room_id_input, room_pass_input)
                if ok:
                    st.session_state.active_room = room_id_input.strip()
                    st.session_state.chat_nickname = nickname_input.strip() or "Anonymous"
                    st.session_state.decrypted_msg_ids = set()
                    st.session_state.decrypt_all_mode = False
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        return

    # --- KHU VỰC 2: BÊN TRONG PHÒNG CHAT ---
    current_room = st.session_state.active_room
    top_c1, top_c2, top_c3, top_c4 = st.columns([2, 1, 1, 1])
    with top_c1:
        st.markdown(f"### 🟢 Room: `{current_room}` (User: **{st.session_state.chat_nickname}**)")
    with top_c2:
        # Nút bật/tắt giải mã toàn bộ cuộc trò chuyện
        btn_label = "🙈 Hide Decrypted" if st.session_state.decrypt_all_mode else "🔓 Decrypt All Chat"
        if st.button(btn_label, use_container_width=True):
            st.session_state.decrypt_all_mode = not st.session_state.decrypt_all_mode
            st.rerun()
    with top_c3:
        if st.button("🧹 Clear History", use_container_width=True):
            clear_room_history(current_room)
            st.session_state.decrypted_msg_ids = set()
            st.rerun()
    with top_c4:
        if st.button("🚪 Leave Room", use_container_width=True):
            st.session_state.active_room = None
            st.rerun()

    st.divider()

    # Hiển thị lịch sử tin nhắn đã lưu trữ
    messages = get_room_messages(current_room)
    if not messages:
        st.info("📭 No messages in this room yet. Start the conversation below! (History is saved automatically).")
    else:
        for m in messages:
            msg_id = m["id"]
            sender = m["sender"]
            ts_str = datetime.fromtimestamp(m["timestamp"], timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            is_enc = m.get("is_encrypted", False)
            enc_type = m.get("enc_type", "NONE")
            content = m["content"]

            with st.container(border=True):
                header_col, action_col = st.columns([4, 1])
                with header_col:
                    badge = "📝 Plain Text"
                    if is_enc:
                        badge = "🎭 English Camouflage" if enc_type == "CAMO" else "🔒 Encrypted Cipher"
                    st.markdown(f"**👤 {sender}** • `{ts_str}` • *{badge}*")

                with action_col:
                    if is_enc:
                        is_shown = (msg_id in st.session_state.decrypted_msg_ids) or st.session_state.decrypt_all_mode
                        toggle_txt = "🔒 Hide" if is_shown else "🔍 Decode"
                        if st.button(toggle_txt, key=f"btn_{msg_id}", use_container_width=True):
                            if msg_id in st.session_state.decrypted_msg_ids:
                                st.session_state.decrypted_msg_ids.remove(msg_id)
                            else:
                                st.session_state.decrypted_msg_ids.add(msg_id)
                            st.rerun()

                # Nội dung hiển thị
                if not is_enc:
                    st.write(content)
                else:
                    st.code(content, language=None)
                    should_decode = (msg_id in st.session_state.decrypted_msg_ids) or st.session_state.decrypt_all_mode
                    if should_decode:
                        if not group_config.get("secret_seed"):
                            st.warning("⚠️ Please enter your 'Group Secret Passphrase' in the top bar to decode this message!")
                        else:
                            try:
                                raw_cypher = decode_english_camouflage(content) if enc_type == "CAMO" else content
                                ok, decoded_text = decrypt_core(raw_cypher, group_key, group_config["reverse_rule"])
                                if ok:
                                    st.success(f"🔓 **Decoded:** {decoded_text}")
                                else:
                                    st.error(decoded_text)
                            except Exception as e:
                                st.error(f"❌ Failed to decode with current Group Key: {e}")

    st.divider()

    # --- KHU VỰC 3: KHUNG SOẠN VÀ GỬI TIN NHẮN MỚI ---
    st.markdown("#### ✉️ Send a Message to this Room")
    send_mode = st.radio(
        "Choose your messaging mode:",
        [
            "📝 Normal Chat (No Encryption)",
            "🔒 Encrypt with Group Cipher Rule",
            "🎭 Disguise as English Camouflage"
        ],
        horizontal=True
    )

    new_msg = st.text_area("Type your message:", height=80, placeholder="Write something to the room...")
    if st.button("📤 Send Message", type="primary"):
        if not new_msg.strip():
            st.warning("Please enter a message before sending!")
        else:
            if "Normal Chat" in send_mode:
                add_message(current_room, st.session_state.chat_nickname, new_msg.strip(), is_encrypted=False, enc_type="NONE")
                st.rerun()
            else:
                if not group_config.get("secret_seed"):
                    st.error("❌ You must set a 'Group Secret Passphrase' in the top configuration bar to send encrypted messages!")
                else:
                    cypher_out = encrypt_core(new_msg.strip(), group_key, group_config["reverse_rule"], "NONE", 0)
                    if "Camouflage" in send_mode:
                        camo_out = encode_english_camouflage(cypher_out)
                        add_message(current_room, st.session_state.chat_nickname, camo_out, is_encrypted=True, enc_type="CAMO")
                    else:
                        add_message(current_room, st.session_state.chat_nickname, cypher_out, is_encrypted=True, enc_type="CIPHER")
                    st.rerun()

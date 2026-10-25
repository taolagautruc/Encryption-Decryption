import streamlit as st
import time
import base64
import io
from PIL import Image
from datetime import datetime, timezone

def inject_zalo_messenger_css():
    """CSS tạo giao diện Sảnh chờ và Bong bóng Chat (Chat Bubbles) giống Zalo / Messenger."""
    st.markdown("""
    <style>
        /* Khung đăng nhập phòng chat ở Màn hình 1 (Lobby) */
        .lobby-login-card {
            background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 100%);
            border: 1.5px solid #3b82f6;
            border-radius: 16px;
            padding: 24px 28px;
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
        }
        /* Thanh Header của phòng chat ở Màn hình 2 */
        .msg-room-header {
            background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%);
            border: 1px solid #334155;
            border-bottom: 2px solid #3b82f6;
            border-radius: 14px;
            padding: 12px 20px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        /* Bong bóng tin nhắn của BẠN (Nằm bên PHẢI, màu xanh Zalo/Messenger) */
        .bubble-me-wrap {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            margin-bottom: 10px;
        }
        .bubble-me {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: #ffffff;
            padding: 12px 16px;
            border-radius: 18px 18px 4px 18px;
            max-width: 78%;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
            word-wrap: break-word;
        }
        /* Bong bóng tin nhắn của NGƯỜI KHÁC (Nằm bên TRÁI, màu xám tối) */
        .bubble-other-wrap {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        .bubble-other {
            background: #1e293b;
            border: 1px solid #334155;
            color: #f8fafc;
            padding: 12px 16px;
            border-radius: 18px 18px 18px 4px;
            max-width: 78%;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            word-wrap: break-word;
        }
        .bubble-meta {
            font-size: 0.74rem;
            color: #94a3b8;
            margin-bottom: 4px;
            padding: 0 4px;
        }
        .bubble-cipher-box {
            font-family: 'Courier New', monospace;
            background: rgba(0, 0, 0, 0.28);
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 0.85rem;
            color: #cbd5e1;
            margin-top: 4px;
        }
        .bubble-plain-box {
            background: rgba(16, 185, 129, 0.18);
            border-left: 3px solid #34d399;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.96rem;
            font-weight: 600;
            color: #ecfdf5;
            margin-top: 6px;
        }
    </style>
    """, unsafe_allow_html=True)


def render_zalo_messenger_rooms(
    secret_seed: str,
    group_key: list,
    reverse_rule: bool,
    load_all_rooms_fn,
    save_all_rooms_fn,
    add_msg_fn,
    delete_single_message_fn,
    clear_room_history_fn,
    destroy_entire_room_fn,
    encrypt_core_fn,
    decrypt_core_fn,
    encode_camo_fn,
    decode_camo_fn,
    gen_carrier_fn,
    encode_lsb_fn,
    decode_lsb_fn
):
    inject_zalo_messenger_css()

    if not secret_seed:
        st.markdown("""
        <div class="hero-box" style="padding: 20px 28px; margin-bottom: 18px;">
            <div class="hero-badge">💬 ZERO-KNOWLEDGE MESSENGER</div>
            <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Encrypted Secret Messenger</h2>
            <p class="hero-sub">Enter your Group Secret Passphrase on the left Sidebar to unlock private Messenger rooms.</p>
        </div>
        """, unsafe_allow_html=True)
        st.warning("⚠️ **Passphrase Required:** Please enter your **Group Secret Passphrase** in the left Sidebar first!")
        return

    # Quản lý trạng thái chuyển màn hình: None = Màn hình Sảnh Chờ | Tên phòng = Màn hình Chat riêng biệt
    if "active_chat_room" not in st.session_state:
        st.session_state.active_chat_room = None
    if "chat_agent_name" not in st.session_state:
        st.session_state.chat_agent_name = st.session_state.get("ctf_user") or "taolagautruc"
    if "unlocked_msgs" not in st.session_state:
        st.session_state.unlocked_msgs = {}

    rooms = load_all_rooms_fn()

    # ==========================================================================
    # MÀN HÌNH 1: CỔNG SẢNH CHỜ (NHẬP ROOM ID + ẤN ENTER LÀ VÀO THẲNG KHUNG CHAT)
    # ==========================================================================
    if st.session_state.active_chat_room is None:
        st.markdown("""
        <div class="hero-box" style="padding: 22px 30px; margin-bottom: 20px;">
            <div class="hero-badge">💬 INSTANT SECRET MESSENGER • END-TO-END ENCRYPTED ROOMS</div>
            <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Secret Messenger Lobby</h2>
            <p class="hero-sub">Type any Room ID and press <b>Enter</b> to launch a dedicated, distraction-free encrypted chat window (just like Zalo, Telegram, or Messenger)!</p>
        </div>
        """, unsafe_allow_html=True)

        lob_col1, lob_col2 = st.columns([1.4, 1.6])

        with lob_col1:
            st.markdown("""
            <div class="lobby-login-card">
                <h4 style="color:#f8fafc; margin-top:0;">🚀 Quick Enter / Create Room</h4>
                <p style="color:#94a3b8; font-size:0.88rem;">Enter a Room ID below and press <b>Enter</b>. If the room doesn't exist yet, it will be created automatically!</p>
            </div>
            """, unsafe_allow_html=True)
            st.write("")

            with st.form("quick_enter_room_form", clear_on_submit=False):
                u_codename = st.text_input("🕵️ Your Messenger Display Name:", value=st.session_state.chat_agent_name)
                r_id_input = st.text_input("🔑 Enter Room ID (Press Enter to Join):", placeholder="e.g. HCMUS-VIP or 8888")
                submit_join = st.form_submit_button("💬 Enter Chat Room Now (Press Enter)", type="primary", use_container_width=True)

                if submit_join:
                    clean_r = r_id_input.strip()
                    clean_u = u_codename.strip() or "Agent-007"
                    if not clean_r:
                        st.error("Please enter a Room ID!")
                    else:
                        st.session_state.chat_agent_name = clean_u
                        if clean_r not in rooms:
                            rooms[clean_r] = {
                                "messages": [],
                                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                            }
                            save_all_rooms_fn(rooms)
                        st.session_state.active_chat_room = clean_r
                        st.rerun()

        with lob_col2:
            st.markdown("##### 📂 Active Encrypted Channels (1-Click Join)")
            if not rooms:
                st.info("📭 No active rooms on the server yet. Type a Room ID on the left and press Enter to open the first room!")
            else:
                for r_key, r_val in rooms.items():
                    m_cnt = len(r_val.get("messages", []))
                    c_time = r_val.get("created_at", "UTC")
                    with st.container(border=True):
                        rc1, rc2 = st.columns([2.5, 1.1])
                        with rc1:
                            st.markdown(f"**📡 Room ID: `{r_key}`**")
                            st.caption(f"💬 `{m_cnt}` messages • Created: {c_time}")
                        with rc2:
                            if st.button("💬 Open Chat", key=f"open_rm_{r_key}", type="primary", use_container_width=True):
                                st.session_state.active_chat_room = r_key
                                st.rerun()

    # ==========================================================================
    # MÀN HÌNH 2: KHÔNG GIAN CHAT CHUYÊN BIỆT (GIỐNG ZALO / MESSENGER)
    # ==========================================================================
    else:
        curr_room = st.session_state.active_chat_room
        agent_name = st.session_state.chat_agent_name

        if curr_room not in rooms:
            st.session_state.active_chat_room = None
            st.rerun()

        msgs = rooms[curr_room].get("messages", [])

        # --- 1. THANH HEADER CỐ ĐỊNH TRÊN ĐỈNH PHÒNG CHAT ---
        h_col1, h_col2, h_col3, h_col4 = st.columns([1.1, 2.5, 1.3, 1.1])
        with h_col1:
            if st.button("⬅️ Leave Room", use_container_width=True, help="Return to Room Lobby"):
                st.session_state.active_chat_room = None
                st.rerun()
        with h_col2:
            st.markdown(
                f"<div style='padding-top:4px;'>"
                f"<span style='font-size:1.2rem; font-weight:800; color:#f8fafc;'>📡 {curr_room}</span> &nbsp;"
                f"<span style='background:rgba(16,185,129,0.2); color:#34d399; padding:2px 8px; border-radius:99px; font-size:0.75rem; font-weight:700;'>● E2EE Active ({len(msgs)} msgs)</span>"
                f"<div style='font-size:0.78rem; color:#94a3b8;'>Chatting as: <b style='color:#60a5fa;'>{agent_name}</b></div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with h_col3:
            auto_decrypt = st.toggle("🔓 Auto-Decrypt View", value=True, help="Automatically show decrypted plaintext inside chat bubbles like Zalo/Messenger")
        with h_col4:
            with st.popover("⚙️ Room Menu", use_container_width=True):
                st.markdown(f"**Manage `{curr_room}`**")
                if st.button("🔄 Refresh Messages", use_container_width=True):
                    st.rerun()
                if st.button("🧹 Clear All Messages", use_container_width=True):
                    clear_room_history_fn(curr_room)
                    st.rerun()
                if st.button("💥 Destroy Room", type="primary", use_container_width=True):
                    destroy_entire_room_fn(curr_room)
                    st.session_state.active_chat_room = None
                    st.rerun()

        # --- 2. KHUNG CUỘN BONG BÓNG TIN NHẮN (SCROLLABLE MESSENGER VIEWPORT) ---
        chat_viewport = st.container(height=450, border=True)
        with chat_viewport:
            if not msgs:
                st.markdown(
                    "<div style='text-align:center; color:#64748b; padding: 120px 20px;'>"
                    "<h3>🔒 End-to-End Encrypted Conversation</h3>"
                    "<p>No messages in <b>" + curr_room + "</b> yet. Type a message in the bar below and press <b>Enter</b> to start chatting!</p>"
                    "</div>",
                    unsafe_allow_html=True
                )
            else:
                for idx, m in enumerate(msgs):
                    m_id = m.get("id", f"m_{idx}")
                    m_sender = m.get("sender", "Agent")
                    m_type = m.get("type", "TEXT")
                    m_time = m.get("timestamp", "")[-12:]  # Lấy giờ:phút:giây UTC gọn gàng
                    m_cipher = m.get("ciphertext", "")
                    m_img_b64 = m.get("image_b64", "")
                    is_me = (m_sender.strip().lower() == agent_name.strip().lower())

                    type_badge = "🔐 Cipher" if m_type == "TEXT" else ("🎭 Camouflage" if m_type == "CAMO" else "🖼️ Stego PNG")

                    # Giải mã tự động nếu bật Auto-Decrypt hoặc nếu người dùng đã bấm nút dịch cho tin nhắn này
                    show_plain = auto_decrypt or st.session_state.unlocked_msgs.get(m_id, False)
                    dec_ok, dec_text = False, ""
                    if show_plain:
                        if m_type == "STEGO_IMG" and m_img_b64:
                            try:
                                raw_img = Image.open(io.BytesIO(base64.b64decode(m_img_b64))).convert("RGB")
                                ok_e, ext_c = decode_lsb_fn(raw_img)
                                if ok_e:
                                    dec_ok, dec_text = decrypt_core_fn(ext_c, group_key, reverse_rule)
                                else:
                                    dec_text = ext_c
                            except Exception:
                                dec_text = "❌ Image error"
                        elif m_type == "CAMO":
                            ok_c, ext_c = decode_camo_fn(m_cipher)
                            if ok_c:
                                dec_ok, dec_text = decrypt_core_fn(ext_c, group_key, reverse_rule)
                            else:
                                dec_text = ext_c
                        else:
                            dec_ok, dec_text = decrypt_core_fn(m_cipher, group_key, reverse_rule)

                    # Giao diện Bong bóng Chat chia cột Trái (Người khác) / Phải (Bạn)
                    if is_me:
                        _, b_col = st.columns([1.5, 3.5])
                        align_cls = "bubble-me-wrap"
                        box_cls = "bubble-me"
                        sender_label = f"You ({m_sender})"
                    else:
                        b_col, _ = st.columns([3.5, 1.5])
                        align_cls = "bubble-other-wrap"
                        box_cls = "bubble-other"
                        sender_label = f"🕵️ {m_sender}"

                    with b_col:
                        plain_html = ""
                        if show_plain:
                            if dec_ok:
                                plain_html = f"<div class='bubble-plain-box'>🔓 {dec_text}</div>"
                            else:
                                plain_html = f"<div class='bubble-plain-box' style='border-left-color:#ef4444; background:rgba(239,68,68,0.15);'>{dec_text}</div>"

                        cipher_preview = m_cipher if len(m_cipher) <= 90 else m_cipher[:90] + "..."
                        st.markdown(f"""
                        <div class="{align_cls}">
                            <div class="bubble-meta"><b>{sender_label}</b> • {m_time} • <code>{type_badge}</code></div>
                            <div class="{box_cls}">
                                <div class="bubble-cipher-box">{cipher_preview}</div>
                                {plain_html}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if m_type == "STEGO_IMG" and m_img_b64:
                            try:
                                st.image(base64.b64decode(m_img_b64), width=220)
                            except Exception:
                                pass

                        # Nút bấm nhỏ gọn ngay dưới mỗi bong bóng chat
                        act1, act2, _ = st.columns([1.2, 0.8, 2.5])
                        with act1:
                            if not auto_decrypt:
                                btn_lbl = "🙈 Hide" if st.session_state.unlocked_msgs.get(m_id) else "🔓 Decode"
                                if st.button(btn_lbl, key=f"tog_{curr_room}_{m_id}"):
                                    st.session_state.unlocked_msgs[m_id] = not st.session_state.unlocked_msgs.get(m_id, False)
                                    st.rerun()
                        with act2:
                            if st.button("🗑️", key=f"del_{curr_room}_{idx}", help="Delete this message"):
                                delete_single_message_fn(curr_room, idx)
                                st.rerun()

        # --- 3. THANH CÔNG CỤ ĐÍNH KÈM & THANH NHẬP TIN NHẮN ẤN ENTER GỬI NGAY (GIỐNG ZALO/MESSENGER) ---
        opt_col1, opt_col2, opt_col3 = st.columns([1.5, 1.5, 1.5])
        with opt_col1:
            send_format = st.selectbox(
                "📤 Message Mode:",
                ["🔐 Standard Ciphertext", "🎭 Disguise as English Prose (Camouflage)"],
                label_visibility="collapsed"
            )
        with opt_col2:
            timer_choice = st.selectbox(
                "⏳ Timer:",
                ["⏱️ No Time Limit", "🔥 Self-Destruct in 5 mins", "🔥 Self-Destruct in 15 mins", "🔥 Self-Destruct in 60 mins", "⏳ Time-Capsule (Wait 5 mins)"],
                label_visibility="collapsed"
            )
        with opt_col3:
            with st.popover("🖼️ Send Stego PNG Image", use_container_width=True):
                st.markdown("##### 🖼️ Hide Secret in PNG & Send to Chat")
                stego_secret_txt = st.text_input("Secret text inside image:", key="pop_stego_txt")
                up_custom_img = st.file_uploader("Optional Image (or auto-generate):", type=["png", "jpg", "jpeg"], key="pop_stego_up")
                if st.button("📤 Embed & Send Image", type="primary", use_container_width=True):
                    if stego_secret_txt.strip():
                        c_img = Image.open(up_custom_img).convert("RGB") if up_custom_img else gen_carrier_fn()
                        enc_p = encrypt_core_fn(stego_secret_txt.strip(), group_key, reverse_rule, "NONE", 0)
                        stego_img_out = encode_lsb_fn(c_img, enc_p)
                        buf = io.BytesIO()
                        stego_img_out.save(buf, format="PNG")
                        b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
                        add_msg_fn(curr_room, agent_name, "[LSB Stego PNG Image]", msg_type="STEGO_IMG", image_b64=b64_img)
                        st.rerun()

        # Thanh gõ chữ ấn Enter gửi ngay của Streamlit
        prompt_msg = st.chat_input(f"💬 Write an encrypted message to #{curr_room} and press Enter...")
        if prompt_msg and prompt_msg.strip():
            t_mode_code = "NONE"
            target_epoch = 0
            if "Self-Destruct" in timer_choice:
                t_mode_code = "EXPIRE"
                mins_val = 5 if "5" in timer_choice else (15 if "15" in timer_choice else 60)
                target_epoch = int(time.time()) + (mins_val * 60)
            elif "Time-Capsule" in timer_choice:
                t_mode_code = "WAIT"
                target_epoch = int(time.time()) + 300

            raw_cipher = encrypt_core_fn(prompt_msg.strip(), group_key, reverse_rule, t_mode_code, target_epoch)
            if "Camouflage" in send_format:
                camo_payload = encode_camo_fn(raw_cipher)
                add_msg_fn(curr_room, agent_name, camo_payload, msg_type="CAMO")
            else:
                add_msg_fn(curr_room, agent_name, raw_cipher, msg_type="TEXT")
            st.rerun()

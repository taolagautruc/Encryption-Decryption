import streamlit as st
import time
import base64
import hashlib
import random
import io
from PIL import Image
from datetime import datetime, timezone


def inject_zalo_messenger_css():
    """CSS tạo giao diện Sảnh chờ và Bong bóng Chat (Chat Bubbles) chuẩn Zalo / Messenger."""
    st.markdown("""
<style>
.lobby-login-card {
    background: linear-gradient(145deg, #0f172a 0%, #1e1b4b 100%);
    border: 1.5px solid #3b82f6;
    border-radius: 16px;
    padding: 22px 26px;
    box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
}
.bubble-me-wrap {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    margin-bottom: 4px;
}
.bubble-me {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: #ffffff;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    max-width: 92%;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    word-wrap: break-word;
}
.bubble-other-wrap {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 4px;
}
.bubble-other {
    background: #1e293b;
    border: 1px solid #334155;
    color: #f8fafc;
    padding: 12px 16px;
    border-radius: 18px 18px 18px 4px;
    max-width: 92%;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    word-wrap: break-word;
}
.bubble-meta {
    font-size: 0.76rem;
    color: #94a3b8;
    margin-bottom: 4px;
    padding: 0 4px;
}
.bubble-cipher-box {
    font-family: 'Courier New', monospace;
    background: rgba(0, 0, 0, 0.32);
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 0.86rem;
    color: #e2e8f0;
    margin-top: 2px;
    word-break: break-all;
}
.bubble-plain-box {
    background: rgba(16, 185, 129, 0.22);
    border-left: 4px solid #34d399;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.96rem;
    font-weight: 700;
    color: #ecfdf5;
    margin-top: 8px;
}
.bubble-error-box {
    background: rgba(239, 68, 68, 0.2);
    border-left: 4px solid #ef4444;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 0.88rem;
    font-weight: 600;
    color: #fecaca;
    margin-top: 8px;
}
.owner-badge {
    background: rgba(245, 158, 11, 0.2);
    border: 1px solid #f59e0b;
    color: #fde047;
    padding: 2px 10px;
    border-radius: 99px;
    font-size: 0.76rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


def append_rich_message(
    load_all_rooms_fn,
    save_all_rooms_fn,
    room_name: str,
    sender: str,
    ciphertext: str,
    msg_type: str = "TEXT",
    image_b64: str = "",
    private_pass_hash: str = ""
):
    """Lưu tin nhắn kèm lớp khóa mật khẩu riêng (private_pass_hash) của người gửi."""
    rooms = load_all_rooms_fn()
    if room_name not in rooms:
        rooms[room_name] = {
            "owner": sender,
            "messages": [],
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        }
    msg_id = f"msg_{int(time.time()*1000)}_{random.randint(100,999)}"
    rooms[room_name]["messages"].append({
        "id": msg_id,
        "sender": sender,
        "type": msg_type,
        "ciphertext": ciphertext,
        "image_b64": image_b64,
        "private_pass_hash": private_pass_hash,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    })
    save_all_rooms_fn(rooms)


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

    if "active_chat_room" not in st.session_state:
        st.session_state.active_chat_room = None
    if "chat_agent_name" not in st.session_state:
        st.session_state.chat_agent_name = st.session_state.get("ctf_user") or "taolagautruc"
    if "unlocked_msgs" not in st.session_state:
        st.session_state.unlocked_msgs = {}
    if "prompting_pass_msg" not in st.session_state:
        st.session_state.prompting_pass_msg = None

    rooms = load_all_rooms_fn()

    # ==========================================================================
    # MÀN HÌNH 1: CỔNG SẢNH CHỜ (NHẬP ROOM ID + ẤN ENTER LÀ VÀO THẲNG PHÒNG CHAT)
    # ==========================================================================
    if st.session_state.active_chat_room is None:
        st.markdown("""
<div class="hero-box" style="padding: 22px 30px; margin-bottom: 20px;">
    <div class="hero-badge">💬 INSTANT SECRET MESSENGER • OWNER CONTROLS • 2ND-LAYER MESSAGE LOCK</div>
    <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Secret Messenger Lobby</h2>
    <p class="hero-sub">Type a Room ID and press <b>Enter</b> to open a dedicated chat screen. If you create a new room, you become the <b>👑 Room Owner</b> (able to wipe/destroy the room and bypass private message locks)!</p>
</div>
""", unsafe_allow_html=True)

        lob_col1, lob_col2 = st.columns([1.45, 1.55])

        with lob_col1:
            st.markdown("""
<div class="lobby-login-card">
    <h4 style="color:#f8fafc; margin-top:0;">🚀 Quick Enter / Create Room</h4>
    <p style="color:#94a3b8; font-size:0.88rem; margin-bottom:0;">Enter your Display Name and Room ID, then press <b>Enter</b>. Creating a new Room ID makes you its <b>👑 Room Owner</b>!</p>
</div>
""", unsafe_allow_html=True)
            st.write("")

            with st.form("quick_enter_room_form", clear_on_submit=False):
                u_codename = st.text_input("🕵️ Your Messenger Display Name:", value=st.session_state.chat_agent_name)
                r_id_input = st.text_input("🔑 Enter Room ID (Press Enter to Join/Create):", placeholder="e.g. 3001 or HCMUS-VIP")
                r_pin_input = st.text_input("👑 Room Owner Master PIN (Optional — for creating/claiming ownership):", type="password", placeholder="Set or enter 4+ digit Owner PIN")
                submit_join = st.form_submit_button("💬 Enter Chat Room Now (Press Enter)", type="primary", use_container_width=True)

                if submit_join:
                    clean_r = r_id_input.strip()
                    clean_u = u_codename.strip() or "taolagautruc"
                    clean_pin = r_pin_input.strip()
                    if not clean_r:
                        st.error("Please enter a Room ID!")
                    else:
                        st.session_state.chat_agent_name = clean_u
                        if clean_r not in rooms:
                            rooms[clean_r] = {
                                "owner": clean_u,
                                "owner_pin_hash": hashlib.sha256(clean_pin.encode("utf-8")).hexdigest() if clean_pin else "",
                                "messages": [],
                                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                            }
                            save_all_rooms_fn(rooms)
                        else:
                            # Nếu phòng cũ chưa có trường owner thì gán cho người tạo đầu tiên
                            if "owner" not in rooms[clean_r]:
                                rooms[clean_r]["owner"] = clean_u
                                save_all_rooms_fn(rooms)
                            elif clean_pin and rooms[clean_r].get("owner_pin_hash") == hashlib.sha256(clean_pin.encode("utf-8")).hexdigest():
                                st.session_state[f"owner_verified_{clean_r}"] = True
                        st.session_state.active_chat_room = clean_r
                        st.rerun()

        with lob_col2:
            st.markdown("##### 📂 Active Encrypted Channels (1-Click Join)")
            if not rooms:
                st.info("📭 No active rooms yet. Type a Room ID on the left and press Enter to create the first room!")
            else:
                for r_key, r_val in rooms.items():
                    m_cnt = len(r_val.get("messages", []))
                    r_owner = r_val.get("owner", "taolagautruc")
                    c_time = r_val.get("created_at", "UTC")
                    with st.container(border=True):
                        rc1, rc2 = st.columns([2.5, 1.1])
                        with rc1:
                            st.markdown(f"**📡 Room ID: `{r_key}`** &nbsp; <span class='owner-badge'>👑 Owner: {r_owner}</span>", unsafe_allow_html=True)
                            st.caption(f"💬 `{m_cnt}` messages • Created: {c_time}")
                        with rc2:
                            if st.button("💬 Open Chat", key=f"open_rm_{r_key}", type="primary", use_container_width=True):
                                st.session_state.active_chat_room = r_key
                                st.rerun()

    # ==========================================================================
    # MÀN HÌNH 2: KHÔNG GIAN CHAT CHUYÊN BIỆT (CÓ NÚT CHỦ PHÒNG, CAMOUFLAGE & KHÓA MẬT MÃ RIÊNG)
    # ==========================================================================
    else:
        curr_room = st.session_state.active_chat_room
        agent_name = st.session_state.chat_agent_name

        if curr_room not in rooms:
            st.session_state.active_chat_room = None
            st.rerun()

        room_obj = rooms[curr_room]
        if "owner" not in room_obj:
            room_obj["owner"] = agent_name
            save_all_rooms_fn(rooms)

        room_owner = room_obj.get("owner", "taolagautruc")
        is_room_owner = (agent_name.strip().lower() == room_owner.strip().lower()) or st.session_state.get(f"owner_verified_{curr_room}", False)
        msgs = room_obj.get("messages", [])

        # --- 1. THANH HEADER TRÊN CÙNG + NÚT XÓA LỊCH SỬ / XÓA PHÒNG CỦA CHỦ PHÒNG ---
        top_c1, top_c2, top_c3, top_c4, top_c5 = st.columns([1.0, 2.2, 1.0, 1.15, 1.15])
        with top_c1:
            if st.button("⬅️ Leave Room", use_container_width=True):
                st.session_state.active_chat_room = None
                st.rerun()
        with top_c2:
            role_tag = "👑 Room Owner (Full Bypass)" if is_room_owner else f"👤 Member (Owner: {room_owner})"
            st.markdown(
                f"<div style='padding-top:2px;'>"
                f"<span style='font-size:1.18rem; font-weight:800; color:#f8fafc;'>📡 Room #{curr_room}</span> &nbsp;"
                f"<span class='owner-badge'>{role_tag}</span>"
                f"<div style='font-size:0.78rem; color:#94a3b8;'>Chatting as: <b style='color:#60a5fa;'>{agent_name}</b> • {len(msgs)} messages</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        with top_c3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        with top_c4:
            if st.button("🧹 Clear All Msgs", use_container_width=True, disabled=not is_room_owner, help="Only the Room Owner can wipe all messages"):
                clear_room_history_fn(curr_room)
                st.toast(f"🧹 Cleared all messages in #{curr_room}!", icon="🧹")
                st.rerun()
        with top_c5:
            if st.button("💥 Destroy Room", type="primary", use_container_width=True, disabled=not is_room_owner, help="Only the Room Owner can permanently delete this room"):
                destroy_entire_room_fn(curr_room)
                st.session_state.active_chat_room = None
                st.toast(f"💥 Room #{curr_room} destroyed!", icon="💥")
                st.rerun()

        if not is_room_owner:
            st.caption(f"🔒 *Note: Only the Room Owner (**`{room_owner}`**) can click **Clear All Msgs** or **Destroy Room**, and can decode private-locked messages without a password.*")

        # --- 2. KHUNG CUỘN BONG BÓNG TIN NHẮN (ĐÃ SỬA TRIỆT ĐỂ LỖI </div> VÀ CĂN LỀ NÚT DECODE) ---
        chat_viewport = st.container(height=410, border=True)
        with chat_viewport:
            if not msgs:
                st.markdown(
                    f"<div style='text-align:center; color:#64748b; padding: 100px 20px;'>"
                    f"<h3>🔒 End-to-End Encrypted Room #{curr_room}</h3>"
                    f"<p>No messages yet. Choose your encryption mode below (Standard, English Camouflage, or Stego PNG), set an optional Private Message Password, and start chatting!</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            else:
                for idx, m in enumerate(msgs):
                    m_id = m.get("id", f"m_{idx}")
                    m_sender = m.get("sender", "Agent")
                    m_type = m.get("type", "TEXT")
                    m_time = m.get("timestamp", "")[-12:]
                    m_cipher = m.get("ciphertext", "")
                    m_img_b64 = m.get("image_b64", "")
                    m_priv_hash = m.get("private_pass_hash", "")
                    has_priv_lock = bool(m_priv_hash)

                    is_me = (m_sender.strip().lower() == agent_name.strip().lower())

                    if m_type == "CAMO":
                        type_badge = "🎭 English Camouflage"
                    elif m_type == "STEGO_IMG":
                        type_badge = "🖼️ Stego PNG"
                    else:
                        type_badge = "🔐 Ciphertext"

                    lock_badge = " • 🔒 Private Pass Locked" if has_priv_lock else ""

                    is_unlocked = st.session_state.unlocked_msgs.get(m_id, False)
                    dec_ok, dec_text = False, ""

                    if is_unlocked:
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

                    # Chia cột Trái / Phải để cả Bong bóng VÀ nút Decode nằm chung 1 phía
                    if is_me:
                        _, b_col = st.columns([1.8, 3.2])
                        align_cls = "bubble-me-wrap"
                        box_cls = "bubble-me"
                        sender_label = f"You ({m_sender})"
                    else:
                        b_col, _ = st.columns([3.2, 1.8])
                        align_cls = "bubble-other-wrap"
                        box_cls = "bubble-other"
                        sender_label = f"🕵️ {m_sender}"

                    with b_col:
                        plain_html = ""
                        if is_unlocked:
                            owner_note = " <i>(👑 Room Owner Bypass)</i>" if (has_priv_lock and is_room_owner) else ""
                            if dec_ok:
                                plain_html = f"<div class='bubble-plain-box'>🔓 {dec_text}{owner_note}</div>"
                            else:
                                plain_html = f"<div class='bubble-error-box'>{dec_text}</div>"

                        # Viết HTML sát lề trái để Markdown không bao giờ biến </div> thành code block
                        bubble_html = (
                            f"<div class='{align_cls}'>"
                            f"<div class='bubble-meta'><b>{sender_label}</b> • {m_time} • <code>{type_badge}{lock_badge}</code></div>"
                            f"<div class='{box_cls}'>"
                            f"<div class='bubble-cipher-box'>{m_cipher}</div>"
                            f"{plain_html}"
                            f"</div>"
                            f"</div>"
                        )
                        st.markdown(bubble_html, unsafe_allow_html=True)

                        if m_type == "STEGO_IMG" and m_img_b64:
                            try:
                                st.image(base64.b64decode(m_img_b64), width=230)
                            except Exception:
                                pass

                        # Nút Decode và Delete nằm gọn ngay dưới đáy bong bóng
                        if is_me:
                            _, btn_c1, btn_c2 = st.columns([2.2, 1.1, 0.7])
                        else:
                            btn_c1, btn_c2, _ = st.columns([1.1, 0.7, 2.2])

                        with btn_c1:
                            if is_unlocked:
                                if st.button("🙈 Hide", key=f"hide_{curr_room}_{m_id}", use_container_width=True):
                                    st.session_state.unlocked_msgs[m_id] = False
                                    st.session_state.prompting_pass_msg = None
                                    st.rerun()
                            else:
                                dec_label = "👑 Decode" if (has_priv_lock and is_room_owner) else ("🔒 Decode" if has_priv_lock else "🔓 Decode")
                                if st.button(dec_label, key=f"dec_{curr_room}_{m_id}", use_container_width=True):
                                    # Nếu tin nhắn không cài pass riêng HOẶC người bấm chính là Chủ phòng -> Giải mã ngay!
                                    if (not has_priv_lock) or is_room_owner:
                                        st.session_state.unlocked_msgs[m_id] = True
                                        st.session_state.prompting_pass_msg = None
                                        st.rerun()
                                    else:
                                        # Nếu là thành viên thường -> Hiện ô bắt nhập mật mã riêng của tin nhắn đó
                                        st.session_state.prompting_pass_msg = m_id
                                        st.rerun()

                        with btn_c2:
                            if is_me or is_room_owner:
                                if st.button("🗑️", key=f"del_{curr_room}_{idx}", use_container_width=True, help="Delete this message"):
                                    delete_single_message_fn(curr_room, idx)
                                    st.rerun()

                        # Khung nhập mật mã riêng khi thành viên bấm Decode vào tin nhắn có khóa
                        if st.session_state.prompting_pass_msg == m_id and not is_unlocked:
                            with st.container(border=True):
                                p_in_c1, p_in_c2 = st.columns([2.2, 1])
                                with p_in_c1:
                                    entered_msg_pass = st.text_input(
                                        f"🔑 Enter `{m_sender}`'s Private Message Password:",
                                        type="password",
                                        key=f"mpass_in_{m_id}",
                                        placeholder="Type message password..."
                                    )
                                with p_in_c2:
                                    st.write("")
                                    if st.button("🔓 Unlock", key=f"unlk_btn_{m_id}", type="primary", use_container_width=True):
                                        if hashlib.sha256(entered_msg_pass.strip().encode("utf-8")).hexdigest() == m_priv_hash:
                                            st.session_state.unlocked_msgs[m_id] = True
                                            st.session_state.prompting_pass_msg = None
                                            st.rerun()
                                        else:
                                            st.error("❌ Wrong Private Message Password!")

        # --- 3. BẢNG CÀI ĐẶT CHẾ ĐỘ GỬI TIN (NGỤY TRANG TIẾNG ANH, MẬT MÃ RIÊNG TỪNG TIN, HẸN GIỜ & ẢNH LSB) ---
        with st.container(border=True):
            s_col1, s_col2, s_col3, s_col4 = st.columns([1.6, 1.5, 1.2, 1.1])
            with s_col1:
                send_format = st.selectbox(
                    "🎭 1. Encryption / Camouflage Mode:",
                    [
                        "🔐 Standard Ciphertext",
                        "🎭 English Camouflage (Disguise as English Prose)"
                    ],
                    key=f"s_fmt_{curr_room}"
                )
            with s_col2:
                msg_private_pass = st.text_input(
                    "🔒 2. Private Message Password (Optional):",
                    type="password",
                    placeholder="Leave blank or set password...",
                    help="If set, everyone EXCEPT the Room Owner must enter this password to decode your message!",
                    key=f"s_priv_{curr_room}"
                )
            with s_col3:
                timer_choice = st.selectbox(
                    "⏳ 3. UTC Time-Lock:",
                    [
                        "⏱️ No Time Limit",
                        "🔥 Self-Destruct (5m)",
                        "🔥 Self-Destruct (15m)",
                        "🔥 Self-Destruct (60m)",
                        "⏳ Time-Capsule (Wait 5m)"
                    ],
                    key=f"s_tmr_{curr_room}"
                )
            with s_col4:
                st.write("")
                with st.popover("🖼️ 4. Stego PNG", use_container_width=True):
                    st.markdown("##### 🖼️ Hide Secret in PNG & Send")
                    stego_secret_txt = st.text_input("Secret message:", key="pop_stego_txt")
                    stego_priv_pass = st.text_input("Optional Private Password:", type="password", key="pop_stego_pass")
                    up_custom_img = st.file_uploader("Upload Image (or auto-generate):", type=["png", "jpg", "jpeg"], key="pop_stego_up")
                    if st.button("📤 Embed & Send Stego PNG", type="primary", use_container_width=True):
                        if stego_secret_txt.strip():
                            c_img = Image.open(up_custom_img).convert("RGB") if up_custom_img else gen_carrier_fn()
                            enc_p = encrypt_core_fn(stego_secret_txt.strip(), group_key, reverse_rule, "NONE", 0)
                            stego_img_out = encode_lsb_fn(c_img, enc_p)
                            buf = io.BytesIO()
                            stego_img_out.save(buf, format="PNG")
                            b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")
                            p_hash = hashlib.sha256(stego_priv_pass.strip().encode("utf-8")).hexdigest() if stego_priv_pass.strip() else ""
                            append_rich_message(
                                load_all_rooms_fn, save_all_rooms_fn,
                                curr_room, agent_name, "[LSB Stego PNG Image]",
                                msg_type="STEGO_IMG", image_b64=b64_img, private_pass_hash=p_hash
                            )
                            st.rerun()

        # Thanh gõ tin nhắn ấn Enter gửi ngay
        mode_hint = "🎭 English Camouflage Mode Active" if "Camouflage" in send_format else "🔐 Standard Cipher Mode Active"
        lock_hint = " + 🔒 Private Password Locked" if msg_private_pass.strip() else ""
        prompt_msg = st.chat_input(f"💬 [{mode_hint}{lock_hint}] Type message to #{curr_room} and press Enter...")

        if prompt_msg and prompt_msg.strip():
            t_mode_code = "NONE"
            target_epoch = 0
            if "Self-Destruct" in timer_choice:
                t_mode_code = "EXPIRE"
                mins_val = 5 if "5m" in timer_choice else (15 if "15m" in timer_choice else 60)
                target_epoch = int(time.time()) + (mins_val * 60)
            elif "Time-Capsule" in timer_choice:
                t_mode_code = "WAIT"
                target_epoch = int(time.time()) + 300

            raw_cipher = encrypt_core_fn(prompt_msg.strip(), group_key, reverse_rule, t_mode_code, target_epoch)
            priv_hash_val = hashlib.sha256(msg_private_pass.strip().encode("utf-8")).hexdigest() if msg_private_pass.strip() else ""

            if "Camouflage" in send_format:
                camo_payload = encode_camo_fn(raw_cipher)
                append_rich_message(
                    load_all_rooms_fn, save_all_rooms_fn,
                    curr_room, agent_name, camo_payload,
                    msg_type="CAMO", private_pass_hash=priv_hash_val
                )
            else:
                append_rich_message(
                    load_all_rooms_fn, save_all_rooms_fn,
                    curr_room, agent_name, raw_cipher,
                    msg_type="TEXT", private_pass_hash=priv_hash_val
                )
            st.rerun()

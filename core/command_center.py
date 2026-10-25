import streamlit as st
import json
import os
import io
import hashlib
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_agent_full_telemetry(username: str) -> dict:
    """Tổng hợp toàn bộ điểm số, tiến độ học tập và vật phẩm của người chơi từ mọi cơ sở dữ liệu."""
    ctf_db = _load_json("ctf_arena_db.json")
    acad_db = _load_json("academy_lms_db.json")
    sdk_db = _load_json("sudoku_arena_db.json")
    comm_db = _load_json("community_hub_db.json")
    inv_db = _load_json("tactical_inventory_db.json")

    ctf_u = ctf_db.get("users", {}).get(username, {})
    ctf_xp = ctf_u.get("xp", 0)
    ctf_solved = len(ctf_u.get("solved", []))

    acad_u = acad_db.get("students", {}).get(username, {})
    acad_xp = acad_u.get("acad_xp", 0)
    acad_tasks = set(acad_u.get("completed_tasks", []))
    full_mods = 0
    for m_idx in range(1, 21):
        mid = f"M{m_idx:02d}"
        if {f"{mid}_Q1", f"{mid}_Q2", f"{mid}_L1", f"{mid}_L2"}.issubset(acad_tasks):
            full_mods += 1

    sdk_u = sdk_db.get("leaderboard", {}).get(username, {})
    arcade_xp = sdk_u.get("sudoku_score", 0)
    arcade_wins = sdk_u.get("puzzles_solved", 0)

    comm_u = comm_db.get("profiles", {}).get(username, {})
    comm_xp = comm_u.get("comm_xp", 500)

    inv_u = inv_db.get("users", {}).get(username, {})
    streak = inv_u.get("streak", 0)
    total_items = sum(inv_u.get("items", {}).values()) if "items" in inv_u else 6

    total_xp = ctf_xp + acad_xp + max(0, arcade_xp) + comm_xp
    level = 1 + (total_xp // 1500)

    if level >= 20:
        rank_title = " GRANDMASTER CRYPTANALYST"
    elif level >= 12:
        rank_title = " SENIOR CYBER ARCHITECT"
    elif level >= 6:
        rank_title = " SPECIAL FORENSIC AGENT"
    elif level >= 3:
        rank_title = " FIELD OPERATIVE"
    else:
        rank_title = " CYBER RECRUIT"

    return {
        "username": username,
        "total_xp": total_xp,
        "level": level,
        "rank_title": rank_title.strip(),
        "ctf_xp": ctf_xp,
        "ctf_solved": ctf_solved,
        "acad_xp": acad_xp,
        "acad_tasks_cnt": len(acad_tasks),
        "acad_full_mods": full_mods,
        "arcade_xp": arcade_xp,
        "arcade_wins": arcade_wins,
        "comm_xp": comm_xp,
        "streak": streak,
        "total_items": total_items
    }


def generate_agent_id_card_png(stats: dict) -> bytes:
    """Vẽ Thẻ Căn Cước Điệp Viên (Agent Cyber ID Card) ra file ảnh .PNG sắc nét bằng thư viện PIL."""
    w, h = 920, 520
    img = Image.new("RGB", (w, h), (9, 13, 22))
    draw = ImageDraw.Draw(img)

    # Vẽ nền chuyển sắc nhẹ và lưới công nghệ (Cyber Grid)
    for y in range(h):
        r_c = int(10 + (y / h) * 18)
        g_c = int(15 + (y / h) * 24)
        b_c = int(32 + (y / h) * 48)
        draw.line([(0, y), (w, y)], fill=(r_c, g_c, b_c))

    for gx in range(0, w, 40):
        draw.line([(gx, 0), (gx, h)], fill=(20, 30, 55), width=1)
    for gy in range(0, h, 40):
        draw.line([(0, gy), (w, gy)], fill=(20, 30, 55), width=1)

    # Khung viền ngoài Neon
    draw.rectangle([12, 12, w - 13, h - 13], outline=(56, 189, 248), width=3)
    draw.rectangle([20, 20, w - 21, h - 21], outline=(30, 58, 138), width=1)

    # Thanh tiêu đề trên cùng
    draw.rectangle([20, 20, w - 21, 92], fill=(15, 23, 42))
    draw.line([(20, 92), (w - 21, 92)], fill=(56, 189, 248), width=2)

    font_def = ImageFont.load_default()
    draw.text((40, 36), "ULTIMATE SECRET MESSENGER // ZERO-TRUST AGENCY", fill=(56, 189, 248), font=font_def)
    draw.text((40, 58), "OFFICIAL CRYPTOGRAPHIC OPERATIVE CREDENTIAL", fill=(248, 250, 252), font=font_def)
    draw.text((w - 240, 46), f"CLEARANCE: LEVEL {stats['level']:02d}", fill=(253, 224, 71), font=font_def)

    # Khung Avatar / Biểu tượng Điệp viên bên trái
    draw.rectangle([42, 120, 242, 340], fill=(17, 24, 39), outline=(99, 102, 241), width=2)
    # Vẽ biểu tượng Khiên Mật Mã cách điệu bên trong khung Avatar
    shield_pts = [(142, 150), (195, 175), (185, 255), (142, 295), (99, 255), (89, 175)]
    draw.polygon(shield_pts, fill=(30, 27, 75), outline=(129, 140, 248))
    draw.text((112, 215), f"LVL {stats['level']:02d}", fill=(253, 224, 71), font=font_def)
    draw.text((78, 312), "VERIFIED AGENT", fill=(52, 211, 153), font=font_def)

    # Thông tin định danh bên phải
    u_name = stats["username"].upper()
    draw.text((275, 122), f"OPERATIVE CALLSIGN :  {u_name}", fill=(255, 255, 255), font=font_def)
    draw.text((275, 152), f"DESIGNATED RANK    :  {stats['rank_title']}", fill=(253, 224, 71), font=font_def)
    draw.text((275, 182), f"TOTAL COMBINED XP  :  {stats['total_xp']:,} XP", fill=(52, 211, 153), font=font_def)

    # 4 Hộp chỉ số thành tích
    boxes = [
        (275, 220, 565, 275, "ACADEMY MASTERY", f"{stats['acad_full_mods']}/20 Modules ({stats['acad_xp']:,} XP)"),
        (585, 220, 875, 275, "ARCADE & SUDOKU", f"{stats['arcade_wins']} Wins ({stats['arcade_xp']:,} PTS)"),
        (275, 285, 565, 340, "CTF ARENA SOLVES", f"{stats['ctf_solved']} Cracked ({stats['ctf_xp']:,} XP)"),
        (585, 285, 875, 340, "LOGIN STREAK & GEAR", f"{stats['streak']}d Streak | {stats['total_items']} Items")
    ]
    for bx1, by1, bx2, by2, b_title, b_val in boxes:
        draw.rectangle([bx1, by1, bx2, by2], fill=(15, 23, 42), outline=(51, 65, 85), width=1)
        draw.text((bx1 + 14, by1 + 10), b_title, fill=(148, 163, 184), font=font_def)
        draw.text((bx1 + 14, by1 + 30), b_val, fill=(248, 250, 252), font=font_def)

    # Chữ ký số SHA-256 ở chân thẻ
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sig_raw = f"USM_ID_{stats['username']}_{stats['total_xp']}_{now_str}"
    sig_hash = hashlib.sha256(sig_raw.encode("utf-8")).hexdigest().upper()

    draw.rectangle([42, 375, w - 42, 475], fill=(11, 15, 25), outline=(30, 41, 59), width=1)
    draw.text((58, 390), f"ISSUED TIMESTAMP (UTC) : {now_str}", fill=(148, 163, 184), font=font_def)
    draw.text((58, 415), f"ISSUING AUTHORITY      : LE HOANG PHU HIEU (FIT - VNUHCM-US)", fill=(96, 165, 250), font=font_def)
    draw.text((58, 440), f"SHA-256 DIGITAL SIG    : {sig_hash[:48]}...", fill=(100, 116, 139), font=font_def)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_academy_certificate_png(stats: dict) -> bytes:
    """Vẽ Bằng Chứng Nhận Học Viện An Ninh Mạng (Official Cryptography Certificate) ra file .PNG."""
    w, h = 1000, 640
    img = Image.new("RGB", (w, h), (10, 14, 26))
    draw = ImageDraw.Draw(img)

    # Viền Vàng Hoàng Gia (Gold Double Border)
    draw.rectangle([18, 18, w - 19, h - 19], outline=(234, 179, 8), width=4)
    draw.rectangle([28, 28, w - 29, h - 29], outline=(56, 189, 248), width=2)
    draw.rectangle([36, 36, w - 37, h - 37], fill=(15, 23, 42))

    font_def = ImageFont.load_default()

    draw.text((310, 68), "ULTIMATE SECRET MESSENGER • SECURITY ACADEMY", fill=(56, 189, 248), font=font_def)
    draw.text((325, 100), "OFFICIAL CERTIFICATE OF CRYPTOGRAPHIC MASTERY", fill=(253, 224, 71), font=font_def)
    draw.line([(200, 128), (800, 128)], fill=(234, 179, 8), width=2)

    draw.text((380, 160), "THIS IS TO CERTIFY THAT OPERATIVE:", fill=(203, 213, 225), font=font_def)

    # Khung tên học viên nổi bật
    draw.rectangle([220, 195, 780, 255], fill=(30, 27, 75), outline=(129, 140, 248), width=2)
    draw.text((390, 218), f"AGENT:  {stats['username'].upper()}", fill=(255, 255, 255), font=font_def)

    draw.text(
        (140, 285),
        "Has demonstrated outstanding analytical proficiency in Classical Ciphers, Low-Level Binary",
        fill=(226, 232, 240), font=font_def
    )
    draw.text(
        (140, 310),
        "Systems (Bits, Bytes, Two's Complement, Assembly), Mathematical Cryptography, and Modern",
        fill=(226, 232, 240), font=font_def
    )
    draw.text(
        (140, 335),
        "Zero-Trust Security Protocols (SHA-256, AES-256, RSA, Steganography & Post-Quantum Crypto).",
        fill=(226, 232, 240), font=font_def
    )

    # Bảng điểm tổng kết trên bằng
    draw.rectangle([140, 375, 860, 455], fill=(9, 13, 22), outline=(56, 189, 248), width=1)
    draw.text(
        (170, 395),
        f"• Completed Curriculum Modules : {stats['acad_full_mods']} / 20 Modules ({stats['acad_tasks_cnt']}/80 Tasks Passed)",
        fill=(52, 211, 153), font=font_def
    )
    draw.text(
        (170, 422),
        f"• Total Academic & Tactical XP : {stats['total_xp']:,} XP  |  Clearance Rank: {stats['rank_title']}",
        fill=(253, 224, 71), font=font_def
    )

    # Dấu mộc chứng nhận & Chữ ký
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d UTC")
    cert_hash = hashlib.sha256(f"CERT_{stats['username']}_{stats['total_xp']}".encode("utf-8")).hexdigest()[:24].upper()

    draw.text((140, 500), f"DATE ISSUED : {now_str}", fill=(148, 163, 184), font=font_def)
    draw.text((140, 525), f"VERIFY HASH : SHA256-{cert_hash}", fill=(148, 163, 184), font=font_def)

    draw.line([(600, 520), (860, 520)], fill=(234, 179, 8), width=1)
    draw.text((625, 530), "LE HOANG PHU HIEU (ID: 25127049)", fill=(253, 224, 71), font=font_def)
    draw.text((615, 550), "Platform Creator • FIT - VNUHCM-US", fill=(56, 189, 248), font=font_def)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def render_home_command_center(default_username: str = "taolagautruc"):
    """
    Hiển thị Trung Tâm Chỉ Huy Điệp Viên (Live Command Center) & Xuất Thẻ Điệp Viên / Chứng Chỉ .PNG
    ngay trên Trang chủ (1. Home Dashboard).
    """
    active_user = (st.session_state.get("auth_callsign") or st.session_state.get("ctf_user") or default_username).strip()
    if active_user == "Guest_Agent":
        active_user = st.session_state.get("ctf_user") or default_username

    stats = get_agent_full_telemetry(active_user)

    st.markdown("---")
    st.markdown("""
    <div class="ws-banner" style="background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #090d16 100%); border: 1.5px solid #38bdf8;">
        <h4>🎖️ Live Agent Command Center & Official Credential Generator</h4>
        <p>Real-time synchronization across all 8 platform modules. Export your verified <b>Agent ID Card (.PNG)</b> or <b>Academy Certificate (.PNG)</b> with embedded SHA-256 digital signatures!</p>
    </div>
    """, unsafe_allow_html=True)

    # 4 Chỉ số tổng hợp trực tiếp của người chơi trên Trang chủ
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("🕵️ Active Operative", stats["username"], f"Level {stats['level']} • {stats['rank_title']}")
    mc2.metric("⚡ Total Platform XP", f"{stats['total_xp']:,} XP", f"🔥 {stats['streak']}-Day Login Streak")
    mc3.metric("🎓 Academy Progress", f"{stats['acad_full_mods']} / 20 Modules", f"{stats['acad_tasks_cnt']}/80 Labs & Quizzes")
    mc4.metric("🏆 CTF & Arcade Wins", f"{stats['ctf_solved'] + stats['arcade_wins']} Victories", f"🎒 {stats['total_items']} Tactical Items")

    tab_idcard, tab_cert, tab_global_lb = st.tabs([
        "🪪 1. Export Agent ID Card (.PNG)",
        "🎓 2. Official Academy Certificate (.PNG)",
        "🌍 3. Global Cross-Platform Leaderboard"
    ])

    with tab_idcard:
        col_img, col_dl = st.columns([2.2, 1.2])
        id_png_bytes = generate_agent_id_card_png(stats)
        with col_img:
            st.image(id_png_bytes, caption=f"Official Cyber Operative ID Card — {stats['username']}", use_container_width=True)
        with col_dl:
            st.markdown("##### 🪪 Your Cyber Operative Credential")
            st.caption(
                "This ID card dynamically compiles your live XP, Clearance Level, Academy mastery, "
                "Arcade victories, and a tamper-proof **SHA-256 Digital Signature**."
            )
            st.download_button(
                "⬇️ Download Agent ID Card (.PNG)",
                data=id_png_bytes,
                file_name=f"USM_Agent_ID_{stats['username']}.png",
                mime="image/png",
                type="primary",
                use_container_width=True
            )

    with tab_cert:
        col_c1, col_c2 = st.columns([2.2, 1.2])
        cert_png_bytes = generate_academy_certificate_png(stats)
        with col_c1:
            st.image(cert_png_bytes, caption=f"Official Security Academy Certificate — {stats['username']}", use_container_width=True)
        with col_c2:
            st.markdown("##### 🎓 Cryptography & CS Graduation Certificate")
            st.caption(
                "Complete modules in **Section 5 (Security Academy)** to upgrade your certificate's completion score! "
                "Signed by Platform Creator **Le Hoang Phu Hieu (FIT - VNUHCM-US)**."
            )
            st.download_button(
                "⬇️ Download Official Certificate (.PNG)",
                data=cert_png_bytes,
                file_name=f"USM_Certificate_{stats['username']}.png",
                mime="image/png",
                type="primary",
                use_container_width=True
            )

    with tab_global_lb:
        st.caption("🏆 **Top Operatives Ranked by Combined Platform XP (CTF + Academy + Game Arcade + Community Hub):**")
        # Tập hợp danh sách tất cả người chơi trên hệ thống
        all_users = {active_user, "taolagautruc", "CipherKing_VN", "Alice_HCMUS", "Grandmaster_Kai"}
        for db_f, k_top in [("ctf_arena_db.json", "users"), ("academy_lms_db.json", "students"), ("sudoku_arena_db.json", "leaderboard")]:
            d_obj = _load_json(db_f)
            all_users.update(d_obj.get(k_top, {}).keys())

        ranked_list = [get_agent_full_telemetry(u) for u in all_users if u and u != "Guest_Agent"]
        ranked_list.sort(key=lambda x: x["total_xp"], reverse=True)

        for idx, r_stat in enumerate(ranked_list[:8], start=1):
            medal = "🥇" if idx == 1 else ("🥈" if idx == 2 else ("🥉" if idx == 3 else f"#{idx}"))
            you_tag = " *(You)*" if r_stat["username"] == active_user else ""
            rc1, rc2, rc3, rc4 = st.columns([2.0, 1.3, 1.3, 1.4])
            rc1.markdown(f"**{medal} &nbsp; `{r_stat['username']}`**{you_tag}")
            rc2.markdown(f"⚡ **{r_stat['total_xp']:,} XP** (`Lv.{r_stat['level']}`)")
            rc3.markdown(f"🎓 `{r_stat['acad_full_mods']}/20` Modules")
            rc4.markdown(f"🕹️ `{r_stat['ctf_solved'] + r_stat['arcade_wins']}` Wins")

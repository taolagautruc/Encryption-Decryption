import streamlit as st
import json
import os
import random
from datetime import datetime, timezone, timedelta

INV_DB_FILE = "tactical_inventory_db.json"

TACTICAL_ITEMS_META = {
    "free_hint_pass": {
        "name": "🎫 Free Hint Pass",
        "vn_name": "Thẻ Miễn Phạt Hint",
        "desc": "Reveals 1 correct Sudoku cell instantly with 0% score penalty & 0s time penalty."
    },
    "forensic_scanner": {
        "name": "🔍 Forensic Scanner",
        "vn_name": "Máy Quét Pháp Y",
        "desc": "Scans your active 9x9 Sudoku board and highlights any wrong numbers you entered."
    },
    "chrono_freeze": {
        "name": "⏳ Chrono-Freeze (+60s)",
        "vn_name": "Bình Đóng Băng (+60s)",
        "desc": "Adds +60 seconds of bonus solve time in your active Multiplayer Sudoku room."
    },
    "score_shield": {
        "name": "🛡️ Score Shield",
        "vn_name": "Khiên Bảo Hộ Điểm",
        "desc": "Protects your score from surrender penalties and restores +1,000 PTS."
    },
    "xp_booster": {
        "name": "⚡ 2x XP Booster",
        "vn_name": "Thẻ Nhân Đôi XP",
        "desc": "Grants an instant +800 Bonus XP surge to your Agent Profile."
    },
    "mystery_lootbox": {
        "name": "📦 Encrypted Lootbox",
        "vn_name": "Rương Mật Mã Bí Ẩn",
        "desc": "Open to receive 2 random tactical items + 300 to 1,200 Bonus XP!"
    }
}

DAILY_STREAK_REWARDS = [
    {"day": 1, "item": "forensic_scanner", "qty": 1, "xp": 200, "label": "Day 1: 🔍 1x Scanner + 200 XP"},
    {"day": 2, "item": "free_hint_pass", "qty": 1, "xp": 300, "label": "Day 2: 🎫 1x Free Hint + 300 XP"},
    {"day": 3, "item": "chrono_freeze", "qty": 1, "xp": 400, "label": "Day 3: ⏳ 1x Chrono-Freeze + 400 XP"},
    {"day": 4, "item": "score_shield", "qty": 1, "xp": 500, "label": "Day 4: 🛡️ 1x Score Shield + 500 XP"},
    {"day": 5, "item": "free_hint_pass", "qty": 2, "xp": 600, "label": "Day 5: 🎫 2x Free Hint + 600 XP"},
    {"day": 6, "item": "xp_booster", "qty": 1, "xp": 800, "label": "Day 6: ⚡ 1x XP Booster + 800 XP"},
    {"day": 7, "item": "mystery_lootbox", "qty": 2, "xp": 1500, "label": "Day 7: 📦 2x Lootbox + 1,500 XP"}
]


def _load_json(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_json(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_inv_db() -> dict:
    db = _load_json(INV_DB_FILE)
    if "users" not in db:
        db = {"users": {}}
    return db


def save_inv_db(db: dict):
    _save_json(INV_DB_FILE, db)


def add_agent_comm_xp(username: str, bonus_xp: int):
    """Cộng điểm XP trực tiếp vào hồ sơ Điệp viên ở Mục 7 (community_hub_db.json)."""
    comm_file = "community_hub_db.json"
    comm_db = _load_json(comm_file)
    if "profiles" not in comm_db:
        comm_db["profiles"] = {}
    if username not in comm_db["profiles"]:
        comm_db["profiles"][username] = {
            "comm_xp": 500,
            "spent_xp": 0,
            "owned_items": ["badge_shield", "theme_cyber"],
            "equipped_badge": "badge_shield",
            "equipped_theme": "theme_cyber",
            "bio": "Cryptanalyst & Forensic Investigator at Ultimate Secret Messenger."
        }
    comm_db["profiles"][username]["comm_xp"] = comm_db["profiles"][username].get("comm_xp", 0) + bonus_xp
    _save_json(comm_file, comm_db)


def get_completed_academy_modules_count(username: str) -> int:
    """Đếm số bài học ở Mục 5 (M01..M20) mà người dùng đã hoàn thành đủ cả 4/4 bài tập (Q1, Q2, L1, L2)."""
    acad_db = _load_json("academy_lms_db.json")
    completed_tasks = set(acad_db.get("students", {}).get(username, {}).get("completed_tasks", []))
    full_modules = 0
    for m_idx in range(1, 21):
        mod_id = f"M{m_idx:02d}"
        req = {f"{mod_id}_Q1", f"{mod_id}_Q2", f"{mod_id}_L1", f"{mod_id}_L2"}
        if req.issubset(completed_tasks):
            full_modules += 1
    return full_modules


def get_total_puzzles_cracked(username: str) -> int:
    """Đếm tổng số câu đố CTF (Mục 4) + số bàn cờ Sudoku đã giải xong."""
    ctf_db = _load_json("ctf_arena_db.json")
    sdk_db = _load_json("sudoku_arena_db.json")
    ctf_cnt = len(ctf_db.get("users", {}).get(username, {}).get("solved", []))
    sdk_cnt = sdk_db.get("leaderboard", {}).get(username, {}).get("puzzles_solved", 0)
    return ctf_cnt + sdk_cnt


def ensure_user_inventory(db: dict, username: str) -> dict:
    if username not in db["users"]:
        db["users"][username] = {
            "streak": 0,
            "last_claim_date": "",
            "claimed_academy_mods": 0,
            "daily_puzzle_claim_date": "",
            "Daily_Baseline_Puzzles": 0,
            "items": {
                "free_hint_pass": 2,
                "forensic_scanner": 1,
                "chrono_freeze": 1,
                "score_shield": 1,
                "xp_booster": 0,
                "mystery_lootbox": 1
            }
        }
        save_inv_db(db)
    return db["users"][username]


def use_tactical_item(username: str, item_key: str) -> tuple[bool, str]:
    """Thực thi công dụng thực chiến của từng vật phẩm khi người chơi bấm Sử dụng."""
    db = load_inv_db()
    u_inv = ensure_user_inventory(db, username)
    curr_qty = u_inv["items"].get(item_key, 0)
    if curr_qty <= 0:
        return False, "❌ Bạn đã hết vật phẩm này trong Túi đồ!"

    # 1. THẺ MIỄN PHẠT HINT (Mở 1 ô đúng trên bàn cờ Sudoku mà không tính vào số lần dùng Hint)
    if item_key == "free_hint_pass":
        if "sudoku_state" not in st.session_state:
            return False, "⚠️ Hãy mở bàn cờ Sudoku 9x9 trước khi dùng Thẻ Miễn Phạt Hint!"
        gs = st.session_state.sudoku_state
        if gs.get("completed"):
            return False, "⚠️ Bàn cờ hiện tại đã hoàn thành rồi!"
        empty_coords = [
            (r, c) for r in range(9) for c in range(9)
            if gs["puzzle"][r][c] == 0 and gs["user_board"][r][c] != gs["solution"][r][c]
        ]
        if not empty_coords:
            return False, "✅ Toàn bộ các ô trên bàn cờ của bạn đều đã điền đúng!"
        r_pick, c_pick = random.choice(empty_coords)
        correct_val = gs["solution"][r_pick][c_pick]
        gs["user_board"][r_pick][c_pick] = correct_val
        # Ghi nhận thành ô cố định để không bị tính vào hinted_cells (0% phạt điểm!)
        gs["puzzle"][r_pick][c_pick] = correct_val
        u_inv["items"][item_key] -= 1
        save_inv_db(db)
        return True, f"🎫 Đã mở khóa miễn phí ô **(R{r_pick+1}, C{c_pick+1}) = `{correct_val}`** (Giữ nguyên 100% điểm thưởng)!"

    # 2. MÁY QUÉT PHÁP Y (Quét lỗi sai trên bàn cờ Sudoku hoặc mở giúp 1 ô đúng)
    elif item_key == "forensic_scanner":
        if "sudoku_state" not in st.session_state:
            return False, "⚠️ Hãy mở bàn cờ Sudoku 9x9 để quét lỗi!"
        gs = st.session_state.sudoku_state
        wrong_cells = []
        for r in range(9):
            for c in range(9):
                val = gs["user_board"][r][c]
                if gs["puzzle"][r][c] == 0 and val != 0 and val != gs["solution"][r][c]:
                    wrong_cells.append(f"(R{r+1}, C{c+1}: đang điền {val})")
        u_inv["items"][item_key] -= 1
        save_inv_db(db)
        if wrong_cells:
            return True, "🔍 **Kết quả Quét Pháp Y:** Phát hiện ô điền sai tại: " + ", ".join(wrong_cells[:5])
        else:
            # Nếu không có ô nào sai, thưởng mở giúp 1 ô trống
            empty_coords = [(r, c) for r in range(9) for c in range(9) if gs["user_board"][r][c] == 0]
            if empty_coords:
                rp, cp = empty_coords[0]
                ans_v = gs["solution"][rp][cp]
                gs["user_board"][rp][cp] = ans_v
                gs["puzzle"][rp][cp] = ans_v
                return True, f"🔍 Không có ô nào sai! Máy quét đã điền giúp bạn ô **(R{rp+1}, C{cp+1}) = `{ans_v}`**!"
            return True, "🔍 Mọi con số trên bàn cờ của bạn đều chính xác 100%!"

    # 3. BÌNH ĐÓNG BĂNG THỜI GIAN (+60 GIÂY TRONG PHÒNG ĐẤU SUDOKU MULTIPLAYER)
    elif item_key == "chrono_freeze":
        sdk_db = _load_json("sudoku_arena_db.json")
        rooms = sdk_db.get("rooms", {})
        if not rooms:
            return False, "⚠️ Hiện chưa có phòng đấu Sudoku Multiplayer nào đang mở!"
        for r_code, r_info in rooms.items():
            if username in r_info.get("players", {}):
                r_info["solve_duration_sec"] = r_info.get("solve_duration_sec", 900) + 60
        _save_json("sudoku_arena_db.json", sdk_db)
        u_inv["items"][item_key] -= 1
        save_inv_db(db)
        return True, "⏳ **Chrono-Freeze Activated!** Đã cộng thêm **+60 giây** vào thời gian giải phòng đấu Sudoku của bạn!"

    # 4. KHIÊN BẢO HỘ ĐIỂM (+1,000 PTS BẢO HIỂM SUDOKU / CTF)
    elif item_key == "score_shield":
        sdk_db = _load_json("sudoku_arena_db.json")
        lb = sdk_db.setdefault("leaderboard", {})
        if username not in lb:
            lb[username] = {"sudoku_score": 0, "puzzles_solved": 0, "best_tier": 1}
        lb[username]["sudoku_score"] = lb[username].get("sudoku_score", 0) + 1000
        _save_json("sudoku_arena_db.json", sdk_db)
        u_inv["items"][item_key] -= 1
        save_inv_db(db)
        return True, "🛡️ **Score Shield Activated!** Đã bọc khiên bảo vệ và cộng bù **+1,000 PTS** vào bảng xếp hạng Sudoku!"

    # 5. THẺ NHÂN ĐÔI XP (+800 XP TỨC THÌ)
    elif item_key == "xp_booster":
        add_agent_comm_xp(username, 800)
        u_inv["items"][item_key] -= 1
        save_inv_db(db)
        return True, "⚡ **2x XP Booster Activated!** Đã cộng ngay **+800 XP** vào Hồ sơ Điệp viên & Cửa hàng Cyber Shop!"

    # 6. RƯƠNG MẬT MÃ BÍ ẨN (NHẬN NGẪU NHIÊN 2 VẬT PHẨM + 300..1,200 XP)
    elif item_key == "mystery_lootbox":
        u_inv["items"][item_key] -= 1
        pool = ["free_hint_pass", "forensic_scanner", "chrono_freeze", "score_shield", "xp_booster"]
        drop1, drop2 = random.choices(pool, k=2)
        bonus_xp = random.choice([300, 500, 800, 1200])
        u_inv["items"][drop1] = u_inv["items"].get(drop1, 0) + 1
        u_inv["items"][drop2] = u_inv["items"].get(drop2, 0) + 1
        save_inv_db(db)
        add_agent_comm_xp(username, bonus_xp)
        n1 = TACTICAL_ITEMS_META[drop1]["name"]
        n2 = TACTICAL_ITEMS_META[drop2]["name"]
        return True, f"🎉 **Mở Rương Thành Công!** Bạn nhận được: **1x {n1}**, **1x {n2}** và **+{bonus_xp:,} XP**!"

    return False, "❌ Vật phẩm không hợp lệ."


def render_sidebar_tactical_hub(default_username: str = "taolagautruc"):
    """
    Hiển thị Trung tâm Điểm danh Hàng ngày, Nhiệm vụ Ngày & Túi đồ Vật phẩm Chiến thuật
    ngay trên thanh Sidebar để người chơi mở dùng bất cứ lúc nào.
    """
    username = (st.session_state.get("ctf_user") or default_username).strip() or "taolagautruc"
    db = load_inv_db()
    u_inv = ensure_user_inventory(db, username)

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday_str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    st.markdown("---")
    st.markdown("### 🎁 Daily Rewards & Backpack")

    # --- 1. ĐIỂM DANH HÀNG NGÀY (7-DAY LOGIN STREAK) ---
    already_claimed_today = (u_inv.get("last_claim_date") == today_str)
    curr_streak = u_inv.get("streak", 0)
    next_day_idx = (curr_streak % 7)
    next_reward_info = DAILY_STREAK_REWARDS[next_day_idx]

    if not already_claimed_today:
        if st.button(f"📅 Claim {next_reward_info['label']}", type="primary", use_container_width=True):
            if u_inv.get("last_claim_date") == yesterday_str:
                u_inv["streak"] = curr_streak + 1
            else:
                u_inv["streak"] = 1
            u_inv["last_claim_date"] = today_str
            u_inv["Daily_Baseline_Puzzles"] = get_total_puzzles_cracked(username)

            r_item = next_reward_info["item"]
            r_qty = next_reward_info["qty"]
            r_xp = next_reward_info["xp"]
            u_inv["items"][r_item] = u_inv["items"].get(r_item, 0) + r_qty
            save_inv_db(db)
            add_agent_comm_xp(username, r_xp)
            st.balloons()
            st.toast(f"🎉 Điểm danh Ngày {u_inv['streak']} thành công! (+{r_xp} XP)", icon="🎁")
            st.rerun()
    else:
        st.success(f"✅ Daily Login Claimed! (🔥 Streak: **{curr_streak} Days**)")

    # --- 2. NHẬN THƯỞNG KHI HỌC XONG BÀI HỌC Ở MỤC 5 & GIẢI ĐỐ MỤC 4 / SUDOKU ---
    with st.expander("📋 Daily Quests & Academy Rewards", expanded=False):
        # Quest A: Giải đố hàng ngày (Mục 4 hoặc Sudoku)
        total_puz_now = get_total_puzzles_cracked(username)
        baseline_puz = u_inv.get("Daily_Baseline_Puzzles", 0)
        puz_claimed_today = (u_inv.get("daily_puzzle_claim_date") == today_str)

        st.markdown("**🕹️ 1. Daily Puzzle Solver Quest**")
        st.caption("Reward: `🎫 1x Free Hint` + `⏳ 1x Chrono-Freeze` + `300 XP`")
        if puz_claimed_today:
            st.info("✅ Đã nhận thưởng Nhiệm vụ Giải đố hôm nay!")
        elif total_puz_now > baseline_puz and total_puz_now > 0:
            if st.button("🎁 Claim Daily Puzzle Reward!", key="btn_claim_daily_puz", type="primary", use_container_width=True):
                u_inv["daily_puzzle_claim_date"] = today_str
                u_inv["items"]["free_hint_pass"] = u_inv["items"].get("free_hint_pass", 0) + 1
                u_inv["items"]["chrono_freeze"] = u_inv["items"].get("chrono_freeze", 0) + 1
                save_inv_db(db)
                add_agent_comm_xp(username, 300)
                st.balloons()
                st.rerun()
        else:
            st.caption("⏳ *Hãy giải thêm 1 câu đố ở Mục 4 hoặc 1 bàn Sudoku 9x9 để mở khóa!*")

        st.divider()

        # Quest B: Hoàn thành trọn vẹn bài học ở Mục 5 (Security Academy)
        full_mods_done = get_completed_academy_modules_count(username)
        already_rewarded_mods = u_inv.get("claimed_academy_mods", 0)
        unclaimed_mods = max(0, full_mods_done - already_rewarded_mods)

        st.markdown("**🎓 2. Security Academy Milestone**")
        st.caption(f"Completed Modules (4/4 tasks): **`{full_mods_done} / 20`**")
        if unclaimed_mods > 0:
            if st.button(f"🎁 Claim {unclaimed_mods} Lesson Reward(s)!", key="btn_claim_acad_mod", type="primary", use_container_width=True):
                u_inv["claimed_academy_mods"] = full_mods_done
                u_inv["items"]["free_hint_pass"] = u_inv["items"].get("free_hint_pass", 0) + unclaimed_mods
                u_inv["items"]["mystery_lootbox"] = u_inv["items"].get("mystery_lootbox", 0) + unclaimed_mods
                save_inv_db(db)
                add_agent_comm_xp(username, unclaimed_mods * 500)
                st.balloons()
                st.rerun()
        else:
            st.caption("💡 *Mỗi khi học xong đủ 4/4 bài tập của 1 bài học ở Mục 5, bạn sẽ nhận được `🎫 1x Free Hint` + `📦 1x Lootbox` + `500 XP` tại đây!*")

    # --- 3. TÚI ĐỒ VẬT PHẨM CHIẾN THUẬT (TACTICAL BACKPACK) ---
    total_items_cnt = sum(u_inv["items"].values())
    with st.expander(f"🎒 Tactical Backpack ({total_items_cnt} Items)", expanded=False):
        if "last_item_msg" in st.session_state and st.session_state.last_item_msg:
            ok_flag, msg_txt = st.session_state.last_item_msg
            if ok_flag:
                st.success(msg_txt)
            else:
                st.warning(msg_txt)

        for k_id, meta in TACTICAL_ITEMS_META.items():
            qty = u_inv["items"].get(k_id, 0)
            ic1, ic2 = st.columns([2.2, 1.1])
            with ic1:
                st.markdown(f"**{meta['name']}** (`x{qty}`)")
                st.caption(meta["desc"])
            with ic2:
                if st.button("⚡ Use", key=f"use_tact_{k_id}", disabled=(qty <= 0), use_container_width=True):
                    ok_u, res_msg = use_tactical_item(username, k_id)
                    st.session_state.last_item_msg = (ok_u, res_msg)
                    st.rerun()

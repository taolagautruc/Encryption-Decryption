import streamlit as st
import random
import time
import json
import os
from datetime import datetime, timezone

SUDOKU_DB_FILE = "sudoku_arena_db.json"

def load_sudoku_db() -> dict:
    if not os.path.exists(SUDOKU_DB_FILE):
        default_db = {
            "leaderboard": {
                "Grandmaster_Kai": {"sudoku_score": 48500, "puzzles_solved": 6, "best_tier": 5},
                "SudokuQueen_99": {"sudoku_score": 21200, "puzzles_solved": 4, "best_tier": 4},
                "LogicKnight_US": {"sudoku_score": 8500, "puzzles_solved": 3, "best_tier": 3}
            },
            "rooms": {}
        }
        with open(SUDOKU_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_db, f, ensure_ascii=False, indent=4)
        return default_db
    try:
        with open(SUDOKU_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"leaderboard": {}, "rooms": {}}

def save_sudoku_db(data: dict):
    with open(SUDOKU_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def generate_sudoku_9x9(tier: int, seed_val: str = None) -> tuple[list[list[int]], list[list[int]]]:
    """Sinh ma trận Sudoku 9x9 chuẩn toán học (81 ô, 9 khối 3x3) theo 5 Tier độ khó."""
    rng = random.Random(seed_val) if seed_val else random.Random()
    base = 3
    side = 9

    def pattern(r, c):
        return (base * (r % base) + r // base + c) % side

    def shuffle(s):
        lst = list(s)
        rng.shuffle(lst)
        return lst

    r_base = range(base)
    rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
    cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
    nums = shuffle(range(1, 10))

    solution = [[nums[pattern(r, c)] for c in cols] for r in rows]

    removals_map = {1: 28, 2: 36, 3: 44, 4: 52, 5: 58}
    removals = removals_map.get(tier, 36)

    puzzle = [row[:] for row in solution]
    all_cells = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(all_cells)

    for i in range(removals):
        r, c = all_cells[i]
        puzzle[r][c] = 0

    return solution, puzzle

def check_board_conflicts(board: list[list[int]]) -> list[str]:
    """Kiểm tra trùng số trên từng Hàng, Cột và Khối 3x3."""
    errors = []
    for r in range(9):
        nums = [x for x in board[r] if x != 0]
        if len(nums) != len(set(nums)):
            errors.append(f"Row R{r+1} has duplicate numbers!")
    for c in range(9):
        nums = [board[r][c] for r in range(9) if board[r][c] != 0]
        if len(nums) != len(set(nums)):
            errors.append(f"Column C{c+1} has duplicate numbers!")
    for br in range(3):
        for bc in range(3):
            nums = [
                board[r][c]
                for r in range(br * 3, br * 3 + 3)
                for c in range(bc * 3, bc * 3 + 3)
                if board[r][c] != 0
            ]
            if len(nums) != len(set(nums)):
                errors.append(f"3x3 Box ({br+1},{bc+1}) has duplicate numbers!")
    return errors

def inject_unified_sudoku_css():
    """CSS ép 81 ô trên 1 bảng 9x9 duy nhất đều nhau tuyệt đối và căn giữa chữ số."""
    st.markdown("""
    <style>
        /* Căn giữa chữ và đồng bộ chiều cao 42px cho mọi ô nhập trên bảng 9x9 duy nhất */
        div[data-testid="stTextInput"] input {
            text-align: center !important;
            font-size: 1.2rem !important;
            font-weight: 800 !important;
            color: #34d399 !important;
            background-color: #090d16 !important;
            border: 1px solid #334155 !important;
            border-radius: 6px !important;
            height: 42px !important;
            padding: 0 !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.5) !important;
        }
        /* Ô đề bài cố định (Xanh dương) và Ô Hint (Vàng kim) có cùng chiều cao 42px */
        .sdk-cell-fixed {
            height: 42px;
            line-height: 42px;
            text-align: center;
            background: #1e293b;
            color: #60a5fa;
            font-size: 1.2rem;
            font-weight: 800;
            border-radius: 6px;
            border: 1px solid #3b82f6;
            user-select: none;
        }
        .sdk-cell-hint {
            height: 42px;
            line-height: 42px;
            text-align: center;
            background: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            font-size: 1.2rem;
            font-weight: 800;
            border-radius: 6px;
            border: 1px solid #f59e0b;
            user-select: none;
        }
        .sdk-col-header {
            text-align: center;
            color: #94a3b8;
            font-weight: 700;
            font-size: 0.82rem;
            padding-bottom: 4px;
        }
        .sdk-row-header {
            height: 42px;
            line-height: 42px;
            text-align: center;
            color: #94a3b8;
            font-weight: 700;
            font-size: 0.85rem;
        }
        .subgrid-divider {
            border: 0;
            border-top: 3px solid #3b82f6;
            margin: 6px 0 10px 0;
            opacity: 0.85;
        }
    </style>
    """, unsafe_allow_html=True)

def render_single_unified_9x9_board(puzzle: list[list[int]], user_board: list[list[int]], hinted_cells: list, key_prefix: str, disabled: bool = False):
    """
    Hiển thị 1 BẢNG 9x9 DUY NHẤT vừa nhìn vừa điền đáp án trực tiếp.
    Có đánh số Hàng (R1-R9), Cột (C1-C9) và vạch phân cách rõ 9 khối 3x3.
    """
    inject_unified_sudoku_css()
    hint_set = set(tuple(x) for x in hinted_cells)

    # Đưa bảng vào khung căn giữa màn hình để gọn gàng, đều đặn
    _, center_board, _ = st.columns([0.6, 3.2, 0.6])
    with center_board:
        st.caption("🔵 **Blue Box** = Fixed Clue &nbsp;|&nbsp; 🟡 **Gold Box** = Hinted Cell &nbsp;|&nbsp; 🟢 **Dark Input Box** = Type `1–9` directly (leave blank to clear)")

        # Tỷ lệ cột có thêm khe ngăn cách ở sau C3 và C6 để tách 3 khối 3x3 theo chiều dọc
        col_weights = [0.65, 1, 1, 1, 0.18, 1, 1, 1, 0.18, 1, 1, 1]
        hdr_cols = st.columns(col_weights)
        hdr_cols[0].markdown("<div class='sdk-col-header'>R\\C</div>", unsafe_allow_html=True)
        for c in range(9):
            ui_idx = c + 1 + (1 if c >= 3 else 0) + (1 if c >= 6 else 0)
            hdr_cols[ui_idx].markdown(f"<div class='sdk-col-header'>C{c+1}</div>", unsafe_allow_html=True)

        # Vẽ 9 hàng
        for r in range(9):
            if r in [3, 6]:
                st.markdown("<hr class='subgrid-divider'>", unsafe_allow_html=True)

            r_cols = st.columns(col_weights)
            r_cols[0].markdown(f"<div class='sdk-row-header'>R{r+1}</div>", unsafe_allow_html=True)

            for c in range(9):
                ui_idx = c + 1 + (1 if c >= 3 else 0) + (1 if c >= 6 else 0)
                with r_cols[ui_idx]:
                    is_fixed = (puzzle[r][c] != 0)
                    is_hinted = ((r, c) in hint_set)
                    curr_val = user_board[r][c]

                    if is_fixed:
                        st.markdown(f"<div class='sdk-cell-fixed'>{puzzle[r][c]}</div>", unsafe_allow_html=True)
                    elif is_hinted:
                        st.markdown(f"<div class='sdk-cell-hint'>{curr_val}</div>", unsafe_allow_html=True)
                    else:
                        disp_str = str(curr_val) if curr_val in range(1, 10) else ""
                        typed = st.text_input(
                            f"R{r+1}C{c+1}",
                            value=disp_str,
                            max_chars=1,
                            key=f"{key_prefix}_r{r}_c{c}",
                            label_visibility="collapsed",
                            disabled=disabled,
                            placeholder="·"
                        ).strip()
                        if typed in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                            user_board[r][c] = int(typed)
                        else:
                            user_board[r][c] = 0

def render_sudoku_arcade(default_username: str = "taolagautruc"):
    st.markdown("""
    <div class="hero-box" style="padding: 24px 32px; margin-bottom: 20px; background: linear-gradient(135deg, #090d16 0%, #1e1b4b 50%, #312e81 100%); border: 1px solid #6366f1;">
        <div class="hero-badge" style="background: rgba(99, 102, 241, 0.2); color: #818cf8; border-color: #6366f1;">🧩 UNIFIED 9x9 SUDOKU BOARD • FAIR COUNTDOWN ROOMS • 5 TIERS</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Cyber Arcade — 9x9 Sudoku Master Arena</h2>
        <p class="hero-sub">
            Unified 9x9 interactive grid! Play solo across 5 infinite tiers or host fair-start Multiplayer Rooms with pre-match countdowns (up to 10m), custom solve timers, and -45s hint penalties!
        </p>
    </div>
    """, unsafe_allow_html=True)

    db = load_sudoku_db()

    p_col1, p_col2, p_col3 = st.columns([1.5, 1.5, 1.5])
    with p_col1:
        player_name = st.text_input("🕹️ Arcade Player Callsign:", value=st.session_state.get("ctf_user") or default_username, key="sdk_player_in").strip() or "Agent_Player"
    p_stats = db["leaderboard"].get(player_name, {"sudoku_score": 0, "puzzles_solved": 0, "best_tier": 0})
    with p_col2:
        st.metric("🏆 Your Total Sudoku Score", f"{p_stats.get('sudoku_score', 0):,} PTS", f"Best Tier Cleared: Tier {p_stats.get('best_tier', 0)}")
    with p_col3:
        st.metric("✅ 9x9 Boards Solved", f"{p_stats.get('puzzles_solved', 0)} Boards", "Global Ranked")

    if "sudoku_state" not in st.session_state:
        sol0, puz0 = generate_sudoku_9x9(1, f"INIT_{player_name}_1_1")
        st.session_state.sudoku_state = {
            "tier": 1,
            "board_num": 1,
            "solution": sol0,
            "puzzle": puz0,
            "user_board": [r[:] for r in puz0],
            "hinted_cells": [],
            "completed": False,
            "surrendered": False,
            "last_score": 0,
            "start_ts": time.time()
        }

    gs = st.session_state.sudoku_state

    tab_solo, tab_duel, tab_lb = st.tabs([
        "🎮 1. Singleplayer 9x9 Sudoku Arena",
        "⚔️ 2. Multiplayer 1v1 & Co-op Rooms (Timed & Fair Countdown)",
        "🏆 3. Global Sudoku Leaderboard"
    ])

    # ==========================================================================
    # TAB 1: SINGLEPLAYER (1 BẢNG 9x9 DUY NHẤT VỪA NHÌN VỪA ĐIỀN ĐÁP ÁN)
    # ==========================================================================
    with tab_solo:
        tier_rewards = {1: 1000, 2: 2500, 3: 5000, 4: 10000, 5: 25000}

        c_sel1, c_sel2, c_sel3 = st.columns([2.2, 1, 1])
        with c_sel1:
            tier_label = st.selectbox(
                "🔥 Select 9x9 Difficulty Tier:",
                [
                    "Tier 1 — Beginner (28 Empty / 81 Cells | Base: 1,000 PTS)",
                    "Tier 2 — Explorer (36 Empty / 81 Cells | Base: 2,500 PTS)",
                    "Tier 3 — Challenger (44 Empty / 81 Cells | Base: 5,000 PTS)",
                    "Tier 4 — Master (52 Empty / 81 Cells | Base: 10,000 PTS)",
                    "Tier 5 — Grandmaster (58 Empty / 81 Cells | Base: 25,000 PTS)"
                ],
                index=gs["tier"] - 1
            )
            selected_tier = int(tier_label.split("Tier ")[1][0])
        with c_sel2:
            board_id = st.number_input("🔢 Board Matrix # (1 - 999,999):", min_value=1, max_value=999999, value=gs["board_num"])
        with c_sel3:
            st.write("")
            if st.button("🎲 New / Shuffle 9x9 Board", type="primary", use_container_width=True):
                new_b_num = random.randint(1, 999999) if (selected_tier == gs["tier"] and board_id == gs["board_num"]) else board_id
                seed_str = f"SUDOKU9X9_{player_name}_T{selected_tier}_B{new_b_num}_{time.time()}"
                sol, puz = generate_sudoku_9x9(selected_tier, seed_str)
                st.session_state.sudoku_state = {
                    "tier": selected_tier,
                    "board_num": new_b_num,
                    "solution": sol,
                    "puzzle": puz,
                    "user_board": [r[:] for r in puz],
                    "hinted_cells": [],
                    "completed": False,
                    "surrendered": False,
                    "last_score": 0,
                    "start_ts": time.time()
                }
                st.rerun()

        curr_tier = gs["tier"]
        base_pts = tier_rewards[curr_tier]
        hints_used_count = len(gs["hinted_cells"])
        hints_remaining = 5 - hints_used_count
        current_multiplier = max(0.25, 1.0 - (hints_used_count * 0.15))
        potential_pts = int(base_pts * current_multiplier)
        surrender_penalty = int(base_pts * 0.92)

        st.markdown(f"""
        <div class="ws-banner">
            <h4>🧩 Active 9x9 Matrix: <code>Tier {curr_tier} • Board #{gs['board_num']}</code> — Potential Reward: <b style="color:#34d399;">+{potential_pts:,} PTS</b></h4>
            <p>
                💡 <b>Hint Rule:</b> Up to <b>5 hints/board</b> (max 1 hint per cell, <b>-15% points</b> each • Used: <b>{hints_used_count}/5</b>). &nbsp;|&nbsp;
                🏳️ <b>Surrender Rule:</b> Revealing full solution deducts <b>92%</b> (<b>-{surrender_penalty:,} PTS</b>).
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Thanh chọn tọa độ Hint gọn gàng ngay phía trên bảng 9x9 duy nhất
        with st.container(border=True):
            hc1, hc2, hc3 = st.columns([1.2, 1.2, 2.2])
            with hc1:
                h_row = st.selectbox("🎯 Target Hint Row (R1–R9):", list(range(1, 10)), key="solo_hr")
            with hc2:
                h_col = st.selectbox("🎯 Target Hint Col (C1–C9):", list(range(1, 10)), key="solo_hc")
            with hc3:
                st.write("")
                can_hint = (not gs["completed"]) and (hints_remaining > 0)
                if st.button(f"💡 Reveal Cell (R{h_row}, C{h_col}) [-15% Score • {hints_remaining} Hints Left]", use_container_width=True, disabled=not can_hint):
                    r_idx, c_idx = h_row - 1, h_col - 1
                    if gs["puzzle"][r_idx][c_idx] != 0:
                        st.warning(f"⚠️ Cell (R{h_row}, C{h_col}) is already a fixed starting clue!")
                    elif (r_idx, c_idx) in [tuple(x) for x in gs["hinted_cells"]]:
                        st.warning(f"⚠️ You already used a hint on Cell (R{h_row}, C{h_col})!")
                    else:
                        gs["user_board"][r_idx][c_idx] = gs["solution"][r_idx][c_idx]
                        gs["hinted_cells"].append((r_idx, c_idx))
                        st.session_state[f"solo_{curr_tier}_{gs['board_num']}_r{r_idx}_c{c_idx}"] = str(gs["solution"][r_idx][c_idx])
                        st.rerun()

        if gs["completed"] and not gs["surrendered"]:
            st.success(f"🎉 **VICTORY! You solved this 9x9 Sudoku Matrix and earned +{gs['last_score']:,} PTS!**")
        elif gs["surrendered"]:
            st.error(f"🏳️ **BOARD SURRENDERED!** Full 9x9 solution is displayed below (-{surrender_penalty:,} PTS penalty applied).")

        # HIỂN THỊ 1 BẢNG 9x9 TƯƠNG TÁC DUY NHẤT
        render_single_unified_9x9_board(
            gs["puzzle"],
            gs["user_board"],
            gs["hinted_cells"],
            key_prefix=f"solo_{curr_tier}_{gs['board_num']}",
            disabled=gs["completed"]
        )

        st.divider()
        b_col1, b_col2, b_col3 = st.columns(3)
        with b_col1:
            if st.button("✅ Verify & Submit 9x9 Solution", type="primary", use_container_width=True, disabled=gs["completed"]):
                empty_count = sum(1 for r in range(9) for c in range(9) if gs["user_board"][r][c] == 0)
                conflicts = check_board_conflicts(gs["user_board"])
                if conflicts:
                    st.error("❌ **Rule Conflict:** " + " | ".join(conflicts[:3]))
                elif empty_count > 0:
                    st.warning(f"⚠️ You still have **{empty_count} empty cells** remaining!")
                elif gs["user_board"] == gs["solution"]:
                    gs["completed"] = True
                    gs["last_score"] = potential_pts
                    lb = db["leaderboard"]
                    if player_name not in lb:
                        lb[player_name] = {"sudoku_score": 0, "puzzles_solved": 0, "best_tier": 0}
                    lb[player_name]["sudoku_score"] += potential_pts
                    lb[player_name]["puzzles_solved"] += 1
                    lb[player_name]["best_tier"] = max(lb[player_name].get("best_tier", 0), curr_tier)
                    save_sudoku_db(db)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Some numbers do not match the solution! Double-check your logic.")

        with b_col2:
            if st.button("🧹 Clear My Entered Numbers", use_container_width=True, disabled=gs["completed"]):
                hint_set = set(tuple(x) for x in gs["hinted_cells"])
                for r in range(9):
                    for c in range(9):
                        if gs["puzzle"][r][c] == 0 and (r, c) not in hint_set:
                            gs["user_board"][r][c] = 0
                            st.session_state[f"solo_{curr_tier}_{gs['board_num']}_r{r}_c{c}"] = ""
                st.rerun()

        with b_col3:
            if st.button(f"🏳️ Surrender & Show Solution (-{surrender_penalty:,} PTS)", use_container_width=True, disabled=gs["completed"]):
                gs["user_board"] = [r[:] for r in gs["solution"]]
                gs["completed"] = True
                gs["surrendered"] = True
                lb = db["leaderboard"]
                if player_name not in lb:
                    lb[player_name] = {"sudoku_score": 0, "puzzles_solved": 0, "best_tier": 0}
                lb[player_name]["sudoku_score"] -= surrender_penalty
                save_sudoku_db(db)
                st.rerun()

    # ==========================================================================
    # TAB 2: MULTIPLAYER ROOMS (TUỲ CHỈNH THỜI GIAN, SỐ HINT -45s/LẦN & ĐẾM NGƯỢC HIỂN THỊ ĐỀ TỐI ĐA 10P)
    # ==========================================================================
    with tab_duel:
        st.markdown("""
        <div class="ws-banner">
            <h4>⚔️ Fair-Start 1v1 & Multiplayer Sudoku Tournament Rooms</h4>
            <p>
                Configure <b>Solve Duration (e.g. 10m, 15m, 20m)</b>, <b>Max Hints Allowed (0–5, each hint deducts 45s of solve time & 15% score)</b>, and a <b>Pre-Match Countdown (up to 600s / 10 mins)</b> so you can share the Room ID before the board is revealed to everyone simultaneously!
            </p>
        </div>
        """, unsafe_allow_html=True)

        rooms = db.get("rooms", {})
        r_col1, r_col2 = st.columns([2.2, 1])
        with r_col1:
            room_sel = st.selectbox("📂 Select Active Duel Room or Create New:", ["➕ Create New Sudoku Duel Room"] + list(rooms.keys()))
        with r_col2:
            st.write("")
            if st.button("🔄 Refresh Room / Timer Status", use_container_width=True):
                st.rerun()

        if room_sel == "➕ Create New Sudoku Duel Room":
            with st.container(border=True):
                st.markdown("##### ⚙️ Configure New Multiplayer / 1v1 Match Rules")
                cr1, cr2, cr3 = st.columns(3)
                with cr1:
                    new_code = st.text_input("🔑 Room ID / Match Code:", placeholder="e.g. HCMUS-ROOM-01")
                    duel_tier = st.selectbox("🔥 Difficulty Tier (1–5):", [1, 2, 3, 4, 5], index=1)
                with cr2:
                    solve_mins = st.selectbox("⏱️ Solve Time Limit (Minutes):", [5, 10, 15, 20, 25, 30, 45, 60], index=2)
                    max_room_hints = st.slider("💡 Max Hints Allowed (Each hint = -45s & -15% pts):", min_value=0, max_value=5, value=3)
                with cr3:
                    reveal_delay_sec = st.number_input(
                        "⏳ Pre-Match Countdown Before Puzzle Appears (Seconds, Max 600s = 10 mins):",
                        min_value=0, max_value=600, value=60, step=10,
                        help="During this countdown, the board is hidden so you can send the Room ID to friends for a 100% fair start!"
                    )

                if st.button("🚀 Create & Start Room Countdown", type="primary", use_container_width=True):
                    code_clean = new_code.strip()
                    if not code_clean:
                        st.error("Please enter a valid Room ID!")
                    elif code_clean in rooms:
                        st.warning("This Room ID already exists! Select it from the dropdown above.")
                    else:
                        now_ts = int(time.time())
                        sol_r, puz_r = generate_sudoku_9x9(duel_tier, f"ROOM_{code_clean}_{now_ts}")
                        rooms[code_clean] = {
                            "tier": duel_tier,
                            "creator": player_name,
                            "created_at": datetime.now(timezone.utc).strftime("%H:%M:%S UTC"),
                            "created_ts": now_ts,
                            "reveal_delay_sec": int(reveal_delay_sec),
                            "reveal_ts": now_ts + int(reveal_delay_sec),
                            "solve_duration_sec": int(solve_mins * 60),
                            "max_hints": int(max_room_hints),
                            "solution": sol_r,
                            "puzzle": puz_r,
                            "players": {
                                player_name: {"status": "⏳ In Lobby / Solving", "score": 0, "time_sec": 0, "hints_used": 0}
                            }
                        }
                        db["rooms"] = rooms
                        save_sudoku_db(db)
                        st.success(f"✅ Room **`{code_clean}`** created! Select it from the dropdown above to enter the lobby!")
                        st.rerun()

        else:
            r_data = rooms[room_sel]
            r_tier = r_data.get("tier", 1)
            r_creator = r_data.get("creator", "Host")
            r_max_hints = r_data.get("max_hints", 5)
            r_solve_sec = r_data.get("solve_duration_sec", 900)
            r_reveal_ts = r_data.get("reveal_ts", 0)
            r_players = r_data.get("players", {})

            # Tự động ghi danh người chơi vào phòng nếu chưa có
            if player_name not in r_players:
                r_players[player_name] = {"status": "⏳ Joined Room", "score": 0, "time_sec": 0, "hints_used": 0}
                db["rooms"][room_sel]["players"] = r_players
                save_sudoku_db(db)

            now_ts = int(time.time())

            # Cài đặt lại đếm ngược chờ đề xuất hiện (Dành riêng cho Chủ phòng nếu muốn chỉnh lại)
            if player_name == r_creator:
                with st.expander("👑 Host Controls: Set / Reset Puzzle Reveal Countdown (Max 10 mins = 600s)"):
                    hc_col1, hc_col2 = st.columns([2, 1])
                    with hc_col1:
                        new_delay = st.number_input("⏳ Reveal puzzle after how many seconds? (0–600s):", min_value=0, max_value=600, value=60, key=f"host_delay_{room_sel}")
                    with hc_col2:
                        st.write("")
                        if st.button("⏱️ Start New Countdown", use_container_width=True):
                            r_data["reveal_ts"] = int(time.time()) + int(new_delay)
                            db["rooms"][room_sel] = r_data
                            save_sudoku_db(db)
                            st.rerun()

            # KIỂM TRA TRẠNG THÁI ĐẾM NGƯỢC TRƯỚC KHI HIỂN THỊ ĐỀ (FAIR-START LOBBY)
            if now_ts < r_reveal_ts:
                wait_rem = r_reveal_ts - now_ts
                wm, ws = divmod(wait_rem, 60)
                st.warning(
                    f"### ⏳ FAIR-START LOBBY COUNTDOWN: Puzzle will be revealed in **`{wm:02d}m {ws:02d}s`** ({wait_rem} seconds)!\n\n"
                    f"- 📢 **Share Room ID with your friends now:** **`{room_sel}`**\n"
                    f"- ⚙️ **Room Rules:** Tier `{r_tier}` &nbsp;|&nbsp; Solve Time Limit: **`{r_solve_sec // 60} mins`** &nbsp;|&nbsp; "
                    f"Max Hints: **`{r_max_hints}`** *(Each hint deducts **-45s** from your timer & **-15%** score)*.\n"
                    f"- 🔒 The 9x9 Sudoku board is currently hidden for everyone (including Host `{r_creator}`) to guarantee 100% fairness!"
                )
                if st.button("🔄 Check Countdown Now", type="primary"):
                    st.rerun()
            else:
                # ĐÃ HẾT ĐẾM NGƯỢC -> MỞ KHÓA BẢNG 9x9 DUY NHẤT NGAY TRONG PHÒNG ĐẤU
                r_session_key = f"room_play_{room_sel}_{player_name}"
                if r_session_key not in st.session_state:
                    st.session_state[r_session_key] = {
                        "user_board": [row[:] for row in r_data["puzzle"]],
                        "hinted_cells": [],
                        "completed": False
                    }
                rp_state = st.session_state[r_session_key]
                used_h = len(rp_state["hinted_cells"])
                rem_h = max(0, r_max_hints - used_h)

                # Tính thời gian giải còn lại (Đã trừ 45 giây cho mỗi lần dùng Hint!)
                elapsed_solve = now_ts - r_reveal_ts
                hint_time_penalty = used_h * 45
                remaining_solve_sec = r_solve_sec - elapsed_solve - hint_time_penalty
                time_expired = (remaining_solve_sec <= 0) and (not rp_state["completed"])

                rm_min, rm_sec = divmod(max(0, remaining_solve_sec), 60)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("📡 Active Room ID", room_sel, f"Host: {r_creator}")
                m2.metric("⏱️ Remaining Solve Time", f"{rm_min:02d}:{rm_sec:02d}", f"-{hint_time_penalty}s Hint Penalty")
                m3.metric("💡 Room Hints Left", f"{rem_h} / {r_max_hints}", "-45s & -15% pts/hint")
                m4.metric("🔥 Match Tier", f"Tier {r_tier}", f"Total Limit: {r_solve_sec//60}m")

                if time_expired:
                    st.error("⏰ **TIME'S UP!** Your solve timer (including `-45s` hint penalties) has reached `00:00`!")
                    r_players[player_name]["status"] = "⏰ Time Expired"
                    db["rooms"][room_sel]["players"] = r_players
                    save_sudoku_db(db)

                # Công cụ dùng Hint trong phòng đấu (-45s thời gian & -15% điểm)
                with st.container(border=True):
                    rh1, rh2, rh3 = st.columns([1.2, 1.2, 2.2])
                    with rh1:
                        rh_r = st.selectbox("Row (R1–R9):", list(range(1, 10)), key=f"rm_hr_{room_sel}")
                    with rh2:
                        rh_c = st.selectbox("Col (C1–C9):", list(range(1, 10)), key=f"rm_hc_{room_sel}")
                    with rh3:
                        st.write("")
                        can_rm_hint = (not rp_state["completed"]) and (not time_expired) and (rem_h > 0)
                        if st.button(f"💡 Use Room Hint (R{rh_r}, C{rh_c}) [-45s Time & -15% Score]", use_container_width=True, disabled=not can_rm_hint):
                            ri, ci = rh_r - 1, rh_c - 1
                            if r_data["puzzle"][ri][ci] != 0:
                                st.warning("That cell is already a fixed clue!")
                            elif (ri, ci) in [tuple(x) for x in rp_state["hinted_cells"]]:
                                st.warning("You already used a hint on this cell!")
                            else:
                                rp_state["user_board"][ri][ci] = r_data["solution"][ri][ci]
                                rp_state["hinted_cells"].append((ri, ci))
                                st.session_state[f"rm_{room_sel}_r{ri}_c{ci}"] = str(r_data["solution"][ri][ci])
                                r_players[player_name]["hints_used"] = len(rp_state["hinted_cells"])
                                db["rooms"][room_sel]["players"] = r_players
                                save_sudoku_db(db)
                                st.rerun()

                # Hiển thị 1 bảng 9x9 duy nhất ngay trong phòng thi đấu
                render_single_unified_9x9_board(
                    r_data["puzzle"],
                    rp_state["user_board"],
                    rp_state["hinted_cells"],
                    key_prefix=f"rm_{room_sel}",
                    disabled=(rp_state["completed"] or time_expired)
                )

                if st.button("🏆 Submit My Room 9x9 Solution", type="primary", use_container_width=True, disabled=(rp_state["completed"] or time_expired)):
                    if rp_state["user_board"] == r_data["solution"]:
                        rp_state["completed"] = True
                        base_pts = {1: 1000, 2: 2500, 3: 5000, 4: 10000, 5: 25000}[r_tier]
                        mult = max(0.25, 1.0 - (used_h * 0.15))
                        final_pts = int(base_pts * mult)
                        r_players[player_name] = {
                            "status": "✅ FINISHED!",
                            "score": final_pts,
                            "time_sec": elapsed_solve + hint_time_penalty,
                            "hints_used": used_h
                        }
                        db["rooms"][room_sel]["players"] = r_players
                        lb = db["leaderboard"]
                        if player_name not in lb:
                            lb[player_name] = {"sudoku_score": 0, "puzzles_solved": 0, "best_tier": 0}
                        lb[player_name]["sudoku_score"] += final_pts
                        lb[player_name]["puzzles_solved"] += 1
                        lb[player_name]["best_tier"] = max(lb[player_name].get("best_tier", 0), r_tier)
                        save_sudoku_db(db)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Your 9x9 board is not complete or contains errors!")

            st.divider()
            st.markdown("##### 🏁 Live Room Scoreboard")
            for p_id, p_info in r_players.items():
                st.markdown(
                    f"- 🕵️ **`{p_id}`** — Status: **{p_info.get('status', 'Solving')}** | "
                    f"Score: **`{p_info.get('score', 0):,} PTS`** | "
                    f"Hints Used: `{p_info.get('hints_used', 0)}/{r_max_hints}` (`-{p_info.get('hints_used', 0)*45}s`) | "
                    f"Effective Time: `{p_info.get('time_sec', 0)}s`"
                )

    # ==========================================================================
    # TAB 3: BẢNG XẾP HẠNG SUDOKU TOÀN CẦU
    # ==========================================================================
    with tab_lb:
        st.markdown("""
        <div class="ws-banner">
            <h4>🏆 Global 9x9 Sudoku Leaderboard</h4>
            <p>Public rankings across all Sudoku players. Higher tiers award up to 25,000 PTS per board!</p>
        </div>
        """, unsafe_allow_html=True)

        lb_all = db.get("leaderboard", {})
        sorted_sdk = sorted(lb_all.items(), key=lambda x: x[1].get("sudoku_score", 0), reverse=True)

        for idx, (u_name, u_val) in enumerate(sorted_sdk, start=1):
            sc = u_val.get("sudoku_score", 0)
            slv = u_val.get("puzzles_solved", 0)
            bt = u_val.get("best_tier", 1)
            medal = "🥇" if idx == 1 else ("🥈" if idx == 2 else ("🥉" if idx == 3 else f"#{idx}"))
            me_badge = " *(You)*" if u_name == player_name else ""

            c1, c2, c3, c4 = st.columns([2.2, 1.4, 1.2, 1.2])
            c1.markdown(f"**{medal} &nbsp; `{u_name}`**{me_badge}")
            c2.markdown(f"🏆 **{sc:,} PTS**")
            c3.markdown(f"✅ `{slv}` boards")
            c4.markdown(f"🔥 Max Tier: `Tier {bt}`")

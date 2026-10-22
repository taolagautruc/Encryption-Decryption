import streamlit as st
import random
import time
import json
import os
import hashlib
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
    """
    Sinh bàn cờ Sudoku 9x9 chuẩn toán học (9 hàng x 9 cột, chia làm 9 khối 3x3).
    Hỗ trợ seed cố định để hàng triệu màn chơi luôn độc nhất và phòng Solo 1v1 có cùng đề bài.
    """
    rng = random.Random(seed_val) if seed_val else random.Random()
    base = 3
    side = 9  # Chuẩn 9x9 (81 ô)

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

    # Bảng đáp án hoàn chỉnh 9x9
    solution = [[nums[pattern(r, c)] for c in cols] for r in rows]

    # Số ô trống cần điền theo 5 Tier độ khó (Tổng 81 ô)
    removals_map = {
        1: 28,  # Tier 1 (Beginner): 28 ô trống, 53 ô gợi ý sẵn
        2: 36,  # Tier 2 (Explorer): 36 ô trống, 45 ô gợi ý sẵn
        3: 44,  # Tier 3 (Challenger): 44 ô trống, 37 ô gợi ý sẵn
        4: 52,  # Tier 4 (Master): 52 ô trống, 29 ô gợi ý sẵn
        5: 58   # Tier 5 (Grandmaster): 58 ô trống, chỉ còn 23 ô gợi ý sẵn!
    }
    removals = removals_map.get(tier, 36)

    puzzle = [row[:] for row in solution]
    all_cells = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(all_cells)

    for i in range(removals):
        r, c = all_cells[i]
        puzzle[r][c] = 0

    return solution, puzzle

def render_visual_9x9_grid_html(puzzle: list[list[int]], user_board: list[list[int]], hinted_cells: list) -> str:
    """
    Vẽ bàn cờ Sudoku 9x9 tuyệt đẹp với đường viền đậm phân tách rõ 9 khối vuông 3x3 (Subgrids).
    - Ô đề bài gốc: Chữ xanh dương sáng (#60a5fa), nền tối (#0f172a).
    - Ô đã dùng Hint mở khóa: Chữ vàng kim (#fbbf24), viền vàng.
    - Ô người chơi tự điền: Chữ xanh ngọc (#34d399).
    - Ô còn trống: Dấu chấm mờ (·).
    """
    html = """
    <style>
        .sudoku-wrapper {
            display: flex;
            justify-content: center;
            margin: 14px 0 20px 0;
        }
        table.sudoku-9x9 {
            border-collapse: collapse;
            border: 3px solid #3b82f6;
            background: #090d16;
            box-shadow: 0 0 30px rgba(59, 130, 246, 0.25);
        }
        table.sudoku-9x9 th {
            background: #111827;
            color: #64748b;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 6px 10px;
            border: 1px solid #1e293b;
            text-align: center;
        }
        table.sudoku-9x9 td {
            width: 46px;
            height: 46px;
            text-align: center;
            vertical-align: middle;
            font-size: 1.25rem;
            font-weight: 800;
            font-family: 'Courier New', monospace;
            border: 1px solid #1e293b;
            transition: all 0.15s ease;
        }
        /* Đường viền đậm chia 9 khối 3x3 (Sau cột 3, cột 6 và sau hàng 3, hàng 6) */
        table.sudoku-9x9 td.border-right-3x3 {
            border-right: 3px solid #3b82f6 !important;
        }
        table.sudoku-9x9 tr.border-bottom-3x3 td {
            border-bottom: 3px solid #3b82f6 !important;
        }
        .cell-fixed {
            background-color: #111827;
            color: #60a5fa;
        }
        .cell-hinted {
            background-color: rgba(245, 158, 11, 0.16);
            color: #fbbf24;
            text-shadow: 0 0 8px rgba(251, 191, 36, 0.5);
        }
        .cell-user {
            background-color: rgba(16, 185, 129, 0.14);
            color: #34d399;
            text-shadow: 0 0 8px rgba(52, 211, 153, 0.4);
        }
        .cell-empty {
            background-color: #090d16;
            color: #334155;
        }
    </style>
    <div class="sudoku-wrapper">
        <table class="sudoku-9x9">
            <thead>
                <tr>
                    <th>R\\C</th>
                    <th>C1</th><th>C2</th><th style="border-right:3px solid #3b82f6;">C3</th>
                    <th>C4</th><th>C5</th><th style="border-right:3px solid #3b82f6;">C6</th>
                    <th>C7</th><th>C8</th><th>C9</th>
                </tr>
            </thead>
            <tbody>
    """
    hint_set = set(tuple(x) for x in hinted_cells)
    for r in range(9):
        row_class = "border-bottom-3x3" if r in [2, 5] else ""
        html += f"<tr class='{row_class}'>"
        html += f"<th>R{r+1}</th>"
        for c in range(9):
            col_border = "border-right-3x3" if c in [2, 5] else ""
            val = user_board[r][c]
            if puzzle[r][c] != 0:
                cell_cls = "cell-fixed"
                disp = str(puzzle[r][c])
            elif (r, c) in hint_set:
                cell_cls = "cell-hinted"
                disp = str(val)
            elif val != 0:
                cell_cls = "cell-user"
                disp = str(val)
            else:
                cell_cls = "cell-empty"
                disp = "·"
            html += f"<td class='{cell_cls} {col_border}'>{disp}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"
    return html

def check_board_conflicts(board: list[list[int]]) -> list[str]:
    """Kiểm tra xem người chơi có điền trùng số trên cùng Hàng, Cột, hoặc Khối 3x3 không."""
    errors = []
    # Kiểm tra 9 hàng
    for r in range(9):
        nums = [x for x in board[r] if x != 0]
        if len(nums) != len(set(nums)):
            errors.append(f"Row R{r+1} has duplicate numbers!")
    # Kiểm tra 9 cột
    for c in range(9):
        nums = [board[r][c] for r in range(9) if board[r][c] != 0]
        if len(nums) != len(set(nums)):
            errors.append(f"Column C{c+1} has duplicate numbers!")
    # Kiểm tra 9 khối vuông 3x3
    for br in range(3):
        for bc in range(3):
            nums = []
            for r in range(br * 3, br * 3 + 3):
                for c in range(bc * 3, bc * 3 + 3):
                    if board[r][c] != 0:
                        nums.append(board[r][c])
            if len(nums) != len(set(nums)):
                errors.append(f"3x3 Box ({br+1},{bc+1}) has duplicate numbers!")
    return errors

def render_sudoku_arcade(default_username: str = "taolagautruc"):
    st.markdown("""
    <div class="hero-box" style="padding: 24px 32px; margin-bottom: 20px; background: linear-gradient(135deg, #090d16 0%, #1e1b4b 50%, #312e81 100%); border: 1px solid #6366f1;">
        <div class="hero-badge" style="background: rgba(99, 102, 241, 0.2); color: #818cf8; border-color: #6366f1;">🧩 INFINITE 9x9 SUDOKU MATRIX • 5 DIFFICULTY TIERS • 1V1 & CO-OP ROOMS</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Cyber Arcade — 9x9 Sudoku Master Arena</h2>
        <p class="hero-sub">
            Play millions of procedural 9x9 Sudoku boards across 5 difficulty tiers! Use targeted cell hints (max 5 hints/board, -15% score each, 1 hint per cell), or reveal full solution (-92% penalty). Compete on the Global Leaderboard or race friends in 1v1 Rooms!
        </p>
    </div>
    """, unsafe_allow_html=True)

    db = load_sudoku_db()

    # Thanh định danh người chơi trong sảnh Game
    p_col1, p_col2, p_col3 = st.columns([1.5, 1.5, 1.5])
    with p_col1:
        player_name = st.text_input("🕹️ Arcade Player Callsign:", value=st.session_state.get("ctf_user") or default_username, key="sdk_player_in").strip() or "Agent_Player"
    
    p_stats = db["leaderboard"].get(player_name, {"sudoku_score": 0, "puzzles_solved": 0, "best_tier": 0})
    with p_col2:
        st.metric("🏆 Your Total Sudoku Score", f"{p_stats.get('sudoku_score', 0):,} PTS", f"Best Tier Cleared: Tier {p_stats.get('best_tier', 0)}")
    with p_col3:
        st.metric("✅ 9x9 Boards Solved", f"{p_stats.get('puzzles_solved', 0)} Boards", "Global Ranked")

    # Khởi tạo trạng thái ván cờ 9x9
    if "sudoku_state" not in st.session_state:
        sol0, puz0 = generate_sudoku_9x9(1, f"INIT_{player_name}_1_1")
        st.session_state.sudoku_state = {
            "tier": 1,
            "board_num": 1,
            "solution": sol0,
            "puzzle": puz0,
            "user_board": [r[:] for r in puz0],
            "hinted_cells": [],   # Danh sách tọa độ (r, c) đã dùng hint (mỗi ô tối đa 1 lần, tối đa 5 ô)
            "completed": False,
            "surrendered": False,
            "last_score": 0,
            "start_ts": time.time()
        }

    gs = st.session_state.sudoku_state

    tab_solo, tab_duel, tab_lb = st.tabs([
        "🎮 1. Infinite 9x9 Sudoku Arena (5 Tiers)",
        "⚔️ 2. Multiplayer 1v1 & Co-op Rooms",
        "🏆 3. Global Sudoku Leaderboard"
    ])

    # ==========================================================================
    # TAB 1: CHẾ ĐỘ CHƠI 9x9 VÔ TẬN (5 TIERS, 5 HINTS -15%/LẦN, SURRENDER -92%)
    # ==========================================================================
    with tab_solo:
        tier_rewards = {1: 1000, 2: 2500, 3: 5000, 4: 10000, 5: 25000}
        
        c_sel1, c_sel2, c_sel3 = st.columns([2.2, 1, 1])
        with c_sel1:
            tier_label = st.selectbox(
                "🔥 Select 9x9 Difficulty Tier (Higher Tier = More Empty Cells & Higher Points):",
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
            if st.button("🎲 Load / Shuffle New 9x9 Board", type="primary", use_container_width=True):
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
        # Mỗi lần dùng Hint trừ 15% điểm của màn đó (Tối đa 5 lần = -75%, còn lại 25% điểm)
        current_multiplier = max(0.25, 1.0 - (hints_used_count * 0.15))
        potential_pts = int(base_pts * current_multiplier)
        surrender_penalty = int(base_pts * 0.92)

        # Thanh thông báo quy tắc tính điểm của màn hiện tại
        st.markdown(f"""
        <div class="ws-banner">
            <h4>🧩 Active 9x9 Matrix: <code>Tier {curr_tier} • Board #{gs['board_num']}</code> — Potential Reward: <b style="color:#34d399;">+{potential_pts:,} PTS</b> <span style="font-size:0.85rem;color:#94a3b8;">(Base: {base_pts:,} PTS)</span></h4>
            <p>
                💡 <b>Hint Rules:</b> You can reveal up to <b>5 cells per board</b> (max 1 hint per cell). Each hint deducts <b>15%</b> of this board's score (Used: <b>{hints_used_count}/5</b> -> <b>-{hints_used_count*15}%</b>).<br>
                🏳️ <b>Surrender Rule:</b> Clicking <i>"Surrender & Reveal 9x9 Solution"</i> shows the full answer key immediately but deducts <b>92%</b> (<b>-{surrender_penalty:,} PTS</b> penalty) from your total score!
            </p>
        </div>
        """, unsafe_allow_html=True)

        if gs["completed"] and not gs["surrendered"]:
            st.success(f"🎉 **VICTORY! You solved this 9x9 Sudoku Matrix and earned +{gs['last_score']:,} PTS!** Click 'Load / Shuffle New 9x9 Board' above to play the next one!")
        elif gs["surrendered"]:
            st.error(f"🏳️ **BOARD SURRENDERED!** Full 9x9 solution is displayed below (-{surrender_penalty:,} PTS penalty applied).")

        # Chia 2 cột: Cột Trái là Bàn cờ Visual 9x9 (có viền 3x3 đậm), Cột Phải là Bảng Nhập Số & Chọn Ô Gợi Ý
        board_col, control_col = st.columns([1.35, 1.25])

        with board_col:
            st.markdown("##### 🎯 Visual 9x9 Sudoku Grid (With 3×3 Subgrid Borders)")
            st.caption("🔵 **Blue** = Fixed Clues &nbsp;|&nbsp; 🟢 **Green** = Your Input &nbsp;|&nbsp; 🟡 **Gold** = Hinted Cell (-15%) &nbsp;|&nbsp; **·** = Empty")
            st.markdown(
                render_visual_9x9_grid_html(gs["puzzle"], gs["user_board"], gs["hinted_cells"]),
                unsafe_allow_html=True
            )

        with control_col:
            # --- CÔNG CỤ 1: MỞ KHÓA GỢI Ý ĐÍCH DANH TỪNG Ô (TỐI ĐA 5 LẦN, MỖI Ô 1 LẦN, -15%/LẦN) ---
            st.markdown("##### 💡 Targeted Cell Hint (Max 5 Hints • -15% Score Each)")
            with st.container(border=True):
                hc1, hc2, hc3 = st.columns([1, 1, 1.4])
                with hc1:
                    h_row = st.selectbox("Row (R1–R9):", list(range(1, 10)), key="hint_r_sel")
                with hc2:
                    h_col = st.selectbox("Col (C1–C9):", list(range(1, 10)), key="hint_c_sel")
                with hc3:
                    st.write("")
                    can_hint = (not gs["completed"]) and (hints_remaining > 0)
                    if st.button(f"💡 Reveal (R{h_row}, C{h_col}) [{hints_remaining} left]", use_container_width=True, disabled=not can_hint):
                        r_idx, c_idx = h_row - 1, h_col - 1
                        if gs["puzzle"][r_idx][c_idx] != 0:
                            st.warning(f"⚠️ Cell (R{h_row}, C{h_col}) is already a fixed starting clue!")
                        elif (r_idx, c_idx) in [tuple(x) for x in gs["hinted_cells"]]:
                            st.warning(f"⚠️ You already used a hint on Cell (R{h_row}, C{h_col})! (Max 1 hint per cell).")
                        else:
                            gs["user_board"][r_idx][c_idx] = gs["solution"][r_idx][c_idx]
                            gs["hinted_cells"].append((r_idx, c_idx))
                            st.toast(f"💡 Revealed R{h_row}C{c_idx+1} = {gs['solution'][r_idx][c_idx]} (-15% score)", icon="💡")
                            st.rerun()

            # --- CÔNG CỤ 2: LƯỚI NHẬP SỐ 9x9 TƯƠNG TÁC ---
            st.markdown("##### ✍️ Interactive 9x9 Number Pad (Type 1–9, or 0 to clear)")
            puz = gs["puzzle"]
            ub = gs["user_board"]
            hint_coords = set(tuple(x) for x in gs["hinted_cells"])

            # Hiển thị 9 hàng x 9 cột ô nhập gọn gàng
            for r in range(9):
                if r in [3, 6]:
                    st.markdown("<hr style='margin:4px 0; border:1px solid #3b82f6;'>", unsafe_allow_html=True)
                row_cols = st.columns(9)
                for c in range(9):
                    with row_cols[c]:
                        is_fixed = (puz[r][c] != 0)
                        is_hinted = ((r, c) in hint_coords)
                        if is_fixed:
                            st.markdown(
                                f"<div style='text-align:center;background:#1e293b;color:#60a5fa;padding:6px 0;border-radius:4px;font-weight:800;font-size:0.9rem;'>{puz[r][c]}</div>",
                                unsafe_allow_html=True
                            )
                        elif is_hinted:
                            st.markdown(
                                f"<div style='text-align:center;background:#451a03;color:#fbbf24;padding:6px 0;border-radius:4px;font-weight:800;font-size:0.9rem;border:1px solid #f59e0b;'>{ub[r][c]}</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            new_v = st.number_input(
                                f"R{r+1}C{c+1}",
                                min_value=0, max_value=9,
                                value=int(ub[r][c]),
                                key=f"sdk_in_{gs['tier']}_{gs['board_num']}_{r}_{c}",
                                label_visibility="collapsed",
                                disabled=gs["completed"]
                            )
                            ub[r][c] = new_v

        st.divider()
        # Hàng nút Kiểm tra Đáp án, Xóa nháp và Đầu hàng (-92%)
        b_col1, b_col2, b_col3 = st.columns(3)
        with b_col1:
            if st.button("✅ Verify & Submit 9x9 Solution", type="primary", use_container_width=True, disabled=gs["completed"]):
                empty_count = sum(1 for r in range(9) for c in range(9) if gs["user_board"][r][c] == 0)
                conflicts = check_board_conflicts(gs["user_board"])
                if conflicts:
                    st.error("❌ **Sudoku Rule Conflict Detected:** " + " | ".join(conflicts[:3]))
                elif empty_count > 0:
                    st.warning(f"⚠️ You still have **{empty_count} empty cells** (`·`) remaining! Fill all 81 cells to complete the board.")
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
                    st.error("❌ Some numbers do not match the valid solution! Use a Hint or double-check your logic.")

        with b_col2:
            if st.button("🧹 Clear My Entered Numbers (Keep Clues & Hints)", use_container_width=True, disabled=gs["completed"]):
                hint_set = set(tuple(x) for x in gs["hinted_cells"])
                for r in range(9):
                    for c in range(9):
                        if gs["puzzle"][r][c] == 0 and (r, c) not in hint_set:
                            gs["user_board"][r][c] = 0
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
    # TAB 2: PHÒNG ĐẤU SOLO 1v1 & CHƠI NHÓM (MULTIPLAYER ROOM DUELS)
    # ==========================================================================
    with tab_duel:
        st.markdown("""
        <div class="ws-banner">
            <h4>⚔️ 1v1 Speedrun Duel & Multiplayer Room Arena</h4>
            <p>Create a Room Code (or join your friend's Room Code) so everyone receives the <b>exact same 9x9 Sudoku Matrix</b>! Race to see who solves it fastest with the highest score!</p>
        </div>
        """, unsafe_allow_html=True)

        rooms = db.get("rooms", {})
        r_col1, r_col2 = st.columns([2, 1])
        with r_col1:
            room_sel = st.selectbox("📂 Select Active Duel Room or Create New:", ["➕ Create New Sudoku Duel Room"] + list(rooms.keys()))
        with r_col2:
            st.write("")
            if st.button("🔄 Refresh Room Status", use_container_width=True):
                st.rerun()

        if room_sel == "➕ Create New Sudoku Duel Room":
            cr1, cr2, cr3 = st.columns([1.5, 1, 1])
            with cr1:
                new_code = st.text_input("🔑 Room Code / Match Name:", placeholder="e.g. HCMUS-SOLO-99")
            with cr2:
                duel_tier = st.selectbox("🔥 Match Difficulty Tier:", [1, 2, 3, 4, 5], index=0)
            with cr3:
                st.write("")
                if st.button("🚀 Create & Launch Room", type="primary", use_container_width=True):
                    code_clean = new_code.strip()
                    if not code_clean:
                        st.error("Please enter a Room Code!")
                    elif code_clean in rooms:
                        st.warning("Room Code already exists! Select it from the dropdown above.")
                    else:
                        sol_r, puz_r = generate_sudoku_9x9(duel_tier, f"ROOM_{code_clean}_{time.time()}")
                        rooms[code_clean] = {
                            "tier": duel_tier,
                            "creator": player_name,
                            "created_at": datetime.now(timezone.utc).strftime("%H:%M UTC"),
                            "solution": sol_r,
                            "puzzle": puz_r,
                            "players": {
                                player_name: {"status": "⏳ Solving...", "score": 0, "time_sec": 0}
                            }
                        }
                        db["rooms"] = rooms
                        save_sudoku_db(db)
                        st.success(f"✅ Room **`{code_clean}`** created! Select it from the dropdown above to start!")
                        st.rerun()
        else:
            r_data = rooms[room_sel]
            r_tier = r_data["tier"]
            r_players = r_data.get("players", {})

            st.markdown(f"#### ⚔️ Duel Room: `{room_sel}` (Tier {r_tier} • Host: `{r_data['creator']}` • Created: {r_data.get('created_at', '')})")

            # Hiển thị bảng xếp hạng trực tiếp của các thành viên trong phòng
            st.markdown("##### 🏁 Live Room Scoreboard")
            for p_id, p_info in r_players.items():
                st.markdown(f"- 🕵️ **`{p_id}`** — Status: **{p_info['status']}** | Score: **`{p_info['score']:,} PTS`** | Time: `{p_info['time_sec']}s`")

            st.write("")
            dl_c1, dl_c2 = st.columns(2)
            with dl_c1:
                if st.button("📥 Load This Room's 9x9 Board Into My Arena (Tab 1)", type="primary", use_container_width=True):
                    r_players[player_name] = {"status": "🔥 Solving Now...", "score": 0, "time_sec": 0}
                    db["rooms"][room_sel]["players"] = r_players
                    save_sudoku_db(db)
                    st.session_state.sudoku_state = {
                        "tier": r_tier,
                        "board_num": 999,
                        "solution": r_data["solution"],
                        "puzzle": r_data["puzzle"],
                        "user_board": [row[:] for row in r_data["puzzle"]],
                        "hinted_cells": [],
                        "completed": False,
                        "surrendered": False,
                        "last_score": 0,
                        "start_ts": time.time()
                    }
                    st.success(f"✅ Loaded Room `{room_sel}` board! Switch to **Tab 1** now to solve it, then click 'Sync My Result' below when done!")
            with dl_c2:
                if st.button("🏆 Sync My Completed Board Result to This Room", use_container_width=True):
                    if gs["completed"] and not gs["surrendered"] and gs["solution"] == r_data["solution"]:
                        elapsed = int(time.time() - gs.get("start_ts", time.time()))
                        r_players[player_name] = {
                            "status": "✅ FINISHED!",
                            "score": gs["last_score"],
                            "time_sec": elapsed
                        }
                        db["rooms"][room_sel]["players"] = r_players
                        save_sudoku_db(db)
                        st.balloons()
                        st.rerun()
                    else:
                        st.warning("⚠️ Load this room's board and finish solving it in Tab 1 first!")

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

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
    """Sinh ma trận Sudoku 9x9 chuẩn toán học (81 ô, chia thành 9 khối 3x3) theo 5 Tier độ khó."""
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
    """Kiểm tra trùng số trên Hàng, Cột và 9 khối 3x3."""
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

def inject_arcade_and_sudoku_css():
    """CSS đồng bộ kích thước 81 ô trên 1 bảng 9x9 duy nhất và trang trí Sảnh Game."""
    st.markdown("""
    <style>
        /* Thẻ chọn Game trong Sảnh (Game Hub Cards) */
        .game-hub-card {
            background: linear-gradient(145deg, #111827 0%, #1e1b4b 100%);
            border: 1px solid #374151;
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 12px;
            transition: all 0.25s ease;
        }
        .game-hub-card:hover {
            border-color: #60a5fa;
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.2);
        }
        .game-hub-title {
            color: #f8fafc;
            font-size: 1.15rem;
            font-weight: 800;
            margin-bottom: 6px;
        }
        .game-hub-desc {
            color: #94a3b8;
            font-size: 0.86rem;
            line-height: 1.45;
        }
        /* Thu gọn khoảng cách dọc giữa 9 hàng của bảng Sudoku 9x9 duy nhất */
        div[data-testid="stVerticalBlock"] > div:has(div.sdk-row-marker) {
            margin-bottom: -10px !important;
        }
        /* Ô người chơi tự điền (Màu xanh ngọc sáng) */
        div[data-testid="stTextInput"] input:not(:disabled) {
            text-align: center !important;
            font-size: 1.22rem !important;
            font-weight: 800 !important;
            color: #34d399 !important;
            -webkit-text-fill-color: #34d399 !important;
            background-color: #090d16 !important;
            border: 1.5px solid #334155 !important;
            border-radius: 6px !important;
            height: 44px !important;
            padding: 0 !important;
        }
        div[data-testid="stTextInput"] input:not(:disabled):focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 12px rgba(59, 130, 246, 0.6) !important;
            background-color: #0f172a !important;
        }
        /* Ô đề bài cố định (Dùng chung st.text_input disabled để 81 ô đều nhau 100% trên Safari) */
        div[data-testid="stTextInput"] input:disabled {
            text-align: center !important;
            font-size: 1.22rem !important;
            font-weight: 800 !important;
            color: #60a5fa !important;
            -webkit-text-fill-color: #60a5fa !important;
            background-color: #1e293b !important;
            border: 1.5px solid #3b82f6 !important;
            border-radius: 6px !important;
            height: 44px !important;
            padding: 0 !important;
            opacity: 1 !important;
            cursor: not-allowed !important;
        }
        .sdk-hdr {
            text-align: center;
            color: #93c5fd;
            font-weight: 800;
            font-size: 0.85rem;
            padding-bottom: 4px;
        }
        .sdk-r-label {
            height: 44px;
            line-height: 44px;
            text-align: center;
            color: #93c5fd;
            font-weight: 800;
            font-size: 0.85rem;
        }
        .sdk-3x3-line {
            border: 0;
            border-top: 3px solid #3b82f6;
            margin: 4px 0 8px 0;
            box-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
        }
    </style>
    """, unsafe_allow_html=True)

def render_single_unified_9x9_board(puzzle: list[list[int]], user_board: list[list[int]], hinted_cells: list, key_prefix: str, lock_all: bool = False):
    """
    1 BẢNG 9x9 DUY NHẤT: Toàn bộ 81 ô đều dùng chung cấu trúc st.text_input (ô đề bài thì disabled=True)
    giúp kích thước, chiều cao và khoảng cách của cả 81 ô đều nhau 100% trên mọi trình duyệt.
    """
    hint_set = set(tuple(x) for x in hinted_cells)

    _, board_wrap, _ = st.columns([0.5, 3.4, 0.5])
    with board_wrap:
        st.markdown(
            "<div style='text-align:center; margin-bottom:8px; color:#cbd5e1; font-size:0.9rem;'>"
            "🔵 <b>Locked Blue Cell</b> = Fixed Clue / Hint &nbsp;|&nbsp; "
            "🟢 <b>Dark Editable Cell</b> = Click & type <code>1–9</code> directly (Backspace to clear)"
            "</div>",
            unsafe_allow_html=True
        )

        # Cột: [Nhãn Hàng] + [C1, C2, C3] + [Vách ngăn 3x3] + [C4, C5, C6] + [Vách ngăn 3x3] + [C7, C8, C9]
        col_ratios = [0.6, 1, 1, 1, 0.15, 1, 1, 1, 0.15, 1, 1, 1]
        h_cols = st.columns(col_ratios)
        h_cols[0].markdown("<div class='sdk-hdr'>R\\C</div>", unsafe_allow_html=True)
        for c in range(9):
            c_idx = c + 1 + (1 if c >= 3 else 0) + (1 if c >= 6 else 0)
            h_cols[c_idx].markdown(f"<div class='sdk-hdr'>C{c+1}</div>", unsafe_allow_html=True)

        for r in range(9):
            if r in [3, 6]:
                st.markdown("<hr class='sdk-3x3-line'>", unsafe_allow_html=True)

            st.markdown("<div class='sdk-row-marker'></div>", unsafe_allow_html=True)
            r_cols = st.columns(col_ratios)
            r_cols[0].markdown(f"<div class='sdk-r-label'>R{r+1}</div>", unsafe_allow_html=True)

            for c in range(9):
                c_idx = c + 1 + (1 if c >= 3 else 0) + (1 if c >= 6 else 0)
                with r_cols[c_idx]:
                    is_fixed = (puzzle[r][c] != 0)
                    is_hinted = ((r, c) in hint_set)
                    cell_key = f"{key_prefix}_r{r}_c{c}"

                    if is_fixed:
                        st.text_input(
                            f"R{r+1}C{c+1}",
                            value=str(puzzle[r][c]),
                            key=f"fix_{cell_key}",
                            label_visibility="collapsed",
                            disabled=True
                        )
                    elif is_hinted:
                        st.text_input(
                            f"R{r+1}C{c+1}",
                            value=f"{user_board[r][c]}",
                            key=f"hnt_{cell_key}",
                            label_visibility="collapsed",
                            disabled=True
                        )
                    else:
                        curr_v = user_board[r][c]
                        default_txt = str(curr_v) if curr_v in range(1, 10) else ""
                        val_in = st.text_input(
                            f"R{r+1}C{c+1}",
                            value=default_txt,
                            max_chars=1,
                            key=cell_key,
                            label_visibility="collapsed",
                            disabled=lock_all,
                            placeholder="·"
                        ).strip()
                        if val_in in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                            user_board[r][c] = int(val_in)
                        else:
                            user_board[r][c] = 0

def render_sudoku_arcade(default_username: str = "taolagautruc"):
    inject_arcade_and_sudoku_css()

    # ==========================================================================
    # SẢNH GAME TRUNG TÂM (CYBER GAME ARCADE HUB — CHỨA NHIỀU CON GAME NHỎ)
    # ==========================================================================
    st.markdown("""
    <div class="hero-box" style="padding: 24px 32px; margin-bottom: 18px; background: linear-gradient(135deg, #090d16 0%, #1e1b4b 50%, #312e81 100%); border: 1px solid #6366f1;">
        <div class="hero-badge" style="background: rgba(99, 102, 241, 0.2); color: #818cf8; border-color: #6366f1;">🎮 CYBER GAME ARCADE • LOGIC, DEDUCTION & CRYPTOGRAPHY MINI-GAMES</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Ultimate Mind & Cryptic Game Center</h2>
        <p class="hero-sub">
            Select a mini-game from the Arcade Lobby below! Compete on game-specific leaderboards, use strategic hints, or host multiplayer duel rooms with friends.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Hiển thị các thẻ Mini-Games trong Sảnh
    g_col1, g_col2, g_col3, g_col4 = st.columns(4)
    with g_col1:
        st.markdown("""
        <div class="game-hub-card" style="border-color:#3b82f6;">
            <div class="game-hub-title">🧩 1. 9x9 Sudoku Arena</div>
            <div class="game-hub-desc">Infinite 5-Tier 9x9 matrices, targeted hints (-15%), and 1v1 Timed Countdown Rooms.</div>
        </div>
        """, unsafe_allow_html=True)
    with g_col2:
        st.markdown("""
        <div class="game-hub-card">
            <div class="game-hub-title">🗝️ 2. Unlock! Escape Room</div>
            <div class="game-hub-desc">Combine item cards, symbol codes & 4-digit locks to escape before time runs out.</div>
        </div>
        """, unsafe_allow_html=True)
    with g_col3:
        st.markdown("""
        <div class="game-hub-card">
            <div class="game-hub-title">🕵️ 3. Sherlock Detective</div>
            <div class="game-hub-desc">Forensic cryptogram & alibi deduction mysteries inspired by Consulting Detective.</div>
        </div>
        """, unsafe_allow_html=True)
    with g_col4:
        st.markdown("""
        <div class="game-hub-card">
            <div class="game-hub-title">🔐 4. Mastermind Vault</div>
            <div class="game-hub-desc">Crack the secret 4-digit vault combination using Exact & Partial logic feedback.</div>
        </div>
        """, unsafe_allow_html=True)

    top_bar1, top_bar2 = st.columns([2.2, 1.3])
    with top_bar1:
        selected_game = st.radio(
            "🕹️ Choose Active Mini-Game to Play:",
            [
                "🧩 9x9 Sudoku Master Arena",
                "🗝️ Unlock! Escape Room",
                "🕵️ Sherlock Consulting Detective",
                "🔐 Mastermind Vault Breaker"
            ],
            horizontal=True
        )
    with top_bar2:
        player_name = st.text_input(
            "🕵️ Your Arcade Player Callsign:",
            value=st.session_state.get("ctf_user") or default_username,
            key="sdk_player_in"
        ).strip() or "Agent_Player"

    st.divider()

    # Nếu người dùng chọn các mini-game số 2, 3, 4 thì hiển thị bản chơi nhanh hoặc预告
    if "Unlock! Escape Room" in selected_game:
        st.subheader("🗝️ Unlock! Cyber Escape Room — Episode 1: The Server Vault")
        st.info("🔍 **Escape Scenario:** You are locked inside a high-security server room. A **Red Card #14** (shows a 3-triangle symbol) and a **Blue Card #27** (shows a 5-star symbol) lie on the desk. The door keypad asks for `CardSum + (Triangles * Stars)`.")
        code_try = st.text_input("🔢 Enter 2-Digit Escape Keypad Code:")
        if st.button("🔓 Unlock Door", type="primary"):
            if code_try.strip() == "56":
                st.balloons()
                st.success("🎉 **DOOR UNLOCKED!** `(14 + 27) + (3 * 5) = 41 + 15 = 56`! More Escape Room episodes coming soon!")
            else:
                st.error("❌ Locked! Hint: Add the two card numbers `(14 + 27)`, then add `(3 * 5)`.")
        return

    elif "Sherlock Consulting Detective" in selected_game:
        st.subheader("🕵️ Sherlock Holmes Consulting Detective — Case #01: The Midnight Cipher")
        st.info("📜 **Case Dossier:** Lord Blackwood's safe was opened at `23:45 UTC`. Three suspects were in the mansion: **Butler James** (alibi: kitchen, no mud on shoes), **Lady Evelyn** (alibi: garden, mud on boots, knew the shift key), and **Dr. Mortimer** (arrived at `00:15 UTC`). The note left behind reads `VRIH` (Caesar Shift +3).")
        suspect = st.selectbox("Who opened the safe, and what does 'VRIH' decode to?", ["-- Select Deduction --", "Butler James (SAFE)", "Lady Evelyn (SAFE)", "Dr. Mortimer (GOLD)"])
        if st.button("🔍 Submit Deduction to Scotland Yard", type="primary"):
            if "Lady Evelyn" in suspect:
                st.balloons()
                st.success("🎉 **BRILLIANT DEDUCTION, HOLMES!** `VRIH` (-3) = `SAFE`, and only Lady Evelyn had garden mud and knew the cipher!")
            else:
                st.error("❌ Elementary mistake, Watson! Check the arrival time, the garden mud, and shift `VRIH` back by 3 letters.")
        return

    elif "Mastermind Vault Breaker" in selected_game:
        st.subheader("🔐 Mastermind Vault Breaker — Crack the 4-Digit Secret Code")
        if "mm_secret" not in st.session_state:
            st.session_state.mm_secret = "".join(random.sample("123456789", 4))
            st.session_state.mm_history = []
        mm_guess = st.text_input("Enter 4 distinct digits (1–9):", max_chars=4, placeholder="e.g. 4829")
        c_m1, c_m2 = st.columns(2)
        if c_m1.button("🚀 Test Combination", type="primary", use_container_width=True) and len(mm_guess) == 4:
            sec = st.session_state.mm_secret
            bulls = sum(1 for i in range(4) if mm_guess[i] == sec[i])
            cows = sum(1 for c in mm_guess if c in sec) - bulls
            st.session_state.mm_history.append((mm_guess, bulls, cows))
            if bulls == 4:
                st.balloons()
                st.success(f"🎉 **VAULT CRACKED!** The code was `{sec}`!")
        if c_m2.button("🔄 New Vault Code", use_container_width=True):
            st.session_state.mm_secret = "".join(random.sample("123456789", 4))
            st.session_state.mm_history = []
            st.rerun()
        for g_str, b_cnt, c_cnt in reversed(st.session_state.mm_history):
            st.markdown(f"- Guess **`{g_str}`** $\\rightarrow$ 🟢 **{b_cnt} Exact Position** | 🟡 **{c_cnt} Wrong Position**")
        return

    # ==========================================================================
    # CON GAME CHỦ LỰC: 🧩 9x9 SUDOKU MASTER ARENA (1 BẢNG DUY NHẤT & PHÒNG ĐẤU CÔNG BẰNG)
    # ==========================================================================
    db = load_sudoku_db()
    p_stats = db["leaderboard"].get(player_name, {"sudoku_score": 0, "puzzles_solved": 0, "best_tier": 0})

    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("🕵️ Active Sudoku Player", player_name, "Sudoku Master Arena")
    m_col2.metric("🏆 Your Total Sudoku Score", f"{p_stats.get('sudoku_score', 0):,} PTS", f"Best Tier: Tier {p_stats.get('best_tier', 0)}")
    m_col3.metric("✅ 9x9 Boards Solved", f"{p_stats.get('puzzles_solved', 0)} Boards", "Global Ranked")

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
        "🎮 1. Singleplayer 9x9 Sudoku (Unified Board)",
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
                💡 <b>Hint Rule:</b> Max <b>5 hints/board</b> (1 hint per cell, <b>-15% score</b> each • Used: <b>{hints_used_count}/5</b>). &nbsp;|&nbsp;
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
                        st.rerun()

        if gs["completed"] and not gs["surrendered"]:
            st.success(f"🎉 **VICTORY! You solved this 9x9 Sudoku Matrix and earned +{gs['last_score']:,} PTS!**")
        elif gs["surrendered"]:
            st.error(f"🏳️ **BOARD SURRENDERED!** Full 9x9 solution is displayed below (-{surrender_penalty:,} PTS penalty applied).")

        # CHỈ HIỂN THỊ 1 BẢNG 9x9 DUY NHẤT VỪA NHÌN VỪA ĐIỀN ĐÁP ÁN
        render_single_unified_9x9_board(
            gs["puzzle"],
            gs["user_board"],
            gs["hinted_cells"],
            key_prefix=f"solo_{curr_tier}_{gs['board_num']}",
            lock_all=gs["completed"]
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
    # TAB 2: PHÒNG CHƠI CHUNG / THI ĐẤU 1v1 (THỜI GIAN GIẢI, HINT -45s, ĐẾM NGƯỢC TỐI ĐA 10P)
    # ==========================================================================
    with tab_duel:
        st.markdown("""
        <div class="ws-banner">
            <h4>⚔️ Fair-Start 1v1 & Multiplayer Sudoku Tournament Rooms</h4>
            <p>
                • <b>Custom Solve Time:</b> Choose 10m, 15m, 20m, 30m, etc.<br>
                • <b>Hint Limit & Penalty:</b> Up to 5 hints max. Each hint used <b>reduces your remaining solve time by 45 seconds (-45s)</b> and deducts <b>15% score</b>.<br>
                • <b>Fair-Play Countdown (Max 10 mins = 600s):</b> Set how many seconds before the puzzle appears so the host can share the Room ID with everyone. The board only unlocks when the countdown hits 0!
            </p>
        </div>
        """, unsafe_allow_html=True)

        rooms = db.get("rooms", {})
        r_col1, r_col2 = st.columns([2.2, 1])
        with r_col1:
            room_sel = st.selectbox("📂 Select Active Duel Room or Create New:", ["➕ Create New Sudoku Duel Room"] + list(rooms.keys()))
        with r_col2:
            st.write("")
            if st.button("🔄 Refresh Room & Countdown Timer", use_container_width=True):
                st.rerun()

        if room_sel == "➕ Create New Sudoku Duel Room":
            with st.container(border=True):
                st.markdown("##### ⚙️ Configure New Multiplayer / 1v1 Match Rules")
                cr1, cr2, cr3 = st.columns(3)
                with cr1:
                    new_code = st.text_input("🔑 Room ID / Match Code:", placeholder="e.g. HCMUS-SOLO-01")
                    duel_tier = st.selectbox("🔥 Difficulty Tier (1–5):", [1, 2, 3, 4, 5], index=1)
                with cr2:
                    solve_mins = st.selectbox("⏱️ Solve Time Limit (Minutes):", [5, 10, 15, 20, 25, 30, 45, 60], index=2)
                    max_room_hints = st.slider("💡 Max Hints Allowed (Max = 5, -45s/hint):", min_value=0, max_value=5, value=3)
                with cr3:
                    reveal_delay_sec = st.number_input(
                        "⏳ Display Puzzle After How Many Seconds? (Max 600s = 10 mins):",
                        min_value=0, max_value=600, value=60, step=10,
                        help="While counting down, the puzzle is hidden so you can send the Room ID to friends!"
                    )

                if st.button("🚀 Create Room & Start Countdown", type="primary", use_container_width=True):
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
                                player_name: {"status": "⏳ Waiting / Solving", "score": 0, "time_sec": 0, "hints_used": 0}
                            }
                        }
                        db["rooms"] = rooms
                        save_sudoku_db(db)
                        st.success(f"✅ Room **`{code_clean}`** created! Select **`{code_clean}`** in the dropdown above to enter the room!")
                        st.rerun()

        else:
            r_data = rooms[room_sel]
            r_tier = r_data.get("tier", 1)
            r_creator = r_data.get("creator", "Host")
            r_max_hints = r_data.get("max_hints", 5)
            r_solve_sec = r_data.get("solve_duration_sec", 900)
            r_reveal_ts = r_data.get("reveal_ts", 0)
            r_players = r_data.get("players", {})

            if player_name not in r_players:
                r_players[player_name] = {"status": "⏳ Joined Room", "score": 0, "time_sec": 0, "hints_used": 0}
                db["rooms"][room_sel]["players"] = r_players
                save_sudoku_db(db)

            now_ts = int(time.time())

            # BẢNG ĐIỀU KHIỂN TRỰC TIẾP CHO NGƯỜI TẠO PHÒNG (HIỆN RÕ Ô NHẬP SỐ GIÂY ĐẾM NGƯỢC TỐI ĐA 10 PHÚT & THỜI GIAN GIẢI)
            if player_name == r_creator:
                with st.container(border=True):
                    st.markdown(f"##### 👑 Room Host Settings (`{room_sel}`) — Set Countdown & Match Rules")
                    st.caption("📝 Fill in how many seconds before the puzzle is displayed (up to 600s / 10 mins) so you can send the Room ID to everyone. The board will stay hidden until the countdown finishes!")
                    hc1, hc2, hc3, hc4 = st.columns([1.4, 1.2, 1.2, 1.2])
                    with hc1:
                        host_delay_in = st.number_input(
                            "⏳ Show puzzle after (seconds, max 600s = 10m):",
                            min_value=0, max_value=600, value=int(r_data.get("reveal_delay_sec", 60)), step=10,
                            key=f"h_delay_{room_sel}"
                        )
                    with hc2:
                        host_solve_m = st.selectbox(
                            "⏱️ Solve Time (Mins):",
                            [5, 10, 15, 20, 25, 30, 45, 60],
                            index=2,
                            key=f"h_smin_{room_sel}"
                        )
                    with hc3:
                        host_max_h = st.number_input(
                            "💡 Max Hints (0–5):",
                            min_value=0, max_value=5, value=int(r_max_hints),
                            key=f"h_mh_{room_sel}"
                        )
                    with hc4:
                        st.write("")
                        if st.button("⏱️ Apply & Start Countdown", type="primary", use_container_width=True):
                            now_click = int(time.time())
                            r_data["reveal_delay_sec"] = int(host_delay_in)
                            r_data["reveal_ts"] = now_click + int(host_delay_in)
                            r_data["solve_duration_sec"] = int(host_solve_m * 60)
                            r_data["max_hints"] = int(host_max_h)
                            db["rooms"][room_sel] = r_data
                            save_sudoku_db(db)
                            st.toast(f"⏳ Countdown started! Puzzle will appear in {host_delay_in} seconds!", icon="⏳")
                            st.rerun()

            # KIỂM TRA ĐẾM NGƯỢC TRƯỚC KHI HIỂN THỊ ĐỀ (ĐẢM BẢO CÔNG BẰNG 100%)
            if now_ts < r_reveal_ts:
                wait_rem = r_reveal_ts - now_ts
                wm, ws = divmod(wait_rem, 60)
                st.warning(
                    f"### ⏳ WAITING FOR COUNTDOWN: Puzzle will be displayed in **`{wm:02d}m {ws:02d}s`** ({wait_rem} seconds)!\n\n"
                    f"- 🔑 **Room ID to share with friends:** **`{room_sel}`**\n"
                    f"- ⚙️ **Match Settings:** Tier `{r_tier}` &nbsp;|&nbsp; Solve Time Limit: **`{r_solve_sec // 60} minutes`** &nbsp;|&nbsp; "
                    f"Max Hints: **`{r_max_hints}`** *(Each hint deducts **-45s** solve time & **-15%** score)*.\n"
                    f"- 🔒 The 9x9 Sudoku puzzle is currently locked and hidden for all players until the countdown reaches `00:00`!"
                )
                if st.button("🔄 Refresh Countdown Timer", type="primary"):
                    st.rerun()
            else:
                # KHI HẾT ĐẾM NGƯỢC -> HIỂN THỊ ĐỀ CHO TẤT CẢ MỌI NGƯỜI CÙNG LÚC
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

                start_solve_ts = r_reveal_ts if r_reveal_ts > 0 else r_data.get("created_ts", now_ts)
                elapsed_solve = max(0, now_ts - start_solve_ts)
                hint_time_penalty = used_h * 45
                remaining_solve_sec = r_solve_sec - elapsed_solve - hint_time_penalty
                time_expired = (remaining_solve_sec <= 0) and (not rp_state["completed"])

                rm_min, rm_sec = divmod(max(0, remaining_solve_sec), 60)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("📡 Active Room ID", room_sel, f"Host: {r_creator}")
                m2.metric("⏱️ Remaining Solve Time", f"{rm_min:02d}:{rm_sec:02d}", f"-{hint_time_penalty}s Hint Penalty")
                m3.metric("💡 Room Hints Left", f"{rem_h} / {r_max_hints}", "-45s & -15% pts/hint")
                m4.metric("🔥 Match Tier", f"Tier {r_tier}", f"Limit: {r_solve_sec//60} mins")

                if time_expired:
                    st.error("⏰ **TIME'S UP!** Your solve timer (including `-45s` hint penalties) has reached `00:00`!")
                    r_players[player_name]["status"] = "⏰ Time Expired"
                    db["rooms"][room_sel]["players"] = r_players
                    save_sudoku_db(db)

                with st.container(border=True):
                    rh1, rh2, rh3 = st.columns([1.2, 1.2, 2.2])
                    with rh1:
                        rh_r = st.selectbox("Row (R1–R9):", list(range(1, 10)), key=f"rm_hr_{room_sel}")
                    with rh2:
                        rh_c = st.selectbox("Col (C1–C9):", list(range(1, 10)), key=f"rm_hc_{room_sel}")
                    with rh3:
                        st.write("")
                        can_rm_hint = (not rp_state["completed"]) and (not time_expired) and (rem_h > 0)
                        if st.button(f"💡 Use Room Hint (R{rh_r}, C{rh_c}) [-45s Solve Time & -15% Score]", use_container_width=True, disabled=not can_rm_hint):
                            ri, ci = rh_r - 1, rh_c - 1
                            if r_data["puzzle"][ri][ci] != 0:
                                st.warning("That cell is already a fixed clue!")
                            elif (ri, ci) in [tuple(x) for x in rp_state["hinted_cells"]]:
                                st.warning("You already used a hint on this cell!")
                            else:
                                rp_state["user_board"][ri][ci] = r_data["solution"][ri][ci]
                                rp_state["hinted_cells"].append((ri, ci))
                                r_players[player_name]["hints_used"] = len(rp_state["hinted_cells"])
                                db["rooms"][room_sel]["players"] = r_players
                                save_sudoku_db(db)
                                st.rerun()

                # HIỂN THỊ 1 BẢNG 9x9 DUY NHẤT TRỰC TIẾP TRONG PHÒNG ĐẤU
                render_single_unified_9x9_board(
                    r_data["puzzle"],
                    rp_state["user_board"],
                    rp_state["hinted_cells"],
                    key_prefix=f"rm_{room_sel}",
                    lock_all=(rp_state["completed"] or time_expired)
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

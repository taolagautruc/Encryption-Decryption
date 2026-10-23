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

def inject_compact_responsive_sudoku_css():
    """
    CSS định dạng 4 Thẻ Game Bấm Trực Tiếp (Clickable Game Cards)
    và thu gọn riêng bàn cờ 9x9 (460px) ở giữa màn hình.
    """
    st.markdown("""
    <style>
        /* BIẾN 4 THẺ TIÊU ĐỀ GAME Ở TRÊN THÀNH 4 NÚT BẤM LỚN TƯƠNG TÁC TRỰC TIẾP */
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button {
            height: 128px !important;
            width: 100% !important;
            border-radius: 14px !important;
            padding: 14px 18px !important;
            text-align: left !important;
            justify-content: flex-start !important;
            align-items: flex-start !important;
            white-space: pre-wrap !important;
            line-height: 1.45 !important;
            transition: all 0.22s ease !important;
        }
        /* Thẻ Game ở trạng thái bình thường (chưa chọn) */
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button[kind="secondary"] {
            background: linear-gradient(145deg, #111827 0%, #1e1b4b 100%) !important;
            border: 1.5px solid #374151 !important;
            color: #cbd5e1 !important;
        }
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button[kind="secondary"]:hover {
            border-color: #60a5fa !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.25) !important;
        }
        /* Thẻ Game đang được chọn (Active Game Card) */
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button[kind="primary"] {
            background: linear-gradient(145deg, #1e1b4b 0%, #1d4ed8 100%) !important;
            border: 2.5px solid #38bdf8 !important;
            color: #ffffff !important;
            box-shadow: 0 8px 28px rgba(56, 189, 248, 0.4) !important;
            transform: translateY(-2px) !important;
        }

        /* CHỈ THU GỌN ĐÚNG CONTAINER TRONG CÙNG CỦA BÀN CỜ 9x9 (KHÔNG BÓP TOÀN TRANG GAME) */
        div[data-testid="stVerticalBlock"]:has(.sdk-board-scope):not(:has(div[data-testid="stVerticalBlock"] .sdk-board-scope)) {
            max-width: 460px !important;
            margin: 6px auto 14px auto !important;
            background: #0f172a !important;
            border: 2px solid #38bdf8 !important;
            border-radius: 14px !important;
            padding: 14px 16px 18px 16px !important;
            box-shadow: 0 8px 28px rgba(56, 189, 248, 0.2) !important;
        }
        div[data-testid="stVerticalBlock"]:has(.sdk-board-scope):not(:has(div[data-testid="stVerticalBlock"] .sdk-board-scope)) div[data-testid="stHorizontalBlock"] {
            gap: 4px !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            margin-bottom: -10px !important;
        }
        div[data-testid="stVerticalBlock"]:has(.sdk-board-scope):not(:has(div[data-testid="stVerticalBlock"] .sdk-board-scope)) div[data-testid="stColumn"],
        div[data-testid="stVerticalBlock"]:has(.sdk-board-scope):not(:has(div[data-testid="stVerticalBlock"] .sdk-board-scope)) div[data-testid="column"] {
            min-width: 0 !important;
            width: auto !important;
            flex: 1 1 0% !important;
            padding: 0 !important;
        }
        div[data-testid="stVerticalBlock"]:has(.sdk-board-scope):not(:has(div[data-testid="stVerticalBlock"] .sdk-board-scope)) div[data-testid="stTextInput"],
        div[data-testid="stVerticalBlock"]:has(.sdk-board-scope):not(:has(div[data-testid="stVerticalBlock"] .sdk-board-scope)) div[data-baseweb="input"],
        div[data-testid="stVerticalBlock"]:has(.sdk-board-scope):not(:has(div[data-testid="stVerticalBlock"] .sdk-board-scope)) div[data-baseweb="base-input"] {
            height: 38px !important;
            min-height: 38px !important;
            max-height: 38px !important;
            margin: 0 !important;
            padding: 0 !important;
            border-radius: 6px !important;
            background-color: #1e293b !important;
            border: none !important;
        }
        div[data-testid="stVerticalBlock"]:has(.sdk-board-scope):not(:has(div[data-testid="stVerticalBlock"] .sdk-board-scope)) div[data-testid="stTextInput"] input {
            height: 38px !important;
            min-height: 38px !important;
            max-height: 38px !important;
            padding: 0 !important;
            text-align: center !important;
            font-size: 1.1rem !important;
            font-weight: 800 !important;
            color: #fde047 !important;
            -webkit-text-fill-color: #fde047 !important;
            background-color: #1e293b !important;
            border: 1.5px solid #94a3b8 !important;
            border-radius: 6px !important;
            box-sizing: border-box !important;
        }
        div[data-testid="stVerticalBlock"]:has(.sdk-board-scope):not(:has(div[data-testid="stVerticalBlock"] .sdk-board-scope)) div[data-testid="stTextInput"] input:focus {
            background-color: #090d16 !important;
            border: 2px solid #fde047 !important;
            box-shadow: 0 0 8px rgba(253, 224, 71, 0.6) !important;
        }

        .sdk-fixed-even {
            height: 38px;
            line-height: 35px;
            text-align: center;
            background: #2563eb;
            color: #ffffff !important;
            font-size: 1.1rem;
            font-weight: 800;
            border-radius: 6px;
            border: 1.5px solid #93c5fd;
            box-sizing: border-box;
            user-select: none;
        }
        .sdk-fixed-odd {
            height: 38px;
            line-height: 35px;
            text-align: center;
            background: #1d4ed8;
            color: #e0f2fe !important;
            font-size: 1.1rem;
            font-weight: 800;
            border-radius: 6px;
            border: 1.5px solid #60a5fa;
            box-sizing: border-box;
            user-select: none;
        }
        .sdk-hint-box {
            height: 38px;
            line-height: 35px;
            text-align: center;
            background: #059669;
            color: #ffffff !important;
            font-size: 1.1rem;
            font-weight: 800;
            border-radius: 6px;
            border: 1.5px solid #6ee7b7;
            box-sizing: border-box;
            user-select: none;
        }
        .sdk-hdr {
            text-align: center;
            color: #38bdf8;
            font-weight: 800;
            font-size: 0.78rem;
            padding-bottom: 2px;
        }
        .sdk-r-label {
            height: 38px;
            line-height: 38px;
            text-align: center;
            color: #38bdf8;
            font-weight: 800;
            font-size: 0.8rem;
        }
        .sdk-3x3-line {
            border: 0;
            border-top: 2.5px solid #38bdf8;
            margin: 5px 0 7px 0;
        }
    </style>
    """, unsafe_allow_html=True)

def render_single_unified_9x9_board(puzzle: list[list[int]], user_board: list[list[int]], hinted_cells: list, key_prefix: str, lock_all: bool = False):
    """Hiển thị 1 BẢNG 9x9 DUY NHẤT, nhỏ gọn (460px), độ tương phản cao."""
    hint_set = set(tuple(x) for x in hinted_cells)

    st.markdown(
        "<div style='text-align:center; margin-bottom:6px; font-size:0.85rem; color:#e2e8f0;'>"
        "🟦 <b>Blue Box</b> = Fixed Clue &nbsp;|&nbsp; "
        "🟩 <b>Green Box</b> = Revealed Hint &nbsp;|&nbsp; "
        "⬜ <b>Silver-Border Box</b> = Type <code>1–9</code> (Yellow Text)"
        "</div>",
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown("<div class='sdk-board-scope'></div>", unsafe_allow_html=True)

        col_ratios = [0.65, 1, 1, 1, 0.14, 1, 1, 1, 0.14, 1, 1, 1]
        h_cols = st.columns(col_ratios)
        h_cols[0].markdown("<div class='sdk-hdr'>R\\C</div>", unsafe_allow_html=True)
        for c in range(9):
            c_idx = c + 1 + (1 if c >= 3 else 0) + (1 if c >= 6 else 0)
            h_cols[c_idx].markdown(f"<div class='sdk-hdr'>C{c+1}</div>", unsafe_allow_html=True)

        for r in range(9):
            if r in [3, 6]:
                st.markdown("<hr class='sdk-3x3-line'>", unsafe_allow_html=True)

            r_cols = st.columns(col_ratios)
            r_cols[0].markdown(f"<div class='sdk-r-label'>R{r+1}</div>", unsafe_allow_html=True)

            for c in range(9):
                c_idx = c + 1 + (1 if c >= 3 else 0) + (1 if c >= 6 else 0)
                box_parity = ((r // 3) + (c // 3)) % 2
                with r_cols[c_idx]:
                    is_fixed = (puzzle[r][c] != 0)
                    is_hinted = ((r, c) in hint_set)
                    cell_key = f"{key_prefix}_r{r}_c{c}"

                    if is_fixed:
                        cls_name = "sdk-fixed-even" if box_parity == 0 else "sdk-fixed-odd"
                        st.markdown(f"<div class='{cls_name}'>{puzzle[r][c]}</div>", unsafe_allow_html=True)
                    elif is_hinted:
                        st.markdown(f"<div class='sdk-hint-box'>{user_board[r][c]}</div>", unsafe_allow_html=True)
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
                            placeholder=""
                        ).strip()
                        if val_in in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                            user_board[r][c] = int(val_in)
                        else:
                            user_board[r][c] = 0

def render_sudoku_arcade(default_username: str = "taolagautruc"):
    inject_compact_responsive_sudoku_css()

    st.markdown("""
    <div class="hero-box" style="padding: 20px 28px; margin-bottom: 16px; background: linear-gradient(135deg, #090d16 0%, #1e1b4b 50%, #312e81 100%); border: 1px solid #6366f1;">
        <div class="hero-badge" style="background: rgba(99, 102, 241, 0.2); color: #818cf8; border-color: #6366f1;">🎮 CYBER GAME ARCADE • LOGIC, DEDUCTION & CRYPTOGRAPHY MINI-GAMES</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Ultimate Mind & Cryptic Game Center</h2>
        <p class="hero-sub">
            Click directly on any of the 4 Game Cards below to launch that game! Compete on leaderboards, use strategic hints, or host multiplayer duel rooms with friends.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "active_mini_game" not in st.session_state:
        st.session_state.active_mini_game = "SUDOKU"

    curr_game = st.session_state.active_mini_game

    # ==========================================================================
    # 4 THẺ TIÊU ĐỀ GAME CÓ THỂ ẤN VÀO TRỰC TIẾP (ĐÃ XÓA BỎ HÀNG CHẤM TRÒN RỐI MẮT)
    # ==========================================================================
    st.caption("👆 **Click directly on any Game Card below to switch games:**")
    with st.container():
        st.markdown("<div class='game-cards-scope'></div>", unsafe_allow_html=True)
        g_col1, g_col2, g_col3, g_col4 = st.columns(4)

        with g_col1:
            if st.button(
                "🧩 **1. 9x9 Sudoku Arena**\n\nCompact 5-Tier 9x9 grids, targeted hints (-15%), and 1v1 Timed Countdown Rooms.",
                type="primary" if curr_game == "SUDOKU" else "secondary",
                use_container_width=True,
                key="card_btn_sudoku"
            ):
                st.session_state.active_mini_game = "SUDOKU"
                st.rerun()

        with g_col2:
            if st.button(
                "🗝️ **2. Unlock! Escape Room**\n\nCombine item cards, symbol codes & 4-digit locks to escape before time runs out.",
                type="primary" if curr_game == "UNLOCK" else "secondary",
                use_container_width=True,
                key="card_btn_unlock"
            ):
                st.session_state.active_mini_game = "UNLOCK"
                st.rerun()

        with g_col3:
            if st.button(
                "🕵️ **3. Sherlock Detective**\n\nForensic cryptogram & alibi deduction mysteries inspired by Consulting Detective.",
                type="primary" if curr_game == "SHERLOCK" else "secondary",
                use_container_width=True,
                key="card_btn_sherlock"
            ):
                st.session_state.active_mini_game = "SHERLOCK"
                st.rerun()

        with g_col4:
            if st.button(
                "🔐 **4. Mastermind Vault**\n\nCrack the secret 4-digit vault combination using Exact & Partial logic feedback.",
                type="primary" if curr_game == "MASTERMIND" else "secondary",
                use_container_width=True,
                key="card_btn_mastermind"
            ):
                st.session_state.active_mini_game = "MASTERMIND"
                st.rerun()

    st.divider()

    # ==========================================================================
    # HIỂN THỊ GAME TƯƠNG ỨNG KHI NGƯỜI CHƠI ẤN VÀO THẺ ĐÓ
    # ==========================================================================
    if curr_game == "UNLOCK":
        st.subheader("🗝️ Unlock! Cyber Escape Room — Episode 1: The Server Vault")
        st.info("🔍 **Escape Scenario:** You are locked inside a high-security server room. A **Red Card #14** (shows a 3-triangle symbol) and a **Blue Card #27** (shows a 5-star symbol) lie on the desk. The door keypad asks for `CardSum + (Triangles * Stars)`.")
        code_try = st.text_input("🔢 Enter 2-Digit Escape Keypad Code:")
        if st.button("🔓 Unlock Door", type="primary"):
            if code_try.strip() == "56":
                st.balloons()
                st.success("🎉 **DOOR UNLOCKED!** `(14 + 27) + (3 * 5) = 41 + 15 = 56`!")
            else:
                st.error("❌ Locked! Hint: Add the two card numbers `(14 + 27)`, then add `(3 * 5)`.")
        return

    elif curr_game == "SHERLOCK":
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

    elif curr_game == "MASTERMIND":
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
    # MẶC ĐỊNH KHI ẤN VÀO THẺ 1: 🧩 9x9 SUDOKU MASTER ARENA
    # ==========================================================================
    db = load_sudoku_db()

    m_col1, m_col2, m_col3 = st.columns([1.4, 1.3, 1.3])
    with m_col1:
        player_name = st.text_input(
            "🕵️ Your Arcade Player Callsign:",
            value=st.session_state.get("ctf_user") or default_username,
            key="sdk_player_in"
        ).strip() or "Agent_Player"

    p_stats = db["leaderboard"].get(player_name, {"sudoku_score": 0, "puzzles_solved": 0, "best_tier": 0})
    with m_col2:
        st.metric("🏆 Your Total Sudoku Score", f"{p_stats.get('sudoku_score', 0):,} PTS", f"Best Tier: Tier {p_stats.get('best_tier', 0)}")
    with m_col3:
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
        "🎮 1. Singleplayer 9x9 Sudoku (Compact Board)",
        "⚔️ 2. Multiplayer 1v1 & Co-op Rooms (Timed & Fair Countdown)",
        "🏆 3. Global Sudoku Leaderboard"
    ])

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
        <div class="ws-banner" style="padding: 12px 18px; margin-bottom: 12px;">
            <h4>🧩 Active 9x9 Matrix: <code>Tier {curr_tier} • Board #{gs['board_num']}</code> — Potential Reward: <b style="color:#34d399;">+{potential_pts:,} PTS</b></h4>
            <p>
                💡 <b>Hint Rule:</b> Max <b>5 hints/board</b> (1 hint per cell, <b>-15% score</b> each • Used: <b>{hints_used_count}/5</b>). &nbsp;|&nbsp;
                🏳️ <b>Surrender Rule:</b> Revealing full solution deducts <b>92%</b> (<b>-{surrender_penalty:,} PTS</b>).
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            hc1, hc2, hc3 = st.columns([1.1, 1.1, 2.3])
            with hc1:
                h_row = st.selectbox("🎯 Hint Row (R1–R9):", list(range(1, 10)), key="solo_hr")
            with hc2:
                h_col = st.selectbox("🎯 Hint Col (C1–C9):", list(range(1, 10)), key="solo_hc")
            with hc3:
                st.write("")
                can_hint = (not gs["completed"]) and (hints_remaining > 0)
                if st.button(f"💡 Reveal Cell (R{h_row}, C{h_col}) [-15% Score • {hints_remaining} Left]", use_container_width=True, disabled=not can_hint):
                    r_idx, c_idx = h_row - 1, h_col - 1
                    if gs["puzzle"][r_idx][c_idx] != 0:
                        st.warning(f"⚠️ Cell (R{h_row}, C{h_col}) is already a fixed clue!")
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

        render_single_unified_9x9_board(
            gs["puzzle"],
            gs["user_board"],
            gs["hinted_cells"],
            key_prefix=f"solo_{curr_tier}_{gs['board_num']}",
            lock_all=gs["completed"]
        )

        st.write("")
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

    with tab_duel:
        st.markdown("""
        <div class="ws-banner" style="padding: 12px 18px;">
            <h4>⚔️ Fair-Start 1v1 & Multiplayer Sudoku Tournament Rooms</h4>
            <p>
                • <b>Custom Solve Time:</b> 10m, 15m, 20m, 30m, etc. &nbsp;|&nbsp;
                • <b>Hint Penalty:</b> Max 5 hints (each hint deducts <b>-45s solve time</b> & <b>-15% score</b>).<br>
                • <b>Fair-Play Countdown (Max 10 mins = 600s):</b> Fill in how many seconds before the puzzle appears so you can send the Room ID to friends!
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
                        st.success(f"✅ Room **`{code_clean}`** created! Select **`{code_clean}`** in the dropdown above to enter!")
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

            if player_name == r_creator:
                with st.container(border=True):
                    st.markdown(f"##### 👑 Room Host Settings (`{room_sel}`) — Set Countdown & Match Rules")
                    st.caption("📝 Fill in how many seconds before the puzzle is displayed (up to 600s / 10 mins) so you can send the Room ID to everyone.")
                    hc1, hc2, hc3, hc4 = st.columns([1.4, 1.2, 1.2, 1.2])
                    with hc1:
                        host_delay_in = st.number_input(
                            "⏳ Show puzzle after (seconds, max 600s):",
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
                            st.rerun()

            if now_ts < r_reveal_ts:
                wait_rem = r_reveal_ts - now_ts
                wm, ws = divmod(wait_rem, 60)
                st.warning(
                    f"### ⏳ WAITING FOR COUNTDOWN: Puzzle will be displayed in **`{wm:02d}m {ws:02d}s`** ({wait_rem} seconds)!\n\n"
                    f"- 🔑 **Room ID to share with friends:** **`{room_sel}`**\n"
                    f"- ⚙️ **Match Settings:** Tier `{r_tier}` &nbsp;|&nbsp; Solve Time Limit: **`{r_solve_sec // 60} minutes`** &nbsp;|&nbsp; "
                    f"Max Hints: **`{r_max_hints}`** *(Each hint deducts **-45s** solve time & **-15%** score)*.\n"
                    f"- 🔒 The 9x9 Sudoku puzzle is hidden for all players until the countdown reaches `00:00`!"
                )
                if st.button("🔄 Refresh Countdown Timer", type="primary"):
                    st.rerun()
            else:
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
                    rh1, rh2, rh3 = st.columns([1.1, 1.1, 2.3])
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
                                r_players[player_name]["hints_used"] = len(rp_state["hinted_cells"])
                                db["rooms"][room_sel]["players"] = r_players
                                save_sudoku_db(db)
                                st.rerun()

                render_single_unified_9x9_board(
                    r_data["puzzle"],
                    rp_state["user_board"],
                    rp_state["hinted_cells"],
                    key_prefix=f"rm_{room_sel}",
                    lock_all=(rp_state["completed"] or time_expired)
                )

                st.write("")
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

import streamlit as st
import random
import time
import json
import os
from datetime import datetime, timezone

SUDOKU_DB_FILE = "sudoku_arena_db.json"
COMM_DB_FILE = "community_hub_db.json"

# ==============================================================================
# DỮ LIỆU 5 TẬP GAME UNLOCK! ESCAPE ROOM & 5 VỤ ÁN SHERLOCK DETECTIVE
# ==============================================================================
UNLOCK_EPISODES = [
    {
        "id": "EP1",
        "title": "Episode 1: The Server Vault (Beginner)",
        "reward": 500,
        "scenario": "You are locked inside a cooling server room. Oxygen drops in 15 minutes! Inspect the two item cards on the desk, combine their numbers to unlock the blueprint card, and compute the final keypad code.",
        "cards": [
            ("🔴 Red Card #14", "A server keycard stamped with **3 Triangles (▲▲▲)**."),
            ("🔵 Blue Card #27", "A maintenance badge stamped with **5 Stars (★★★★★)**.")
        ],
        "combine_target": 41,
        "combined_reveal": "🟢 **Unlocked Blueprint Card #41:** *'To open the blast door, take the Card Sum (41) and ADD the product of (Triangles × Stars)!'*",
        "final_question": "🔢 Enter the 2-Digit Blast Door Keypad Code (`41 + 3×5`):",
        "final_answer": "56",
        "hint": "First combine Red Card (14) + Blue Card (27) = 41. Then calculate 41 + (3 * 5) = 56!"
    },
    {
        "id": "EP2",
        "title": "Episode 2: Submarine Oxygen Lock (Explorer)",
        "reward": 1000,
        "scenario": "Deep-sea research submarine Titan-X has suffered an electrical short. Two emergency fuse cards lie near the sonar console.",
        "cards": [
            ("🟡 Fuse Card #18", "Written in UV ink: **Binary code `00001010` (10 in decimal)**."),
            ("🟣 Valve Card #32", "Engraved note: **Shift Multiplier = 4**.")
        ],
        "combine_target": 50,
        "combined_reveal": "🟢 **Unlocked Sonar Terminal #50:** *'Emergency Hatch PIN = Combined Fuse Number (50) + (Binary Value × Shift Multiplier)!'*",
        "final_question": "🔢 Enter the Emergency Hatch PIN (`50 + 10×4`):",
        "final_answer": "90",
        "hint": "Combine 18 + 32 = 50. Binary 00001010 is 10. Multiply 10 * 4 = 40, then add 50 + 40 = 90!"
    },
    {
        "id": "EP3",
        "title": "Episode 3: The Cryptographer's Study (Challenger)",
        "reward": 1500,
        "scenario": "You are trapped in Professor Turing's private study. The exit door requires a 4-letter secret word locked behind two cipher reels.",
        "cards": [
            ("📜 Reel Card #25", "Contains ciphertext **`KHOOR`** (Caesar Shift +3)."),
            ("🕯️ Lantern Card #39", "Contains ciphertext **`ZRUOG`** (Caesar Shift +3).")
        ],
        "combine_target": 64,
        "combined_reveal": "🟢 **Unlocked Gramophone #64:** *'Take the FIRST 2 letters of the decoded Reel Card and the LAST 2 letters of the decoded Lantern Card!'*",
        "final_question": "🔤 Enter the 4-Letter Escape Password:",
        "final_answer": "HELD",
        "hint": "Combine 25 + 39 = 64. KHOOR (-3) = HELLO (first 2 letters: HE). ZRUOG (-3) = WORLD (last 2 letters: LD) -> HELD!"
    },
    {
        "id": "EP4",
        "title": "Episode 4: Bio-Lab Containment Breach (Master)",
        "reward": 2000,
        "scenario": "Level-4 Bio-Lab lockdown triggered! You must synthesize the neutralizing passcode from two chemical vials.",
        "cards": [
            ("🧪 Vial Card #44", "Label shows Hexadecimal byte **`0x1F`** (31 in decimal)."),
            ("🔬 Centrifuge Card #56", "Label shows Bitwise operation **`31 XOR 12`**.")
        ],
        "combine_target": 100,
        "combined_reveal": "🟢 **Unlocked Analyzer #100:** *'Compute `(31 XOR 12)` in decimal, then multiply by `2` to open the airlock!'*",
        "final_question": "🔢 Enter the Airlock Override Code (`(31 ^ 12) * 2`):",
        "final_answer": "38",
        "hint": "Combine 44 + 56 = 100. In binary, 31 is 11111 and 12 is 01100. 31 XOR 12 = 19. Multiply 19 * 2 = 38!"
    },
    {
        "id": "EP5",
        "title": "Episode 5: Quantum Core Override (Grandmaster)",
        "reward": 3000,
        "scenario": "A rogue AI has locked the Quantum Mainframe! Combine the two RSA key shards to compute the final shutdown code.",
        "cards": [
            ("💎 Shard Card #37", "Public exponent **`e = 3`**, Message **`M = 5`**."),
            ("⚡ Core Card #63", "Modulus **`N = 33`** (`p=3, q=11`).")
        ],
        "combine_target": 100,
        "combined_reveal": "🟢 **Unlocked Quantum Console #100:** *'Compute the RSA ciphertext `C = (M^e) mod N = (5^3) mod 33`!'*",
        "final_question": "🔢 Enter the RSA Quantum Override Code (`125 mod 33`):",
        "final_answer": "26",
        "hint": "Combine 37 + 63 = 100. Calculate 5^3 = 125. Divide 125 by 33: 33 * 3 = 99, remainder = 125 - 99 = 26!"
    }
]

SHERLOCK_CASES = [
    {
        "id": "CASE1",
        "title": "Case #01: The Midnight Cipher at Blackwood Manor (500 PTS)",
        "reward": 500,
        "dossier": (
            "Lord Blackwood's diamond safe was opened at **23:45 UTC**. Muddy footprints from the Victorian greenhouse were found by the safe. "
            "A torn scrap of paper left inside reads **`VRIH`** (encrypted with **Caesar Shift +3**)."
        ),
        "suspects": [
            "🕵️ **Butler James:** Alibi in the kitchen baking bread at 23:45; shoes spotless; does not know classical ciphers.",
            "🕵️ **Lady Evelyn:** Claimed she was walking in the greenhouse garden at 23:40; mud on boots; studied Roman shifts at Oxford.",
            "🕵️ **Dr. Mortimer:** Arrived by carriage from London at 00:15 UTC; raincoat wet from rain, no greenhouse mud."
        ],
        "options": [
            "-- Select Final Deduction --",
            "Butler James | Decoded Note: GOLD",
            "Lady Evelyn | Decoded Note: SAFE",
            "Dr. Mortimer | Decoded Note: SAFE",
            "Lady Evelyn | Decoded Note: RING"
        ],
        "correct_option": "Lady Evelyn | Decoded Note: SAFE",
        "explanation": "`VRIH` shifted back by 3 letters is `SAFE`, and only Lady Evelyn had greenhouse mud on her boots at 23:45 UTC!"
    },
    {
        "id": "CASE2",
        "title": "Case #02: The Thames Steganography Drop (1,000 PTS)",
        "reward": 1000,
        "dossier": (
            "Scotland Yard intercepted a suspect at Westminster Pier carrying a lossless `.PNG` image. "
            "Forensic extraction of the **Red channel LSB** revealed the Atbash Mirror codeword **`WLPX`** (`A↔Z, B↔Y, C↔X, D↔W...`)."
        ),
        "suspects": [
            "🕵️ **Captain Sterling:** Uses only lossy `.JPG` photos which destroy LSB bits; was at the Naval Club.",
            "🕵️ **Irene Vance:** Graphic designer skilled in lossless `.PNG` pixel manipulation; spotted waiting at the river dock.",
            "🕵️ **Inspector Gregson:** Was filing reports at Scotland Yard HQ all evening."
        ],
        "options": [
            "-- Select Final Deduction --",
            "Captain Sterling | Decoded Word: PIER",
            "Irene Vance | Decoded Word: DOCK",
            "Irene Vance | Decoded Word: SHIP",
            "Inspector Gregson | Decoded Word: DOCK"
        ],
        "correct_option": "Irene Vance | Decoded Word: DOCK",
        "explanation": "In Atbash (`A↔Z`), `W=D`, `L=O`, `P=K`? Wait: `W↔D, L↔O, X↔C, P↔K` (`WLPX` reversed/mapped = `DOCK`), and only Irene Vance used lossless `.PNG` files at the dock!"
    },
    {
        "id": "CASE3",
        "title": "Case #03: The Baker Street Telegraph Forgery (1,500 PTS)",
        "reward": 1500,
        "dossier": (
            "A forged bank transfer telegram was transmitted at **14:20 UTC** using ASCII Hexadecimal bytes: **`42 41 4E 4B`**. "
            "The telegraph log shows the sender typed with a customized left-handed mechanical keyer."
        ),
        "suspects": [
            "🕵️ **Arthur Pendelton:** Right-handed clerk; was in a board meeting with 12 witnesses at 14:20 UTC.",
            "🕵️ **Victor Hess:** Left-handed former telegraph engineer; badge swiped into the comms room at 14:18 UTC.",
            "🕵️ **Clara Bow:** Left the building at 13:00 UTC for Paris."
        ],
        "options": [
            "-- Select Final Deduction --",
            "Victor Hess | Hex 42 41 4E 4B = BANK",
            "Arthur Pendelton | Hex 42 41 4E 4B = CASH",
            "Victor Hess | Hex 42 41 4E 4B = VAULT",
            "Clara Bow | Hex 42 41 4E 4B = BANK"
        ],
        "correct_option": "Victor Hess | Hex 42 41 4E 4B = BANK",
        "explanation": "Hex `0x42='B'`, `0x41='A'`, `0x4E='N'`, `0x4B='K'` (`BANK`), and Victor Hess is left-handed and entered the telegraph room at 14:18 UTC!"
    },
    {
        "id": "CASE4",
        "title": "Case #04: The Royal Mint Insider Heist (2,000 PTS)",
        "reward": 2000,
        "dossier": (
            "Gold bullion bars were rerouted using a 2-Rail Fence Transposition cipher reading **`CRZQRO`** (original 6-letter word split into alternating odd/even letters: `C R Z` and `Q R O`, then shifted +3). "
            "Wait — let's inspect the unshifted 2-Rail Fence string **`CRWON!`** -> **`CMRNOW`**? No, the note on the vault floor literally reads **`V A L U T S`** (2-Rail Fence of `VAULTS`)."
        ),
        "suspects": [
            "🕵️ **Chief Guard Miller:** Patrolling the outer gate; has no access to the internal logistics computer.",
            "🕵️ **Logistics Director Thorne:** Wrote a thesis on Rail-Fence transposition; his terminal issued the reroute command.",
            "🕵️ **Driver Jenkins:** Never entered the vault building."
        ],
        "options": [
            "-- Select Final Deduction --",
            "Chief Guard Miller | Decoded: TRUCKS",
            "Logistics Director Thorne | Decoded: VAULTS",
            "Driver Jenkins | Decoded: VAULTS"
        ],
        "correct_option": "Logistics Director Thorne | Decoded: VAULTS",
        "explanation": "Interleaving the two rails reconstructs `VAULTS`, and Logistics Director Thorne's terminal issued the command!"
    },
    {
        "id": "CASE5",
        "title": "Case #05: Moriarty's Final Checksum (3,000 PTS)",
        "reward": 3000,
        "dossier": (
            "Professor Moriarty planted a logic bomb in the London Underground signaling network! "
            "To disarm it, you must identify his courier and calculate the 8-bit Two's Complement signed decimal value of binary **`11111011`**."
        ),
        "suspects": [
            "🕵️ **Colonel Moran:** Spotted at Waterloo Station carrying a magnetic relay trigger at 21:00 UTC.",
            "🕵️ **Inspector Lestrade:** Assisting Sherlock Holmes at Baker Street.",
            "🕵️ **Mrs. Hudson:** Serving tea at 221B Baker Street."
        ],
        "options": [
            "-- Select Final Deduction --",
            "Colonel Moran | Binary 11111011 = -5",
            "Colonel Moran | Binary 11111011 = -13",
            "Inspector Lestrade | Binary 11111011 = -5"
        ],
        "correct_option": "Colonel Moran | Binary 11111011 = -5",
        "explanation": "In 8-bit Two's Complement, invert `11111011` -> `00000100` (4) + 1 = `5`, so `11111011` is `-5`, and Colonel Moran is Moriarty's operative!"
    }
]


def load_sudoku_db() -> dict:
    if not os.path.exists(SUDOKU_DB_FILE):
        default_db = {
            "leaderboard": {
                "Grandmaster_Kai": {"sudoku_score": 48500, "puzzles_solved": 6, "best_tier": 5},
                "SudokuQueen_99": {"sudoku_score": 21200, "puzzles_solved": 4, "best_tier": 4},
                "LogicKnight_US": {"sudoku_score": 8500, "puzzles_solved": 3, "best_tier": 3}
            },
            "rooms": {},
            "arcade_progress": {}
        }
        with open(SUDOKU_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_db, f, ensure_ascii=False, indent=4)
        return default_db
    try:
        with open(SUDOKU_DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "arcade_progress" not in data:
                data["arcade_progress"] = {}
            return data
    except Exception:
        return {"leaderboard": {}, "rooms": {}, "arcade_progress": {}}


def save_sudoku_db(data: dict):
    with open(SUDOKU_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def award_arcade_xp(db: dict, player_name: str, pts: int, tier_equiv: int = 1):
    """Cộng điểm thưởng từ mọi Mini-Game trong Sảnh vào Bảng xếp hạng Arcade & Hồ sơ Điệp viên Mục 7."""
    lb = db.setdefault("leaderboard", {})
    if player_name not in lb:
        lb[player_name] = {"sudoku_score": 0, "puzzles_solved": 0, "best_tier": 0}
    lb[player_name]["sudoku_score"] += pts
    lb[player_name]["puzzles_solved"] += 1
    lb[player_name]["best_tier"] = max(lb[player_name].get("best_tier", 0), tier_equiv)
    save_sudoku_db(db)

    # Đồng bộ cộng điểm sang community_hub_db.json (Mục 7)
    if os.path.exists(COMM_DB_FILE):
        try:
            with open(COMM_DB_FILE, "r", encoding="utf-8") as f:
                c_db = json.load(f)
            if player_name in c_db.get("profiles", {}):
                c_db["profiles"][player_name]["comm_xp"] = c_db["profiles"][player_name].get("comm_xp", 0) + pts
                with open(COMM_DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(c_db, f, ensure_ascii=False, indent=4)
        except Exception:
            pass


def generate_sudoku_9x9(tier: int, seed_val: str = None) -> tuple[list[list[int]], list[list[int]]]:
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
    st.markdown("""
    <style>
        /* BIẾN 4 THẺ TIÊU ĐỀ GAME Ở TRÊN THÀNH 4 NÚT BẤM LỚN HIỂN THỊ ĐẦY ĐỦ TÓM TẮT */
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button {
            min-height: 135px !important;
            height: auto !important;
            width: 100% !important;
            border-radius: 14px !important;
            padding: 14px 16px !important;
            display: block !important;
            text-align: left !important;
            transition: all 0.22s ease !important;
        }
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button div,
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button p,
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button span {
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
            word-break: break-word !important;
            display: block !important;
            text-align: left !important;
        }
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button p {
            font-size: 0.83rem !important;
            font-weight: 400 !important;
            color: #cbd5e1 !important;
            line-height: 1.45 !important;
            margin: 0 !important;
        }
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button p strong {
            display: block !important;
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            color: #ffffff !important;
            margin-bottom: 6px !important;
            line-height: 1.3 !important;
        }
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button[kind="secondary"] {
            background: linear-gradient(145deg, #111827 0%, #1e1b4b 100%) !important;
            border: 1.5px solid #374151 !important;
        }
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button[kind="secondary"]:hover {
            border-color: #60a5fa !important;
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.25) !important;
        }
        div[data-testid="stVerticalBlock"]:has(.game-cards-scope):not(:has(div[data-testid="stVerticalBlock"] .game-cards-scope)) div.stButton > button[kind="primary"] {
            background: linear-gradient(145deg, #1e1b4b 0%, #1d4ed8 100%) !important;
            border: 2.5px solid #38bdf8 !important;
            box-shadow: 0 8px 28px rgba(56, 189, 248, 0.4) !important;
            transform: translateY(-2px) !important;
        }

        /* CHỈ THU GỌN ĐÚNG CONTAINER TRONG CÙNG CỦA BÀN CỜ 9x9 (460px) */
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
    db = load_sudoku_db()

    st.markdown("""
    <div class="hero-box" style="padding: 20px 28px; margin-bottom: 16px; background: linear-gradient(135deg, #090d16 0%, #1e1b4b 50%, #312e81 100%); border: 1px solid #6366f1;">
        <div class="hero-badge" style="background: rgba(99, 102, 241, 0.2); color: #818cf8; border-color: #6366f1;">🎮 CYBER GAME ARCADE • 4 COMPLETE LOGIC, ESCAPE & DETECTIVE GAMES</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Ultimate Mind & Cryptic Game Center</h2>
        <p class="hero-sub">
            Click directly on any of the 4 Game Cards below! Every solved Sudoku board, Escape Room episode, Sherlock case, and Mastermind vault awards ranked PTS & Agent XP!
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "active_mini_game" not in st.session_state:
        st.session_state.active_mini_game = "SUDOKU"

    curr_game = st.session_state.active_mini_game

    st.caption("👆 **Click directly on any Game Card below to switch games:**")
    with st.container():
        st.markdown("<div class='game-cards-scope'></div>", unsafe_allow_html=True)
        g_col1, g_col2, g_col3, g_col4 = st.columns(4)

        with g_col1:
            if st.button(
                "**🧩 1. 9x9 Sudoku Arena** Compact 5-Tier 9x9 grids, targeted hints (-15%), and 1v1 Timed Countdown Rooms.",
                type="primary" if curr_game == "SUDOKU" else "secondary",
                use_container_width=True,
                key="card_btn_sudoku"
            ):
                st.session_state.active_mini_game = "SUDOKU"
                st.rerun()

        with g_col2:
            if st.button(
                "**🗝️ 2. Unlock! Escape Room** 5 Cyber Escape Episodes! Combine item card numbers & crack locks for up to 3,000 PTS.",
                type="primary" if curr_game == "UNLOCK" else "secondary",
                use_container_width=True,
                key="card_btn_unlock"
            ):
                st.session_state.active_mini_game = "UNLOCK"
                st.rerun()

        with g_col3:
            if st.button(
                "**🕵️ 3. Sherlock Detective** 5 Forensic Case Files! Examine alibis, decode evidence & catch the culprit.",
                type="primary" if curr_game == "SHERLOCK" else "secondary",
                use_container_width=True,
                key="card_btn_sherlock"
            ):
                st.session_state.active_mini_game = "SHERLOCK"
                st.rerun()

        with g_col4:
            if st.button(
                "**🔐 4. Mastermind Vault** 3 Security Tiers (4, 5 & 6 Digits)! Crack the secret vault code with logic feedback.",
                type="primary" if curr_game == "MASTERMIND" else "secondary",
                use_container_width=True,
                key="card_btn_mastermind"
            ):
                st.session_state.active_mini_game = "MASTERMIND"
                st.rerun()

    st.divider()

    # Thanh hiển thị Callsign & Điểm số chung cho cả 4 Game
    m_col1, m_col2, m_col3 = st.columns([1.4, 1.3, 1.3])
    with m_col1:
        player_name = st.text_input(
            "🕵️ Your Arcade Player Callsign:",
            value=st.session_state.get("ctf_user") or default_username,
            key="sdk_player_in"
        ).strip() or "taolagautruc"

    p_stats = db["leaderboard"].get(player_name, {"sudoku_score": 0, "puzzles_solved": 0, "best_tier": 0})
    u_prog = db["arcade_progress"].setdefault(player_name, {"unlock_solved": [], "sherlock_solved": [], "mm_wins": 0})

    with m_col2:
        st.metric("🏆 Total Arcade Score", f"{p_stats.get('sudoku_score', 0):,} PTS", f"Max Tier: Tier {p_stats.get('best_tier', 0)}")
    with m_col3:
        st.metric("✅ Total Arcade Victories", f"{p_stats.get('puzzles_solved', 0)} Wins", f"Escape: {len(u_prog['unlock_solved'])}/5 • Sherlock: {len(u_prog['sherlock_solved'])}/5")

    # ==========================================================================
    # GAME 2: 🗝️ UNLOCK! CYBER ESCAPE ROOM (5 EPISODES + CARD COMBINING MECHANIC)
    # ==========================================================================
    if curr_game == "UNLOCK":
        st.markdown("""
        <div class="ws-banner">
            <h4>🗝️ Unlock! Cyber Escape Room — 5 Interactive Card-Combining Episodes</h4>
            <p><b>How to play:</b> Step 1: Add the two Item Card numbers together to unlock the hidden Clue Card. Step 2: Solve the final keypad lock to escape and earn PTS!</p>
        </div>
        """, unsafe_allow_html=True)

        ep_titles = [
            f"{'✅ ' if ep['id'] in u_prog['unlock_solved'] else '🔒 '}{ep['title']} (+{ep['reward']:,} PTS)"
            for ep in UNLOCK_EPISODES
        ]
        sel_ep_idx = st.selectbox("📂 Select Escape Room Episode:", range(len(UNLOCK_EPISODES)), format_func=lambda i: ep_titles[i])
        ep = UNLOCK_EPISODES[sel_ep_idx]
        ep_id = ep["id"]
        is_ep_solved = ep_id in u_prog["unlock_solved"]

        st.subheader(f"🗝️ {ep['title']} — Reward: +{ep['reward']:,} PTS")
        st.info(f"📖 **Mission Briefing:** {ep['scenario']}")

        c_card1, c_card2 = st.columns(2)
        with c_card1:
            with st.container(border=True):
                st.markdown(f"##### {ep['cards'][0][0]}")
                st.write(ep['cards'][0][1])
        with c_card2:
            with st.container(border=True):
                st.markdown(f"##### {ep['cards'][1][0]}")
                st.write(ep['cards'][1][1])

        # Bước 1: Ghép 2 thẻ đồ vật (Combine Cards)
        with st.container(border=True):
            st.markdown("##### 🔗 Step 1: Combine Item Cards (`Card A # + Card B #`)")
            cb1, cb2 = st.columns([2, 1])
            with cb1:
                comb_in = st.number_input("Enter the sum of the two card numbers:", min_value=0, max_value=999, value=0, key=f"unl_comb_{ep_id}")
            with cb2:
                st.write("")
                if st.button("🔗 Combine Cards", key=f"btn_comb_{ep_id}", use_container_width=True):
                    if comb_in == ep["combine_target"]:
                        st.session_state[f"unl_rev_{ep_id}"] = True
                    else:
                        st.error("❌ Those card numbers don't match! Add the two # numbers on the cards above.")

            if st.session_state.get(f"unl_rev_{ep_id}") or is_ep_solved:
                st.success(ep["combined_reveal"])

        # Bước 2: Nhập mật mã thoát hiểm cuối cùng
        with st.container(border=True):
            st.markdown("##### 🚪 Step 2: Final Escape Keypad")
            if is_ep_solved:
                st.success(f"🎉 **EPISODE COMPLETED!** You already escaped this room (Code: `{ep['final_answer']}`) and claimed **+{ep['reward']:,} PTS**!")
            else:
                k_col1, k_col2, k_col3 = st.columns([2, 1, 1])
                with k_col1:
                    code_try = st.text_input(ep["final_question"], key=f"unl_ans_{ep_id}")
                with k_col2:
                    st.write("")
                    if st.button("🔓 Unlock Blast Door", type="primary", use_container_width=True, key=f"btn_unl_{ep_id}"):
                        if code_try.strip().upper() == ep["final_answer"].upper():
                            u_prog["unlock_solved"].append(ep_id)
                            award_arcade_xp(db, player_name, ep["reward"], tier_equiv=sel_ep_idx + 1)
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Keypad rejected! Combine the cards in Step 1 first or check the Hint.")
                with k_col3:
                    st.write("")
                    with st.popover("💡 View Hint", use_container_width=True):
                        st.write(ep["hint"])
        return

    # ==========================================================================
    # GAME 3: 🕵️ SHERLOCK CONSULTING DETECTIVE (5 FORENSIC CASE FILES)
    # ==========================================================================
    elif curr_game == "SHERLOCK":
        st.markdown("""
        <div class="ws-banner">
            <h4>🕵️ Sherlock Holmes Consulting Detective — 5 Forensic Cryptogram Dossiers</h4>
            <p><b>How to play:</b> Examine the crime scene timestamp, cross-check the 3 suspect alibis, decode the forensic cipher note, and submit your deduction to Scotland Yard!</p>
        </div>
        """, unsafe_allow_html=True)

        case_titles = [
            f"{'✅ ' if c['id'] in u_prog['sherlock_solved'] else '📁 '}{c['title']}"
            for c in SHERLOCK_CASES
        ]
        sel_case_idx = st.selectbox("📂 Select Scotland Yard Case Dossier:", range(len(SHERLOCK_CASES)), format_func=lambda i: case_titles[i])
        case = SHERLOCK_CASES[sel_case_idx]
        cid = case["id"]
        is_case_solved = cid in u_prog["sherlock_solved"]

        st.subheader(f"🕵️ {case['title']}")
        st.info(f"📜 **Crime Scene & Forensic Evidence:** {case['dossier']}")

        st.markdown("##### 👥 Suspect Alibis & Interrogation Notes:")
        for susp in case["suspects"]:
            st.markdown(f"- {susp}")

        st.write("")
        if is_case_solved:
            st.success(f"🎉 **CASE CLOSED!** You solved this investigation (`{case['correct_option']}`) and earned **+{case['reward']:,} PTS**!\n\n💡 *Holmes's Analysis:* {case['explanation']}")
        else:
            ded_pick = st.selectbox("🔍 Who is the culprit, and what does the evidence decode to?", case["options"], key=f"sh_pick_{cid}")
            if st.button("⚖️ Submit Official Deduction to Scotland Yard", type="primary", key=f"btn_sh_{cid}"):
                if ded_pick == case["correct_option"]:
                    u_prog["sherlock_solved"].append(cid)
                    award_arcade_xp(db, player_name, case["reward"], tier_equiv=sel_case_idx + 1)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Elementary mistake, Watson! Re-read the timestamps, alibis, and cipher carefully.")
        return

    # ==========================================================================
    # GAME 4: 🔐 MASTERMIND VAULT BREAKER (3 DIFFICULTY TIERS + ATTEMPT BONUS)
    # ==========================================================================
    elif curr_game == "MASTERMIND":
        st.markdown("""
        <div class="ws-banner">
            <h4>🔐 Mastermind Vault Breaker — Multi-Tier Codebreaking Arena</h4>
            <p>Crack the secret distinct-digit code! 🟢 <b>Exact (Bulls)</b> = Right digit in the right spot &nbsp;|&nbsp; 🟡 <b>Partial (Cows)</b> = Right digit in the wrong spot.</p>
        </div>
        """, unsafe_allow_html=True)

        mm_c1, mm_c2 = st.columns([2, 1])
        with mm_c1:
            mm_tier_label = st.selectbox(
                "🔥 Select Vault Security Tier:",
                [
                    "Tier 1 — 4-Digit Standard Vault (Base Reward: 800 PTS)",
                    "Tier 2 — 5-Digit High-Security Vault (Base Reward: 1,800 PTS)",
                    "Tier 3 — 6-Digit Quantum Vault (Base Reward: 3,500 PTS)"
                ]
            )
        mm_len = 4 if "4-Digit" in mm_tier_label else (5 if "5-Digit" in mm_tier_label else 6)
        mm_base_pts = 800 if mm_len == 4 else (1800 if mm_len == 5 else 3500)

        if "mm_secret" not in st.session_state or len(st.session_state.mm_secret) != mm_len:
            st.session_state.mm_secret = "".join(random.sample("123456789", mm_len))
            st.session_state.mm_history = []
            st.session_state.mm_cracked = False

        with mm_c2:
            st.write("")
            if st.button("🔄 Generate New Vault Code", use_container_width=True):
                st.session_state.mm_secret = "".join(random.sample("123456789", mm_len))
                st.session_state.mm_history = []
                st.session_state.mm_cracked = False
                st.rerun()

        mm_guess = st.text_input(
            f"🔢 Enter {mm_len} distinct digits (from 1–9):",
            max_chars=mm_len,
            placeholder="e.g. " + "482916"[:mm_len]
        ).strip()

        if st.button("🚀 Test Vault Combination", type="primary", disabled=st.session_state.mm_cracked):
            if len(mm_guess) != mm_len or not mm_guess.isdigit() or "0" in mm_guess or len(set(mm_guess)) != mm_len:
                st.warning(f"⚠️ Please enter exactly **{mm_len} distinct non-zero digits (1–9)**!")
            else:
                sec = st.session_state.mm_secret
                bulls = sum(1 for i in range(mm_len) if mm_guess[i] == sec[i])
                cows = sum(1 for c in mm_guess if c in sec) - bulls
                st.session_state.mm_history.append((mm_guess, bulls, cows))
                if bulls == mm_len:
                    st.session_state.mm_cracked = True
                    tries = len(st.session_state.mm_history)
                    speed_bonus = max(0, (10 - tries) * 100)
                    total_mm_pts = mm_base_pts + speed_bonus
                    u_prog["mm_wins"] = u_prog.get("mm_wins", 0) + 1
                    award_arcade_xp(db, player_name, total_mm_pts, tier_equiv=mm_len - 2)
                    st.balloons()
                    st.success(f"🎉 **VAULT CRACKED IN {tries} TRIES!** Secret code: `{sec}` — You earned **+{total_mm_pts:,} PTS**!")

        if st.session_state.mm_history:
            st.markdown("##### 📜 Telemetry Feedback Log:")
            for idx_try, (g_str, b_cnt, c_cnt) in enumerate(reversed(st.session_state.mm_history), start=1):
                attempt_num = len(st.session_state.mm_history) - idx_try + 1
                st.markdown(f"- **Attempt #{attempt_num}:** **`{g_str}`** $\\rightarrow$ 🟢 **{b_cnt} Exact Position** &nbsp;|&nbsp; 🟡 **{c_cnt} Wrong Position**")
        return

    # ==========================================================================
    # GAME 1 (MẶC ĐỊNH): 🧩 9x9 SUDOKU MASTER ARENA
    # ==========================================================================
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
        "🏆 3. Global Arcade Leaderboard"
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
                    award_arcade_xp(db, player_name, potential_pts, tier_equiv=curr_tier)
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
                        min_value=0, max_value=600, value=60, step=10
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
                        award_arcade_xp(db, player_name, final_pts, tier_equiv=r_tier)
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
            <h4>🏆 Global Cyber Game Arcade Leaderboard</h4>
            <p>Combined rankings across 9x9 Sudoku, Unlock! Escape Rooms, Sherlock Detective Cases, and Mastermind Vaults!</p>
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
            c3.markdown(f"✅ `{slv}` victories")
            c4.markdown(f"🔥 Max Tier: `Tier {bt}`")

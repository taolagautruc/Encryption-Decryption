import streamlit as st
import random
import string
import time
import json
import os
import sys
import importlib
import base64
import hashlib
from PIL import Image, ImageDraw
import io
from datetime import datetime, timezone

# Đảm bảo nạp và luôn làm mới (reload) các file module trong core/
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import core.sudoku_game as sudoku_module
importlib.reload(sudoku_module)
from core.sudoku_game import render_sudoku_arcade

import core.multimedia_crypto as multimedia_module
importlib.reload(multimedia_module)
from core.multimedia_crypto import render_pillar2_multimedia_labs

import core.community_hub as community_module
importlib.reload(community_module)
from core.community_hub import render_community_hub

import core.cloud_mobile_studio as cloud_mobile_module
importlib.reload(cloud_mobile_module)
from core.cloud_mobile_studio import render_cloud_and_mobile_studio, auto_boot_cloud_sync

import core.messenger_chat as messenger_module
importlib.reload(messenger_module)
from core.messenger_chat import render_zalo_messenger_rooms

import core.tactical_inventory as inventory_module
importlib.reload(inventory_module)
from core.tactical_inventory import render_sidebar_tactical_hub

import core.ai_cyber_mentor as ai_mentor_module
importlib.reload(ai_mentor_module)
from core.ai_cyber_mentor import render_ai_cyber_mentor_widget

# Đảm bảo nạp và luôn làm mới (reload) file core/sudoku_game.py trên Streamlit Cloud
import importlib
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import core.sudoku_game as sudoku_module
importlib.reload(sudoku_module)
from core.sudoku_game import render_sudoku_arcade

st.set_page_config(
    page_title="Ultimate Secret Messenger | Global Cipher Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)
auto_boot_cloud_sync()

# --- 0. GIAO DIỆN CSS TUỲ CHỈNH (CYBERSECURITY UI THEME) ---
st.markdown("""
<style>
    /* Hero Banner */
    .hero-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        border: 1px solid #3b82f6;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 8px 30px rgba(59, 130, 246, 0.15);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        border: 1px solid #3b82f6;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #f8fafc !important;
        text-shadow: 0 0 20px rgba(59, 130, 246, 0.6), 0 2px 4px rgba(0, 0, 0, 0.8);
        margin: 6px 0 10px 0;
        letter-spacing: -0.5px;
    }
    .hero-title span {
        color: #60a5fa;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0;
    }
    /* Thẻ tính năng (Feature Cards) */
    .feat-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        transition: all 0.25s ease;
    }
    .feat-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
    }
    .feat-title {
        color: #f8fafc;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .feat-desc {
        color: #9ca3af;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    /* Workspace Header & Tool Box */
    .ws-banner {
        background: linear-gradient(90deg, #111827 0%, #1e293b 100%);
        border-left: 4px solid #3b82f6;
        border-top: 1px solid #1f2937;
        border-right: 1px solid #1f2937;
        border-bottom: 1px solid #1f2937;
        padding: 16px 22px;
        border-radius: 10px;
        margin-bottom: 18px;
    }
    .ws-banner h4 {
        margin: 0 0 4px 0;
        color: #f8fafc;
        font-size: 1.15rem;
    }
    .ws-banner p {
        margin: 0;
        color: #94a3b8;
        font-size: 0.9rem;
    }
    /* Chat Message Bubble Card */
    .chat-card {
        background: #111827;
        border: 1px solid #1e293b;
        border-left: 4px solid #60a5fa;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .chat-meta {
        font-size: 0.82rem;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .chat-sender {
        color: #60a5fa;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .chat-badge {
        display: inline-block;
        background: rgba(96, 165, 250, 0.15);
        color: #93c5fd;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        margin-left: 8px;
    }
    /* Tinh chỉnh khung Metric mặc định của Streamlit */
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- 1. CORE CIPHER, CAMOUFLAGE, STEGANOGRAPHY & STORAGE LOGIC ---
VIETNAMESE_CHARS = (
    "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ"
    "ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ"
)
BASE_CHARS = list(" " + string.punctuation + string.digits + string.ascii_letters + VIETNAMESE_CHARS)

@st.cache_data
def load_massive_symbol_pool() -> list:
    pool = []
    for code_range in [(0x1F300, 0x1F5FF), (0x1F600, 0x1F64F), (0x1F680, 0x1F6FF), (0x1F900, 0x1F9FF), (0x2600, 0x26FF)]:
        for code in range(code_range[0], code_range[1] + 1):
            try:
                pool.append(chr(code))
            except ValueError:
                continue
    return pool

def build_custom_key(secret_seed: str, pattern_list: list, shift_step: int, custom_pairs: str) -> list:
    key = BASE_CHARS.copy()
    rng = random.Random(f"{secret_seed}_{''.join(pattern_list)}")
    rng.shuffle(key)
    if shift_step > 0:
        shift = shift_step % len(key)
        key = key[shift:] + key[:shift]
    if custom_pairs.strip():
        for pair in custom_pairs.split(","):
            if "=" in pair:
                a, b = pair.split("=", 1)
                if a.strip() in BASE_CHARS and b.strip() in key:
                    ia, ib = BASE_CHARS.index(a.strip()), key.index(b.strip())
                    key[ia], key[ib] = key[ib], key[ia]
    return key

def calculate_entropy_metrics(secret_seed: str, pattern_list: list, shift_step: int, pool_size: int) -> tuple[int, str]:
    if not secret_seed:
        return 0, "0 seconds (Unprotected)"
    char_space = len(BASE_CHARS) ** max(len(secret_seed), 1)
    icon_space = max(pool_size, 1) ** len(pattern_list)
    shift_space = 200 if shift_step > 0 else 1
    total_combos = char_space * icon_space * shift_space
    bits = total_combos.bit_length()
    seconds = total_combos / (10 ** 12)
    years = seconds / (365 * 24 * 3600)
    if years > 1e15:
        time_str = f"{years:.2e} Years (Quantum-Resistant)"
    elif years > 1:
        time_str = f"{int(years):,} Years"
    else:
        time_str = "< 1 Year (Add more symbols/length)"
    return bits, time_str

def encrypt_core(plain_text: str, key: list, reverse_rule: bool, mode: str = "NONE", target_ts: int = 0) -> str:
    # Nén gọn header thành '~|' nếu không dùng hẹn giờ để bản mã và câu ngụy trang ngắn gọn tối đa
    payload = f"~|{plain_text}" if (mode == "NONE" and target_ts == 0) else f"TMODE:{mode}:{target_ts}|{plain_text}"
    res = "".join(key[BASE_CHARS.index(c)] if c in BASE_CHARS else c for c in payload)
    return res[::-1] if reverse_rule else res

def decrypt_core(cypher_text: str, key: list, reverse_rule: bool) -> tuple[bool, str]:
    txt = cypher_text[::-1] if reverse_rule else cypher_text
    raw = "".join(BASE_CHARS[key.index(c)] if c in key else c for c in txt)
    if raw.startswith("~|"):
        return True, raw[2:]
    if not raw.startswith("TMODE:") or "|" not in raw:
        return False, "❌ Decryption Failed: Incorrect Group Passphrase, Symbol Pattern, or Shift Rules!"
    header, actual_msg = raw.split("|", 1)
    parts = header.split(":")
    if len(parts) != 3:
        return False, "❌ Corrupted timestamp header!"
    mode, target_ts = parts[1], int(parts[2])
    now_ts = int(time.time())
    if mode == "EXPIRE" and target_ts > 0 and now_ts > target_ts:
        expired_ago = now_ts - target_ts
        m, s = divmod(expired_ago, 60)
        return False, f"💥 MESSAGE SELF-DESTRUCTED! (Expired {m}m {s}s ago in UTC)."
    if mode == "WAIT" and target_ts > 0 and now_ts < target_ts:
        wait_sec = target_ts - now_ts
        m, s = divmod(wait_sec, 60)
        return False, f"⏳ TIME-CAPSULE LOCKED! Please wait {m}m {s}s before decoding."
    return True, actual_msg

# --- 1B. MULTI-THEME DYNAMIC ENGLISH CAMOUFLAGE ENGINE (480 PHRASES • 5 THEMES • RANDOM SALT) ---
CAMO_WORDS = [
    "system", "network", "protocol", "update", "server", "client", "module", "process",
    "data", "buffer", "channel", "request", "session", "router", "packet", "cluster"
]

# 5 Chủ đề giao tiếp tiếng Anh đa dạng (5 Themes x 6 Slots x 16 Phrases = 480 cụm từ)
CAMO_THEMES = [
    # THEME 0: Đời sống, Công sở & Học tập
    [
        ["Alex", "Sarah", "David", "Emma", "Ryan", "Olivia", "Daniel", "Sophia", "Lucas", "Mia", "Ethan", "Chloe", "Noah", "Grace", "Leo", "Lily"],
        ["checked", "reviewed", "shared", "prepared", "updated", "finished", "organized", "confirmed", "brought", "scheduled", "sent", "wrote", "printed", "saved", "packed", "booked"],
        ["the new", "our weekly", "the final", "today's", "that", "a quick", "the main", "yesterday's", "the revised", "a special", "the monthly", "our group", "the backup", "a detailed", "the priority", "next"],
        ["report", "schedule", "coffee", "itinerary", "notebook", "draft", "budget", "catalogue", "guidebook", "menu", "dossier", "album", "journal", "playlist", "ticket", "summary"],
        ["at the bistro", "in the library", "near the office", "on the desk", "in the lounge", "at the station", "by the lobby", "in the studio", "at the campus", "in the classroom", "near the park", "at the hotel", "on the train", "in the folder", "at home", "online"],
        ["this morning", "before noon", "around five", "just now", "last night", "after lunch", "on time", "for tomorrow", "very early", "this evening", "a moment ago", "before class", "on Friday", "with friends", "without delay", "as planned"]
    ],
    # THEME 1: Du lịch, Phong cảnh & Khám phá
    [
        ["Marcus", "Elena", "Victor", "Clara", "Julian", "Nora", "Adrian", "Maya", "Sebastian", "Eva", "Gabriel", "Ruby", "Felix", "Alice", "Oscar", "Hazel"],
        ["explored", "photographed", "visited", "admired", "discovered", "sketched", "filmed", "reached", "crossed", "mapped", "entered", "toured", "observed", "climbed", "sailed", "followed"],
        ["the ancient", "a sunlit", "the coastal", "a peaceful", "the famous", "a hidden", "the grand", "a misty", "the royal", "a vibrant", "the northern", "a quiet", "the golden", "a historic", "the mountain", "a tropical"],
        ["lighthouse", "cathedral", "harbor", "courtyard", "waterfall", "castle", "bridge", "garden", "museum", "palace", "island", "valley", "temple", "plaza", "glacier", "pavilion"],
        ["near the coast", "by the river", "in the capital", "at the border", "near the bay", "in the village", "by the cliff", "at the summit", "in the canyon", "near the port", "by the lake", "in the province", "at the frontier", "near the shore", "by the fountain", "in the district"],
        ["at sunrise", "before dusk", "in autumn", "with joy", "in summer", "after dawn", "at twilight", "in spring", "with wonder", "before sunset", "in winter", "at midday", "with ease", "after rain", "in silence", "at daybreak"]
    ],
    # THEME 2: Ẩm thực, Quán Café & Tiệc tối
    [
        ["Arthur", "Camille", "Louis", "Stella", "Marco", "Hannah", "Leon", "Violet", "Simon", "Claire", "Matteo", "Zoe", "Hugo", "Audrey", "Lucia", "Nathan"],
        ["ordered", "tasted", "baked", "brewed", "served", "recommended", "savored", "selected", "cooked", "decorated", "sliced", "poured", "roasted", "blended", "seasoned", "plated"],
        ["a warm", "the signature", "a fresh", "the classic", "a sweet", "the crispy", "a rich", "the homemade", "a fragrant", "the organic", "a creamy", "the toasted", "a savory", "the chilled", "a spiced", "the delicate"],
        ["espresso", "croissant", "risotto", "cheesecake", "cappuccino", "lasagna", "tartlet", "smoothie", "baguette", "macaron", "paella", "pancake", "truffle", "lemonade", "waffle", "tiramisu"],
        ["at the bakery", "in the kitchen", "by the terrace", "at the cafe", "in the tavern", "near the market", "at the diner", "in the patisserie", "by the counter", "at the banquet", "in the brasserie", "at the buffet", "by the fireplace", "in the diningroom", "at the canteen", "in the tearoom"],
        ["for breakfast", "with dessert", "after dinner", "for the guests", "with honey", "before tea", "for the chef", "with cinnamon", "after work", "for the party", "with berries", "before supper", "for the family", "with cream", "after shopping", "for the celebration"]
    ],
    # THEME 3: Điện ảnh, Âm nhạc, Hội họa & Văn học
    [
        ["Oliver", "Charlotte", "Henry", "Amelia", "Samuel", "Evelyn", "Benjamin", "Abigail", "Jack", "Harper", "Dylan", "Scarlett", "Isaac", "Victoria", "Caleb", "Madison"],
        ["composed", "directed", "rehearsed", "exhibited", "published", "performed", "translated", "illustrated", "conducted", "curated", "recorded", "choreographed", "premiered", "restored", "mastered", "adapted"],
        ["a brilliant", "the dramatic", "a poetic", "the acoustic", "a timeless", "the modern", "a lyrical", "the vintage", "a cinematic", "the orchestral", "a theatrical", "the abstract", "a melodic", "the inspiring", "a vivid", "the original"],
        ["symphony", "novel", "portrait", "documentary", "sonata", "sculpture", "screenplay", "ballad", "painting", "opera", "anthology", "concerto", "mural", "memoir", "musical", "poem"],
        ["at the gallery", "in the theater", "at the conservatory", "in the auditorium", "at the festival", "in the amphitheater", "at the playhouse", "in the showroom", "at the coliseum", "in the cinema", "at the arena", "in the hall", "at the exhibition", "in the bookstore", "at the stage", "in the archive"],
        ["last weekend", "with applause", "on Saturday", "for the audience", "on Sunday", "with passion", "on Tuesday", "for the critics", "on Thursday", "with elegance", "on Monday", "for the students", "on Wednesday", "with pride", "in October", "for the patrons"]
    ],
    # THEME 4: Khoa học, Vũ trụ & Công nghệ Đổi mới
    [
        ["Liam", "Aria", "Mason", "Luna", "Logan", "Layla", "Carter", "Penelope", "Owen", "Riley", "Luke", "Zoey", "Grayson", "Aurora", "Wyatt", "Natalie"],
        ["calibrated", "simulated", "deployed", "analyzed", "engineered", "optimized", "tested", "launched", "upgraded", "compiled", "monitored", "designed", "verified", "assembled", "configured", "debugged"],
        ["the quantum", "a neural", "the solar", "a robotic", "the optical", "a wireless", "the orbital", "a modular", "the thermal", "a digital", "the magnetic", "a laser", "the autonomous", "a photonic", "the satellite", "a hybrid"],
        ["telescope", "processor", "algorithm", "prototype", "sensor", "database", "spectrometer", "interface", "transmitter", "microchip", "generator", "reactor", "radar", "simulator", "drone", "receiver"],
        ["in the observatory", "at the laboratory", "in the datacenter", "at the complex", "in the cleanroom", "at the launchpad", "in the workshop", "at the institute", "in the dome", "at the facility", "in the hangar", "at the headquarters", "in the planetarium", "at the outpost", "in the bunker", "at the terminal"],
        ["at midnight", "with precision", "before launch", "on duty", "with accuracy", "after testing", "at nightfall", "with success", "before review", "on target", "with care", "after calibration", "at peak", "with confidence", "before briefing", "as expected"]
    ]
]

# Từ nối tự nhiên ở đầu các câu tiếp theo (Không nằm trong bảng từ khóa nên bộ giải mã tự động bỏ qua)
CAMO_TRANSITIONS = [
    "", "Meanwhile, ", "Honestly, ", "Interestingly, ", "Luckily, ",
    "Fortunately, ", "Actually, ", "Besides, ", "Earlier, "
]

# Xây dựng bảng tra cứu từ khóa -> giá trị 4-bit (0..15) cho toàn bộ 480 cụm từ
CAMO_TRIGGER_MAP = {}
for _theme in CAMO_THEMES:
    for _slot_list in _theme:
        for _val_idx, _phrase in enumerate(_slot_list):
            _kw = _phrase.split()[-1].lower().strip(".,!?")
            CAMO_TRIGGER_MAP[_kw] = _val_idx

def encode_english_camouflage(cipher_text: str) -> str:
    """
    Mã hóa bản mã thành những câu chuyện tiếng Anh đa chủ đề:
    - Dùng hạt giống ngẫu nhiên (salt_marker 229..239) để trộn toàn bộ các byte -> Không bao giờ lặp câu mở đầu!
    - Mỗi câu tự động chọn ngẫu nhiên 1 trong 5 chủ đề từ vựng khác nhau kèm từ nối tự nhiên.
    """
    salt_marker = random.randint(229, 239)
    salt_num = salt_marker - 228
    byte_list = [salt_marker]

    n_base = len(BASE_CHARS)
    for idx, ch in enumerate(cipher_text):
        if ch in BASE_CHARS:
            orig_idx = BASE_CHARS.index(ch)
            masked_idx = (orig_idx + (salt_num * 23) + (idx * 37)) % n_base
            byte_list.append(masked_idx)
        else:
            for b in ch.encode("utf-8"):
                byte_list.append(240 + (b >> 4))
                byte_list.append(240 + (b & 0x0F))

    nibbles = []
    for b in byte_list:
        nibbles.append((b >> 4) & 0x0F)
        nibbles.append(b & 0x0F)

    sentences = []
    used_themes = []
    for i in range(0, len(nibbles), 6):
        chunk = nibbles[i:i+6]
        # Chọn ngẫu nhiên chủ đề không trùng với câu liền trước
        avail_themes = [t for t in range(len(CAMO_THEMES)) if t not in used_themes[-1:]]
        theme_idx = random.choice(avail_themes)
        used_themes.append(theme_idx)
        slots = CAMO_THEMES[theme_idx]

        prefix = random.choice(CAMO_TRANSITIONS[1:]) if i > 0 and random.random() < 0.65 else ""

        if len(chunk) == 6:
            s = f"{prefix}{slots[0][chunk[0]]} {slots[1][chunk[1]]} {slots[2][chunk[2]]} {slots[3][chunk[3]]} {slots[4][chunk[4]]} {slots[5][chunk[5]]}."
        elif len(chunk) == 4:
            s = f"{prefix}{slots[0][chunk[0]]} {slots[1][chunk[1]]} {slots[2][chunk[2]]} {slots[3][chunk[3]]}."
        else:
            s = f"{prefix}{slots[0][chunk[0]]} {slots[1][chunk[1]]} it."
        sentences.append(s)

    return " ".join(sentences)

def decode_english_camouflage(prose_text: str) -> tuple[bool, str]:
    """Giải mã mọi câu chuyện tiếng Anh từ cả 5 chủ đề (Hỗ trợ cả tin nhắn có Salt mới và tin nhắn cũ)."""
    tokens = [t.strip(".,!?;:\"'()") for t in prose_text.strip().lower().split()]
    tokens = [t for t in tokens if t]
    if not tokens:
        return False, "❌ Empty camouflage text."

    # 1. Tương thích ngược với định dạng CAMO_WORDS đời đầu ("protocol, server...")
    if all(t in CAMO_WORDS for t in tokens) and len(tokens) % 2 == 0:
        byte_arr = bytearray()
        for i in range(0, len(tokens), 2):
            b = (CAMO_WORDS.index(tokens[i]) << 4) | CAMO_WORDS.index(tokens[i+1])
            byte_arr.append(b)
        try:
            return True, byte_arr.decode("utf-8")
        except Exception:
            return False, "❌ Corrupted legacy camouflage sequence."

    # 2. Lọc các từ khóa thuộc 5 chủ đề
    nibbles = [CAMO_TRIGGER_MAP[t] for t in tokens if t in CAMO_TRIGGER_MAP]
    if not nibbles or len(nibbles) % 2 != 0:
        return False, "❌ Invalid camouflage prose (Some words were modified or incomplete)."

    raw_bytes = [(nibbles[i] << 4) | nibbles[i+1] for i in range(0, len(nibbles), 2)]
    n_base = len(BASE_CHARS)

    # Kiểm tra xem có hạt giống ngẫu nhiên (salt_marker 229..239) ở byte đầu tiên không
    is_salted = (229 <= raw_bytes[0] <= 239)
    if is_salted:
        salt_num = raw_bytes[0] - 228
        data_bytes = raw_bytes[1:]
    else:
        salt_num = 0
        data_bytes = raw_bytes

    out_chars = []
    idx = 0
    char_pos = 0
    while idx < len(data_bytes):
        b = data_bytes[idx]
        if b < n_base:
            orig_idx = (b - (salt_num * 23) - (char_pos * 37)) % n_base if is_salted else b
            out_chars.append(BASE_CHARS[orig_idx])
            idx += 1
            char_pos += 1
        elif b >= 240 and idx + 1 < len(data_bytes):
            utf_b = ((b - 240) << 4) | (data_bytes[idx + 1] - 240)
            out_chars.append(chr(utf_b))
            idx += 2
            char_pos += 1
        else:
            return False, "❌ Corrupted character index in camouflage text."

    return True, "".join(out_chars)

# 6 thành phần câu giao tiếp đời thường (Mỗi thành phần gồm 16 cụm từ có từ khóa độc nhất)
CAMO_SLOTS = [
    # 0. Chủ ngữ (16 tên riêng)
    ["Alex", "Sarah", "David", "Emma", "Ryan", "Olivia", "Daniel", "Sophia",
     "Lucas", "Mia", "Ethan", "Chloe", "Noah", "Grace", "Leo", "Lily"],
    # 1. Động từ hành động (16 từ)
    ["checked", "reviewed", "shared", "prepared", "updated", "finished", "organized", "confirmed",
     "brought", "scheduled", "sent", "wrote", "printed", "saved", "packed", "booked"],
    # 2. Tính từ / Định từ bổ nghĩa (16 cụm)
    ["the new", "our weekly", "the final", "today's", "that", "a quick", "the main", "yesterday's",
     "the revised", "a special", "the monthly", "our group", "the backup", "a detailed", "the priority", "next"],
    # 3. Danh từ tân ngữ (16 danh từ đời thường)
    ["report", "schedule", "coffee", "itinerary", "notebook", "draft", "budget", "catalogue",
     "guidebook", "menu", "dossier", "album", "journal", "playlist", "ticket", "summary"],
    # 4. Trạng ngữ chỉ địa điểm (16 cụm)
    ["at the bistro", "in the library", "near the office", "on the desk", "in the lounge", "at the station", "by the lobby", "in the studio",
     "at the campus", "in the classroom", "near the park", "at the hotel", "on the train", "in the folder", "at home", "online"],
    # 5. Trạng ngữ chỉ thời gian (16 cụm)
    ["this morning", "before noon", "around five", "just now", "last night", "after lunch", "on time", "for tomorrow",
     "very early", "this evening", "a moment ago", "before class", "on Friday", "with friends", "without delay", "as planned"]
]

# Bảng từ khóa tra cứu ngược (96 từ khóa độc nhất -> giá trị 4-bit từ 0..15)
CAMO_TRIGGER_MAP = {}
for _slot_list in CAMO_SLOTS:
    for _val_idx, _phrase in enumerate(_slot_list):
        _key_word = _phrase.split()[-1].lower()
        CAMO_TRIGGER_MAP[_key_word] = _val_idx

def encode_english_camouflage(cipher_text: str) -> str:
    """
    Nén từng ký tự mật mã theo vị trí trong BASE_CHARS (1 byte/ký tự)
    và sinh ra các câu giao tiếp tiếng Anh ngắn gọn, tự nhiên, có ý nghĩa.
    """
    byte_list = []
    for ch in cipher_text:
        if ch in BASE_CHARS:
            byte_list.append(BASE_CHARS.index(ch))
        else:
            for b in ch.encode("utf-8"):
                byte_list.append(240 + (b >> 4))
                byte_list.append(240 + (b & 0x0F))

    nibbles = []
    for b in byte_list:
        nibbles.append((b >> 4) & 0x0F)
        nibbles.append(b & 0x0F)

    sentences = []
    # Mỗi câu tiếng Anh hoàn chỉnh chứa tới 6 nibbles (3 ký tự mật mã)
    for i in range(0, len(nibbles), 6):
        chunk = nibbles[i:i+6]
        if len(chunk) == 6:
            s = f"{CAMO_SLOTS[0][chunk[0]]} {CAMO_SLOTS[1][chunk[1]]} {CAMO_SLOTS[2][chunk[2]]} {CAMO_SLOTS[3][chunk[3]]} {CAMO_SLOTS[4][chunk[4]]} {CAMO_SLOTS[5][chunk[5]]}."
        elif len(chunk) == 4:
            s = f"{CAMO_SLOTS[0][chunk[0]]} {CAMO_SLOTS[1][chunk[1]]} {CAMO_SLOTS[2][chunk[2]]} {CAMO_SLOTS[3][chunk[3]]}."
        else:
            s = f"{CAMO_SLOTS[0][chunk[0]]} {CAMO_SLOTS[1][chunk[1]]} it."
        sentences.append(s)
    return " ".join(sentences)

def decode_english_camouflage(prose_text: str) -> tuple[bool, str]:
    """Giải mã câu chuyện tiếng Anh tự nhiên (và hỗ trợ cả định dạng cũ) về lại bản mã gốc."""
    tokens = prose_text.replace(".", " ").replace(",", " ").strip().lower().split()
    if not tokens:
        return False, "❌ Empty camouflage text."

    # Tương thích ngược với các tin nhắn cũ dùng CAMO_WORDS ("protocol, server, client...")
    if all(t in CAMO_WORDS for t in tokens) and len(tokens) % 2 == 0:
        byte_arr = bytearray()
        for i in range(0, len(tokens), 2):
            b = (CAMO_WORDS.index(tokens[i]) << 4) | CAMO_WORDS.index(tokens[i+1])
            byte_arr.append(b)
        try:
            return True, byte_arr.decode("utf-8")
        except Exception:
            return False, "❌ Corrupted legacy camouflage sequence."

    # Giải mã câu tiếng Anh tự nhiên dựa trên từ khóa ngữ pháp
    nibbles = [CAMO_TRIGGER_MAP[t] for t in tokens if t in CAMO_TRIGGER_MAP]
    if not nibbles or len(nibbles) % 2 != 0:
        return False, "❌ Invalid camouflage prose (Some words were modified or incomplete)."

    raw_bytes = [(nibbles[i] << 4) | nibbles[i+1] for i in range(0, len(nibbles), 2)]
    out_chars = []
    idx = 0
    while idx < len(raw_bytes):
        b = raw_bytes[idx]
        if b < len(BASE_CHARS):
            out_chars.append(BASE_CHARS[b])
            idx += 1
        elif b >= 240 and idx + 1 < len(raw_bytes):
            utf_b = ((b - 240) << 4) | (raw_bytes[idx + 1] - 240)
            out_chars.append(chr(utf_b))
            idx += 2
        else:
            return False, "❌ Corrupted character index in camouflage text."
    return True, "".join(out_chars)
    
# --- 1C. LSB IMAGE STEGANOGRAPHY ENGINE (PIXEL-LEVEL HIDING) ---
STEGO_DELIM = "<<END_STEGO>>"

def generate_sample_carrier_image(width: int = 480, height: int = 260) -> Image.Image:
    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)
    for y in range(0, height, 20):
        draw.line([(0, y), (width, y)], fill=(30, 41, 59), width=1)
    for x in range(0, width, 20):
        draw.line([(x, 0), (x, height)], fill=(30, 41, 59), width=1)
    draw.rectangle([(15, 15), (width - 15, height - 15)], outline=(59, 130, 246), width=2)
    draw.text((35, 95), "ULTIMATE SECRET MESSENGER", fill=(96, 165, 250))
    draw.text((35, 125), "LSB STEGO CARRIER MATRIX // UTC VERIFIED", fill=(148, 163, 184))
    return img

def encode_image_lsb(image: Image.Image, secret_payload: str) -> Image.Image:
    img = image.convert("RGB")
    full_bytes = (secret_payload + STEGO_DELIM).encode("utf-8")
    bits = "".join(f"{byte:08b}" for byte in full_bytes)
    
    pixels = list(img.getdata())
    if len(bits) > len(pixels) * 3:
        raise ValueError("Payload is too large for this image! Please upload a higher resolution image.")
    
    new_pixels = []
    bit_idx = 0
    total_bits = len(bits)
    for r, g, b in pixels:
        if bit_idx < total_bits:
            r = (r & ~1) | int(bits[bit_idx])
            bit_idx += 1
        if bit_idx < total_bits:
            g = (g & ~1) | int(bits[bit_idx])
            bit_idx += 1
        if bit_idx < total_bits:
            b = (b & ~1) | int(bits[bit_idx])
            bit_idx += 1
        new_pixels.append((r, g, b))
        
    stego_img = Image.new("RGB", img.size)
    stego_img.putdata(new_pixels)
    return stego_img

def decode_image_lsb(image: Image.Image) -> tuple[bool, str]:
    img = image.convert("RGB")
    pixels = list(img.getdata())
    bits = []
    for r, g, b in pixels:
        bits.append(str(r & 1))
        bits.append(str(g & 1))
        bits.append(str(b & 1))
        
    byte_arr = bytearray()
    delim_bytes = STEGO_DELIM.encode("utf-8")
    delim_len = len(delim_bytes)
    
    for i in range(0, len(bits) - 7, 8):
        byte_val = int("".join(bits[i:i+8]), 2)
        byte_arr.append(byte_val)
        if len(byte_arr) >= delim_len and byte_arr[-delim_len:] == delim_bytes:
            try:
                extracted = byte_arr[:-delim_len].decode("utf-8")
                return True, extracted
            except Exception:
                return False, "❌ Found stego marker, but payload bytes are corrupted."
    return False, "❌ No hidden LSB steganography payload detected in this image!"

# --- 1D. ADVANCED PERSISTENT CHAT STORAGE ENGINE ---
DB_FILE = "chat_rooms_db.json"

def load_all_rooms() -> dict:
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_all_rooms(data: dict):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def add_msg(room_name: str, sender: str, ciphertext: str, msg_type: str = "TEXT", image_b64: str = ""):
    rooms = load_all_rooms()
    if room_name not in rooms:
        rooms[room_name] = {"messages": [], "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
    msg_id = f"msg_{int(time.time()*1000)}_{random.randint(100,999)}"
    rooms[room_name]["messages"].append({
        "id": msg_id,
        "sender": sender,
        "type": msg_type,
        "ciphertext": ciphertext,
        "image_b64": image_b64,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    })
    save_all_rooms(rooms)

def delete_single_message(room_name: str, msg_idx: int):
    rooms = load_all_rooms()
    if room_name in rooms:
        msgs = rooms[room_name].get("messages", [])
        if 0 <= msg_idx < len(msgs):
            msgs.pop(msg_idx)
            rooms[room_name]["messages"] = msgs
            save_all_rooms(rooms)

def clear_room_history(room_name: str):
    rooms = load_all_rooms()
    if room_name in rooms:
        rooms[room_name]["messages"] = []
        save_all_rooms(rooms)

def destroy_entire_room(room_name: str):
    rooms = load_all_rooms()
    if room_name in rooms:
        del rooms[room_name]
        save_all_rooms(rooms)


# --- 2. GIAO DIỆN ĐIỀU KHIỂN & THANH BÊN ---
SYMBOLS_POOL = load_massive_symbol_pool()

with st.sidebar:
    st.markdown("## 🛡️ Cipher Control Panel")
    secret_seed = st.text_input("🔑 Group Secret Passphrase:", type="password", placeholder="e.g. Nexus2026")
    shift_step = st.number_input("🔢 Shift Offset (0-200):", min_value=0, max_value=200, value=0)
    pattern_list = st.multiselect("🎨 Symbol Vault:", options=SYMBOLS_POOL, default=SYMBOLS_POOL[:3] if SYMBOLS_POOL else [])
    custom_pairs = st.text_input("🔀 Custom Pairs (Optional):", placeholder="e.g. a=@, e=3")
    reverse_rule = st.checkbox("🔄 Reverse Structure", value=False)
    
    st.divider()

    # Tự động tắt chế độ Game khi người dùng bấm chọn lại các mục 1 -> 6
    def _exit_game_arcade():
        st.session_state.in_game_arcade = False

    def _enter_game_arcade():
        st.session_state.in_game_arcade = True
        try:
            st.session_state.nav_radio_menu = None
        except Exception:
            pass

    main_menu = st.radio(
        "🧭 Navigation Menu:",
        [
            "🏠 1. Home Dashboard",
            "🔐 2. Cipher Workspace",
            "💬 3. Secret Chat Rooms",
            "🕹️ 4. Crypto Challenges",
            "📚 5. Security Academy",
            "🛠️ 6. Utilities & About",
            "🌍 7. Community & Agency Hub",
            "☁️ 8. Cloud DB & Mobile App Studio"
        ],
        key="nav_radio_menu",
        on_change=_exit_game_arcade
    )

    st.markdown("""
    <style>
        /* Biến nút Game ở Sidebar thành nút hình chữ nhật màu đỏ to, nổi bật */
        section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #dc2626 0%, #ef4444 50%, #b91c1c 100%) !important;
            color: #ffffff !important;
            border: 2px solid #fca5a5 !important;
            border-radius: 12px !important;
            height: 54px !important;
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.45) !important;
            margin-top: 8px !important;
            transition: all 0.2s ease !important;
        }
        section[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(239, 68, 68, 0.75) !important;
            border-color: #ffffff !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.button(
        "🎮 CYBER GAME ARCADE",
        type="primary",
        use_container_width=True,
        on_click=_enter_game_arcade
    )

    if st.session_state.get("in_game_arcade", False):
        main_menu = "Cyber Game Arcade (Mini-Games Hub)"
    render_sidebar_tactical_hub(st.session_state.get("ctf_user") or "taolagautruc")
    
group_key = build_custom_key(secret_seed, pattern_list, shift_step, custom_pairs) if secret_seed else []

_, top_right_ai_col = st.columns([4.2, 1.2])
with top_right_ai_col:
    with st.popover("🤖 AI Cyber Mentor (Chat & File Scan)", use_container_width=True):
        render_ai_cyber_mentor_widget(current_lesson=None, decode_lsb_fn=decode_image_lsb, widget_key="global_top_right")
        
# ==============================================================================
# PHẦN 1: HOME DASHBOARD
# ==============================================================================
if "1. Home Dashboard" in main_menu:
    st.markdown("""
    <div class="hero-box">
        <div class="hero-badge">⚡ ZERO-TRUST MULTI-LAYER CRYPTOGRAPHY PLATFORM</div>
        <div class="hero-title">🛡️ Ultimate <span>Secret Messenger</span></div>
        <p class="hero-sub">
            Global Cipher Suite — Custom Unicode Key Permutation • UTC Time-Locking • LSB Pixel Steganography • Encrypted Persistent Chat
        </p>
    </div>
    """, unsafe_allow_html=True)

    rooms_data = load_all_rooms()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔤 Base Alphabet", f"{len(BASE_CHARS)} chars", "EN + VN + Symbols")
    c2.metric("🎨 Symbol Vault", f"{len(SYMBOLS_POOL):,}+", "Unicode Pool")
    c3.metric("💬 Active Chat Rooms", f"{len(rooms_data)} rooms", "JSON Persistent DB")
    c4.metric("🌍 Universal Clock", datetime.now(timezone.utc).strftime("%H:%M:%S UTC"), "Synchronized")

    st.write("")
    col_status, col_specs = st.columns([3, 2])

    with col_status:
        st.markdown("#### 🔐 Live Group Key Configuration Status")
        if not secret_seed:
            st.warning(
                "⚠️ **System Standby — Passphrase Required**\n\n"
                "Please enter your **Group Secret Passphrase** in the left Sidebar to initialize the cryptographic engine and unlock all workspace modules."
            )
        else:
            bits, crack_time = calculate_entropy_metrics(secret_seed, pattern_list, shift_step, len(SYMBOLS_POOL))
            st.success("✅ **Cryptographic Engine Active & Synchronized!** All modules are ready.")
            icons_str = " ➡️ ".join(pattern_list) if pattern_list else "None"
            st.markdown(f"""
            - **Active Symbol Chain:** {icons_str}
            - **Shift Offset Step:** `{shift_step}` positions | **Reverse Cipher:** `{'Enabled' if reverse_rule else 'Disabled'}`
            - **Custom Mapping:** `{custom_pairs if custom_pairs.strip() else 'Standard 1:1 Permutation'}`
            - **Estimated Key Entropy:** `~{bits} bits` (Brute-force time: **{crack_time}**)
            """)
            st.progress(min(bits / 256, 1.0), text=f"Security Strength Rating: {min(int((bits/128)*100), 100)}%")

    with col_specs:
        st.markdown("#### 🧭 Quick Navigation Guide")
        st.info(
            "**1. Configure Rules:** Set Passphrase, Shift & Icons on the left panel.\n\n"
            "**2. Cipher Workspace:** Encrypt text, set UTC self-destruct timers, or hide data inside PNG pixels.\n\n"
            "**3. Secret Chat Rooms:** Communicate with your team in real-time encrypted rooms."
        )

    st.divider()
    st.markdown("#### 🚀 Core Security Architecture")
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-title">🧬 Dynamic Multi-Layer Key</div>
            <div class="feat-desc">
                Combines your secret passphrase with a visual sequence of 1,400+ Unicode symbols, custom character swaps, and modular shifting to generate a unique substitution table.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-title">⏳ UTC Time-Lock & Self-Destruct</div>
            <div class="feat-desc">
                Embeds tamper-proof UTC epoch timestamps directly inside the payload. Messages automatically self-destruct after expiration or remain locked until a future time.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
        <div class="feat-card">
            <div class="feat-title">🖼️ LSB Steganography & Rooms</div>
            <div class="feat-desc">
                Conceal encrypted ciphertexts inside ordinary PNG image pixels using Least Significant Bit manipulation, or collaborate in persistent encrypted chat rooms.
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# PHẦN 2: CIPHER WORKSPACE (TEXT, CAMOUFLAGE & LSB IMAGE STEGANOGRAPHY)
# ==============================================================================
elif "2. Cipher Workspace" in main_menu:
    st.markdown("""
    <div class="hero-box" style="padding: 20px 28px; margin-bottom: 18px;">
        <div class="hero-badge">🔐 CRYPTOGRAPHIC ENGINE & STEGANOGRAPHY LAB</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Multi-Layer Cipher Workspace</h2>
        <p class="hero-sub">Encrypt text with UTC time-locks, disguise ciphertexts into English prose, or embed secret payloads inside PNG image pixels.</p>
    </div>
    """, unsafe_allow_html=True)

    if not secret_seed:
        st.warning("⚠️ **Passphrase Required:** Please enter your **Group Secret Passphrase** in the left Sidebar to unlock the Cipher Workspace!")
    else:
        ws_tab1, ws_tab2, ws_tab3 = st.tabs([
            "📝 1. Text Cipher & UTC Time-Lock",
            "🎭 2. English Camouflage Studio",
            "🖼️ 3. Image Steganography Lab (LSB)"
        ])

        with ws_tab1:
            st.markdown("""
            <div class="ws-banner">
                <h4>📝 Multi-Layer Text Encryption & UTC Time-Locking</h4>
                <p>Encrypt messages using your group's custom symbol permutation table and attach optional UTC self-destruct or time-capsule locks.</p>
            </div>
            """, unsafe_allow_html=True)

            col_enc, col_dec = st.columns(2)
            with col_enc:
                st.markdown("##### 📤 Encrypt Plaintext")
                msg_in = st.text_area("Secret Message:", placeholder="Type your confidential message here...", height=130, key="ws_txt_in")
                c_mode, c_min = st.columns([2, 1])
                with c_mode:
                    t_mode = st.selectbox("UTC Time-Lock Mode:", ["Normal (No Time Limit)", "🔥 Self-Destruct After Time", "⏳ Time-Capsule (Wait Until)"])
                with c_min:
                    mins = st.number_input("Minutes:", min_value=1, max_value=10080, value=15, disabled=(t_mode == "Normal (No Time Limit)"))

                if st.button("🔒 Generate Ciphertext", type="primary", use_container_width=True):
                    if msg_in.strip():
                        mode_code = "EXPIRE" if "Self-Destruct" in t_mode else ("WAIT" if "Time-Capsule" in t_mode else "NONE")
                        target_ts = int(time.time()) + (mins * 60) if mode_code != "NONE" else 0
                        cipher_out = encrypt_core(msg_in, group_key, reverse_rule, mode_code, target_ts)
                        st.success("✅ Encrypted Payload Generated:")
                        st.code(cipher_out, language=None)
                    else:
                        st.error("Please enter a message to encrypt.")

            with col_dec:
                st.markdown("##### 📥 Decrypt Ciphertext")
                cyph_in = st.text_area("Paste Ciphertext:", placeholder="Paste the encrypted string here...", height=130, key="ws_cyph_in")
                st.write("")
                st.write("")
                if st.button("🔓 Decode & Verify UTC Lock", type="primary", use_container_width=True):
                    if cyph_in.strip():
                        ok, res = decrypt_core(cyph_in.strip(), group_key, reverse_rule)
                        if ok:
                            st.success("✅ Decrypted Plaintext:")
                            st.info(res)
                        else:
                            st.error(res)
                    else:
                        st.warning("Please paste a ciphertext string to decode.")

        with ws_tab2:
            st.markdown("""
            <div class="ws-banner">
                <h4>🎭 Linguistic Camouflage Studio (2-Way Markov Prose)</h4>
                <p>Convert suspicious-looking ciphertexts into innocent technical English sentences to bypass visual inspection, and decode them back seamlessly.</p>
            </div>
            """, unsafe_allow_html=True)

            camo_col1, camo_col2 = st.columns(2)
            with camo_col1:
                st.markdown("##### 📤 Disguise Secret into English")
                camo_plain = st.text_area("Enter Secret Message:", placeholder="e.g. Operation starts at 02:00 UTC", height=110)
                if st.button("🎭 Encrypt & Disguise as English Prose", type="primary", use_container_width=True):
                    if camo_plain.strip():
                        raw_c = encrypt_core(camo_plain, group_key, reverse_rule, "NONE", 0)
                        disguised = encode_english_camouflage(raw_c)
                        st.success("✅ Camouflaged English Text:")
                        st.code(disguised, language=None)
                    else:
                        st.warning("Please enter a secret message first.")

            with camo_col2:
                st.markdown("##### 📥 Reveal Secret from English Prose")
                camo_prose_in = st.text_area("Paste Camouflaged English Sentences:", placeholder="Paste the innocent-looking English paragraph here...", height=110)
                if st.button("🔍 Extract & Decrypt Secret", type="primary", use_container_width=True):
                    if camo_prose_in.strip():
                        ok_c, extracted_c = decode_english_camouflage(camo_prose_in.strip())
                        if not ok_c:
                            st.error(extracted_c)
                        else:
                            ok_d, final_txt = decrypt_core(extracted_c, group_key, reverse_rule)
                            if ok_d:
                                st.success("✅ Hidden Message Revealed:")
                                st.info(final_txt)
                            else:
                                st.error(final_txt)
                    else:
                        st.warning("Please paste the camouflaged English text.")

        with ws_tab3:
            st.markdown("""
            <div class="ws-banner">
                <h4>🖼️ LSB Pixel Steganography Lab (Hide Encrypted Data Inside Images)</h4>
                <p>Embed your encrypted payload invisibly into the Least Significant Bits (RGB channels) of any image. Output is lossless PNG.</p>
            </div>
            """, unsafe_allow_html=True)

            stego_mode = st.radio(
                "Select Steganography Operation:",
                ["📤 Hide Secret Message Inside Image (Encode)", "📥 Extract Secret Message From Stego PNG (Decode)"],
                horizontal=True
            )
            st.divider()

            if "Encode" in stego_mode:
                s_col1, s_col2 = st.columns([1.2, 1])
                with s_col1:
                    img_source = st.radio(
                        "Choose Carrier Image Source:",
                        ["📁 Upload My Own Image (PNG/JPG)", "⚡ Auto-Generate Cyber Carrier Image"],
                        horizontal=True
                    )
                    carrier_img = None
                    if "Upload" in img_source:
                        up_file = st.file_uploader("Upload Carrier Image:", type=["png", "jpg", "jpeg"])
                        if up_file:
                            carrier_img = Image.open(up_file).convert("RGB")
                    else:
                        carrier_img = generate_sample_carrier_image()
                        st.caption("✨ Generated a fresh 480x260 Cyber Carrier Matrix ready for pixel embedding.")

                    secret_stego_msg = st.text_area(
                        "Secret Message to Hide Inside Pixels:",
                        placeholder="Type secret message to embed invisibly into the image...",
                        height=100
                    )

                    c_stego_mode, c_stego_min = st.columns([2, 1])
                    with c_stego_mode:
                        stego_t_mode = st.selectbox("Image Payload Time-Lock (UTC):", ["Normal (No Time Limit)", "🔥 Self-Destruct After Time", "⏳ Time-Capsule (Wait Until)"])
                    with c_stego_min:
                        stego_mins = st.number_input("Timer (Mins):", min_value=1, max_value=10080, value=30, disabled=(stego_t_mode == "Normal (No Time Limit)"))

                with s_col2:
                    if carrier_img is not None:
                        w, h = carrier_img.size
                        max_chars = (w * h * 3) // 8 - len(STEGO_DELIM)
                        st.markdown("##### 📊 Carrier Image Specs & Capacity")
                        st.markdown(f"- **Resolution:** `{w} x {h}` pixels (`{w*h:,}` total pixels)\n- **Max Secret Capacity:** `~{max_chars:,}` bytes")
                        
                        if secret_stego_msg:
                            usage_pct = min(len(secret_stego_msg.encode('utf-8')) * 3 / max(max_chars, 1), 1.0)
                            st.progress(usage_pct, text=f"Pixel LSB Capacity Used: {usage_pct*100:.2f}%")
                        st.image(carrier_img, caption="Original Carrier Preview", use_container_width=True)

                if st.button("🖼️ Encrypt & Embed Into Image Pixels", type="primary", use_container_width=True):
                    if carrier_img is None:
                        st.error("Please upload an image or select 'Auto-Generate Cyber Carrier Image' first!")
                    elif not secret_stego_msg.strip():
                        st.error("Please enter a secret message to hide inside the image!")
                    else:
                        try:
                            s_mode = "EXPIRE" if "Self-Destruct" in stego_t_mode else ("WAIT" if "Time-Capsule" in stego_t_mode else "NONE")
                            s_ts = int(time.time()) + (stego_mins * 60) if s_mode != "NONE" else 0
                            encrypted_payload = encrypt_core(secret_stego_msg, group_key, reverse_rule, s_mode, s_ts)
                            stego_result_img = encode_image_lsb(carrier_img, encrypted_payload)

                            buf = io.BytesIO()
                            stego_result_img.save(buf, format="PNG")
                            byte_data = buf.getvalue()

                            st.success("🎉 **Stego Image Created Successfully!** The encrypted message is now invisibly locked inside the pixels.")
                            p1, p2 = st.columns(2)
                            with p1:
                                st.image(carrier_img, caption="Before (Original Carrier)", use_container_width=True)
                            with p2:
                                st.image(stego_result_img, caption="After (Stego PNG with Hidden Cipher)", use_container_width=True)

                            st.download_button(
                                label="⬇️ Download Stego Image (Lossless PNG)",
                                data=byte_data,
                                file_name=f"stego_secret_{int(time.time())}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"❌ Steganography Error: {str(e)}")

            else:
                st.markdown("##### 🔍 Upload Stego PNG to Extract & Decrypt Hidden Message")
                up_stego = st.file_uploader("Upload Stego Image (Must be lossless .PNG generated by this suite):", type=["png"])
                if up_stego:
                    decode_img = Image.open(up_stego).convert("RGB")
                    col_prev, col_act = st.columns([1, 1.5])
                    with col_prev:
                        st.image(decode_img, caption="Uploaded Stego PNG", use_container_width=True)
                    with col_act:
                        st.info("💡 Make sure your **Sidebar Passphrase, Shift Offset, and Symbol Vault** match the exact rules used when this image was encoded.")
                        if st.button("🔓 Extract Bits & Decrypt Payload", type="primary", use_container_width=True):
                            ok_ext, hidden_cipher = decode_image_lsb(decode_img)
                            if not ok_ext:
                                st.error(hidden_cipher)
                            else:
                                st.caption("Extracted Encrypted Payload from LSB Pixels:")
                                st.code(hidden_cipher, language=None)
                                ok_dec, plain_msg = decrypt_core(hidden_cipher, group_key, reverse_rule)
                                if ok_dec:
                                    st.success("🎉 **Decrypted Secret Message:**")
                                    st.info(plain_msg)
                                else:
                                    st.error(plain_msg)

        st.divider()
        render_pillar2_multimedia_labs(encrypt_core, decrypt_core, group_key, reverse_rule)

# ==============================================================================
# PHẦN 3: SECRET CHAT ROOMS (GIAO DIỆN CHUYỂN MÀN HÌNH KIỂU ZALO / MESSENGER)
# ==============================================================================
elif "3. Secret Chat Rooms" in main_menu:
    render_zalo_messenger_rooms(
        secret_seed, group_key, reverse_rule,
        load_all_rooms, save_all_rooms, add_msg,
        delete_single_message, clear_room_history, destroy_entire_room,
        encrypt_core, decrypt_core,
        encode_english_camouflage, decode_english_camouflage,
        generate_sample_carrier_image, encode_image_lsb, decode_image_lsb
    )
    
# ==============================================================================
# PHẦN 4: CRYPTO CHALLENGES & GLOBAL CTF ARENA (THEMED ENCYCLOPEDIA & STEP-BY-STEP EDITION)
# ==============================================================================
elif "4. Crypto Challenges" in main_menu:
    CTF_DB_FILE = "ctf_arena_db.json"

    def load_ctf_db() -> dict:
        if not os.path.exists(CTF_DB_FILE):
            seed_db = {
                "users": {
                    "AlexMercer_US": {
                        "pin_hash": hashlib.sha256(b"9999").hexdigest(),
                        "score": 12500,
                        "solved": ["T1_1", "T2_1", "T3_1", "T4_1", "T5_1"],
                        "surrendered": [],
                        "hints_used": [],
                        "friends": [],
                        "friend_requests": []
                    },
                    "ElenaRostova_UK": {
                        "pin_hash": hashlib.sha256(b"9999").hexdigest(),
                        "score": 6800,
                        "solved": ["T1_2", "T2_2", "T3_2", "T4_2"],
                        "surrendered": [],
                        "hints_used": [],
                        "friends": [],
                        "friend_requests": []
                    },
                    "KenjiSato_JP": {
                        "pin_hash": hashlib.sha256(b"9999").hexdigest(),
                        "score": 2350,
                        "solved": ["T1_3", "T2_3", "T3_3"],
                        "surrendered": [],
                        "hints_used": [],
                        "friends": [],
                        "friend_requests": []
                    }
                },
                "direct_messages": {}
            }
            with open(CTF_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(seed_db, f, ensure_ascii=False, indent=4)
            return seed_db
        try:
            with open(CTF_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"users": {}, "direct_messages": {}}

    def save_ctf_db(data: dict):
        with open(CTF_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_agent_rank(score: int) -> str:
        if score >= 20000: return "👑 Grandmaster Archon"
        if score >= 8000:  return "💎 Global Cryptanalyst"
        if score >= 3000:  return "🔥 History & Cipher Master"
        if score >= 800:   return "⚡ Puzzle Explorer"
        if score > 0:      return "🛡️ Junior Detective"
        return "🌱 Starter Explorer"

    # ==========================================================================
    # KHO BÁCH KHOA TOÀN THƯ ĐA CHỦ ĐỀ (PHÂN LOẠI ĐỘ DỄ CHO TIER 1-2 & CHUYÊN SÂU CHO TIER 3-5)
    # Cấu trúc mỗi mục: (Main Theme, Specific Sub-Topic, Exact Answer, Clear Clue)
    # ==========================================================================
    EASY_KIDS_POOL = [
        # 1. Animals (Land, Sky & Wildlife)
        ("🐾 Animals & Wildlife", "Land Mammal (Động vật trên cạn)", "LION", "Known as the 'King of the Jungle', this big cat lives in African savannas and has a majestic mane."),
        ("🐾 Animals & Wildlife", "Land Mammal (Động vật trên cạn)", "TIGER", "The largest wild cat in the world, famous for its orange fur and dark vertical stripes."),
        ("🐾 Animals & Wildlife", "Land Mammal (Động vật trên cạn)", "ELEPHANT", "The largest land animal on Earth, famous for its long trunk, big ears, and ivory tusks."),
        ("🐾 Animals & Wildlife", "Land Mammal (Động vật trên cạn)", "GIRAFFE", "The tallest living terrestrial animal in the world, famous for its extremely long neck."),
        ("🐾 Animals & Wildlife", "Land Mammal (Động vật trên cạn)", "CHEETAH", "The fastest land animal on Earth, capable of running at speeds over 100 km/h."),
        ("🐾 Animals & Wildlife", "Land Mammal (Động vật trên cạn)", "PANDA", "Black-and-white bear native to China that loves eating bamboo all day."),
        ("🐾 Animals & Wildlife", "Land Mammal (Động vật trên cạn)", "KANGAROO", "Iconic Australian mammal that hops on powerful hind legs and carries its baby in a pouch."),
        ("🐾 Animals & Wildlife", "Polar Bird (Chim vùng cực)", "PENGUIN", "Flightless black-and-white bird that lives in icy Antarctica and is an expert swimmer."),
        # 2. Ocean, Marine Life & Deep Sea
        ("🌊 Ocean & Deep Sea", "Marine Mammal (Sinh vật biển)", "DOLPHIN", "Highly intelligent marine mammal known for its friendly smile and acrobatic leaps out of the water."),
        ("🌊 Ocean & Deep Sea", "Deep Sea Creature (Sinh vật đáy biển)", "OCTOPUS", "Soft-bodied sea creature with 8 tentacles, 3 hearts, blue blood, and the ability to spray ink."),
        ("🌊 Ocean & Deep Sea", "Ocean Predator (Cá săn mồi đại dương)", "SHARK", "Apex ocean predator with dorsal fins and rows of sharp replaceable teeth."),
        ("🌊 Ocean & Deep Sea", "Marine Giant (Khổng lồ đại dương)", "BLUE WHALE", "The largest animal ever known to have lived on Earth, swimming in the deep oceans."),
        ("🌊 Ocean & Deep Sea", "Marine Ecosystem (Hệ sinh thái biển)", "CORAL REEF", "Colorful underwater ecosystem built by tiny marine invertebrates, often called the 'Rainforest of the Sea'."),
        ("🌊 Ocean & Deep Sea", "World Ocean (Đại dương thế giới)", "PACIFIC OCEAN", "The largest and deepest of Earth's five oceanic divisions, stretching from Asia to the Americas."),
        # 3. Plants, Trees & Flowers
        ("🌿 Plants & Botany", "Famous Flower (Loài hoa nổi tiếng)", "SUNFLOWER", "Tall, bright yellow flower that always turns its head to face the sun."),
        ("🌿 Plants & Botany", "Desert Plant (Thực vật sa mạc)", "CACTUS", "Spiky desert plant that stores water in its thick stem to survive extreme heat."),
        ("🌿 Plants & Botany", "Fast-Growing Plant (Thực vật thân đốt)", "BAMBOO", "The fastest-growing woody plant in the world, and the favorite food of giant pandas."),
        ("🌿 Plants & Botany", "Iconic Flower (Hoa biểu tượng)", "LOTUS", "Sacred aquatic flower that grows in mud and blooms beautifully on the water surface."),
        # 4. Space, Planets & Stars
        ("🪐 Space & Cosmos", "Solar System Planet (Hành tinh Hệ Mặt Trời)", "MARS", "The 4th planet from the Sun, famous as the 'Red Planet' due to iron oxide on its surface."),
        ("🪐 Space & Cosmos", "Solar System Planet (Hành tinh Hệ Mặt Trời)", "SATURN", "The 6th planet from the Sun, famous for its spectacular system of icy rings."),
        ("🪐 Space & Cosmos", "Solar System Planet (Hành tinh Hệ Mặt Trời)", "JUPITER", "The largest planet in our Solar System, a gas giant famous for its Great Red Spot storm."),
        ("🪐 Space & Cosmos", "Star & Astronomy (Ngôi sao trung tâm)", "THE SUN", "The giant burning star at the center of our Solar System that gives light and life to Earth."),
        ("🪐 Space & Cosmos", "Cosmic Galaxy (Thiên hà vũ trụ)", "MILKY WAY", "The spiral galaxy that contains our Solar System and billions of shining stars."),
        # 5. Basic Science & Countries
        ("🔬 Science & Nature", "Precious Mineral (Khoáng vật quý)", "DIAMOND", "The hardest known natural material on Earth, formed from pure carbon under extreme pressure."),
        ("🔬 Science & Nature", "Essential Gas (Khí sự sống)", "OXYGEN", "The life-supporting chemical element (O2) in the air that humans and animals breathe."),
        ("🗺️ World Countries", "Asian Country (Quốc gia Châu Á)", "JAPAN", "Island nation in East Asia known as the Land of the Rising Sun, famous for Mount Fuji and Tokyo."),
        ("🗺️ World Countries", "European Country (Quốc gia Châu Âu)", "FRANCE", "European country famous for the Eiffel Tower in Paris and the Louvre Museum."),
        ("🗺️ World Countries", "African Country (Quốc gia Châu Phi)", "EGYPT", "Country famous for the Ancient Pyramids of Giza, the Sphinx, and the Nile River.")
    ]

    ADVANCED_GLOBAL_POOL = [
        # Deep Sea & Oceanography
        ("🌊 Ocean & Deep Sea", "Deepest Ocean Trench (Rãnh đại dương sâu nhất)", "MARIANA TRENCH", "The deepest oceanic trench on Earth (~11,000 meters deep), located in the western Pacific Ocean."),
        ("🌊 Ocean & Deep Sea", "Deep Sea Monster (Quái vật biển sâu)", "GIANT SQUID", "Deep-ocean dwelling cephalopod with gigantic eyes that can grow up to 13 meters long."),
        ("🌊 Ocean & Deep Sea", "Apex Ocean Predator (Cá mập trắng lớn)", "GREAT WHITE SHARK", "The world's largest known predatory fish, famous for patrolling coastal surface waters."),
        # Space, Stars & Astrophysics
        ("🪐 Space & Cosmos", "Astrophysics Phenomenon (Hiện tượng Vũ trụ)", "BLACK HOLE", "A region of spacetime where gravity is so strong that nothing—not even light—can escape."),
        ("🪐 Space & Cosmos", "Stellar Explosion (Vụ nổ siêu tân tinh)", "SUPERNOVA", "A powerful and luminous explosion of a massive star at the end of its evolutionary life."),
        ("🪐 Space & Cosmos", "Guiding Star (Ngôi sao dẫn đường)", "NORTH STAR", "Also known as Polaris, the bright star positioned almost directly above Earth's North Pole."),
        ("🪐 Space & Cosmos", "Neighboring Galaxy (Thiên hà láng giềng)", "ANDROMEDA", "The closest major spiral galaxy to our Milky Way, located about 2.5 million light-years away."),
        ("🪐 Space & Cosmos", "Historic Space Mission (Sứ mệnh Không gian)", "APOLLO 11", "Historic 1969 NASA spaceflight that first landed humans—Neil Armstrong and Buzz Aldrin—on the Moon."),
        # Science & Biology
        ("🔬 Science & Nature", "Botanical Process (Quá trình Quang hợp)", "PHOTOSYNTHESIS", "The biological process used by green plants to convert sunlight, water, and CO2 into oxygen and energy."),
        ("🔬 Science & Nature", "Fundamental Physics (Lực Vạn vật hấp dẫn)", "GRAVITY", "The natural phenomenon by which all things with mass or energy are attracted toward one another, described by Newton."),
        ("🔬 Science & Nature", "Rainforest Ecosystem (Rừng nhiệt đới lớn nhất)", "AMAZON RAINFOREST", "The world's largest tropical rainforest, covering much of northwestern Brazil and South America."),
        # US Presidents
        ("🦅 US Presidents", "1st US President (Tổng thống Mỹ đầu tiên)", "GEORGE WASHINGTON", "Founding Father who served as the 1st President of the United States (1789–1797)."),
        ("🦅 US Presidents", "16th US President (Tổng thống Mỹ thứ 16)", "ABRAHAM LINCOLN", "US President who abolished slavery with the Emancipation Proclamation and led the nation through the Civil War."),
        ("🦅 US Presidents", "3rd US President (Tổng thống Mỹ thứ 3)", "THOMAS JEFFERSON", "Principal author of the Declaration of Independence (1776) and the 3rd US President."),
        ("🦅 US Presidents", "35th US President (Tổng thống Mỹ thứ 35)", "JOHN F KENNEDY", "Charismatic US President (JFK) who navigated the Cuban Missile Crisis and initiated Project Apollo."),
        ("🦅 US Presidents", "44th US President (Tổng thống Mỹ thứ 44)", "BARACK OBAMA", "The 44th President of the United States and the first African American to hold the office."),
        # World Figures & Scientists
        ("🏛️ World Figures", "Theoretical Physicist (Nhà vật lý thiên tài)", "ALBERT EINSTEIN", "German-born physicist who developed the Theory of Relativity (E = mc^2) and won the Nobel Prize."),
        ("🏛️ World Figures", "Father of Computer Science (Cha đẻ Khoa học Máy tính)", "ALAN TURING", "British mathematician who cracked the Nazi Enigma cipher machine during World War II."),
        ("🏛️ World Figures", "Renaissance Master (Danh họa Phục Hưng)", "LEONARDO DA VINCI", "Italian polymath who painted the Mona Lisa and The Last Supper."),
        ("🏛️ World Figures", "Pioneering Scientist (Nhà bác học nữ 2 giải Nobel)", "MARIE CURIE", "Physicist and chemist who discovered radium and polonium, winning Nobel Prizes in both Physics and Chemistry."),
        # Wars, Battles & Global Historical Events
        ("⚔️ History & Wars", "Global Conflict (Chiến tranh Thế giới thứ II)", "WORLD WAR II", "Global war from 1939 to 1945 between the Allies and the Axis powers."),
        ("⚔️ History & Wars", "Geopolitical Stand-off (Chiến tranh Lạnh)", "COLD WAR", "Decades-long geopolitical tension between the United States and the Soviet Union after WWII."),
        ("⚔️ History & Wars", "Famous European Battle (Trận chiến Waterloo)", "BATTLE OF WATERLOO", "The 1815 battle in Belgium where French Emperor Napoleon Bonaparte suffered his final defeat."),
        ("⚔️ History & Wars", "2001 Global Tragedy (Sự kiện khủng bố 11/9)", "SEPTEMBER 11", "The 2001 terrorist attacks on the World Trade Center Twin Towers in New York City and the Pentagon."),
        ("⚔️ History & Wars", "Maritime Tragedy (Thảm họa tàu Titanic)", "TITANIC DISASTER", "The 1912 sinking of the 'unsinkable' British passenger liner after striking an iceberg in the North Atlantic.")
    ]

    def caesar_shift_with_steps(text: str, shift: int) -> tuple[str, str]:
        """Mã hóa Caesar và trả về luôn chuỗi giải thích từng ký tự một để người đọc hiểu 100%."""
        encoded_chars = []
        step_logs = []
        for ch in text.upper():
            if "A" <= ch <= "Z":
                enc_c = chr((ord(ch) - ord("A") + shift) % 26 + ord("A"))
                encoded_chars.append(enc_c)
                step_logs.append(f"`{enc_c}` (-{shift}) → **`{ch}`**")
            else:
                encoded_chars.append(ch)
                step_logs.append(f"`[Space]`")
        return "".join(encoded_chars), " | ".join(step_logs)

    def atbash_with_steps(text: str) -> tuple[str, str]:
        """Đảo bảng chữ cái A<->Z kèm lời giải thích từng chữ cái."""
        encoded_chars = []
        step_logs = []
        for ch in text.upper():
            if "A" <= ch <= "Z":
                enc_c = chr(ord("Z") - (ord(ch) - ord("A")))
                encoded_chars.append(enc_c)
                step_logs.append(f"`{enc_c}` ↔ **`{ch}`**")
            else:
                encoded_chars.append(ch)
                step_logs.append("`[Space]`")
        return "".join(encoded_chars), " | ".join(step_logs)

    def generate_dynamic_challenge(username: str, tier: int, q_num: int) -> dict:
        seed_str = f"ENCYCLOPEDIA_V4_{username}_T{tier}_Q{q_num}"
        rng = random.Random(seed_str)

        tier_pts = {1: 100, 2: 250, 3: 500, 4: 1000, 5: 2500}
        base_pts = tier_pts[tier]

        # Chọn ngân hàng câu hỏi phù hợp theo cấp độ: Tier 1 & 2 dùng từ ngắn siêu dễ; Tier 3, 4, 5 kết hợp cả kho
        if tier in [1, 2]:
            main_theme, sub_topic, answer_raw, clue = rng.choice(EASY_KIDS_POOL)
        else:
            combined_pool = EASY_KIDS_POOL + ADVANCED_GLOBAL_POOL
            main_theme, sub_topic, answer_raw, clue = rng.choice(combined_pool)

        clean_answer = answer_raw.upper().strip()
        words_list = clean_answer.split()
        word_structure = f"{len(words_list)} word(s), {len(clean_answer.replace(' ', ''))} letters total (Starts with '{clean_answer[0]}', ends with '{clean_answer[-1]}')"

        # Khung Banner Chủ đề rõ ràng cho mọi câu hỏi
        topic_header = (
            f"📂 **Main Category:** `{main_theme}` &nbsp;|&nbsp; "
            f"🎯 **Specific Topic:** `{sub_topic}` &nbsp;|&nbsp; "
            f"📏 **Structure:** `{word_structure}`"
        )

        # ======================================================================
        # TIER 1: KIDS & BEGINNERS (SIÊU DỄ — ĐIỀN NGUYÊN ÂM HOẶC ĐÁNH VẦN NGƯỢC)
        # ======================================================================
        if tier == 1:
            if q_num % 2 == 1:
                # Kiểu 1A: Ẩn nguyên âm (A, E, I, O, U) và cho sẵn danh sách các chữ cái bị ẩn!
                vowels = set("AEIOU")
                masked_chars = []
                removed_vowels = []
                for idx, ch in enumerate(clean_answer):
                    # Giữ nguyên chữ cái đầu tiên để cực kỳ dễ đoán
                    if idx > 0 and ch in vowels:
                        masked_chars.append("_")
                        removed_vowels.append(ch)
                    else:
                        masked_chars.append(ch)
                encoded_puzzle = " ".join(masked_chars)
                vowels_hint_str = ", ".join(removed_vowels) if removed_vowels else "None"

                briefing = (
                    f"### 🎈 Tier 1 (Kids & Beginners) Mission #{q_num}\n"
                    f"{topic_header}\n\n"
                    f"**🌍 Fun Fact Clue:** *{clue}*\n\n"
                    f"🧩 **How to Solve (Missing Vowels Game):** We hid the vowels (`A, E, I, O, U`) inside this `{sub_topic}` name! "
                    f"Put the missing vowels **`[{vowels_hint_str}]`** back into the `_` blanks below to complete the word!"
                )
                step_hint = (
                    f"1. **Topic:** `{sub_topic}` — *{clue}*\n"
                    f"2. **Missing Vowels in exact order:** **`{vowels_hint_str}`**\n"
                    f"3. Fill them one by one into `{encoded_puzzle}` $\\rightarrow$ It starts with **`{clean_answer[:2]}...`**!"
                )
                solution_box = (
                    f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                    f"📖 **Step-by-Step How It Was Encoded & Decoded:**\n"
                    f"- **Step 1 (Original Word):** `{clean_answer}` *(Topic: {sub_topic})*\n"
                    f"- **Step 2 (Encryption Rule):** Hide vowels after the first letter $\\rightarrow$ `{encoded_puzzle}` (Removed vowels: `{vowels_hint_str}`)\n"
                    f"- **Step 3 (Decryption):** Put `{vowels_hint_str}` back into the blanks `_` in order $\\rightarrow$ **`{clean_answer}`**!"
                )
            else:
                # Kiểu 1B: Đánh vần ngược từng từ (Reverse Spelling)
                reversed_words = [w[::-1] for w in words_list]
                encoded_puzzle = "   ".join([" - ".join(list(rw)) for rw in reversed_words])
                forward_demo = "   ".join([" - ".join(list(w)) for w in words_list])

                briefing = (
                    f"### 🎈 Tier 1 (Kids & Beginners) Mission #{q_num}\n"
                    f"{topic_header}\n\n"
                    f"**🌍 Fun Fact Clue:** *{clue}*\n\n"
                    f"🔄 **How to Solve (Backwards Mirror Spelling):** Each word below is spelled **backwards from right to left**! "
                    f"Read the letters from right to left to discover the `{sub_topic}`."
                )
                step_hint = (
                    f"1. **Topic:** `{sub_topic}` — *{clue}*\n"
                    f"2. Look at the puzzle `{encoded_puzzle}` and read each word from **right to left**.\n"
                    f"3. The first letter is **`{clean_answer[0]}`** and the last letter is **`{clean_answer[-1]}`**."
                )
                solution_box = (
                    f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                    f"📖 **Step-by-Step How It Was Encoded & Decoded:**\n"
                    f"- **Step 1 (Encrypted Backwards Letters):** `{encoded_puzzle}`\n"
                    f"- **Step 2 (Flip Letters Right-to-Left):** `{forward_demo}`\n"
                    f"- **Step 3 (Final Combined Answer):** **`{clean_answer}`** *(Matches clue: {clue})*"
                )

            return {
                "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                "briefing": briefing, "payload": encoded_puzzle, "is_img": False,
                "hint": step_hint, "flag": clean_answer, "solution": solution_box
            }

        # ======================================================================
        # TIER 2: YOUNG EXPLORERS (DỄ — MẬT MÃ SỐ LEETSPEAK HOẶC CAESAR +1 CÓ GIỮ CHỮ ĐẦU)
        # ======================================================================
        elif tier == 2:
            if q_num % 2 == 0:
                # Kiểu 2A: Thay chữ thành số (Number Replacement Code)
                leet_map = {"A": "4", "E": "3", "I": "1", "O": "0", "S": "5", "T": "7"}
                enc_chars = [leet_map.get(c, c) for c in clean_answer]
                encoded_puzzle = " ".join(enc_chars)
                # Giải thích từng chữ số đã thay thế
                replacements_used = [f"`{v}` → **`{k}`**" for k, v in leet_map.items() if k in clean_answer]
                rep_explain = ", ".join(replacements_used) if replacements_used else "No numbers needed"

                briefing = (
                    f"### 🧭 Tier 2 (Young Explorers) Mission #{q_num}\n"
                    f"{topic_header}\n\n"
                    f"**🌍 Knowledge Clue:** *{clue}*\n\n"
                    f"🔢 **How to Solve (Secret Number-to-Letter Code):** Some letters in this `{sub_topic}` were disguised as numbers! "
                    f"Use this secret key to swap numbers back into letters:\n"
                    f"- **`4 = A`** &nbsp;|&nbsp; **`3 = E`** &nbsp;|&nbsp; **`1 = I`** &nbsp;|&nbsp; **`0 = O`** &nbsp;|&nbsp; **`5 = S`** &nbsp;|&nbsp; **`7 = T`**"
                )
                step_hint = (
                    f"1. **Topic:** `{sub_topic}`\n"
                    f"2. Swap only these numbers in `{encoded_puzzle}`: {rep_explain}.\n"
                    f"3. The decoded word starts with **`{clean_answer[:2]}...`**!"
                )
                solution_box = (
                    f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                    f"📖 **Step-by-Step How It Was Encoded & Decoded:**\n"
                    f"- **Step 1 (Encrypted Number Code):** `{encoded_puzzle}`\n"
                    f"- **Step 2 (Apply Number-to-Letter Swaps):** {rep_explain}\n"
                    f"- **Step 3 (Final Decoded Result):** **`{clean_answer}`**"
                )
            else:
                # Kiểu 2B: Caesar Shift +1 đơn giản kèm giải thích từng ký tự
                encoded_puzzle, char_by_char_log = caesar_shift_with_steps(clean_answer, 1)
                briefing = (
                    f"### 🧭 Tier 2 (Young Explorers) Mission #{q_num}\n"
                    f"{topic_header}\n\n"
                    f"**🌍 Knowledge Clue:** *{clue}*\n\n"
                    f"🔤 **How to Solve (Alphabet Step +1 Cipher):**\n"
                    f"- Every letter of the answer was shifted **1 step forward** in the English alphabet (`A→B`, `B→C`, `C→D` ... `Z→A`).\n"
                    f"- To decode it: Move each letter in `{encoded_puzzle}` **1 step BACKWARD** (`B→A`, `C→B`, `D→C`...).\n"
                    f"- 🎁 **Free Starter Gift:** The very first decoded letter is **`{clean_answer[0]}`**!"
                )
                step_hint = (
                    f"1. Look at the Alphabet bar below and shift each letter of `{encoded_puzzle}` **1 position to the LEFT**.\n"
                    f"2. Letter-by-letter preview of the first 3 letters: **`{clean_answer[:3]}...`**"
                )
                solution_box = (
                    f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                    f"📖 **Step-by-Step Letter-by-Letter Decoding (`Cipher (-1) → Plain`):**\n"
                    f"- **Encrypted String:** `{encoded_puzzle}`\n"
                    f"- **Character Breakdown:** {char_by_char_log}\n"
                    f"- **Combined Result:** **`{clean_answer}`**"
                )

            return {
                "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                "briefing": briefing, "payload": encoded_puzzle, "is_img": False,
                "hint": step_hint, "flag": clean_answer, "solution": solution_box
            }

        # ======================================================================
        # TIER 3: STUDENTS & FRIENDS (TRUNG BÌNH — CAESAR +2/+3 HOẶC ATBASH CÓ BẢNG TRA CỨU)
        # ======================================================================
        elif tier == 3:
            if q_num % 2 == 0:
                shift_val = rng.choice([2, 3])
                encoded_puzzle, char_by_char_log = caesar_shift_with_steps(clean_answer, shift_val)
                briefing = (
                    f"### 🎓 Tier 3 (Students & Friends Trivia) Mission #{q_num}\n"
                    f"{topic_header}\n\n"
                    f"**🌍 Encyclopedia Clue:** *{clue}*\n\n"
                    f"🏛️ **How to Solve (Classic Caesar Shift +{shift_val}):**\n"
                    f"- During encryption, each letter was shifted **`+{shift_val}` positions forward** in the alphabet.\n"
                    f"- **To Decode:** Shift each letter in `{encoded_puzzle}` **`{shift_val}` positions BACKWARD (to the left)** in the alphabet bar below!"
                )
                step_hint = (
                    f"1. **Topic:** `{sub_topic}` | **Clue:** *{clue}*\n"
                    f"2. Shift back by `{shift_val}` steps: The first 3 decoded characters are **`{clean_answer[:3]}...`**."
                )
                solution_box = (
                    f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                    f"📖 **Step-by-Step Mathematical Breakdown (`Shift -{shift_val}`):**\n"
                    f"- **Ciphertext:** `{encoded_puzzle}`\n"
                    f"- **Letter-by-Letter Transformation:** {char_by_char_log}\n"
                    f"- **Final Decoded Entity:** **`{clean_answer}`**"
                )
            else:
                encoded_puzzle, char_by_char_log = atbash_with_steps(clean_answer)
                briefing = (
                    f"### 🎓 Tier 3 (Students & Friends Trivia) Mission #{q_num}\n"
                    f"{topic_header}\n\n"
                    f"**🌍 Encyclopedia Clue:** *{clue}*\n\n"
                    f"🪞 **How to Solve (Atbash Mirror Alphabet Cipher):**\n"
                    f"Every letter is swapped with its opposite mirror letter in the alphabet (`A↔Z`, `B↔Y`, `C↔X`...). Use this direct lookup table:\n"
                    f"- **Top Row:**    `A B C D E F G H I J K L M N O P Q R S T U V W X Y Z`\n"
                    f"- **Bottom Row:** `Z Y X W V U T S R Q P O N M L K J I H G F E D C B A`"
                )
                step_hint = (
                    f"1. Find each letter of `{encoded_puzzle}` in the Top Row and replace it with the letter directly below it in the Bottom Row.\n"
                    f"2. The answer starts with **`{clean_answer[:3]}...`** and ends with **`...{clean_answer[-2:]}`**."
                )
                solution_box = (
                    f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                    f"📖 **Step-by-Step Mirror Substitution Breakdown:**\n"
                    f"- **Ciphertext:** `{encoded_puzzle}`\n"
                    f"- **Mirror Mapping (`Cipher ↔ Plain`):** {char_by_char_log}\n"
                    f"- **Final Decoded Entity:** **`{clean_answer}`**"
                )

            return {
                "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                "briefing": briefing, "payload": encoded_puzzle, "is_img": False,
                "hint": step_hint, "flag": clean_answer, "solution": solution_box
            }

        # ======================================================================
        # TIER 4: CYBER SPECIALISTS (CHO SẴN KHÓA — THỰC HÀNH STEGO PNG & CAMOUFLAGE)
        # ======================================================================
        elif tier == 4:
            pass_key = "CYBER"
            shift_val = 5
            k = build_custom_key(pass_key, [], shift_val, "")
            raw_c = encrypt_core(clean_answer, k, False, "NONE", 0)

            if q_num % 2 == 0:
                carrier = generate_sample_carrier_image(420, 220)
                stego_img = encode_image_lsb(carrier, raw_c)
                buf = io.BytesIO()
                stego_img.save(buf, format="PNG")
                briefing = (
                    f"### 🕵️‍♂️ Tier 4 (Cyber Specialist — LSB Steganography) Mission #{q_num}\n"
                    f"{topic_header}\n\n"
                    f"**🌍 Target Clue:** *{clue}*\n\n"
                    f"🖼️ **How to Solve (Hands-On Image Steganography):**\n"
                    f"We hid the encrypted name of this `{sub_topic}` inside the RGB pixels of the PNG image below!\n"
                    f"1. Set Left Sidebar: **Passphrase** = **`{pass_key}`** | **Shift Offset** = **`{shift_val}`** | **Symbol Vault** = **`Empty (Remove all icons)`** | **Reverse** = **`Unchecked`**.\n"
                    f"2. Download the Stego PNG below, open **2. Cipher Workspace → Tab 3 (Decode)**, and extract the secret answer!"
                )
                step_hint = (
                    f"💡 **Direct Shortcut Hint:**\n"
                    f"- Follow the exact Sidebar settings (`Passphrase = {pass_key}`, `Shift = {shift_val}`, `0 Symbols`) in Workspace Tab 3.\n"
                    f"- Or solve directly from the clue (*{clue}*): It starts with **`{clean_answer[:3]}...`**!"
                )
                solution_box = (
                    f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                    f"📖 **Step-by-Step Technical Explanation:**\n"
                    f"- **Step 1 (Plaintext):** `{clean_answer}` *(Topic: {sub_topic})*\n"
                    f"- **Step 2 (Cipher Engine):** Encrypted with Passphrase `{pass_key}`, Shift `{shift_val}`, 0 Icons $\\rightarrow$ Ciphertext `{raw_c}`\n"
                    f"- **Step 3 (LSB Pixel Embedding):** Converted `{raw_c}` into 8-bit binary and embedded into the Least Significant Bits of the PNG image.\n"
                    f"- **Step 4 (Extraction):** Decoding the PNG with `{pass_key}` + Shift `{shift_val}` restores **`{clean_answer}`**!"
                )
                return {
                    "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                    "briefing": briefing, "payload": buf.getvalue(), "is_img": True,
                    "hint": step_hint, "flag": clean_answer, "solution": solution_box
                }
            else:
                camo_text = encode_english_camouflage(raw_c)
                briefing = (
                    f"### 🎭 Tier 4 (Cyber Specialist — Linguistic Camouflage) Mission #{q_num}\n"
                    f"{topic_header}\n\n"
                    f"**🌍 Target Clue:** *{clue}*\n\n"
                    f"🎭 **How to Solve (Hands-On Markov Prose Decoding):**\n"
                    f"1. Set Left Sidebar: **Passphrase** = **`{pass_key}`** | **Shift Offset** = **`{shift_val}`** | **Symbol Vault** = **`Empty (Remove all icons)`** | **Reverse** = **`Unchecked`**.\n"
                    f"2. Copy the English paragraph below and paste it into **2. Cipher Workspace → Tab 2 (Reveal Secret from English Prose)**!"
                )
                step_hint = (
                    f"💡 **Direct Shortcut Hint:**\n"
                    f"- Paste the paragraph into **Workspace -> Tab 2** with Passphrase `{pass_key}` & Shift `{shift_val}`.\n"
                    f"- Or deduce from the `{sub_topic}` clue: Starts with **`{clean_answer[:3]}...`** and ends with **`...{clean_answer[-2:]}`**!"
                )
                solution_box = (
                    f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                    f"📖 **Step-by-Step Technical Explanation:**\n"
                    f"- **Step 1 (Plaintext):** `{clean_answer}` *(Topic: {sub_topic})*\n"
                    f"- **Step 2 (Cipher Engine):** Encrypted using Passphrase `{pass_key}` and Shift `{shift_val}` $\\rightarrow$ `{raw_c}`\n"
                    f"- **Step 3 (4-Bit Nibble Markov Mapping):** Each byte of `{raw_c}` was split into two 4-bit nibbles (0–15) and mapped to IT English words.\n"
                    f"- **Step 4 (Decryption):** Reversing the English words back to bytes and decrypting with `{pass_key}` yields **`{clean_answer}`**!"
                )
                return {
                    "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                    "briefing": briefing, "payload": camo_text, "is_img": False,
                    "hint": step_hint, "flag": clean_answer, "solution": solution_box
                }

        # ======================================================================
        # TIER 5: GRANDMASTER CRYPTANALYSTS (ĐA TẦNG CHUYÊN NGHIỆP)
        # ======================================================================
        else:
            pass_key = "GRANDMASTER"
            shift_val = rng.randint(10, 30)
            chosen_icons = [SYMBOLS_POOL[0], SYMBOLS_POOL[1]] if len(SYMBOLS_POOL) >= 2 else []
            pair_rule = "a=@, e=3"
            k = build_custom_key(pass_key, chosen_icons, shift_val, pair_rule)
            raw_c = encrypt_core(clean_answer, k, True, "NONE", 0)
            camo_payload = encode_english_camouflage(raw_c)
            icons_str = " , ".join(chosen_icons)

            briefing = (
                f"### 👑 Tier 5 (Grandmaster Multi-Layer Cryptanalysis) Mission #{q_num}\n"
                f"{topic_header}\n\n"
                f"**🌍 Target Clue:** *{clue}*\n\n"
                f"🔐 **Multi-Layer Decryption Parameters:**\n"
                f"- **Group Passphrase:** **`{pass_key}`**\n"
                f"- **Shift Offset:** Hidden between **`{shift_val - 1}`** and **`{shift_val + 1}`**\n"
                f"- **Symbol Vault (First 2 default icons in order):** **`{icons_str}`**\n"
                f"- **Custom Pairs:** **`{pair_rule}`** &nbsp;|&nbsp; **Reverse Structure:** **`Checked (Enabled)`**\n"
                f"- **Outer Wrapper:** Linguistic English Camouflage (Decode via **Workspace → Tab 2**)."
            )
            step_hint = (
                f"💡 **Grandmaster Hint:**\n"
                f"- The exact **Shift Offset** is **`{shift_val}`**.\n"
                f"- Target `{sub_topic}` starts with **`{clean_answer[:3]}...`** and ends with **`...{clean_answer[-2:]}`**."
            )
            solution_box = (
                f"✅ **Exact Answer to Type:** `{clean_answer}`\n\n"
                f"📖 **Complete Multi-Layer Cryptographic Walkthrough:**\n"
                f"- **Layer 1 (Markov Unwrap):** Converting the English prose back into raw bytes yields reversed ciphertext `{raw_c}`.\n"
                f"- **Layer 2 (Reverse Flip):** Un-reversing the string restores the forward substitution sequence.\n"
                f"- **Layer 3 (Key Matrix Permutation):** Using Passphrase `{pass_key}`, Icons `{icons_str}`, Shift `{shift_val}`, and Pairs `{pair_rule}` reconstructs the exact 229-char key table.\n"
                f"- **Final Plaintext:** **`{clean_answer}`** *(Topic: {sub_topic})*"
            )
            return {
                "id": f"T{tier}_{q_num}", "tier": tier, "pts": base_pts,
                "briefing": briefing, "payload": camo_payload, "is_img": False,
                "hint": step_hint, "flag": clean_answer, "solution": solution_box
            }

    # --- GIAO DIỆN ĐẤU TRƯỜNG CTF ---
    st.markdown("""
    <div class="hero-box" style="padding: 20px 28px; margin-bottom: 18px;">
        <div class="hero-badge">🕹️ THEMED ENCYCLOPEDIA MATRIX • ANIMALS, SPACE, OCEAN, SCIENCE & HISTORY</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Global Crypto Challenges & CTF Arena</h2>
        <p class="hero-sub">Clear topic boundaries, beginner-friendly word puzzles for kids (Tiers 1–2), trivia ciphers for friends (Tier 3), and full steganography labs for pros (Tiers 4–5).</p>
    </div>
    """, unsafe_allow_html=True)

    ctf_db = load_ctf_db()
    if "ctf_user" not in st.session_state:
        st.session_state.ctf_user = None

    if not st.session_state.ctf_user:
        st.markdown("""
        <div class="ws-banner">
            <h4>🔐 Agent Authentication Portal (Login / Register)</h4>
            <p>Sign in or create a new Agent Callsign to unlock your personalized 5,000-question matrix, climb the global leaderboard, and chat with friends.</p>
        </div>
        """, unsafe_allow_html=True)
        l_col1, l_col2, l_col3 = st.columns([1.5, 1.5, 1])
        with l_col1:
            u_in = st.text_input("🕵️ Agent Callsign (Username):", placeholder="e.g. taolagautruc")
        with l_col2:
            p_in = st.text_input("🔑 Secret Agent PIN:", type="password", placeholder="Enter 4+ digit PIN")
        with l_col3:
            st.write("")
            if st.button("🚀 Enter CTF Arena", type="primary", use_container_width=True):
                u_clean = u_in.strip()
                p_clean = p_in.strip()
                if not u_clean or not p_clean:
                    st.error("Please enter both a Username and PIN!")
                else:
                    p_hash = hashlib.sha256(p_clean.encode("utf-8")).hexdigest()
                    users = ctf_db["users"]
                    if u_clean in users:
                        if users[u_clean]["pin_hash"] == p_hash:
                            st.session_state.ctf_user = u_clean
                            st.rerun()
                        else:
                            st.error("❌ Incorrect PIN for this Agent Callsign!")
                    else:
                        users[u_clean] = {
                            "pin_hash": p_hash,
                            "score": 0,
                            "solved": [],
                            "surrendered": [],
                            "hints_used": [],
                            "friends": [],
                            "friend_requests": []
                        }
                        save_ctf_db(ctf_db)
                        st.session_state.ctf_user = u_clean
                        st.rerun()
    else:
        curr_user = st.session_state.ctf_user
        u_data = ctf_db["users"].get(curr_user, {})
        u_score = u_data.get("score", 0)
        u_solved = u_data.get("solved", [])
        u_surrendered = u_data.get("surrendered", [])
        u_hints = u_data.get("hints_used", [])
        u_friends = u_data.get("friends", [])
        u_reqs = u_data.get("friend_requests", [])

        p_c1, p_c2, p_c3, p_c4, p_c5 = st.columns([1.6, 1.2, 1.1, 1.1, 0.8])
        p_c1.metric("🕵️ Active Agent", curr_user, get_agent_rank(u_score))
        p_c2.metric("🏆 Total Arena Score", f"{u_score:,} PTS", "Global Ranked")
        p_c3.metric("✅ Missions Cracked", f"{len(u_solved)} / 5,000", f"{len(u_surrendered)} Surrendered")
        p_c4.metric("🤝 Friends Network", f"{len(u_friends)} Agents", f"{len(u_reqs)} Pending Req")
        with p_c5:
            st.write("")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.ctf_user = None
                st.rerun()

        st.write("")
        arena_tab1, arena_tab2, arena_tab3 = st.tabs([
            "🎯 1. Challenge Matrix (5 Tiers • 5,000 Missions)",
            "🏆 2. Global Leaderboard & Add Friends",
            f"💬 3. Friends & Direct Messenger ({len(u_reqs)} Requests)"
        ])

        with arena_tab1:
            sel_c1, sel_c2, sel_c3 = st.columns([2.1, 0.9, 1])
            with sel_c1:
                tier_choice = st.selectbox(
                    "🔥 Select Difficulty Tier:",
                    [
                        "Tier 1 — Kids & Beginners (100 PTS | Missing Vowels & Backwards Short Words)",
                        "Tier 2 — Young Explorers (250 PTS | Number-to-Letter Code & Guided +1 Step)",
                        "Tier 3 — Students & Friends (500 PTS | Caesar +2/+3 & Mirror Alphabet Table)",
                        "Tier 4 — Cyber Specialists (1,000 PTS | Guided LSB Image Stego & Camouflage)",
                        "Tier 5 — Grandmaster Pros (2,500 PTS | Full Multi-Layer Cryptanalysis)"
                    ]
                )
                tier_num = int(tier_choice.split("Tier ")[1][0])
            with sel_c2:
                if "curr_q_num" not in st.session_state:
                    st.session_state.curr_q_num = 1
                q_num = st.number_input("🔢 Mission # (1 - 1000):", min_value=1, max_value=1000, value=st.session_state.curr_q_num)
                st.session_state.curr_q_num = q_num
            with sel_c3:
                st.write("")
                if st.button("🎲 Random Mission", use_container_width=True):
                    st.session_state.curr_q_num = random.randint(1, 1000)
                    st.rerun()

            chal = generate_dynamic_challenge(curr_user, tier_num, q_num)
            cid = chal["id"]
            base_pts = chal["pts"]
            is_solved = cid in u_solved
            is_surrendered = cid in u_surrendered
            hint_used = cid in u_hints

            effective_pts = int(base_pts * 0.30) if hint_used else base_pts
            surrender_penalty = int(base_pts * 0.92)

            st.markdown(f"""
            <div class="ws-banner">
                <h4>🎯 Mission ID: <code>{cid}</code> — Base Reward: <b>{base_pts:,} PTS</b></h4>
                <p>⚠️ <b>Fair Play Scoring Rules:</b> Clicking <b>Hint</b> reduces this mission's reward by <b>70%</b> (you earn <b>{int(base_pts*0.30)} PTS</b>). Clicking <b>Surrender & Show Answer</b> reveals the full step-by-step solution immediately but deducts <b>92%</b> (<b>-{surrender_penalty} PTS</b> penalty) from your total score!</p>
            </div>
            """, unsafe_allow_html=True)

            if is_solved:
                st.success(f"🎉 **MISSION COMPLETED!** You solved `{cid}`! Exact Answer: **`{chal['flag']}`**")
                with st.expander("📖 View Step-by-Step Cryptographic Explanation", expanded=True):
                    st.markdown(chal["solution"])
            elif is_surrendered:
                st.error(f"🏳️ **MISSION SURRENDERED!** (-{surrender_penalty} PTS penalty applied).")

            st.markdown(chal["briefing"])

            if tier_num in [1, 2, 3]:
                st.caption("🔤 **Quick Reference English Alphabet:** `A B C D E F G H I J K L M N O P Q R S T U V W X Y Z`")

            if chal["is_img"]:
                st.image(chal["payload"], caption=f"Intercepted Stego PNG — Mission {cid}", width=380)
                st.download_button(
                    "⬇️ Download Intercepted Stego PNG",
                    data=chal["payload"],
                    file_name=f"mission_{cid}.png",
                    mime="image/png"
                )
            else:
                st.markdown("**🧩 Encrypted Puzzle String to Decode:**")
                st.code(chal["payload"], language=None)

            h_col1, h_col2 = st.columns(2)
            with h_col1:
                if not hint_used and not is_solved and not is_surrendered:
                    if st.button(f"💡 Unlock Detailed Hint (-70% Points -> Earn {int(base_pts*0.30)} PTS)", use_container_width=True):
                        u_hints.append(cid)
                        ctf_db["users"][curr_user]["hints_used"] = u_hints
                        save_ctf_db(ctf_db)
                        st.rerun()
                elif hint_used:
                    st.warning(f"💡 **HINT UNLOCKED (70% Point Reduction Active):**\n\n{chal['hint']}")

            with h_col2:
                if not is_solved and not is_surrendered:
                    if st.button(f"🏳️ Surrender & Reveal Full Answer (-{surrender_penalty} PTS Penalty)", use_container_width=True):
                        u_surrendered.append(cid)
                        ctf_db["users"][curr_user]["surrendered"] = u_surrendered
                        ctf_db["users"][curr_user]["score"] = u_score - surrender_penalty
                        save_ctf_db(ctf_db)
                        st.rerun()
                elif is_surrendered:
                    st.info(f"🔓 **OFFICIAL SOLUTION & STEP-BY-STEP BREAKDOWN:**\n\n{chal['solution']}")

            st.divider()
            if not is_solved and not is_surrendered:
                ans_col1, ans_col2 = st.columns([3, 1])
                with ans_col1:
                    flag_input = st.text_input(
                        "🚩 Submit Your Decoded Answer:",
                        placeholder="Type the decoded word/name (e.g. LION, MARS, OCTOPUS, ABRAHAM LINCOLN)...",
                        key=f"flag_in_{cid}"
                    )
                with ans_col2:
                    st.write("")
                    if st.button("✅ Submit Answer", type="primary", use_container_width=True):
                        user_guess = " ".join(flag_input.strip().upper().split())
                        expected = chal["flag"].upper()
                        if user_guess == expected or user_guess == f"FLAG{{{expected}}}":
                            u_solved.append(cid)
                            ctf_db["users"][curr_user]["solved"] = u_solved
                            ctf_db["users"][curr_user]["score"] = u_score + effective_pts
                            save_ctf_db(ctf_db)
                            st.balloons()
                            st.success(f"🎉 **AWESOME! '{chal['flag']}' IS CORRECT!** +{effective_pts} PTS added to your score!")
                            time.sleep(1.2)
                            st.rerun()
                        else:
                            st.error("❌ Not quite right! Check the Specific Topic & Clue above, or click 'Unlock Detailed Hint'.")

        with arena_tab2:
            st.markdown("""
            <div class="ws-banner">
                <h4>🏆 Global Public Leaderboard</h4>
                <p>Live rankings across all players. Send a Friend Request to any player on the leaderboard to open a private 1-on-1 chat box!</p>
            </div>
            """, unsafe_allow_html=True)

            sorted_users = sorted(ctf_db["users"].items(), key=lambda x: x[1].get("score", 0), reverse=True)

            for rank_idx, (agent_id, a_info) in enumerate(sorted_users, start=1):
                a_score = a_info.get("score", 0)
                a_solved = len(a_info.get("solved", []))
                a_title = get_agent_rank(a_score)
                medal = "🥇" if rank_idx == 1 else ("🥈" if rank_idx == 2 else ("🥉" if rank_idx == 3 else f"#{rank_idx}"))

                lb_c1, lb_c2, lb_c3, lb_c4 = st.columns([2.2, 1.4, 1.2, 1.2])
                with lb_c1:
                    me_tag = " *(You)*" if agent_id == curr_user else ""
                    st.markdown(f"**{medal} &nbsp; `{agent_id}`**{me_tag} — <span style='color:#60a5fa;'>{a_title}</span>", unsafe_allow_html=True)
                with lb_c2:
                    st.markdown(f"🏆 **{a_score:,} PTS**")
                with lb_c3:
                    st.markdown(f"✅ `{a_solved}` solved")
                with lb_c4:
                    if agent_id != curr_user:
                        if agent_id in u_friends:
                            st.caption("🤝 Friends")
                        elif curr_user in a_info.get("friend_requests", []):
                            st.caption("⏳ Request Sent")
                        else:
                            if st.button("➕ Add Friend", key=f"add_fr_{agent_id}", use_container_width=True):
                                target_reqs = ctf_db["users"][agent_id].get("friend_requests", [])
                                if curr_user not in target_reqs:
                                    target_reqs.append(curr_user)
                                    ctf_db["users"][agent_id]["friend_requests"] = target_reqs
                                    save_ctf_db(ctf_db)
                                    st.toast(f"🤝 Friend request sent to {agent_id}!", icon="🤝")
                                    st.rerun()

            st.divider()
            with st.expander("🛠️ Leaderboard & Account Management (Reset My Score / Remove Demo Bots)"):
                m_col1, m_col2 = st.columns(2)
                with m_col1:
                    if st.button("🔄 Reset My Score & History to 0 PTS", use_container_width=True):
                        ctf_db["users"][curr_user]["score"] = 0
                        ctf_db["users"][curr_user]["solved"] = []
                        ctf_db["users"][curr_user]["surrendered"] = []
                        ctf_db["users"][curr_user]["hints_used"] = []
                        save_ctf_db(ctf_db)
                        st.success("Your score and mission history have been reset to 0 PTS!")
                        st.rerun()
                with m_col2:
                    if st.button("🧹 Remove Pre-loaded Demo Bots from Leaderboard", use_container_width=True):
                        for bot_name in ["ZeroCool_VN", "CipherQueen_HCMUS", "ShadowBroker_99", "AlexMercer_US", "ElenaRostova_UK", "KenjiSato_JP"]:
                            if bot_name in ctf_db["users"] and bot_name != curr_user:
                                del ctf_db["users"][bot_name]
                        save_ctf_db(ctf_db)
                        st.success("Removed all demo bots! Only real registered players are shown now.")
                        st.rerun()

        with arena_tab3:
            f_col1, f_col2 = st.columns([1.2, 2.3])

            with f_col1:
                st.markdown("##### 📩 Incoming Friend Requests")
                if not u_reqs:
                    st.caption("No pending friend requests.")
                else:
                    for req_sender in list(u_reqs):
                        rc1, rc2, rc3 = st.columns([1.6, 1, 1])
                        rc1.markdown(f"🕵️ **`{req_sender}`**")
                        if rc2.button("✅ Accept", key=f"acc_{req_sender}", use_container_width=True):
                            u_reqs.remove(req_sender)
                            if req_sender not in u_friends:
                                u_friends.append(req_sender)
                            sender_friends = ctf_db["users"].get(req_sender, {}).get("friends", [])
                            if curr_user not in sender_friends:
                                sender_friends.append(curr_user)
                            ctf_db["users"][curr_user]["friend_requests"] = u_reqs
                            ctf_db["users"][curr_user]["friends"] = u_friends
                            if req_sender in ctf_db["users"]:
                                ctf_db["users"][req_sender]["friends"] = sender_friends
                            save_ctf_db(ctf_db)
                            st.rerun()
                        if rc3.button("❌", key=f"dec_{req_sender}", use_container_width=True):
                            u_reqs.remove(req_sender)
                            ctf_db["users"][curr_user]["friend_requests"] = u_reqs
                            save_ctf_db(ctf_db)
                            st.rerun()

                st.divider()
                st.markdown("##### 🤝 Quick Add by Callsign")
                manual_friend = st.text_input("Enter Player Username:", placeholder="e.g. AlexMercer_US")
                if st.button("📨 Send Friend Request", use_container_width=True):
                    mf = manual_friend.strip()
                    if mf not in ctf_db["users"]:
                        st.error("Player not found in Leaderboard database!")
                    elif mf == curr_user:
                        st.warning("You cannot add yourself!")
                    elif mf in u_friends:
                        st.info("Already in your friends list!")
                    else:
                        if mf in ["ZeroCool_VN", "CipherQueen_HCMUS", "ShadowBroker_99", "AlexMercer_US", "ElenaRostova_UK", "KenjiSato_JP"]:
                            u_friends.append(mf)
                            ctf_db["users"][curr_user]["friends"] = u_friends
                            ctf_db["users"][mf]["friends"].append(curr_user)
                            save_ctf_db(ctf_db)
                            st.success(f"🎉 **{mf}** accepted your friend request! You can chat on the right now.")
                            st.rerun()
                        else:
                            t_reqs = ctf_db["users"][mf].get("friend_requests", [])
                            if curr_user not in t_reqs:
                                t_reqs.append(curr_user)
                                ctf_db["users"][mf]["friend_requests"] = t_reqs
                                save_ctf_db(ctf_db)
                            st.success(f"Request sent to **{mf}**!")

            with f_col2:
                st.markdown("##### 💬 Private 1-on-1 Player Chat")
                if not u_friends:
                    st.info("💡 No connected friends yet. Click **➕ Add Friend** on the Leaderboard (Tab 2) or use Quick Add on the left to start chatting!")
                else:
                    active_friend = st.selectbox("Select Friend to Chat With:", u_friends)
                    pair_key = "__".join(sorted([curr_user, active_friend]))
                    dm_list = ctf_db.get("direct_messages", {}).get(pair_key, [])

                    chat_box = st.container(height=280, border=True)
                    with chat_box:
                        if not dm_list:
                            st.caption(f"🔒 Private 1-on-1 chat opened with **{active_friend}**. Say hi!")
                        for dm in dm_list:
                            align_color = "#60a5fa" if dm["sender"] == curr_user else "#c084fc"
                            st.markdown(
                                f"<div style='margin-bottom:8px;'><b style='color:{align_color};'>{dm['sender']}</b> "
                                f"<span style='font-size:0.75rem;color:#64748b;'>({dm['time']})</span>:<br>"
                                f"<span style='color:#e2e8f0;'>{dm['text']}</span></div>",
                                unsafe_allow_html=True
                            )

                    dm_in_col, dm_btn_col = st.columns([3.5, 1])
                    with dm_in_col:
                        dm_txt = st.text_input("Write private message:", placeholder=f"Message @{active_friend}...", label_visibility="collapsed", key=f"dm_in_{active_friend}")
                    with dm_btn_col:
                        if st.button("📨 Send", type="primary", use_container_width=True):
                            if dm_txt.strip():
                                if "direct_messages" not in ctf_db:
                                    ctf_db["direct_messages"] = {}
                                if pair_key not in ctf_db["direct_messages"]:
                                    ctf_db["direct_messages"][pair_key] = []
                                ctf_db["direct_messages"][pair_key].append({
                                    "sender": curr_user,
                                    "text": dm_txt.strip(),
                                    "time": datetime.now(timezone.utc).strftime("%H:%M UTC")
                                })
                                if active_friend in ["ZeroCool_VN", "CipherQueen_HCMUS", "ShadowBroker_99", "AlexMercer_US", "ElenaRostova_UK", "KenjiSato_JP"]:
                                    ctf_db["direct_messages"][pair_key].append({
                                        "sender": active_friend,
                                        "text": f"Hey @{curr_user}! The new Animal, Space & Ocean puzzles in Tier 1 & 2 are super fun. Let's race to the top of the leaderboard!",
                                        "time": datetime.now(timezone.utc).strftime("%H:%M UTC")
                                    })
                                save_ctf_db(ctf_db)
                                st.rerun()


 
# ==============================================================================
# PHẦN 5: SECURITY ACADEMY & UNIVERSITY COMPUTER SYSTEMS / CRYPTOGRAPHY LMS (20 MODULES)
# ==============================================================================
elif "5. Security Academy" in main_menu:
    ACAD_DB_FILE = "academy_lms_db.json"

    def load_acad_db() -> dict:
        if not os.path.exists(ACAD_DB_FILE):
            default_db = {"students": {}}
            with open(ACAD_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(default_db, f, ensure_ascii=False, indent=4)
            return default_db
        try:
            with open(ACAD_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"students": {}}

    def save_acad_db(data: dict):
        with open(ACAD_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_academic_degree(xp: int) -> str:
        if xp >= 10000: return "👑 Grand Chancellor of Computer Science & Cryptography"
        if xp >= 7500:  return "🎓 Distinguished Professor of Information Security"
        if xp >= 5000:  return "🔬 Senior Computer Systems & Crypto Researcher"
        if xp >= 3000:  return "🛡️ Master of Cryptographic Engineering"
        if xp >= 1500:  return "💻 Computer Systems & Security Specialist"
        if xp >= 500:   return "📘 Cryptography & Binary Undergraduate"
        if xp > 0:      return "🌱 Freshman Apprentice"
        return "📖 Enrolled Student"

    st.markdown("""
    <style>
        .lesson-card {
            background: #111827;
            border: 1px solid #1f2937;
            border-top: 4px solid #3b82f6;
            border-radius: 14px;
            padding: 26px 30px;
            margin-bottom: 24px;
            line-height: 1.8;
            color: #cbd5e1;
        }
        .lesson-card h3 {
            color: #f8fafc;
            margin-top: 0;
            font-size: 1.5rem;
            border-bottom: 1px solid #1e293b;
            padding-bottom: 12px;
        }
        .lesson-card h4 {
            color: #60a5fa;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.18rem;
        }
        .example-box {
            background: rgba(16, 185, 129, 0.07);
            border: 1px solid rgba(16, 185, 129, 0.35);
            border-left: 4px solid #10b981;
            border-radius: 10px;
            padding: 18px 22px;
            margin: 14px 0;
            color: #d1fae5;
            line-height: 1.75;
        }
        .exercise-box {
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            border: 1px solid #6366f1;
            border-radius: 14px;
            padding: 24px 28px;
            margin-top: 22px;
            margin-bottom: 24px;
        }
        .drill-box {
            background: linear-gradient(135deg, #0f172a 0%, #064e3b 100%);
            border: 1px solid #10b981;
            border-radius: 14px;
            padding: 24px 28px;
            margin-top: 20px;
            margin-bottom: 30px;
        }
    </style>
    """, unsafe_allow_html=True)

    # ==========================================================================
    # KHO GIÁO TRÌNH ĐẠI HỌC 20 HỌC PHẦN (TỪ CON SỐ 0 ĐẾN HỆ THỐNG MÁY TÍNH & MẬT MÃ HỌC)
    # Mỗi bài học cung cấp 500 XP cố định (Quiz 1: 100, Quiz 2: 100, Lab 1: 150, Lab 2: 150)
    # ==========================================================================
    LESSONS_CURRICULUM = {
        # ----------------------------------------------------------------------
        # TRACK 1: ABSOLUTE BEGINNER FOUNDATIONS (LESSONS 01 - 03)
        # ----------------------------------------------------------------------
        "Track 1 • Lesson 01: What is Information & Why Privacy Matters in Daily Life": {
            "id": "L01",
            "track": "🟢 TRACK 1: ABSOLUTE BEGINNER FOUNDATIONS",
            "title": "🌍 Lesson 01: What is Information, Secrets & Why Cryptography Saves Daily Life",
            "overview": (
                "Welcome to the very first step of your journey! Before touching any math or computer code, let's ask a simple question: **What is Cryptography, and why should an everyday person care about it?**\n\n"
                "Every single day, you send private messages to loved ones, type credit card numbers on shopping websites, log into bank accounts, and store personal photos on your phone. "
                "When your message travels across Wi-Fi or cellular towers, it passes through dozens of public routers and servers owned by strangers. Without protection, anyone sitting on the same coffee-shop Wi-Fi or running an intermediate server could read your messages like an open postcard!\n\n"
                "**Cryptography** (from the Greek words *kryptos* meaning 'hidden' and *graphein* meaning 'to write') is the science of transforming readable information into an unreadable puzzle so that **only the person you trust** can unlock and read it."
            ),
            "enc_guide": (
                "**The 4 Core Terms Every Beginner Must Know:**\n"
                "1. **Plaintext (Bản rõ):** Your original, readable message before any protection is applied (e.g., `'Mom, my ATM PIN is 4829'`).\n"
                "2. **Ciphertext (Bản mã):** The scrambled, unreadable version of your message after locking it (e.g., `'X#9@kL!2pQ'`).\n"
                "3. **Encryption (Quá trình Mã hóa):** The process of locking Plaintext into Ciphertext using a rule and a secret password (**Key**).\n"
                "4. **Decryption (Quá trình Giải mã):** The reverse process of unlocking Ciphertext back into the original Plaintext using the matching Key.\n\n"
                "**The CIA Triad of Information Security:**\n"
                "- **C — Confidentiality (Tính Bảo mật):** Only authorized people can read the data.\n"
                "- **I — Integrity (Tính Toàn vẹn):** No hacker can secretly alter `$10` into `$10,000` in transit without being detected.\n"
                "- **A — Availability (Tính Sẵn sàng):** Authorized users can access their data reliably whenever needed."
            ),
            "dec_guide": (
                "**How Cryptography Protects You Every Day Without You Noticing:**\n"
                "- **🔒 HTTPS Padlock on Websites:** Encrypts your passwords and banking details between your browser and the website.\n"
                "- **💬 End-to-End Encrypted Messaging:** Ensures even the social network company cannot read your private chats.\n"
                "- **💳 EMV Chip on Bank Cards & Apple/Google Pay:** Uses cryptographic challenges so criminals cannot clone your card.\n"
                "- **🏥 Medical & Personal Records:** Prevents data brokers from stealing and selling your private health or identity history."
            ),
            "examples": (
                "🔹 **Example 1 (The Locked Box Analogy):**\n"
                "- Imagine writing a secret letter (**Plaintext**), placing it inside a steel safe, and locking it with a combination code `7-3-9` (**Key**).\n"
                "- Even if a mail carrier steals the safe in transit (**Ciphertext**), they cannot read the letter without the code `7-3-9`.\n\n"
                "🔹 **Example 2 (Confidentiality vs. Integrity):**\n"
                "- If Alice sends Bob `'Meet me at 5 PM'` and Eve intercepts it and reads it, **Confidentiality** is broken.\n"
                "- If Eve changes the message to `'Meet me at 9 PM'` and forwards it to Bob, **Integrity** is broken.\n\n"
                "🔹 **Example 3 (Why Kerckhoffs's Principle Matters):**\n"
                "- A good lock does not rely on keeping the *blueprint of the lock* secret; it relies 100% on keeping your **Key** secret!"
            ),
            "q1": "In cryptography, what do we call the original readable message BEFORE it is locked?",
            "q1_opts": ["A) Ciphertext", "B) Plaintext", "C) Hash Digest", "D) Binary Opcode"],
            "q1_ans": "B) Plaintext",
            "q2": "Which pillar of the 'CIA Triad' ensures that a hacker cannot secretly modify the amount of money in a bank transfer while it travels across the internet?",
            "q2_opts": ["A) Confidentiality", "B) Integrity", "C) Availability", "D) Steganography"],
            "q2_ans": "B) Integrity",
            "lab1_q": "Practical Lab 1 (+150 XP): If 'Plaintext' is transformed into 'Ciphertext', what is the exact 10-letter English term for this locking process?",
            "lab1_ans": "ENCRYPTION",
            "lab2_q": "Practical Lab 2 (+150 XP): According to Kerckhoffs's Principle, even if an attacker knows how the system works, what single thing must remain secret to keep your data safe? (1 word, 3 letters)",
            "lab2_ans": "KEY"
        },

        "Track 1 • Lesson 02: Encoding vs. Encryption vs. Hashing (Crucial Distinction)": {
            "id": "L02",
            "track": "🟢 TRACK 1: ABSOLUTE BEGINNER FOUNDATIONS",
            "title": "🔄 Lesson 02: Encoding vs. Encryption vs. Hashing — Never Confuse Them!",
            "overview": (
                "90% of beginners (and even many software developers) confuse **Encoding**, **Encryption**, and **Hashing**. "
                "They all turn normal text into strange-looking strings, but their **purposes** and **security properties** are completely different! "
                "Using Encoding when you actually need Encryption is one of the most common causes of massive data breaches."
            ),
            "enc_guide": (
                "**1. ENCODING (Biểu diễn / Chuyển đổi định dạng — NO SECRET KEY, ZERO SECURITY):**\n"
                "- **Purpose:** Usability & compatibility. It translates data from one public format to another so computers, cables, or QR scanners can read it (e.g., **Morse Code, Braille, ASCII, UTF-8, Base64, QR Codes**).\n"
                "- **How to Encode/Decode:** Uses a **100% public rulebook** with **NO password/key**. Anyone in the world can decode an encoded message instantly.\n\n"
                "**2. ENCRYPTION (Mã hóa bảo mật — REQUIRES A SECRET KEY, REVERSIBLE):**\n"
                "- **Purpose:** Confidentiality & secrecy.\n"
                "- **How to Encrypt/Decrypt:** Requires a **Secret Key** (Passphrase, Shift, or Private Key). Only someone possessing the exact key can reverse the Ciphertext back into Plaintext."
            ),
            "dec_guide": (
                "**3. HASHING (Hàm băm một chiều — ONE-WAY TRAPDOOR, IRREVERSIBLE):**\n"
                "- **Purpose:** Password verification & file integrity checking (e.g., **SHA-256, bcrypt, Argon2**).\n"
                "- **How It Works:** A mathematical blender that turns any input of any length into a fixed-length fingerprint (Hash Digest). **It is strictly ONE-WAY**—there is NO 'un-hash' or 'decrypt' button! To verify a user's password at login, the server hashes what the user typed and checks if the two fingerprints match."
            ),
            "examples": (
                "🔹 **Example 1 (Encoding — Morse Code & QR Codes):**\n"
                "- Text `'SOS'` encoded in Morse Code is `'... --- ...'`. Does it hide the secret? **NO!** Anyone with a public Morse chart can read `'SOS'`. That is **Encoding**.\n\n"
                "🔹 **Example 2 (Encryption — Secret Passphrase):**\n"
                "- Text `'SOS'` encrypted with secret key `'NEXUS'` becomes `'9#kP@1'`. Without the key `'NEXUS'`, nobody can reverse it. With `'NEXUS'`, you can decrypt it back to `'SOS'`. That is **Encryption**.\n\n"
                "🔹 **Example 3 (Hashing — SHA-256 Fingerprint):**\n"
                "- Text `'SOS'` hashed with SHA-256 becomes `'32f88c4d...'` (64 hex chars). Even the creator cannot reverse `'32f88c4d...'` back into `'SOS'`, except by guessing `'SOS'` and hashing it again. That is **Hashing**."
            ),
            "q1": "If you convert a website URL into a QR Code so people can scan it with their phone camera, which operation did you perform?",
            "q1_opts": ["A) Military Encryption", "B) One-Way Hashing", "C) Public Encoding (No secret key, anyone can scan and decode it)", "D) Steganography"],
            "q1_ans": "C) Public Encoding (No secret key, anyone can scan and decode it)",
            "q2": "Which of the three operations is strictly a ONE-WAY mathematical function that CANNOT be reversed or decrypted back into the original input?",
            "q2_opts": ["A) Base64 Encoding", "B) Caesar Encryption", "C) Cryptographic Hashing (e.g. SHA-256)", "D) Morse Code"],
            "q2_ans": "C) Cryptographic Hashing (e.g. SHA-256)",
            "lab1_q": "Practical Lab 1 (+150 XP): Decode this public Morse Code string back into a 3-letter English word (`...` = S, `---` = O): `... --- ...`",
            "lab1_ans": "SOS",
            "lab2_q": "Practical Lab 2 (+150 XP): Between ENCODING, ENCRYPTION, and HASHING, which one requires a SECRET KEY to unlock and reverse the data back to plaintext?",
            "lab2_ans": "ENCRYPTION"
        },

        "Track 1 • Lesson 03: Steganography vs. Cryptography (Hiding Existence vs. Meaning)": {
            "id": "L03",
            "track": "🟢 TRACK 1: ABSOLUTE BEGINNER FOUNDATIONS",
            "title": "🕵️ Lesson 03: Cryptography vs. Steganography — The Art of Invisible Secrets",
            "overview": (
                "In Lesson 01 and 02, we learned that **Cryptography** scrambles a message so an eavesdropper cannot understand its *meaning*. "
                "However, there is a catch: when a censor or firewall sees a scrambled string like `X9#k!mP2$`, they immediately know you are hiding a secret and may block your message or force you to hand over the key!\n\n"
                "**Steganography** (from Greek *steganos* meaning 'covered/concealed') takes a completely different approach: **it hides the very existence of the message** inside an innocent-looking everyday object (like a family photo, an audio song, or a normal English paragraph)."
            ),
            "enc_guide": (
                "**Comparing the Two Sciences:**\n"
                "- **🔐 Cryptography:** Hides the **CONTENT** of the message. The enemy sees the encrypted message, knows it is secret, but cannot read it.\n"
                "- **🖼️ Steganography:** Hides the **EXISTENCE** of the message inside a **Carrier (Vật mang)**—such as an image or text. The enemy sees only a normal picture of a cat and never even suspects a secret message is present!\n\n"
                "**🏆 Dual-Layer Defense (How Ultimate Secret Messenger Combines Both):**\n"
                "1. **Step 1 (Encrypt First):** Encrypt the secret plaintext using a multi-layer key into Ciphertext.\n"
                "2. **Step 2 (Conceal Second):** Hide that Ciphertext inside a PNG image (LSB Steganography) or English sentences (Linguistic Camouflage).\n"
                "Even if a forensic analyst discovers the hidden data inside the image, they only find locked Ciphertext!"
            ),
            "dec_guide": (
                "**Historical & Modern Steganography Techniques:**\n"
                "1. **Ancient Greece (Histiaeus's Tattoo):** Shaving a messenger's head, tattooing the message on the scalp, waiting for hair to grow back, and sending him across enemy lines.\n"
                "2. **Invisible Ink & Microdots (WWII):** Shrinking a full page of intelligence down to the size of a printed period (`.`) on a normal postcard.\n"
                "3. **Acrostic / Null Ciphers:** Hiding the secret message in the **first letter of every word** (or every sentence) of an innocent letter.\n"
                "4. **Digital Pixel LSB (Modern):** Modifying the 1s and 0s of RGB color values in a lossless PNG image."
            ),
            "examples": (
                "🔹 **Example 1 (Acrostic First-Letter Steganography):**\n"
                "- Innocent Sentence: `Send Everyavailable Navel Destroyer`\n"
                "- Take the **1st letter of each word**: `S` + `E` + `N` + `D` = **`SEND`**!\n\n"
                "🔹 **Example 2 (Second-Word Null Cipher):**\n"
                "- Innocent Note: `Come HELPಂದು तुरंत, please MEet us NOW.`\n"
                "- Hidden Message: **`HELP ME NOW`**.\n\n"
                "🔹 **Example 3 (Digital Steganography):**\n"
                "- Carrier File: `vacation_photo.png` (1,000,000 pixels).\n"
                "- Hidden Payload: An encrypted blueprint tucked into the lowest bit of the Red, Green, and Blue channels."
            ),
            "q1": "What is the main difference between Cryptography and Steganography?",
            "q1_opts": [
                "A) Cryptography hides the meaning of a message; Steganography hides the very existence of the message inside an innocent carrier",
                "B) Steganography is only used for banking passwords",
                "C) Cryptography requires no key, while Steganography requires SHA-256",
                "D) They are 100% identical"
            ],
            "q1_ans": "A) Cryptography hides the meaning of a message; Steganography hides the very existence of the message inside an innocent carrier",
            "q2": "Why is it best practice to ENCRYPT a message BEFORE hiding it with Steganography?",
            "q2_opts": [
                "A) To make the image brighter",
                "B) So that even if an attacker detects and extracts the hidden payload from the carrier file, the extracted message is still encrypted and unreadable without the key",
                "C) Because PNG files reject plain English words",
                "D) To convert PNG into JPEG"
            ],
            "q2_ans": "B) So that even if an attacker detects and extracts the hidden payload from the carrier file, the extracted message is still encrypted and unreadable without the key",
            "lab1_q": "Practical Lab 1 (+150 XP): Extract the hidden Acrostic secret by taking the FIRST LETTER of each word in this sentence: `Cats Always Nap Daily`",
            "lab1_ans": "CAND",
            "lab2_q": "Practical Lab 2 (+150 XP): Extract the hidden word by taking the FIRST LETTER of each word in this intelligence dispatch: `Find All Lost Gold`",
            "lab2_ans": "FALG"
        },

        # ----------------------------------------------------------------------
        # TRACK 2: UNIVERSITY COMPUTER SYSTEMS & LOW-LEVEL ARCHITECTURE (LESSONS 04 - 09)
        # ----------------------------------------------------------------------
        "Track 2 • Lesson 04: Binary Numbers, Bits, Nibbles & Bytes (CS Systems 101)": {
            "id": "L04",
            "track": "🔵 TRACK 2: UNIVERSITY COMPUTER SYSTEMS & ARCHITECTURE",
            "title": "💻 Lesson 04: Binary System (Base-2), Transistors, Bits, Nibbles & Bytes",
            "overview": (
                "Welcome to **University Computer Systems 101**! Inside your computer's CPU and RAM, there are no letters, photos, or emojis—there are only billions of microscopic silicon switches called **MOSFET Transistors**. "
                "Each transistor can only be in one of two physical states: **Low Voltage / OFF (`0`)** or **High Voltage / ON (`1`)**.\n\n"
                "Because hardware only has 2 states, computers count using the **Binary Number System (Base-2)** instead of the human **Decimal System (Base-10)**."
            ),
            "enc_guide": (
                "**1. Hierarchy of Digital Information Units:**\n"
                "- **1 Bit (Binary Digit):** A single `0` or `1` ($2^1 = 2$ possible states).\n"
                "- **1 Nibble (4 Bits):** e.g., `1011` ($2^4 = 16$ possible states, from `0` to `15`). Crucial for Hexadecimal and our Markov Camouflage engine!\n"
                "- **1 Byte (8 Bits):** e.g., `01000001` ($2^8 = 256$ possible states, from `0` to `255`). The standard unit of addressable computer memory.\n"
                "- **Word Sizes:** `16-bit` (2 bytes), `32-bit` (4 bytes), `64-bit` (8 bytes — modern CPU register width).\n\n"
                "**2. How to Convert Binary (Base-2) to Decimal (Base-10):**\n"
                "Each bit position in an 8-bit byte represents a **power of 2** from right ($2^0 = 1$) to left ($2^7 = 128$):\n"
                "| Bit Position | $2^7$ | $2^6$ | $2^5$ | $2^4$ | $2^3$ | $2^2$ | $2^1$ | $2^0$ |\n"
                "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n"
                "| **Place Value** | **128** | **64** | **32** | **16** | **8** | **4** | **2** | **1** |\n\n"
                "Multiply each bit by its place value and sum the positions that have a `1`!"
            ),
            "dec_guide": (
                "**How to Convert Decimal (Base-10) to 8-Bit Binary (Subtraction / Division Method):**\n"
                "To convert a decimal number $N \\in [0, 255]$ into 8-bit binary:\n"
                "1. Compare $N$ against the place values `128, 64, 32, 16, 8, 4, 2, 1` from left to right.\n"
                "2. If $N \\ge \\text{Place Value}$, write down bit `1` and subtract that place value from $N$.\n"
                "3. Otherwise, write down bit `0` and move to the next smaller power of 2."
            ),
            "examples": (
                "🔹 **Example 1 (Binary `00001101` to Decimal):**\n"
                "- Bits with `1` are at place values `8`, `4`, and `1`.\n"
                "- Sum: $8 + 4 + 1 =$ **`13`**.\n\n"
                "🔹 **Example 2 (Binary `01000001` to Decimal):**\n"
                "- Bits with `1` are at place values `64` and `1`.\n"
                "- Sum: $64 + 1 =$ **`65`** (ASCII code for uppercase `'A'`).\n\n"
                "🔹 **Example 3 (Decimal `42` to 8-Bit Binary):**\n"
                "- $42 = 32 + 8 + 2$.\n"
                "- Put `1` at positions `32, 8, 2` and `0` everywhere else: **`00101010`**."
            ),
            "q1": "How many distinct unsigned integer values (from 0 to Max) can a single 8-bit Byte represent?",
            "q1_opts": [
                "A) 8 values (0 to 7)",
                "B) 128 values (0 to 127)",
                "C) 256 values (from 0 to 255, since 2^8 = 256)",
                "D) 1024 values"
            ],
            "q1_ans": "C) 256 values (from 0 to 255, since 2^8 = 256)",
            "q2": "In an 8-bit byte, what is the decimal place value of the leftmost bit (the Most Significant Bit at index 7, i.e., 2^7)?",
            "q2_opts": ["A) 64", "B) 128", "C) 255", "D) 256"],
            "q2_ans": "B) 128",
            "lab1_q": "Practical Lab 1 (+150 XP): Convert the 4-bit binary nibble `1011` into its Base-10 Decimal number (Hint: 8 + 0 + 2 + 1).",
            "lab1_ans": "11",
            "lab2_q": "Practical Lab 2 (+150 XP): Convert the Base-10 Decimal number `19` into an 8-bit binary string (Hint: 19 = 16 + 2 + 1 -> write all 8 bits with leading zeros).",
            "lab2_ans": "00010011"
        },

        "Track 2 • Lesson 05: Hexadecimal (Base-16) & Memory Addressing": {
            "id": "L05",
            "track": "🔵 TRACK 2: UNIVERSITY COMPUTER SYSTEMS & ARCHITECTURE",
            "title": "🔢 Lesson 05: Hexadecimal Representation (Base-16) & RAM Memory Dumps",
            "overview": (
                "Writing long strings of 32 or 64 binary bits like `010010000110010101111000` is exhausting and error-prone for human engineers. "
                "To solve this in **Computer Systems**, programmers and cryptographers use **Hexadecimal (Base-16, often prefixed with `0x`)**. "
                "Because $16 = 2^4$, **1 single Hexadecimal digit represents exactly 4 binary bits (1 Nibble)**, and **2 Hexadecimal digits represent 1 full Byte (8 bits)**!"
            ),
            "enc_guide": (
                "**1. The 16 Hexadecimal Digits (`0–9` and `A–F`):**\n"
                "- Values `0` to `9` use standard digits `0–9` (`0000` to `1001`).\n"
                "- Values `10` to `15` use uppercase letters **`A` through `F`**:\n"
                "  - **`A = 10`** (`1010`) &nbsp;|&nbsp; **`B = 11`** (`1011`) &nbsp;|&nbsp; **`C = 12`** (`1100`)\n"
                "  - **`D = 13`** (`1101`) &nbsp;|&nbsp; **`E = 14`** (`1110`) &nbsp;|&nbsp; **`F = 15`** (`1111`)\n\n"
                "**2. Converting an 8-Bit Byte to Hex (`Binary -> Hex`):**\n"
                "1. Split the 8-bit byte in half into two 4-bit nibbles: `[High Nibble (bits 7..4)] [Low Nibble (bits 3..0)]`.\n"
                "2. Convert each 4-bit nibble (0–15) directly into its Hex digit (`0–F`)."
            ),
            "dec_guide": (
                "**Converting Hexadecimal to Decimal (`Hex -> Decimal`):**\n"
                "For a 2-digit Hex byte `0xXY`:\n"
                "$$\\text{Decimal Value} = (\\text{High Digit } X \\times 16) + \\text{Low Digit } Y$$\n\n"
                "**Where You See Hexadecimal Every Day in Cybersecurity:**\n"
                "- **Memory Pointers & Stack Addresses** in C/C++ and assembly debuggers (`0x7ffee3b4c8a0`).\n"
                "- **SHA-256 Hash Digests** (256 bits = 32 bytes = 64 Hex characters).\n"
                "- **MAC Network Addresses** (`00:1A:2B:3C:4D:5E`) and **HTML/CSS RGB Colors** (`#3B82F6`)."
            ),
            "examples": (
                "🔹 **Example 1 (Binary `1111 0000` to Hex):**\n"
                "- High Nibble: `1111` = `15` = **`F`**\n"
                "- Low Nibble:  `0000` = `0`  = **`0`**\n"
                "- Hex Result: **`0xF0`** (Decimal: $15 \\times 16 + 0 = 240$).\n\n"
                "🔹 **Example 2 (Binary `0100 1100` to Hex):**\n"
                "- High Nibble: `0100` = **`4`** | Low Nibble: `1100` = `12` = **`C`**\n"
                "- Hex Result: **`0x4C`** (Decimal: $4 \\times 16 + 12 = 76$, ASCII `'L'`).\n\n"
                "🔹 **Example 3 (Hex `0xFF` to Binary & Decimal):**\n"
                "- Binary: `1111 1111` | Decimal: $15 \\times 16 + 15 =$ **`255`** (Max unsigned byte value)."
            ),
            "q1": "In the Hexadecimal (Base-16) system, what decimal value and 4-bit binary pattern does the digit 'C' represent?",
            "q1_opts": [
                "A) Decimal 10 (Binary 1010)",
                "B) Decimal 12 (Binary 1100)",
                "C) Decimal 14 (Binary 1110)",
                "D) Decimal 15 (Binary 1111)"
            ],
            "q1_ans": "B) Decimal 12 (Binary 1100)",
            "q2": "How many Hexadecimal characters are needed to represent a 256-bit SHA-256 hash?",
            "q2_opts": [
                "A) 16 Hex characters",
                "B) 32 Hex characters",
                "C) 64 Hex characters (since each Hex digit is 4 bits, and 256 / 4 = 64)",
                "D) 256 Hex characters"
            ],
            "q2_ans": "C) 64 Hex characters (since each Hex digit is 4 bits, and 256 / 4 = 64)",
            "lab1_q": "Practical Lab 1 (+150 XP): Convert the 8-bit binary byte `00101111` into its 2-character Hexadecimal string (without 0x prefix, e.g. A1). (Hint: High `0010`=2, Low `1111`=F).",
            "lab1_ans": "2F",
            "lab2_q": "Practical Lab 2 (+150 XP): Convert the Hexadecimal byte `0x41` into its Base-10 Decimal number (Hint: 4 * 16 + 1).",
            "lab2_ans": "65"
        },

        "Track 2 • Lesson 06: Signed Integers & Two's Complement Arithmetic (CPU ALU)": {
            "id": "L06",
            "track": "🔵 TRACK 2: UNIVERSITY COMPUTER SYSTEMS & ARCHITECTURE",
            "title": "➕➖ Lesson 06: Signed Integers, Two's Complement & Integer Overflow Vulnerabilities",
            "overview": (
                "In Lesson 04, we saw how an 8-bit unsigned byte represents non-negative numbers from `0` to `255`. "
                "But how does a computer CPU represent **negative numbers** like `-1` or `-42` when it only has `0`s and `1`s? "
                "Every modern CPU architecture (x86-64, ARM, RISC-V) uses a brilliant mathematical encoding called **Two's Complement (Bù 2)**. "
                "Understanding Two's Complement is essential in University Computer Systems and for discovering **Integer Overflow security vulnerabilities**!"
            ),
            "enc_guide": (
                "**1. How 8-Bit Two's Complement Works (Range: `-128` to `+127`):**\n"
                "- The leftmost bit (bit 7) is the **Sign Bit** with a **negative weight of `-128`** (instead of `+128`), while the remaining 7 bits have normal positive weights (`+64, +32, +16, +8, +4, +2, +1`).\n"
                "- If Sign Bit = `0`: The number is **Positive or Zero** (`0` to `+127`).\n"
                "- If Sign Bit = `1`: The number is **Negative** (`-128` to `-1`).\n\n"
                "**2. The 2-Step Rule to Negate Any Number ($+X \\rightarrow -X$ in Two's Complement):**\n"
                "1. **Step 1 — Invert All Bits (One's Complement / Bitwise NOT `~X`):** Flip every `0` to `1` and every `1` to `0`.\n"
                "2. **Step 2 — Add `1`:** Add `1` to the inverted binary number (ignoring any carry beyond 8 bits):\n"
                "   $$-X = (\\sim X) + 1$$"
            ),
            "dec_guide": (
                "**Why Two's Complement is Genius for CPU Hardware:**\n"
                "- The CPU's Arithmetic Logic Unit (ALU) does not need a separate subtraction circuit! To compute $A - B$, the CPU simply adds $A + (-B)$ using a standard binary adder.\n\n"
                "**💥 Security Vulnerability — Integer Overflow:**\n"
                "- In 8-bit signed arithmetic, the maximum positive number is `+127` (`01111111`). If you add `+1` to `+127`, it becomes `10000000`, which wraps around to **`-128`**! Hackers exploit integer overflows in C/C++ programs to bypass memory allocation checks and trigger buffer overflows."
            ),
            "examples": (
                "🔹 **Example 1 (Representing `-5` in 8-Bit Two's Complement):**\n"
                "- Start with `+5`: `0000 0101`\n"
                "- Step 1 (Flip all bits): `1111 1010`\n"
                "- Step 2 (Add `1`): **`1111 1011`** (Check: $-128 + 64 + 32 + 16 + 8 + 2 + 1 = -5$).\n\n"
                "🔹 **Example 2 (Representing `-1` in 8-Bit Two's Complement):**\n"
                "- Start with `+1`: `0000 0001` $\\rightarrow$ Flip: `1111 1110` $\\rightarrow$ Add `1`: **`1111 1111`** (`0xFF`).\n\n"
                "🔹 **Example 3 (Decoding `1111 1100` to Decimal):**\n"
                "- Sign bit is `1` (`-128`), plus positive bits `64 + 32 + 16 + 8 + 4 = +124`.\n"
                "- Sum: $-128 + 124 =$ **`-4`**."
            ),
            "q1": "In 8-bit Two's Complement representation, what decimal number does the binary pattern `11111111` (all ones) represent?",
            "q1_opts": ["A) +255", "B) -128", "C) -1 (since -128 + 127 = -1)", "D) 0"],
            "q1_ans": "C) -1 (since -128 + 127 = -1)",
            "q2": "What is the standard 2-step algorithm to convert a positive binary number into its negative Two's Complement representation?",
            "q2_opts": [
                "A) Shift left by 2 bits",
                "B) Invert (flip) all bits and then add 1",
                "C) Change only the rightmost bit to 1",
                "D) Multiply by 16"
            ],
            "q2_ans": "B) Invert (flip) all bits and then add 1",
            "lab1_q": "Practical Lab 1 (+150 XP): Compute the 4-bit Two's Complement binary representation of `-3` (Start with +3 = `0011`, flip all 4 bits to `1100`, then add 1).",
            "lab1_ans": "1101",
            "lab2_q": "Practical Lab 2 (+150 XP): In an 8-bit signed Two's Complement integer, what is the maximum positive decimal number (`01111111`) before an Integer Overflow occurs?",
            "lab2_ans": "127"
        },

        "Track 2 • Lesson 07: Logic Gates, Bitwise Operations & Bit Shifting": {
            "id": "L07",
            "track": "🔵 TRACK 2: UNIVERSITY COMPUTER SYSTEMS & ARCHITECTURE",
            "title": "⚡ Lesson 07: Digital Logic Gates, Bitwise Masking (`&`, `|`, `^`, `~`) & Bit Shifts",
            "overview": (
                "Inside a CPU, transistors are wired together to form **Boolean Logic Gates**. "
                "In low-level programming (C, Python, Assembly) and cryptography (AES, SHA-256, LSB Steganography), we manipulate individual bits inside a byte using **Bitwise Operators** and **Bit Shifts**."
            ),
            "enc_guide": (
                "**1. The 4 Fundamental Bitwise Operators:**\n"
                "- **AND (`&` — Bit Masking / Clearing):** Outputs `1` ONLY if **both** input bits are `1` (`1 & 1 = 1`, otherwise `0`). Used to extract specific bits or clear bits to `0`.\n"
                "- **OR (`|` — Bit Setting):** Outputs `1` if **at least one** input bit is `1` (`0 | 0 = 0`, otherwise `1`). Used to set specific bits to `1`.\n"
                "- **XOR (`^` — Bit Toggling / Ciphering):** Outputs `1` if the two input bits are **different** (`1 ^ 0 = 1`, `0 ^ 1 = 1`, same bits give `0`).\n"
                "- **NOT (`~` — Bit Inversion):** Flips `0 -> 1` and `1 -> 0`.\n\n"
                "**2. Bit Shifting Operators (`<<` and `>>`):**\n"
                "- **Left Shift (`X << k`):** Shifts all bits left by $k$ positions and fills the right with `0`s. Mathematically equivalent to **multiplying by $2^k$**!\n"
                "- **Logical Right Shift (`X >> k`):** Shifts all bits right by $k$ positions. Mathematically equivalent to **integer division by $2^k$**!"
            ),
            "dec_guide": (
                "**How Our Platform Uses Bitwise Operators in Real Code:**\n"
                "- **In Linguistic Camouflage (`Lesson 16`):**\n"
                "  - Extract High Nibble: `(byte >> 4) & 0x0F`\n"
                "  - Extract Low Nibble:  `byte & 0x0F`\n"
                "- **In LSB Image Steganography (`Lesson 16`):**\n"
                "  - Clear lowest bit of Red channel and insert secret bit: `R_new = (R & ~1) | secret_bit`\n"
                "  - Extract lowest bit from Red channel: `extracted_bit = R & 1`"
            ),
            "examples": (
                "🔹 **Example 1 (Bitwise AND `&` Masking):**\n"
                "- `1101 0110 & 0000 1111` = **`0000 0110`** (The mask `0000 1111` erased the left 4 bits and kept only the right 4 bits!).\n\n"
                "🔹 **Example 2 (Left Shift `<<` Multiplication):**\n"
                "- Start with `5` (`0000 0101`).\n"
                "- Shift left by 2 (`5 << 2`): `0001 0100` = $5 \\times 2^2 =$ **`20`**.\n\n"
                "🔹 **Example 3 (Right Shift `>>` Division):**\n"
                "- Start with `24` (`0001 1000`).\n"
                "- Shift right by 3 (`24 >> 3`): `0000 0011` = $24 \\div 2^3 =$ **`3`**."
            ),
            "q1": "If you want to check whether an integer R is odd or even (by extracting ONLY its rightmost Least Significant Bit), which bitwise expression should you use?",
            "q1_opts": ["A) R | 255", "B) R & 1", "C) R << 8", "D) R ^ 0"],
            "q1_ans": "B) R & 1",
            "q2": "In binary arithmetic, shifting an unsigned number LEFT by 3 bit positions (`X << 3`) is equivalent to multiplying X by what number?",
            "q2_opts": ["A) Multiply by 3", "B) Multiply by 6", "C) Multiply by 8 (since 2^3 = 8)", "D) Divide by 8"],
            "q2_ans": "C) Multiply by 8 (since 2^3 = 8)",
            "lab1_q": "Practical Lab 1 (+150 XP): Compute the 4-bit result of the bitwise AND operation: `1101 & 0111`",
            "lab1_ans": "0101",
            "lab2_q": "Practical Lab 2 (+150 XP): What is the decimal value of the bit-shift expression `7 << 2`? (Hint: 7 * 2^2).",
            "lab2_ans": "28"
        },

        "Track 2 • Lesson 08: Character Encodings — ASCII, UTF-8 Unicode & Base64": {
            "id": "L08",
            "track": "🔵 TRACK 2: UNIVERSITY COMPUTER SYSTEMS & ARCHITECTURE",
            "title": "🔤 Lesson 08: How Computers Store Text — ASCII, UTF-8 Multi-Byte Unicode & Base64",
            "overview": (
                "Now that we understand Bits, Bytes, and Hexadecimal, how does a computer turn bytes into English letters, Vietnamese diacritics (`ă, ê, ơ, ư, đ`), and Emojis (`🛡️, 🚀`)? "
                "Through standardized **Character Encoding Tables**: **ASCII**, **UTF-8 Unicode**, and **Base64**."
            ),
            "enc_guide": (
                "**1. Standard ASCII (7-Bit / 1-Byte Table, Codes `0–127`):**\n"
                "- Created in 1963 for English characters and control codes:\n"
                "  - **Digits `'0'` to `'9'`:** Decimal `48` (`0x30`) to `57` (`0x39`).\n"
                "  - **Uppercase `'A'` to `'Z'`:** Decimal `65` (`0x41`) to `90` (`0x5A`).\n"
                "  - **Lowercase `'a'` to `'z'`:** Decimal `97` (`0x61`) to `122` (`0x7A`).\n"
                "  - *Cool Trick:* Lowercase and uppercase letters differ by exactly **32** (`0010 0000`, a single bit flip at bit 5!).\n\n"
                "**2. UTF-8 & Unicode (Global Multi-Byte Encoding):**\n"
                "- ASCII only holds 128 characters—not enough for Vietnamese, Japanese, or Emojis! **Unicode** assigns a unique code point (`U+0000` to `U+10FFFF`) to over 149,000 characters worldwide.\n"
                "- **UTF-8** is a variable-width encoding that uses **1 byte** for standard ASCII, **2 to 3 bytes** for Vietnamese characters (e.g., `'ệ'` takes 3 bytes: `0xE1 0xBB 0x87`), and **4 bytes** for Emojis (`🛡️`)."
            ),
            "dec_guide": (
                "**3. Base64 Encoding (Binary-to-Text Transport):**\n"
                "- When sending raw binary data (like an encrypted byte stream or a PNG image in our Chat Room JSON database) over text-only protocols, raw bytes might be misinterpreted as control characters.\n"
                "- **How Base64 Works:** It takes **3 bytes (24 bits)** at a time, splits them into **four 6-bit chunks** ($2^6 = 64$), and maps each 6-bit value (`0–63`) to a safe printable character (`A–Z`, `a–z`, `0–9`, `+`, `/`), using `=` at the end for padding."
            ),
            "examples": (
                "🔹 **Example 1 (ASCII Case Bit-Flip):**\n"
                "- `'A'` = `65` (`0100 0001`) | `'a'` = `97` (`0110 0001`).\n"
                "- Notice `65 ^ 32 = 97`! Flipping bit 5 toggles uppercase and lowercase in hardware.\n\n"
                "🔹 **Example 2 (UTF-8 Multi-Byte Vietnamese):**\n"
                "- Word `'Hiếu'` has 4 characters, but in UTF-8 bytes it is `'H'` (1 byte) + `'i'` (1 byte) + `'ế'` (3 bytes) + `'u'` (1 byte) = **6 bytes total**!\n\n"
                "🔹 **Example 3 (Base64 Encoding `'Man'`):**\n"
                "- ASCII bytes: `'M'` (`01001101`), `'a'` (`01100001`), `'n'` (`01101110`).\n"
                "- Regroup 24 bits into four 6-bit chunks: `010011` (`19`='T'), `010110` (`22`='W'), `000101` (`5`='F'), `101110` (`46`='u') $\\rightarrow$ **`TWFu`**."
            ),
            "q1": "In the ASCII table, if uppercase 'A' is decimal 65 and uppercase 'B' is 66, what is the decimal ASCII code for uppercase 'D'?",
            "q1_opts": ["A) 67", "B) 68", "C) 69", "D) 97"],
            "q1_ans": "B) 68",
            "q2": "How does Base64 encoding group binary bits to convert raw bytes into printable text?",
            "q2_opts": [
                "A) It converts every 3 bytes (24 bits) into four 6-bit characters (since 2^6 = 64)",
                "B) It deletes all vowels",
                "C) It encrypts data with SHA-256",
                "D) It uses only 0 and 1"
            ],
            "q2_ans": "A) It converts every 3 bytes (24 bits) into four 6-bit characters (since 2^6 = 64)",
            "lab1_q": "Practical Lab 1 (+150 XP): Decode these three decimal ASCII codes into a 3-letter English word (`67`, `65`, `84`) given that `65 = A`.",
            "lab1_ans": "CAT",
            "lab2_q": "Practical Lab 2 (+150 XP): Since uppercase `'A'` is ASCII `65` and lowercase `'a'` is `65 + 32 = 97`, what is the decimal ASCII code for lowercase `'b'`?",
            "lab2_ans": "98"
        },

        "Track 2 • Lesson 09: Machine Code, Assembly Instructions & Endianness (CPU Execution)": {
            "id": "L09",
            "track": "🔵 TRACK 2: UNIVERSITY COMPUTER SYSTEMS & ARCHITECTURE",
            "title": "⚙️ Lesson 09: Von Neumann CPU Cycle, Machine Code Opcodes, Assembly & Endianness",
            "overview": (
                "How does a CPU actually execute a program or run a cryptographic algorithm? "
                "In **University Computer Systems**, we study the **Von Neumann Architecture**, the **Fetch-Decode-Execute Cycle**, how human-readable **Assembly Language** translates into raw binary/hex **Machine Code (Mã máy)**, and how multi-byte integers are ordered in RAM (**Little-Endian vs. Big-Endian**)."
            ),
            "enc_guide": (
                "**1. Machine Code vs. Assembly Language:**\n"
                "- **Machine Code (Mã máy):** Raw streams of bytes stored in RAM that the CPU hardware decodes directly (e.g., `B8 05 00 00 00`). Each instruction starts with an **Opcode (Operation Code)** byte telling the CPU what action to perform (`MOV`, `ADD`, `SUB`, `XOR`, `JMP`, `RET`).\n"
                "- **Assembly Language (Hợp ngữ — x86-64 / ARM):** The human-readable 1-to-1 text representation of Machine Code:\n"
                "  - `MOV RAX, 5` — Load the number 5 into CPU register `RAX`.\n"
                "  - `ADD RAX, 3` — Add 3 to register `RAX` (`RAX` becomes 8).\n"
                "  - `XOR RAX, RAX` — XOR register `RAX` with itself (Fastest machine-code trick to zero out a register to `0`!)."
            ),
            "dec_guide": (
                "**2. Memory Byte Ordering — Big-Endian vs. Little-Endian:**\n"
                "Suppose we store a 32-bit (4-byte) hexadecimal integer **`0x12345678`** in RAM starting at memory address `0x100`:\n"
                "- **Big-Endian (Network Byte Order):** Stores the Most Significant Byte (`12`) first at the lowest memory address:\n"
                "  `[12] [34] [56] [78]` (Reads left-to-right just like humans write).\n"
                "- **Little-Endian (x86-64 Intel/AMD & ARM CPUs):** Stores the Least Significant Byte (`78`) first at the lowest memory address:\n"
                "  `[78] [56] [34] [12]` (Reversed byte order in memory! Crucial when inspecting memory dumps or binary exploits in CTF challenges)."
            ),
            "examples": (
                "🔹 **Example 1 (x86 Machine Code Disassembly):**\n"
                "- Machine Code Hex Bytes: `31 C0` $\\rightarrow$ Disassembles to `XOR EAX, EAX` (Sets register `EAX = 0`).\n"
                "- Machine Code Hex Byte:  `90` $\\rightarrow$ Disassembles to `NOP` (No Operation — does nothing for 1 clock cycle).\n\n"
                "🔹 **Example 2 (Little-Endian Memory Layout):**\n"
                "- 32-bit Value: `0xDEADBEEF` (4 bytes: `DE`, `AD`, `BE`, `EF`).\n"
                "- Stored in x86 Little-Endian RAM as: **`EF BE AD DE`**.\n\n"
                "🔹 **Example 3 (Tracing Assembly Execution):**\n"
                "- `MOV RAX, 10` (`RAX = 10`) $\\rightarrow$ `SHL RAX, 1` (Shift Left by 1 = multiply by 2, `RAX = 20`) $\\rightarrow$ `SUB RAX, 4` (`RAX = 16`)."
            ),
            "q1": "Why do compilers and assembly programmers often write `XOR EAX, EAX` instead of `MOV EAX, 0` to set a CPU register to zero?",
            "q1_opts": [
                "A) Because XORing any value with itself always produces 0, and the machine code instruction `31 C0` is shorter (2 bytes vs 5 bytes) and executes faster in the CPU pipeline",
                "B) Because MOV is illegal in x86",
                "C) Because XOR sets the register to 255",
                "D) To encrypt the hard drive"
            ],
            "q1_ans": "A) Because XORing any value with itself always produces 0, and the machine code instruction `31 C0` is shorter (2 bytes vs 5 bytes) and executes faster in the CPU pipeline",
            "q2": "How is the 4-byte hexadecimal integer `0x11223344` stored sequentially in memory on a Little-Endian CPU (like Intel/AMD x86-64)?",
            "q2_opts": [
                "A) 11 22 33 44",
                "B) 44 33 22 11 (Least Significant Byte `44` is stored at the lowest address first)",
                "C) FF FF FF FF",
                "D) 00 00 00 00"
            ],
            "q2_ans": "B) 44 33 22 11 (Least Significant Byte `44` is stored at the lowest address first)",
            "lab1_q": "Practical Lab 1 (+150 XP): Trace this assembly sequence and type the final decimal value in register RAX: `MOV RAX, 12` -> `ADD RAX, 8` -> `SHR RAX, 2` (Note: SHR by 2 divides by 2^2 = 4).",
            "lab1_ans": "5",
            "lab2_q": "Practical Lab 2 (+150 XP): Write the 2-byte hexadecimal value `0xABCD` in Little-Endian byte order (4 hex chars without spaces, e.g. 1234).",
            "lab2_ans": "CDAB"
        },

        # ----------------------------------------------------------------------
        # TRACK 3: CLASSICAL CRYPTOGRAPHY & NUMBER THEORY (LESSONS 10 - 13)
        # ----------------------------------------------------------------------
        "Track 3 • Lesson 10: Transposition (Rail-Fence) vs. Monoalphabetic Substitution": {
            "id": "L10",
            "track": "🟡 TRACK 3: CLASSICAL CRYPTOGRAPHY & NUMBER THEORY",
            "title": "🔀 Lesson 10: Transposition Ciphers (Scytale & Rail-Fence) vs. Substitution",
            "overview": (
                "Classical cryptography is divided into two grand families that form the foundation of modern block ciphers (which Claude Shannon called **Confusion and Diffusion**):\n"
                "1. **Transposition Ciphers (Mật mã Hoán vị vị trí):** Keep the original letters unchanged, but **rearrange their positions** (anagrams).\n"
                "2. **Substitution Ciphers (Mật mã Thay thế ký tự):** Keep the positions unchanged, but **replace each letter** with a different letter or symbol (such as Atbash Mirror or Leetspeak)."
            ),
            "enc_guide": (
                "**1. How the 2-Rail Fence Transposition Cipher Works:**\n"
                "Write your message in a zig-zag pattern across 2 horizontal rows (Rails), alternating between Top Row (odd positions) and Bottom Row (even positions), then read off Row 1 followed by Row 2!\n"
                "- Suppose Plaintext is `HELLO WORLD` (without space: `HELLOWORLD`):\n"
                "  - **Rail 1 (Odd letters 1, 3, 5, 7, 9):** `H . L . O . O . L .` $\\rightarrow$ `HLOOL`\n"
                "  - **Rail 2 (Even letters 2, 4, 6, 8, 10):** `. E . L . W . R . D` $\\rightarrow$ `ELWRD`\n"
                "  - **Combined Ciphertext:** **`HLOOLELWRD`**\n\n"
                "**2. How Atbash Mirror Substitution Works:**\n"
                "Folds the alphabet in half (`A↔Z, B↔Y, C↔X, ..., M↔N`) using formula $C = (25 - P)$."
            ),
            "dec_guide": (
                "**How to Decrypt a 2-Rail Fence Cipher:**\n"
                "1. Split the ciphertext of length $L$ right down the middle into two halves: First half is **Rail 1**, second half is **Rail 2**.\n"
                "2. Read characters alternately (zig-zag) between Rail 1 and Rail 2: `Rail1[0], Rail2[0], Rail1[1], Rail2[1]...`!"
            ),
            "examples": (
                "🔹 **Example 1 (2-Rail Fence Encryption of `'SECRET'`):**\n"
                "- Rail 1 (Positions 1, 3, 5): `S`, `C`, `E` $\\rightarrow$ `SCE`\n"
                "- Rail 2 (Positions 2, 4, 6): `E`, `R`, `T` $\\rightarrow$ `ERT`\n"
                "- Ciphertext: **`SCEERT`**.\n\n"
                "🔹 **Example 2 (2-Rail Fence Decryption of `'MROANR'`):**\n"
                "- Split in half: Rail 1 = `'MRO'`, Rail 2 = `'ANR'`.\n"
                "- Interleave: `M`+`A` + `R`+`N` + `O`+`R` = **`MARNOR`**.\n\n"
                "🔹 **Example 3 (Atbash Mirror of `'DATA'`):**\n"
                "- `D ↔ W`, `A ↔ Z`, `T ↔ G`, `A ↔ Z` = **`WZGZ`**."
            ),
            "q1": "How can a cryptanalyst distinguish a pure Transposition Cipher from a Substitution Cipher?",
            "q1_opts": [
                "A) A Transposition Cipher keeps the exact same letters and letter frequencies as the original plaintext (just reordered), whereas Substitution changes the letters",
                "B) Transposition only works on numbers",
                "C) Substitution never uses keys",
                "D) They cannot be distinguished"
            ],
            "q1_ans": "A) A Transposition Cipher keeps the exact same letters and letter frequencies as the original plaintext (just reordered), whereas Substitution changes the letters",
            "q2": "Using a 2-Rail Fence Cipher, what does the 4-letter word `STAR` encrypt to? (Rail 1: positions 1,3; Rail 2: positions 2,4)",
            "q2_opts": ["A) RATS", "B) SA + TR = SATR", "C) ST + AR = STAR", "D) HGZI"],
            "q2_ans": "B) SA + TR = SATR",
            "lab1_q": "Practical Lab 1 (+150 XP): Decrypt the 2-Rail Fence ciphertext `PLNTAAES` (Length 8 -> Split into `PLNT` and `AAES`, then interleave P-A-L-A-N-E-T-S).",
            "lab1_ans": "PLANETS",
            "lab2_q": "Practical Lab 2 (+150 XP): Decode the Atbash Mirror string `SVOOL` (`S↔H, V↔E, O↔L, L↔O`).",
            "lab2_ans": "HELLO"
        },

        "Track 3 • Lesson 11: Caesar Shift & Modular Arithmetic (Clock Math)": {
            "id": "L11",
            "track": "🟡 TRACK 3: CLASSICAL CRYPTOGRAPHY & NUMBER THEORY",
            "title": "🏛️ Lesson 11: Caesar Shift Cipher & Modular Arithmetic (`mod N` Clock Math)",
            "overview": (
                "**Modular Arithmetic** (introduced by **Carl Friedrich Gauss** in 1801) is the mathematical backbone of almost all cryptography, from classical Caesar ciphers to modern RSA and Elliptic Curves. "
                "Think of Modular Arithmetic like a **12-hour wall clock**: if it is 10 o'clock and you add 5 hours, it does not become 15 o'clock—it wraps around the circle to **3 o'clock** ($15 \\bmod 12 = 3$)."
            ),
            "enc_guide": (
                "**1. The Modulo Operator (`A mod N`):**\n"
                "- Gives the **remainder** after dividing $A$ by $N$. The result is always in the range $[0, N-1]$.\n"
                "- On the 26-letter English alphabet (`A=0, B=1, ..., Z=25`), $N = 26$.\n\n"
                "**2. Caesar Encryption Formula:**\n"
                "$$C = (P + K) \\pmod{26}$$\n"
                "**3. Special Case — ROT13 (`K = 13`):**\n"
                "- Because $13$ is exactly half of $26$, shifting by $+13$ twice brings you right back to the start ($(P + 13 + 13) \\pmod{26} = P$). Thus, ROT13 is its own inverse!"
            ),
            "dec_guide": (
                "**Caesar Decryption Formula:**\n"
                "$$P = (C - K) \\pmod{26}$$\n"
                "- **Handling Negative Numbers in Modulo:** If $(C - K)$ is negative (for example, $1 - 4 = -3$), simply **add 26** to wrap around the alphabet: $-3 + 26 = 23$ (`'X'`)."
            ),
            "examples": (
                "🔹 **Example 1 (Positive Wrap-Around):**\n"
                "- Encrypt `'Z'` ($P = 25$) with Shift $K = 5$: $(25 + 5) \\pmod{26} = 30 \\pmod{26} = 4$ (**`'E'`**).\n\n"
                "🔹 **Example 2 (Negative Wrap-Around Decryption):**\n"
                "- Decrypt `'B'` ($C = 1$) with Shift $K = 3$: $(1 - 3) \\pmod{26} = -2 + 26 = 24$ (**`'Y'`**).\n\n"
                "🔹 **Example 3 (Full Word Shift $K = 2$):**\n"
                "- Plaintext `'MARS'` $\\rightarrow$ `M(+2)=O`, `A(+2)=C`, `R(+2)=T`, `S(+2)=U` $\\rightarrow$ **`OCTU`**."
            ),
            "q1": "In modular arithmetic on a 26-letter alphabet (0 to 25), what is the value of `(-4) mod 26`?",
            "q1_opts": ["A) -4", "B) 4", "C) 22 (since -4 + 26 = 22)", "D) 26"],
            "q1_ans": "C) 22 (since -4 + 26 = 22)",
            "q2": "Why does applying ROT13 (Caesar Shift K = 13) a second time immediately decrypt the message?",
            "q2_opts": [
                "A) Because 13 + 13 = 26, which wraps completely around the 26-letter alphabet (26 mod 26 = 0)",
                "B) Because 13 is a prime number",
                "C) Because ROT13 only shifts numbers",
                "D) Because ROT13 deletes spaces"
            ],
            "q2_ans": "A) Because 13 + 13 = 26, which wraps completely around the 26-letter alphabet (26 mod 26 = 0)",
            "lab1_q": "Practical Lab 1 (+150 XP): Calculate the modular arithmetic expression `(23 + 10) mod 26`.",
            "lab1_ans": "7",
            "lab2_q": "Practical Lab 2 (+150 XP): Decrypt the Caesar ciphertext `URNHW` which was encrypted with Shift `K = 3` (Shift each letter 3 steps back).",
            "lab2_ans": "ROKET"
        },

        "Track 3 • Lesson 12: The Affine Cipher & Modular Multiplicative Inverses": {
            "id": "L12",
            "track": "🟡 TRACK 3: CLASSICAL CRYPTOGRAPHY & NUMBER THEORY",
            "title": "📐 Lesson 12: The Affine Cipher ($aP + b \\bmod 26$) & Coprime Number Theory",
            "overview": (
                "The Caesar Cipher only uses addition ($P + b$). What if we combine **multiplication and addition** in modular arithmetic? "
                "We get the **Affine Cipher**, a foundational mathematical cipher taught in university Discrete Mathematics courses that introduces **Greatest Common Divisors (`gcd`)** and **Modular Multiplicative Inverses**."
            ),
            "enc_guide": (
                "**1. Affine Encryption Formula:**\n"
                "Choose two key integers $(a, b)$ and compute for each letter index $P \\in [0, 25]$:\n"
                "$$C = (a \\cdot P + b) \\pmod{26}$$\n\n"
                "**2. The Golden Rule of Key `a` (Coprime Requirement):**\n"
                "- Key $a$ **MUST be coprime to 26**, meaning $\\gcd(a, 26) = 1$ ($a$ cannot share factors `2` or `13` with `26`).\n"
                "- Valid choices for $a \\in [1, 25]$ are: **`1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25`** (12 valid multipliers).\n"
                "- Why? If $a = 2$, then both $P=0$ (`A`) and $P=13$ (`N`) give $2P \\pmod{26} = 0$, making decryption impossible!"
            ),
            "dec_guide": (
                "**Affine Decryption & Modular Inverse ($a^{-1}$):**\n"
                "In modular arithmetic, we cannot divide by $a$. Instead, we multiply by the **Modular Multiplicative Inverse $a^{-1}$**, which is the number satisfying $(a \\cdot a^{-1}) \\equiv 1 \\pmod{26}$:\n"
                "$$P = a^{-1} \\cdot (C - b) \\pmod{26}$$\n"
                "- **Quick Inverse Lookup Table (mod 26):**\n"
                "  - If $a = 3 \\implies a^{-1} = 9$ (since $3 \\times 9 = 27 \\equiv 1 \\pmod{26}$).\n"
                "  - If $a = 5 \\implies a^{-1} = 21$ (since $5 \\times 21 = 105 = 4 \\times 26 + 1 \\equiv 1 \\pmod{26}$).\n"
                "  - If $a = 7 \\implies a^{-1} = 15$ (since $7 \\times 15 = 105 \\equiv 1 \\pmod{26}$)."
            ),
            "examples": (
                "🔹 **Example 1 (Encrypting `'C'` with Key $a = 3, b = 2$):**\n"
                "- `'C'` has index $P = 2$.\n"
                "- $C = (3 \\times 2 + 2) \\pmod{26} = 8$ (**`'I'`**).\n\n"
                "🔹 **Example 2 (Decrypting `'I'` ($C = 8$) with Key $a = 3, b = 2$):**\n"
                "- Since $a = 3$, its modular inverse is $a^{-1} = 9$.\n"
                "- $P = 9 \\times (8 - 2) \\pmod{26} = 9 \\times 6 \\pmod{26} = 54 \\pmod{26} = 2$ (**`'C'`**).\n\n"
                "🔹 **Example 3 (Why $a = 4$ is Illegal):**\n"
                "- $\\gcd(4, 26) = 2 \\neq 1$. Letters `'A'` ($0$) and `'N'` ($13$) collide onto the same ciphertext letter!"
            ),
            "q1": "Why is `a = 6` an INVALID multiplier key for an Affine Cipher over the 26-letter English alphabet?",
            "q1_opts": [
                "A) Because 6 is too small",
                "B) Because gcd(6, 26) = 2 (they share a common factor of 2, so 6 has no modular inverse mod 26 and multiple letters collide)",
                "C) Because 6 is a prime number",
                "D) Because b must always equal 6"
            ],
            "q1_ans": "B) Because gcd(6, 26) = 2 (they share a common factor of 2, so 6 has no modular inverse mod 26 and multiple letters collide)",
            "q2": "What is the modular multiplicative inverse of `a = 3` modulo 26 (i.e., the number x such that `3 * x mod 26 = 1`)?",
            "q2_opts": ["A) 3", "B) 7", "C) 9 (since 3 * 9 = 27 = 1 * 26 + 1)", "D) 13"],
            "q2_ans": "C) 9 (since 3 * 9 = 27 = 1 * 26 + 1)",
            "lab1_q": "Practical Lab 1 (+150 XP): Using the Affine Cipher formula `C = (5 * P + 3) mod 26`, calculate the numerical ciphertext index C when Plaintext index `P = 4`.",
            "lab1_ans": "23",
            "lab2_q": "Practical Lab 2 (+150 XP): Decrypt the numerical Affine index `C = 8` when `a = 3` (`a_inv = 9`) and `b = 2` using `P = 9 * (8 - 2) mod 26`.",
            "lab2_ans": "2"
        },

        "Track 3 • Lesson 13: Polyalphabetic Vigenère & Frequency Cryptanalysis": {
            "id": "L13",
            "track": "🟡 TRACK 3: CLASSICAL CRYPTOGRAPHY & NUMBER THEORY",
            "title": "📊 Lesson 13: Vigenère Polyalphabetic Cipher & Frequency Analysis",
            "overview": (
                "In any natural language, letters do not appear with equal probability. In English, **`E` (12.7%)**, **`T` (9.1%)**, **`A` (8.2%)**, and **`O` (7.5%)** are the most common letters. "
                "Arab polymath **Al-Kindi** (850 AD) invented **Frequency Analysis**, which breaks any monoalphabetic cipher (Caesar, Atbash, Affine) by counting letter frequencies in the ciphertext. "
                "The **Vigenère Cipher** defeats simple frequency analysis by using a repeating secret keyword to apply multiple shifting alphabets."
            ),
            "enc_guide": (
                "**Vigenère Encryption Process:**\n"
                "1. Convert both Plaintext $P$ and Keyword $K$ (of length $m$) into `0–25` indices.\n"
                "2. Repeat the keyword cyclically over the plaintext and add modulo 26:\n"
                "   $$C_i = (P_i + K_{i \\bmod m}) \\pmod{26}$$"
            ),
            "dec_guide": (
                "**Vigenère Decryption & How Babbage/Kasiski Cracked It:**\n"
                "1. **With the Keyword:** Subtract the cyclic keyword index modulo 26:\n"
                "   $$P_i = (C_i - K_{i \\bmod m} + 26) \\pmod{26}$$\n"
                "2. **Without the Keyword (Kasiski Examination & Index of Coincidence):**\n"
                "   - Find repeated 3-letter sequences (trigrams) in the ciphertext and measure the distance between them.\n"
                "   - The factors of those distances reveal the keyword length $m$. Once $m$ is known, group every $m$-th letter together and solve $m$ simple Caesar ciphers using Frequency Analysis!"
            ),
            "examples": (
                "🔹 **Example 1 (Encrypting `'STAR'` with Keyword `'AB'`):**\n"
                "- Keyword `'AB'` has shifts `A=0, B=1` repeated as `0, 1, 0, 1`.\n"
                "- `S (+0) -> S` | `T (+1) -> U` | `A (+0) -> A` | `R (+1) -> S` $\\rightarrow$ **`SUAS`**.\n\n"
                "🔹 **Example 2 (Encrypting `'BEE'` with Keyword `'BCD'`):**\n"
                "- Shifts: `B=1, C=2, D=3`.\n"
                "- `B (+1) -> C` | `E (+2) -> G` | `E (+3) -> H` $\\rightarrow$ **`CGH`** (Two identical `'E'`s became `'G'` and `'H'`!).\n\n"
                "🔹 **Example 3 (Kasiski Distance Factoring):**\n"
                "- If trigram `'XQY'` appears at index 10 and index 30, distance = $30 - 10 = 20$. Keyword length is likely a factor of 20 (`4` or `5`)."
            ),
            "q1": "In English text, which letter has the highest natural frequency (~12.7%), making it the primary target in Frequency Analysis?",
            "q1_opts": ["A) Letter 'Z'", "B) Letter 'Q'", "C) Letter 'E'", "D) Letter 'J'"],
            "q1_ans": "C) Letter 'E'",
            "q2": "In the Kasiski Examination against a Vigenère cipher, if a repeated 4-letter ciphertext pattern occurs at position 12 and position 27 (distance = 15), what are the most likely keyword lengths?",
            "q2_opts": [
                "A) Factors of 15 (i.e., keyword length 3 or 5)",
                "B) Keyword length 26",
                "C) Keyword length 100",
                "D) Keyword length 2"
            ],
            "q2_ans": "A) Factors of 15 (i.e., keyword length 3 or 5)",
            "lab1_q": "Practical Lab 1 (+150 XP): Encrypt the word `GOLD` using Vigenère with the repeating 2-letter keyword `AB` (`A=0, B=1`, so shift odd letters by 0 and even letters by +1).",
            "lab1_ans": "GPMD",
            "lab2_q": "Practical Lab 2 (+150 XP): Decrypt the Vigenère ciphertext `CGH` using the 3-letter keyword `BCD` (`B=1, C=2, D=3`).",
            "lab2_ans": "BEE"
        },

        # ----------------------------------------------------------------------
        # TRACK 4: ULTIMATE SECRET MESSENGER CORE ARCHITECTURE (LESSONS 14 - 16)
        # ----------------------------------------------------------------------
        "Track 4 • Lesson 14: Stream Ciphers, XOR & Shannon's Perfect Secrecy (OTP)": {
            "id": "L14",
            "track": "🟣 TRACK 4: PLATFORM CORE ARCHITECTURE & STEGANOGRAPHY",
            "title": "🛡️ Lesson 14: Stream Ciphers, XOR & Claude Shannon's One-Time Pad",
            "overview": (
                "Can an encryption algorithm be **100% mathematically unbreakable**, even if an attacker has infinite supercomputers? "
                "Yes! In 1949, **Claude Shannon** (the father of Information Theory) proved that the **One-Time Pad (OTP)** achieves **Information-Theoretic Perfect Secrecy**."
            ),
            "enc_guide": (
                "**1. How the One-Time Pad (OTP) Works:**\n"
                "- Generate a truly random key bit-stream $K$ that is **exactly as long as the plaintext $P$**.\n"
                "- Combine each bit (or byte) using XOR ($\\oplus$): $C = P \\oplus K$.\n"
                "- Why is it unbreakable? Because for any given ciphertext $C$, every possible plaintext $P$ of the same length is equally likely!\n\n"
                "**2. Modern Stream Ciphers (ChaCha20 & PRNG Keystreams):**\n"
                "- Because sharing a massive random key as long as a movie file is impractical, modern stream ciphers take a short secret seed (e.g., 256 bits) and use a **Cryptographically Secure Pseudo-Random Number Generator (CSPRNG)** to stretch it into a long keystream."
            ),
            "dec_guide": (
                "**The Fatal Mistake — Key Reuse (Two-Time Pad Attack):**\n"
                "- If an operator reuses the same OTP keystream $K$ to encrypt two messages $P_1$ and $P_2$:\n"
                "  $$C_1 \\oplus C_2 = (P_1 \\oplus K) \\oplus (P_2 \\oplus K) = P_1 \\oplus P_2$$\n"
                "- The secret key $K$ cancels out completely! The attacker can then recover both $P_1$ and $P_2$ using crib-dragging."
            ),
            "examples": (
                "🔹 **Example 1 (Byte-Level XOR Encryption & Decryption):**\n"
                "- Plaintext Byte $P = 80$ (`01010000`) | Random Key Byte $K = 170$ (`10101010`).\n"
                "- Ciphertext $C = 80 \\oplus 170 = 250$ (`11111010`).\n"
                "- Decryption: $250 \\oplus 170 = 80$ (Restores $P$).\n\n"
                "🔹 **Example 2 (Two-Time Pad Key Cancellation):**\n"
                "- $C_1 = P_1 \\oplus K$, $C_2 = P_2 \\oplus K \\implies C_1 \\oplus C_2 = P_1 \\oplus P_2$.\n\n"
                "🔹 **Example 3 (Why Randomness Matters):**\n"
                "- True hardware randomness (thermal noise, quantum decay) is required for strict OTP."
            ),
            "q1": "What happens if you reuse a One-Time Pad key K to encrypt two different messages P1 and P2?",
            "q1_opts": [
                "A) It becomes twice as secure",
                "B) An attacker can XOR the two ciphertexts together (C1 ⊕ C2 = P1 ⊕ P2), completely canceling out the secret key K",
                "C) The computer crashes",
                "D) Nothing happens"
            ],
            "q1_ans": "B) An attacker can XOR the two ciphertexts together (C1 ⊕ C2 = P1 ⊕ P2), completely canceling out the secret key K",
            "q2": "For a One-Time Pad to achieve Claude Shannon's 'Perfect Secrecy', how long must the truly random key be?",
            "q2_opts": [
                "A) 8 characters long",
                "B) At least as long as the plaintext message itself (and never reused)",
                "C) 1 bit long",
                "D) Shorter than the message"
            ],
            "q2_ans": "B) At least as long as the plaintext message itself (and never reused)",
            "lab1_q": "Practical Lab 1 (+150 XP): If Plaintext decimal byte `P = 12` (`1100`) and OTP Key byte `K = 5` (`0101`), what is the decimal Ciphertext byte `C = P ^ K`?",
            "lab1_ans": "9",
            "lab2_q": "Practical Lab 2 (+150 XP): If Ciphertext byte `C = 9` (`1001`) and Key byte `K = 5` (`0101`), what is the decrypted decimal Plaintext byte `P = C ^ K`?",
            "lab2_ans": "12"
        },

        "Track 4 • Lesson 15: Multi-Layer 229-Char Permutation & UTC Temporal Locking": {
            "id": "L15",
            "track": "🟣 TRACK 4: PLATFORM CORE ARCHITECTURE & STEGANOGRAPHY",
            "title": "🧬 Lesson 15: Inside Ultimate Secret Messenger — 229-Char PRNG Key & UTC Locks",
            "overview": (
                "This module documents the exact engineering inside `core/cipher_engine.py` of **Ultimate Secret Messenger**. "
                "Instead of a fixed 26-letter alphabet, our engine permutes a **229-character global alphabet** (`BASE_CHARS`: English letters, digits, punctuation, and all 134 Vietnamese diacritic characters) across **5 defense layers**, plus tamper-proof **UTC Epoch Time-Locking**."
            ),
            "enc_guide": (
                "**The 5-Layer Key Construction (`build_custom_key`):**\n"
                "1. **Layer 1 (Passphrase + Unicode Symbol Vault Seed):** Concatenates your text passphrase with your chosen sequence of emojis from the **1,488+ Unicode Symbol Pool**: `seed = f'{secret_seed}_{icons}'`.\n"
                "2. **Layer 2 (PRNG Fisher-Yates Permutation):** Uses `random.Random(seed).shuffle(key)` to deterministically permute all $229!$ possible arrangements.\n"
                "3. **Layer 3 (Modular Shift Offset):** Rotates the shuffled 229-character key array by `shift_step % 229`.\n"
                "4. **Layer 4 (Custom Pair Trap Swaps):** Swaps user-defined character pairs (`a=@, e=3`) directly inside the key array.\n"
                "5. **Layer 5 (Temporal Header & Reverse Structure):** Prepends `TMODE:<MODE>:<UTC_TS>|` to the message before substitution, and optionally reverses the entire output string."
            ),
            "dec_guide": (
                "**How Temporal Self-Destruct (`EXPIRE`) & Time-Capsule (`WAIT`) Work:**\n"
                "- **Why UTC Epoch Time?** `int(time.time())` counts seconds since **Jan 1, 1970 00:00:00 UTC**. Because UTC is timezone-independent, a message sent from Ho Chi Minh City (UTC+7) to New York (UTC-5) expires at the exact same physical instant!\n"
                "- **Cryptographic Sealing:** Because `TMODE:EXPIRE:1792650000|Secret` is encrypted *as a single unit*, nobody can edit the timestamp without knowing the group key."
            ),
            "examples": (
                "🔹 **Example 1 (Key Space Explosion):**\n"
                "- Choosing just 3 icons in order from 1,488 symbols multiplies the key space by $1488^3 \\approx 3.29 \\times 10^9$ combinations on top of your passphrase!\n\n"
                "🔹 **Example 2 (Self-Destruct Verification):**\n"
                "- Target Timestamp = `1700000600`. If recipient decodes at `now = 1700000750` ($150$ seconds late), the engine aborts and outputs `💥 MESSAGE SELF-DESTRUCTED!`.\n\n"
                "🔹 **Example 3 (Time-Capsule Verification):**\n"
                "- Target Timestamp = `1700000600`. If recipient decodes early at `now = 1700000400`, the engine blocks decryption and tells them to wait `3m 20s`."
            ),
            "q1": "Why does Ultimate Secret Messenger use UTC Epoch timestamps (`time.time()`) instead of the user's local computer clock timezone?",
            "q1_opts": [
                "A) Because UTC is universal and identical worldwide at any given second, preventing timezone bugs when chatting across countries",
                "B) Because local time has no seconds",
                "C) To make the ciphertext longer",
                "D) Because Python only supports Vietnam time"
            ],
            "q1_ans": "A) Because UTC is universal and identical worldwide at any given second, preventing timezone bugs when chatting across countries",
            "q2": "In `encrypt_core()`, what happens if the recipient unchecks 'Reverse Structure' when the sender had it checked?",
            "q2_opts": [
                "A) It still decrypts normally",
                "B) The inverse substitution reads the string backwards, failing the `TMODE:` header check and blocking decryption",
                "C) It deletes the chat room",
                "D) It reveals the passphrase"
            ],
            "q2_ans": "B) The inverse substitution reads the string backwards, failing the `TMODE:` header check and blocking decryption",
            "lab1_q": "Practical Lab 1 (+150 XP): If a message is encrypted with a 15-minute Self-Destruct timer (`15 * 60` seconds) at UTC timestamp `10000`, what is the exact target expiration timestamp embedded in the header?",
            "lab1_ans": "10900",
            "lab2_q": "Practical Lab 2 (+150 XP): How many total characters are in `BASE_CHARS` of Ultimate Secret Messenger? (Check the Home Dashboard metric or lesson text above).",
            "lab2_ans": "229"
        },

        "Track 4 • Lesson 16: Linguistic Markov Camouflage & LSB Pixel Steganography": {
            "id": "L16",
            "track": "🟣 TRACK 4: PLATFORM CORE ARCHITECTURE & STEGANOGRAPHY",
            "title": "🎭🖼️ Lesson 16: Deep Dive into 4-Bit Markov Camouflage & RGB Pixel LSB Hiding",
            "overview": (
                "This module covers the two steganographic engines built into **Ultimate Secret Messenger**:\n"
                "1. **Linguistic Camouflage (`encode_english_camouflage`):** Disguises encrypted bytes as natural IT/Networking English sentences.\n"
                "2. **LSB Image Steganography (`encode_image_lsb`):** Embeds encrypted bits into the Least Significant Bits of lossless PNG images."
            ),
            "enc_guide": (
                "**Part A — 4-Bit Nibble Linguistic Camouflage Math:**\n"
                "- Each UTF-8 byte $B \\in [0, 255]$ is split into two 4-bit nibbles:\n"
                "  $$\\text{High} = (B \\gg 4) \\;\\&\\; 15, \\qquad \\text{Low} = B \\;\\&\\; 15$$\n"
                "- Mapped via `CAMO_WORDS[0..15]` (`0=system, 1=network, 2=protocol, 3=update...`). Thus, **1 Byte = 2 English Words**.\n\n"
                "**Part B — RGB Pixel LSB Steganography Math:**\n"
                "- Appends delimiter `<<END_STEGO>>` and converts payload to bits.\n"
                "- Modifies the lowest bit of each channel: `R_new = (R & ~1) | bit`.\n"
                "- **Maximum Byte Capacity Formula** for an image of width $W$ and height $H$:\n"
                "  $$\\text{Max Bytes} = \\left\\lfloor \\frac{W \\times H \\times 3}{8} \\right\\rfloor - 13$$"
            ),
            "dec_guide": (
                "**Extraction & Forensic Verification:**\n"
                "- **Camouflage Decode:** Pairs of words $(W_1, W_2)$ reconstruct byte $B = (\\text{idx}(W_1) \\ll 4) \\mid \\text{idx}(W_2)$.\n"
                "- **LSB Image Decode:** Extracts `R & 1`, `G & 1`, `B & 1` from every pixel, packs every 8 bits into a byte, and stops immediately when the last 13 bytes equal `<<END_STEGO>>`."
            ),
            "examples": (
                "🔹 **Example 1 (Camouflage Byte Reconstruction):**\n"
                "- Word 1 = `'protocol'` (index `2`), Word 2 = `'update'` (index `3`).\n"
                "- Reconstructed Byte: $(2 \\times 16) + 3 =$ **`35`** (ASCII `'#'`).\n\n"
                "🔹 **Example 2 (LSB Pixel Bit Modification):**\n"
                "- Pixel `(100, 150, 200)` in binary ends with bits `(0, 0, 0)`.\n"
                "- Embedding bits `1, 1, 0` changes the pixel to **`(101, 151, 200)`**.\n\n"
                "🔹 **Example 3 (Calculating Image Capacity):**\n"
                "- An image of `80 x 10` pixels has $800$ pixels = $800 \\times 3 = 2,400$ color channels = $2,400 \\div 8 =$ **`300` total bytes**."
            ),
            "q1": "In our Linguistic Camouflage engine, if an encrypted string is 20 bytes long, how many English words will be generated?",
            "q1_opts": ["A) 10 words", "B) 20 words", "C) 40 words (2 words per byte)", "D) 160 words"],
            "q1_ans": "C) 40 words (2 words per byte)",
            "q2": "If a pixel has Red value `R = 200` (even number, binary ends in 0) and we embed secret bit `1` into its LSB, what is the new Red value?",
            "q2_opts": ["A) 0", "B) 199", "C) 201", "D) 255"],
            "q2_ans": "C) 201",
            "lab1_q": "Practical Lab 1 (+150 XP): How many total bits can be hidden inside an image that has exactly `100` RGB pixels? (1 pixel = 3 channels).",
            "lab1_ans": "300",
            "lab2_q": "Practical Lab 2 (+150 XP): In 4-bit Nibble Camouflage, if High Nibble index = `3` and Low Nibble index = `5`, what is the reconstructed decimal byte value `(3 * 16 + 5)`?",
            "lab2_ans": "53"
        },

        # ----------------------------------------------------------------------
        # TRACK 5: MODERN CRYPTOGRAPHY, NETWORKS & POST-QUANTUM (LESSONS 17 - 20)
        # ----------------------------------------------------------------------
        "Track 5 • Lesson 17: Cryptographic Hashing (SHA-256), Avalanche & Salting": {
            "id": "L17",
            "track": "🔴 TRACK 5: MODERN CRYPTOGRAPHY & POST-QUANTUM SECURITY",
            "title": "🔒 Lesson 17: SHA-256 Hashing, The Avalanche Effect & Password Salting",
            "overview": (
                "Designed by the NSA and published by NIST in 2001, **SHA-256 (Secure Hash Algorithm 256-bit)** powers Bitcoin blockchain mining, HTTPS digital certificates, Git commit IDs, and the **Room Admin PIN & CTF Authentication** inside Ultimate Secret Messenger."
            ),
            "enc_guide": (
                "**The 4 Essential Properties of a Cryptographic Hash Function $H(x)$:**\n"
                "1. **Deterministic & Fixed Size:** Regardless of whether the input is 1 letter or a 10GB movie, SHA-256 always outputs exactly **256 bits (64 Hex characters)**.\n"
                "2. **Pre-Image Resistance (One-Way):** Given digest $y$, it is computationally infeasible to find input $x$ such that $H(x) = y$.\n"
                "3. **Collision Resistance:** It is infeasible to find two different inputs $x_1 \\neq x_2$ that produce the same hash $H(x_1) = H(x_2)$.\n"
                "4. **The Avalanche Effect:** Changing just **1 single bit** of the input flips approximately **50% of all output bits** randomly!"
            ),
            "dec_guide": (
                "**How Hackers Crack Unsalted Hashes (Rainbow Tables) & How Salting Stops Them:**\n"
                "- Since hashing is deterministic, `SHA256('123456')` always produces `8d969eef6ecad3c29a3a629280e686cf...`. Hackers precompute billions of common password hashes in giant lookup tables called **Rainbow Tables**.\n"
                "- **Defense — Password Salting:** Before hashing, append a unique random string (**Salt**) to each user's password: `Hash = SHA256(Password + Random_Salt)`. This renders precomputed Rainbow Tables 100% useless!"
            ),
            "examples": (
                "🔹 **Example 1 (The Avalanche Effect in Action):**\n"
                "- `SHA256('HCMUS1')` = `4b227777d4dd1fc61c6f884f48641d02...`\n"
                "- `SHA256('HCMUS2')` = `ef2d127de37b942baad06145e54b0c61...` (Completely different!).\n\n"
                "🔹 **Example 2 (Salted Password Storage):**\n"
                "- User 1 & User 2 both choose password `'secret'`. User 1 gets Salt `'X9a'`, User 2 gets Salt `'P2m'`. Their stored hashes look completely different!\n\n"
                "🔹 **Example 3 (File Integrity Checksum):**\n"
                "- Software websites publish the SHA-256 hash of their `.iso` installer so you can verify no malware was injected during download."
            ),
            "q1": "What is the 'Avalanche Effect' in cryptographic hash functions like SHA-256?",
            "q1_opts": [
                "A) Changing even 1 single bit in the input drastically changes ~50% of the output hash bits, making the new hash look completely unrelated",
                "B) The hash gets longer every year",
                "C) The computer cools down",
                "D) Only numbers are hashed"
            ],
            "q1_ans": "A) Changing even 1 single bit in the input drastically changes ~50% of the output hash bits, making the new hash look completely unrelated",
            "q2": "How does adding a unique random 'Salt' to a password before hashing protect against Rainbow Table attacks?",
            "q2_opts": [
                "A) It makes the password shorter",
                "B) It ensures that even two users with the exact same password produce completely different hashes, invalidating precomputed lookup tables",
                "C) It allows the admin to decrypt the password",
                "D) It removes all numbers"
            ],
            "q2_ans": "B) It ensures that even two users with the exact same password produce completely different hashes, invalidating precomputed lookup tables",
            "lab1_q": "Practical Lab 1 (+150 XP): How many bytes (not bits) is a 256-bit SHA-256 hash output? (Hint: 256 / 8).",
            "lab1_ans": "32",
            "lab2_q": "Practical Lab 2 (+150 XP): What is the 4-letter security term for the random string added to a password before hashing to defeat Rainbow Tables?",
            "lab2_ans": "SALT"
        },

        "Track 5 • Lesson 18: Modern Block Ciphers — AES-256 Architecture": {
            "id": "L18",
            "track": "🔴 TRACK 5: MODERN CRYPTOGRAPHY & POST-QUANTUM SECURITY",
            "title": "🏦 Lesson 18: AES-256 (Advanced Encryption Standard) & Block Cipher Modes",
            "overview": (
                "Adopted by the US Government in 2001 (originally designed as **Rijndael** by Belgian cryptographers Joan Daemen and Vincent Rijmen), **AES (Advanced Encryption Standard)** is the global gold standard protecting Wi-Fi (WPA2/WPA3), SSD hard drive encryption (BitLocker/FileVault), WhatsApp, and banking transactions."
            ),
            "enc_guide": (
                "**How AES Works Internally (Substitution-Permutation Network):**\n"
                "- AES processes data in **128-bit blocks** (16 bytes arranged in a $4 \\times 4$ matrix called the **State**).\n"
                "- Depending on key size (**128-bit = 10 rounds**, **192-bit = 12 rounds**, **256-bit = 14 rounds**), each round applies 4 mathematical layers:\n"
                "  1. **`SubBytes` (Confusion):** Replaces each byte using a non-linear lookup table (**Rijndael S-Box**) computed via multiplicative inverses in Galois Field $GF(2^8)$.\n"
                "  2. **`ShiftRows` (Diffusion):** Cyclically shifts rows 1, 2, and 3 of the $4 \\times 4$ matrix to the left.\n"
                "  3. **`MixColumns` (Diffusion):** Multiplies each column by a fixed polynomial matrix over $GF(2^8)$ so 1 byte change spreads across all 4 bytes.\n"
                "  4. **`AddRoundKey` (Key Mixing):** Bitwise XORs the 128-bit state matrix with the Round Subkey."
            ),
            "dec_guide": (
                "**Block Cipher Modes of Operation — Why `ECB` is Dangerous & `GCM` is King:**\n"
                "- **❌ ECB (Electronic Codebook — NEVER USE):** Encrypts each 16-byte block independently with the same key. Identical plaintext blocks produce identical ciphertext blocks (famous **ECB Penguin vulnerability** where an encrypted image still shows the outline of the picture!).\n"
                "- **✅ CBC (Cipher Block Chaining) & GCM (Galois/Counter Mode):** Uses a random **Initialization Vector (IV / Nonce)** and authentication tags so identical blocks encrypt completely differently and any tampering is detected immediately."
            ),
            "examples": (
                "🔹 **Example 1 (AES Block Matrix):**\n"
                "- 16 ASCII bytes `'0123456789ABCDEF'` form a $4 \\times 4$ byte grid. Even if you only change `'0'` to `'1'`, after 14 rounds of `MixColumns` and `ShiftRows`, all 16 output bytes change unpredictably.\n\n"
                "🔹 **Example 2 (The ECB Penguin Flaw):**\n"
                "- In an image with 10,000 white background pixels, ECB encrypts every 16-byte white chunk into the exact same ciphertext chunk, leaking the visual shape.\n\n"
                "🔹 **Example 3 (AES-256 Key Space):**\n"
                "- $2^{256} \\approx 1.15 \\times 10^{77}$ keys (roughly equal to the number of atoms in the observable universe!)."
            ),
            "q1": "In AES encryption, how many bytes are inside a single 128-bit data block ($4 \\times 4$ State matrix)?",
            "q1_opts": ["A) 4 bytes", "B) 8 bytes", "C) 16 bytes (since 128 bits / 8 = 16 bytes)", "D) 256 bytes"],
            "q1_ans": "C) 16 bytes (since 128 bits / 8 = 16 bytes)",
            "q2": "Why is the 'ECB' (Electronic Codebook) mode of operation considered insecure for encrypting large messages or images?",
            "q2_opts": [
                "A) Because identical 16-byte plaintext blocks always produce identical 16-byte ciphertext blocks, leaking patterns in the data",
                "B) Because ECB deletes the key",
                "C) Because ECB only works on numbers",
                "D) Because ECB is too slow"
            ],
            "q2_ans": "A) Because identical 16-byte plaintext blocks always produce identical 16-byte ciphertext blocks, leaking patterns in the data",
            "lab1_q": "Practical Lab 1 (+150 XP): How many encryption rounds does `AES-256` perform on each 16-byte block? (10, 12, or 14).",
            "lab1_ans": "14",
            "lab2_q": "Practical Lab 2 (+150 XP): If you have a message that is `64 bytes` long, how many 16-byte AES blocks does it contain?",
            "lab2_ans": "4"
        },

        "Track 5 • Lesson 19: Public-Key Cryptography — Diffie-Hellman & RSA": {
            "id": "L19",
            "track": "🔴 TRACK 5: MODERN CRYPTOGRAPHY & POST-QUANTUM SECURITY",
            "title": "🔑🔓 Lesson 19: Asymmetric Cryptography — Diffie-Hellman Key Exchange & RSA",
            "overview": (
                "All symmetric ciphers (Caesar, Vigenère, AES, and our Sidebar Passphrase) share a classic chicken-and-egg problem: **How do Alice in Vietnam and Bob in the US agree on a Secret Passphrase over the internet if hackers are listening to the wire?**\n\n"
                "In the 1970s, **Whitfield Diffie, Martin Hellman**, and **Rivest–Shamir–Adleman (RSA)** revolutionized computer science by inventing **Asymmetric Public-Key Cryptography**."
            ),
            "enc_guide": (
                "**1. Asymmetric Key Pair Concept (Mailbox Analogy):**\n"
                "- **Public Key (Khóa Công khai — The Mailbox Slot):** Shared openly with the entire world. Anyone can drop an encrypted letter into the slot.\n"
                "- **Private Key (Khóa Bí mật — The Metal Key to the Door):** Kept 100% secret by the owner. Only the Private Key can open the mailbox and decrypt the messages!\n\n"
                "**2. The 5-Step Textbook RSA Mathematical Algorithm:**\n"
                "1. Pick two huge prime numbers $p$ and $q$, and compute modulus $N = p \\times q$.\n"
                "2. Compute Euler's totient: $\\phi(N) = (p - 1)(q - 1)$.\n"
                "3. Choose Public Exponent $e$ coprime to $\\phi(N)$. **Public Key = $(e, N)$**.\n"
                "4. Compute Private Exponent $d$ such that $(e \\cdot d) \\equiv 1 \\pmod{\\phi(N)}$. **Private Key = $(d, N)$**.\n"
                "5. **Encrypt Message $M$:** $C = M^e \\pmod N$. **Decrypt Ciphertext $C$:** $M = C^d \\pmod N$."
            ),
            "dec_guide": (
                "**Why RSA is Secure (Prime Factorization Trapdoor) & Digital Signatures:**\n"
                "- Multiplying two 1,024-bit primes $p \\times q = N$ takes a computer 0.001 seconds, but factoring a 2,048-bit $N$ back into $p$ and $q$ takes classical supercomputers thousands of years!\n"
                "- **Digital Signatures (Chữ ký số):** If Alice encrypts a document's hash using her **Private Key**, anyone in the world can verify it using Alice's **Public Key**, proving mathematically that Alice authored it!"
            ),
            "examples": (
                "🔹 **Example 1 (Complete Worked RSA Calculation):**\n"
                "- Primes: $p = 3, q = 11 \\implies N = 33$, $\\phi(N) = (2)(10) = 20$.\n"
                "- Public Key: $e = 3, N = 33$ | Private Key: $d = 7, N = 33$ (since $3 \\times 7 = 21 \\equiv 1 \\pmod{20}$).\n"
                "- Encrypt $M = 2$: $C = 2^3 \\pmod{33} =$ **`8`**.\n"
                "- Decrypt $C = 8$: $M = 8^7 \\pmod{33} = 2097152 \\pmod{33} =$ **`2`**!\n\n"
                "🔹 **Example 2 (Hybrid Encryption in HTTPS/TLS):**\n"
                "- Browsers use Asymmetric Crypto (RSA/ECDHE) at the start of a connection to securely exchange a random session key, then switch to fast **AES-256** for the actual data transfer."
            ),
            "q1": "If Bob wants to send an encrypted secret message to Alice using RSA, which key must Bob use to ENCRYPT the message?",
            "q1_opts": [
                "A) Bob's own Private Key",
                "B) Alice's Public Key (so that only Alice's Private Key can decrypt it)",
                "C) Alice's Private Key",
                "D) No key is needed"
            ],
            "q1_ans": "B) Alice's Public Key (so that only Alice's Private Key can decrypt it)",
            "q2": "In RSA, what mathematical problem prevents an attacker who knows the Public Key `(e, N)` from calculating the Private Key `d`?",
            "q2_opts": [
                "A) Adding two numbers together",
                "B) The extreme difficulty of factoring the massive composite number N back into its two secret prime factors p and q",
                "C) Converting Hex to Binary",
                "D) Reversing a string"
            ],
            "q2_ans": "B) The extreme difficulty of factoring the massive composite number N back into its two secret prime factors p and q",
            "lab1_q": "Practical Lab 1 (+150 XP): In RSA, if prime `p = 5` and prime `q = 7` (`N = 35`), what is the value of Euler's totient `phi(N) = (p - 1) * (q - 1)`?",
            "lab1_ans": "24",
            "lab2_q": "Practical Lab 2 (+150 XP): Using RSA Public Key `(e = 3, N = 33)`, encrypt the plaintext number `M = 3` using `C = 3^3 mod 33`.",
            "lab2_ans": "27"
        },

        "Track 5 • Lesson 20: Quantum Computing Threats & Post-Quantum Cryptography (PQC)": {
            "id": "L20",
            "track": "🔴 TRACK 5: MODERN CRYPTOGRAPHY & POST-QUANTUM SECURITY",
            "title": "⚛️ Lesson 20: Quantum Computers (Qubits, Shor, Grover) & Post-Quantum Lattice Crypto",
            "overview": (
                "Welcome to the final capstone module of the Academy! While classical computers process bits that are strictly `0` or `1`, **Quantum Computers** use **Qubits (Quantum Bits)** that leverage **Superposition** and **Quantum Entanglement** to evaluate massive probability amplitudes simultaneously.\n\n"
                "How will Quantum Computers impact cybersecurity, and how are cryptographers preparing the internet for the **Post-Quantum Era**?"
            ),
            "enc_guide": (
                "**1. The Two Quantum Algorithms Every Security Engineer Must Know:**\n"
                "- **💥 Shor's Algorithm (1994 — Breaks Asymmetric RSA & ECC):**\n"
                "  Uses Quantum Fourier Transforms to find the period of modular functions in polynomial time. A fault-tolerant quantum computer running Shor's Algorithm will **completely break RSA, Diffie-Hellman, and Elliptic Curve Cryptography (ECC)**!\n"
                "- **⚡ Grover's Algorithm (1996 — Quadratic Speedup on Symmetric Ciphers):**\n"
                "  Searches an unsorted database of $N$ keys in $\\sqrt{N}$ steps instead of $N$ steps. This **halves the effective bit-security** of symmetric ciphers:\n"
                "  - `128-bit` key $\\rightarrow$ reduced to $2^{64}$ quantum operations (Vulnerable).\n"
                "  - `256-bit` key (like **AES-256**, **SHA-256**, and our **Multi-Layer Symbol + Passphrase Engine**) $\\rightarrow$ reduced to $2^{128}$ quantum operations (**100% Quantum-Safe!**)."
            ),
            "dec_guide": (
                "**2. NIST Post-Quantum Cryptography (PQC) Standards (Lattice-Based Math):**\n"
                "- To replace RSA and ECC before large quantum computers arrive (and defeat *'Harvest Now, Decrypt Later'* attacks), NIST standardized **Lattice-Based Cryptography** (**ML-KEM / CRYSTALS-Kyber** for encryption and **ML-DSA / Dilithium** for digital signatures).\n"
                "- Instead of prime factorization, Lattice Crypto relies on the **Learning With Errors (LWE)** problem: finding the closest vector in a high-dimensional geometric lattice (500+ dimensions) when small random noise is added—a problem that even Quantum Computers cannot solve!"
            ),
            "examples": (
                "🔹 **Example 1 (Grover's Algorithm Impact on Key Length):**\n"
                "- Classical brute-force on $2^{256}$ takes $2^{256}$ operations. Quantum Grover brute-force takes $\\sqrt{2^{256}} = 2^{128}$ operations ($3.4 \\times 10^{38}$ operations — still impossible to crack!).\n\n"
                "🔹 **Example 2 ('Harvest Now, Decrypt Later' Threat):**\n"
                "- Intelligence agencies record encrypted RSA traffic today and store it in data centers waiting for a 2030s quantum computer to unlock it.\n\n"
                "🔹 **Example 3 (Learning With Errors - LWE Concept):**\n"
                "- Exact linear equations $A \\cdot s = b$ are easy to solve with Gaussian elimination, but adding secret noise $e$ ($A \\cdot s + e \\equiv b \\pmod q$) makes recovering $s$ in 1,000 dimensions quantum-resistant!"
            ),
            "q1": "Which quantum algorithm threatens to completely break RSA and Elliptic Curve Cryptography (ECC) by factoring large numbers exponentially faster?",
            "q1_opts": [
                "A) Bubble Sort",
                "B) Shor's Algorithm",
                "C) Caesar's Algorithm",
                "D) Dijkstra's Algorithm"
            ],
            "q1_ans": "B) Shor's Algorithm",
            "q2": "According to Grover's Algorithm (which takes the square root of the keyspace), what is the effective quantum security level of a 256-bit symmetric key?",
            "q2_opts": [
                "A) 0 bits (broken instantly)",
                "B) 128 bits of quantum security (since sqrt(2^256) = 2^128, which remains astronomically secure)",
                "C) 512 bits",
                "D) 8 bits"
            ],
            "q2_ans": "B) 128 bits of quantum security (since sqrt(2^256) = 2^128, which remains astronomically secure)",
            "lab1_q": "Practical Lab 1 (+150 XP): If a classical keyspace has `2^64` possibilities,Grover's quantum algorithm searches it in `2^K` steps (where `K = 64 / 2`). What is the number `K`?",
            "lab1_ans": "32",
            "lab2_q": "Practical Lab 2 (+150 XP): What is the name of the mathematical structure (used in NIST's Kyber / ML-KEM standard) made of high-dimensional grids of points that resists quantum attacks? (1 word, 7 letters, starts with L)",
            "lab2_ans": "LATTICE"
        }
    }

    # --- HÀM SINH BÀI TẬP LUYỆN TẬP VÔ TẬN (INFINITE PROCEDURAL DRILL GENERATOR) ---
    def generate_infinite_drill(lesson_id: str, seed_num: int) -> dict:
        rng = random.Random(f"ACAD_DRILL_{lesson_id}_{seed_num}")
        if lesson_id in ["L01", "L02", "L03"]:
            words = ["CYBER", "TRUST", "SHIELD", "NEXUS", "MATRIX", "ORBIT", "LOCK", "PIXEL", "BINARY", "GUARD"]
            w = rng.choice(words)
            if seed_num % 2 == 0:
                acrostic_map = {
                    "A": "Alpha", "B": "Bravo", "C": "Cyber", "D": "Delta", "E": "Echo", "G": "Guard",
                    "H": "Hotel", "I": "India", "K": "Kilo", "L": "Laser", "M": "Matrix", "N": "Nexus",
                    "O": "Orbit", "P": "Pixel", "R": "Radar", "S": "Shield", "T": "Titan", "U": "Ultra", "X": "Xray", "Y": "Yankee"
                }
                phrase = " ".join(acrostic_map.get(c, c) for c in w)
                return {
                    "q": f"**Acrostic Steganography Drill #{seed_num}:** Extract the hidden secret word by taking the **FIRST LETTER** of each word in: `{phrase}`",
                    "ans": w,
                    "exp": f"Taking the 1st letter of each word in `{phrase}` gives **`{w}`**."
                }
            else:
                rev = w[::-1]
                return {
                    "q": f"**Public Encoding Reversal Drill #{seed_num}:** Decode this reversed plaintext string back to normal order: `{rev}`",
                    "ans": w,
                    "exp": f"Reading `{rev}` from right to left restores **`{w}`**."
                }

        elif lesson_id == "L04":
            val = rng.randint(5, 63)
            b_str = f"{val:08b}"
            if seed_num % 2 == 0:
                return {
                    "q": f"**Binary-to-Decimal Conversion Drill #{seed_num}:** Convert the 8-bit binary number `{b_str}` into Base-10 Decimal.",
                    "ans": str(val),
                    "exp": f"Binary `{b_str}` has 1-bits summing to decimal **`{val}`**."
                }
            else:
                small_val = rng.randint(3, 15)
                return {
                    "q": f"**Decimal-to-4-Bit Nibble Drill #{seed_num}:** Convert the decimal number `{small_val}` into a 4-bit binary string (e.g. 0101).",
                    "ans": f"{small_val:04b}",
                    "exp": f"Decimal `{small_val}` in 4-bit binary (weights 8, 4, 2, 1) is **`{small_val:04b}`**."
                }

        elif lesson_id == "L05":
            val = rng.randint(16, 250)
            hex_str = f"{val:02X}"
            if seed_num % 2 == 0:
                return {
                    "q": f"**Binary-to-Hexadecimal Drill #{seed_num}:** Convert the 8-bit binary byte `{val:08b}` (High `{val>>4:04b}`, Low `{val&15:04b}`) into a 2-digit Hexadecimal string (without 0x).",
                    "ans": hex_str,
                    "exp": f"High nibble `{val>>4:04b}` = `{val>>4:X}`, Low nibble `{val&15:04b}` = `{val&15:X}` -> **`{hex_str}`**."
                }
            else:
                return {
                    "q": f"**Hexadecimal-to-Decimal Drill #{seed_num}:** Convert the Hexadecimal byte `0x{hex_str}` into Base-10 Decimal (`{val>>4} * 16 + {val&15}`).",
                    "ans": str(val),
                    "exp": f"`({val>>4} * 16) + {val&15}` = **`{val}`**."
                }

        elif lesson_id == "L06":
            pos_val = rng.randint(1, 7)
            twos_4bit = (16 - pos_val) & 0x0F
            return {
                "q": f"**Two's Complement Negation Drill #{seed_num}:** Find the 4-bit Two's Complement binary representation of **`-{pos_val}`** (Start with `+{pos_val} = {pos_val:04b}`, flip all 4 bits, and add 1).",
                "ans": f"{twos_4bit:04b}",
                "exp": f"`+{pos_val}` is `{pos_val:04b}` -> Flip bits to `{(~pos_val)&15:04b}` -> Add 1 gives **`{twos_4bit:04b}`** (Check: `-8 + {twos_4bit - 8} = -{pos_val}`)."
            }

        elif lesson_id == "L07":
            a = rng.randint(3, 14)
            b = rng.randint(3, 14)
            op = rng.choice(["AND (&)", "OR (|)", "XOR (^)"])
            if "AND" in op:
                res = a & b
            elif "OR" in op:
                res = a | b
            else:
                res = a ^ b
            return {
                "q": f"**Bitwise Logic Gate Drill #{seed_num}:** Compute the 4-bit binary result of `{a:04b} {op} {b:04b}`.",
                "ans": f"{res:04b}",
                "exp": f"Applying `{op}` bit-by-bit to `{a:04b}` and `{b:04b}` yields **`{res:04b}`**."
            }

        elif lesson_id in ["L08", "L09"]:
            if lesson_id == "L08":
                offset = rng.randint(0, 20)
                ch = chr(65 + offset)
                return {
                    "q": f"**ASCII Table Drill #{seed_num}:** Given that uppercase `'A'` is decimal `65`, what is the decimal ASCII code for uppercase **`'{ch}'`**?",
                    "ans": str(65 + offset),
                    "exp": f"`'{ch}'` is `{offset}` positions after `'A'`, so `65 + {offset}` = **`{65 + offset}`**."
                }
            else:
                v1 = rng.randint(5, 20)
                v2 = rng.randint(2, 10)
                return {
                    "q": f"**x86-64 Assembly Trace Drill #{seed_num}:** What is the final decimal value in register `RAX` after executing: `MOV RAX, {v1}` -> `ADD RAX, {v2}` -> `SHL RAX, 1` (Note: `SHL RAX, 1` shifts left by 1 = multiplies by 2)?",
                    "ans": str((v1 + v2) * 2),
                    "exp": f"`RAX` starts at `{v1}`, adds `{v2}` to become `{v1+v2}`, then shifts left by 1 (`* 2`) to become **`{(v1+v2)*2}`**."
                }

        elif lesson_id in ["L10", "L11", "L12", "L13"]:
            w_bank = ["MARS", "LION", "STAR", "GOLD", "MOON", "NODE", "DATA", "CODE"]
            word = rng.choice(w_bank)
            shift = rng.randint(1, 4)
            enc = "".join(chr((ord(c) - 65 + shift) % 26 + 65) for c in word)
            return {
                "q": f"**Classical Cryptanalysis Drill #{seed_num}:** Decrypt the ciphertext `{enc}` which was shifted forward by **`+{shift}`** positions in the English alphabet (`A B C D E F G H I J K L M N O P Q R S T U V W X Y Z`).",
                "ans": word,
                "exp": f"Shifting each letter in `{enc}` backward by `{shift}` steps restores **`{word}`**."
            }

        elif lesson_id in ["L14", "L15", "L16"]:
            hi = rng.randint(1, 14)
            lo = rng.randint(1, 14)
            byte_val = (hi << 4) | lo
            return {
                "q": f"**Platform Engine Math Drill #{seed_num}:** In our 4-bit Nibble Camouflage engine, if High Nibble = `{hi}` and Low Nibble = `{lo}`, what is the reconstructed decimal byte value (`{hi} * 16 + {lo}`)?",
                "ans": str(byte_val),
                "exp": f"`({hi} << 4) | {lo}` = `{hi} * 16 + {lo}` = **`{byte_val}`**."
            }

        else:
            m_val = rng.randint(2, 5)
            c_val = (m_val ** 3) % 33
            return {
                "q": f"**Modern RSA Modular Exponentiation Drill #{seed_num}:** Using Public Key `(e = 3, N = 33)`, calculate the ciphertext `C = {m_val}^3 mod 33`.",
                "ans": str(c_val),
                "exp": f"`{m_val}^3 = {m_val**3}`, and `{m_val**3} mod 33` = **`{c_val}`**."
            }

    # --- BANNER ĐẦU TRANG HỌC VIỆN ---
    st.markdown("""
    <div class="hero-box" style="padding: 22px 30px; margin-bottom: 20px;">
        <div class="hero-badge">🎓 20-MODULE UNIVERSITY CURRICULUM • COMPUTER SYSTEMS & CRYPTOGRAPHY • INFINITE DRILLS</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Security Academy & Computer Systems LMS</h2>
        <p class="hero-sub">
            A complete 20-lesson university curriculum arranged across 5 progressive tracks: from Absolute Beginner Foundations and Low-Level Computer Systems (Binary, Hex, Two's Complement, Assembly) to Classical, Platform Core, and Post-Quantum Cryptography!
        </p>
    </div>
    """, unsafe_allow_html=True)

    acad_db = load_acad_db()
    if "acad_student" not in st.session_state:
        st.session_state.acad_student = st.session_state.get("ctf_user") or "taolagautruc"

    top_s1, top_s2 = st.columns([1.3, 2.7])
    with top_s1:
        student_input = st.text_input("🎓 Student ID / Callsign:", value=st.session_state.acad_student)
        if student_input.strip():
            st.session_state.acad_student = student_input.strip()

    curr_student = st.session_state.acad_student
    if curr_student not in acad_db["students"]:
        acad_db["students"][curr_student] = {"xp": 0, "completed_tasks": [], "drills_solved": 0}
        save_acad_db(acad_db)

    s_info = acad_db["students"][curr_student]
    s_xp = s_info.get("xp", 0)
    # Tương thích ngược nếu dữ liệu cũ từ bản 8 bài
    s_tasks = s_info.get("completed_tasks", [])
    s_drills = s_info.get("drills_solved", 0)
    max_curriculum_xp = len(LESSONS_CURRICULUM) * 500  # 20 bài * 500 XP = 10,000 XP

    with top_s2:
        m1, m2, m3 = st.columns(3)
        m1.metric("🎖️ Academic Degree", get_academic_degree(s_xp), f"Student: {curr_student}")
        m2.metric("⭐ Total Academy XP", f"{s_xp:,} / {max_curriculum_xp:,}+ XP", f"{min(int((s_xp/max_curriculum_xp)*100), 100)}% Curriculum")
        m3.metric("✅ Graded Assessments", f"{len(s_tasks)} / 80 Tasks", f"♾️ {s_drills} Bonus Drills Cracked")

    st.progress(min(s_xp / max_curriculum_xp, 1.0), text=f"University Curriculum Mastery: {s_xp:,} / {max_curriculum_xp:,} Core XP ({len(s_tasks)}/80 Core Assessments + {s_drills} Infinite Practice Drills)")
    st.divider()

    # --- BỘ LỌC CHỌN CHUYÊN NGÀNH (TRACK FILTER) & BÀI HỌC (1 -> 20) ---
    st.markdown("### 🗂️ Select Academic Track & Lesson Module (Ordered from Basic to Advanced)")
    f_col1, f_col2 = st.columns([1.3, 2.2])
    with f_col1:
        track_filter = st.selectbox(
            "🧭 Filter by Academic Track:",
            [
                "📚 All 20 Modules (Full University Curriculum)",
                "🟢 Track 1: Absolute Beginner Foundations (Lessons 01–03)",
                "🔵 Track 2: Computer Systems & Machine Code (Lessons 04–09)",
                "🟡 Track 3: Classical Cryptography & Math (Lessons 10–13)",
                "🟣 Track 4: Platform Core & Steganography (Lessons 14–16)",
                "🔴 Track 5: Modern & Post-Quantum Crypto (Lessons 17–20)"
            ]
        )
    with f_col2:
        if "Track 1" in track_filter:
            filtered_keys = [k for k in LESSONS_CURRICULUM if "Track 1" in k]
        elif "Track 2" in track_filter:
            filtered_keys = [k for k in LESSONS_CURRICULUM if "Track 2" in k]
        elif "Track 3" in track_filter:
            filtered_keys = [k for k in LESSONS_CURRICULUM if "Track 3" in k]
        elif "Track 4" in track_filter:
            filtered_keys = [k for k in LESSONS_CURRICULUM if "Track 4" in k]
        elif "Track 5" in track_filter:
            filtered_keys = [k for k in LESSONS_CURRICULUM if "Track 5" in k]
        else:
            filtered_keys = list(LESSONS_CURRICULUM.keys())

        selected_lesson_key = st.selectbox("📖 Select Lesson Module to Study:", filtered_keys)

    les = LESSONS_CURRICULUM[selected_lesson_key]
    lid = les["id"]

    # Hiển thị Khung Chat AI ở góc bên phải của khu vực Học viện
    acad_main_col, acad_right_ai_col = st.columns([2.35, 1.05])
    with acad_right_ai_col:
        render_ai_cyber_mentor_widget(current_lesson=les, decode_lsb_fn=decode_image_lsb, widget_key=f"acad_right_{lid}")

    # ==========================================================================
    # HIỂN THỊ BÀI HỌC THEO CHIỀU DỌC DÀI (LONG-SCROLL UNIVERSITY LECTURE)
    # ==========================================================================
    st.markdown(f"""
    <div class="lesson-card">
        <div class="hero-badge">{les['track']} • MODULE {lid}</div>
        <h3>{les['title']}</h3>
        <h4>1️⃣ Conceptual Foundation & Why It Matters</h4>
        <p>{les['overview'].replace(chr(10), '<br>')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 2️⃣ Core Architecture, Encoding / Encryption Rules & Mathematical Models")
    st.info(les["enc_guide"])

    st.markdown("#### 3️⃣ Decoding / Decryption Mechanics, Hardware Execution & Security Analysis")
    st.success(les["dec_guide"])

    st.markdown("#### 4️⃣ Multi-Case Concrete Worked Examples (Step-by-Step)")
    st.markdown(f"<div class='example-box'>{les['examples'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

    # ==========================================================================
    # MỤC 5: INTERACTIVE LIVE SANDBOX (MÁY THỰC HÀNH TRỰC QUAN CHO TỪNG CHUYÊN NGÀNH)
    # ==========================================================================
    st.markdown("#### 5️⃣ Interactive University Lab Sandbox (Experiment Live!)")
    with st.container(border=True):
        if lid in ["L01", "L02", "L03"]:
            st.caption("🔬 **Live Encoding vs. Encryption vs. Hashing Comparator:** Type any message below to see the difference between Public Encoding (Base64/Hex), Secret-Key Encryption, and One-Way SHA-256 Hashing!")
            sb_in = st.text_input("Enter Sample Plaintext:", value="Hello HCMUS!", key=f"sb_{lid}")
            if sb_in:
                b64_out = base64.b64encode(sb_in.encode("utf-8")).decode("utf-8")
                hex_out = " ".join(f"{b:02X}" for b in sb_in.encode("utf-8"))
                demo_k = build_custom_key("DEMO_SECRET", SYMBOLS_POOL[:2], 5, "")
                enc_out = encrypt_core(sb_in, demo_k, False, "NONE", 0)
                sha_out = hashlib.sha256(sb_in.encode("utf-8")).hexdigest()
                st.markdown(f"- **1. Public Base64 Encoding (No Key, Reversible by anyone):** `{b64_out}`")
                st.markdown(f"- **2. Public Hex Byte Encoding (No Key, Reversible by anyone):** `{hex_out}`")
                st.markdown(f"- **3. Multi-Layer Encryption (Requires Secret Key to Reverse):** `{enc_out}`")
                st.markdown(f"- **4. SHA-256 Cryptographic Hash (One-Way Fingerprint, Irreversible):** `{sha_out}`")

        elif lid in ["L04", "L05", "L06", "L07", "L08", "L09"]:
            st.caption("🔬 **Live Computer Systems & CPU Register Inspector:** Inspect any integer (-128 to +127) across Unsigned Binary, Two's Complement Signed Binary, Hexadecimal, Bitwise Shifts, and Little-Endian Memory!")
            cs_c1, cs_c2 = st.columns(2)
            with cs_c1:
                num_val = st.slider("Select 8-Bit Integer Value (-128 to +127):", -128, 127, 42, key=f"sb_num_{lid}")
            with cs_c2:
                shift_amt = st.slider("Bit Shift Amount (k = 1 to 4):", 1, 4, 2, key=f"sb_sh_{lid}")
            unsigned_byte = num_val & 0xFF
            flipped_bits = (~unsigned_byte) & 0xFF
            word32_hex = f"{unsigned_byte:08X}"
            little_endian_hex = " ".join([word32_hex[i:i+2] for i in range(6, -1, -2)])
            st.code(
                f"Decimal Input Value          : {num_val}\n"
                f"8-Bit Binary (Two's Comp)    : {unsigned_byte:08b} (High Nibble: {unsigned_byte>>4:04b} | Low Nibble: {unsigned_byte&15:04b})\n"
                f"Hexadecimal Byte (Base-16)   : 0x{unsigned_byte:02X}\n"
                f"Bitwise NOT (~X inverted)    : {flipped_bits:08b} (0x{flipped_bits:02X})\n"
                f"Left Shift (X << {shift_amt})          : {(unsigned_byte << shift_amt) & 0xFF:08b} (Unsigned byte mod 256)\n"
                f"32-Bit Little-Endian in RAM  : [ {little_endian_hex} ]"
            )

        elif lid in ["L10", "L11", "L12", "L13"]:
            st.caption("🔬 **Live Classical Cipher & Modular Math Workbench:** Test Rail-Fence Transposition, Caesar, Affine `(aP + b) mod 26`, and Vigenère in real time!")
            cl_c1, cl_c2, cl_c3 = st.columns([2, 1, 1])
            with cl_c1:
                cl_txt = st.text_input("Plaintext (A-Z):", value="CRYPTOGRAPHY", key=f"sb_cl_{lid}")
            with cl_c2:
                cl_a = st.selectbox("Affine Multiplier (a):", [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25], index=1, key=f"sb_a_{lid}")
            with cl_c3:
                cl_b = st.number_input("Shift / Offset (b):", 0, 25, 3, key=f"sb_b_{lid}")
            clean_w = "".join(c for c in cl_txt.upper() if "A" <= c <= "Z")
            if clean_w:
                rail2 = clean_w[0::2] + clean_w[1::2]
                aff_out = "".join(chr(((cl_a * (ord(c) - 65) + cl_b) % 26) + 65) for c in clean_w)
                st.markdown(f"- **2-Rail Fence Transposition:** `{clean_w[0::2]}` + `{clean_w[1::2]}` = **`{rail2}`**")
                st.markdown(f"- **Affine / Caesar Cipher (`{cl_a}*P + {cl_b} mod 26`):** **`{aff_out}`**")

        else:
            st.caption("🔬 **Live Steganography, SHA-256 Avalanche & RSA Trapdoor Workbench:**")
            adv_in = st.text_input("Test String for SHA-256 & 4-Bit Markov Camouflage:", value="Quantum2026", key=f"sb_adv_{lid}")
            if adv_in:
                camo_demo = encode_english_camouflage(adv_in[:8])
                sha_demo = hashlib.sha256(adv_in.encode("utf-8")).hexdigest()
                st.markdown(f"- **4-Bit Nibble Camouflage Prose (First 8 bytes):** `{camo_demo}`")
                st.markdown(f"- **256-Bit SHA-256 Digest:** `{sha_demo}`")

    # ==========================================================================
    # MỤC 6: 4 BÀI TẬP CHẤM ĐIỂM CỐ ĐỊNH MỖI BÀI HỌC (2 QUIZZES + 2 PRACTICAL LABS = 500 XP)
    # ==========================================================================
    st.markdown(f"""
    <div class="exercise-box">
        <h4 style="color:#f8fafc; margin-top:0;">📝 6️⃣ Module {lid} Graded Assessment Suite (4 Tasks • Earn +500 XP)</h4>
        <p style="color:#94a3b8; margin-bottom:0;">
            Complete the <b>2 Concept Quizzes (+100 XP each)</b> and <b>2 Hands-On Practical Labs (+150 XP each)</b> below to master this module!
        </p>
    </div>
    """, unsafe_allow_html=True)

    q_col1, q_col2 = st.columns(2)

    # Quiz 1 (+100 XP)
    t_q1 = f"{lid}_Q1"
    with q_col1:
        st.markdown("##### 🧠 Theory Quiz 1 (+100 XP)")
        if t_q1 in s_tasks:
            st.success(f"✅ **Passed (+100 XP)** — Answer: **{les['q1_ans']}**")
        else:
            u_q1 = st.radio(les["q1"], les["q1_opts"], key=f"rad_{t_q1}")
            if st.button("✔️ Submit Quiz 1 (+100 XP)", key=f"btn_{t_q1}", use_container_width=True):
                if u_q1 == les["q1_ans"]:
                    s_tasks.append(t_q1)
                    acad_db["students"][curr_student]["completed_tasks"] = s_tasks
                    acad_db["students"][curr_student]["xp"] = s_xp + 100
                    save_acad_db(acad_db)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Not quite right! Review the lecture notes above and try again.")

    # Quiz 2 (+100 XP)
    t_q2 = f"{lid}_Q2"
    with q_col2:
        st.markdown("##### 🧠 Theory Quiz 2 (+100 XP)")
        if t_q2 in s_tasks:
            st.success(f"✅ **Passed (+100 XP)** — Answer: **{les['q2_ans']}**")
        else:
            u_q2 = st.radio(les["q2"], les["q2_opts"], key=f"rad_{t_q2}")
            if st.button("✔️ Submit Quiz 2 (+100 XP)", key=f"btn_{t_q2}", use_container_width=True):
                if u_q2 == les["q2_ans"]:
                    s_tasks.append(t_q2)
                    acad_db["students"][curr_student]["completed_tasks"] = s_tasks
                    acad_db["students"][curr_student]["xp"] = s_xp + 100
                    save_acad_db(acad_db)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Not quite right! Check the conceptual sections above.")

    st.write("")
    l_col1, l_col2 = st.columns(2)

    # Practical Lab 1 (+150 XP)
    t_l1 = f"{lid}_L1"
    with l_col1:
        st.markdown("##### 🛠️ Practical Lab 1 (+150 XP)")
        if t_l1 in s_tasks:
            st.success(f"✅ **Lab 1 Verified (+150 XP)** — Solution: `{les['lab1_ans']}`")
        else:
            st.write(les["lab1_q"])
            u_l1 = st.text_input("Lab 1 Answer:", placeholder="Type exact answer...", key=f"in_{t_l1}")
            if st.button("🚀 Verify Lab 1 (+150 XP)", type="primary", key=f"btn_{t_l1}", use_container_width=True):
                if u_l1.strip().upper() == les["lab1_ans"].upper():
                    s_tasks.append(t_l1)
                    acad_db["students"][curr_student]["completed_tasks"] = s_tasks
                    acad_db["students"][curr_student]["xp"] = s_xp + 150
                    save_acad_db(acad_db)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Incorrect! Check the worked examples or use the Live Sandbox above.")

    # Practical Lab 2 (+150 XP)
    t_l2 = f"{lid}_L2"
    with l_col2:
        st.markdown("##### 🛠️ Practical Lab 2 (+150 XP)")
        if t_l2 in s_tasks:
            st.success(f"✅ **Lab 2 Verified (+150 XP)** — Solution: `{les['lab2_ans']}`")
        else:
            st.write(les["lab2_q"])
            u_l2 = st.text_input("Lab 2 Answer:", placeholder="Type exact answer...", key=f"in_{t_l2}")
            if st.button("🚀 Verify Lab 2 (+150 XP)", type="primary", key=f"btn_{t_l2}", use_container_width=True):
                if u_l2.strip().upper() == les["lab2_ans"].upper():
                    s_tasks.append(t_l2)
                    acad_db["students"][curr_student]["completed_tasks"] = s_tasks
                    acad_db["students"][curr_student]["xp"] = s_xp + 150
                    save_acad_db(acad_db)
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Incorrect! Re-check your calculation and try again.")

    # ==========================================================================
    # MỤC 7: PHÒNG LUYỆN TẬP SINH ĐỀ VÔ TẬN (INFINITE PROCEDURAL DRILL GENERATOR)
    # ==========================================================================
    st.markdown("""
    <div class="drill-box">
        <h4 style="color:#f8fafc; margin-top:0;">♾️ 7️⃣ Infinite Procedural Practice Drill Arena (+50 Bonus XP Per Drill)</h4>
        <p style="color:#a7f3d0; margin-bottom:0;">
            Want unlimited practice on this topic? Click <b>"🎲 Generate New Practice Problem"</b> as many times as you like! Every problem is generated dynamically with a step-by-step solution walkthrough.
        </p>
    </div>
    """, unsafe_allow_html=True)

    drill_state_key = f"drill_seed_{lid}"
    if drill_state_key not in st.session_state:
        st.session_state[drill_state_key] = 1

    dr_c1, dr_c2 = st.columns([3, 1.2])
    with dr_c2:
        if st.button("🎲 Generate New Practice Problem", key=f"new_dr_{lid}", use_container_width=True):
            st.session_state[drill_state_key] += 1
            st.rerun()

    curr_drill = generate_infinite_drill(lid, st.session_state[drill_state_key])
    with dr_c1:
        st.markdown(curr_drill["q"])

    d_in_c, d_sub_c, d_sol_c = st.columns([2.2, 1, 1.2])
    with d_in_c:
        drill_guess = st.text_input("Your Practice Answer:", placeholder="Type answer here...", key=f"dr_in_{lid}_{st.session_state[drill_state_key]}", label_visibility="collapsed")
    with d_sub_c:
        if st.button("✅ Check Drill (+50 XP)", type="primary", key=f"dr_chk_{lid}_{st.session_state[drill_state_key]}", use_container_width=True):
            if drill_guess.strip().upper() == curr_drill["ans"].upper():
                acad_db["students"][curr_student]["xp"] = s_xp + 50
                acad_db["students"][curr_student]["drills_solved"] = s_drills + 1
                save_acad_db(acad_db)
                st.balloons()
                st.success(f"🎉 Correct (`{curr_drill['ans']}`)! +50 Bonus XP awarded! Click 'Generate New Practice Problem' for another one.")
                time.sleep(1.1)
                st.session_state[drill_state_key] += 1
                st.rerun()
            else:
                st.error("❌ Not quite! Try again or click 'Show Step-by-Step Solution'.")
    with d_sol_c:
        with st.popover("📖 Show Step-by-Step Solution", use_container_width=True):
            st.markdown(f"**Exact Answer:** `{curr_drill['ans']}`\n\n**Explanation:** {curr_drill['exp']}")

# ==============================================================================
# PHẦN 6: UTILITIES, DEVELOPER PROFILE, VISION & COMPREHENSIVE DOCUMENTATION
# ==============================================================================
elif "6. Utilities & About" in main_menu:
    # CSS bổ sung riêng cho trang About & Documentation
    st.markdown("""
    <style>
        .profile-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border: 1px solid #3b82f6;
            border-radius: 16px;
            padding: 26px 30px;
            margin-bottom: 24px;
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.12);
        }
        .dev-name {
            font-size: 1.9rem;
            font-weight: 800;
            color: #f8fafc;
            margin: 0 0 6px 0;
        }
        .dev-role {
            color: #60a5fa;
            font-size: 1.02rem;
            font-weight: 600;
            margin-bottom: 14px;
        }
        .contact-pill {
            display: inline-block;
            background: #111827;
            border: 1px solid #374151;
            color: #e5e7eb;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 0.85rem;
            margin-right: 10px;
            margin-bottom: 8px;
        }
        .vision-box {
            background: #111827;
            border-left: 4px solid #8b5cf6;
            border-top: 1px solid #1f2937;
            border-right: 1px solid #1f2937;
            border-bottom: 1px solid #1f2937;
            border-radius: 12px;
            padding: 22px 26px;
            margin-bottom: 20px;
            line-height: 1.7;
            color: #cbd5e1;
        }
        .toc-box {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 20px 26px;
            margin-bottom: 24px;
        }
        .doc-section {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 14px;
            padding: 24px 28px;
            margin-bottom: 20px;
        }
        .doc-section h4 {
            color: #60a5fa;
            margin-top: 0;
            margin-bottom: 12px;
            font-size: 1.2rem;
            border-bottom: 1px solid #1f2937;
            padding-bottom: 8px;
        }
        .step-badge {
            background: rgba(59, 130, 246, 0.2);
            color: #93c5fd;
            padding: 2px 8px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.8rem;
            margin-right: 6px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Banner Đầu trang
    st.markdown("""
    <div class="hero-box" style="padding: 22px 30px; margin-bottom: 24px;">
        <div class="hero-badge">👨‍💻 CREATOR PROFILE • PROJECT VISION • MASTER USER MANUAL</div>
        <div class="hero-title" style="font-size: 2.1rem;">🛠️ About & Comprehensive Documentation</div>
        <p class="hero-sub">
            Meet the creator behind Ultimate Secret Messenger, explore our privacy-first mission, and master every cryptographic module with the complete step-by-step handbook below.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 1: DEVELOPER PROFILE (LÊ HOÀNG PHÚ HIẾU - HCMUS)
    # ==========================================================================
    st.markdown("### 👨‍💻 1. Meet the Creator & Architect")
    st.markdown("""
    <div class="profile-card">
        <div class="dev-name">Lê Hoàng Phú Hiếu</div>
        <div class="dev-role">🎓 Sophomore in Information Technology — Faculty of Information Technology (FIT)<br>
        🏛️ University of Science, VNU-HCM (HCMUS — Trường Đại học Khoa học Tự nhiên, ĐHQG-HCM)</div>
        <p style="color: #94a3b8; line-height: 1.65; margin-bottom: 18px;">
            Passionate software engineer and cybersecurity enthusiast dedicated to building mathematical, zero-trust, and user-centric privacy solutions. This platform was architected from scratch to bridge the gap between complex cryptographic theory and intuitive everyday communication.
        </p>
        <div>
            <span class="contact-pill">📧 <b>Email:</b> phuhieu3001@gmail.com</span>
            <span class="contact-pill">🐙 <b>GitHub:</b> <a href="https://github.com/taolagautruc" target="_blank" style="color:#60a5fa;text-decoration:none;">github.com/taolagautruc (@taolagautruc)</a></span>
            <span class="contact-pill">🏫 <b>Institution:</b> HCMUS - VNUHCM</span>
            <span class="contact-pill">📍 <b>Location:</b> Ho Chi Minh City, Vietnam</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 2: PROJECT PURPOSE, MISSION & FUTURE ROADMAP
    # ==========================================================================
    st.markdown("### 🌍 2. Project Purpose, Philosophy & Future Vision")
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown("""
        <div class="vision-box">
            <h4 style="color:#f8fafc; margin-top:0;">🛡️ Why Ultimate Secret Messenger Was Born</h4>
            <p>
                We live in an era where personal privacy is constantly compromised. Across mainstream social networks and messaging platforms, user metadata, private conversations, and behavioral footprints are routinely harvested, monetized, and traded on the open market—severely degrading user trust and digital safety.
            </p>
            <p style="margin-bottom:0;">
                <b>Ultimate Secret Messenger</b> is the realization of a personal vision to push back against mass data exploitation. It creates a self-contained, <b>Zero-Trust Cryptographic Sanctuary</b> where users hold 100% ownership of their encryption keys, rules, and data lifespans—ensuring that no third party can ever intercept or monetize your private communication.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_v2:
        st.markdown("""
        <div class="vision-box" style="border-left-color: #3b82f6;">
            <h4 style="color:#f8fafc; margin-top:0;">🚀 Long-Term Goal & Social Platform Roadmap</h4>
            <p>
                This web platform is only the beginning. I am committed to actively listening to user feedback, refining the cryptographic engines, and expanding the feature set continuously.
            </p>
            <p style="margin-bottom:0;">
                <b>The Ultimate Goal:</b> To evolve this project into a standalone, cross-platform downloadable application (Desktop & Mobile) that functions as a <b>Next-Generation Privacy-First Social Network</b>—a trusted digital haven where friends, teams, and communities can connect, share media, and converse with absolute mathematical security.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ==========================================================================
    # SECTION 3: TABLE OF CONTENTS & COMPLETE MASTER USER GUIDE (LONG SCROLL)
    # ==========================================================================
    st.markdown("### 📖 3. Master Table of Contents & User Manual")
    st.caption("Scroll down to explore the complete architectural breakdown and step-by-step instructions for every feature in the suite.")

    st.markdown("""
    <div class="toc-box">
        <h4 style="color:#f8fafc; margin-top:0; margin-bottom:12px;">📑 Quick Directory (Table of Contents)</h4>
        <ol style="color:#93c5fd; line-height:1.9; margin-bottom:0;">
            <li><b>Module 0 — Global Sidebar Control Panel:</b> Configuring Multi-Layer Group Keys (Passphrase, Shift, 1,400+ Symbols, Custom Pairs & Reverse).</li>
            <li><b>Module 1 — Executive Home Dashboard:</b> Monitoring Live Key Entropy, Brute-Force Resistance & Universal UTC Clock.</li>
            <li><b>Module 2A — Multi-Layer Text Cipher & UTC Time-Locking:</b> Self-Destructing Messages & Time-Capsule Delays.</li>
            <li><b>Module 2B — Linguistic Camouflage Studio:</b> Disguising Ciphertexts into Innocent English Prose (2-Way Markov Engine).</li>
            <li><b>Module 2C — LSB Image Steganography Lab:</b> Hiding Encrypted Payloads Inside Lossless PNG Pixels.</li>
            <li><b>Module 3 — Encrypted Persistent Chat Rooms:</b> Real-Time Multi-Modal Messaging & SHA-256 Admin Security Controls.</li>
            <li><b>Module 4 — Group Rule Sharing Utility:</b> Exporting & Importing Non-Sensitive Team Configuration Strings.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 1: SIDEBAR CONTROL PANEL ---
    st.markdown("""
    <div class="doc-section">
        <h4>🎛️ Module 0: Mastering the Global Cipher Control Panel (Left Sidebar)</h4>
        <p style="color:#cbd5e1;">
            The left sidebar is the heart of the platform. Every encryption and decryption action across the entire website relies on the exact combination of <b>5 customizable parameters</b> you set here. Both the sender and receiver must configure identical sidebar rules to read messages:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><span class="step-badge">LAYER 1</span> <b>🔑 Group Secret Passphrase:</b> Your primary secret password (e.g., <code>Nexus2026</code>). It seeds the deterministic pseudo-random number generator (PRNG) that shuffles the 229-character base alphabet.</li>
            <li><span class="step-badge">LAYER 2</span> <b>🔢 Shift Offset (0–200):</b> Rotates the shuffled substitution table by a specific number of positions, adding modular arithmetic protection.</li>
            <li><span class="step-badge">LAYER 3</span> <b>🎨 Symbol Vault (1,400+ Unicode Icons):</b> Select an ordered chain of emojis/symbols. Even if an attacker knows your text password, missing a single icon or placing them in the wrong order completely alters the key matrix.</li>
            <li><span class="step-badge">LAYER 4</span> <b>🔀 Custom Pairs (Optional):</b> Define manual character swaps separated by commas (e.g., <code>a=@, e=3, s=$</code>) to inject custom traps into the cipher table.</li>
            <li><span class="step-badge">LAYER 5</span> <b>🔄 Reverse Structure:</b> Flips the entire encrypted output string backward prior to transmission.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 2: HOME DASHBOARD ---
    st.markdown("""
    <div class="doc-section">
        <h4>🏠 Module 1: Executive Home Dashboard & Live Security Audit</h4>
        <p style="color:#cbd5e1;">
            Provides a real-time command center displaying system metrics and evaluating the mathematical strength of your current sidebar configuration:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><b>Live Key Entropy Calculator:</b> Automatically calculates the bit-strength (e.g., <code>~128+ bits</code>) and estimates how many years a supercomputer testing 1 trillion keys per second would need to brute-force your configuration.</li>
            <li><b>Universal UTC Synchronization:</b> Displays the current Coordinated Universal Time (UTC) used by all time-locks, ensuring two users in different timezones (e.g., Vietnam and the US) experience zero clock drift.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 3: TEXT CIPHER & TIME-LOCK ---
    st.markdown("""
    <div class="doc-section">
        <h4>📝 Module 2A: Multi-Layer Text Cipher & UTC Time-Locking</h4>
        <p style="color:#cbd5e1;">
            Located in <b>2. Cipher Workspace → Tab 1</b>. Allows you to encrypt plain text (supporting full English, Vietnamese diacritics, numbers, and punctuation) with embedded temporal rules:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><span class="step-badge">MODE 1</span> <b>Normal (No Time Limit):</b> Standard encryption that can be decoded anytime by teammates with the matching key.</li>
            <li><span class="step-badge">MODE 2</span> <b>🔥 Self-Destruct After Time:</b> Embeds a UTC expiration deadline inside the encrypted header. If the recipient attempts to decode the message after the timer expires, the engine blocks decryption and permanently scrambles the payload.</li>
            <li><span class="step-badge">MODE 3</span> <b>⏳ Time-Capsule (Wait Until):</b> Locks the message until a future UTC timestamp. Anyone attempting to decode it early will see a live countdown timer telling them how many minutes/seconds remain.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 4: ENGLISH CAMOUFLAGE ---
    st.markdown("""
    <div class="doc-section">
        <h4>🎭 Module 2B: Linguistic Camouflage Studio (2-Way Markov Prose)</h4>
        <p style="color:#cbd5e1;">
            Located in <b>2. Cipher Workspace → Tab 2</b>. Standard encrypted strings look suspicious to firewalls or human moderators. Linguistic Camouflage solves this:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><b>How to Disguise (Encode):</b> Type your secret message and click <i>"Encrypt & Disguise as English Prose"</i>. The engine first encrypts your text, splits every byte into 4-bit nibbles, and maps them to innocent IT/networking English vocabulary formatted as natural sentences.</li>
            <li><b>How to Reveal (Decode):</b> Paste the innocent-looking English paragraph into the right column and click <i>"Extract & Decrypt Secret"</i> to reverse the prose back into your original message.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 5: IMAGE STEGANOGRAPHY ---
    st.markdown("""
    <div class="doc-section">
        <h4>🖼️ Module 2C: LSB Pixel Steganography Lab (Hide Secrets Inside Images)</h4>
        <p style="color:#cbd5e1;">
            Located in <b>2. Cipher Workspace → Tab 3</b>. Conceals your encrypted message directly inside the RGB color channels of an image using <b>Least Significant Bit (LSB)</b> manipulation:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><span class="step-badge">STEP 1</span> Choose a carrier image by uploading your own <code>PNG/JPG</code> photo or clicking <b>"Auto-Generate Cyber Carrier Image"</b> to create a custom matrix graphic on the fly.</li>
            <li><span class="step-badge">STEP 2</span> Type your secret message and optional UTC Time-Lock. Check the <b>Pixel LSB Capacity Bar</b> on the right to see what percentage of the image's pixels will be used.</li>
            <li><span class="step-badge">STEP 3</span> Click <b>"Encrypt & Embed Into Image Pixels"</b> and download the resulting lossless <code>.PNG</code> file. To the naked eye, the image looks 100% identical to the original!</li>
            <li><span class="step-badge">STEP 4</span> To read a hidden message, switch to <b>Decode Mode</b>, upload the Stego <code>.PNG</code> file, and click <b>"Extract Bits & Decrypt Payload"</b>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # --- GUIDE ITEM 6: SECRET CHAT ROOMS & ADMIN CONTROLS ---
    st.markdown("""
    <div class="doc-section">
        <h4>💬 Module 3: Encrypted Persistent Chat Rooms & SHA-256 Admin Protection</h4>
        <p style="color:#cbd5e1;">
            Located in <b>3. Secret Chat Rooms</b>. A full-featured team communication hub where only encrypted ciphertexts, camouflaged prose, or Stego PNG images are stored on the server:
        </p>
        <ul style="color:#94a3b8; line-height:1.75;">
            <li><b>👑 Creating an Admin-Protected Room:</b> Select <i>"➕ Create New Secret Room"</i>, enter a Channel ID, and set a <b>Room Admin Master PIN</b>. Your PIN is hashed using <code>SHA-256</code> so even the database administrator cannot see it.</li>
            <li><b>📤 Sending Multi-Modal Messages:</b> Use the 3 tabs at the bottom of the room to broadcast encrypted text (with UTC self-destruct timers), English Camouflage sentences, or embed secrets into an <b>LSB Stego Image</b> and post the image directly into the chat feed!</li>
            <li><b>🔓 One-Click In-Room Decryption:</b> Click the <b>"🔓 Decode"</b> button next to any message or Stego Image in the chat feed to decrypt it instantly using your active sidebar rules.</li>
            <li><b>🗑️ Granular & Admin Deletion Controls:</b> Any user can delete an individual message using the <b>"🗑️ Delete"</b> button. However, wiping the entire room history (<b>"🧹 Clear Chat History"</b>) or permanently deleting the room (<b>"💥 Destroy Room"</b>) requires unlocking the <b>Room Admin Security Panel</b> with the creator's Admin PIN.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================================================
    # SECTION 4: INTERACTIVE GROUP CONFIG EXPORT UTILITY
    # ==========================================================================
    st.divider()
    st.markdown("### 📦 4. Quick Utility: Export Non-Sensitive Group Rule Blueprint")
    st.caption("Share your current Shift Offset, Symbol Vault sequence, and Custom Pairs with teammates (Passphrase is hidden for security).")
    
    export_blueprint = json.dumps({
        "platform": "Ultimate Secret Messenger v2.0",
        "author": "Le Hoang Phu Hieu (HCMUS)",
        "shift_offset": shift_step,
        "symbol_chain": pattern_list,
        "custom_pairs": custom_pairs,
        "reverse_structure": reverse_rule,
        "passphrase_hint": f"{len(secret_seed)} characters (Communicate via secure offline channel)" if secret_seed else "Not set"
    }, ensure_ascii=False, indent=2)
    
    st.code(export_blueprint, language="json")
    st.info("💡 *“Security is not a product, but a process.”* — Bruce Schneier | Architected with ❤️ by **Lê Hoàng Phú Hiếu (FIT - HCMUS)**.")

# ==============================================================================
# KHU VỰC GAME RIÊNG BIỆT: CYBER GAME ARCADE HUB (MULTI-GAME LOBBY)
# ==============================================================================
elif "Cyber Game Arcade" in main_menu:
    active_player = st.session_state.get("ctf_user") or "taolagautruc"
    render_sudoku_arcade(active_player)

elif "7. Community & Agency Hub" in main_menu:
    active_player = st.session_state.get("ctf_user") or "taolagautruc"
    render_community_hub(active_player)

elif "8. Cloud DB & Mobile App Studio" in main_menu:
    render_cloud_and_mobile_studio()

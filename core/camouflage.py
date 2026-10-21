import random
from core.cipher_engine import BASE_CHARS

# Ma trận từ vựng 16x16 (256 trạng thái mỗi cặp Adjective + Noun)
ADJ_POOL = [
    "new", "current", "updated", "global", "local", "primary", "secondary", "active",
    "pending", "final", "initial", "custom", "standard", "internal", "external", "core"
]
NOUN_POOL = [
    "report", "system", "project", "module", "server", "dataset", "schedule", "package",
    "client", "network", "document", "protocol", "agenda", "budget", "archive", "session"
]
VERB_POOL = [
    "requires", "confirms", "updates", "validates", "processes", "maintains", "reviews", "initiates",
    "completes", "monitors", "optimizes", "allocates", "prepares", "verifies", "tracks", "secures"
]
ADV_POOL = [
    "today", "smoothly", "properly", "quickly", "online", "now", "daily", "weekly",
    "effectively", "securely", "globally", "directly", "shortly", "carefully", "fully", "early"
]
CONNECTORS = [
    "Additionally,", "Meanwhile,", "Furthermore,", "As discussed,", "Please note that",
    "In the meantime,", "For the next phase,", "According to the team,", "Moving forward,"
]


def encode_english_camouflage(cypher_text: str) -> str:
    """Biến chuỗi mật mã thành đoạn văn tiếng Anh tự nhiên với Salt ngẫu nhiên mỗi lần bấm."""
    salt = random.randint(0, 255)
    raw_bytes = [salt] + [BASE_CHARS.index(c) if c in BASE_CHARS else 0 for c in cypher_text]
    
    sentences = []
    for idx, val in enumerate(raw_bytes):
        masked_val = (val + salt + idx * 7) % 256 if idx > 0 else salt
        high_nibble = (masked_val >> 4) & 0x0F
        low_nibble = masked_val & 0x0F
        
        adj = ADJ_POOL[high_nibble]
        noun = NOUN_POOL[low_nibble]
        verb = VERB_POOL[(high_nibble + idx) % 16]
        adv = ADV_POOL[(low_nibble + idx) % 16]
        
        prefix = f"{random.choice(CONNECTORS)} the" if (idx > 0 and idx % 2 == 0) else "The"
        sentences.append(f"{prefix} {adj} {noun} {verb} {adv}.")
        
    return " ".join(sentences)


def decode_english_camouflage(camo_text: str) -> str:
    """Trích xuất ngược từ đoạn văn tiếng Anh về chuỗi mật mã gốc."""
    words = [w.strip(".,!?;:").lower() for w in camo_text.split()]
    extracted_adjs = [w for w in words if w in ADJ_POOL]
    extracted_nouns = [w for w in words if w in NOUN_POOL]
    
    if not extracted_adjs or len(extracted_adjs) != len(extracted_nouns):
        raise ValueError("Invalid camouflage text format! Missing keyword pairs.")
        
    raw_vals = []
    for i in range(len(extracted_adjs)):
        high_nibble = ADJ_POOL.index(extracted_adjs[i])
        low_nibble = NOUN_POOL.index(extracted_nouns[i])
        raw_vals.append((high_nibble << 4) | low_nibble)
        
    salt = raw_vals[0]
    chars = []
    for idx in range(1, len(raw_vals)):
        masked_val = raw_vals[idx]
        orig_val = (masked_val - salt - idx * 7) % 256
        if 0 <= orig_val < len(BASE_CHARS):
            chars.append(BASE_CHARS[orig_val])
    return "".join(chars)


def inspect_camouflage_structure(camo_text: str) -> list[dict]:
    """Hàm phục vụ trang Security Academy: Phân tích từng cặp từ ra mã nhị phân 8-bit."""
    words = [w.strip(".,!?;:").lower() for w in camo_text.split()]
    adjs = [w for w in words if w in ADJ_POOL]
    nouns = [w for w in words if w in NOUN_POOL]
    
    breakdown = []
    limit = min(len(adjs), len(nouns), 6)  # Hiển thị tối đa 6 cặp đầu tiên cho gọn
    for i in range(limit):
        h = ADJ_POOL.index(adjs[i])
        l = NOUN_POOL.index(nouns[i])
        byte_val = (h << 4) | l
        breakdown.append({
            "Step": "Random Salt" if i == 0 else f"Char #{i}",
            "Word Pair": f"{adjs[i]} + {nouns[i]}",
            "4-Bit High": format(h, '04b'),
            "4-Bit Low": format(l, '04b'),
            "Merged Byte": format(byte_val, '08b')
        })
    return breakdown

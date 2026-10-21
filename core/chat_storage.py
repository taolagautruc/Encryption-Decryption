import json
import os
import time
import hashlib

# File JSON lưu trữ vĩnh viễn lịch sử các phòng chat
STORAGE_FILE = "chat_rooms_db.json"


def _hash_password(password: str) -> str:
    """Băm mật khẩu phòng bằng SHA-256 để không lưu mật khẩu thô."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_all_rooms() -> dict:
    """Đọc dữ liệu toàn bộ các phòng chat từ ổ cứng."""
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_all_rooms(data: dict):
    """Lưu dữ liệu phòng chat xuống ổ cứng để không bị mất khi mọi người thoát ra."""
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def create_or_join_room(room_id: str, room_pass: str) -> tuple[bool, str]:
    """Tạo phòng mới nếu chưa tồn tại, hoặc kiểm tra mật khẩu nếu phòng đã có sẵn."""
    room_id = room_id.strip()
    if not room_id or not room_pass:
        return False, "⚠️ Please enter both Room ID and Room Password!"

    rooms = load_all_rooms()
    pass_hash = _hash_password(room_pass)

    if room_id not in rooms:
        rooms[room_id] = {
            "password_hash": pass_hash,
            "created_at": int(time.time()),
            "messages": []
        }
        save_all_rooms(rooms)
        return True, f"✨ Created and joined new secret room: '{room_id}'"
    else:
        if rooms[room_id]["password_hash"] == pass_hash:
            return True, f"🔓 Successfully joined room: '{room_id}'"
        else:
            return False, "❌ Incorrect Room Password! Access denied."


def add_message(room_id: str, sender: str, content: str, is_encrypted: bool, enc_type: str = "NONE"):
    """Thêm tin nhắn mới (thường hoặc mã hóa) vào lịch sử phòng chat."""
    rooms = load_all_rooms()
    if room_id in rooms:
        msg_obj = {
            "id": f"msg_{int(time.time() * 1000)}",
            "sender": sender.strip() or "Anonymous",
            "content": content,
            "is_encrypted": is_encrypted,
            "enc_type": enc_type,  # "NONE", "CIPHER", hoặc "CAMO"
            "timestamp": int(time.time())
        }
        rooms[room_id]["messages"].append(msg_obj)
        save_all_rooms(rooms)


def get_room_messages(room_id: str) -> list[dict]:
    """Lấy toàn bộ lịch sử tin nhắn của phòng."""
    rooms = load_all_rooms()
    if room_id in rooms:
        return rooms[room_id].get("messages", [])
    return []


def clear_room_history(room_id: str):
    """Xóa toàn bộ lịch sử trò chuyện của phòng khi cần thiết."""
    rooms = load_all_rooms()
    if room_id in rooms:
        rooms[room_id]["messages"] = []
        save_all_rooms(rooms)

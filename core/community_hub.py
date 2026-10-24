import streamlit as st
import json
import os
import time
import random
import hashlib
from datetime import datetime, timezone

COMM_DB_FILE = "community_hub_db.json"

def load_json_safe(filepath: str) -> dict:
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def load_comm_db() -> dict:
    if not os.path.exists(COMM_DB_FILE):
        seed_data = {
            "profiles": {},
            "daily_solvers": {},
            "ugc_puzzles": [
                {
                    "id": "UGC_101",
                    "title": "The Phantom Server Breach",
                    "author": "AlexMercer_US",
                    "category": "🕵️ Digital Forensics",
                    "difficulty": "Medium (500 XP)",
                    "reward": 500,
                    "story": "An insider leaked our database IP. They left a Caesar +2 shifted note on the terminal: `QPGTCVKQP DNCEM`.",
                    "cipher_display": "QPGTCVKQP DNCEM",
                    "hint": "Shift each letter 2 positions backward in the English alphabet (Q -> O, P -> N...).",
                    "answer_hash": hashlib.sha256(b"OPERATION BLACK").hexdigest(),
                    "upvotes": 14,
                    "upvoters": [],
                    "solvers": ["ElenaRostova_UK"]
                },
                {
                    "id": "UGC_102",
                    "title": "Sherlock's Reversed Telegram",
                    "author": "ElenaRostova_UK",
                    "category": "📜 Classical Cipher",
                    "difficulty": "Easy (300 XP)",
                    "reward": 300,
                    "story": " Irene Adler sent a telegram to 221B Baker Street written completely backwards with numbers (`4=A, 3=E, 1=I, 0=O`).",
                    "cipher_display": "N 0 D N 0 L",
                    "hint": "Read from right to left and replace 0 with O!",
                    "answer_hash": hashlib.sha256(b"LONDON").hexdigest(),
                    "upvotes": 9,
                    "upvoters": [],
                    "solvers": ["AlexMercer_US", "KenjiSato_JP"]
                }
            ],
            "agencies": {
                "HCMUS Cyber Division": {
                    "founder": "taolagautruc",
                    "motto": "Zero-Trust • Mathematical Excellence • VNU-HCM",
                    "members": ["taolagautruc"],
                    "raid_locks_cracked": []
                },
                "Baker Street Irregulars": {
                    "founder": "ElenaRostova_UK",
                    "motto": "When you have eliminated the impossible, whatever remains must be the truth.",
                    "members": ["ElenaRostova_UK", "AlexMercer_US"],
                    "raid_locks_cracked": ["LOCK_1"]
                }
            }
        }
        with open(COMM_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(seed_data, f, ensure_ascii=False, indent=4)
        return seed_data
    try:
        with open(COMM_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"profiles": {}, "daily_solvers": {}, "ugc_puzzles": [], "agencies": {}}

def save_comm_db(data: dict):
    with open(COMM_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_unified_agent_stats(username: str, comm_db: dict) -> dict:
    """Tự động tổng hợp điểm số của người chơi từ tất cả các chế độ trong hệ sinh thái."""
    ctf_db = load_json_safe("ctf_arena_db.json")
    acad_db = load_json_safe("academy_lms_db.json")
    sdk_db = load_json_safe("sudoku_arena_db.json")

    ctf_pts = ctf_db.get("users", {}).get(username, {}).get("score", 0)
    ctf_solved = len(ctf_db.get("users", {}).get(username, {}).get("solved", []))

    acad_xp = acad_db.get("students", {}).get(username, {}).get("xp", 0)
    acad_tasks = len(acad_db.get("students", {}).get(username, {}).get("completed_tasks", []))

    sdk_pts = sdk_db.get("leaderboard", {}).get(username, {}).get("sudoku_score", 0)
    sdk_solved = sdk_db.get("leaderboard", {}).get(username, {}).get("puzzles_solved", 0)

    prof = comm_db.get("profiles", {}).get(username, {})
    comm_xp = prof.get("comm_xp", 0)

    total_xp = max(0, ctf_pts) + acad_xp + max(0, sdk_pts) + comm_xp
    return {
        "ctf_pts": ctf_pts,
        "ctf_solved": ctf_solved,
        "acad_xp": acad_xp,
        "acad_tasks": acad_tasks,
        "sdk_pts": sdk_pts,
        "sdk_solved": sdk_solved,
        "comm_xp": comm_xp,
        "total_xp": total_xp
    }

def generate_daily_global_mystery(date_str: str) -> dict:
    """Sinh Vụ án Toàn cầu 24h tự động theo ngày UTC (Mọi người chơi trong ngày đều có chung vụ án)."""
    rng = random.Random(f"GLOBAL_DAILY_MYSTERY_{date_str}")
    cases = [
        {
            "title": "Case #24A: The Geneva Vault Heist",
            "story": (
                "At 02:15 UTC today, an encrypted distress signal was broadcast from a private Swiss vault in Geneva. "
                "Forensic analysts recovered a 2-layer cipher: the culprit took the name of a famous **European capital city**, "
                "shifted every letter forward by **+3 (Caesar +3)**, and then **reversed the entire word from right to left**."
            ),
            "plain": "PARIS",
            "clue": "The City of Light and home to the Eiffel Tower (5 letters)."
        },
        {
            "title": "Case #24B: Submarine Blackbox Intercept",
            "story": (
                "A deep-sea research submarine near the Mariana Trench transmitted an emergency beacon before losing contact. "
                "The beacon payload was encoded using **Caesar Shift +2** and then **reversed backwards**."
            ),
            "plain": "TITAN",
            "clue": "A 5-letter word meaning a giant deity in Greek mythology (also the largest moon of Saturn)."
        },
        {
            "title": "Case #24C: The Syndicate Satellite Key",
            "story": (
                "Interpol intercepted a rogue satellite command. The operator disguised a 6-letter astronomical word "
                "by shifting each letter forward by **+1 (Caesar +1)** and then **writing it backwards**."
            ),
            "plain": "NEBULA",
            "clue": "A giant interstellar cloud of dust and gas in space where stars are born (6 letters, starts with N)."
        },
        {
            "title": "Case #24D: The Baker Street Cryptogram",
            "story": (
                "A mysterious envelope arrived at Scotland Yard. Inside was a single codeword encrypted with "
                "**Caesar Shift +2** and **flipped from right to left**."
            ),
            "plain": "SHADOW",
            "clue": "A dark shape produced when a body blocks rays of light (6 letters, starts with S)."
        }
    ]
    chosen = rng.choice(cases)
    shift = 3 if "Geneva" in chosen["title"] else (1 if "Satellite" in chosen["title"] else 2)
    shifted = "".join(chr((ord(c) - 65 + shift) % 26 + 65) for c in chosen["plain"])
    cipher_out = shifted[::-1]
    return {
        "date": date_str,
        "title": chosen["title"],
        "story": chosen["story"],
        "clue": chosen["clue"],
        "shift": shift,
        "cipher": cipher_out,
        "answer": chosen["plain"]
    }

# ==============================================================================
# DANH SÁCH VẬT PHẨM TRONG CỬA HÀNG (CYBER SHOP ITEMS)
# ==============================================================================
SHOP_ITEMS = {
    "badge_shield": {"name": "🛡️ Aegis Defender Badge", "type": "badge", "icon": "🛡️", "cost": 0, "desc": "Default operative emblem."},
    "badge_detective": {"name": "🕵️ Master Sleuth Emblem", "type": "badge", "icon": "🕵️", "cost": 500, "desc": "Awarded to sharp forensic minds."},
    "badge_dragon": {"name": "🐉 Cyber Dragon Crest", "type": "badge", "icon": "🐉", "cost": 2000, "desc": "Elite emblem of high-tier cryptanalysts."},
    "badge_crown": {"name": "👑 Sovereign Archon Crown", "type": "badge", "icon": "👑", "cost": 5000, "desc": "Reserved for top global legends."},
    "theme_cyber": {"name": "🌌 Cyber Neon Blue (Default)", "type": "theme", "color": "#3b82f6", "bg": "linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)", "cost": 0},
    "theme_matrix": {"name": "🟢 Matrix Emerald Hacker", "type": "theme", "color": "#10b981", "bg": "linear-gradient(135deg, #022c22 0%, #064e3b 100%)", "cost": 1000},
    "theme_crimson": {"name": "🔴 Red Team Crimson Ops", "type": "theme", "color": "#ef4444", "bg": "linear-gradient(135deg, #450a0a 0%, #7f1d1d 100%)", "cost": 2500},
    "theme_gold": {"name": "🟡 Sherlock Victorian Gold", "type": "theme", "color": "#f59e0b", "bg": "linear-gradient(135deg, #451a03 0%, #78350f 100%)", "cost": 4000}
}

def render_community_hub(default_user: str = "taolagautruc"):
    comm_db = load_comm_db()

    st.markdown("""
    <div class="hero-box" style="padding: 22px 30px; margin-bottom: 18px;">
        <div class="hero-badge">🌍 PILLAR 3 ECOSYSTEM • AGENT ID CARD • DAILY GLOBAL MYSTERY • UGC PUZZLE MAKER • CLANS</div>
        <h2 style="color: #f8fafc; margin: 4px 0 6px 0; font-weight: 800;">Global Community, Detective Agencies & Agent Hub</h2>
        <p class="hero-sub">
            Customize your Agent ID Card, crack the 24-Hour Global Mystery, design your own puzzles for the community, or team up in Detective Agencies!
        </p>
    </div>
    """, unsafe_allow_html=True)

    top_c1, top_c2 = st.columns([1.5, 2.5])
    with top_c1:
        agent_id = st.text_input("🕵️ Active Agent Callsign:", value=st.session_state.get("ctf_user") or default_user, key="comm_user_in").strip() or "taolagautruc"

    if agent_id not in comm_db["profiles"]:
        comm_db["profiles"][agent_id] = {
            "comm_xp": 500,  # Tặng 500 XP khởi điểm cho điệp viên mới
            "spent_xp": 0,
            "owned_items": ["badge_shield", "theme_cyber"],
            "equipped_badge": "badge_shield",
            "equipped_theme": "theme_cyber",
            "bio": "Cryptanalyst & Forensic Investigator at Ultimate Secret Messenger."
        }
        save_comm_db(comm_db)

    prof = comm_db["profiles"][agent_id]
    stats = get_unified_agent_stats(agent_id, comm_db)
    available_credits = max(0, stats["total_xp"] - prof.get("spent_xp", 0))

    with top_c2:
        m1, m2, m3 = st.columns(3)
        m1.metric("🌟 Total Ecosystem XP", f"{stats['total_xp']:,} XP", "All Modules Combined")
        m2.metric("💰 Spendable Cyber Credits", f"{available_credits:,} CR", f"Spent: {prof.get('spent_xp', 0):,} CR")
        m3.metric("🧩 Total Cases/Boards Cracked", f"{stats['ctf_solved'] + stats['sdk_solved'] + stats['acad_tasks']}", "CTF + Sudoku + Academy")

    tab_id, tab_daily, tab_ugc, tab_clan = st.tabs([
        "🪪 1. Agent ID Card & Cyber Shop",
        "🌍 2. Daily Global Mystery (24h Event)",
        "🛠️ 3. Community Puzzle Maker (UGC)",
        "🦅 4. Detective Agencies & Clan Raid"
    ])

    # ==========================================================================
    # TAB 1: AGENT ID CARD & CYBER SHOP
    # ==========================================================================
    with tab_id:
        id_col, shop_col = st.columns([1.3, 1.7])

        eq_badge = SHOP_ITEMS.get(prof.get("equipped_badge", "badge_shield"), SHOP_ITEMS["badge_shield"])
        eq_theme = SHOP_ITEMS.get(prof.get("equipped_theme", "theme_cyber"), SHOP_ITEMS["theme_cyber"])

        with id_col:
            st.markdown("##### 🪪 Official Cryptographic Agent ID Card")
            st.markdown(f"""
            <div style="background: {eq_theme['bg']}; border: 2px solid {eq_theme['color']}; border-radius: 16px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.45); margin-bottom: 16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.15); padding-bottom:12px; margin-bottom:14px;">
                    <div>
                        <div style="font-size:0.75rem; color:#93c5fd; font-weight:700; letter-spacing:1.2px;">ULTIMATE SECRET MESSENGER // ID PASSPORT</div>
                        <div style="font-size:1.65rem; font-weight:800; color:#ffffff; margin-top:2px;">{eq_badge['icon']} {agent_id}</div>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:rgba(255,255,255,0.12); color:#fde047; padding:4px 10px; border-radius:999px; font-size:0.78rem; font-weight:700;">
                            LEVEL {max(1, stats['total_xp'] // 1000 + 1)}
                        </span>
                    </div>
                </div>
                <p style="color:#e2e8f0; font-size:0.9rem; font-style:italic; margin-bottom:16px;">"{prof.get('bio', '')}"</p>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; background:rgba(0,0,0,0.3); padding:12px; border-radius:10px; font-size:0.84rem; color:#cbd5e1;">
                    <div>🕹️ <b>CTF Arena:</b> {stats['ctf_pts']:,} PTS ({stats['ctf_solved']} solved)</div>
                    <div>📚 <b>Academy LMS:</b> {stats['acad_xp']:,} XP ({stats['acad_tasks']} tasks)</div>
                    <div>🧩 <b>Sudoku Arcade:</b> {stats['sdk_pts']:,} PTS ({stats['sdk_solved']} boards)</div>
                    <div>🌍 <b>Community XP:</b> {stats['comm_xp']:,} XP</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            new_bio = st.text_input("✏️ Update Agent Motto / Bio:", value=prof.get("bio", ""))
            if st.button("💾 Save Bio", use_container_width=True):
                prof["bio"] = new_bio.strip()
                save_comm_db(comm_db)
                st.toast("✅ Agent Bio updated!", icon="🪪")
                st.rerun()

        with shop_col:
            st.markdown("##### 🛒 Cyber Armory & Cosmetic Shop (Spend Your Earned Credits!)")
            st.caption(f"You currently have **{available_credits:,} Cyber Credits (CR)** available to unlock badges and ID Card themes.")

            for item_id, item in SHOP_ITEMS.items():
                owned = item_id in prof.get("owned_items", [])
                is_equipped = (item_id == prof.get("equipped_badge")) or (item_id == prof.get("equipped_theme"))

                sc1, sc2 = st.columns([2.6, 1.2])
                with sc1:
                    status_tag = "✅ *Equipped*" if is_equipped else ("🔓 *Owned*" if owned else f"🔒 **{item['cost']:,} CR**")
                    st.markdown(f"**{item['name']}** — {status_tag}")
                with sc2:
                    if is_equipped:
                        st.button("Equipped", key=f"eq_{item_id}", disabled=True, use_container_width=True)
                    elif owned:
                        if st.button("✨ Equip", key=f"use_{item_id}", use_container_width=True):
                            if item["type"] == "badge":
                                prof["equipped_badge"] = item_id
                            else:
                                prof["equipped_theme"] = item_id
                            save_comm_db(comm_db)
                            st.rerun()
                    else:
                        if st.button(f"🛒 Buy ({item['cost']} CR)", key=f"buy_{item_id}", type="primary", use_container_width=True, disabled=(available_credits < item["cost"])):
                            prof["spent_xp"] = prof.get("spent_xp", 0) + item["cost"]
                            prof["owned_items"].append(item_id)
                            if item["type"] == "badge":
                                prof["equipped_badge"] = item_id
                            else:
                                prof["equipped_theme"] = item_id
                            save_comm_db(comm_db)
                            st.balloons()
                            st.rerun()

    # ==========================================================================
    # TAB 2: DAILY GLOBAL MYSTERY (24H WORLDWIDE EVENT)
    # ==========================================================================
    with tab_daily:
        today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        daily_case = generate_daily_global_mystery(today_utc)
        todays_solvers = comm_db.get("daily_solvers", {}).get(today_utc, [])

        st.markdown(f"""
        <div class="ws-banner">
            <h4>🌍 Daily Global Mystery — Date: <code>{today_utc} (UTC)</code> • Reward: <b style="color:#34d399;">+1,500 XP</b></h4>
            <p>Every 24 hours at 00:00 UTC, all operatives worldwide receive the exact same forensic case. Solve it to claim your spot on today's First-Blood Hall of Fame!</p>
        </div>
        """, unsafe_allow_html=True)

        d_col1, d_col2 = st.columns([1.8, 1.2])
        with d_col1:
            st.markdown(f"### 🕵️ {daily_case['title']}")
            st.write(daily_case["story"])
            st.info(f"💡 **Intelligence Clue:** {daily_case['clue']}")
            st.markdown("**Intercepted Encrypted Transmission:**")
            st.code(daily_case["cipher"], language=None)

            already_cracked = any(s["agent"] == agent_id for s in todays_solvers)
            if already_cracked:
                st.success(f"✅ **CASE CLOSED!** You have already solved today's Global Mystery (`{daily_case['answer']}`)!")
            else:
                d_guess = st.text_input("🚩 Enter Decoded Codeword:", placeholder="Type the decoded word...")
                if st.button("🔓 Submit Daily Mystery Deduction (+1,500 XP)", type="primary"):
                    if d_guess.strip().upper() == daily_case["answer"].upper():
                        if today_utc not in comm_db["daily_solvers"]:
                            comm_db["daily_solvers"][today_utc] = []
                        comm_db["daily_solvers"][today_utc].append({
                            "agent": agent_id,
                            "time": datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
                        })
                        prof["comm_xp"] = prof.get("comm_xp", 0) + 1500
                        save_comm_db(comm_db)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Incorrect deduction! Hint: Reverse `{daily_case['cipher']}` first, then shift each letter back by `{daily_case['shift']}`!")

        with d_col2:
            st.markdown(f"##### 🏆 Today's First-Blood Hall of Fame (`{today_utc}`)")
            if not todays_solvers:
                st.info("🔥 No operative has cracked today's mystery yet! Be the **#1 First Blood** solver today!")
            else:
                for idx, s_entry in enumerate(todays_solvers, start=1):
                    medal = "🥇 First Blood" if idx == 1 else (f"🥈 #{idx}" if idx == 2 else f"🎖️ #{idx}")
                    st.markdown(f"- **{medal}:** `{s_entry['agent']}` *(at {s_entry['time']})*")

    # ==========================================================================
    # TAB 3: COMMUNITY PUZZLE & CASE MAKER (USER-GENERATED CONTENT - UGC)
    # ==========================================================================
    with tab_ugc:
        st.markdown("""
        <div class="ws-banner">
            <h4>🛠️ Community Puzzle Studio & Bounty Board (User-Generated Content)</h4>
            <p>Create your own cipher mysteries for other players to solve! Earn <b>+300 Creator XP</b> when publishing a puzzle and <b>+100 XP</b> every time a player upvotes your creation!</p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("➕ Create & Publish Your Own Detective / Cipher Puzzle (+300 Creator XP)"):
            u_c1, u_c2 = st.columns(2)
            with u_c1:
                p_title = st.text_input("📌 Puzzle / Case Title:", placeholder="e.g. The Saigon Midnight Drop")
                p_cat = st.selectbox("📂 Category:", ["🕵️ Digital Forensics", "📜 Classical Cipher", "🧩 Logic & Trivia", "🪐 Sci-Fi Mystery"])
                p_diff = st.selectbox("🔥 Difficulty & Bounty Reward:", ["Easy (300 XP)", "Medium (500 XP)", "Hard (1,000 XP)"])
            with u_c2:
                p_ans = st.text_input("🔑 Exact Secret Answer (Plaintext):", placeholder="e.g. ENIGMA")
                p_enc_mode = st.selectbox("🔐 Auto-Encryption Method:", [
                    "Caesar Shift +3 (Auto-encode my answer)",
                    "Reverse Spelling Backwards (Auto-encode)",
                    "Atbash Mirror A<->Z (Auto-encode)",
                    "Custom Ciphertext (I will type my own encrypted string below)"
                ])
                p_custom_cipher = st.text_input("Custom Ciphertext (Only if 'Custom' selected above):")

            p_story = st.text_area("📖 Case Story & Clue for Players:", placeholder="Describe the mystery scenario and give players a fair clue...")
            p_hint = st.text_input("💡 Helpful Hint for Players:", placeholder="e.g. Shift each letter 3 steps back...")

            if st.button("🚀 Publish Puzzle to Community Bounty Board (+300 XP)", type="primary"):
                if not p_title.strip() or not p_ans.strip() or not p_story.strip():
                    st.error("Please fill in the Title, Secret Answer, and Story!")
                else:
                    clean_ans = " ".join(p_ans.strip().upper().split())
                    if "Caesar" in p_enc_mode:
                        gen_cipher = "".join(chr((ord(c) - 65 + 3) % 26 + 65) if "A" <= c <= "Z" else c for c in clean_ans)
                    elif "Reverse" in p_enc_mode:
                        gen_cipher = clean_ans[::-1]
                    elif "Atbash" in p_enc_mode:
                        gen_cipher = "".join(chr(90 - (ord(c) - 65)) if "A" <= c <= "Z" else c for c in clean_ans)
                    else:
                        gen_cipher = p_custom_cipher.strip() or clean_ans[::-1]

                    rew_val = 300 if "300" in p_diff else (500 if "500" in p_diff else 1000)
                    new_ugc = {
                        "id": f"UGC_{int(time.time()) % 100000}",
                        "title": p_title.strip(),
                        "author": agent_id,
                        "category": p_cat,
                        "difficulty": p_diff,
                        "reward": rew_val,
                        "story": p_story.strip(),
                        "cipher_display": gen_cipher,
                        "hint": p_hint.strip() or "Analyze the cipher pattern carefully!",
                        "answer_hash": hashlib.sha256(clean_ans.encode("utf-8")).hexdigest(),
                        "upvotes": 1,
                        "upvoters": [agent_id],
                        "solvers": []
                    }
                    comm_db["ugc_puzzles"].insert(0, new_ugc)
                    prof["comm_xp"] = prof.get("comm_xp", 0) + 300
                    save_comm_db(comm_db)
                    st.success("🎉 Your puzzle is now live on the Community Bounty Board! (+300 Creator XP awarded)")
                    st.rerun()

        st.markdown("##### 📋 Active Community Bounty Board")
        for idx, puz in enumerate(comm_db.get("ugc_puzzles", [])):
            pid = puz["id"]
            solved_by_me = agent_id in puz.get("solvers", [])
            with st.container(border=True):
                h1, h2, h3 = st.columns([2.5, 1, 0.8])
                with h1:
                    st.markdown(f"#### {puz['category']} — **{puz['title']}** `({ pid })`")
                    st.caption(f"✍️ Created by: **`{puz['author']}`** &nbsp;|&nbsp; 🔥 **{puz['difficulty']}** &nbsp;|&nbsp; ✅ Solved by `{len(puz.get('solvers', []))}` agents")
                with h2:
                    if solved_by_me:
                        st.success("✅ Cracked!")
                with h3:
                    if st.button(f"⭐ {puz.get('upvotes', 0)} Upvote", key=f"upv_{pid}", use_container_width=True):
                        if agent_id not in puz.get("upvoters", []):
                            puz.setdefault("upvoters", []).append(agent_id)
                            puz["upvotes"] = puz.get("upvotes", 0) + 1
                            author_id = puz["author"]
                            if author_id in comm_db["profiles"]:
                                comm_db["profiles"][author_id]["comm_xp"] = comm_db["profiles"][author_id].get("comm_xp", 0) + 100
                            save_comm_db(comm_db)
                            st.rerun()
                        else:
                            st.toast("You already upvoted this puzzle!", icon="⭐")

                st.write(puz["story"])
                st.code(puz["cipher_display"], language=None)

                if not solved_by_me:
                    uc1, uc2, uc3 = st.columns([2.2, 1, 1])
                    with uc1:
                        u_try = st.text_input("Your Answer:", key=f"try_{pid}", placeholder="Type decoded answer...", label_visibility="collapsed")
                    with uc2:
                        if st.button(f"🔓 Solve (+{puz['reward']} XP)", key=f"btn_s_{pid}", type="primary", use_container_width=True):
                            clean_try = " ".join(u_try.strip().upper().split())
                            if hashlib.sha256(clean_try.encode("utf-8")).hexdigest() == puz["answer_hash"]:
                                puz.setdefault("solvers", []).append(agent_id)
                                prof["comm_xp"] = prof.get("comm_xp", 0) + puz["reward"]
                                save_comm_db(comm_db)
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("❌ Incorrect answer!")
                    with uc3:
                        with st.popover("💡 View Hint", use_container_width=True):
                            st.write(puz.get("hint", "No hint provided."))

    # ==========================================================================
    # TAB 4: DETECTIVE AGENCIES & CLAN CO-OP RAID VAULT
    # ==========================================================================
    with tab_clan:
        st.markdown("""
        <div class="ws-banner">
            <h4>🦅 Detective Agencies (Clans) & Co-op Syndicate Raid</h4>
            <p>Join or found a Detective Agency! Combine your members' total XP on the Agency Leaderboard and work together to unlock the 3 Co-op Raid Vault Locks!</p>
        </div>
        """, unsafe_allow_html=True)

        agencies = comm_db.get("agencies", {})
        c_left, c_right = st.columns([1.3, 1.7])

        with c_left:
            st.markdown("##### 🏛️ Found or Join an Agency")
            new_ag_name = st.text_input("New Agency Name:", placeholder="e.g. Saigon Phantom Agency")
            new_ag_motto = st.text_input("Agency Motto:", placeholder="e.g. In Cryptography We Trust")
            if st.button("🦅 Establish New Agency", type="primary", use_container_width=True):
                aname = new_ag_name.strip()
                if aname and aname not in agencies:
                    agencies[aname] = {
                        "founder": agent_id,
                        "motto": new_ag_motto.strip() or " Truth through Cryptanalysis.",
                        "members": [agent_id],
                        "raid_locks_cracked": []
                    }
                    save_comm_db(comm_db)
                    st.rerun()

            st.divider()
            st.markdown("##### 🏆 Global Agency Standings")
            for ag_name, ag_info in agencies.items():
                members = ag_info.get("members", [])
                team_xp = sum(get_unified_agent_stats(m, comm_db)["total_xp"] for m in members)
                with st.container(border=True):
                    st.markdown(f"**🦅 {ag_name}** — 🏆 **{team_xp:,} Team XP**")
                    st.caption(f"*{ag_info.get('motto', '')}* • 👥 Members ({len(members)}): `{', '.join(members)}`")
                    if agent_id not in members:
                        if st.button(f"➕ Join {ag_name}", key=f"join_{ag_name}", use_container_width=True):
                            ag_info["members"].append(agent_id)
                            save_comm_db(comm_db)
                            st.rerun()

        with c_right:
            st.markdown("##### 🔐 Weekend Co-op Raid Boss: The 3-Lock Quantum Vault")
            st.info("Work together with your Agency teammates to crack all 3 security locks! Each lock cracked awards **+1,000 XP** to the solver!")

            my_agency = next((k for k, v in agencies.items() if agent_id in v.get("members", [])), None)
            if not my_agency:
                st.warning("⚠️ Please join or establish a Detective Agency on the left to participate in the Co-op Raid!")
            else:
                ag_obj = agencies[my_agency]
                cracked_list = ag_obj.get("raid_locks_cracked", [])
                st.markdown(f"📡 **Active Agency:** `{my_agency}` — **Vault Progress:** `{len(cracked_list)} / 3 Locks Cracked`")
                st.progress(len(cracked_list) / 3.0)

                raid_locks = [
                    ("LOCK_1", "Lock #1 (Binary Gate)", "Convert 8-bit binary `01001011` to its decimal ASCII number (`64 + 8 + 2 + 1`):", "75"),
                    ("LOCK_2", "Lock #2 (Atbash Mirror)", "Decode the Atbash Mirror codeword `XIBKGL` (`X↔C, I↔R, B↔Y, K↔P, G↔T, O↔L`):", "CRYPTO"),
                    ("LOCK_3", "Lock #3 (RSA Final Core)", "Calculate RSA Encryption `C = 4^3 mod 33` (`64 mod 33`):", "31")
                ]

                for lid, ltitle, lprompt, lans in raid_locks:
                    if lid in cracked_list:
                        st.success(f"🔓 **{ltitle}:** CRACKED BY AGENCY! (Solution: `{lans}`)")
                    else:
                        rc1, rc2 = st.columns([2.5, 1])
                        with rc1:
                            l_in = st.text_input(f"🔐 {ltitle} — {lprompt}", key=f"raid_{my_agency}_{lid}")
                        with rc2:
                            st.write("")
                            if st.button(f"⚡ Crack {lid}", key=f"btn_r_{lid}", use_container_width=True):
                                if l_in.strip().upper() == lans:
                                    cracked_list.append(lid)
                                    ag_obj["raid_locks_cracked"] = cracked_list
                                    prof["comm_xp"] = prof.get("comm_xp", 0) + 1000
                                    save_comm_db(comm_db)
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("❌ Lock held firm!")

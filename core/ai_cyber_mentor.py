import streamlit as st
import json
import os
import re
import html
import base64
import hashlib
import random
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from PIL import Image
import io

AI_MEMORY_FILE = "ai_mentor_memory_db.json"
DEFAULT_ADMIN_PIN_HASH = hashlib.sha256(b"HCMUS3001").hexdigest()

# ==============================================================================
# 1. CẦU NỐI DỊCH THUẬT & NHẬN DIỆN 100+ NGÔN NGỮ TỰ ĐỘNG
# ==============================================================================
def auto_translate_text(text: str, source_lang: str = "auto", target_lang: str = "en") -> tuple[str, str]:
    if not text or not text.strip():
        return "", "en"
    try:
        q_enc = urllib.parse.quote(text.strip())
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={q_enc}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated_chunks = [seg[0] for seg in data[0] if seg and seg[0]]
            translated_str = "".join(translated_chunks)
            detected_lang = data[2] if len(data) > 2 and isinstance(data[2], str) else "en"
            return translated_str, detected_lang
    except Exception:
        low = text.lower()
        if any(c in "àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ" for c in low):
            return text, "vi"
        if any(c in "äöüß" for c in low) or "ich " in low or "wie " in low:
            return text, "de"
        return text, "en"


# ==============================================================================
# 2. MỞ RỘNG GIÁO TRÌNH ĐẠI HỌC: BÀI 21 ĐẾN BÀI 30 (TRACK 5 & TRACK 6)
# ==============================================================================
EXPANDED_MODULES_21_TO_30 = {
    "Lesson 21: Character Encoding Internals (ASCII, UTF-8, UTF-16/32)": {
        "num": 21,
        "track": "Track 5: Encoding Standards & Web Security",
        "title": "Character Encoding Internals (ASCII, UTF-8, UTF-16/32)",
        "overview": (
            "Character Encoding maps human-readable text characters into binary bytes that computers can store and transmit. "
            "ASCII uses 7 bits (128 characters: 0–127) for basic English letters and control codes. "
            "UTF-8 dominates ~90% of the global web by using variable-length encoding (1 to 4 bytes per character) while remaining 100% backward-compatible with ASCII (any ASCII byte 0x00–0x7F is identical in UTF-8). "
            "UTF-16 and UTF-32 use 2 to 4 bytes per character for internal OS memory and runtime engines."
        ),
        "formula": "ASCII: 1 char = 7 bits (0x00..0x7F) | UTF-8: 1B (0xxxxxxx), 2B (110xxxxx 10xxxxxx), 3B (1110xxxx 10xxxxxx 10xxxxxx), 4B (11110xxx ...)",
        "example": "Character 'A' -> ASCII/UTF-8 = 0x41 (1 byte: 01000001). Euro sign '€' (U+20AC) -> UTF-8 = E2 82 AC (3 bytes).",
        "q1_q": "Why is UTF-8 the dominant character encoding standard on the modern web (~90% of websites)?",
        "q1_opts": [
            "It supports all global languages using 1–4 bytes and is 100% backward-compatible with 7-bit ASCII",
            "It uses a secret AES encryption key to hide text",
            "It compresses video files into MP4 containers",
            "It only supports uppercase English letters"
        ],
        "q1_ans": "It supports all global languages using 1–4 bytes and is 100% backward-compatible with 7-bit ASCII",
        "q2_q": "How many characters are defined in the standard 7-bit ASCII table?",
        "q2_opts": ["64 characters", "128 characters", "256 characters", "65536 characters"],
        "q2_ans": "128 characters",
        "lab1_q": "Convert the ASCII string 'OK' into two 2-digit uppercase Hexadecimal bytes separated by a space (Hint: 'O'=79=0x4F, 'K'=75=0x4B):",
        "lab1_ans": "4F 4B",
        "lab2_q": "A UTF-8 leading byte starts with binary bits '1110xxxx' (e.g. 0xE2). How many total bytes does this UTF-8 character occupy? (Enter a single digit):",
        "lab2_ans": "3"
    },
    "Lesson 22: Data & Binary-to-Text Encoding (Base64, URL %20 & HTML XSS Defense)": {
        "num": 22,
        "track": "Track 5: Encoding Standards & Web Security",
        "title": "Data & Binary-to-Text Encoding (Base64, URL %20 & HTML XSS Defense)",
        "overview": (
            "Binary-to-Text encoding ensures raw binary assets (images, keys, arbitrary bytes) survive transmission across text-only protocols. "
            "Base64 slices every 3 bytes (24 bits) into four 6-bit chunks (64 printable ASCII symbols: A-Z, a-z, 0-9, +, /) with '=' padding, used in HTML Data URIs, MIME emails, and JWT tokens. "
            "URL Percent Encoding converts unsafe URI characters into '%XX' hex (e.g. space -> '%20'). "
            "HTML Entity Encoding replaces '<', '>', '&' with '&lt;', '&gt;', '&amp;' to neutralize Cross-Site Scripting (XSS) injection."
        ),
        "formula": "Base64 Length = 4 * ceil(N_bytes / 3) | URL Space = %20 (0x20) | HTML '<' = &lt;",
        "example": "ASCII 'Man' (3 bytes: 0x4D, 0x61, 0x6E) -> 24 bits -> four 6-bit values (19, 22, 5, 46) -> Base64 'TWFu'.",
        "q1_q": "How does Base64 transform binary bytes into printable ASCII text?",
        "q1_opts": [
            "Groups every 3 bytes (24 bits) into four 6-bit ASCII characters",
            "Encrypts every byte using a 256-bit private key",
            "Hashes the file using SHA-256",
            "Replaces spaces with %20"
        ],
        "q1_ans": "Groups every 3 bytes (24 bits) into four 6-bit ASCII characters",
        "q2_q": "Which encoding prevents Cross-Site Scripting (XSS) by converting '<script>' into '&lt;script&gt;'?",
        "q2_opts": ["HTML Entity Encoding", "One-Hot Encoding", "FLAC Audio Encoding", "Caesar Shift"],
        "q2_ans": "HTML Entity Encoding",
        "lab1_q": "Encode the 3-character string 'Cat' into Base64 (Case-sensitive):",
        "lab1_ans": "Q2F0",
        "lab2_q": "What is the URL Percent-Encoded representation of 'A B' (capital A, a single space, capital B)?",
        "lab2_ans": "A%20B"
    },
    "Lesson 23: Multimedia Encoding (Video/Audio Codecs & Lossless Steganography)": {
        "num": 23,
        "track": "Track 5: Encoding Standards & Web Security",
        "title": "Multimedia Encoding (Video/Audio Codecs & Lossless Steganography)",
        "overview": (
            "Multimedia Encoding compresses high-bitrate video and audio streams for fast storage and network streaming. "
            "Popular video codecs include H.264 (AVC), H.265 (HEVC), VP9, and AV1 inside MP4 or MKV containers. "
            "Audio standards split into Lossy perceptual codecs (MP3, AAC, OGG) that discard frequencies to shrink size, and Lossless formats (FLAC, uncompressed WAV PCM) that preserve every exact bit. "
            "In LSB Steganography, operatives MUST use Lossless media (PNG, WAV, FLAC) because lossy quantization overwrites least significant bits."
        ),
        "formula": "Lossless (PNG, WAV, FLAC): Reconstructed == Original | Lossy (JPG, MP3, AAC): Reconstructed ≈ Original (Destroys LSB)",
        "example": "Hiding 1 bit per sample in 44.1 kHz 16-bit mono WAV yields 44,100 bits/sec (~5.5 KB/sec) of covert channel bandwidth.",
        "q1_q": "Which of the following is a lossless audio codec suitable for bit-exact preservation?",
        "q1_opts": ["FLAC", "MP3", "AAC", "H.264"],
        "q1_ans": "FLAC",
        "q2_q": "Why does saving a Stego-PNG image as a compressed JPEG (.jpg) destroy the hidden LSB message?",
        "q2_opts": [
            "JPEG uses lossy Discrete Cosine Transform (DCT) quantization that alters pixel LSB values",
            "JPEG files cannot display RGB colors",
            "JPEG automatically encrypts the image with RSA",
            "JPEG converts the image into an MP3 audio file"
        ],
        "q2_ans": "JPEG uses lossy Discrete Cosine Transform (DCT) quantization that alters pixel LSB values",
        "lab1_q": "An uncompressed 800x600 RGB PNG image hides 1 bit in each R, G, and B channel per pixel. How many total bits can be embedded across all pixels? (Compute 800 * 600 * 3):",
        "lab1_ans": "1440000",
        "lab2_q": "What is the standard 4-character acronym for 'High Efficiency Video Coding' (H.265)?",
        "lab2_ans": "HEVC"
    },
    "Lesson 24: Machine Learning Categorical Encoding (One-Hot, Label & Target)": {
        "num": 24,
        "track": "Track 5: Encoding Standards & Web Security",
        "title": "Machine Learning Categorical Encoding (One-Hot, Label & Target)",
        "overview": (
            "Machine Learning models (Neural Networks, SVMs, Linear Regression) require numerical tensors rather than raw text strings. "
            "1) One-Hot Encoding creates K binary columns (0 or 1) for K distinct categories, avoiding artificial ordering. "
            "2) Label / Ordinal Encoding assigns each category a fixed integer (0, 1, 2...), ideal for ranked features (Low=0, Medium=1, High=2). "
            "3) Target Encoding replaces a category with the mean of the target variable y for that category, compactly handling high-cardinality features."
        ),
        "formula": "One-Hot(c_i) = [0, ..., 1 (at index i), ..., 0] | TargetEnc(c) = Mean(y | X == c)",
        "example": "Categories ['TCP', 'UDP', 'ICMP'] -> One-Hot for 'UDP' is [0, 1, 0]. If 4 out of 5 'UDP' packets were attacks (y=1), TargetEnc('UDP') = 4/5 = 0.8.",
        "q1_q": "Which encoding represents each category as a binary vector of 0s and a single 1?",
        "q1_opts": ["One-Hot Encoding", "Target Encoding", "URL Percent Encoding", "Atbash Cipher"],
        "q1_ans": "One-Hot Encoding",
        "q2_q": "How does Target Encoding transform a categorical feature?",
        "q2_opts": [
            "Replaces the category with the mean (average) of the target variable for that category",
            "Converts text into 7-bit ASCII hex bytes",
            "Compresses video frames using H.265",
            "Hashes the category with MD5"
        ],
        "q2_ans": "Replaces the category with the mean (average) of the target variable for that category",
        "lab1_q": "A firewall dataset has 3 protocol categories in order: ['HTTP', 'SSH', 'DNS']. Write the 3-digit One-Hot binary vector for 'SSH' (Format: 010):",
        "lab1_ans": "010",
        "lab2_q": "In a fraud detection dataset, category 'Night_Login' appears 10 times, and 7 of those had Fraud=1 (while 3 had Fraud=0). What is the Target Encoded decimal value for 'Night_Login'? (Format: 0.7):",
        "lab2_ans": "0.7"
    },
    "Lesson 25: Web Security — SQL Injection (SQLi) & Parameterized Defense": {
        "num": 25,
        "track": "Track 5: Encoding Standards & Web Security",
        "title": "Web Security — SQL Injection (SQLi) & Parameterized Defense",
        "overview": (
            "SQL Injection (SQLi) occurs when untrusted user input is concatenated directly into a database query string, allowing an attacker to alter the SQL syntax tree. "
            "The classic payload \"' OR '1'='1' --\" forces the WHERE clause to evaluate to TRUE for every row, bypassing authentication. "
            "Defense-in-depth requires Prepared Statements (Parameterized Queries using '?' placeholders), where the database treats user input strictly as literal data rather than executable SQL commands."
        ),
        "formula": "Vulnerable: \"SELECT * FROM users WHERE user='\" + inp + \"'\" | Secure: cursor.execute(\"SELECT * FROM users WHERE user = ?\", (inp,))",
        "example": "Input: admin' -- -> Query becomes: SELECT * FROM users WHERE user='admin' -- AND pass='...' (the '--' comments out the password check!).",
        "q1_q": "What is the primary root cause of an SQL Injection (SQLi) vulnerability?",
        "q1_opts": [
            "Concatenating untrusted user input directly into dynamic SQL query strings",
            "Using HTTPS TLS 1.3 encryption",
            "Hashing passwords with PBKDF2-HMAC-SHA256",
            "Using PNG images instead of JPEG"
        ],
        "q1_ans": "Concatenating untrusted user input directly into dynamic SQL query strings",
        "q2_q": "What is the industry-standard defense that completely neutralizes SQL Injection?",
        "q2_opts": [
            "Prepared Statements (Parameterized Queries)",
            "Hiding the login page URL",
            "Encoding the database in ROT13",
            "Client-side CSS styling"
        ],
        "q2_ans": "Prepared Statements (Parameterized Queries)",
        "lab1_q": "In SQL, which two-character sequence is used to start an inline comment that ignores the rest of the query line (such as the password check)?",
        "lab1_ans": "--",
        "lab2_q": "What boolean value (TRUE or FALSE) does the injected condition ('1'='1' OR 'a'='b') evaluate to?",
        "lab2_ans": "TRUE"
    },
    "Lesson 26: JSON Web Tokens (JWT) & HMAC-SHA256 API Authentication": {
        "num": 26,
        "track": "Track 5: Encoding Standards & Web Security",
        "title": "JSON Web Tokens (JWT) & HMAC-SHA256 API Authentication",
        "overview": (
            "JSON Web Tokens (JWT, RFC 7519) provide stateless authentication across modern microservices. "
            "A JWT consists of 3 dot-separated Base64URL-encoded parts: Header.Payload.Signature. "
            "IMPORTANT: The Header and Payload are merely Base64URL-encoded (NOT encrypted—anyone can decode and read them!). "
            "Security relies entirely on the cryptographic Signature (e.g., HMAC-SHA256 or RS256), which prevents attackers from tampering with the payload (such as changing 'role':'user' to 'role':'admin')."
        ),
        "formula": "JWT = Base64URL(Header) + '.' + Base64URL(Payload) + '.' + HMAC_SHA256(Header.Payload, Secret_Key)",
        "example": "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiaGlldSJ9.Signature -> Decoding the middle part reveals JSON: {\"user\":\"hieu\"}.",
        "q1_q": "Can anyone without the secret key read the claims inside a standard signed JWT payload?",
        "q1_opts": [
            "Yes, because the payload is only Base64URL-encoded (signed for integrity, not encrypted for secrecy)",
            "No, Base64URL is an unbreakable quantum encryption",
            "Only if they have a quantum computer",
            "No, JWT payloads are hashed one-way with SHA-256"
        ],
        "q1_ans": "Yes, because the payload is only Base64URL-encoded (signed for integrity, not encrypted for secrecy)",
        "q2_q": "How many dot-separated sections make up a standard JWT string?",
        "q2_opts": ["3 sections (Header.Payload.Signature)", "2 sections", "4 sections", "16 sections"],
        "q2_ans": "3 sections (Header.Payload.Signature)",
        "lab1_q": "Decode this Base64 JWT payload segment to find the role value: 'eyJyb2xlIjoiYWRtaW4ifQ==' (Enter the 5-letter role value only):",
        "lab1_ans": "admin",
        "lab2_q": "In the notorious JWT 'alg: none' vulnerability, what signature algorithm name did attackers set in the header to bypass signature verification?",
        "lab2_ans": "none"
    },
    "Lesson 27: Network Security — TLS 1.3 Handshake, PKI & Forward Secrecy": {
        "num": 27,
        "track": "Track 6: Advanced Cryptography & AI Security",
        "title": "Network Security — TLS 1.3 Handshake, PKI & Forward Secrecy",
        "overview": (
            "Transport Layer Security (TLS 1.3) secures HTTPS traffic across the internet in a 1-RTT handshake. "
            "It combines 3 cryptographic primitives: 1) Ephemeral Diffie-Hellman (ECDHE) for key exchange, 2) X.509 Digital Certificates (PKI) signed by a Certificate Authority (CA) to authenticate the server and prevent Man-in-the-Middle (MitM) attacks, and 3) AEAD Symmetric Ciphers (AES-GCM or ChaCha20-Poly1305) for fast bulk encryption. "
            "ECDHE provides Perfect Forward Secrecy (PFS): even if the server's long-term private key is stolen years later, past recorded sessions cannot be decrypted."
        ),
        "formula": "TLS 1.3 = ECDHE (Forward-Secret Key Exchange) + X.509/ECDSA (Server Auth) + AES-256-GCM (Authenticated Encryption)",
        "example": "Every HTTPS connection generates a fresh throwaway ECDHE keypair that is destroyed immediately after the session ends.",
        "q1_q": "What security property ensures that compromising a server's long-term private key today does NOT allow decrypting past recorded network traffic?",
        "q1_opts": [
            "Perfect Forward Secrecy (PFS) via Ephemeral Diffie-Hellman (ECDHE)",
            "Base64 Encoding",
            "ECB Block Cipher Mode",
            "Static RSA Key Transport"
        ],
        "q1_ans": "Perfect Forward Secrecy (PFS) via Ephemeral Diffie-Hellman (ECDHE)",
        "q2_q": "How many network Round-Trip Times (RTT) does a fresh TLS 1.3 handshake require before encrypted application data can be sent?",
        "q2_opts": ["1-RTT (and 0-RTT for resumed sessions)", "4-RTT", "10-RTT", "100-RTT"],
        "q2_ans": "1-RTT (and 0-RTT for resumed sessions)",
        "lab1_q": "What is the standard TCP port number used by HTTPS (HTTP over TLS)?",
        "lab1_ans": "443",
        "lab2_q": "In PKI, what is the 2-letter acronym for the trusted entity that issues and signs X.509 digital certificates?",
        "lab2_ans": "CA"
    },
    "Lesson 28: Elliptic Curve Cryptography (ECC — Curve25519 & ECDSA)": {
        "num": 28,
        "track": "Track 6: Advanced Cryptography & AI Security",
        "title": "Elliptic Curve Cryptography (ECC — Curve25519 & ECDSA)",
        "overview": (
            "Elliptic Curve Cryptography (ECC) achieves the same security level as RSA using drastically smaller keys by operating on points (x, y) satisfying y^2 = x^3 + ax + b (mod p). "
            "Security relies on the Elliptic Curve Discrete Logarithm Problem (ECDLP): given base point G and public point Q = k * G (adding G to itself k times), it is computationally infeasible to recover the private scalar k. "
            "A 256-bit ECC key provides ~128-bit security, equivalent to a bulky 3072-bit RSA key!"
        ),
        "formula": "Weierstrass Curve: y^2 ≡ x^3 + ax + b (mod p) | Public Key: Q = k · G (Scalar Point Multiplication)",
        "example": "Bitcoin/Ethereum use secp256k1 (y^2 = x^3 + 7); Signal, WireGuard & SSH use Curve25519 / Ed25519 (256-bit keys).",
        "q1_q": "What mathematical hard problem underpins the security of Elliptic Curve Cryptography (ECC)?",
        "q1_opts": [
            "Elliptic Curve Discrete Logarithm Problem (ECDLP): finding scalar k from Q = k * G",
            "Multiplying two small integers",
            "Counting vowel frequencies in English text",
            "Inverting a Caesar cipher"
        ],
        "q1_ans": "Elliptic Curve Discrete Logarithm Problem (ECDLP): finding scalar k from Q = k * G",
        "q2_q": "A 256-bit ECC key provides comparable classical security to roughly what size RSA key?",
        "q2_opts": ["3072-bit RSA key", "64-bit RSA key", "128-bit RSA key", "256-bit RSA key"],
        "q2_ans": "3072-bit RSA key",
        "lab1_q": "On the curve y^2 = x^3 + 7 (mod 11), evaluate the right-hand side (x^3 + 7) mod 11 when x = 2:",
        "lab1_ans": "4",
        "lab2_q": "How many bits is a standard Ed25519 / Curve25519 private key?",
        "lab2_ans": "256"
    },
    "Lesson 29: Zero-Knowledge Proofs (ZKP — Schnorr Protocol & zk-SNARKs)": {
        "num": 29,
        "track": "Track 6: Advanced Cryptography & AI Security",
        "title": "Zero-Knowledge Proofs (ZKP — Schnorr Protocol & zk-SNARKs)",
        "overview": (
            "A Zero-Knowledge Proof (ZKP) allows a Prover (Peggy) to mathematically convince a Verifier (Victor) that she knows a secret witness w (such as a password or private key) WITHOUT revealing w or any information about it! "
            "Every ZKP must satisfy 3 properties: 1) Completeness (an honest prover convinces an honest verifier), 2) Soundness (a cheating prover cannot fake the proof except with negligible probability), and 3) Zero-Knowledge (the verifier learns nothing beyond the statement's truth)."
        ),
        "formula": "Schnorr ZKP: Commit R = r·G -> Challenge c -> Response s = (r + c·k) mod q -> Verify: s·G == R + c·Q",
        "example": "Alibaba Cave & zk-SNARKs in privacy blockchains/digital IDs: prove 'Age >= 18' without revealing your birth date!",
        "q1_q": "Which of the following is NOT one of the three core mathematical properties of a Zero-Knowledge Proof?",
        "q1_opts": [
            "Key Exposure (sending the raw secret password in plaintext to the verifier)",
            "Completeness",
            "Soundness",
            "Zero-Knowledge"
        ],
        "q1_ans": "Key Exposure (sending the raw secret password in plaintext to the verifier)",
        "q2_q": "What does a Zero-Knowledge Proof allow a Prover to demonstrate to a Verifier?",
        "q2_opts": [
            "That they know a secret value without revealing the secret itself",
            "That SHA-256 is a reversible cipher",
            "That ASCII uses 32 bits per character",
            "That SQL Injection is impossible"
        ],
        "q2_ans": "That they know a secret value without revealing the secret itself",
        "lab1_q": "In a modular Schnorr proof with q = 23, random nonce r = 7, challenge c = 2, and secret key k = 5, compute response s = (r + c * k) mod 23:",
        "lab1_ans": "17",
        "lab2_q": "If a cheating prover has a 1/2 (50%) chance of guessing the verifier's binary challenge in 1 round, what is the denominator X of their success probability (1/X) after 10 independent rounds? (Compute 2^10):",
        "lab2_ans": "1024"
    },
    "Lesson 30: AI Security, Prompt Guardrails & Homomorphic Encryption (FHE)": {
        "num": 30,
        "track": "Track 6: Advanced Cryptography & AI Security",
        "title": "AI Security, Prompt Guardrails & Homomorphic Encryption (FHE)",
        "overview": (
            "Modern AI systems face two critical security frontiers: "
            "1) Adversarial AI & Data Poisoning: Attackers attempt Prompt Injection (jailbreaking instructions) or Data Poisoning (injecting false training samples). Defenses require strict Domain Guardrails, Admin-verified training queues, and cryptographic provenance. "
            "2) Fully Homomorphic Encryption (FHE): Enables cloud servers to run AI inference directly on encrypted ciphertexts Enc(x) without ever decrypting them: Dec(Enc(a) ⊕ Enc(b)) = a + b!"
        ),
        "formula": "Additive Homomorphism: Enc(x) · Enc(y) = Enc(x + y) | Multiplicative (RSA): (M1^e)(M2^e) mod N = (M1·M2)^e mod N",
        "example": "A hospital encrypts patient X-rays with FHE and sends them to a cloud AI; the AI returns an encrypted diagnosis without ever seeing the raw image.",
        "q1_q": "What makes Fully Homomorphic Encryption (FHE) revolutionary for cloud AI privacy?",
        "q1_opts": [
            "It allows performing arbitrary computations (addition & multiplication) directly on encrypted data without decrypting it",
            "It replaces binary 0 and 1 with base-10 numbers",
            "It makes passwords unnecessary",
            "It converts PNG images into WAV audio"
        ],
        "q1_ans": "It allows performing arbitrary computations (addition & multiplication) directly on encrypted data without decrypting it",
        "q2_q": "What is 'Data Poisoning' in Machine Learning and AI systems?",
        "q2_opts": [
            "Injecting malicious or corrupted samples into the AI's training dataset to manipulate its behavior",
            "Encrypting a hard drive with AES-256",
            "Using UTF-8 character encoding on a website",
            "Solving a 9x9 Sudoku puzzle"
        ],
        "q2_ans": "Injecting malicious or corrupted samples into the AI's training dataset to manipulate its behavior",
        "lab1_q": "Textbook RSA is multiplicatively homomorphic: Enc(m1) * Enc(m2) mod N = Enc(m1 * m2). If Enc(2) = 8 and Enc(3) = 27 under N = 35, compute (8 * 27) mod 35 to get Enc(6):",
        "lab1_ans": "6",
        "lab2_q": "What 3-letter acronym stands for 'Fully Homomorphic Encryption'?",
        "lab2_ans": "FHE"
    }
}


def inject_expanded_curriculum(curriculum_dict: dict):
    """
    Tự động tiêm thêm 10 Bài học Đại học nâng cao (Lesson 21 -> Lesson 30) vào LESSONS_CURRICULUM
    của streamlit_app.py với độ tương thích Schema 100% (không bao giờ lỗi KeyError).
    """
    if not isinstance(curriculum_dict, dict) or not curriculum_dict:
        return

    sample_lesson = next(iter(curriculum_dict.values()))
    sample_id = str(sample_lesson.get("id", "M01"))
    id_prefix = "M" if sample_id.startswith("M") else "L"

    for mod_key, mod_data in EXPANDED_MODULES_21_TO_30.items():
        if mod_key not in curriculum_dict:
            m_num = mod_data["num"]
            cloned = dict(sample_lesson)
            cloned.update({
                "id": f"{id_prefix}{m_num:02d}",
                "track": mod_data["track"],
                "title": mod_data["title"],
                "overview": mod_data["overview"],
                "formula": mod_data["formula"],
                "example": mod_data["example"],
                "q1_q": mod_data["q1_q"],
                "q1_opts": mod_data["q1_opts"],
                "q1_ans": mod_data["q1_ans"],
                "q2_q": mod_data["q2_q"],
                "q2_opts": mod_data["q2_opts"],
                "q2_ans": mod_data["q2_ans"],
                "lab1_q": mod_data["lab1_q"],
                "lab1_ans": mod_data["lab1_ans"],
                "lab2_q": mod_data["lab2_q"],
                "lab2_ans": mod_data["lab2_ans"]
            })
            curriculum_dict[mod_key] = cloned


# ==============================================================================
# 3. KHO TRI THỨC CHUYÊN SÂU ĐƯỢC HUẤN LUYỆN SẴN (PRE-TRAINED DEEP KNOWLEDGE BASE)
# ==============================================================================
CORE_KNOWLEDGE_BASE = [
    {
        "id": "KB_BEGINNER_ROADMAP",
        "keywords": [
            "start", "begin", "beginner", "newbie", "roadmap", "learn cybersecurity", "get into cybersecurity",
            "how to learn", "where to start", "anfangen", "cybersicherheit", "einsteiger", "bắt đầu", "người mới", "lộ trình"
        ],
        "en": (
            "🗺️ **Complete 6-Track University Roadmap to Cybersecurity & Cryptography (30 Modules):**\n"
            "1. **Track 1 — Classical Cryptography (`Modules 01–03`):** Encoding vs. Encryption vs. Hashing, Caesar, Affine, Atbash, Vigenère & Frequency Analysis.\n"
            "2. **Track 2 — Low-Level Computer Systems (`Modules 04–09`):** Bits, Nibbles, Bytes, Hexadecimal, Two's Complement signed integers, Bitwise XOR/Shifts, Little-Endian memory & x86-64 Assembly.\n"
            "3. **Track 3 — Mathematical Foundations (`Modules 10–13`):** Modular Arithmetic, Euclidean GCD, Modular Inverse, Euler's Totient & Shannon's Perfect Secrecy (OTP).\n"
            "4. **Track 4 — Modern & Post-Quantum Crypto (`Modules 14–20`):** SHA-256, AES-256, RSA Public-Key, LSB Steganography & Post-Quantum Lattice Cryptography.\n"
            "5. **Track 5 — Encoding Standards & Web Security (`Modules 21–26`):** `UTF-8/ASCII`, `Base64/URL/HTML XSS Defense`, `Multimedia Codecs`, `ML One-Hot/Target Encoding`, `SQL Injection` & `JWT Tokens`.\n"
            "6. **Track 6 — Advanced Protocols & AI Security (`Modules 27–30`):** `TLS 1.3 & PKI`, `Elliptic Curve (ECC)`, `Zero-Knowledge Proofs (ZKP)` & `Homomorphic Encryption (FHE)`."
        ),
        "vi": (
            "🗺️ **Lộ Trình 6 Track Đại Học Về An Ninh Mạng & Mật Mã Học (30 Bài Học):**\n"
            "1. **Track 1 (`Bài 01–03`):** Phân biệt Encoding/Encryption/Hashing, Caesar, Affine, Vigenère.\n"
            "2. **Track 2 (`Bài 04–09`):** Hệ nhị phân (Bits, Bytes, Hex), Số bù 2 (Two's Complement), Bitwise XOR/Shift, Endianness & Assembly.\n"
            "3. **Track 3 (`Bài 10–13`):** Toán học Modulo, GCD, Nghịch đảo Modulo, Hàm Euler & One-Time Pad.\n"
            "4. **Track 4 (`Bài 14–20`):** SHA-256, AES-256, RSA, Giấu tin Steganography & Mật mã Lượng tử.\n"
            "5. **Track 5 (`Bài 21–26`):** Chuẩn `UTF-8/ASCII`, `Base64/URL/HTML chống XSS`, `Video/Audio Codecs`, `One-Hot/Target ML`, `SQL Injection` & `JWT`.\n"
            "6. **Track 6 (`Bài 27–30`):** `TLS 1.3 & PKI`, `Đường cong Elliptic (ECC)`, `Zero-Knowledge Proofs (ZKP)` & `Mã hóa Đồng cấu (FHE)`."
        )
    },
    {
        "id": "KB_CHAR_ENC",
        "keywords": ["character encoding", "mã hóa ký tự", "utf-8", "utf8", "utf-16", "utf-32", "ascii", "unicode", "7-bit", "lesson 21", "m21"],
        "en": (
            "🔤 **1. Character Encoding (`Lesson 21` — Text-to-Binary Representation):**\n"
            "- **UTF-8:** Dominates ~90% of all websites. Variable-length (1 to 4 bytes per character), supports all languages, and is 100% backward-compatible with ASCII.\n"
            "- **UTF-16 / UTF-32:** Uses 2 to 4 bytes per character for internal OS and runtime memory.\n"
            "- **ASCII:** Foundational 7-bit encoding (128 characters, `0–127`) for English letters (`A=65`, `a=97`), digits (`0=48`), and control codes."
        ),
        "vi": (
            "🔤 **1. Mã hóa ký tự (`Bài 21` — Character Encoding):**\n"
            "- **UTF-8:** Chiếm gần 90% các trang web. Dùng 1–4 bytes/ký tự, hỗ trợ đa ngôn ngữ và tương thích ngược hoàn hảo với ASCII.\n"
            "- **UTF-16 / UTF-32:** Dùng 2 đến 4 byte cho mỗi ký tự trong lưu trữ nội bộ hệ điều hành.\n"
            "- **ASCII:** Bộ mã hóa 7-bit cơ bản gồm 128 ký tự (`0–127`) cho chữ cái tiếng Anh (`A=65`, `a=97`) và chữ số (`0=48`)."
        )
    },
    {
        "id": "KB_DATA_BIN_ENC",
        "keywords": ["base64", "url encode", "percent encoding", "html encode", "xss", "entity", "%20", "jwt", "data uri", "nhị phân sang văn bản", "binary encoding", "lesson 22", "m22"],
        "en": (
            "🔄 **2. Data & Binary-to-Text Encoding (`Lesson 22`):**\n"
            "- **Base64:** Groups 3 bytes (24 bits) into four 6-bit ASCII characters. Used in HTML `Data URIs`, MIME email attachments, and `JWT` tokens.\n"
            "- **URL Encode (Percent Encoding):** Converts spaces and special URL symbols into safe `%XX` hex (e.g., space becomes `%20`).\n"
            "- **HTML Encode:** Converts `<`, `>`, `&` into HTML entities (`&lt;`, `&gt;`, `&amp;`) to prevent **Cross-Site Scripting (XSS)** attacks."
        ),
        "vi": (
            "🔄 **2. Mã hóa dữ liệu / Nhị phân sang văn bản (`Bài 22`):**\n"
            "- **Base64:** Chia mỗi 3 bytes (24 bits) thành 4 ký tự ASCII 6-bit. Dùng cho HTML `Data URI`, gửi file qua Email và `JWT`.\n"
            "- **URL Encode (Percent Encoding):** Chuyển ký tự đặc biệt và dấu cách thành `%20` an toàn trên trình duyệt.\n"
            "- **HTML Encode:** Chuyển `<`, `>`, `&` thành `&lt;`, `&gt;`, `&amp;` để chống tấn công **XSS**."
        )
    },
    {
        "id": "KB_MULTIMEDIA_ENC",
        "keywords": ["multimedia encoding", "mã hóa đa phương tiện", "codec", "h.264", "h.265", "hevc", "avc", "vp9", "av1", "mp4", "mkv", "mp3", "aac", "flac", "ogg", "video", "audio", "lesson 23", "m23"],
        "en": (
            "🎬 **3. Multimedia Encoding (`Lesson 23` — Video & Audio Codecs):**\n"
            "- **Video Codecs & Containers:** `H.264 (AVC)`, `H.265 (HEVC)`, `VP9`, `AV1`, packaged in `MP4` or `MKV`.\n"
            "- **Audio Formats:** Lossy (`MP3`, `AAC`, `OGG`) vs. Lossless (`FLAC`, `WAV PCM`).\n"
            "- 💡 *Steganography Rule:* Always use **Lossless (`PNG`, `WAV`, `FLAC`)** for LSB steganography because lossy compression (`JPG`, `MP3`) destroys least significant bits!"
        ),
        "vi": (
            "🎬 **3. Mã hóa đa phương tiện (`Bài 23` — Multimedia Encoding):**\n"
            "- **Video:** `H.264 (AVC)`, `H.265 (HEVC)`, `VP9`, `AV1`, `MP4`, `MKV`.\n"
            "- **Âm thanh:** Nén có hao hụt (`MP3`, `AAC`, `OGG`) và nén bảo toàn (`FLAC`, `WAV`).\n"
            "- 💡 *Quy tắc Steganography:* Phải dùng chuẩn Lossless (`PNG`, `WAV`, `FLAC`) khi giấu bit LSB!"
        )
    },
    {
        "id": "KB_ML_ENC",
        "keywords": ["categorical encoding", "machine learning", "khoa học dữ liệu", "one-hot", "one hot", "label encoding", "ordinal encoding", "target encoding", "học máy", "lesson 24", "m24"],
        "en": (
            "🤖 **4. Machine Learning Categorical Encoding (`Lesson 24`):**\n"
            "- **One-Hot Encoding:** Creates binary (`0` or `1`) columns for each category.\n"
            "- **Label / Ordinal Encoding:** Maps each category to a fixed integer (`0, 1, 2...`).\n"
            "- **Target Encoding:** Replaces a category with the statistical mean of the target variable for that category."
        ),
        "vi": (
            "🤖 **4. Mã hóa trong Khoa học dữ liệu / Machine Learning (`Bài 24`):**\n"
            "- **One-Hot Encoding:** Tạo các cột nhị phân (`0` hoặc `1`) tương ứng với từng danh mục.\n"
            "- **Label / Ordinal Encoding:** Gán mỗi giá trị chữ bằng một số nguyên cố định (`0, 1, 2...`).\n"
            "- **Target Encoding:** Thay thế danh mục bằng giá trị trung bình của biến mục tiêu (target)."
        )
    },
    {
        "id": "KB_WEB_SEC_SQLI_JWT",
        "keywords": ["sql", "sqli", "sql injection", "prepared statement", "jwt", "json web token", "hmac", "bearer", "lesson 25", "lesson 26", "m25", "m26"],
        "en": (
            "🛡️ **Web Security — SQL Injection (`Lesson 25`) & JWT Authentication (`Lesson 26`):**\n"
            "- **SQL Injection (SQLi):** Caused by concatenating raw user input into SQL strings (e.g., `' OR '1'='1' --`). Defended 100% by **Prepared Statements (Parameterized Queries)**.\n"
            "- **JSON Web Token (JWT):** Structured as `Header.Payload.Signature` (Base64URL-encoded). The payload is readable by anyone; security relies on the **HMAC-SHA256 / RS256 Signature** to prevent tampering."
        ),
        "vi": (
            "🛡️ **Bảo mật Web — SQL Injection (`Bài 25`) & Xác thực JWT (`Bài 26`):**\n"
            "- **SQL Injection (SQLi):** Xảy ra khi nối trực tiếp chuỗi người dùng nhập vào câu lệnh SQL (`' OR '1'='1' --`). Phòng chống triệt để bằng **Prepared Statements (Parameterized Queries)**.\n"
            "- **JSON Web Token (JWT):** Gồm 3 phần `Header.Payload.Signature` (mã hóa Base64URL). Payload không được mã hóa bí mật mà được bảo vệ chống sửa đổi nhờ **Chữ ký số HMAC-SHA256 / RS256**."
        )
    },
    {
        "id": "KB_ADV_CRYPTO_TLS_ECC_ZKP_FHE",
        "keywords": ["tls", "https", "pki", "certificate", "forward secrecy", "pfs", "ecc", "elliptic", "curve25519", "ecdsa", "zkp", "zero-knowledge", "snark", "schnorr", "homomorphic", "fhe", "lesson 27", "lesson 28", "lesson 29", "lesson 30"],
        "en": (
            "🔬 **Advanced Cryptography (`Lessons 27–30` — TLS 1.3, ECC, ZKP & Homomorphic Encryption):**\n"
            "- **TLS 1.3 & PFS (`Lesson 27`):** Uses Ephemeral Diffie-Hellman (`ECDHE`) for Perfect Forward Secrecy, `X.509 CA Certificates` for server authentication, and `AES-GCM` for encryption.\n"
            "- **Elliptic Curve Cryptography (`Lesson 28`):** Based on $y^2 \\equiv x^3 + ax + b \\pmod p$ and the ECDLP ($Q = k \\cdot G$). A **256-bit ECC key** equals **3072-bit RSA** security.\n"
            "- **Zero-Knowledge Proofs (`Lesson 29`):** Proves knowledge of a secret without revealing it (*Completeness, Soundness, Zero-Knowledge*).\n"
            "- **Fully Homomorphic Encryption (`Lesson 30`):** Allows computing directly on encrypted ciphertexts $\\text{Enc}(a) \\oplus \\text{Enc}(b) = \\text{Enc}(a+b)$ without decrypting."
        ),
        "vi": (
            "🔬 **Mật mã học Hiện đại (`Bài 27–30` — TLS 1.3, ECC, ZKP & Mã hóa Đồng cấu FHE):**\n"
            "- **TLS 1.3 & PFS (`Bài 27`):** Dùng `ECDHE` để đạt Độ mật chuyển tiếp hoàn hảo (Perfect Forward Secrecy), chứng chỉ số `X.509 CA` và `AES-GCM`.\n"
            "- **Đường cong Elliptic ECC (`Bài 28`):** Dựa trên $y^2 \\equiv x^3 + ax + b \\pmod p$ ($Q = k \\cdot G$). Khóa **ECC 256-bit** mạnh ngang khóa **RSA 3072-bit**.\n"
            "- **Zero-Knowledge Proofs (`Bài 29`):** Chứng minh bạn biết bí mật mà không tiết lộ bí mật đó (*Completeness, Soundness, Zero-Knowledge*).\n"
            "- **Mã hóa Đồng cấu FHE (`Bài 30`):** Cho phép AI tính toán trực tiếp trên dữ liệu đang mã hóa mà không cần giải mã."
        )
    },
    {
        "id": "KB_BINARY_BITS",
        "keywords": ["nhị phân", "binary", "bit", "nibble", "byte", "hex", "hexadecimal", "bù 2", "two's complement", "bitwise", "xor", "and", "shift", "dịch bit", "endian", "little-endian"],
        "en": (
            "💻 **Core Binary, Bits & Computer Architecture (`Lessons 04–09`):**\n"
            "- **1 Bit:** `0` or `1` | **1 Nibble (4 bits):** `0..15` (1 Hex digit `0..F`) | **1 Byte (8 bits):** $2^8 = 256$ values (`0..255`) with weights `128, 64, 32, 16, 8, 4, 2, 1`.\n"
            "- **Two's Complement (Signed Integers):** MSB has weight `-128`. To negate $+X \\rightarrow -X$: invert all bits (`~X`) and add `1`.\n"
            "- **Bitwise Operations:** `AND (&)` masks bits (`R & 1` extracts LSB), `XOR (^)` is self-inverting (`(P ^ K) ^ K = P`), `X << k` multiplies by $2^k$, `X >> k` divides by $2^k$."
        ),
        "vi": (
            "💻 **Kiến thức Cốt lõi về Hệ Nhị Phân, Bits & Kiến trúc Máy tính (`Bài 04–09`):**\n"
            "- **1 Bit:** `0` hoặc `1` | **1 Nibble (4 bits):** `0..15` (1 chữ số Hex `0..F`) | **1 Byte (8 bits):** $2^8 = 256$ giá trị (`0..255`).\n"
            "- **Số nguyên có dấu Bù 2 (Two's Complement):** Đảo toàn bộ các bit (`~X`) rồi cộng thêm `1`.\n"
            "- **Phép toán Bitwise:** `AND (&)` lọc bit; `XOR (^)` khả nghịch (`A ^ K ^ K = A`); Dịch trái `X << k` nhân với $2^k$, dịch phải `X >> k` chia nguyên cho $2^k$."
        )
    }
]

ALLOWED_DOMAIN_KEYWORDS = {
    "cyber", "cybersecurity", "cybersicherheit", "sicherheit", "security", "bảo mật", "an ninh mạng",
    "mật mã", "mã hóa", "giải mã", "cipher", "crypto", "cryptography", "kryptographie", "verschlüsselung", "encode", "encoding", "decode",
    "utf", "ascii", "unicode", "base64", "url", "html", "xss", "percent", "multimedia", "video", "audio",
    "h.264", "h.265", "hevc", "av1", "vp9", "mp3", "mp4", "flac", "wav", "png", "lsb", "steganography", "giấu tin",
    "one-hot", "onehot", "label", "ordinal", "target", "machine learning", "học máy", "data", "dữ liệu",
    "nhị phân", "binary", "binär", "bit", "bits", "byte", "bytes", "nibble", "hex", "hexadecimal", "decimal", "thập phân",
    "bù 2", "complement", "overflow", "bitwise", "xor", "and", "shift", "dịch", "assembly", "rax", "mov", "shl", "shr",
    "endian", "little-endian", "big-endian", "caesar", "rot13", "atbash", "affine", "vigenere", "rail-fence", "transposition",
    "modulo", "mod", "inverse", "nghịch đảo", "coprime", "frequency", "tần suất", "otp", "one-time pad", "shannon", "entropy",
    "sha", "sha-256", "hash", "băm", "salt", "rainbow", "aes", "ecb", "gcm", "cbc", "rsa", "diffie", "public key", "private key",
    "prime", "totient", "phi", "quantum", "lượng tử", "qubit", "shor", "grover", "lattice", "kyber", "enigma", "elliptic", "ecc",
    "zero-knowledge", "zkp", "snark", "schnorr", "homomorphic", "fhe", "block cipher", "stream cipher", "kerckhoffs", "hmac", "digital signature",
    "tls", "ssl", "https", "pki", "sql", "sqli", "injection", "jwt", "token", "crack", "brute",
    "bài", "lesson", "module", "track", "lab", "quiz", "câu hỏi", "đáp án", "hint", "gợi ý", "sudoku", "ctf", "web", "app",
    "camouflage", "ngụy trang", "morse", "visual", "pháp y", "forensic", "password", "mật khẩu", "key", "khóa",
    "start", "begin", "anfangen", "lernen", "learn", "study", "course", "academy", "roadmap",
    "hello", "hi", "hallo", "bonjour", "hola", "xin chào", "chào", "help", "giúp", "hướng dẫn", "explain", "giải thích", "what", "how", "why"
}

OFF_TOPIC_KEYWORDS = {
    "nấu ăn", "công thức nấu", "phở", "bún bò", "bóng đá", "ngoại hạng anh", "world cup", "messi", "ronaldo",
    "thời tiết", "xổ số", "lô đề", "tử vi", "bói toán", "cung hoàng đạo", "người yêu", "tình yêu", "thất tình",
    "recipe", "cooking", "pasta", "pizza", "football", "soccer", "weather", "horoscope", "astrology", "dating", "boyfriend", "girlfriend",
    "kochen", "rezept", "fußball", "wetter"
}

AUTO_HARVEST_TOPICS = [
    ("Enigma machine", ["enigma", "rotor", "turing"]),
    ("Elliptic-curve cryptography", ["ecc", "elliptic", "curve"]),
    ("Diffie–Hellman key exchange", ["diffie", "hellman", "dh", "key exchange"]),
    ("Homomorphic encryption", ["homomorphic", "fhe", "đồng cấu"]),
    ("Zero-knowledge proof", ["zkp", "zero-knowledge", "zero knowledge"]),
    ("Digital signature", ["digital signature", "chữ ký số", "ecdsa"]),
    ("JSON Web Token", ["jwt", "json web token", "bearer"]),
    ("SQL injection", ["sqli", "sql injection", "prepared statement"]),
    ("Transport Layer Security", ["tls", "https", "handshake"]),
    ("Post-quantum cryptography", ["post-quantum", "pqc", "kyber", "dilithium", "lattice"])
]


def load_ai_memory() -> dict:
    if not os.path.exists(AI_MEMORY_FILE):
        default_mem = {
            "admin_pin_hash": DEFAULT_ADMIN_PIN_HASH,
            "gemini_api_key": "",
            "learned_facts": [
                {
                    "topic": "Post-Quantum Cryptography & AI Security (2026 Standard)",
                    "keywords": ["trend", "2026", "ai security", "ml-kem", "post-quantum", "xu hướng"],
                    "content": "Modern cryptographic infrastructure is migrating to NIST Post-Quantum standards (ML-KEM / CRYSTALS-Kyber for key encapsulation and ML-DSA for digital signatures) combined with AI-driven anomaly detection and strict Anti-Data-Poisoning guardrails.",
                    "taught_by": "Admin_Core",
                    "timestamp": "2026-10-25 UTC"
                }
            ],
            "pending_suggestions": []
        }
        with open(AI_MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(default_mem, f, ensure_ascii=False, indent=4)
        return default_mem
    try:
        with open(AI_MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "admin_pin_hash" not in data:
                data["admin_pin_hash"] = DEFAULT_ADMIN_PIN_HASH
            if "pending_suggestions" not in data:
                data["pending_suggestions"] = []
            return data
    except Exception:
        return {"admin_pin_hash": DEFAULT_ADMIN_PIN_HASH, "learned_facts": [], "pending_suggestions": []}


def save_ai_memory(data: dict):
    with open(AI_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def fetch_wikipedia_crypto_summary(query_term: str, lang_code: str = "en") -> tuple[bool, str, str]:
    clean_q = re.sub(
        r'^(what is|what are|explain|define|how does|tell me about|là gì|giải thích|khái niệm|was ist|qu\'est-ce que|qué es)\s+',
        '', query_term.strip(), flags=re.IGNORECASE
    ).strip(" ?!.,")
    if len(clean_q) < 2:
        return False, "", ""

    wiki_lang = lang_code.split("-")[0] if lang_code else "en"
    if wiki_lang not in ["en", "vi", "de", "fr", "es", "ja", "ko", "zh", "ru", "it", "pt"]:
        wiki_lang = "en"

    search_url = f"https://{wiki_lang}.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(clean_q)}&limit=1&namespace=0&format=json"

    try:
        req = urllib.request.Request(search_url, headers={"User-Agent": "USM-CyberMentor/4.0 (HCMUS Educational Suite)"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            search_data = json.loads(resp.read().decode("utf-8"))
            if not search_data or len(search_data) < 2 or not search_data[1]:
                if wiki_lang != "en":
                    return fetch_wikipedia_crypto_summary(clean_q, "en")
                return False, "", ""
            best_title = search_data[1][0]

        sum_url = f"https://{wiki_lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(best_title.replace(' ', '_'))}"
        req_sum = urllib.request.Request(sum_url, headers={"User-Agent": "USM-CyberMentor/4.0 (HCMUS Educational Suite)"})
        with urllib.request.urlopen(req_sum, timeout=4) as resp2:
            sum_data = json.loads(resp2.read().decode("utf-8"))
            extract = sum_data.get("extract", "").strip()
            if len(extract) > 40:
                return True, best_title, extract
    except Exception:
        pass
    return False, "", ""


def call_optional_gemini_llm(query: str, current_lesson: dict, api_key: str) -> str:
    if not api_key:
        return ""
    les_info = f"Current Lesson: {current_lesson.get('id')} - {current_lesson.get('title')}. Overview: {current_lesson.get('overview')}" if current_lesson else "Global 30-Module Security Academy"
    sys_prompt = (
        "You are AI Cyber Mentor v4.0 for the Ultimate Secret Messenger & 30-Module Security Academy platform created by Le Hoang Phu Hieu (FIT-HCMUS). "
        "CRITICAL RULES:\n"
        "1. ALWAYS reply in the EXACT SAME LANGUAGE that the user used in their question.\n"
        "2. If the user asks about something unrelated to Cybersecurity, Cryptography, Encoding (UTF-8, Base64, URL/HTML, Multimedia, ML One-Hot/Target), Binary/Bits, Web Security (SQLi, JWT), or the 30 Security Academy lessons, politely refuse IN THEIR LANGUAGE and remind them to stay on topic.\n"
        f"3. Context: {les_info}"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key.strip()}"
    payload = {
        "contents": [{"parts": [{"text": f"{sys_prompt}\n\nUser Question: {query}"}]}]
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return ""


def is_query_on_topic(original_query: str, english_translated_query: str, mem_db: dict) -> bool:
    combined = f"{original_query} {english_translated_query}".lower()
    if any(bad in combined for bad in OFF_TOPIC_KEYWORDS):
        return False
    if any(good in combined for good in ALLOWED_DOMAIN_KEYWORDS):
        return True
    for fact in mem_db.get("learned_facts", []):
        if any(kw.lower() in combined for kw in fact.get("keywords", [])):
            return True
    if re.search(r'\b[01]{4,}\b|\b0x[0-9a-f]+\b|\bmod\b|<<|>>|\b[ml]\d{2}\b', combined):
        return True
    return False


def try_live_computation(query: str, lang: str) -> str:
    """
    Trình tính toán & giải mã trực tiếp trong khung chat:
    - Chuyển đổi Binary / Hex / Two's Complement
    - Encode / Decode Base64, URL, HTML, UTF-8 Hex
    - Brute-force Caesar Cipher & tính XOR
    """
    q_clean = query.strip()
    low = q_clean.lower()

    # 1. Tính XOR trực tiếp giữa 2 số (VD: "XOR 42 with 15" hoặc "31 xor 12")
    xor_match = re.search(r'(\d+)\s*(?:xor|\^)\s*(\d+)', low)
    if xor_match:
        a, b = int(xor_match.group(1)), int(xor_match.group(2))
        res = a ^ b
        return (
            f"🧮 **Live Bitwise XOR Computation (`{a} ^ {b}`):**\n"
            f"- `{a:3d}` in 8-bit binary = `{a & 0xFF:08b}`\n"
            f"- `{b:3d}` in 8-bit binary = `{b & 0xFF:08b}`\n"
            f"- **Result (`{a} XOR {b}`)** = **`{res}`** (Binary: `{res & 0xFF:08b}`, Hex: `0x{res:02X}`)"
        )

    # 2. Chuyển đổi số thập phân sang Nhị phân & Bù 2
    nums = re.findall(r'\b\d+\b', q_clean)
    if nums and any(k in low for k in ["binary", "nhị phân", "binär", "hex", "bù 2", "complement", "bit"]):
        n = int(nums[0])
        if 0 <= n <= 255:
            twos = f"{(256 - n) & 0xFF:08b}" if n > 0 else "00000000"
            return (
                f"🧮 **Live Binary & Hex Computation for `{n}`:**\n"
                f"- **8-Bit Binary:** `{n:08b}` (High nibble: `{n>>4:04b}`, Low nibble: `{n&15:04b}`)\n"
                f"- **Hexadecimal:** `0x{n:02X}` | **Two's Complement (`-{n}`):** `{twos}`"
            )

    # 3. Giải mã hoặc Mã hóa chuỗi trong dấu ngoặc kép "..."
    quote_match = re.findall(r'["\']([^"\']+)["\']', q_clean)
    if quote_match:
        sample = quote_match[0]
        if any(k in low for k in ["decode", "giải mã", "crack", "caesar"]):
            out_lines = [f"🔓 **Live Decryption & Decoding Analysis for `'{sample}'`:**"]
            # Thử giải mã Base64
            try:
                b64_dec = base64.b64decode(sample).decode("utf-8")
                if all(32 <= ord(c) < 127 for c in b64_dec):
                    out_lines.append(f"- **Base64 Decoded:** `{b64_dec}`")
            except Exception:
                pass
            # Thử giải mã URL
            url_dec = urllib.parse.unquote(sample)
            if url_dec != sample:
                out_lines.append(f"- **URL Decoded:** `{url_dec}`")
            # Nếu là chữ cái, hiển thị 3 shift Caesar phổ biến
            if sample.isalpha() and len(sample) <= 30:
                s3 = "".join(chr((ord(c.upper()) - 65 - 3) % 26 + 65) for c in sample)
                r13 = "".join(chr((ord(c.upper()) - 65 - 13) % 26 + 65) for c in sample)
                out_lines.append(f"- **Caesar (-3 Shift):** `{s3}` | **ROT13:** `{r13}`")
            if len(out_lines) > 1:
                return "\n".join(out_lines)

        if any(k in low for k in ["encode", "mã hóa", "base64", "url", "html", "utf-8", "ascii"]):
            b64 = base64.b64encode(sample.encode("utf-8")).decode("utf-8")
            url_e = urllib.parse.quote(sample)
            html_e = html.escape(sample)
            utf8_hex = " ".join(f"{b:02X}" for b in sample.encode("utf-8"))
            return (
                f"⚡ **Live Encoding Results for `'{sample}'`:**\n"
                f"- **UTF-8 Hex Bytes:** `{utf8_hex}` ({len(sample.encode('utf-8'))} bytes)\n"
                f"- **Base64:** `{b64}` | **URL Encode:** `{url_e}` | **HTML Encode:** `{html_e}`"
            )
    return ""


def search_across_30_modules(combined_low: str) -> str:
    """Tra cứu trực tiếp bất kỳ bài học nào từ Lesson 21 đến Lesson 30 nếu người học hỏi cụ thể."""
    for mod_key, mod_data in EXPANDED_MODULES_21_TO_30.items():
        m_num = mod_data["num"]
        if f"lesson {m_num}" in combined_low or f"bài {m_num}" in combined_low or f"m{m_num}" in combined_low or f"l{m_num}" in combined_low:
            return (
                f"🎓 **Module {m_num} Deep Guide — {mod_data['title']}:**\n"
                f"- **Overview:** {mod_data['overview']}\n"
                f"- **Core Formula:** `{mod_data['formula']}`\n"
                f"- **Quiz 1 Key:** `{mod_data['q1_ans']}` | **Quiz 2 Key:** `{mod_data['q2_ans']}`\n"
                f"- **Lab 1 Solution:** `{mod_data['lab1_ans']}` | **Lab 2 Solution:** `{mod_data['lab2_ans']}`"
            )
    return ""


def finalize_in_user_language(response_text: str, user_lang: str) -> str:
    base_lang = user_lang.split("-")[0].lower() if user_lang else "en"
    if base_lang in ["en", "vi"]:
        return response_text
    translated_reply, _ = auto_translate_text(response_text, source_lang="en", target_lang=user_lang)
    return translated_reply if translated_reply else response_text


def generate_ai_mentor_response(query: str, current_lesson: dict, mem_db: dict) -> str:
    eng_query, detected_lang = auto_translate_text(query, source_lang="auto", target_lang="en")
    base_lang = detected_lang.split("-")[0].lower() if detected_lang else "en"
    kb_lang = "vi" if base_lang == "vi" else "en"

    combined_low = f"{query.lower()} {eng_query.lower()}"

    api_key = mem_db.get("gemini_api_key", "")
    try:
        if not api_key and "GEMINI_API_KEY" in st.secrets:
            api_key = str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass
    if api_key:
        llm_ans = call_optional_gemini_llm(query, current_lesson, api_key)
        if llm_ans:
            return llm_ans

    if not is_query_on_topic(query, eng_query, mem_db):
        if kb_lang == "vi":
            return (
                "⚠️ **Nhắc nhở từ AI Cyber Mentor:** Câu hỏi của bạn nằm ngoài phạm vi bài học. "
                "Vui lòng chỉ hỏi các chủ đề liên quan đến **An ninh mạng, Mật mã học, 4 Trụ cột Encoding (UTF-8, Base64, Multimedia, One-Hot ML), Bảo mật Web (SQLi, JWT), ECC, ZKP và 30 Bài học trong Security Academy**!"
            )
        off_topic_en = (
            "⚠️ **Topic Reminder from AI Cyber Mentor:** Your question appears to be off-topic. "
            "I am strictly trained to assist you with **Cybersecurity, Cryptography, the 4 Encoding Pillars, Binary/Bits, Web Security (SQLi, JWT), ECC, ZKP, and the 30 Security Academy Modules**. Please ask a question related to these topics!"
        )
        return finalize_in_user_language(off_topic_en, detected_lang)

    matched_learned = []
    for fact in mem_db.get("learned_facts", []):
        if any(kw in combined_low for kw in fact.get("keywords", [])) or fact["topic"].lower() in combined_low:
            matched_learned.append(f"🧠 **[{fact['topic']}]:**\n{fact['content']}")

    live_calc = try_live_computation(eng_query, kb_lang)
    cross_mod = search_across_30_modules(combined_low)

    lesson_context_reply = ""
    if current_lesson and any(k in combined_low for k in ["this lesson", "current lesson", "bài này", "bài hiện tại", "quiz", "lab", "hint", "gợi ý", "đáp án", "summary", "explain lesson"]):
        lid = current_lesson.get("id", "M01")
        ltitle = current_lesson.get("title", "")
        lesson_context_reply = (
            f"📘 **Active Module Guide ({lid} — {ltitle}):**\n"
            f"- **Core Concept:** {current_lesson.get('overview', '')}\n"
            f"- **Formula:** `{current_lesson.get('formula', '')}`\n"
            f"- **Quiz 1 Key:** `{current_lesson.get('q1_ans', '')}` | **Quiz 2 Key:** `{current_lesson.get('q2_ans', '')}`\n"
            f"- **Lab 1 Solution:** {current_lesson.get('lab1_q', '')} -> **`{current_lesson.get('lab1_ans', '')}`**\n"
            f"- **Lab 2 Solution:** {current_lesson.get('lab2_q', '')} -> **`{current_lesson.get('lab2_ans', '')}`**"
        )

    kb_matches = [item[kb_lang] for item in CORE_KNOWLEDGE_BASE if any(kw in combined_low for kw in item["keywords"])]

    parts = [p for p in (matched_learned + ([live_calc] if live_calc else []) + ([cross_mod] if cross_mod else []) + ([lesson_context_reply] if lesson_context_reply else []) + kb_matches) if p]
    if parts:
        combined_answer = "\n\n---\n\n".join(parts[:3])
        return finalize_in_user_language(combined_answer, detected_lang)

    ok_wiki, wiki_title, wiki_extract = fetch_wikipedia_crypto_summary(query, base_lang)
    if not ok_wiki and base_lang != "en":
        ok_wiki, wiki_title, wiki_extract = fetch_wikipedia_crypto_summary(eng_query, "en")
        if ok_wiki:
            wiki_extract = finalize_in_user_language(wiki_extract, detected_lang)

    if ok_wiki:
        kws_auto = [w.lower() for w in re.split(r'\W+', wiki_title) if len(w) >= 3]
        mem_db["learned_facts"].insert(0, {
            "topic": f"{wiki_title} (Verified Encyclopedia)",
            "keywords": kws_auto or [wiki_title.lower()],
            "content": wiki_extract,
            "taught_by": f"Auto_Wiki_{base_lang.upper()}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        })
        save_ai_memory(mem_db)
        return f"🌐 **[{wiki_title}]:**\n\n{wiki_extract}"

    fallback_en = CORE_KNOWLEDGE_BASE[0]["vi" if kb_lang == "vi" else "en"]
    return finalize_in_user_language(fallback_en, detected_lang)


def analyze_uploaded_file_or_image(uploaded_file, decode_lsb_fn=None, decode_audio_fn=None) -> str:
    fname = uploaded_file.name
    raw_bytes = uploaded_file.getvalue()
    fsize = len(raw_bytes)
    ext = fname.split(".")[-1].lower() if "." in fname else ""

    report = [f"📎 **AI Forensic File Analysis for `{fname}` ({fsize:,} bytes):**"]

    if ext in ["png", "jpg", "jpeg"]:
        try:
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
            w, h = img.size
            max_lsb_bytes = (w * h * 3) // 8 - 13
            report.append(f"- 🖼️ **Image Format:** `{ext.upper()}` | Resolution: `{w} x {h}` px (`{w*h:,}` pixels).")
            report.append(f"- 📊 **Max LSB Stego Capacity:** `~{max_lsb_bytes:,} bytes`.")
            if decode_lsb_fn and ext == "png":
                ok_lsb, hidden_pay = decode_lsb_fn(img)
                if ok_lsb:
                    report.append(f"- 🎯 **HIDDEN LSB PAYLOAD DETECTED:** `{hidden_pay}`")
                else:
                    report.append("- 🔍 **LSB Scan:** No `<<END_STEGO>>` hidden payload found in this image.")
        except Exception as e:
            report.append(f"- ❌ Image read error: {str(e)}")
    elif ext == "wav":
        report.append("- 🎵 **Audio Format:** `16-bit PCM WAV Audio`.")
        if decode_audio_fn:
            ok_aud, aud_pay = decode_audio_fn(raw_bytes)
            if ok_aud:
                report.append(f"- 🎯 **HIDDEN AUDIO LSB PAYLOAD DETECTED:** `{aud_pay}`")
            else:
                report.append("- 🔍 **WAV LSB Scan:** No hidden payload detected.")
    else:
        first_16_hex = " ".join(f"{b:02X}" for b in raw_bytes[:16])
        first_4_bin = " ".join(f"{b:08b}" for b in raw_bytes[:4])
        report.append(f"- 💻 **First 16 Hex Bytes:** `{first_16_hex}`")
        report.append(f"- 🔢 **First 4 Binary Bytes (32 bits):** `{first_4_bin}`")
        try:
            txt_content = raw_bytes.decode("utf-8")
            is_ascii = all(ord(c) < 128 for c in txt_content)
            enc_type = "7-Bit ASCII (UTF-8 Compatible)" if is_ascii else "Multi-Byte UTF-8 Unicode"
            report.append(f"- 🔤 **Character Encoding:** `{enc_type}` ({len(txt_content)} chars).")
            report.append(f"- 📄 **Text Preview:** `{txt_content[:180].replace(chr(10), ' ')}...`")
        except Exception:
            b64_preview = base64.b64encode(raw_bytes[:45]).decode("utf-8")
            report.append(f"- 📦 **Raw Binary -> Base64 Preview:** `{b64_preview}...`")

    return "\n".join(report)


def render_ai_cyber_mentor_widget(current_lesson: dict = None, decode_lsb_fn=None, decode_audio_fn=None, widget_key: str = "acad_ai"):
    mem_db = load_ai_memory()

    st.markdown("""
    <style>
        .ai-mentor-header {
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #0f172a 100%);
            border: 1.5px solid #6366f1;
            border-radius: 14px;
            padding: 14px 16px;
            margin-bottom: 10px;
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.25);
        }
        .ai-mentor-badge {
            background: rgba(99, 102, 241, 0.25);
            color: #a5b4fc;
            border: 1px solid #6366f1;
            padding: 2px 8px;
            border-radius: 99px;
            font-size: 0.7rem;
            font-weight: 700;
        }
    </style>
    """, unsafe_allow_html=True)

    active_lid = current_lesson.get("id", "Global") if current_lesson else "Global"
    learned_cnt = len(mem_db.get("learned_facts", [])) + len(EXPANDED_MODULES_21_TO_30) + len(CORE_KNOWLEDGE_BASE)

    st.markdown(f"""
    <div class="ai-mentor-header">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="ai-mentor-badge">🤖 AI CYBER MENTOR v4.0 • MODULE {active_lid}</span>
            <span style="font-size:0.72rem; color:#34d399; font-weight:700;">🌍 30 Modules • {learned_cnt}+ Topics</span>
        </div>
        <div style="font-size:1.06rem; font-weight:800; color:#f8fafc; margin-top:6px;">Deep-Trained Cryptography & Web Security AI</div>
        <div style="font-size:0.77rem; color:#94a3b8; margin-top:2px;">100+ Languages • 30-Lesson Index • Live Cipher Solver • Forensic File Scanner</div>
    </div>
    """, unsafe_allow_html=True)

    chat_hist_key = f"ai_mentor_v4_{widget_key}"
    if chat_hist_key not in st.session_state:
        st.session_state[chat_hist_key] = [
            {
                "role": "assistant",
                "content": (
                    "👋 **Welcome! I am AI Cyber Mentor v4.0 (Deep-Trained across all 30 Modules).**\n"
                    "- Ask me in **any language** about **Lessons 01–30**, **Binary/Bits**, **the 4 Encoding Pillars** (`UTF-8`, `Base64`, `Multimedia`, `One-Hot ML`), **Web Security (`SQLi`, `JWT`, `TLS 1.3`)**, **ECC**, or **Zero-Knowledge Proofs**.\n"
                    "- Try live commands like: `XOR 42 with 15`, `Encode \"Hello\"`, or `Decode \"Q2F0\"`!"
                )
            }
        ]

    tab_chat, tab_attach, tab_admin = st.tabs([
        "💬 Ask AI",
        "📎 Scan File/Image",
        "🔐 Admin & Feedback"
    ])

    with tab_chat:
        q_c1, q_c2, q_c3 = st.columns(3)
        with q_c1:
            if st.button("📘 Lesson Hints", key=f"q_les_{widget_key}", use_container_width=True):
                ans = generate_ai_mentor_response("Explain this lesson and give quiz/lab hints", current_lesson, mem_db)
                st.session_state[chat_hist_key].append({"role": "user", "content": "📘 Explain active lesson & show hints"})
                st.session_state[chat_hist_key].append({"role": "assistant", "content": ans})
                st.rerun()
        with q_c2:
            if st.button("🔤 4 Encodings", key=f"q_enc_{widget_key}", use_container_width=True):
                ans = generate_ai_mentor_response("Explain Character Encoding UTF-8, Base64 URL HTML, Multimedia, and One-Hot ML Encoding", current_lesson, mem_db)
                st.session_state[chat_hist_key].append({"role": "user", "content": "🔤 Summarize the 4 Encoding Pillars"})
                st.session_state[chat_hist_key].append({"role": "assistant", "content": ans})
                st.rerun()
        with q_c3:
            if st.button("🎲 Quiz Me", key=f"q_qz_{widget_key}", use_container_width=True):
                if current_lesson and "q1_q" in current_lesson:
                    qz_prompt = (
                        f"🎯 **Interactive Practice Challenge ({current_lesson.get('id', 'Academy')}):**\n\n"
                        f"**Question:** {current_lesson.get('q1_q')}\n"
                        f"- **Lab Practice:** {current_lesson.get('lab1_q')}\n\n"
                        f"*(Type your answer in the chat box below or click '📘 Lesson Hints' to verify!)*"
                    )
                else:
                    rand_mod = random.choice(list(EXPANDED_MODULES_21_TO_30.values()))
                    qz_prompt = (
                        f"🎯 **Random Practice Challenge (Module {rand_mod['num']} — {rand_mod['title']}):**\n\n"
                        f"**Question:** {rand_mod['q1_q']}\n"
                        f"- **Hands-on Lab:** {rand_mod['lab1_q']}"
                    )
                st.session_state[chat_hist_key].append({"role": "user", "content": "🎲 Give me a practice quiz!"})
                st.session_state[chat_hist_key].append({"role": "assistant", "content": qz_prompt})
                st.rerun()

        msg_box = st.container(height=340, border=True)
        with msg_box:
            for msg in st.session_state[chat_hist_key]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_q = st.chat_input("Ask in any language (e.g. 'Lesson 25 SQLi', 'XOR 31 with 12', 'What is ZKP?')...", key=f"in_ai_{widget_key}")
        if user_q and user_q.strip():
            st.session_state[chat_hist_key].append({"role": "user", "content": user_q.strip()})
            ai_reply = generate_ai_mentor_response(user_q.strip(), current_lesson, mem_db)
            st.session_state[chat_hist_key].append({"role": "assistant", "content": ai_reply})
            st.rerun()

        if len(st.session_state[chat_hist_key]) > 1:
            if st.button("🧹 Clear AI Chat", key=f"clr_ai_{widget_key}", use_container_width=True):
                st.session_state[chat_hist_key] = st.session_state[chat_hist_key][:1]
                st.rerun()

    with tab_attach:
        st.caption("📎 Upload an image (`.png, .jpg`), audio (`.wav`), or document (`.txt, .json, .csv, .py`) for AI binary byte inspection, UTF-8/ASCII verification, and hidden LSB steganography scanning:")
        up_file = st.file_uploader(
            "Select File or Image for AI Analysis:",
            type=["png", "jpg", "jpeg", "wav", "txt", "json", "csv", "py", "md"],
            key=f"up_ai_{widget_key}"
        )
        if up_file:
            if up_file.name.split(".")[-1].lower() in ["png", "jpg", "jpeg"]:
                st.image(up_file, caption=f"Attached: {up_file.name}", use_container_width=True)
            if st.button("🔍 Run AI Forensic File Analysis", type="primary", key=f"btn_anl_{widget_key}", use_container_width=True):
                file_report = analyze_uploaded_file_or_image(up_file, decode_lsb_fn, decode_audio_fn)
                st.session_state[chat_hist_key].append({"role": "user", "content": f"📎 *[Attached `{up_file.name}`]* Analyze this file!"})
                st.session_state[chat_hist_key].append({"role": "assistant", "content": file_report})
                st.success("✅ Analysis complete! Switch to the **💬 Ask AI** tab to view the full report.")

    with tab_admin:
        st.markdown("##### 💡 For Students/Users: Suggest a Topic or Feedback")
        st.caption("🔒 User submissions are placed in the **Admin Moderation Queue** and only enter AI memory after Admin approval.")

        sug_topic = st.text_input("📌 Suggested Topic / Question:", placeholder="e.g. ChaCha20-Poly1305 cipher", key=f"sug_t_{widget_key}")
        sug_note = st.text_area("📝 Details or Feedback for Admin:", placeholder="Write your suggestion or feedback...", height=68, key=f"sug_n_{widget_key}")
        if st.button("📨 Submit to Admin Review Queue", key=f"btn_sug_{widget_key}", use_container_width=True):
            if sug_topic.strip() and sug_note.strip():
                mem_db.setdefault("pending_suggestions", []).append({
                    "topic": sug_topic.strip(),
                    "note": sug_note.strip(),
                    "user": st.session_state.get("ctf_user") or "Student",
                    "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                })
                save_ai_memory(mem_db)
                st.success("✅ Sent to Admin review queue!")
            else:
                st.warning("Please fill in both fields.")

        st.divider()
        st.markdown("##### 👑 Admin Training Studio (Creator Only — Le Hoang Phu Hieu)")
        admin_pin_in = st.text_input(
            "🔑 Enter Admin Master PIN:",
            type="password",
            placeholder="Enter Admin PIN...",
            key=f"adm_pin_{widget_key}"
        )

        is_admin_unlocked = (
            hashlib.sha256(admin_pin_in.strip().encode("utf-8")).hexdigest() == mem_db.get("admin_pin_hash", DEFAULT_ADMIN_PIN_HASH)
        ) if admin_pin_in else False

        if not is_admin_unlocked:
            st.info("🔒 **Locked:** Only the platform creator can train the AI or approve user suggestions.")
        else:
            st.success("🔓 **Admin Verified!** Full AI Training & Autonomous Harvester Unlocked.")

            if st.button("🚀 Auto-Harvest 10 Core Crypto & Web Security Topics from Wikipedia", type="primary", key=f"btn_harv_{widget_key}", use_container_width=True):
                existing_topics = {f["topic"].lower() for f in mem_db.get("learned_facts", [])}
                added_count = 0
                for t_name, t_kws in AUTO_HARVEST_TOPICS:
                    if t_name.lower() not in existing_topics:
                        ok_w, w_title, w_ext = fetch_wikipedia_crypto_summary(t_name, "en")
                        if ok_w:
                            mem_db["learned_facts"].insert(0, {
                                "topic": w_title,
                                "keywords": t_kws,
                                "content": w_ext,
                                "taught_by": "Admin_Auto_Harvester",
                                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                            })
                            added_count += 1
                save_ai_memory(mem_db)
                st.balloons()
                st.success(f"🎉 Autonomous Harvester indexed **{added_count} verified topics** from Wikipedia!")

            st.divider()
            t_topic = st.text_input("Topic Name:", key=f"tr_top_{widget_key}")
            t_kws = st.text_input("Trigger Keywords (comma-separated):", key=f"tr_kw_{widget_key}")
            t_content = st.text_area("Verified Explanation:", height=80, key=f"tr_cnt_{widget_key}")
            if st.button("🧠 Save to Verified AI Memory", key=f"btn_tr_{widget_key}", use_container_width=True):
                if t_topic.strip() and t_content.strip():
                    kw_list = [k.strip().lower() for k in t_kws.split(",") if k.strip()] or [w.lower() for w in t_topic.split() if len(w) > 2]
                    mem_db["learned_facts"].insert(0, {
                        "topic": t_topic.strip(),
                        "keywords": kw_list,
                        "content": t_content.strip(),
                        "taught_by": "Admin_PhuHieu",
                        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                    })
                    save_ai_memory(mem_db)
                    st.success(f"✅ Trained topic `{t_topic.strip()}`!")

            st.divider()
            pending = mem_db.get("pending_suggestions", [])
            st.markdown(f"**📋 Pending User Suggestions ({len(pending)}):**")
            for p_idx, p_item in enumerate(pending):
                with st.container(border=True):
                    st.markdown(f"**{p_item['topic']}** *(by `{p_item['user']}`)*")
                    st.caption(p_item["note"])
                    ac1, ac2 = st.columns(2)
                    if ac1.button("✅ Approve", key=f"ap_{widget_key}_{p_idx}", use_container_width=True):
                        kws = [w.lower() for w in p_item["topic"].split() if len(w) >= 2]
                        mem_db["learned_facts"].insert(0, {
                            "topic": p_item["topic"],
                            "keywords": kws,
                            "content": p_item["note"],
                            "taught_by": f"Approved({p_item['user']})",
                            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                        })
                        mem_db["pending_suggestions"].pop(p_idx)
                        save_ai_memory(mem_db)
                        st.rerun()
                    if ac2.button("🗑️ Reject", key=f"rj_{widget_key}_{p_idx}", use_container_width=True):
                        mem_db["pending_suggestions"].pop(p_idx)
                        save_ai_memory(mem_db)
                        st.rerun()

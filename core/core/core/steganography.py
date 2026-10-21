from PIL import Image


def encode_image_lsb(img: Image.Image, secret_str: str) -> Image.Image:
    """Nhúng chuỗi mật mã vào các bit cuối cùng (LSB) của điểm ảnh RGB."""
    img = img.convert("RGB")
    data_bytes = secret_str.encode('utf-8')
    length_bits = format(len(data_bytes), '032b')
    payload_bits = length_bits + ''.join(format(byte, '08b') for byte in data_bytes)
    
    pixels = list(img.getdata())
    if len(payload_bits) > len(pixels) * 3:
        raise ValueError("Image resolution is too small for this message! Please upload a larger image.")
        
    new_pixels = []
    bit_idx = 0
    for r, g, b in pixels:
        if bit_idx < len(payload_bits):
            r = (r & ~1) | int(payload_bits[bit_idx]); bit_idx += 1
        if bit_idx < len(payload_bits):
            g = (g & ~1) | int(payload_bits[bit_idx]); bit_idx += 1
        if bit_idx < len(payload_bits):
            b = (b & ~1) | int(payload_bits[bit_idx]); bit_idx += 1
        new_pixels.append((r, g, b))
        
    encoded_img = Image.new(img.mode, img.size)
    encoded_img.putdata(new_pixels)
    return encoded_img


def decode_image_lsb(img: Image.Image) -> str:
    """Trích xuất chuỗi mật mã ẩn từ các bit cuối cùng (LSB) của bức ảnh."""
    img = img.convert("RGB")
    pixels = list(img.getdata())
    bits = []
    for r, g, b in pixels:
        bits.extend([str(r & 1), str(g & 1), str(b & 1)])
        
    length = int("".join(bits[:32]), 2)
    if length <= 0 or length > len(pixels):
        raise ValueError("No valid hidden cipher found in this image!")
        
    total_bits = 32 + length * 8
    byte_list = [int("".join(bits[i:i+8]), 2) for i in range(32, total_bits, 8)]
    return bytes(byte_list).decode('utf-8')


def inspect_pixel_lsb(img: Image.Image, num_pixels: int = 5) -> list[dict]:
    """Hàm phục vụ trang Security Academy: Phóng to và soi mã nhị phân của các Pixel đầu tiên."""
    img = img.convert("RGB")
    pixels = list(img.getdata())[:num_pixels]
    report = []
    for idx, (r, g, b) in enumerate(pixels):
        report.append({
            "Pixel": f"Pixel #{idx + 1}",
            "RGB Value": f"({r}, {g}, {b})",
            "R Binary (LSB)": f"{format(r, '08b')[:-1]}[{r & 1}]",
            "G Binary (LSB)": f"{format(g, '08b')[:-1]}[{g & 1}]",
            "B Binary (LSB)": f"{format(b, '08b')[:-1]}[{b & 1}]",
        })
    return report

# -*- coding: utf-8 -*-
"""
Casio fx-580VN X Image-to-Screen / Hex-to-Screen Auto Compiler
Usage:
  python casio_img2screen.py               (chạy chế độ tương tác dán hex / ảnh)
  python casio_img2screen.py <input.txt>   (đọc từ file hex hoặc ảnh)
"""

import os
import sys
import re
import subprocess

HDCOMPILER_DIR = os.path.join(os.path.dirname(__file__), "hdcompiler_vn")
COMPILER_PY = os.path.join(HDCOMPILER_DIR, "580vnx", "compiler_.py")

def hex_to_asm(hex_text):
    # Clean and parse hex bytes
    cleaned = hex_text.replace(",", " ").replace("0x", " ").replace("hex", " ")
    bytes_list = re.findall(r'[0-9a-fA-F]{2}', cleaned)
    if not bytes_list:
        raise ValueError("Khong tim thay byte hex hop le!")
    
    total_bytes = len(bytes_list)
    bpr = 24  # 192 pixels / 8 = 24 bytes per line
    rows = []
    for i in range(0, total_bytes, bpr):
        chunk = bytes_list[i:i+bpr]
        rows.append(" ".join(chunk))
    
    hex_len_str = f"{total_bytes:04X}"
    
    asm_lines = [
        "org 0xd730",
        "home:",
        "    setlr",
        "    setsfr",
        "    buffer_clear",
        f"    # Chep {total_bytes} bytes tu RAM vao VRAM 0xDDD4",
        f"    qr8 = 0xDDD4, adr_of [+4784] img_bitmap, 0x{hex_len_str}, 0x3030",
        "    call 10F20",
        "    render.ddd4",
        "",
        "loop:",
        "    delay",
        "    goto loop",
        "",
        "img_bitmap:"
    ]
    for r in rows:
        asm_lines.append(f"    hex {r}")
    
    return "\n".join(asm_lines), total_bytes

def compile_asm(asm_code):
    cmd = [sys.executable, COMPILER_PY, "-f", "hex"]
    proc = subprocess.Popen(
        cmd,
        cwd=os.path.join(HDCOMPILER_DIR, "580vnx"),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    stdout, stderr = proc.communicate(input=asm_code)
    return stdout

def main():
    print("=" * 60)
    print("  CASIO FX-580VN X - AUTO IMAGE / BITMAP COMPILER")
    print("=" * 60)
    
    hex_input = ""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                hex_input = f.read()
            print(f"[*] Da doc file: {file_path}")
        else:
            hex_input = " ".join(sys.argv[1:])
    else:
        print("[*] Dan chuoi hex vao day (nhan Enter 2 lan de bat dau bien dich):")
        lines = []
        while True:
            try:
                l = input()
                if not l and lines:
                    break
                if l:
                    lines.append(l)
            except EOFError:
                break
        hex_input = "\n".join(lines)

    if not hex_input.strip():
        print("[!] Khong co du lieu hex.")
        return

    try:
        asm_code, byte_count = hex_to_asm(hex_input)
        asm_out_path = os.path.join(HDCOMPILER_DIR, "580vnx_ropchain", "auto_image.asm")
        with open(asm_out_path, "w", encoding="utf-8") as f:
            f.write(asm_code)
        print(f"[+] Da tao file ASM: {asm_out_path} ({byte_count} bytes)")

        print("[*] Dang bien dich thanh chuoi ROP Hex Payload...")
        result = compile_asm(asm_code)
        print("\n" + "=" * 60)
        print("  KET QUA BIEN DICH (HEX PAYLOAD):")
        print("=" * 60)
        print(result)

        # Extract only the hex string
        hex_matches = re.findall(r'===.*?===\s*([0-9a-fA-F\s]+)', result)
        if hex_matches:
            raw_hex = hex_matches[0].strip()
            print("=" * 60)
            print("[*] Chuoi Hex gon (Copy chuoi nay dan vao Emulator / Launcher):")
            print("=" * 60)
            print(raw_hex[:200] + " ... [da luu day du vao auto_image_payload.txt]")
            with open(os.path.join(os.path.dirname(__file__), "auto_image_payload.txt"), "w", encoding="utf-8") as f:
                f.write(raw_hex)

    except Exception as e:
        print(f"[X] Loi: {e}")

if __name__ == "__main__":
    main()

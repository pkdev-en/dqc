# Casio Bot - Discord Bot for CASIO fx-580VN X / fx-880BTG

Bot Discord hỗ trợ ROP CASIO, chuyển đổi ảnh bitmap, và trả lời câu hỏi về CASIO bằng AI Gemini.

## 🚀 Tính năng chính

### 🤖 AI Chat
- Trả lời câu hỏi về CASIO 580/880 bằng Gemini AI
- Tự động đọc file `.txt` đính kèm hoặc được đề cập (`xem file`, `đọc`, `nội dung`)
- Ghi nhớ hội thoại (40 tin nhắn gần nhất)
- Tự động chat 2h/lần ở kênh đã join
- `c!learn <nội dung>` - Dạy bot kiến thức mới
- `c!study [số lượng]` - Quét tin nhắn kênh để học
- `c!reset` - Xóa bộ nhớ hội thoại

### ⚡ CASIO Engine
- `c!decomp <hex>` - Giải mã hex → assembly
- `c!comp <asm>` - Biên dịch assembly → hex (built-in)
- `c!comp5 <asm>` - Biên dịch assembly → hex (fx-580VN X)
- `c!comp8 <asm>` - Biên dịch assembly → hex (fx-880BTG)
- `c!transhex <hex>` - Alias của decomp
- Hỗ trợ nhập file `.txt` đính kèm
- Tự động loại bỏ comment (`#`, `;`) trước khi compile

### 🖼️ P2B: Ảnh ⇄ Bitmap Hex
- `c!p` hoặc `c!p2b` - Bắt đầu session chuyển ảnh sang bitmap
- **Vị trí:** `move <x> <y>`, `center`, `topleft`, `topright`, `bottomleft`, `bottomright`
- **Kích thước:** `size <WxH>` (mặc định 192×63, tối đa 500×500)
- **Threshold:** `threshold <0-255>` (mặc định 128)
- **Invert:** `invert`
- **Dither:** `dither <2/4/8>` (Bayer ordered dithering)
- **Điều chỉnh ảnh:** `brightness`, `contrast`, `exposure`, `levels`, `clarity`, `nr`, `grain`
- **Bộ lọc:** `smartsharpen`, `fieldblur`, `motionblur`, `highpass`, `emboss`, `posterize`, `equalize`, `clahe`, `removebg`
- `reset` - Reset về mặc định
- `xong` - Xuất hex kèm preview
- `exit` - Thoát session
- `c!h2i [WxH] <hex>` - Hex → ảnh PNG trực tiếp
- `c!hexsplit <hex>` - Tách hex thành dạng hexdump
- `c!dichhex <hex>` - Hex → ảnh (auto-detect width)
- `c!ganhex <hex>` - Format hex gọn gàng

### 🔧 Hệ thống
- `c!join` - Vô kênh, auto trả lời mọi tin nhắn
- `c!leave` - Rời kênh, chỉ trả lời khi tag/reply
- `c!dongmon` - Xem số member/bot trong server
- `c!snipe` - Xem tin nhắn đã xoá gần nhất
- `c!hoidap` - Menu tra cứu chủ đề CASIO
- `c!file` - Quản lý file (view/write/append)
- `c!restart` - Khởi động lại bot
- `c!console <#kênh>` - Chuyển console sang kênh Discord
- `c!help` - Xem danh sách lệnh

### 🔑 API Keys
- `c!api <key>` - Set key duy nhất
- `c!addkey <key>` - Thêm key mới
- `c!addkeyat <index> <key>` - Ghi đè key tại vị trí
- `c!keys` - Xem danh sách key (masked)
- `c!model <model>` - Đổi model AI
- Tự động rotate key khi hết quota

## 📁 Cấu trúc file

```
.env                    - Biến môi trường (token, API key, model)
persona.txt             - Tính cách AI
knowledge.txt           - Kiến thức CASIO
knowledge_learned.txt   - Kiến thức học được từ người dùng
api_keys.txt            - Danh sách API key
api_key_index.txt       - Chỉ số key hiện tại
bot.py                  - Bot chính
bridge.py               - Module phụ trợ
bitmapreader.py         - Dữ liệu hex bitmap mẫu
hdcompiler_vn/          - Compiler CASIO (580/880)
```

## 🛠️ Công nghệ

- Python 3.11+
- discord.py (discord.ext.commands)
- Google Gemini API
- Pillow (xử lý ảnh)
- NumPy
- OpenCV (removebg, optional)

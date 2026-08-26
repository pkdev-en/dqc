"""
Discord → Firestore Bridge
Thêm đoạn code này vào bot.py để đồng bộ tin nhắn từ Discord #chat-chung lên Firestore.

Cách dùng:
1. pip install firebase-admin
2. Copy file serviceAccount.json vào cùng thư mục với bot.py
3. Thêm code này vào bot.py (import + event handler)
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os

# === FIREBASE INIT ===
FIREBASE_CRED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serviceAccount.json")
if os.path.exists(FIREBASE_CRED):
    try:
        cred = credentials.Certificate(FIREBASE_CRED)
        firebase_admin.initialize_app(cred)
        fb_db = firestore.client()
        print("[Firestore Bridge] ✓ Đã kết nối Firebase")
    except Exception as e:
        print(f"[Firestore Bridge] ✗ Lỗi Firebase: {e}")
        fb_db = None
else:
    print(f"[Firestore Bridge] ✗ Không tìm thấy {FIREBASE_CRED}")
    fb_db = None

# === DISCORD CHAT CHANNEL ID ===
CHAT_CHANNEL_ID = 1481167996461252652

# === THÊM VÀO on_message() TRONG BOT CỦA BẠN ===
"""
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # Bridge Discord → Firestore
    if message.channel.id == CHAT_CHANNEL_ID and fb_db:
        try:
            fb_db.collection('messages').add({
                'text': message.content,
                'uid': str(message.author.id),
                'author': message.author.display_name,
                'avatar': message.author.avatar.url if message.author.avatar else '',
                'timestamp': firestore.SERVER_TIMESTAMP,
                'source': 'discord'
            })
        except Exception as e:
            print(f"[Firestore Bridge] Lỗi ghi tin: {e}")
    
    # ... code xử lý tin nhắn còn lại của bạn ...
    await bot.process_commands(message)
"""

print("[Firestore Bridge] Module loaded - sẵn sàng đồng bộ Discord → Firestore")

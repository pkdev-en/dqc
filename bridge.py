"""
Discord → Firestore Bridge (độc lập, không ảnh hưởng bot.py)
Dùng REST API, không dùng Gateway → chạy song song với bot.py OK
"""
import os, time, requests, json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = "1481167996461252652"
BACKEND = "http://localhost:4000/api/bridge/discord-message"
HEADERS = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

last_id = None

def fetch_messages():
    global last_id
    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages?limit=5"
    if last_id:
        url += f"&after={last_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=5)
        if r.status_code != 200:
            return
        msgs = r.json()
        if not msgs:
            return
        for msg in reversed(msgs):
            if msg["author"].get("bot") or msg.get("webhook_id"):
                continue
            mid = msg["id"]
            if last_id and int(mid) <= int(last_id):
                continue
            payload = {
                "text": msg["content"],
                "uid": msg["author"]["id"],
                "author": msg["author"]["global_name"] or msg["author"]["username"],
                "avatar": f"https://cdn.discordapp.com/avatars/{msg['author']['id']}/{msg['author']['avatar']}.png" if msg["author"].get("avatar") else ""
            }
            if payload["text"]:
                requests.post(BACKEND, json=payload, timeout=2)
        last_id = msgs[-1]["id"]
    except Exception as e:
        print(f"[Bridge] Loi: {e}")

print("[Bridge] Dang chay -- dong bo Discord -> Web (poll 3s)")
while True:
    fetch_messages()
    time.sleep(3)

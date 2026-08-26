import discord
import asyncio
import sys
import threading
import json
from flask import Flask, request, jsonify, render_template_string

token = input("Nhap token: ").strip()
if not token:
    print("Thieu token")
    sys.exit(1)

PORT = 5000

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

app = Flask(__name__)
bot_data = {"guilds": [], "ready": False}

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Bot Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:#1a1a2e;color:#eee;padding:20px}
h1{color:#e94560;margin-bottom:20px}
.card{background:#16213e;border-radius:10px;padding:15px;margin-bottom:15px}
.server{background:#0f3460;border-radius:8px;padding:12px;margin-bottom:10px;cursor:pointer}
.server:hover{background:#1a4a8a}
.channel{padding:6px 12px;margin:4px 0;border-radius:5px;display:flex;justify-content:space-between;background:#1a1a3e;cursor:pointer}
.channel:hover{background:#2a2a5e}
.perms{font-size:12px;color:#aaa;margin-top:4px}
.badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;margin:2px}
.badge-green{background:#2ecc71;color:#000}
.badge-red{background:#e74c3c;color:#fff}
.badge-blue{background:#3498db;color:#fff}
#chat{max-height:300px;overflow-y:auto;background:#0d1117;border-radius:8px;padding:10px;margin:10px 0}
.msg{padding:4px 0;border-bottom:1px solid #222}
.msg-name{color:#58a6ff;font-weight:bold}
.msg-time{color:#555;font-size:11px;margin-left:8px}
#input-area{display:flex;gap:8px;margin-top:10px}
#input-area input{flex:1;padding:10px;border-radius:6px;border:none;background:#0d1117;color:#eee;font-size:14px}
#input-area button{padding:10px 20px;border-radius:6px;border:none;background:#e94560;color:#fff;font-weight:bold;cursor:pointer}
#input-area button:hover{background:#ff6b81}
.active{background:#2a4a7a !important}
.quyen{margin-top:8px;padding:8px;background:#1a1a3e;border-radius:5px;font-size:13px}
</style>
</head>
<body>
<h1>🤖 Bot Dashboard</h1>
<div id="status" class="card">Dang ket noi...</div>
<div id="main" style="display:none">
  <div class="card">
    <h3>📡 Server</h3>
    <select id="guild-select" onchange="loadChannels()" style="width:100%;padding:8px;background:#0d1117;color:#eee;border:1px solid #333;border-radius:5px;margin:8px 0"></select>
    <div id="guild-perms" class="quyen"></div>
  </div>
  <div class="card">
    <h3>📢 Kenh</h3>
    <div id="channels"></div>
  </div>
  <div class="card">
    <h3>💬 Chat</h3>
    <div id="chat"></div>
    <div id="input-area">
      <input id="msg-input" placeholder="Nhap tin nhan..." onkeydown="if(event.key=='Enter')sendMsg()">
      <button onclick="sendMsg()">Gui</button>
    </div>
  </div>
</div>

<script>
let selectedGuild = null, selectedChannel = null;

async function fetchData() {
  const r = await fetch('/api/data');
  const d = await r.json();
  if (d.ready) {
    document.getElementById('status').innerHTML = '✅ Bot dang online: <b>' + d.bot_name + '</b> (ID: ' + d.bot_id + ')';
    document.getElementById('main').style.display = 'block';
    const sel = document.getElementById('guild-select');
    sel.innerHTML = d.guilds.map((g,i) => '<option value="' + i + '">' + g.name + ' (' + g.members + ' members)</option>').join('');
    if (d.guilds.length > 0) loadChannels();
  }
}

async function loadChannels() {
  const idx = document.getElementById('guild-select').value;
  const r = await fetch('/api/guild/' + idx);
  const d = await r.json();
  selectedGuild = d;
  document.getElementById('guild-perms').innerHTML = d.key_perms.map(p => '<span class="badge badge-green">' + p + '</span>').join(' ');
  const ch = document.getElementById('channels');
  ch.innerHTML = d.channels.map((c,i) => '<div class="channel" onclick="selectChannel(' + i + ')" id="ch-' + i + '"><span>' + (c.can_send ? '✅ ' : '❌ ') + '#' + c.name + '</span><span style="color:#888">' + c.id + '</span></div>').join('');
  if (d.channels.length > 0) selectChannel(0);
}

function selectChannel(idx) {
  document.querySelectorAll('.channel').forEach(el => el.classList.remove('active'));
  const el = document.getElementById('ch-' + idx);
  if (el) el.classList.add('active');
  selectedChannel = selectedGuild.channels[idx];
  document.getElementById('chat').innerHTML = '';
}

async function fetchMessages() {
  if (!selectedChannel) return;
  const r = await fetch('/api/messages/' + selectedChannel.id);
  const msgs = await r.json();
  const chat = document.getElementById('chat');
  chat.innerHTML = msgs.map(m => '<div class="msg"><span class="msg-name">' + m.author + '</span><span class="msg-time">' + m.time + '</span><br>' + m.content + '</div>').join('');
}

async function sendMsg() {
  const input = document.getElementById('msg-input');
  const text = input.value.trim();
  if (!text || !selectedChannel) return;
  input.value = '';
  await fetch('/api/send', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({channel_id: selectedChannel.id, content: text})
  });
  fetchMessages();
}

setInterval(fetchData, 2000);
setInterval(fetchMessages, 3000);
fetchData();
</script>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/data")
def api_data():
    if not bot_data["ready"]:
        return jsonify({"ready": False})
    return jsonify({
        "ready": True,
        "bot_name": bot_data.get("bot_name", ""),
        "bot_id": bot_data.get("bot_id", 0),
        "guilds": [{"name": g["name"], "members": g["members"], "id": g["id"]} for g in bot_data["guilds"]]
    })

@app.route("/api/guild/<int:idx>")
def api_guild(idx):
    if idx < 0 or idx >= len(bot_data["guilds"]):
        return jsonify({"error": "invalid index"})
    return jsonify(bot_data["guilds"][idx])

@app.route("/api/messages/<int:channel_id>")
def api_messages(channel_id):
    msgs = bot_data.get("message_cache", {}).get(channel_id, [])
    return jsonify(msgs[-20:])

@app.route("/api/send", methods=["POST"])
def api_send():
    data = request.json
    ch_id = data.get("channel_id")
    content = data.get("content")
    if not ch_id or not content:
        return jsonify({"error": "missing fields"}), 400
    ch = client.get_channel(int(ch_id))
    if not ch:
        return jsonify({"error": "channel not found"}), 404
    coro = ch.send(content)
    asyncio.run_coroutine_threadsafe(coro, client.loop)
    return jsonify({"ok": True})

PERM_NAMES = {
    "administrator": "Admin", "manage_guild": "QL Server", "kick_members": "Kick",
    "ban_members": "Ban", "manage_messages": "QL Tin nhan", "manage_channels": "QL Kenh",
    "manage_roles": "QL Role", "manage_webhooks": "QL Webhook", "send_messages": "Gui tin",
    "read_message_history": "Doc lich su", "mention_everyone": "Mention @everyone",
    "manage_emojis": "QL Emoji"
}
KEY_PERMS = ["administrator", "manage_guild", "kick_members", "ban_members", "manage_messages", "manage_channels", "manage_roles", "manage_webhooks"]

@client.event
async def on_ready():
    print(f"[Dang nhap] {client.user}")
    bot_data["ready"] = True
    bot_data["bot_name"] = str(client.user)
    bot_data["bot_id"] = client.user.id
    bot_data["message_cache"] = {}

    for g in client.guilds:
        me = g.me or g.get_member(client.user.id)
        gp = me.guild_permissions if me else discord.Permissions.none()
        key_perms = [PERM_NAMES[n] for n in KEY_PERMS if getattr(gp, n, False)]

        channels = []
        for c in g.text_channels:
            cp = c.permissions_for(me) if me else discord.Permissions.none()
            channels.append({
                "id": c.id, "name": c.name, "can_send": cp.send_messages and cp.view_channel,
                "perms": [PERM_NAMES[n] for n in PERM_NAMES if getattr(cp, n, False)]
            })

        bot_data["guilds"].append({
            "id": g.id, "name": g.name, "members": g.member_count, "key_perms": key_perms,
            "channels": channels
        })
        bot_data["message_cache"][g.id] = []

    print(f"Da san sang: {len(bot_data['guilds'])} servers")
    print(f"Dashboard: http://localhost:{PORT}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    cid = message.channel.id
    if cid not in bot_data["message_cache"]:
        bot_data["message_cache"][cid] = []
    bot_data["message_cache"][cid].append({
        "author": message.author.name, "content": message.content[:200],
        "time": message.created_at.strftime("%H:%M")
    })
    if len(bot_data["message_cache"][cid]) > 50:
        bot_data["message_cache"][cid] = bot_data["message_cache"][cid][-50:]

def run_flask():
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)

threading.Thread(target=run_flask, daemon=True).start()
client.run(token)

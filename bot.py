import threading, http.server
import discord
from discord.ext import commands, tasks
from openai import AsyncOpenAI
import os
import sys
import subprocess
import json
import re
import io
import math
import random
import threading
import asyncio
from io import BytesIO
from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageDraw
import numpy as np
from dotenv import load_dotenv
import time
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8')
os.environ["PYTHONIOENCODING"] = "utf-8"

dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://sarsed.eu.cc/v1")
MODEL = os.getenv("MODEL", "oc/union-alpha")
KNOWLEDGE_FILE = os.getenv("KNOWLEDGE_FILE", "knowledge.txt")
LEARNED_KNOWLEDGE_FILE = "knowledge_learned.txt"
CHANNELS_FILE = "joined_channels.json"
PERSONA_FILE = os.getenv("PERSONA_FILE", "persona.txt")

def load_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def save_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def append_file(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n" + content.strip() + "\n")

def fix_emoji(text, guild=None):
    if guild:
        emoji_map = {e.name: f"<:{e.name}:{e.id}>" for e in guild.emojis}
        def repl(m):
            return emoji_map.get(m.group(1), m.group(0))
        text = re.sub(r'<:([^:]+):\d*>', r':\1:', text)
        text = re.sub(r':([\w~]+):', repl, text)
    else:
        text = re.sub(r'<:([^:]+):\d*>', r':\1:', text)
    return text

def split_message(text, max_len=2000):
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        split = max_len
        nl = text.rfind("\n", 0, split)
        if nl > split // 2:
            split = nl + 1
        chunk = text[:split]
        text = text[split:]
        if chunk.count("```") % 2 == 1:
            chunk += "\n```"
            text = "```\n" + text
        chunks.append(chunk)
    return chunks

ALLOWED_FILES = [".env", "persona.txt", "knowledge.txt", "knowledge_learned.txt"]
ALLOWED_FILE_USERS = [1173632231474995281, 1046054858580561960, 1358317538869776395]
SPECIAL_USERS = {
    1358317538869776395: "chủ server",
    1173632231474995281: "nhà phát triển bot",
}
CONTRIBUTOR_ROLES = ["trưởng lão", "công thần"]
API_KEYS_FILE = "api_keys.txt"
API_KEY_INDEX_FILE = "api_key_index.txt"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HD580_DIR = os.path.join(BASE_DIR, "hdcompiler_vn", "580vnx")
HD580_COMPILER = os.path.join(HD580_DIR, "compiler_.py")
HD880_DIR = os.path.join(BASE_DIR, "hdcompiler_vn", "880btg")
HD880_COMPILER = os.path.join(HD880_DIR, "compiler_.py")

def get_file_info(path):
    try:
        size = os.path.getsize(path)
        modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
        preview = load_file(path)[:200].replace("\n", " ")[:200]
        return size, modified, preview
    except:
        return None, None, None

def update_env_var(key, value):
    try:
        with open(".env", "r", encoding="utf-8") as f:
            lines = f.readlines()
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith(key + "="):
                lines[i] = f"{key}={value}\n"
                found = True
                break
        if not found:
            lines.append(f"{key}={value}\n")
        with open(".env", "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    except:
        return False

def load_api_keys():
    try:
        with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
            keys = [line.strip() for line in f if line.strip()]
        return keys if keys else [GEMINI_API_KEY]
    except FileNotFoundError:
        return [GEMINI_API_KEY]

def load_key_index():
    try:
        with open(API_KEY_INDEX_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_key_index(idx):
    try:
        with open(API_KEY_INDEX_FILE, "w") as f:
            f.write(str(idx))
    except:
        pass

api_keys = load_api_keys()
api_key_index = load_key_index()
if api_key_index >= len(api_keys):
    api_key_index = 0
GEMINI_API_KEY = api_keys[api_key_index]

KNOWLEDGE_BASE = load_file(KNOWLEDGE_FILE)
KNOWLEDGE_LEARNED = load_file(LEARNED_KNOWLEDGE_FILE)
PERSONA = load_file(PERSONA_FILE)

if not PERSONA:
    PERSONA = "Bạn là một trợ lý ảo Discord thân thiện, thông minh và hài hước."

def refresh_globals(filename):
    global KNOWLEDGE_BASE, KNOWLEDGE_LEARNED, PERSONA
    if filename == "knowledge.txt":
        KNOWLEDGE_BASE = load_file(KNOWLEDGE_FILE)
    elif filename == "knowledge_learned.txt":
        KNOWLEDGE_LEARNED = load_file(LEARNED_KNOWLEDGE_FILE)
    elif filename == "persona.txt":
        PERSONA = load_file(PERSONA_FILE)

def get_full_knowledge():
    parts = []
    if KNOWLEDGE_BASE:
        parts.append(f"Kiến thức gốc:\n{KNOWLEDGE_BASE}")
    if KNOWLEDGE_LEARNED:
        parts.append(f"Kiến thức học được từ người dùng:\n{KNOWLEDGE_LEARNED}")
    return "\n\n".join(parts)

def get_system_prompt():
    knowledge = get_full_knowledge()
    if knowledge:
        return PERSONA + "\n\n" + knowledge
    return PERSONA

def get_user_context(member):
    if not member:
        return ""
    lines = []
    lines.append(f"Tên người dùng: {member.display_name}")
    uid = member.id
    if uid in SPECIAL_USERS:
        lines.append(f"Danh hiệu: {SPECIAL_USERS[uid]}")
    user_roles = [r.name for r in member.roles if r.name != "@everyone"]
    contributor_roles_found = [r for r in user_roles if r.lower() in CONTRIBUTOR_ROLES]
    if contributor_roles_found:
        lines.append(f"Vai trò trong server: {', '.join(contributor_roles_found)}")
    return "\n".join(lines)

def switch_api_key():
    global api_key_index, GEMINI_API_KEY, genai_client
    api_key_index = (api_key_index + 1) % len(api_keys)
    GEMINI_API_KEY = api_keys[api_key_index]
    genai_client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)
    save_key_index(api_key_index)
    print(f"[API] Đã chuyển sang key #{api_key_index}")

async def call_gemini(model, contents, config=None, max_retries=1):
    global api_exhausted_until

    now = time.time()
    if now < api_exhausted_until:
        raise Exception(
            f"API đang trong thời gian chờ, thử lại sau "
            f"{int(api_exhausted_until - now)}s"
        )

    for attempt in range(max_retries):
        try:
            response = await genai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": contents
                    }
                ]
            )

            return type(
                "Response",
                (),
                {
                    "text": response.choices[0].message.content or ""
                }
            )()

        except Exception as e:
            print(f"[API] Lỗi: {e}")

            if attempt + 1 >= max_retries:
                raise

            await asyncio.sleep(1)

def load_joined_channels():
    try:
        with open(CHANNELS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_joined_channels(channels):
    with open(CHANNELS_FILE, "w") as f:
        json.dump(channels, f)

joined_channels = load_joined_channels()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="c!", intents=intents, help_command=None)

def start_keepalive():
    port = int(os.getenv("PORT", 8080))
    srv = http.server.HTTPServer(("0.0.0.0", port), http.server.SimpleHTTPRequestHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
start_keepalive()

genai_client = genai.Client(api_key=GEMINI_API_KEY)

snipe_store = {}
console_channel_id = None
conversation_memory = {}
MAX_MEMORY = 40
api_exhausted_until = 0

@bot.event
async def on_ready():
    print(f"--- Bot đã online thành công với tên: {bot.user} ---")
    print(f"Đang theo dõi {len(joined_channels)} kênh tự động: {joined_channels}")
    global console_channel_id
    if console_channel_id:
        ch = bot.get_channel(console_channel_id)
        if ch:
            print(f"Console chat đang gửi đến: #{ch.name} ({console_channel_id})")
    auto_chat_loop.start()


@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    snipe_store[message.channel.id] = {
        "author": message.author,
        "content": message.content,
        "attachments": [a.url for a in message.attachments],
        "time": message.created_at
    }

@bot.command(name="join")
async def join(ctx):
    if ctx.channel.id in joined_channels:
        await ctx.reply("Mình đã ở trong kênh này rồi mà! 👀")
    else:
        joined_channels.append(ctx.channel.id)
        save_joined_channels(joined_channels)
        await ctx.reply("✅ Đã tham gia kênh này! Mình sẽ tự động trả lời mọi câu hỏi ở đây.")

@bot.command(name="learn")
async def learn(ctx, *, content):
    global KNOWLEDGE_LEARNED, KNOWLEDGE_BASE
    append_file(LEARNED_KNOWLEDGE_FILE, content)
    KNOWLEDGE_LEARNED = load_file(LEARNED_KNOWLEDGE_FILE)
    KNOWLEDGE_BASE = load_file(KNOWLEDGE_FILE)
    await ctx.reply("✅ Mình đã ghi nhớ thông tin này!")

@bot.command(name="study")
async def study(ctx, limit: int = 1000):
    global KNOWLEDGE_LEARNED
    if limit > 100000:
        await ctx.reply("⚠️ Giới hạn tối đa 100000 tin nhắn.")
        limit = 100000
    msg = await ctx.reply(f"📖 Đang học {limit} tin nhắn gần nhất...")

    async with ctx.channel.typing():
        lines = []
        async for msg_h in ctx.channel.history(limit=limit):
            if msg_h.author == bot.user or msg_h.content.startswith("c!"):
                continue
            if msg_h.attachments:
                continue
            text = msg_h.content.strip()
            if text:
                lines.append(f"{msg_h.author.display_name}: {text}")

        if not lines:
            await msg.edit(content="Không có tin nhắn nào để học.")
            return

        learned = "\n".join(reversed(lines))
        append_file(LEARNED_KNOWLEDGE_FILE, learned)
        KNOWLEDGE_LEARNED = load_file(LEARNED_KNOWLEDGE_FILE)
        await msg.edit(content=f"✅ Đã học xong {len(lines)} tin nhắn!")

@bot.command(name="api")
async def api(ctx, *, api_key):
    global API_KEY, genai_client

    API_KEY = api_key.strip()

    genai_client = AsyncOpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )

    update_env_var("API_KEY", API_KEY)

    await ctx.reply("✅ Đã cập nhật API key thành công!")

@bot.command(name="model")
async def model(ctx, *, model):
    global MODEL
    MODEL = model
    update_env_var("MODEL", model)
    await ctx.reply(f"✅ Đã chuyển sang model: {model}")

@bot.command(name="reset")
async def reset(ctx):
    cid = ctx.channel.id
    conversation_memory.pop(cid, None)
    await ctx.reply("🧹 Đã xóa bộ nhớ hội thoại cho kênh này!")

@bot.command(name="keys")
async def keys(ctx):
    total = len(api_keys)
    mask = lambda k: k[:8] + "..." + k[-4:]
    current = mask(api_keys[api_key_index]) if api_keys else "N/A"
    lines = [f"🔑 **API Keys**: {total} keys\n**Đang dùng**: #{api_key_index} - `{current}`"]
    for i, k in enumerate(api_keys):
        mark = " ✅" if i == api_key_index else ""
        lines.append(f"`#{i}` {mask(k)}{mark}")
    await ctx.reply("\n".join(lines))

@bot.command(name="addkey")
async def addkey(ctx, *, api_key):
    global api_keys
    api_key = api_key.strip()
    if not api_key:
        await ctx.reply("❌ Thiếu API key!")
        return
    if api_key in api_keys:
        await ctx.reply("⚠️ Key này đã có trong danh sách!")
        return
    api_keys.append(api_key)
    try:
        with open(API_KEYS_FILE, "a", encoding="utf-8") as f:
            f.write(api_key + "\n")
    except Exception as e:
        await ctx.reply(f"✅ Đã thêm key nhưng lỗi ghi file: {e}")
        return
    await ctx.reply(f"✅ Đã thêm API key #{len(api_keys) - 1}!")

@bot.command(name="addkeyat")
async def addkeyat(ctx, index: int, *, api_key):
    global api_keys, api_key_index
    api_key = api_key.strip()
    if not api_key:
        await ctx.reply("❌ Thiếu API key!")
        return
    if index < 0 or index > len(api_keys):
        await ctx.reply(f"❌ Vị trí phải từ 0 đến {len(api_keys)}!")
        return
    if api_key in api_keys:
        await ctx.reply("⚠️ Key này đã có trong danh sách!")
        return
    api_keys.insert(index, api_key)
    if index <= api_key_index:
        api_key_index += 1
        save_key_index(api_key_index)
    try:
        with open(API_KEYS_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(api_keys) + "\n")
    except Exception as e:
        await ctx.reply(f"✅ Đã thêm key nhưng lỗi ghi file: {e}")
        return
    await ctx.reply(f"✅ Đã thêm API key vào vị trí #{index}!")

@bot.command(name="file")
async def file(ctx, action=None, filename=None, *, content=None):
    if ctx.author.id not in ALLOWED_FILE_USERS:
        await ctx.reply("❌ Bạn không có quyền sử dụng lệnh này.")
        return
    if action is None:
        embed = discord.Embed(title="📁 File Manager", color=0x00ff00)
        for f in ALLOWED_FILES:
            size, modified, preview = get_file_info(f)
            if size is not None:
                val = f"**Size:** {size} bytes\n**Sửa lần cuối:** {modified}\n**Preview:** `{preview}`"
            else:
                val = "*File chưa tồn tại*"
            embed.add_field(name=f"`{f}`", value=val, inline=False)
        embed.add_field(name="Cách dùng", value="`c!file view <file>` - Xem nội dung\n`c!file write <file> <nội dung>` - Ghi đè\n`c!file append <file> <nội dung>` - Thêm vào cuối", inline=False)
        await ctx.reply(embed=embed)
        return

    if filename not in ALLOWED_FILES:
        await ctx.reply(f"❌ File không được phép chỉnh sửa. Cho phép: {', '.join(ALLOWED_FILES)}")
        return

    if action == "view":
        content = load_file(filename)
        if not content:
            await ctx.reply(f"📄 `{filename}`: *rỗng hoặc không tồn tại*")
        elif len(content) > 1900:
            for i in range(0, len(content), 1900):
                await ctx.reply(f"📄 `{filename}`:\n```\n{content[i:i+1900]}\n```")
        else:
            await ctx.reply(f"📄 `{filename}`:\n```\n{content}\n```")

    elif action == "write":
        if not content:
            await ctx.reply("❌ Ghi thiếu nội dung. Dùng: `c!file write <file> <nội dung>`")
            return
        save_file(filename, content)
        refresh_globals(filename)
        size, modified, _ = get_file_info(filename)
        embed = discord.Embed(title=f"✅ Đã ghi `{filename}`", color=0x00ff00)
        embed.add_field(name="Size", value=f"{size} bytes")
        embed.add_field(name="Cập nhật", value=modified)
        await ctx.reply(embed=embed)

    elif action == "append":
        if not content:
            await ctx.reply("❌ Thiếu nội dung. Dùng: `c!file append <file> <nội dung>`")
            return
        append_file(filename, content)
        refresh_globals(filename)
        await ctx.reply(f"✅ Đã thêm vào `{filename}`")

    else:
        await ctx.reply("❌ Action không hợp lệ. Dùng: `view`, `write`, `append`")

@bot.command(name="restart")
async def restart(ctx):
    await ctx.reply("🔄 Đang khởi động lại...")
    await bot.close()
    subprocess.Popen([sys.executable] + sys.argv)
    os._exit(0)

# ================= GADGET DB + ENGINE =================
raw_gadget_list = [
    ["09fa8","setlr"],["308d0","setlr_pc"],["0a05c","DI,RT"],
    ["23f9e","calc_checksum_set_f004"],["23fa6","calc_checksum_no_set_f004"],
    ["23fad","calc_checksum_0"],["23fc0","calc_checksum_1"],["23fd4","calc_checksum_2"],
    ["23fea","calc_checksum_3"],["23f21","pr_checksum"],["09ca0","[er8]+=er2,pop xr8"],
    ["2702e","sp=er14,pop er14,rt"],["12da6","sp=er14,pop qr8"],
    ["23f82","sp=er14,pop qr8,pop qr0"],["20d60","sp=er14,pop er14"],
    ["21f74","sp=er6,pop er8"],["09820","sp=er14,pop xr12"],["13aac","sp=er14,pop qr8,pop er6"],
    ["0ac34","er14=sp,rt"],["0a8a8","nop"],["13b66","er0+=er0,er0+=er2,er8=[er0]"],
    ["13b9a","er0+=er0,er2+=er0,er0=[er2]"],["1ec0c","pop ea"],["27030","pop er14,rt"],
    ["13332","pop er0,rt"],["18974","pop er2"],["250a6","pop er4"],["0a8a6","pop er8"],
    ["16eca","pop er12,rt"],["17bda","pop qr0"],["12da8","pop qr8"],["177da","pop r0"],
    ["1844a","pop r8"],["1622e","pop xr0"],["1d040","pop xr4"],["183a6","pop xr8"],
    ["0d516","pop er10"],["0d04c","pop r12"],["12602","pop er0"],["21636","pop er12"],
    ["15c78","pop er14"],["13ab0","pop er6"],["1dcf6","pop er6,rt"],["20730","pop xr12"],
    ["16d88","pop er4,rt"],["16d7c","pop er8,rt"],["17072","pop qr0,rt"],["14c50","pop qr8,rt"],
    ["15fc0","pop r4"],["16210","pop r4,rt"],["14c98","pop r9"],["10e5a","pop xr12,rt"],
    ["1d972","pop xr4,rt"],["0e5e2","pop xr8,rt"],["093b8","pop er2,pop er8,er0=er2,rt"],
    ["1893a","pop er0,pop er4"],["16754","pop er4,pop er8"],["201f6","pop er4,pop er12,pop r9"],
    ["14bd8","er0+=er4,rt"],["13b80","er4+=er0,r8=r8,rt"],["21ba8","er0+=er8,rt"],
    ["21bae","er2+=er8,rt"],["2fa0c","er0+=er2,rt"],["16078","er0+=1,rt"],
    ["09ce4","r0+=1,rt"],["14fcc","er0+=er6,er10=er0,rt"],["20838","and r0,0f"],
    ["24008","er6=er0,er0=er8,pop qr8"],["16170","er8=er0"],["0ea70","er2=er0,er0=er2,pop er8,rt"],
    ["14bd6","er2=er0,er0+=er4,rt"],["0bf30","er0=er2,rt"],["2470a","er0=er4,pop er4"],
    ["2f786","er0=er8,pop er8,rt"],["0a246","er0=er8,pop er8"],["15386","er0=er8"],
    ["1edea","er0=er6,pop er8,pop xr4,rt"],["28c86","er2=er0,r0=r4,r1=0,pop xr4,rt"],
    ["2ffc0","r0=r5,pop er4"],["1abb0","r0=r2=0"],["1abb2","r0=r2"],["15fde","r2=r0,pop er0"],
    ["164e4","r2=r0,pop r6,pop er12"],["177b4","r2=0,r7=4"],["1ca8a","r0=0"],
    ["1DD54","r0=0,rt"],["1DD58","r0=1,rt"],["18978","r0=0,pop er2"],["2ac30","r1=0,rt"],
    ["16df2","r5=0,rt"],["17b32","er14=er0,pop xr0"],["0ac7c","er0=er12,pop er12,rt"],
    ["13916","er10=er2,rt"],["20b52","er0=er10,pop xr8"],["1e60c","er0=1,rt"],
    ["180d2","er2=0,er4=0,er6=0,er8=1,rt"],["09caa","er2=0,r0=2,[er8]=er2,pop xr8"],
    ["0a88a","er2=1,r0=r2,rt"],["09c9e","r0=0,[er8]+=er2,pop xr8"],
    ["27e7c","r2=1,r0=r2,pop er4,pop er8,rt"],["27e92","r0=r1,rt"],
    ["14fce","er10=er0,rt"],["283fe","er2=0,er0=er2,pop er8"],["140e4","er0=er6,er2=er12"],
    ["16e18","r4=0"],["0eda0","er0=0,rt"],["16d9a","[er2]=er0,r2=0,pop er4,rt"],
    ["139d8","[er0]=er2,rt"],["208b2","[er0]=r2,rt"],["203D2","[er0]=r2"],
    ["176d4","[er2]=r0,r2=0"],["09ca4","[er8]=er2,pop xr8"],["13330","[er4]=er0,pop er0,rt"],
    ["1a588","[ea]=qr0"],["22226","[er12]=er14,pop xr4,pop qr8"],["1332a","[er4]+=1,rt"],
    ["13336","[er4]-=1,rt"],["19e5a","er8=[ea+],rt"],["16614","[er2]=r0,r0=0"],
    ["16d7a","er4=[er8],pop er8,rt"],["13b9e","er0=[er2],r2=9,rt"],["13b6a","er8=[er0],rt"],
    ["09e4a","r0=[er2]"],["18274","r0=[er0]"],["298dc","er0=[er0],pop xr8,rt"],
    ["09fdc","r0=[ea],rt"],["21f72","sp=[er8],pop er8"],["1c2c0","qr0=[ea],lea D002H,[ea]=qr0"],
    ["1c64a","er6=[ea]"],["09e8a","er0-=er2,rt"],["29a40","er0-=er12,pop er8,pop er12,rt"],
    ["09e98","r0-=1,rt"],["0ac5a","r0-=r8,pop er8,rt"],["122d4","or r0,r1"],["1a5c2","or qr0,qr8"],
    ["20830","r0>>4,rt"],["1bb28","qr0>>4,rt"],["1bb5c","r0<<4,rt"],["1bb70","r1<<4,rt"],
    ["1bb5a","er0<<4,rt"],["1bb56","xr0<<4,rt"],["1bb4e","qr0<<4,rt"],
    ["0c790","er0-er2_gt,r0=0|r0=1,rt"],["09ae6","er0-er2_eq,r0=1|r0=0,rt"],
    ["0c7a8","er2-er0_gt,r0=0|r0=1,rt"],["2abda","er0-er2_le,er0=er2,rt"],
    ["297e2","er8-er0_lt,pop xr8"],["091ec","r0-0_lt,rt"],["091f4","r1-0_lt,rt"],
    ["14bd4","er0*=r2,er2=er0,er0+=er4,rt"],["14fca","er0*=r2,er0+=er6,er10=er0,rt"],
    ["28C54","er0/=r2,rt"],["160c2","sp+=20"],["162d4","sp+=10"],["168f0","sp+=2"],
    ["1d3c8","sp+=4"],["09932","sp+=6,pop qr8"],["13184","sp+=50,pop qr8"],
    ["131f6","sp+=20,pop qr8"],["13320","sp+=30,pop qr8"],["15c76","sp+=30,pop er14"],
    ["1d3f2","sp+=2,r0=0"],["1d798","sp+=20,pop xr12"],["21634","sp+=10,pop er12"],
    ["21b9c","sp+=60,pop xr8"],["284ac","sp+=4,pop xr8"],["08f74","sp+=64,pop er6,pop qr8"],
    ["098ec","sp+=4,pop qr8,pop xr4"],["13412","sp+=40,pop qr8,pop xr4"],
    ["138a6","sp+=60,pop qr8,pop xr4"],["18266","sp+=50,pop qr8,pop xr4"],
    ["193a0","sp+=50,pop xr4,pop qr8"],["202b0","sp+=120,pop qr8,pop xr4"],
    ["20660","sp+=2,pop xr4,pop qr8"],["21b9a","sp+=120,pop xr8"],
    ["26b12","sp+=2,r0=1,pop er8"],["2122a","sp+=32,r2=r0,pop xr8"],
    ["18614","?r0=00"],["33030","brk"],["0d71c","[ea]+=1,r0=3"],["2c81e","[ea]-=1,pop xr4"],
    ["24836","B LEAVE"],["09450","BL memcpy,pop er0"],["203CC","BL strcpy"],
    ["203E0","BL strcat"],["09D3A","BL memset,pop er2"],["23CAC","BL delay,pop xr0"],
    ["20C40","BL line_print"],["23F62","BL printline"],["24004","BL hex_byte,er6=er0,er0=er8,pop qr8"],
    ["20A50","BL smart_strcpy,pop er8"],["0A052","BL zero_KO"],["28AC2","BL line_draw"],
    ["09AD4","BL render.ddd4"],["2B2BA","memcpy_auto_jmp"],["08f80","line_print"],
    ["25c1c","getkeycode"],["09E96","[ea+]=r0,r0-=1,bne"],["09C20","cmp_ea"],
    ["17922","calc_func"],["16082","cvt_hex_1"],["160f8","cvt_hex_2"],
    ["10f20","memcpy_length_rn/8"],["1700e","memcpy_length_rn/2,pop qr0"],["13324","pop pc"],
    ["0E5C8","strcpy"],["2EDA0","strcat"],["26FFA","memcpy"],["0A8AA","memmove"],
    ["29A2C","strlen"],["1EB94","memset"],["203C2","smart_strcpy"],["203D6","smart_strcat"],
    ["203B8","smart_strlen_n"],["2086C","basen_base_print"],["23DCC","smallprint"],
    ["08F7C","line_print.col_0"],["08F7E","line_print"],["23DC8","printline"],
    ["09470","render.e3d4"],["0947C","render.ddd4"],["09848","render_bitmap"],
    ["09D34","memzero"],["26086","reset_routine"],["24BD6","get_string_constant"],
    ["08C0C","fill_screen"],["08F02","str_decompress_print"],["09F3C","delay"],
    ["0A1CE","_start"],["293D8","main"],["09440","buf1_to_buf2"],["09458","buf2_to_buf1"],
    ["2AB26","byte_strlen_n"],["23C4C","diagnostic_mode"],["0ACB6","f_0ACB6"],
    ["0AD92","diagnostic_wait_key"],["0E826","check_any_key_pressed__"],["23CB4","diagnostic"],
    ["24344","diag_scr_888_ws"],["23DD6","diag_scr_fill_ws"],["23DDA","waitshift_striped"],
    ["23DDE","waitshift"],["23DE4","diag_scr_ckb1_ws"],["23E40","diag_scr_ckb2_ws"],
    ["23E6A","diag_scr_version"],["23E92","diag_print_ver"],["23EEE","diag_checksum"],
    ["23F8A","store_reg_to_stack"],["23EC8","diag_print_pd"],["23F9A","diag_calc_checksum"],
    ["09A24","pd_value"],["24010","hex_byte"],["16EAE","byte_hex"],["09938","hex_to_dec"],
    ["2541A","diag_serial_num"],["10E5E","get_serial_num"],["23D5A","diag_check_key"],
    ["2641A","diag_contrast"],["2C58A","diag_8_keytest"],["1F24E","getscancode"],
    ["2F5EA","getkey"],["25C1A","getkeycode"],["29892","cvt_key"],["0A0E0","setsfr"],
    ["19808","byte_to_bcd"],["19832","bcd_to_byte"],["08E62","line_draw"],["091FC","pixel_draw"],
    ["090D2","draw_glyph"],["2EDC8","line_print__call__"],["0996C","str_decompress_print__call__"],
    ["099C2","str_decompress_print__call1__"],["0904E","char_print_1byte"],["09056","char_print"],
    ["09238","char_get_14"],["09318","char_get_l14"],["0A16A","zero_KO"],["09DE6","assign_var"],
    ["08C60","buffer_clear"],["0AC30","ENTER"],["0AC38","LEAVE"],["224DE","LEAVE1"],
    ["22D66","LEAVE2"],["13D92","LEAVE3"],["2110A","LEAVE4"],["1652C","num_add"],
    ["16538","num_sub"],["16544","num_mul"],["16550","num_div"],["1D24A","num_add_1"],
    ["1D236","num_sub_1"],["1D272","num_mul_1"],["1D25E","num_div_1"],["20C46","num_output_print"],
    ["1D950","num_fromdigit"],["1DC2E","num_frombyte"],["1D898","num_invalid__"],
    ["1DBE2","num_trunc__"],["1DAF0","num_mulxp__"],["1391A","num_random"],["13A20","num_randint"],
    ["139D2","num_normalize"],["1DC8A","num_to_byte"],["1ED58","num_to_hex"],["279B6","num_to_str"],
    ["1DCE4","num_cpy"],["1D902","num_cmp"],["16844","num_sin"],["1684E","num_cos"],
    ["168E4","num_tan"],["2AD4C","display_menu"],["093D2","draw_byte"],
    ["2045c","pop xr4,pop xr12"],["1c696","[ea+] = er0"],["13622","pop qr8"],
    ["1fcf4","pop er4"], ["09d3e","pop er2"], ["10e80","pop ea, r6-=1_ne,call 10e6e|pop xr4"],
    ["1216a","pop er0"], ["17b34","pop xr0"], ["1622e","pop xr0"], ["08e64","line_draw"],
    ["13344","calc_func_verify"],["2F210","input_func"],["2E234","mode_calc"],
    ["1ED56","num_to_hex"],["1A6E4","setlr,er0 = 0,r2 = f3"],["23C90","pop qr0"],
    ["09E68","pop xr0"],["0E232","er0 = er8,pop er8"],["140E6","er2 = er12"],
    ["13AD8","er0 = er10,bl num_cpy"],["17BFA","er2 = er14, r1 = 3"],["09E48","er2 += er0,r0 = [er2]"],
    ["2245C","r1 = 0,pop er12"],["16070","xr0 = -xr0,rt"],["17BD8","[ea] = xr4"],
    ["17BF8","[ea] = xr12, er2 = er14, r1 = 3"],["17CAE","[ea+] = qr0, [ea+] = er8, rt"],
    ["17E7A","r10 = r11"],["17E7D","r11 = 0"],["2245A","r0 = r12, r1 = 0, pop er12"],
    ["1DF54","er2 = er0, er0 += er0, er0 += er2, er6 += er0"],["1DF9A","r5 += 1"],
    ["27FCE","r7 = 0"],["09FF8","var_m = r0, rt"],["0A06A","[ea+] = er0, [ea] = r0, rt"],
    ["0A07A","[ea+] = er2, [ea] = r2, rt"],["0A0A8","rt"],["0A0DA","setnormal"],
    ["0A0DC","setdelay"],["0A11C","setcursor"],["0A562","r0 = r4, pop er4"],
    ["0A594","er4 += 1"],["0A598","er8 += 1"],["0A908","er0 = er8, pop er4, pop er12, pop xr8, sp = er14, pop er14, rt"],
    ["0A930","r0 >> 2"],["0AA87","r10 = r6, r9 = r0"],["0AA88","r9 = r0"],
    ["0AA8A","r6 += 1"],["0AC58","r0 = r2, r0 -= r8"],["0AC7A","er12 = 0"],
    ["0ACFA","r6 = 0"],["0B4E0","r5 = r0"],["0B684","er4 = er0"],["0BDA2","er4 = er8, er6 = er2"],
    ["0BDA5","er6 = er2"],["0BE30","er8 -= 1"],["0BF2E","er2 += 1"],["1A5D0","or r7, r15"],
    ["1A610","[ea+] = xr4"],["28C5A","er8 = er0, er10 = er2"],["28C5C","er10 = er2"],
    ["272B8","r10 = 0"],["1C64C","qr8 = [ea]"],["279B8","num_to_str"],["1DC8C","num_to_byte"],
    ["1DC30","num_frombyte"]
]

GADGET_MAP = {}
for hex_addr, name in raw_gadget_list:
    num = int(hex_addr, 16)
    if num not in GADGET_MAP:
        GADGET_MAP[num] = re.sub(r'\s*([=+\-]|>>|<<|,)\s*', r'\1', name).strip()

NAME_MAP = {v: k for k, v in GADGET_MAP.items()}

MIN_VALID_CALL_ADDR = 0x8000

SPECIAL_NO_POP_GADGETS = {
    "sp=er14,pop er14,rt", "sp=er14,pop qr8", "sp=er14,pop qr8,pop qr0",
    "sp=er14,pop er14", "sp=er6,pop er8", "sp=er14,pop xr12",
    "sp=er14,pop qr8,pop er6", "sp+=6,pop qr8", "sp+=50,pop qr8",
    "sp+=20,pop qr8", "sp+=30,pop qr8", "sp+=30,pop er14", "sp+=2,r0=0",
    "sp+=20,pop xr12", "sp+=10,pop er12", "sp+=60,pop xr8", "sp+=4,pop xr8",
    "sp+=64,pop er6,pop qr8", "sp+=4,pop qr8,pop xr4", "sp+=40,pop qr8,pop xr4",
    "sp+=60,pop qr8,pop xr4", "sp+=50,pop qr8,pop xr4", "sp+=50,pop xr4,pop qr8",
    "sp+=120,pop qr8,pop xr4", "sp+=2,pop xr4,pop qr8", "sp+=120,pop xr8",
    "sp+=2,r0=1,pop er8", "sp+=32,r2=r0,pop xr8"
}

VALUE_TO_NAME = {
    0x0180: "key_shift", 0x0280: "key_alpha", 0x1080: "key_menu",
    0x0480: "key_up", 0x0840: "key_down", 0x0440: "key_left", 0x0880: "key_right",
    0x0140: "key_optn", 0x0240: "key_calc", 0x1040: "key_intg", 0x2040: "key_x",
    0x0120: "key_frac", 0x0220: "key_sqrt", 0x0420: "key_sqr", 0x0820: "key_power",
    0x1020: "key_logb", 0x2020: "key_inx", 0x0110: "key_neg", 0x0210: "key_deg",
    0x0410: "key_inv", 0x0810: "key_sin", 0x1010: "key_cos", 0x2010: "key_tan",
    0x0108: "key_sto", 0x0208: "key_eng", 0x0408: "key_lpar", 0x0808: "key_rpar",
    0x1008: "key_std", 0x2008: "key_addm", 0x4010: "key_0", 0x0101: "key_1",
    0x0201: "key_2", 0x0401: "key_3", 0x0102: "key_4", 0x0202: "key_5",
    0x0402: "key_6", 0x0104: "key_7", 0x0204: "key_8", 0x0404: "key_9",
    0x4008: "key_dot", 0x0804: "key_del", 0x1004: "key_ac", 0x4001: "key_exe",
    0x4002: "key_ans", 0x4004: "key_exp", 0x0801: "key_add", 0x1001: "key_sub",
    0x0802: "key_mul", 0x1002: "key_div",
    0x83DA: "adrcvtkey", 0xD000: "reg0", 0xD009: "reg0.9", 0xD110: "modifiers",
    0xD111: "mode", 0xD112: "submode", 0xD11A: "num_format", 0xD11B: "num_format_i",
    0xD11D: "angle_unit", 0xD138: "draw_mode", 0xD180: "input_range",
    0xD318: "unstable_char", 0xD31A: "var_m", 0xD324: "var_ans", 0xD32E: "var_a",
    0xD338: "var_b", 0xD342: "var_c", 0xD34C: "var_d", 0xD356: "var_e",
    0xD360: "var_f", 0xD36A: "var_x", 0xD374: "var_y", 0xD37E: "var_preans",
    0xD388: "var_z", 0xD392: "calc_history", 0xD139: "current_screen_buffer",
    0xDDD4: "screen_buffer", 0xD137: "font_size", 0xD113: "cursor_noflash",
    0xDBD0: "magic_string"
}
VALUE_TO_HEX = {v: k for k, v in VALUE_TO_NAME.items()}
HEX_PAIR = re.compile(r'^[0-9a-fA-F]{2}$')

def is_pure_pop_gadget(name):
    return bool(name and re.match(r'^pop\s+[a-z0-9]+$', name.strip(), re.IGNORECASE))

def get_pop_sizes(name):
    if not name:
        return None
    sizes = []
    for m in re.finditer(r'pop\s+([a-z0-9]+)', name, re.IGNORECASE):
        t = m.group(1).lower()
        if t in ('rt', 'pop', 'sp'): continue
        if t in ('ea', 'pc'): sizes.append(2)
        elif t == 'psw': sizes.append(1)
        elif t.startswith('qr'): sizes.extend([2]*4)
        elif t.startswith('xr'): sizes.extend([2]*2)
        elif t.startswith('er'): sizes.append(2)
        elif t.startswith('r'): sizes.append(1)
    return sizes if sizes else None

def get_pop_bytes_count(name):
    s = get_pop_sizes(name)
    return sum(s) if s else 0

def get_pop_registers(name):
    return [m.group(1) for m in re.finditer(r'pop\s+([a-z0-9]+)', name, re.IGNORECASE)]

def normalize_address(addr):
    if addr == 0x09c21: return 0x09c20
    if addr == 0x0947e: return 0x0947c
    if (addr & 1) and (addr - 1) in GADGET_MAP: return addr - 1
    return addr

def hex_to_bytes(h):
    c = h.replace(" ","").replace("\n","").replace("\r","")
    if not c: return []
    if len(c) % 2: c = c[:-1]
    return [int(c[i:i+2],16) for i in range(0,len(c),2)]

def parse_to_items(bytes_data, start_addr=0xd730):
    items = []
    offset = 0; i = 0
    while i < len(bytes_data):
        ra = start_addr + offset
        if i + 3 < len(bytes_data):
            zz, yy, third, fourth = bytes_data[i], bytes_data[i+1], bytes_data[i+2], bytes_data[i+3]
            if 0x30 <= third <= 0x39 and fourth == 0x30:
                X = third - 0x30
                raw = (X << 16) | (yy << 8) | zz
                if raw == 0x03030:
                    items.append({'type':'data','hexBytes':[zz],'value':zz,'ramAddr':ra})
                    offset+=1; ra=start_addr+offset
                    items.append({'type':'data','hexBytes':[yy],'value':yy,'ramAddr':ra})
                    i+=2; offset+=1; continue
                if raw < MIN_VALID_CALL_ADDR:
                    for b in [zz,yy,third,fourth]:
                        items.append({'type':'data','hexBytes':[b],'value':b,'ramAddr':ra})
                        offset+=1; ra=start_addr+offset
                    i+=4; continue
                fa = normalize_address(raw)
                name = GADGET_MAP.get(fa)
                items.append({'type':'call','hexBytes':[zz,yy,third,fourth],'addr':fa,'name':name,'ramAddr':ra,'popGrouped':False})
                i+=4; offset+=4
                if name and name not in SPECIAL_NO_POP_GADGETS:
                    ps = get_pop_sizes(name)
                    if ps:
                        tb = sum(ps)
                        if i + tb <= len(bytes_data):
                            for sz in ps:
                                for _ in range(sz):
                                    items.append({'type':'data','hexBytes':[bytes_data[i]],'value':bytes_data[i],'ramAddr':start_addr+offset})
                                    i+=1; offset+=1
                            continue
                continue
        items.append({'type':'data','hexBytes':[bytes_data[i]],'value':bytes_data[i],'ramAddr':ra})
        i+=1; offset+=1
    return items

def add_label_references(items):
    addr_to_idx = {}
    for idx, it in enumerate(items):
        if it['type'] == 'label': continue
        size = 4 if it['type'] == 'call' else len(it['hexBytes'])
        for b in range(size):
            addr_to_idx[it['ramAddr'] + b] = (idx, b)
            
    label_map = {}
    lc = 1
    i = 0
    while i < len(items) - 1:
        it0, it1 = items[i], items[i+1]
        if it0['type'] != 'data' or it1['type'] != 'data' or len(it0['hexBytes']) != 1 or len(it1['hexBytes']) != 1:
            i += 1; continue
            
        val = (it1['value'] << 8) | it0['value']
        target = addr_to_idx.get(val)
        
        if target is None:
            i += 1; continue
            
        tgt_idx, offset = target
        tgt_item = items[tgt_idx]
        base = tgt_item['ramAddr']
        
        if base not in label_map:
            label_map[base] = {'name': f'label{lc}', 'insert_idx': tgt_idx}
            lc += 1
            
        it0['labelRef'] = {'label': label_map[base]['name'], 'offset': offset}
        i += 2
        
    labels = []
    for addr, info in label_map.items():
        labels.append({'type': 'label', 'label': info['name'], 'insertBefore': info['insert_idx'], 'addr': addr})
        
    labels.sort(key=lambda x: x['insertBefore'], reverse=True)
    for li in labels:
        items.insert(li['insertBefore'], {'type': 'label', 'label': li['label'], 'addr': li['addr']})
        
    return items

def mark_pop_groups(items):
    i = 0
    while i < len(items):
        it = items[i]
        if it['type'] == 'call' and it['name'] and is_pure_pop_gadget(it['name']):
            tb = get_pop_bytes_count(it['name'])
            if tb > 0:
                b = 0; j = i + 1
                while j < len(items) and b < tb:
                    if items[j]['type'] == 'data':
                        b += len(items[j]['hexBytes'])
                    j += 1
                if b >= tb:
                    it['popGrouped'] = True
        i += 1
    return items

def format_simple(items):
    out = ["org 0xd730"]
    I = "    "
    i = 0
    while i < len(items):
        it = items[i]
        if it['type'] == 'label':
            out.append(f"{it['label']}:")
            i += 1
            continue
            
        if it['type'] == 'call':
            if it['name']:
                if is_pure_pop_gadget(it['name']) and it.get('popGrouped'):
                    tb = get_pop_bytes_count(it['name'])
                    regs = get_pop_registers(it['name'])
                    consumed = []
                    j = i + 1
                    b = 0
                    while j < len(items) and b < tb:
                        if items[j]['type'] == 'data':
                            consumed.append(items[j])
                            b += len(items[j]['hexBytes'])
                        j += 1
                        
                    vals = []
                    k = 0
                    while k < len(consumed):
                        c = consumed[k]
                        if 'labelRef' in c:
                            offset = c['labelRef'].get('offset', 0)
                            if offset != 0:
                                vals.append(f"adr_of [+{offset}] {c['labelRef']['label']}")
                            else:
                                vals.append(f"adr_of {c['labelRef']['label']}")
                            k += 2
                            continue
                            
                        if k + 1 < len(consumed) and 'labelRef' not in consumed[k+1]:
                            nxt = consumed[k+1]
                            dv = (nxt['value'] << 8) | c['value']
                            if dv in VALUE_TO_NAME:
                                vals.append(VALUE_TO_NAME[dv])
                            else:
                                hs = ' '.join(f'{b:02x}' for b in (c['hexBytes'] + nxt['hexBytes']))
                                vals.append(f"hex {hs}")
                            k += 2
                            continue
                            
                        hs = ' '.join(f'{b:02x}' for b in c['hexBytes'])
                        vals.append(f"hex {hs}")
                        k += 1
                        
                    out.append(f"{I}{', '.join(regs)} = {', '.join(vals)}")
                    i = j
                    continue
                else:
                    out.append(f"{I}{it['name']}")
            else:
                out.append(f"{I}call {it['addr']:05X}")
            i += 1
            continue
            
        if it['type'] == 'data':
            if 'labelRef' in it:
                offset = it['labelRef'].get('offset', 0)
                if offset != 0:
                    out.append(f"{I}adr_of [+{offset}] {it['labelRef']['label']}")
                else:
                    out.append(f"{I}adr_of {it['labelRef']['label']}")
                i += 2
                continue
                
            if i + 1 < len(items) and items[i+1]['type'] == 'data' and 'labelRef' not in items[i+1]:
                nxt = items[i+1]
                dv = (nxt['value'] << 8) | it['value']
                if dv in VALUE_TO_NAME:
                    out.append(f"{I}{VALUE_TO_NAME[dv]}")
                else:
                    hs = ' '.join(f'{b:02x}' for b in (it['hexBytes'] + nxt['hexBytes']))
                    out.append(f"{I}hex {hs}")
                i += 2
                continue
                
            hs = ' '.join(f'{b:02x}' for b in it['hexBytes'])
            out.append(f"{I}hex {hs}")
            i += 1
            continue
        i += 1
    return "\n".join(out)

def decompile(hex_str):
    bytes_data = hex_to_bytes(hex_str)
    if not bytes_data: return ""
    items = parse_to_items(bytes_data)
    items = add_label_references(items)
    items = mark_pop_groups(items)
    return format_simple(items)

def compile_asm(asm):
    lines = asm.strip().split("\n")
    
    # ------------------ Vòng 1: Quét Label & Tính địa chỉ bộ nhớ ------------------
    org_addr = 0xd730
    current_addr = org_addr
    labels = {}
    instructions = []
    
    for line in lines:
        line = line.split(";")[0].strip()
        if not line: continue
        
        if line.startswith("org "):
            try:
                org_str = line[4:].strip()
                org_addr = int(org_str, 16)
                current_addr = org_addr
            except: pass
            continue
            
        if line.endswith(":"):
            label_name = line[:-1].strip()
            labels[label_name] = current_addr
            continue
            
        instructions.append((line, current_addr))
        
        size = 0
        if line.startswith("hex "):
            size = len(line[4:].strip().split())
        elif line in NAME_MAP:
            size = 4
        elif line in VALUE_TO_HEX:
            size = 2
        elif re.match(r'^call\s+([0-9a-fA-F]+)$', line, re.IGNORECASE):
            size = 4
        elif "=" in line:
            parts = line.split("=", 1)[1].strip()
            for seg in parts.split(","):
                seg = seg.strip()
                if seg.startswith("hex "):
                    size += len(seg[4:].strip().split())
                elif seg.startswith("adr_of"):
                    size += 2
                elif seg in VALUE_TO_HEX:
                    size += 2
                elif HEX_PAIR.match(seg):
                    size += 1
                else:
                    raise ValueError(f"Không nhận diện được đối số gán: '{seg}'")
        else:
            tokens = line.replace(",", " ").split()
            i = 0
            while i < len(tokens):
                tok = tokens[i]
                if tok == "adr_of":
                    size += 2
                    if i + 1 < len(tokens) and tokens[i+1].startswith("[") and tokens[i+1].endswith("]"):
                        i += 3
                    else:
                        i += 2
                    continue
                elif tok in NAME_MAP:
                    size += 4
                elif tok in VALUE_TO_HEX:
                    size += 2
                elif HEX_PAIR.match(tok):
                    size += 1
                else:
                    raise ValueError(f"Lệnh hoặc token không hợp lệ: '{tok}'")
                i += 1

        current_addr += size

    # ------------------ Vòng 2: Sinh Assembly Hex theo bộ nhớ thực ------------------
    out = []
    for line, addr in instructions:
        if line.startswith("hex "):
            for p in line[4:].strip().split():
                out.append(f"{int(p,16):02x}")
            continue
            
        if line in NAME_MAP:
            addr_val = NAME_MAP[line]
            out.extend([f"{addr_val & 0xFF:02x}", f"{(addr_val >> 8) & 0xFF:02x}", f"{((addr_val >> 16) & 0xF) + 0x30:02x}", "30"])
            continue
            
        if line in VALUE_TO_HEX:
            v = VALUE_TO_HEX[line]
            out.extend([f"{v & 0xFF:02x}", f"{(v >> 8) & 0xFF:02x}"])
            continue
            
        call_match = re.match(r'^call\s+([0-9a-fA-F]+)$', line, re.IGNORECASE)
        if call_match:
            addr_val = int(call_match.group(1), 16)
            out.extend([f"{addr_val & 0xFF:02x}", f"{(addr_val >> 8) & 0xFF:02x}", f"{((addr_val >> 16) & 0xF) + 0x30:02x}", "30"])
            continue
            
        if "=" in line:
            parts = line.split("=", 1)[1].strip()
            for seg in parts.split(","):
                seg = seg.strip()
                if seg.startswith("hex "):
                    for p in seg[4:].strip().split():
                        out.append(f"{int(p,16):02x}")
                elif seg.startswith("adr_of"):
                    parts_adr = seg.split()
                    lname = parts_adr[-1]
                    laddr = labels.get(lname, 0)
                    if len(parts_adr) >= 3 and parts_adr[1].startswith("[") and parts_adr[1].endswith("]"):
                        offset_str = parts_adr[1][1:-1]
                        if offset_str.startswith("+"): laddr += int(offset_str[1:])
                        elif offset_str.startswith("-"): laddr -= int(offset_str[1:])
                        else: laddr += int(offset_str)
                    out.extend([f"{laddr & 0xFF:02x}", f"{(laddr >> 8) & 0xFF:02x}"])
                elif seg in VALUE_TO_HEX:
                    v = VALUE_TO_HEX[seg]
                    out.extend([f"{v & 0xFF:02x}", f"{(v >> 8) & 0xFF:02x}"])
                elif HEX_PAIR.match(seg):
                    out.append(f"{int(seg,16):02x}")
            continue
            
        tokens = line.replace(",", " ").split()
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok == "adr_of":
                if i + 1 < len(tokens):
                    offset = 0
                    if tokens[i+1].startswith("[") and tokens[i+1].endswith("]"):
                        offset_str = tokens[i+1][1:-1]
                        if offset_str.startswith("+"): offset = int(offset_str[1:])
                        elif offset_str.startswith("-"): offset = -int(offset_str[1:])
                        else: offset = int(offset_str)
                        if i + 2 < len(tokens):
                            lname = tokens[i+2]
                            i += 3
                        else:
                            raise ValueError("Thiếu tên label sau `adr_of`")
                    else:
                        lname = tokens[i+1]
                        i += 2
                        
                    laddr = labels.get(lname, 0) + offset
                    out.extend([f"{laddr & 0xFF:02x}", f"{(laddr >> 8) & 0xFF:02x}"])
                    continue
                else:
                    raise ValueError("`adr_of` bị thiếu đối số (cần truyền vào tên Label)")
                    
            if tok in NAME_MAP:
                addr_val = NAME_MAP[tok]
                out.extend([f"{addr_val & 0xFF:02x}", f"{(addr_val >> 8) & 0xFF:02x}", f"{((addr_val >> 16) & 0xF) + 0x30:02x}", "30"])
            elif tok in VALUE_TO_HEX:
                v = VALUE_TO_HEX[tok]
                out.extend([f"{v & 0xFF:02x}", f"{(v >> 8) & 0xFF:02x}"])
            elif HEX_PAIR.match(tok):
                out.append(f"{int(tok,16):02x}")
            i += 1
            
    return " ".join(out)

def extract_codeblock(text):
    text = text.strip()
    if text.startswith("```"):
        text = text[3:]
        idx = text.find("\n")
        if idx != -1:
            text = text[idx+1:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
    if text.startswith("`") and text.endswith("`") and not text.startswith("``"):
        return text[1:-1].strip()
    return text

def strip_asm_comments(text):
    lines = text.split("\n")
    clean = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith(";"):
            continue
        clean.append(line)
    return "\n".join(clean)

@bot.command(name="decomp")
async def decomp(ctx):
    _, _, content = ctx.message.content.partition("c!decomp")
    content = extract_codeblock(content)
    content = await get_input_text(ctx, content)
    if not content:
        await ctx.reply("❌ Cần hex để decompile. VD: `c!decomp FD 24 30 30` hoặc gửi file `.txt`")
        return
    try:
        result = decompile(content)
        await ctx.reply(f"```asm\n{result}\n```" if len(result) <= 1900 else f"```asm\n{result[:1900]}\n```")
    except Exception as e:
        await ctx.reply(f"❌ Lỗi khi giải mã: {e}")

@bot.command(name="comp")
async def comp(ctx):
    _, _, content = ctx.message.content.partition("c!comp")
    content = extract_codeblock(content)
    content = await get_input_text(ctx, content)
    if not content:
        await ctx.reply("❌ Cần assembly để compile. VD: `c!comp setlr` hoặc gửi file `.txt`")
        return
    content = strip_asm_comments(content)
    try:
        result = compile_asm(content)
        await ctx.reply(f"```\n{result}\n```" if len(result) <= 1900 else f"```\n{result[:1900]}\n```")
    except Exception as e:
        await ctx.reply(f"❌ Có lỗi cú pháp trong mã của bạn:\n> `{e}`")

@bot.command(name="comp5")
async def comp5(ctx):
    _, _, content = ctx.message.content.partition("c!comp5")
    content = extract_codeblock(content)
    content = await get_input_text(ctx, content)
    if not content:
        await ctx.reply("❌ Cần assembly để compile 580. VD: `c!comp5 setlr` hoặc gửi file `.txt`")
        return
    content = strip_asm_comments(content)
    asm = content.strip()
    if not asm.startswith("org "):
        asm = "org 0xD730\n" + asm
    try:
        result = subprocess.run(
            [sys.executable, HD580_COMPILER, "-f", "hex"],
            input=asm, capture_output=True, encoding="utf-8", errors="replace", timeout=30, cwd=HD580_DIR
        )
        if result.returncode != 0:
            raise Exception(result.stderr.strip().split("\n")[-1])
        lines = [l.strip() for l in result.stdout.split("\n") if l.strip()]
        hex_out = " ".join(lines[-1].split())
        await ctx.reply(f"```\n{hex_out}\n```")
    except Exception as e:
        await ctx.reply(f"❌ Lỗi compile 580:\n> `{e}`")

@bot.command(name="comp8")
async def comp8(ctx):
    _, _, content = ctx.message.content.partition("c!comp8")
    content = extract_codeblock(content)
    content = await get_input_text(ctx, content)
    if not content:
        await ctx.reply("❌ Cần assembly để compile 880. VD: `c!comp8 setlr` hoặc gửi file `.txt`")
        return
    content = strip_asm_comments(content)
    asm = content.strip()
    if not asm.startswith("org "):
        asm = "org 0xD730\n" + asm
    try:
        result = subprocess.run(
            [sys.executable, HD880_COMPILER, "-f", "hex"],
            input=asm, capture_output=True, encoding="utf-8", errors="replace", timeout=30, cwd=HD880_DIR
        )
        if result.returncode != 0:
            raise Exception(result.stderr.strip().split("\n")[-1])
        lines = [l.strip() for l in result.stdout.split("\n") if l.strip()]
        hex_out = " ".join(lines[-1].split())
        await ctx.reply(f"```\n{hex_out}\n```")
    except Exception as e:
        await ctx.reply(f"❌ Lỗi compile 880:\n> `{e}`")

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="⚙️ Casio Dao Truong - Danh sách lệnh",
        description="Tag bot (@Stacked) hoặc reply tin nhắn bot để hỏi về CASIO 580/880.\nDùng `c!help <lệnh>` để xem chi tiết từng lệnh.",
        color=0x00ff00
    )
    embed.add_field(name="🤖 Cơ bản", value="`c!join` - Vô kênh, auto rep\n`c!leave` - Rời kênh, chỉ rep khi tag/reply\n`c!dongmon` - Xem số member/bot\n`c!hoidap` - Hỏi đáp chủ đề CASIO\n`c!snipe` - Snipe tin nhắn đã xoá", inline=False)
    embed.add_field(name="🧠 Học tập", value="`c!learn <nd>` - Dạy bot ghi nhớ\n`c!study [sl]` - Quét tin nhắn học kiến thức", inline=False)
    embed.add_field(name="⚡ CASIO Engine", value="`c!decomp <hex>` - Decompile hex → asm\n`c!comp <asm>` - Compile asm → hex (gadget)\n`c!comp5 <asm>` - Compile asm → hex (580)\n`c!comp8 <asm>` - Compile asm → hex (880)\n`c!transhex <hex>` - Dịch hex ra asm", inline=False)
    embed.add_field(name="🖼️ P2B & Hex Tools", value="`c!p2b` / `c!p` - P2B Pro: Ảnh ⇄ Bitmap Hex\n`c!dichhex <hex>` - Dịch hex → ảnh bitmap\n`c!ganhex <hex>` - Format hex đẹp, chuẩn Casio\n`c!h2i [WxH] <hex>` - Hex → Image (tuỳ size)\n`c!hexsplit <hex>` - Split hex thành dòng", inline=False)
    embed.add_field(name="🔧 API Keys", value="`c!api <key>` - Set API key hiện tại\n`c!addkey <key>` - Thêm API key mới\n`c!addkeyat <index> <key>` - Ghi đè key tại vị trí\n`c!keys` - Xem danh sách API key\n`c!model <model>` - Đổi model AI", inline=False)
    embed.add_field(name="⚙️ Hệ thống", value="`c!reset` - Reset toàn bộ bot\n`c!restart` - Khởi động lại bot\n`c!file` - Quản lý file (list/view/delete)\n`c!console <#kênh>` - Bật console debug\n`c!help` - Xem danh sách lệnh", inline=False)
    embed.set_footer(text="Casio Đạo Trưởng · @Stacked · 24 lệnh | v2.0")
    await ctx.reply(embed=embed)

@bot.command(name="leave")
async def leave(ctx):
    if ctx.channel.id not in joined_channels:
        await ctx.reply("Mình đâu có ở trong kênh này đâu? 🤔")
    else:
        joined_channels.remove(ctx.channel.id)
        save_joined_channels(joined_channels)
        await ctx.reply("👋 Đã rời kênh! Giờ chỉ trả lời khi được tag hoặc reply thôi.")

@bot.command(name="dongmon")
async def dongmon(ctx):
    if not ctx.guild:
        await ctx.reply("❌ Lệnh này chỉ dùng trong server!")
        return
    members = []
    async for m in ctx.guild.fetch_members():
        members.append(m)
    total = len(members)
    bots = sum(1 for m in members if m.bot)
    humans = total - bots
    await ctx.reply(f"# Trong đây có {total} thằng đệ tử <:Daide_Putin:1483786083077455913>\n**{humans} Phàm nhân**\n**{bots} Bot đại đạo**")

HOIDAP_DATA = {
    "spell": "**Spell**\nĐánh vần chữ. Có thể spell 1-5 line font thường và 6-8 line font nhỏ.",
    "an": "**An**\nThứ không có khái niệm cụ thể nhưng lúc nào cũng dùng tới. Một số an: 100an, 124an, 136an,...",
    "small font": "**Small font**\nHàm `smallprint` (23DCC) in chữ font nhỏ 8x8.\n- r0: font size (08, 0a, 0e)\n- r1: linepos\n- er2: địa chỉ chuỗi",
    "quickcpy": "**Quick Copy**\nChương trình dùng để inject data, có nhiều phiên bản: qcm, qc++,... Phiên bản nâng cấp: hexdmax :/",
    "hex editor": "**Hex Editor / Hexd**\nChương trình dùng để inject data, có thể tuỳ chỉnh addr và hex tuỳ thích.",
    "inject": "**Inject**\nChương trình dùng để inject data. Có nhiều phiên bản: qcm, qc++,... Phiên bản nâng cấp: hexdmax :/",
    "addr": "**Địa chỉ (Address)**\n- 0xD730: runtime\n- 0xE9E0: backup\n- 0xD111: mode\n- 0xD137: font_size\n- 0xDDD4: screen buffer 1\n- 0xE3D4: screen buffer 2\n- 0xF033: độ sáng\n- 0xF039: scroll",
    "launcher": "**Launcher**\nDùng để chạy chương trình ROP từ màn hình tính toán:\n```\nFD24 30 30 DA 7B 31 30 FE 03 E0 E9 30 D7 2E D7 32 89 31 30 30 30 74 1F 32 48\n```\nẤn [=] để chạy.",
    "token": "**Token**\nToken trong CASIO là mã hex đại diện cho phép tính.\nVí dụ: `33 36 a6 36 37 00` là token của \"36+67\".",
    "hex": "**Hệ thập lục phân (Hex)**\nCơ số 16, dùng 0-9 và A-F.\n- `hex 00 01` = `0x0100` (little-endian)\n- `0x` đảo ngược với `hex`",
    "dec": "**Hệ thập phân (Dec)**\nCơ số 10, dùng 0-9.",
    "bin": "**Hệ nhị phân (Bin)**\nCơ số 2, chỉ dùng 0 và 1.",
    "rop": "**ROP (Return-Oriented Programming)**\nKỹ thuật nối các gadget (đoạn mã kết thúc bằng RT/POP PC) trên stack.\n- Gọi gadget qua `call <địa chỉ>`\n- Dữ liệu đặt ngay sau gadget trên stack",
    "asm": "**Assembly ASM**\nCác lệnh: MOV, ADD, SUB, L, ST, PUSH, POP, B, BL, RT.\nThanh ghi: R0-R15 (1B), ER0-ER14 (2B), XR0-XR12 (4B), QR0-QR8 (8B).",
    "bangkitu": "__bangkitu__",
    "store": "**Store / Ghi giá trị**\nDùng `xr0 = addr, value, pad` + `[er0]=r2` ghi 1 byte.\nDùng `xr0 = addr, v_high, v_low` + `[er0]=er2` ghi 2 byte.\nVùng backup: dùng `adr_of [+4784] label`."
}

class HoiDapSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=k, description=v.split("\n")[0][:50] if v != "__bangkitu__" else "Bảng kí tự CASIO")
            for k, v in HOIDAP_DATA.items()
        ]
        super().__init__(placeholder="Chọn chủ đề...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        key = self.values[0]
        val = HOIDAP_DATA[key]
        if key == "bangkitu":
            try:
                files_to_send = []
                for fn in ["1.webp", "wth.webp"]:
                    fp = os.path.join(BASE_DIR, fn)
                    if os.path.exists(fp):
                        files_to_send.append(discord.File(fp))
                if not files_to_send:
                    await interaction.response.send_message("❌ Không tìm thấy file ảnh (`1.webp`, `wth.webp`)", ephemeral=True)
                    return
                await interaction.response.send_message("**Bảng kí tự CASIO fx-580VN X:**", files=files_to_send, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ Lỗi: {e}", ephemeral=True)
        else:
            await interaction.response.send_message(val + "\n\n📚 Xem thêm `knowledge.txt` hoặc `c!learn`", ephemeral=True)

@bot.command(name="hoidap")
async def hoidap(ctx):
    view = discord.ui.View(timeout=120)
    view.add_item(HoiDapSelect())
    await ctx.reply("📌 **Chọn chủ đề:**", view=view)

@bot.command(name="snipe")
async def snipe(ctx):
    data = snipe_store.get(ctx.channel.id)
    if not data:
        await ctx.reply("Không có tin nhắn nào bị xóa gần đây.")
        return
    content = data["content"] or "(không có nội dung)"
    att = "\n" + "\n".join(data["attachments"]) if data["attachments"] else ""
    time_str = discord.utils.format_dt(data["time"], style="R")
    await ctx.reply(f"**{data['author'].name}** đã xóa: {time_str}\n{content}{att}")

@bot.command(name="console")
async def console(ctx, channel_id: str = None):
    global console_channel_id
    if not channel_id:
        if console_channel_id:
            ch = bot.get_channel(console_channel_id)
            await ctx.reply(f"Console chat đang gửi đến: #{ch.name}" if ch else f"ID: {console_channel_id}")
        else:
            await ctx.reply("Chưa set channel cho console chat. Dùng `c!console <channel_id>`")
        return
    try:
        cid = int(channel_id)
        ch = bot.get_channel(cid)
        if not ch:
            await ctx.reply("❌ Không tìm thấy channel với ID đó.")
            return
        console_channel_id = cid
        await ctx.reply(f"✅ Console chat sẽ gửi đến #{ch.name}")
        print(f"Console chat đã set → #{ch.name} ({cid})")
    except ValueError:
        await ctx.reply("❌ ID channel không hợp lệ.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    is_joined_channel = message.channel.id in joined_channels
    is_mentioned = bot.user.mentioned_in(message)
    is_reply_to_bot = (
        message.reference
        and isinstance(message.reference.resolved, discord.Message)
        and message.reference.resolved.author == bot.user
    )

    should_reply = is_joined_channel or is_mentioned or is_reply_to_bot

    if not should_reply:
        await bot.process_commands(message)
        return

    prompt = message.content

    if is_mentioned:
        prompt = prompt.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()

    if not prompt:
        if is_joined_channel or is_reply_to_bot:
            return
        await message.reply("Hửm? Bạn tag mình nhưng chưa hỏi gì kìa!")
        await bot.process_commands(message)
        return

    if prompt.startswith("c!"):
        await bot.process_commands(message)
        return

    if message.author.id in p2b_sessions:
        result = handle_p2b_command(message.author.id, prompt)
        if result is None:
            return
        if isinstance(result, str):
            await message.reply(result)
        elif isinstance(result, dict):
            f = result.get("file")
            e = result.get("embed")
            await message.reply(file=f, embed=e)
        elif isinstance(result, discord.Embed):
            await message.reply(embed=result)
        return

    file_match = re.search(r'`([^`]+\.txt)`|(?:xem|đọc|nội dung|file)\s+`?(\S+\.txt)`?', prompt, re.IGNORECASE)
    if file_match:
        fname = file_match.group(1) or file_match.group(2)
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
        if os.path.isfile(fpath):
            fcontent = load_file(fpath)
            if fcontent:
                prompt += f"\n\nNội dung file {fname}:\n```\n{fcontent[:4000]}\n```"

    # Read attached .txt files for AI context
    if message.attachments:
        for att in message.attachments:
            if att.filename.lower().endswith(".txt"):
                try:
                    data = await att.read()
                    txt_content = data.decode("utf-8", errors="replace")
                    prompt += f"\n\nFile {att.filename} của bạn:\n```\n{txt_content[:4000]}\n```"
                except Exception:
                    pass
                break

    user_context = get_user_context(message.author)
    if user_context:
        prompt = f"({user_context})\n{prompt}"

    async with message.channel.typing():
        try:
            cid = message.channel.id
            if cid not in conversation_memory:
                conversation_memory[cid] = []

            contents = conversation_memory[cid] + [
                types.Content(role="user", parts=[types.Part(text=prompt)])
            ]

            response = await call_gemini(
                model=MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=get_system_prompt()
                )
            )

            reply_text = fix_emoji(response.text, message.guild)

            conversation_memory[cid].append(
                types.Content(role="user", parts=[types.Part(text=prompt)])
            )
            conversation_memory[cid].append(
                types.Content(role="model", parts=[types.Part(text=reply_text)])
            )
            if len(conversation_memory[cid]) > MAX_MEMORY:
                conversation_memory[cid] = conversation_memory[cid][-MAX_MEMORY:]

            chunks = split_message(reply_text)
            try:
                dao_phu = discord.utils.get(message.guild.emojis, name='dao_phu')
                if dao_phu:
                    await message.add_reaction(dao_phu)
            except:
                pass
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await message.reply(chunk)
                else:
                    await message.channel.send(chunk)

        except Exception as e:
            err_str = str(e)
            print(f"Lỗi hệ thống khi gọi AI: {e}")
            if "does not support image" in err_str.lower() or "image input" in err_str.lower():
                await message.reply("⚠️ Model này không hỗ trợ ảnh. Vui lòng chỉ gửi tin nhắn chữ!")
            else:
                await message.reply("⚠️ Hết API key rồi, thử lại sau nhé!")

    await bot.process_commands(message)

# ================= P2B: Ảnh → Bitmap System =================
p2b_sessions = {}

def pil_to_bitmap(img, threshold=128, invert=False):
    arr = np.array(img.convert("L"), dtype=np.uint8)
    bits = (arr < threshold).astype(np.uint8)
    if invert:
        bits = 1 - bits
    return bits

def bitmap_to_hex_bytes(bits):
    h, w = bits.shape
    out = []
    for y in range(h):
        for x in range(0, w, 8):
            byte = 0
            for b in range(8):
                if x + b < w:
                    byte |= int(bits[y, x + b]) << (7 - b)
            out.append(f"{byte:02x}")
    return " ".join(out)

def _get_thumb_size(s):
    iw, ih = s["original"].size
    cw, ch = s["canvas_w"], s["canvas_h"]
    if iw > cw or ih > ch:
        ratio = min(cw / iw, ch / ih)
        iw = int(iw * ratio)
        ih = int(ih * ratio)
    return iw, ih

def bitmap_to_preview(bits, scale=4):
    h, w = bits.shape
    total_w = w * scale
    total_h = h * scale
    img = Image.new("RGB", (total_w, total_h), (255, 255, 255))
    px = img.load()
    for y in range(h):
        for x in range(w):
            c = (0, 0, 0) if bits[y, x] else (255, 255, 255)
            for dy in range(scale):
                for dx in range(scale):
                    px[x * scale + dx, y * scale + dy] = c
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, total_w - 1, total_h - 1], outline="red", width=2)
    buf = BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return buf

def apply_adjustments(img, adj):
    img = img.copy()
    for a in adj:
        t = a["type"]
        if t == "brightness":
            v = a["val"] / 150.0
            img = ImageEnhance.Brightness(img).enhance(1.0 + v)
        elif t == "contrast":
            v = a["val"] / 150.0
            img = ImageEnhance.Contrast(img).enhance(1.0 + v)
        elif t == "exposure":
            ev = a["val"]
            img = ImageEnhance.Brightness(img).enhance(2.0 ** ev)
        elif t == "levels":
            black, white, gamma = a["black"], a["white"], a.get("gamma", 1.0)
            arr = np.array(img.convert("L"), dtype=np.float32)
            arr = (arr - black) / max(white - black, 1)
            arr = np.clip(arr, 0, 1)
            if gamma != 1.0:
                arr = arr ** (1.0 / gamma)
            arr = (arr * 255).astype(np.uint8)
            img = Image.fromarray(arr, "L").convert("RGB")
        elif t == "clarity":
            v = a["val"] / 100.0
            blur = img.filter(ImageFilter.GaussianBlur(3))
            arr = np.array(img, dtype=np.float32)
            blur_arr = np.array(blur, dtype=np.float32)
            diff = arr - blur_arr
            img = Image.fromarray(np.clip(arr + diff * v, 0, 255).astype(np.uint8))
        elif t == "nr":
            k = max(1, int(a["val"] / 10))
            img = img.filter(ImageFilter.MedianFilter(k * 2 + 1))
        elif t == "grain":
            v = a["val"] / 100.0
            arr = np.array(img, dtype=np.float32)
            noise = np.random.randn(*arr.shape).astype(np.float32) * v * 50
            img = Image.fromarray(np.clip(arr + noise, 0, 255).astype(np.uint8))
        elif t == "highpass":
            r = max(1, a["val"])
            blur = img.filter(ImageFilter.GaussianBlur(r))
            arr = np.array(img, dtype=np.float32)
            blur_arr = np.array(blur, dtype=np.float32)
            hp = arr - blur_arr + 128
            img = Image.fromarray(np.clip(hp, 0, 255).astype(np.uint8))
        elif t == "emboss":
            img = img.filter(ImageFilter.EMBOSS)
        elif t == "smartsharpen":
            amt = a["amt"] / 100.0
            r = a.get("radius", 1)
            blur = img.filter(ImageFilter.GaussianBlur(r))
            arr = np.array(img, dtype=np.float32)
            blur_arr = np.array(blur, dtype=np.float32)
            sharp = arr + (arr - blur_arr) * amt
            img = Image.fromarray(np.clip(sharp, 0, 255).astype(np.uint8))
        elif t == "fieldblur":
            r = max(1, a["val"])
            img = img.filter(ImageFilter.GaussianBlur(r))
        elif t == "motionblur":
            r = max(1, a["val"])
            ang = a.get("angle", 0)
            if ang % 180 < 45 or ang % 180 > 135:
                kern = (1, r * 2 + 1)
            else:
                kern = (r * 2 + 1, 1)
            img = img.filter(ImageFilter.Kernel(kern, [1] * (kern[0] * kern[1])))
        elif t == "posterize":
            bits_val = max(2, min(20, a["val"]))
            img = ImageOps.posterize(img.convert("RGB"), bits_val)
        elif t == "equalize":
            img = ImageOps.equalize(img.convert("L")).convert("RGB")
        elif t == "clahe":
            clip = a["val"]
            arr = np.array(img.convert("L"), dtype=np.float32)
            h, w = arr.shape
            tile = 8
            for ty in range(0, h, tile):
                for tx in range(0, w, tile):
                    tile_arr = arr[ty:min(ty+tile,h), tx:min(tx+tile,w)]
                    hist, _ = np.histogram(tile_arr, 256, (0, 256))
                    clip_limit = clip * (tile*tile) / 256
                    excess = max(0, hist.sum() - clip_limit * 256)
                    hist = np.minimum(hist, clip_limit)
                    hist += excess / 256
                    cdf = hist.cumsum()
                    cdf = (cdf - cdf.min()) * 255 / max(cdf.max() - cdf.min(), 1)
                    tile_arr[:] = np.interp(tile_arr.flatten(), np.arange(256), cdf).reshape(tile_arr.shape)
            img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGB")
    return img

def apply_dither(arr, mode):
    h, w = arr.shape
    if mode == 2:
        out = (arr > 0.5).astype(np.float32)
    elif mode == 4:
        out = np.floor(arr * 4) / 3
    elif mode == 8:
        out = np.floor(arr * 8) / 7
    else:
        return (arr > 0.5).astype(np.float32)
    bayer2 = np.array([[0, 2], [3, 1]]) / 4
    bayer4 = np.kron(bayer2 * 4, bayer2)
    bayer8 = np.kron(bayer4 * 4, bayer2)
    if mode == 2:
        bayer = bayer2
    elif mode == 4:
        bayer = bayer4
    else:
        bayer = bayer8
    bayer = np.tile(bayer, (h // bayer.shape[0] + 1, w // bayer.shape[1] + 1))[:h, :w]
    return (arr > bayer).astype(np.float32)

def remove_bg_grabcut(img):
    try:
        import cv2
        arr = np.array(img)
        mask = np.zeros(arr.shape[:2], np.uint8)
        bgd = np.zeros((1, 65), np.float64)
        fgd = np.zeros((1, 65), np.float64)
        h, w = arr.shape[:2]
        rect = (2, 2, w - 4, h - 4)
        cv2.grabCut(arr, mask, rect, bgd, fgd, 3, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype(np.uint8)
        result = arr * mask2[:, :, np.newaxis] + (255 * (1 - mask2[:, :, np.newaxis])).astype(np.uint8)
        return Image.fromarray(result)
    except ImportError:
        return img

def build_p2b_embed(s, bits):
    total = s["canvas_w"] * s["canvas_h"]
    on_px = int(bits.sum())
    adj_list = s["adjustments"]
    adj_str = ", ".join(f"{a['type']}={a.get('val','')}" for a in adj_list) if adj_list else "*none*"
    dt = s.get("dither", 0)
    embed = discord.Embed(title="🖼️ P2B Bitmap", color=0x5865f2)
    embed.add_field(name="📐 Canvas", value=f"{s['canvas_w']}×{s['canvas_h']}", inline=True)
    embed.add_field(name="📷 Ảnh gốc", value=f"{s['original'].size[0]}×{s['original'].size[1]}", inline=True)
    embed.add_field(name="📍 Vị trí", value=f"({s['pos_x']}, {s['pos_y']})", inline=True)
    embed.add_field(name="⚙️ Threshold", value=str(s['threshold']), inline=True)
    embed.add_field(name="🔄 Invert", value="✅" if s['invert'] else "❌", inline=True)
    embed.add_field(name="🎲 Dither", value=str(dt) if dt > 0 else "❌", inline=True)
    embed.add_field(name="🔲 Pixels bật", value=f"{on_px}/{total} ({on_px*100//total}%)", inline=False)
    embed.add_field(name="🎨 Adjustments", value=adj_str, inline=False)
    embed.set_footer(text=f"UID: {id(s)} | Gõ help để xem lệnh, exit để thoát")
    return embed

def build_p2b_xong_embed(bits, w, h):
    hex_out = bitmap_to_hex_bytes(bits)
    total = w * h
    on_px = int(bits.sum())
    embed = discord.Embed(title="✅ P2B Done!", color=0x57f287)
    embed.add_field(name="📐 Canvas", value=f"{w}×{h}", inline=True)
    embed.add_field(name="🔲 Pixels bật", value=f"{on_px}/{total} ({on_px*100//total}%)", inline=True)
    embed.add_field(name="📝 Hex", value=f"```\n{hex_out[:1024]}\n```" if len(hex_out) > 1024 else f"```\n{hex_out}\n```", inline=False)
    if len(hex_out) > 1024:
        embed.add_field(name="📎 Tiếp theo", value=f"Còn {len(hex_out)-1024} ký tự hex nữa", inline=False)
    return embed

def process_p2b(s):
    img = s["original"].copy()
    cw, ch = s["canvas_w"], s["canvas_h"]
    iw, ih = img.size
    if iw > cw or ih > ch:
        img.thumbnail((cw, ch), Image.LANCZOS)
        iw, ih = img.size
    px = min(s["pos_x"], max(0, cw - iw))
    py = min(s["pos_y"], max(0, ch - ih))
    canvas = Image.new("RGB", (cw, ch), (255, 255, 255))
    canvas.paste(img, (px, py))
    img = canvas
    img = apply_adjustments(img, s["adjustments"])
    gray = img.convert("L")
    arr = np.array(gray, dtype=np.float32)
    dt = s.get("dither", 0)
    if dt > 0:
        arr = apply_dither(arr / 255.0, dt) * 255
    bits = (arr < s["threshold"]).astype(np.uint8)
    if s["invert"]:
        bits = 1 - bits
    s["bits"] = bits
    s["processed_image"] = img
    return bits

def build_p2b_help():
    embed = discord.Embed(title="📖 P2B Pro - Image ⇄ Bitmap Hex", color=0x5865f2)
    embed.add_field(name="🌐 Web Tool (khuyên dùng)", value="Mở file `picture to bitmap/index.html` trong browser:\n• Ảnh → Hex: kéo thả ảnh, chỉnh threshold/invert/filters, xuất hex\n• Hex → Ảnh: dán hex space-separated, xem preview bitmap\n• Auto-detect: Ctrl+V tự nhận diện ảnh hay hex\n• Tích hợp slider, zoom, xuất file .h", inline=False)
    embed.add_field(name="📍 Vị trí", value="`move <x> <y>` · `center` · `topleft` · `topright` · `bottomleft` · `bottomright`\n`size <WxH>`", inline=False)
    embed.add_field(name="🎨 Adjustments", value="`brightness <-150~150>` · `contrast <-150~150>`\n`exposure <-5.0~5.0>`\n`levels <black> <white> [gamma]`\n`clarity <-100~100>` · `nr <0-100>` · `grain <0-100>`", inline=False)
    embed.add_field(name="🔧 Filters", value="`smartsharpen <amt> [radius]` · `fieldblur <1-50>`\n`motionblur <1-50> [angle]` · `highpass <1-100>`\n`emboss` · `posterize <2-20>` · `equalize`\n`clahe <1.0-10.0>` · `removebg`", inline=False)
    embed.add_field(name="⚙️ Khác", value="`threshold <0-255>` · `invert` · `dither <2/4/8>`\n`reset` · `xong` · `exit`\n\n💡 **Hex → Ảnh trên chat:** gửi hex kèm `c!p2b` để auto decode", inline=False)
    return embed

SIZE_RE = re.compile(r'^size\s+(\d+)x(\d+)$', re.IGNORECASE)

@bot.command(name="p2b")
async def p2b(ctx):
    uid = ctx.author.id
    if not ctx.message.attachments:
        if uid in p2b_sessions:
            del p2b_sessions[uid]
        await ctx.reply("📷 Gửi ảnh kèm theo `c!p2b` để convert bitmap.\n" + build_p2b_help())
        return
    att = ctx.message.attachments[0]
    if not att.filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
        await ctx.reply("❌ Chỉ hỗ trợ PNG/JPG/BMP/GIF.")
        return
    img_data = await att.read()
    try:
        pil_img = Image.open(BytesIO(img_data)).convert("RGB")
    except Exception:
        await ctx.reply("❌ Không đọc được ảnh.")
        return
    s = {
        "original": pil_img.copy(),
        "img": pil_img,
        "canvas_w": 192, "canvas_h": 63,
        "pos_x": 0, "pos_y": 0,
        "threshold": 128, "invert": False,
        "adjustments": [],
        "dither": 0,
        "bits": None,
        "processed_image": None,
        "msg_id": None,
    }
    p2b_sessions[uid] = s
    bits = process_p2b(s)
    embed = build_p2b_embed(s, bits)
    preview = bitmap_to_preview(bits)
    file = discord.File(preview, "preview.png")
    embed.set_image(url="attachment://preview.png")
    view = P2BTutorialButton()
    msg = await ctx.reply(file=file, embed=embed, view=view)
    s["msg_id"] = msg.id

class P2BTutorialButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="📖 Hướng dẫn P2B", style=discord.ButtonStyle.secondary)
    async def tutorial(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = build_p2b_help()
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name="p")
async def p(ctx):
    uid = ctx.author.id
    text = ctx.message.content[len("c!p"):].strip()
    has_session = uid in p2b_sessions

    if not text and not ctx.message.attachments:
        if not has_session:
            await ctx.reply("📷 Gửi ảnh kèm `c!p` để convert bitmap.\nHoặc dùng `c!p <lệnh>` nếu đang trong session.", view=P2BTutorialButton())
        return

    if ctx.message.attachments:
        att = ctx.message.attachments[0]
        if not att.filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            await ctx.reply("❌ Chỉ hỗ trợ PNG/JPG/BMP/GIF.")
            return
        img_data = await att.read()
        try:
            pil_img = Image.open(BytesIO(img_data)).convert("RGB")
        except Exception:
            await ctx.reply("❌ Không đọc được ảnh.")
            return
        p2b_sessions[uid] = {"original": pil_img.copy(), "img": pil_img, "canvas_w": 192, "canvas_h": 63, "pos_x": 0, "pos_y": 0, "threshold": 128, "invert": False, "adjustments": [], "dither": 0, "bits": None, "processed_image": None, "msg_id": None}
        bits = process_p2b(p2b_sessions[uid])
        embed = build_p2b_embed(p2b_sessions[uid], bits)
        preview = bitmap_to_preview(bits)
        file = discord.File(preview, "preview.png")
        embed.set_image(url="attachment://preview.png")
        msg = await ctx.reply(file=file, embed=embed, view=P2BTutorialButton())
        p2b_sessions[uid]["msg_id"] = msg.id
        return

    if has_session:
        result = handle_p2b_command(uid, text)
        if result is None:
            return
        if isinstance(result, str):
            await ctx.reply(result)
        elif isinstance(result, dict):
            f = result.get("file")
            e = result.get("embed")
            xf = result.get("extra_files", [])
            all_f = [f] + xf if f else xf
            await ctx.reply(files=all_f, embed=e)
        elif isinstance(result, discord.Embed):
            await ctx.reply(embed=result)
        return

    await ctx.reply("❌ Bạn chưa có session P2B. Gửi ảnh kèm `c!p` để bắt đầu.", view=P2BTutorialButton())

def handle_p2b_command(uid, text):
    s = p2b_sessions.get(uid)
    if not s:
        return None
    text_stripped = text.strip().lower()
    parts = text_stripped.split()
    cmd = parts[0] if parts else ""

    if cmd == "exit":
        del p2b_sessions[uid]
        return "👋 Đã thoát P2B."
    if cmd == "help":
        return build_p2b_help()

    changed = False
    if cmd == "move" and len(parts) >= 3:
        try:
            s["pos_x"] = max(0, int(parts[1]))
            s["pos_y"] = max(0, int(parts[2]))
            changed = True
        except: pass
    elif cmd == "center":
        cw, ch = s["canvas_w"], s["canvas_h"]
        iw, ih = _get_thumb_size(s)
        s["pos_x"] = max(0, (cw - iw) // 2)
        s["pos_y"] = max(0, (ch - ih) // 2)
        changed = True
    elif cmd in ("topleft",):
        s["pos_x"] = s["pos_y"] = 0; changed = True
    elif cmd == "topright":
        cw = s["canvas_w"]
        iw, ih = _get_thumb_size(s)
        s["pos_x"] = max(0, cw - iw); s["pos_y"] = 0; changed = True
    elif cmd == "bottomleft":
        ch = s["canvas_h"]
        iw, ih = _get_thumb_size(s)
        s["pos_x"] = 0; s["pos_y"] = max(0, ch - ih); changed = True
    elif cmd == "bottomright":
        cw, ch = s["canvas_w"], s["canvas_h"]
        iw, ih = _get_thumb_size(s)
        s["pos_x"] = max(0, cw - iw); s["pos_y"] = max(0, ch - ih); changed = True
    elif cmd == "size" and len(parts) >= 2:
        m = SIZE_RE.match(text_stripped)
        if m:
            s["canvas_w"] = max(1, min(500, int(m.group(1))))
            s["canvas_h"] = max(1, min(500, int(m.group(2))))
            changed = True
        else:
            return "❌ Sai cú pháp! Dùng `size <rộng>x<cao>` (vd: `size 192x63`)"
    elif cmd == "threshold" and len(parts) >= 2:
        try:
            s["threshold"] = max(0, min(255, int(parts[1])))
            changed = True
        except: pass
    elif cmd == "invert":
        s["invert"] = not s["invert"]; changed = True
    elif cmd == "dither" and len(parts) >= 2:
        try:
            v = int(parts[1])
            s["dither"] = v if v in (2, 4, 8) else 0; changed = True
        except: pass
    elif cmd == "brightness" and len(parts) >= 2:
        try:
            v = max(-150, min(150, int(parts[1])))
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "brightness"]
            s["adjustments"].append({"type": "brightness", "val": v}); changed = True
        except: pass
    elif cmd == "contrast" and len(parts) >= 2:
        try:
            v = max(-150, min(150, int(parts[1])))
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "contrast"]
            s["adjustments"].append({"type": "contrast", "val": v}); changed = True
        except: pass
    elif cmd == "exposure" and len(parts) >= 2:
        try:
            v = max(-5.0, min(5.0, float(parts[1])))
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "exposure"]
            s["adjustments"].append({"type": "exposure", "val": v}); changed = True
        except: pass
    elif cmd == "levels" and len(parts) >= 3:
        try:
            blk = max(0, min(255, int(parts[1])))
            wht = max(0, min(255, int(parts[2])))
            gam = float(parts[3]) if len(parts) >= 4 else 1.0
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "levels"]
            s["adjustments"].append({"type": "levels", "black": blk, "white": wht, "gamma": gam})
            changed = True
        except: pass
    elif cmd == "clarity" and len(parts) >= 2:
        try:
            v = max(-100, min(100, int(parts[1])))
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "clarity"]
            s["adjustments"].append({"type": "clarity", "val": v}); changed = True
        except: pass
    elif cmd == "nr" and len(parts) >= 2:
        try:
            v = max(0, min(100, int(parts[1])))
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "nr"]
            s["adjustments"].append({"type": "nr", "val": v}); changed = True
        except: pass
    elif cmd == "grain" and len(parts) >= 2:
        try:
            v = max(0, min(100, int(parts[1])))
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "grain"]
            s["adjustments"].append({"type": "grain", "val": v}); changed = True
        except: pass
    elif cmd == "smartsharpen" and len(parts) >= 2:
        try:
            amt = max(0, min(1000, int(parts[1])))
            rad = int(parts[2]) if len(parts) >= 3 else 1
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "smartsharpen"]
            s["adjustments"].append({"type": "smartsharpen", "amt": amt, "radius": rad})
            changed = True
        except: pass
    elif cmd == "fieldblur" and len(parts) >= 2:
        try:
            v = max(1, min(50, int(parts[1])))
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "fieldblur"]
            s["adjustments"].append({"type": "fieldblur", "val": v}); changed = True
        except: pass
    elif cmd == "motionblur" and len(parts) >= 2:
        try:
            v = max(1, min(50, int(parts[1])))
            ang = float(parts[2]) if len(parts) >= 3 else 0
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "motionblur"]
            s["adjustments"].append({"type": "motionblur", "val": v, "angle": ang})
            changed = True
        except: pass
    elif cmd == "highpass" and len(parts) >= 2:
        try:
            v = max(1, min(100, int(parts[1])))
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "highpass"]
            s["adjustments"].append({"type": "highpass", "val": v}); changed = True
        except: pass
    elif cmd == "emboss":
        existing = any(a["type"] == "emboss" for a in s["adjustments"])
        if existing:
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "emboss"]
        else:
            s["adjustments"].append({"type": "emboss"})
        changed = True
    elif cmd == "posterize" and len(parts) >= 2:
        try:
            v = max(2, min(20, int(parts[1])))
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "posterize"]
            s["adjustments"].append({"type": "posterize", "val": v}); changed = True
        except: pass
    elif cmd == "equalize":
        existing = any(a["type"] == "equalize" for a in s["adjustments"])
        if existing:
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "equalize"]
        else:
            s["adjustments"].append({"type": "equalize"})
        changed = True
    elif cmd == "clahe" and len(parts) >= 2:
        try:
            v = max(1.0, min(10.0, float(parts[1])))
            s["adjustments"] = [a for a in s["adjustments"] if a["type"] != "clahe"]
            s["adjustments"].append({"type": "clahe", "val": v}); changed = True
        except: pass
    elif cmd == "removebg":
        if "original_backup" not in s:
            s["original_backup"] = s["original"].copy()
        s["original"] = remove_bg_grabcut(s["original"])
        changed = True
    elif cmd == "reset":
        s["adjustments"] = []; s["dither"] = 0
        s["threshold"] = 128; s["invert"] = False
        s["pos_x"] = s["pos_y"] = 0
        s["canvas_w"] = 192; s["canvas_h"] = 63
        if "original_backup" in s:
            s["original"] = s["original_backup"]
        changed = True
    elif cmd == "xong":
        bits = process_p2b(s)
        embed = build_p2b_xong_embed(bits, s["canvas_w"], s["canvas_h"])
        file = discord.File(bitmap_to_preview(bits), "preview.png")
        embed.set_image(url="attachment://preview.png")
        hex_str = bitmap_to_hex_bytes(bits)
        hex_bytes = hex_str.encode("utf-8")
        hex_file = discord.File(BytesIO(hex_bytes), "bitmap_hex.txt")
        del p2b_sessions[uid]
        return {"file": file, "embed": embed, "extra_files": [hex_file]}

    if changed:
        bits = process_p2b(s)
        embed = build_p2b_embed(s, bits)
        preview = bitmap_to_preview(bits)
        file = discord.File(preview, "preview.png")
        embed.set_image(url="attachment://preview.png")
        return {"file": file, "embed": embed}

    return None

def hex_to_image(hex_str, width, height):
    hex_str = hex_str.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
    img_data = []
    for i in range(0, len(hex_str), 2):
        byte = int(hex_str[i:i+2], 16)
        for bit in range(7, -1, -1):
            img_data.append(255 if (byte >> bit) & 1 else 0)
    while len(img_data) < width * height:
        img_data.append(0)
    img = Image.new('L', (width, height))
    img.putdata(img_data[:width*height])
    buf = BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return buf

async def get_input_text(ctx, inline_text):
    if inline_text:
        return inline_text
    if ctx.message.attachments:
        att = ctx.message.attachments[0]
        if att.filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")):
            return None
        data = await att.read()
        return data.decode("utf-8", errors="replace")
    return None

@bot.command(name="h2i")
async def h2i(ctx, *, args=None):
    width, height = 192, 63
    hex_data = None
    if args:
        parts = args.split()
        try:
            width = int(parts[0])
            height = int(parts[1])
            hex_data = " ".join(parts[2:]) if len(parts) > 2 else None
        except (ValueError, IndexError):
            hex_data = args
    hex_data = await get_input_text(ctx, hex_data)
    if not hex_data:
        await ctx.reply("❌ Cần hex data. VD: `c!h2i FF 00 AA` hoặc gửi file `.txt` kèm lệnh")
        return
    try:
        hex_data = hex_data or ""
        hex_clean = hex_data.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
        if not hex_clean:
            await ctx.reply("❌ Ko có dữ liệu hex!")
            return
        if not all(c in "0123456789abcdefABCDEF" for c in hex_clean):
            matches = re.findall(r'\b[0-9a-fA-F]{2}\b', hex_data)
            hex_clean = "".join(matches)
            if not hex_clean:
                await ctx.reply("❌ Hex ko hợp lệ! Chỉ gồm 0-9 A-F.")
                return
        if len(hex_clean) % 2 != 0:
            await ctx.reply("❌ Hex phải có độ dài chẵn!")
            return
        buf = hex_to_image(hex_clean, width, height)
        file = discord.File(buf, "bitmap.png")
        embed = discord.Embed(title="🖼️ Hex → Image", color=0x5865f2)
        embed.add_field(name="📐 Kích thước", value=f"{width}×{height}", inline=True)
        embed.set_image(url="attachment://bitmap.png")
        await ctx.reply(file=file, embed=embed)
    except Exception as e:
        await ctx.reply(f"❌ Lỗi: {e}")

@bot.command(name="hexsplit")
async def hexsplit(ctx, *, hex_str=None):
    hex_str = await get_input_text(ctx, hex_str)
    if not hex_str:
        await ctx.reply("❌ Cần hex để split. VD: `c!hexsplit FD243030DA7B3130` hoặc gửi file `.txt`")
        return
    hex_str = hex_str.replace(" ", "").replace("\n", "")
    if not all(c in "0123456789abcdefABCDEF" for c in hex_str):
        await ctx.reply("❌ Hex ko hợp lệ!")
        return
    bytes_list = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
    lines = []
    for i in range(0, len(bytes_list), 16):
        addr = i
        chunk = bytes_list[i:i+16]
        hex_part = " ".join(chunk)
        ascii_part = "".join(chr(int(b, 16)) if 32 <= int(b, 16) < 127 else "." for b in chunk)
        lines.append(f"{addr:04X}  {hex_part:<48} {ascii_part}")
    result = "\n".join(lines)
    await ctx.reply(f"```\n{result[:1900]}\n```" if len(result) > 1900 else f"```\n{result}\n```")

@bot.command(name="transhex")
async def transhex(ctx, *, hex_str=None):
    hex_str = await get_input_text(ctx, hex_str)
    if not hex_str:
        await ctx.reply("❌ Cần hex để dịch. VD: `c!transhex FD 24 30 30` hoặc gửi file `.txt`")
        return
    try:
        result = decompile(hex_str)
        await ctx.reply(f"```asm\n{result[:1900]}\n```" if len(result) > 1900 else f"```asm\n{result}\n```")
    except Exception as e:
        await ctx.reply(f"❌ Lỗi dịch hex: {e}")

@bot.command(name="dichhex")
async def dichhex(ctx, *, hex_str=None):
    hex_str = await get_input_text(ctx, hex_str)
    if not hex_str:
        await ctx.reply("❌ Cần hex để dịch. VD: `c!dichhex 00 FF 00 FF` hoặc gửi file `.txt`")
        return
    try:
        hex_str = hex_str.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
        bytes_list = [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]
        total_bits = len(bytes_list) * 8
        width = 192
        height = total_bits // width
        if height == 0 or total_bits % width != 0:
            height = len(bytes_list)
            width = 8
        elif height > 200:
            height = total_bits // 192
        buf = hex_to_image(hex_str, width, height)
        file = discord.File(buf, "bitmap.png")
        embed = discord.Embed(title="🖼️ Dịch Hex → Bitmap", color=0x5865f2)
        embed.add_field(name="📐 Kích thước", value=f"{width}×{height}", inline=True)
        embed.add_field(name="📦 Bytes", value=str(len(bytes_list)), inline=True)
        embed.set_image(url="attachment://bitmap.png")
        hex_formatted = " ".join(f"{b:02X}" for b in bytes_list[:48])
        if len(bytes_list) > 48:
            hex_formatted += "..."
        embed.add_field(name="📝 Hex", value=f"```\n{hex_formatted}\n```", inline=False)
        await ctx.reply(file=file, embed=embed)
    except Exception as e:
        await ctx.reply(f"❌ Lỗi: {e}")

@bot.command(name="ganhex")
async def ganhex(ctx, *, hex_str=None):
    hex_str = await get_input_text(ctx, hex_str)
    if not hex_str:
        await ctx.reply("❌ Cần hex để gán. VD: `c!ganhex FD243030DA7B3130FE03E0E930D7`")
        return
    hex_str = hex_str.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
    if not all(c in "0123456789abcdefABCDEF" for c in hex_str):
        await ctx.reply("❌ Hex ko hợp lệ! Chỉ gồm 0-9 A-F.")
        return
    bytes_list = [hex_str[i:i+2] for i in range(0, len(hex_str), 2)]
    lines = []
    for i in range(0, len(bytes_list), 24):
        chunk = bytes_list[i:i+24]
        lines.append(" ".join(chunk))
    result = "\n".join(lines)
    await ctx.reply(
        f"```\n{result[:1900]}\n```" if len(result) > 1900 else f"```\n{result}\n```",
        file=discord.File(result.encode(), "hex_data.txt")
    )

# Auto-chat: thỉnh thoảng chat linh tinh ở kênh joined
auto_chat_topics = [
    "hỏi thăm mọi người trong kênh hôm nay thế nào",
    "kêu ca về thời tiết hôm nay",
    "nói gì đó về chính trị thế giới kiểu báo mới",
    "kể chuyện vui về đời sống",
    "hỏi có ai cần giúp gì về CASIO ko",
    "nói mấy câu Gen Z láo láo về cuộc sống",
]

@tasks.loop(hours=2)
async def auto_chat_loop():
    if not joined_channels:
        return
    channel_id = random.choice(joined_channels)
    ch = bot.get_channel(channel_id)
    if not ch:
        return
    topic = random.choice(auto_chat_topics)
    try:
        prompt = f"Hãy nói {topic}, chỉ 1-2 câu, phong cách Gen Z, láo láo tí, ko cần kiến thức CASIO. Có thể dùng emoji."
        resp = await call_gemini(model=MODEL, contents=prompt, max_retries=1)
        text = fix_emoji(resp.text.strip(), ch.guild if hasattr(ch, 'guild') else None)
        await ch.send(text)
    except:
        pass

@auto_chat_loop.before_loop
async def before_auto_chat():
    await bot.wait_until_ready()

if __name__ == "__main__":
    if not DISCORD_TOKEN or not GEMINI_API_KEY:
        print("LỖI: Vui lòng kiểm tra lại cấu hình DISCORD_TOKEN và GEMINI_API_KEY trong file .env!")
    elif not MODEL:
        print("LỖI: Vui lòng kiểm tra biến MODEL trong file .env!")
    else:
        def console_chat():
            while True:
                try:
                    text = sys.stdin.readline()
                    if not text:
                        break
                    text = text.strip()
                    if text and console_channel_id:
                        ch = bot.get_channel(console_channel_id)
                        if ch:
                            coro = ch.send(text)
                            asyncio.run_coroutine_threadsafe(coro, bot.loop)
                            print(f"[Console] Đã gửi: {text[:50]}...")
                except Exception as e:
                    print(f"[Console] Lỗi: {e}")
        t = threading.Thread(target=console_chat, daemon=True)
        t.start()
        bot.run(DISCORD_TOKEN)

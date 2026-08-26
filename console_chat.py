import discord
import asyncio
import sys
import os

token = input("Nhap token: ").strip()
if not token:
    print("Thieu token")
    sys.exit(1)

channel_id = input("Nhap channel ID: ").strip()
if not channel_id:
    print("Thieu channel ID")
    sys.exit(1)
try:
    channel_id = int(channel_id)
except ValueError:
    print("Channel ID khong hop le")
    sys.exit(1)

os.environ["DISCORD_TOKEN"] = token

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"\n[Dang nhap] {client.user}")
    ch = client.get_channel(channel_id)
    if ch:
        print(f"[Channel] #{ch.name} ({channel_id})")
    else:
        print(f"[Khong tim thay channel] ID: {channel_id}")
    print("[Go tin nhan va Enter de gui, Ctrl+C de thoat]\n")

    loop = asyncio.get_running_loop()
    while True:
        text = await loop.run_in_executor(None, sys.stdin.readline)
        text = text.strip()
        if text:
            target = client.get_channel(channel_id)
            if target:
                await target.send(text)
                print(f"[Gui #{target.name if hasattr(target,'name') else channel_id}] {text[:60]}")
            else:
                print(f"[Khong tim thay channel]")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id == channel_id:
        print(f"[{message.author.name}] #{message.channel.name} ({message.channel.id}): {message.content}")

try:
    client.run(token)
except KeyboardInterrupt:
    print("\nThoat")
except Exception as e:
    print(f"Loi: {e}")

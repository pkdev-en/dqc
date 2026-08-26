import discord
import asyncio
import sys

token = input("Nhap token: ").strip()
if not token:
    print("Thieu token")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

selected_guild = None
selected_channel = None

PERM_NAMES = {
    "send_messages": "Gui tin nhan",
    "read_messages": "Doc tin nhan",
    "read_message_history": "Doc lich su",
    "manage_messages": "Quan ly tin nhan",
    "manage_channels": "Quan ly kenh",
    "kick_members": "Kick thanh vien",
    "ban_members": "Ban thanh vien",
    "administrator": "Administrator",
    "manage_guild": "Quan ly server",
    "view_channel": "Xem kenh",
    "attach_files": "Dinh file",
    "embed_links": "Embed link",
    "mention_everyone": "Mention @everyone",
    "mute_members": "Mute",
    "deafen_members": "Deafen",
    "move_members": "Di chuyen",
    "manage_roles": "Quan ly role",
    "manage_webhooks": "Quan ly webhook",
    "create_instant_invite": "Tao invite"
}

KEY_PERMS = ["administrator", "manage_guild", "kick_members", "ban_members", "manage_messages", "manage_channels", "manage_roles", "manage_webhooks"]

@client.event
async def on_ready():
    global selected_guild, selected_channel
    print(f"\n[Dang nhap] {client.user} (ID: {client.user.id})")
    print()

    guilds = list(client.guilds)
    if not guilds:
        print("Bot khong o server nao")
        await client.close()
        return

    print("=== DANH SACH SERVER ===")
    for i, g in enumerate(guilds):
        me = g.me or g.get_member(client.user.id)
        gp = me.guild_permissions if me else discord.Permissions.none()
        print(f"\n[{i}] {g.name} (ID: {g.id})")
        print(f"    Owner: {g.owner}")
        print(f"    Members: {g.member_count}")
        has_key = [n for n, v in PERM_NAMES.items() if getattr(gp, n, False)]
        if has_key:
            print(f"    Quyen quan trong: {', '.join(PERM_NAMES[n] for n in has_key)}")

        channels = [c for c in g.channels if isinstance(c, discord.TextChannel)]
        print(f"    Text channels: {len(channels)}")
        for c in channels[:5]:
            cp = c.permissions_for(me) if me else discord.Permissions.none()
            marks = []
            for n in KEY_PERMS:
                if getattr(cp, n, False):
                    marks.append(PERM_NAMES[n].split(" ")[0])
            print(f"      #{c.name} (ID: {c.id}) - {', '.join(marks) if marks else 'co ban'}")

    print()
    while True:
        try:
            idx = int(input(f"Chon server (0-{len(guilds)-1}): ").strip())
            selected_guild = guilds[idx]
            break
        except:
            print("Nhap lai")

    channels = [c for c in selected_guild.channels if isinstance(c, discord.TextChannel)]
    print(f"\n=== KENH TRONG {selected_guild.name} ===")
    for i, c in enumerate(channels):
        me = selected_guild.me or selected_guild.get_member(client.user.id)
        cp = c.permissions_for(me) if me else discord.Permissions.none()
        can_send = cp.send_messages and cp.view_channel
        marks = []
        for n in KEY_PERMS:
            if getattr(cp, n, False):
                marks.append(PERM_NAMES[n])
        print(f"[{i}] #{c.name} (ID: {c.id}) {'✅' if can_send else '❌'}")
        if marks:
            print(f"    Quyen: {', '.join(marks)}")

    print()
    while True:
        try:
            idx = int(input(f"Chon kenh (0-{len(channels)-1}): ").strip())
            selected_channel = channels[idx]
            break
        except:
            print("Nhap lai")

    me = selected_guild.me or selected_guild.get_member(client.user.id)
    cp = selected_channel.permissions_for(me) if me else discord.Permissions.none()
    if not cp.send_messages or not cp.view_channel:
        print(f"\n❌ Bot khong co quyen gui tin nhan trong #{selected_channel.name}")
        await client.close()
        return

    print(f"\n✅ Da chon #{selected_channel.name} | {selected_guild.name}")
    print("[Go tin nhan Enter de gui, Ctrl+C de thoat]\n")

    loop = asyncio.get_running_loop()
    while True:
        text = await loop.run_in_executor(None, sys.stdin.readline)
        text = text.strip()
        if not text:
            continue
        try:
            if text.startswith("!"):
                await selected_channel.send(text[1:])
            else:
                await selected_channel.send(text)
            print(f"[Da gui] #{selected_channel.name}: {text[:60]}")
        except Exception as e:
            print(f"[Loi] {e}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if selected_channel and message.channel.id == selected_channel.id:
        print(f"[{message.author.name}] {message.content[:100]}")

try:
    client.run(token)
except KeyboardInterrupt:
    print("\nThoat")
except Exception as e:
    print(f"Loi: {e}")

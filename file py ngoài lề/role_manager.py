import discord
import asyncio
import sys

token = input("Nhap token: ").strip()
if not token:
    print("Thieu token"); sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"\n[Dang nhap] {client.user}")

    guilds = list(client.guilds)
    if not guilds:
        print("Bot khong o server nao"); await client.close(); return

    print("\n=== SERVER ===")
    for i, g in enumerate(guilds):
        me = g.me or g.get_member(client.user.id)
        gp = me.guild_permissions if me else discord.Permissions.none()
        can = gp.manage_roles or gp.administrator
        print(f"[{i}] {g.name} {'' if can else '(❌ KO CO QUYEN manage_roles)'}")

    await menu_loop(guilds)
    await client.close()

async def input_async(prompt):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: input(prompt).strip())

async def menu_loop(guilds):
    while True:
        try:
            idx = int(await input_async("\nChon server: "))
            g = guilds[idx]
            break
        except: print("Nhap lai")

    me = g.me or g.get_member(client.user.id)
    gp = me.guild_permissions if me else discord.Permissions.none()
    if not gp.manage_roles and not gp.administrator:
        print(f"\n❌ Bot khong co quyen Manage Roles trong {g.name}")
        return

    print(f"\n✅ Co quyen Manage Roles trong {g.name}")

    while True:
        print(f"\n=== {g.name} ===")
        print("1. Xem danh sach role")
        print("2. Tim user (theo ten/ID)")
        print("3. Them role cho user")
        print("4. Xoa role khoi user")
        print("5. Xem role cua user")
        print("0. Thoat")

        c = await input_async("Chon: ")
        if c == "0": break

        elif c == "1":
            roles = sorted(g.roles, key=lambda r: r.position, reverse=True)
            print(f"\nRoles ({len(roles)}):")
            for r in roles:
                if r.is_default(): continue
                bot_has = me.top_role > r if me else False
                print(f"  {r.name} (ID: {r.id}) - #{r.color.value:06x} - {len(r.members)} members{' ✅' if bot_has else ' ❌ bot thap hon'}")

        elif c == "2":
            q = await input_async("Nhap ten hoac ID: ")
            members = []
            async for m in g.fetch_members(limit=None):
                if q.lower() in m.name.lower() or q.lower() in (m.display_name or "").lower() or q == str(m.id):
                    members.append(m)
            for m in members[:20]:
                roles_str = ", ".join(r.name for r in m.roles if not r.is_default()) or "(none)"
                print(f"  {m.name} (ID: {m.id}) - {roles_str}")

        elif c == "3":
            uid = await input_async("Nhap user ID: ")
            try: user = await g.fetch_member(int(uid))
            except: print("Ko tim thay user"); continue
            print(f"User: {user.name}")
            role_name = await input_async("Nhap ten role can them: ")
            role = discord.utils.get(g.roles, name=role_name)
            if not role:
                print(f"Ko tim thay role '{role_name}'"); continue
            if not (me and me.top_role > role):
                print("❌ Bot ko the gan role cao hon hoac bang top role cua bot"); continue
            await user.add_roles(role, reason="Role manager tool")
            print(f"✅ Da them role '{role.name}' cho {user.name}")

        elif c == "4":
            uid = await input_async("Nhap user ID: ")
            try: user = await g.fetch_member(int(uid))
            except: print("Ko tim thay user"); continue
            print(f"User: {user.name}")
            roles = [r for r in user.roles if not r.is_default()]
            if not roles: print("User ko co role nao"); continue
            print("Roles cua user:")
            for i, r in enumerate(roles):
                print(f"  [{i}] {r.name} (ID: {r.id})")
            try:
                idx2 = int(await input_async("Chon role can xoa: "))
                role = roles[idx2]
            except: print("Ko hop le"); continue
            if not (me and me.top_role > role):
                print("❌ Bot ko the xoa role cao hon top role cua bot"); continue
            await user.remove_roles(role, reason="Role manager tool")
            print(f"✅ Da xoa role '{role.name}' khoi {user.name}")

        elif c == "5":
            uid = await input_async("Nhap user ID: ")
            try: user = await g.fetch_member(int(uid))
            except: print("Ko tim thay user"); continue
            roles = [r.name for r in user.roles if not r.is_default()]
            print(f"\nRoles cua {user.name}: {', '.join(roles) if roles else '(none)'}")

try:
    client.run(token)
except KeyboardInterrupt:
    print("\nThoat")
except Exception as e:
    print(f"Loi: {e}")

# CasioAI - Huong dan Setup (Tutorial)

## 1. Yeu cau
- Python 3.11+
- Git
- Discord Bot Token (https://discord.com/developers/applications)
- Gemini API Key (https://aistudio.google.com/app/apikey)

## 2. Clone project
```bash
git clone https://github.com/sarsvankelsion/casioai.git
cd casioai
```

## 3. Tao moi truong
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

requirements: discord.py, google-genai, python-dotenv, Pillow, numpy, opencv-python

## 4. Cau hinh .env
Copy file mau:
```bash
cp .env.example .env
# Windows: copy .env.example .env
```
Mo `.env` va dien:
```
DISCORD_TOKEN=token_bot_discord_cua_ban
GEMINI_API_KEY=key_gemini_cua_ban
MODEL=gemini-2.0-flash
```
* Neu co nhieu key Gemini, tao file `api_keys.txt` moi dong 1 key, bot se tu rotate khi het quota

## 5. Chay bot
```bash
python bot.py
# hoac
bash start.sh
```

## 6. Cau truc file quan trong
- `bot.py` - bot chinh
- `persona.txt` - tinh cach AI
- `knowledge.txt` - kien thuc CASIO
- `api_keys.txt` - (khong commit) danh sach key
- `serviceAccount.json` - (khong commit) Firebase service account neu dung

## 7. Luu y bao mat
- KHONG commit `.env`, `api_keys.txt`, `serviceAccount.json` - da co trong `.gitignore`
- Neu lo commit, dung `git rm --cached <file>` de go

## 8. Cac lenh bot chinh
- `c!help` - xem help
- `c!comp <asm>` / `c!decomp <hex>` - bien dich CASIO
- `c!p` - chuyen anh sang bitmap hex
- `c!learn <noi dung>` - day bot

## 9. Day len GitHub moi (neu fork)
```bash
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

# MUHAMMADAZIZ WEB SAYTI

## Nimalar bor
- 7 ta kurs
- Har kursda 10 ta dars
- Har testda 25 ta savol
- Online umumiy reyting
- 10 tadan kam natija = ❌ JARIMA
- Admin panel: `/admin`
- Jarima bo‘lsa Telegram xabari (ixtiyoriy)
- SQLite lokal ishlash uchun
- PostgreSQL Render uchun

## Lokal ishga tushirish
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
So‘ng: http://127.0.0.1:5000

## Render Environment Variables
Quyidagilarni Render → Environment Variables ga qo‘shing:

- `DATABASE_URL` = Render PostgreSQL Internal Database URL
- `SECRET_KEY` = uzun maxfiy tasodifiy matn
- `ADMIN_PASSWORD` = o‘zingiz belgilaydigan admin parol

Telegram xabari kerak bo‘lsa:
- `TELEGRAM_BOT_TOKEN` = BotFather bergan bot token
- `TELEGRAM_CHAT_ID` = sizning Telegram chat ID

Admin panel: `https://SIZNING-SAYTINGIZ.onrender.com/admin`

## GitHub ga yuklash
Repository ichida quyidagi tuzilma saqlansin:
```
app.py
requirements.txt
.python-version
.gitignore
README_UZ.md
templates/index.html
templates/admin.html
templates/admin_login.html
static/style.css
```

`rating.db` ni GitHub ga yuklamang. Render online ishlaganda PostgreSQL ishlatiladi.

# MUHAMMADAZIZ WEB SAYTI — online versiya

## 1. Kompyuterda ishga tushirish

PowerShell:

```powershell
cd "MUHAMMADAZIZ_WEB_SAYTI_ONLINE"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Brauzerda: http://127.0.0.1:5000

## 2. Nima o‘zgardi?

- Telefon, planshet va kompyuter ekranlariga mos responsive dizayn.
- Dars oynasining ichki scrolli saqlangan.
- Test natijasi `/api/rating` orqali serverga yuboriladi.
- Reyting barcha qurilmalarda bir xil bo‘lishi uchun PostgreSQL qo‘llab-quvvatlanadi.
- `DATABASE_URL` bo‘lmasa, lokalda `rating.db` ishlaydi.

## 3. Jarima va Admin panel

- Yangi test: **⌨️ Ctrl tezkor tugmalari** (25 ta savol).
- Istalgan testda **10 tadan kam** to‘g‘ri javob bo‘lsa, **10 000 so‘m** jarima yoziladi.
  Qoida `app.py` boshidagi `MIN_PASS_SCORE` va `FINE_AMOUNT` qiymatlarida.
- Admin panel: `/admin` (login ixtiyoriy, **parol** = `ADMIN_PASSWORD`).
  Unda barcha natijalar, xabarlar, jarimalar va "to‘langan/to‘lanmagan" holati bor.
- `ADMIN_PASSWORD` o‘rnatilmasa, admin panel yopiq turadi.

Lokalda (PowerShell):

```powershell
$env:ADMIN_PASSWORD="o'zingizning_parolingiz"
python app.py
```

Render'da: Web Service → Environment → `ADMIN_PASSWORD` qo‘shing.

## 4. Internetga chiqarish

Render Web Service uchun:
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Python: `.python-version` orqali 3.13

Render Postgres yaratib, uning Internal Database URL qiymatini Web Service'dagi `DATABASE_URL` environment variable'iga qo‘ying.

GitHub repository tuzilmasi:

```
MUHAMMADAZIZ_WEB_SAYTI_ONLINE/
├── app.py
├── requirements.txt
├── .python-version
├── templates/
│   ├── index.html
│   └── admin.html
└── static/
    └── style.css
```

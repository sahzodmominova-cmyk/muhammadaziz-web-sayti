# EduStar integratsiyasi — texnik qaydlar

## Ishga tushirish
1. Python 3.11+ o‘rnating.
2. Loyihaning ushbu papkasida virtual muhit yarating:
   `py -m venv .venv`
3. Windows PowerShell: ` .\.venv\Scripts\Activate.ps1`
4. `pip install -r requirements.txt`
5. Admin parolini muhit o‘zgaruvchisi sifatida belgilang:
   `$env:ADMIN_PASSWORD="uzun_va_noyob_parol"`
6. `python app.py` va `http://127.0.0.1:5000` manzilini oching.
7. EduStar sahifasi: `/edustar`. Admin API'lari HTTP Basic autentifikatsiyasi bilan himoyalangan.

## Ma’lumotlar
- Eski `rating.db` yoki `DATABASE_URL` bazasidagi `ratings` jadvaliga tegilmaydi.
- Yangi EduStar funksiyalari hozircha alohida `edustar.db` SQLite bazasidan foydalanadi; u birinchi ishga tushishda yaratiladi.
- `edustar.db` faylini muntazam zaxiralang. Deploy muhiti vaqtinchalik fayl tizimiga ega bo‘lsa, doimiy disk yoki PostgreSQL migratsiyasi kerak.

## Yangi API yo‘llari
- `GET /api/edustar/lessons?grade=5&quarter=1&subject=Matematika`
- `POST /api/edustar/progress` — `student`, `lesson_id`, `percent`
- `GET /api/edustar/profile?student=Ism`
- `POST /api/admin/edustar/lessons` — admin bilan himoyalangan
- `GET /api/edustar/battle/categories`
- `POST /api/admin/edustar/battle/categories`
- `POST /api/admin/edustar/battle` — 1–3 guruh, aynan 30 savol va 6 bonus savolni tekshiradi
- `POST /api/admin/edustar/battle/<id>/start`
- `GET /api/edustar/battle/<id>` — to‘g‘ri javoblar ommaga yuborilmaydi
- `POST /api/edustar/battle/<id>/answer`
- `POST /api/admin/edustar/battle/<id>/finish`
- `GET /api/admin/edustar/battle/<id>/events`

## Muhim holat
Bu versiyada integratsiyaning backend asosi qo‘shildi, lekin talabnomadagi barcha imkoniyatlar hali yakunlanmagan. Xususan, o‘quvchi uchun to‘liq autentifikatsiya, admin uchun vizual kontent boshqaruvi, kategoriya tahrirlash/o‘chirish, bonus/jarima ehtimollarini to‘liq boshqarish UI'si, guruh ishtirokchilarini boshqarish, vaqt bo‘yicha server-side javobni yopish, barcha guruh rejimlari va to‘liq yakuniy hisobot interfeysi hali ishlab chiqilishi kerak. Shu sababli loyiha to‘liq tayyor mahsulot sifatida emas, mavjud saytni buzmasdan qo‘shilgan dastlabki integratsiya sifatida topshiriladi.


## Ushbu yangilanish
- EduStar Battle bo‘limida musobaqa ID kiritish olib tashlandi; sahifa eng yangi faol musobaqani avtomatik topadi.
- Fanlar bo‘limida 1–4-chorakning har biriga mavzu ko‘rsatiladi. Qo‘shimcha mavzular hozircha boshlang‘ich namuna materiallari; to‘liq rasmiy darslik mazmuni deb qabul qilinmasin.

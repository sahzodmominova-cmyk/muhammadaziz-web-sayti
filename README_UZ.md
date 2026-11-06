# V4: o‘quv dasturini kengaytirish (davom etadi)
- **5 va 6-sinf darslik darajasida kengaytirildi** (5-sinf: 190, 6-sinf: 260 mavzu). Jami 1180 mavzu. 1–4 va 7–11-sinflar hali qisqartirilgan reja; ular navbat bilan kengaytiriladi.
- **Mavzularni tahrirlash oson:** `tools/kurikulum.txt` ni oching (har satr = bitta fan), so‘ng `python tools/build_kurikulum.py` — u xatolarni tekshirib `static/kurikulum.js` ni yangilaydi.
- Rasmiy darslik/KTR bilan solishtirib, mavzularni to‘g‘rilab boring. Dars matni va test hozircha 10 ta mavzuda bor.

---

# V3 yangiliklari (1–11-sinf o‘quv dasturi, xatolarni tuzatish)

## EduStar: 1–11-sinf o‘quv dasturi
- **20 ta fan, 110 ta fan–sinf juftligi, 866 ta mavzu** (`static/kurikulum.js`). Sinf tanlovi endi 1–11 va u haqiqatan fanlar ro‘yxati hamda mavzularni almashtiradi (masalan, kimyo 7-sinfdan, algebra va geometriya 7-sinfdan, astronomiya 11-sinfda).
- Mavzular choraklarga teng taqsimlanadi; «Barcha choraklar» ko‘rinishi qo‘shildi. Progress tanlangan sinf bo‘yicha hisoblanadi, tanlangan sinf eslab qolinadi.
- Tayyor dars matni va testi bor 10 ta mavzu o‘z sinfiga ulangan (nomi bo‘yicha). Qolganlarida «dars matni hali qo‘shilmagan» deb ochiq yoziladi, «Darsni tugatdim» tugmasi ishlaydi, test tugmasi yashiriladi.
- **Muhim:** mavzular nomlari **umumiy o‘quv dasturi asosida tuzilgan reja** bo‘lib, rasmiy darsliklar bilan solishtirilmagan. Maktabingiz darsligiga qarab `static/kurikulum.js` ni tahrirlang. Dars matni va savollar hozircha faqat 10 ta mavzuda bor.
- «Mantiq» fani olib tashlandi (standart maktab fani emas); tarix «Jahon tarixi» va «O‘zbekiston tarixi»ga ajratildi.

## Topilgan va tuzatilgan xatolar
- Choraklar bo‘sh chiqardi (mavzu `i+1`-chorakka bog‘langan edi), sinf tanlovi hech narsani o‘zgartirmasdi.
- **API:** JSON tanasi obyekt bo‘lmasa (matn, son) 54 ta joyda 500 xato berardi. Endi barcha marshrutlarda `json_body()` ishlatiladi.
- **Telefon:** EduStar sahifasi ekrandan kengroq (470px) edi; bosiladigan joylar juda kichik edi; kichik matn 14px ga keltirildi.
- Bosh sahifadagi qattiq yozilgan sonlar («16 fan», «10 o‘yin g‘oyasi») haqiqiy sonlar bilan almashtirildi.
- **Animatsiya:** «⏸ Animatsiyani o‘chirish» tugmasi qo‘shildi (tanlov eslab qolinadi); tizimning «animatsiyani kamaytirish» sozlamasi hurmat qilinadi.

## Tekshiruv
`python -m unittest discover -s tests` — 21 ta test (reyting himoyasi, musobaqa kodlari, hamma marshrutlarga axlat ma’lumot yuborish, o‘quv dasturi tuzilmasi). Brauzerda: 866 mavzu kartochkasi, 8 kursning barcha darsi va testi, telefon ko‘rinishi sinab ko‘rilgan.

---

# V2 yangiliklari (xavfsizlik, serverga ulanish, Ctrl kursi)

## Nima o‘zgardi
- **Sayt serverga ulandi.** Test boshlanganda server imzolangan sessiya beradi, yakunda javoblar serverga yuboriladi va **ball serverda tekshiriladi**. Reyting endi barcha qurilmalarda bir xil (`/api/rating/overall`); aloqa bo‘lmasa, natija faqat shu brauzerda saqlanadi.
- **Soxta natijaga qarshi himoya:** sessiyasiz yuborish rad etiladi, imzo o‘zgartirilsa rad etiladi, bir sessiya bilan faqat bir marta yozish mumkin, 25 savolga kamida `TEST_MIN_SECONDS` (45) soniya kerak, IP bo‘yicha so‘rovlar cheklangan.
- **Umumiy reyting** endi har kurs bo‘yicha **eng yaxshi** natijani hisoblaydi (takroriy topshirish reytingni oshirmaydi).
- **Parolsiz `/test-violation` o‘chirildi.** Mijoz yuborgan `violation` bayrog‘i endi hisobga olinmaydi (boshqa odamga jarima yozish yo‘li yopildi).
- **Admin panel:** soxta yoki xato yozuvni o‘chirish tugmasi (🗑) qo‘shildi.
- **Yangi kurs: ⌨️ Ctrl tezkor tugmalari** (6 dars, 54 savol; testda 25 tasi tasodifiy tanlanadi).
- **EduStar musobaqa:** har guruhga maxfiy kod (admin yaratganda javobda qaytadi), javob yuborishda `group_code` shart. Noto‘g‘ri ma’lumotda 500 o‘rniga 400 qaytadi.
- Xavfsizlik sarlavhalari, `EDUSTAR_DB_PATH` (Render doimiy disk uchun), `.gitignore` to‘ldirildi, ichki dublikat arxiv va bo‘sh bazalar olib tashlandi.
- Haqiqiy API testlari: `python -m unittest discover -s tests` (16 ta test).

## Muhit o‘zgaruvchilari
| Nomi | Vazifasi |
|---|---|
| `ADMIN_PASSWORD` | Admin panel paroli (bo‘sh bo‘lsa admin yopiq) |
| `SECRET_KEY` | Test sessiyalarini imzolash. **Bir nechta gunicorn worker bo‘lsa, albatta o‘rnating** |
| `TEST_MIN_SECONDS` | Testga kamida ketadigan vaqt (standart 45) |
| `EDUSTAR_DB_PATH` | EduStar bazasi yo‘li (Render doimiy diskida, masalan `/data/edustar.db`) |
| `DATABASE_URL` | PostgreSQL (reyting uchun) |

Musobaqa guruh kodi: musobaqa yaratilganda javobdagi `groups[].code` ni har guruhga bering; guruh javob yuborganda so‘rovga `"group_code": "KOD"` qo‘shiladi.

## Savollarni o‘zgartirsangiz
To‘g‘ri javoblar kaliti `quiz_key.json` da. `templates/index.html` dagi savollar o‘zgarsa, `tools/export_quiz_key.py` bilan kalitni yangilang (ichidagi ko‘rsatma bor).

## Hali bajarilmagan (ma’lum cheklovlar)
- EduStar dars/progress sahifasi hali backend'ga ulanmagan (`edustar.js` ichidagi ma’lumot bilan ishlaydi); EduStar admin interfeysi yo‘q; 16 fandan faqat 5 tasida dars mazmuni bor.
- Musobaqada savol vaqtini server tekshirmaydi.
- Akkaunt yo‘q: ism ixtiyoriy yoziladi, shu sabab kimdir boshqa ism bilan test topshirishi mumkin (admin yozuvni o‘chira oladi). To‘liq yechim: o‘quvchiga PIN/akkaunt.
- Savollar hali sahifa ichida, shuning uchun javoblarni sahifa manbasidan ko‘rib olish mumkin. To‘liq yechim: savollarni serverga ko‘chirish.
- IP bo‘yicha cheklov har jarayon uchun alohida ishlaydi.
- Eski 10 savollik AI testi faqat shu qurilmada saqlanadi.
- O‘quvchilarga pul jarimasi yozilishi va ismlarning ommaviy reytingda ko‘rinishi maktab/ota-onalar bilan kelishilgan bo‘lishi kerak.

---

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


## EduStar qo‘shimchasi
Batafsil API, ma’lumotlar bazasi va hali bajarilishi kerak bo‘lgan ishlar: `EDUSTAR_INTEGRATSIYA_UZ.md`.

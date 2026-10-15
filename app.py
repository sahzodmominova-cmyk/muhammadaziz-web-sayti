import json
import hmac
import os
import random
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, Response, jsonify, render_template, request

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, "rating.db")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ---- Jarima qoidasi -------------------------------------------------------
# 25 tadan shundan KAM to'g'ri javob bo'lsa, quyidagi ro'yxatdan bitta jarima
# TASODIFIY tanlanadi (pul jarimasi yoki vazifa-jarima bo'lishi mumkin).
# "amount" > 0 bo'lgani pul jarimasi hisoblanadi, "amount" == 0 bo'lgani esa
# vazifa-jarima (pulsiz) hisoblanadi.
TOTAL_QUESTIONS = 25
MIN_PASS_SCORE = 10
PENALTIES = [
    {"amount": 5000, "label": "5 000 so‘m jarima"},
    {"amount": 10000, "label": "10 000 so‘m jarima"},
    {"amount": 0, "label": "2 ta dars davomida kompyuterga o‘tirmaslik"},
    {"amount": 0, "label": "1 hafta davomida telefonda o‘yin o‘ynamaslik"},
    {"amount": 0, "label": "Sinf doskasini 2 kun tozalash"},
]

# ---- Qidiruv tizimlari (SEO) ----------------------------------------------
# Sayt manzili o'zgarsa (masalan o'z domeningiz), Render'da SITE_URL ni yangilang.
SITE_URL = os.getenv("SITE_URL", "https://muhammadaziz-web-sayti.onrender.com").strip().rstrip("/")
# Google Search Console bergan tasdiqlash kodi (meta tag ichidagi content qiymati)
GOOGLE_VERIFICATION = os.getenv("GOOGLE_SITE_VERIFICATION", "").strip()

# ---- Admin panel paroli (Render'da Environment Variable sifatida qo'ying) --
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()


def is_postgres():
    return DATABASE_URL.startswith(("postgresql://", "postgres://"))


def sql(query):
    """Savol belgisi (?) ni Postgres uchun %s ga almashtiradi."""
    return query.replace("?", "%s") if is_postgres() else query


def get_conn():
    if is_postgres():
        import psycopg
        return psycopg.connect(DATABASE_URL)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    try:
        cur = conn.cursor()
        if is_postgres():
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ratings (
                    id BIGSERIAL PRIMARY KEY,
                    name VARCHAR(40) NOT NULL,
                    course VARCHAR(40) NOT NULL,
                    score INTEGER NOT NULL,
                    total INTEGER NOT NULL DEFAULT 25,
                    percent INTEGER NOT NULL,
                    xp INTEGER NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            # Eski bazaga jarima ustunlarini xavfsiz qo'shish
            cur.execute("ALTER TABLE ratings ADD COLUMN IF NOT EXISTS fine INTEGER NOT NULL DEFAULT 0")
            cur.execute("ALTER TABLE ratings ADD COLUMN IF NOT EXISTS fine_paid INTEGER NOT NULL DEFAULT 0")
            cur.execute("ALTER TABLE ratings ADD COLUMN IF NOT EXISTS penalty_label TEXT NOT NULL DEFAULT ''")
            cur.execute("ALTER TABLE ratings ADD COLUMN IF NOT EXISTS violation INTEGER NOT NULL DEFAULT 0")
            cur.execute("ALTER TABLE ratings ADD COLUMN IF NOT EXISTS violation_reason TEXT NOT NULL DEFAULT ''")
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    course TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    total INTEGER NOT NULL DEFAULT 25,
                    percent INTEGER NOT NULL,
                    xp INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            cols = {row[1] for row in cur.execute("PRAGMA table_info(ratings)").fetchall()}
            if "fine" not in cols:
                cur.execute("ALTER TABLE ratings ADD COLUMN fine INTEGER NOT NULL DEFAULT 0")
            if "fine_paid" not in cols:
                cur.execute("ALTER TABLE ratings ADD COLUMN fine_paid INTEGER NOT NULL DEFAULT 0")
            if "penalty_label" not in cols:
                cur.execute("ALTER TABLE ratings ADD COLUMN penalty_label TEXT NOT NULL DEFAULT ''")
            if "violation" not in cols:
                cur.execute("ALTER TABLE ratings ADD COLUMN violation INTEGER NOT NULL DEFAULT 0")
            if "violation_reason" not in cols:
                cur.execute("ALTER TABLE ratings ADD COLUMN violation_reason TEXT NOT NULL DEFAULT ''")
        conn.commit()
    finally:
        conn.close()


COURSE_NAMES = {
    "computer": "💻 Kompyuter asoslari",
    "keyboard": "⌨️ Klaviatura",
    "ctrl": "⌨️ Ctrl tezkor tugmalari",
    "word": "📝 Microsoft Word",
    "excel": "📊 Microsoft Excel",
    "powerpoint": "🎞️ PowerPoint",
    "internet": "🌐 Internet va xavfsizlik",
    "ai": "🤖 Sun’iy intellekt",
}


def money(value):
    return f"{int(value):,}".replace(",", " ")


def build_message(name, course, score, total, penalty_label):
    course_name = COURSE_NAMES.get(course, course)
    text = f"{name} — {course_name}: {score}/{total} to‘g‘ri."
    if penalty_label:
        return f"{text} Jarima: {penalty_label}."
    return f"{text} Jarima yo‘q."


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not ADMIN_PASSWORD:
            return Response(
                "Admin panel o‘chirilgan: ADMIN_PASSWORD o‘rnatilmagan.", 503
            )
        auth = request.authorization
        given = (auth.password or "") if auth else ""
        if not auth or not hmac.compare_digest(
            given.encode("utf-8"), ADMIN_PASSWORD.encode("utf-8")
        ):
            return Response(
                "Parol kerak.", 401,
                {"WWW-Authenticate": 'Basic realm="Admin", charset="UTF-8"'},
            )
        return view(*args, **kwargs)
    return wrapper


@app.get("/edustar")
def edustar_page():
    """EduStar ta'lim platformasi sahifasi."""
    return render_template("edustar.html")


@app.get("/")
def index():
    return render_template(
        "index.html",
        site_url=SITE_URL,
        google_verification=GOOGLE_VERIFICATION,
    )


@app.get("/googlef6cbbcf56781e5d8.html")
def google_site_verification_file():
    # Google Search Console "HTML-fayl" usuli bilan tasdiqlash uchun.
    return Response(
        "google-site-verification: googlef6cbbcf56781e5d8.html",
        mimetype="text/html",
    )


@app.get("/robots.txt")
def robots_txt():
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        "Disallow: /api/admin\n"
        "\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )
    return Response(body, mimetype="text/plain")


@app.get("/sitemap.xml")
def sitemap_xml():
    today = datetime.now().date().isoformat()
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{SITE_URL}/</loc><lastmod>{today}</lastmod>'
        '<changefreq>weekly</changefreq><priority>1.0</priority></url>\n'
        '</urlset>\n'
    )
    return Response(xml, mimetype="application/xml")


@app.get("/health")
def health():
    return jsonify({"ok": True})


@app.get("/api/rating")
def get_rating():
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT name, course, score, total, percent, xp, created_at
            FROM ratings
            ORDER BY score DESC, percent DESC, created_at ASC
            LIMIT 100
        """)
        rows = cur.fetchall()
        result = []
        for row in rows:
            if is_postgres():
                name, course, score, total, percent, xp, created_at = row
                date_text = created_at.isoformat() if created_at else ""
            else:
                name = row["name"]; course = row["course"]; score = row["score"]
                total = row["total"]; percent = row["percent"]; xp = row["xp"]
                date_text = row["created_at"]
            result.append({
                "name": name, "course": course, "score": score,
                "total": total, "percent": percent, "xp": xp, "date": date_text
            })
        return jsonify(result)
    finally:
        conn.close()


@app.get("/api/rating/overall")
def get_rating_overall():
    """Har bir o'quvchining barcha testlardagi (eski va yangi) natijalarini
    bitta umumiy qatorga yig'ib, umumiy reyting sifatida qaytaradi."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name, score, total, xp FROM ratings")
        rows = cur.fetchall()
    finally:
        conn.close()

    agg = {}
    for row in rows:
        if is_postgres():
            name, score, total, xp = row
        else:
            name = row["name"]; score = row["score"]; total = row["total"]; xp = row["xp"]
        name = (name or "").strip()
        if not name:
            continue
        key = name.lower()
        entry = agg.setdefault(key, {"name": name, "score": 0, "total": 0, "xp": 0, "attempts": 0})
        entry["name"] = name  # oxirgi yozilgan yozuvdagi ism ko'rinishi saqlanadi
        entry["score"] += int(score or 0)
        entry["total"] += int(total or 0)
        entry["xp"] += int(xp or 0)
        entry["attempts"] += 1

    result = list(agg.values())
    for r in result:
        r["percent"] = round(r["score"] / r["total"] * 100) if r["total"] else 0
    result.sort(key=lambda r: (-r["score"], -r["xp"], r["name"].lower()))
    return jsonify(result[:100])


@app.post("/api/rating")
def add_rating():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()[:40]
    course = str(data.get("course", "")).strip()[:40]
    try:
        score = int(data.get("score", 0))
    except (TypeError, ValueError):
        score = -1
    if not name or course not in COURSE_NAMES or not 0 <= score <= TOTAL_QUESTIONS:
        return jsonify({"ok": False, "error": "Noto‘g‘ri ma’lumot."}), 400

    total = TOTAL_QUESTIONS
    percent = round(score / total * 100)
    xp = score * 5
    violation = bool(data.get("violation"))
    violation_reason = str(data.get("violation_reason", "")).strip()[:200]

    if violation:
        # Qoidabuzarlikda test darhol bloklanadi va admin panelda alohida ko‘rinadi.
        fine = 10000
        penalty_label = "🚫 Test bloklandi — 10 000 so‘m jarima"
    else:
        penalty = random.choice(PENALTIES) if score < MIN_PASS_SCORE else None
        fine = penalty["amount"] if penalty else 0
        penalty_label = penalty["label"] if penalty else ""

    now = datetime.now().astimezone().isoformat(timespec="seconds")

    conn = get_conn()
    try:
        cur = conn.cursor()
        if is_postgres():
            cur.execute("""
                INSERT INTO ratings (name, course, score, total, percent, xp, fine, penalty_label, violation, violation_reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, course, score, total, percent, xp, fine, penalty_label, int(violation), violation_reason))
        else:
            cur.execute("""
                INSERT INTO ratings (name, course, score, total, percent, xp, created_at, fine, penalty_label, violation, violation_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, course, score, total, percent, xp, now, fine, penalty_label, int(violation), violation_reason))
        conn.commit()
    finally:
        conn.close()
    return jsonify({
        "ok": True,
        "fine": fine,
        "penalty_label": penalty_label,
        "violation": violation,
        "violation_reason": violation_reason,
        "message": build_message(name, course, score, total, penalty_label),
    })


# ---------------------------------------------------------------------------
# ADMIN PANEL
# ---------------------------------------------------------------------------
@app.get("/admin")
@admin_required
def admin_page():
    return render_template("admin.html")


@app.get("/api/admin/results")
@admin_required
def admin_results():
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, course, score, total, percent, xp, created_at,
                   fine, fine_paid, penalty_label, violation, violation_reason
            FROM ratings
            ORDER BY id DESC
            LIMIT 500
        """)
        results = []
        for row in cur.fetchall():
            (rid, name, course, score, total, percent, xp, created_at,
             fine, fine_paid, penalty_label, violation, violation_reason) = tuple(row)
            if hasattr(created_at, "isoformat"):
                created_at = created_at.isoformat()
            results.append({
                "id": rid, "name": name, "course": course,
                "course_name": COURSE_NAMES.get(course, course),
                "score": score, "total": total, "percent": percent, "xp": xp,
                "date": created_at, "fine": fine, "fine_paid": bool(fine_paid),
                "penalty_label": penalty_label or "",
                "violation": bool(violation),
                "violation_reason": violation_reason or "",
                "message": build_message(name, course, score, total, penalty_label),
            })

        cur.execute("""
            SELECT COUNT(*),
                   COALESCE(SUM(CASE WHEN penalty_label <> '' THEN 1 ELSE 0 END), 0),
                   COALESCE(SUM(fine), 0),
                   COALESCE(SUM(CASE WHEN fine_paid = 0 THEN fine ELSE 0 END), 0),
                   COALESCE(SUM(CASE WHEN penalty_label <> '' AND fine_paid = 0 THEN 1 ELSE 0 END), 0)
            FROM ratings
        """)
        (total_count, penalties_count, money_total,
         unpaid_money_total, unresolved_count) = (int(x) for x in tuple(cur.fetchone()))
        return jsonify({
            "summary": {
                "total_results": total_count,
                "fines_count": penalties_count,
                "fines_total": money_total,
                "unpaid_total": unpaid_money_total,
                "unresolved_count": unresolved_count,
                "min_pass_score": MIN_PASS_SCORE,
            },
            "results": results,
        })
    finally:
        conn.close()


@app.post("/api/admin/results/<int:rid>/paid")
@admin_required
def admin_mark_paid(rid):
    # JSON talab qilinadi: boshqa saytdan yashirin (CSRF) so'rov yuborishni qiyinlashtiradi
    if not request.is_json:
        return jsonify({"ok": False, "error": "JSON kerak."}), 415
    paid = 1 if (request.get_json(silent=True) or {}).get("paid") else 0
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            sql("UPDATE ratings SET fine_paid = ? WHERE id = ? AND penalty_label <> ''"),
            (paid, rid),
        )
        changed = cur.rowcount
        conn.commit()
    finally:
        conn.close()
    if not changed:
        return jsonify({"ok": False, "error": "Jarimali yozuv topilmadi."}), 404
    return jsonify({"ok": True, "paid": bool(paid)})


with app.app_context():
    init_db()



@app.post("/test-violation")
def test_violation():
    data = request.get_json(silent=True) or {}
    record = {
        "name": str(data.get("name", "Noma'lum"))[:100],
        "course": str(data.get("course", ""))[:100],
        "reason": str(data.get("reason", ""))[:300],
        "time": str(data.get("time", ""))[:100],
        "fine": 10000
    }
    log_path = os.path.join(app.root_path, "test_violations.json")
    try:
        existing = []
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        if not isinstance(existing, list):
            existing = []
        existing.append(record)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return jsonify({"ok": True, "fine": 10000})


# ---- EduStar platform and Battle (additive subsystem; legacy ratings untouched) ----
EDUSTAR_DB = os.path.join(BASE_DIR, "edustar.db")

def edu_conn():
    c = sqlite3.connect(EDUSTAR_DB, timeout=15)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    return c

def edu_init():
    c = edu_conn()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS edu_lessons(
      id INTEGER PRIMARY KEY, grade INTEGER NOT NULL, subject TEXT NOT NULL,
      quarter INTEGER NOT NULL, topic TEXT NOT NULL, title TEXT NOT NULL,
      content TEXT NOT NULL DEFAULT '', media_url TEXT NOT NULL DEFAULT '',
      quiz_json TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS edu_progress(
      id INTEGER PRIMARY KEY, student TEXT NOT NULL, lesson_id INTEGER NOT NULL REFERENCES edu_lessons(id),
      completed INTEGER NOT NULL DEFAULT 0, best_percent INTEGER NOT NULL DEFAULT 0,
      attempts INTEGER NOT NULL DEFAULT 0, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(student, lesson_id));
    CREATE TABLE IF NOT EXISTS edu_battle_categories(
      id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
    CREATE TABLE IF NOT EXISTS edu_battles(
      id INTEGER PRIMARY KEY, title TEXT NOT NULL, mode TEXT NOT NULL DEFAULT 'turn',
      status TEXT NOT NULL DEFAULT 'draft', allow_negative INTEGER NOT NULL DEFAULT 0,
      bonus_on_wrong TEXT NOT NULL DEFAULT 'keep', bonus_points INTEGER NOT NULL DEFAULT 5,
      penalty_enabled INTEGER NOT NULL DEFAULT 1, penalty15_weight INTEGER NOT NULL DEFAULT 50,
      penalty30_weight INTEGER NOT NULL DEFAULT 50, tie_rule TEXT NOT NULL DEFAULT 'correct',
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS edu_battle_groups(
      id INTEGER PRIMARY KEY, battle_id INTEGER NOT NULL REFERENCES edu_battles(id) ON DELETE CASCADE,
      name TEXT NOT NULL, score INTEGER NOT NULL DEFAULT 0, ordinary_score INTEGER NOT NULL DEFAULT 0,
      bonus_question_score INTEGER NOT NULL DEFAULT 0, multiplier_score INTEGER NOT NULL DEFAULT 0,
      extra_score INTEGER NOT NULL DEFAULT 0, penalties INTEGER NOT NULL DEFAULT 0,
      cancelled_penalties INTEGER NOT NULL DEFAULT 0, correct INTEGER NOT NULL DEFAULT 0,
      wrong INTEGER NOT NULL DEFAULT 0, shield INTEGER NOT NULL DEFAULT 0,
      multiplier INTEGER NOT NULL DEFAULT 1, UNIQUE(battle_id,name));
    CREATE TABLE IF NOT EXISTS edu_battle_questions(
      id INTEGER PRIMARY KEY, battle_id INTEGER NOT NULL REFERENCES edu_battles(id) ON DELETE CASCADE,
      position INTEGER NOT NULL, category TEXT NOT NULL, difficulty TEXT NOT NULL,
      kind TEXT NOT NULL, prompt TEXT NOT NULL, image_url TEXT NOT NULL DEFAULT '',
      options_json TEXT NOT NULL DEFAULT '[]', answer TEXT NOT NULL,
      seconds INTEGER NOT NULL DEFAULT 30, points INTEGER NOT NULL,
      is_bonus INTEGER NOT NULL DEFAULT 0, UNIQUE(battle_id,position));
    CREATE TABLE IF NOT EXISTS edu_battle_answers(
      id INTEGER PRIMARY KEY, event_key TEXT NOT NULL UNIQUE, battle_id INTEGER NOT NULL,
      question_id INTEGER NOT NULL, group_id INTEGER NOT NULL, answer TEXT NOT NULL,
      correct INTEGER NOT NULL, base_points INTEGER NOT NULL, awarded_points INTEGER NOT NULL,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(battle_id,question_id,group_id));
    CREATE TABLE IF NOT EXISTS edu_battle_events(
      id INTEGER PRIMARY KEY, event_key TEXT NOT NULL UNIQUE, battle_id INTEGER NOT NULL,
      group_id INTEGER NOT NULL, question_id INTEGER, event_type TEXT NOT NULL,
      amount INTEGER NOT NULL DEFAULT 0, details TEXT NOT NULL DEFAULT '',
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    """)
    defaults = ["Ingliz tili","Matematika","Mantiqiy savollar","Davlat bayroqlari",
      "Suv osti dunyosi va dengiz hayvonlari","Informatika","Umumiy bilim","Rasmli savollar"]
    for name in defaults:
        c.execute("INSERT OR IGNORE INTO edu_battle_categories(name) VALUES (?)",(name,))
    c.commit(); c.close()

def edu_admin(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not ADMIN_PASSWORD:
            return jsonify({"ok":False,"error":"Admin uchun ADMIN_PASSWORD sozlanmagan."}),503
        auth=request.authorization
        if not auth or not hmac.compare_digest((auth.password or "").encode(), ADMIN_PASSWORD.encode()):
            return Response("Admin paroli kerak.",401,{"WWW-Authenticate":'Basic realm="EduStar Admin"'})
        return view(*a, **kw)
    return wrapped

@app.get("/api/edustar/lessons")
def edu_lessons_list():
    c=edu_conn()
    try:
        q="SELECT * FROM edu_lessons WHERE 1=1"; args=[]
        for key,col,lo,hi in [("grade","grade",1,11),("quarter","quarter",1,4)]:
            if request.args.get(key):
                try: v=int(request.args[key])
                except ValueError: return jsonify({"error":"Filtr noto‘g‘ri"}),400
                if not lo<=v<=hi:return jsonify({"error":"Filtr chegaradan tashqarida"}),400
                q+=f" AND {col}=?";args.append(v)
        if request.args.get("subject"): q+=" AND subject=?";args.append(request.args["subject"][:100])
        q+=" ORDER BY grade,subject,quarter,topic,title"
        return jsonify([dict(r) for r in c.execute(q,args).fetchall()])
    finally:c.close()

@app.post("/api/edustar/progress")
def edu_save_progress():
    d=request.get_json(silent=True) or {}
    student=str(d.get("student","")).strip()[:60]
    try: lesson=int(d.get("lesson_id")); percent=int(d.get("percent",0))
    except (TypeError,ValueError): return jsonify({"error":"Ma’lumot noto‘g‘ri"}),400
    if not student or not 0<=percent<=100:return jsonify({"error":"Ism yoki foiz noto‘g‘ri"}),400
    c=edu_conn()
    try:
        if not c.execute("SELECT 1 FROM edu_lessons WHERE id=?",(lesson,)).fetchone():return jsonify({"error":"Dars topilmadi"}),404
        c.execute("""INSERT INTO edu_progress(student,lesson_id,completed,best_percent,attempts)
        VALUES(?,?,1,?,1) ON CONFLICT(student,lesson_id) DO UPDATE SET completed=1,
        best_percent=MAX(best_percent,excluded.best_percent),attempts=attempts+1,updated_at=CURRENT_TIMESTAMP""",(student,lesson,percent))
        c.commit()
        rows=c.execute("SELECT COUNT(*) n,COALESCE(AVG(best_percent),0) p FROM edu_progress WHERE student=?",(student,)).fetchone()
        return jsonify({"ok":True,"completed_lessons":rows["n"],"average_percent":round(rows["p"])})
    finally:c.close()

@app.get("/api/edustar/profile")
def edu_profile():
    student=request.args.get("student","").strip()[:60]
    if not student:return jsonify({"error":"student parametri kerak"}),400
    c=edu_conn()
    try:
        p=c.execute("""SELECT COUNT(*) lessons,COALESCE(AVG(best_percent),0) percent,
        COALESCE(SUM(best_percent),0)/5 xp FROM edu_progress WHERE student=? AND completed=1""",(student,)).fetchone()
        history=[dict(r) for r in c.execute("""SELECT l.title,l.subject,p.best_percent,p.attempts,p.updated_at
          FROM edu_progress p JOIN edu_lessons l ON l.id=p.lesson_id WHERE p.student=?
          ORDER BY p.updated_at DESC LIMIT 100""",(student,)).fetchall()]
        return jsonify({"student":student,"completed_lessons":p["lessons"],"average_percent":round(p["percent"]),
          "xp":p["xp"],"level":1+p["xp"]//100,"history":history})
    finally:c.close()

@app.post("/api/admin/edustar/lessons")
@edu_admin
def edu_admin_create_lesson():
    d=request.get_json(silent=True) or {}
    try: grade=int(d.get("grade")); quarter=int(d.get("quarter"))
    except (TypeError,ValueError):return jsonify({"error":"Sinf/chorak noto‘g‘ri"}),400
    vals=[str(d.get(k,"")).strip() for k in ("subject","topic","title")]
    if not 1<=grade<=11 or not 1<=quarter<=4 or not all(vals):return jsonify({"error":"Sinf, chorak, fan, mavzu va dars nomi shart"}),400
    c=edu_conn()
    try:
        cur=c.execute("""INSERT INTO edu_lessons(grade,subject,quarter,topic,title,content,media_url,quiz_json)
          VALUES(?,?,?,?,?,?,?,?)""",(grade,vals[0],quarter,vals[1],vals[2],str(d.get("content",""))[:50000],
          str(d.get("media_url",""))[:1000],json.dumps(d.get("quiz",[]),ensure_ascii=False)[:30000]))
        c.commit();return jsonify({"ok":True,"id":cur.lastrowid}),201
    finally:c.close()

@app.get("/api/edustar/battle/categories")
def edu_battle_categories():
    c=edu_conn()
    try:return jsonify([dict(r) for r in c.execute("SELECT * FROM edu_battle_categories ORDER BY name")])
    finally:c.close()

@app.post("/api/admin/edustar/battle/categories")
@edu_admin
def edu_battle_category_create():
    d=request.get_json(silent=True) or {}; name=str(d.get("name","")).strip()[:80]
    if not name:return jsonify({"error":"Kategoriya nomi kerak"}),400
    c=edu_conn()
    try:
        c.execute("INSERT INTO edu_battle_categories(name) VALUES(?)",(name,));c.commit()
        return jsonify({"ok":True}),201
    except sqlite3.IntegrityError:return jsonify({"error":"Bu kategoriya mavjud"}),409
    finally:c.close()

@app.post("/api/admin/edustar/battle")
@edu_admin
def edu_battle_create():
    d=request.get_json(silent=True) or {}; title=str(d.get("title","")).strip()[:120]
    groups=d.get("groups",[]); questions=d.get("questions",[])
    if not title or not isinstance(groups,list) or not 1<=len(groups)<=3 or not isinstance(questions,list):
        return jsonify({"error":"Nom, 1–3 guruh va savollar ro‘yxati shart"}),400
    if len(questions)!=30 or sum(1 for q in questions if q.get("is_bonus"))!=6:
        return jsonify({"error":"Musobaqada aynan 30 savol, ulardan 6 tasi bonus bo‘lishi shart"}),400
    c=edu_conn()
    try:
        c.execute("BEGIN IMMEDIATE")
        cur=c.execute("""INSERT INTO edu_battles(title,mode,allow_negative,bonus_points,penalty_enabled,
          penalty15_weight,penalty30_weight,bonus_on_wrong,tie_rule) VALUES(?,?,?,?,?,?,?,?,?)""",
          (title,d.get("mode","turn") if d.get("mode") in ("turn","simultaneous") else "turn",
           int(bool(d.get("allow_negative"))),max(0,min(1000,int(d.get("bonus_points",5)))),
           int(bool(d.get("penalty_enabled",True))),max(0,int(d.get("penalty15_weight",50))),
           max(0,int(d.get("penalty30_weight",50)),),d.get("bonus_on_wrong","keep") if d.get("bonus_on_wrong") in ("keep","consume") else "keep",
           d.get("tie_rule","correct") if d.get("tie_rule") in ("correct","time") else "correct"))
        bid=cur.lastrowid
        for g in groups:
            n=str(g).strip()[:80]
            if not n:raise ValueError("Guruh nomi bo‘sh")
            c.execute("INSERT INTO edu_battle_groups(battle_id,name) VALUES(?,?)",(bid,n))
        shuffled_questions = list(questions)
        random.SystemRandom().shuffle(shuffled_questions)
        for i,q in enumerate(shuffled_questions,1):
            diff=q.get("difficulty","easy"); points={"easy":10,"medium":15,"hard":20}.get(diff)
            if not points:raise ValueError("Qiyinlik darajasi noto‘g‘ri")
            category=str(q.get("category","Umumiy bilim"))[:80]
            if not c.execute("SELECT 1 FROM edu_battle_categories WHERE name=?",(category,)).fetchone():raise ValueError("Kategoriya topilmadi")
            prompt=str(q.get("prompt","")).strip()
            answer=str(q.get("answer","")).strip()
            if not prompt or not answer:raise ValueError("Savol va javob bo‘sh bo‘lmasin")
            c.execute("""INSERT INTO edu_battle_questions(battle_id,position,category,difficulty,kind,prompt,image_url,
              options_json,answer,seconds,points,is_bonus) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
              (bid,i,category,diff,q.get("kind","choice") if q.get("kind") in ("choice","image","short","timed") else "choice",
               prompt,str(q.get("image_url",""))[:1000],json.dumps(q.get("options",[]),ensure_ascii=False),
               answer,max(5,min(300,int(q.get("seconds",30)))),points,int(bool(q.get("is_bonus")))))
        c.commit();return jsonify({"ok":True,"battle_id":bid}),201
    except (ValueError,sqlite3.IntegrityError) as e:
        c.rollback();return jsonify({"error":str(e)}),400
    finally:c.close()

@app.post("/api/admin/edustar/battle/<int:bid>/start")
@edu_admin
def edu_battle_start(bid):
    c=edu_conn()
    try:
        c.execute("BEGIN IMMEDIATE")
        b=c.execute("SELECT status FROM edu_battles WHERE id=?",(bid,)).fetchone()
        qs=c.execute("SELECT id FROM edu_battle_questions WHERE battle_id=?",(bid,)).fetchall()
        gs=c.execute("SELECT id FROM edu_battle_groups WHERE battle_id=?",(bid,)).fetchall()
        if not b:return jsonify({"error":"Musobaqa topilmadi"}),404
        if b["status"]!="draft":return jsonify({"error":"Musobaqa allaqachon boshlangan yoki yakunlangan"}),409
        if len(qs)!=30 or len(gs)<1 or len(gs)>3:return jsonify({"error":"30 savol va 1–3 guruh talab qilinadi"}),400
        c.execute("UPDATE edu_battles SET status='active' WHERE id=?",(bid,));c.commit()
        return jsonify({"ok":True})
    finally:c.close()

@app.get("/api/edustar/battle/latest")
def edu_battle_latest():
    """Return the newest active battle, or newest battle if none is active; no public ID needed."""
    c=edu_conn()
    try:
        b=c.execute("SELECT id FROM edu_battles ORDER BY CASE WHEN status='active' THEN 0 ELSE 1 END, id DESC LIMIT 1").fetchone()
        if not b:
            return jsonify({"error":"Faol musobaqa topilmadi"}),404
        bid=b["id"]
        battle=c.execute("SELECT id,title,mode,status,created_at FROM edu_battles WHERE id=?",(bid,)).fetchone()
        q=c.execute("SELECT id,position,category,difficulty,kind,prompt,image_url,options_json,seconds,points,is_bonus FROM edu_battle_questions WHERE battle_id=? ORDER BY position",(bid,)).fetchall()
        groups=c.execute("SELECT id,name,score,correct,wrong FROM edu_battle_groups WHERE battle_id=? ORDER BY score DESC",(bid,)).fetchall()
        return jsonify({"battle":dict(battle),"groups":[dict(r) for r in groups],"questions":[{**dict(r),"options":json.loads(r["options_json"])} for r in q]})
    finally:c.close()

@app.get("/api/edustar/battle/<int:bid>")
def edu_battle_state(bid):
    c=edu_conn()
    try:
        b=c.execute("SELECT id,title,mode,status,created_at FROM edu_battles WHERE id=?",(bid,)).fetchone()
        if not b:return jsonify({"error":"Musobaqa topilmadi"}),404
        q=c.execute("""SELECT id,position,category,difficulty,kind,prompt,image_url,options_json,seconds,points,is_bonus
          FROM edu_battle_questions WHERE battle_id=? ORDER BY position""",(bid,)).fetchall()
        # Correct answers are intentionally never sent to the public client.
        return jsonify({"battle":dict(b),"groups":[dict(r) for r in c.execute(
          "SELECT id,name,score,correct,wrong FROM edu_battle_groups WHERE battle_id=? ORDER BY score DESC",(bid,)).fetchall()],
          "questions":[{**dict(r),"options":json.loads(r["options_json"])} for r in q]})
    finally:c.close()

@app.post("/api/edustar/battle/<int:bid>/answer")
def edu_battle_answer(bid):
    d=request.get_json(silent=True) or {}
    try: qid=int(d.get("question_id")); gid=int(d.get("group_id"))
    except (TypeError,ValueError):return jsonify({"error":"Savol/guruh noto‘g‘ri"}),400
    answer=str(d.get("answer",""))[:1000]
    event_key=str(d.get("event_key","")).strip()[:100]
    if not event_key:return jsonify({"error":"Noyob event_key kerak"}),400
    c=edu_conn()
    try:
        c.execute("BEGIN IMMEDIATE")
        b=c.execute("SELECT * FROM edu_battles WHERE id=?",(bid,)).fetchone()
        q=c.execute("SELECT * FROM edu_battle_questions WHERE id=? AND battle_id=?",(qid,bid)).fetchone()
        g=c.execute("SELECT * FROM edu_battle_groups WHERE id=? AND battle_id=?",(gid,bid)).fetchone()
        if not b or b["status"]!="active" or not q or not g:return jsonify({"error":"Musobaqa faol emas yoki savol/guruh noto‘g‘ri"}),409
        if c.execute("SELECT 1 FROM edu_battle_answers WHERE battle_id=? AND question_id=? AND group_id=?",(bid,qid,gid)).fetchone():
            return jsonify({"error":"Bu guruh ushbu savolga javob bergan"}),409
        correct= int(answer.strip().casefold()==q["answer"].strip().casefold())
        base=q["points"] if correct else 0; mult=g["multiplier"] if correct else 1
        awarded=base*mult
        if correct and mult>1:
            c.execute("INSERT INTO edu_battle_events(event_key,battle_id,group_id,question_id,event_type,amount,details) VALUES(?,?,?,?,?,?,?)",
              (event_key+":mult",bid,gid,qid,"multiplier",awarded-base,f"{mult}x bonus"))
            c.execute("UPDATE edu_battle_groups SET multiplier=1,multiplier_score=multiplier_score+? WHERE id=?",(awarded-base,gid))
        c.execute("""INSERT INTO edu_battle_answers(event_key,battle_id,question_id,group_id,answer,correct,base_points,awarded_points)
          VALUES(?,?,?,?,?,?,?,?)""",(event_key,bid,qid,gid,answer,correct,base,awarded))
        c.execute("UPDATE edu_battle_groups SET score=score+?,ordinary_score=ordinary_score+?,bonus_question_score=bonus_question_score+?,correct=correct+?,wrong=wrong+? WHERE id=?",
          (awarded,awarded if not q["is_bonus"] else 0,awarded if q["is_bonus"] else 0,correct,1-correct,gid))
        bonus_event=None
        if correct and random.random()<0.15:
            kind=random.choice(["extra","2x","3x","shield"])
            if kind=="extra":
                amount=b["bonus_points"];c.execute("UPDATE edu_battle_groups SET score=score+?,extra_score=extra_score+? WHERE id=?",(amount,amount,gid))
            elif kind in ("2x","3x"):
                c.execute("UPDATE edu_battle_groups SET multiplier=? WHERE id=?",(2 if kind=="2x" else 3,gid));amount=0
            else:c.execute("UPDATE edu_battle_groups SET shield=shield+1 WHERE id=?",(gid,));amount=0
            ek=event_key+":random"
            c.execute("INSERT INTO edu_battle_events(event_key,battle_id,group_id,question_id,event_type,amount,details) VALUES(?,?,?,?,?,?,?)",
              (ek,bid,gid,qid,kind,amount,"Tasodifiy bonus"))
            bonus_event={"type":kind,"amount":amount}
        elif not correct and b["penalty_enabled"] and random.random()<0.25:
            weights=[b["penalty15_weight"],b["penalty30_weight"]]
            fine=random.choices([-15,-30],weights=weights,k=1)[0] if sum(weights)>0 else 0
            if fine:
                if g["shield"]>0:
                    c.execute("UPDATE edu_battle_groups SET shield=shield-1,cancelled_penalties=cancelled_penalties+? WHERE id=?",(abs(fine),gid))
                    ek=event_key+":shield";typ="penalty_cancelled";amt=abs(fine)
                else:
                    c.execute("UPDATE edu_battle_groups SET score=score+?,penalties=penalties+? WHERE id=?",(fine,abs(fine),gid))
                    ek=event_key+":penalty";typ="penalty";amt=fine
                c.execute("INSERT INTO edu_battle_events(event_key,battle_id,group_id,question_id,event_type,amount,details) VALUES(?,?,?,?,?,?,?)",
                  (ek,bid,gid,qid,typ,amt,"Tasodifiy jarima hodisasi"))
                bonus_event={"type":typ,"amount":amt}
        c.commit()
        ng=c.execute("SELECT score FROM edu_battle_groups WHERE id=?",(gid,)).fetchone()
        return jsonify({"ok":True,"correct":bool(correct),"awarded":awarded,"event":bonus_event,"group_score":ng["score"]})
    except sqlite3.IntegrityError:
        c.rollback();return jsonify({"error":"Hodisa takrorlangan"}),409
    finally:c.close()

@app.post("/api/admin/edustar/battle/<int:bid>/finish")
@edu_admin
def edu_battle_finish(bid):
    c=edu_conn()
    try:
        cur=c.execute("UPDATE edu_battles SET status='finished' WHERE id=? AND status='active'",(bid,))
        if not cur.rowcount:return jsonify({"error":"Faol musobaqa topilmadi"}),409
        c.commit()
        rows=[dict(r) for r in c.execute("""SELECT id,name,score,ordinary_score,bonus_question_score,multiplier_score,
          extra_score,penalties,cancelled_penalties,correct,wrong FROM edu_battle_groups WHERE battle_id=?
          ORDER BY score DESC,correct DESC,id ASC""",(bid,)).fetchall()]
        for i,r in enumerate(rows,1):r["place"]=i
        return jsonify({"ok":True,"results":rows})
    finally:c.close()

@app.get("/api/admin/edustar/battle/<int:bid>/events")
@edu_admin
def edu_battle_events(bid):
    c=edu_conn()
    try:return jsonify([dict(r) for r in c.execute("SELECT * FROM edu_battle_events WHERE battle_id=? ORDER BY id",(bid,)).fetchall()])
    finally:c.close()

with app.app_context():
    edu_init()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)

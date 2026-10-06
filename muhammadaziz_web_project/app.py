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


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)


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

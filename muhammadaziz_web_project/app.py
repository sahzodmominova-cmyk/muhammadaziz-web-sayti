import hmac
import os
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

# ---- Jarima qoidasi ------------------------------------------------------
TOTAL_QUESTIONS = 25
MIN_PASS_SCORE = 10      # shundan KAM to'g'ri javob bo'lsa jarima yoziladi
FINE_AMOUNT = 10000      # so'mda

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


def build_message(name, course, score, total, fine):
    course_name = COURSE_NAMES.get(course, course)
    text = f"{name} — {course_name}: {score}/{total} to‘g‘ri."
    if fine:
        return f"{text} Jarima: {money(fine)} so‘m."
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
    return render_template("index.html")


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
    fine = FINE_AMOUNT if score < MIN_PASS_SCORE else 0
    now = datetime.now().astimezone().isoformat(timespec="seconds")

    conn = get_conn()
    try:
        cur = conn.cursor()
        if is_postgres():
            cur.execute("""
                INSERT INTO ratings (name, course, score, total, percent, xp, fine)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, course, score, total, percent, xp, fine))
        else:
            cur.execute("""
                INSERT INTO ratings (name, course, score, total, percent, xp, created_at, fine)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, course, score, total, percent, xp, now, fine))
        conn.commit()
    finally:
        conn.close()
    return jsonify({
        "ok": True,
        "fine": fine,
        "message": build_message(name, course, score, total, fine),
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
            SELECT id, name, course, score, total, percent, xp, created_at, fine, fine_paid
            FROM ratings
            ORDER BY id DESC
            LIMIT 500
        """)
        results = []
        for row in cur.fetchall():
            rid, name, course, score, total, percent, xp, created_at, fine, fine_paid = tuple(row)
            if hasattr(created_at, "isoformat"):
                created_at = created_at.isoformat()
            results.append({
                "id": rid, "name": name, "course": course,
                "course_name": COURSE_NAMES.get(course, course),
                "score": score, "total": total, "percent": percent, "xp": xp,
                "date": created_at, "fine": fine, "fine_paid": bool(fine_paid),
                "message": build_message(name, course, score, total, fine),
            })

        cur.execute("""
            SELECT COUNT(*),
                   COALESCE(SUM(CASE WHEN fine > 0 THEN 1 ELSE 0 END), 0),
                   COALESCE(SUM(fine), 0),
                   COALESCE(SUM(CASE WHEN fine_paid = 0 THEN fine ELSE 0 END), 0)
            FROM ratings
        """)
        total_count, fines_count, fines_total, unpaid_total = (int(x) for x in tuple(cur.fetchone()))
        return jsonify({
            "summary": {
                "total_results": total_count,
                "fines_count": fines_count,
                "fines_total": fines_total,
                "unpaid_total": unpaid_total,
                "min_pass_score": MIN_PASS_SCORE,
                "fine_amount": FINE_AMOUNT,
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
        cur.execute(sql("UPDATE ratings SET fine_paid = ? WHERE id = ? AND fine > 0"), (paid, rid))
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

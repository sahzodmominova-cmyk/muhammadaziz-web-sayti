import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, "rating.db")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def is_postgres():
    return DATABASE_URL.startswith(("postgresql://", "postgres://"))


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
        conn.commit()
    finally:
        conn.close()


COURSE_NAMES = {
    "computer": "💻 Kompyuter asoslari",
    "keyboard": "⌨️ Klaviatura",
    "word": "📝 Microsoft Word",
    "excel": "📊 Microsoft Excel",
    "powerpoint": "🎞️ PowerPoint",
    "internet": "🌐 Internet va xavfsizlik",
    "ai": "🤖 Sun’iy intellekt",
}


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
    if not name or course not in COURSE_NAMES or not 0 <= score <= 25:
        return jsonify({"ok": False, "error": "Noto‘g‘ri ma’lumot."}), 400

    total = 25
    percent = round(score / total * 100)
    xp = score * 5
    now = datetime.now().astimezone().isoformat(timespec="seconds")

    conn = get_conn()
    try:
        cur = conn.cursor()
        if is_postgres():
            cur.execute("""
                INSERT INTO ratings (name, course, score, total, percent, xp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, course, score, total, percent, xp))
        else:
            cur.execute("""
                INSERT INTO ratings (name, course, score, total, percent, xp, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, course, score, total, percent, xp, now))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True})


with app.app_context():
    init_db()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

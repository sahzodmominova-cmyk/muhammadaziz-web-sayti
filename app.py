import os
import sqlite3
import json
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from flask import Flask, jsonify, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(BASE_DIR, "rating.db")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

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


COURSE_NAMES = {
    "computer": "💻 Kompyuter asoslari",
    "keyboard": "⌨️ Klaviatura",
    "word": "📝 Microsoft Word",
    "excel": "📊 Microsoft Excel",
    "powerpoint": "🎞️ PowerPoint",
    "internet": "🌐 Internet va xavfsizlik",
    "ai": "🤖 Sun’iy intellekt",
}


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
                    penalty BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            cur.execute("ALTER TABLE ratings ADD COLUMN IF NOT EXISTS penalty BOOLEAN NOT NULL DEFAULT FALSE")
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
                    penalty INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            cur.execute("PRAGMA table_info(ratings)")
            columns = {row[1] for row in cur.fetchall()}
            if "penalty" not in columns:
                cur.execute("ALTER TABLE ratings ADD COLUMN penalty INTEGER NOT NULL DEFAULT 0")
        conn.commit()
    finally:
        conn.close()


def send_telegram_penalty(name, course, score, percent):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    message = (
        "🚨 JARIMA!\n\n"
        f"👤 O‘quvchi: {name}\n"
        f"📚 Kurs: {COURSE_NAMES.get(course, course)}\n"
        f"📝 Natija: {score} / 25\n"
        f"📊 Foiz: {percent}%\n"
        "❌ 10 tadan kam — JARIMA"
    )

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        body = urlencode({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
        }).encode("utf-8")
        req = Request(url, data=body, method="POST")
        with urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception:
        return False


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
            SELECT name, course, score, total, percent, xp, penalty, created_at
            FROM ratings
            ORDER BY score DESC, percent DESC, created_at ASC
            LIMIT 100
        """)
        rows = cur.fetchall()
        result = []
        for row in rows:
            if is_postgres():
                name, course, score, total, percent, xp, penalty, created_at = row
                date_text = created_at.isoformat() if created_at else ""
            else:
                name = row["name"]
                course = row["course"]
                score = row["score"]
                total = row["total"]
                percent = row["percent"]
                xp = row["xp"]
                penalty = bool(row["penalty"])
                date_text = row["created_at"]
            result.append({
                "name": name,
                "course": course,
                "score": score,
                "total": total,
                "percent": percent,
                "xp": xp,
                "penalty": penalty,
                "date": date_text,
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
    penalty = score < 10
    now = datetime.now().astimezone().isoformat(timespec="seconds")

    conn = get_conn()
    try:
        cur = conn.cursor()
        if is_postgres():
            cur.execute("""
                INSERT INTO ratings
                (name, course, score, total, percent, xp, penalty)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, course, score, total, percent, xp, penalty))
        else:
            cur.execute("""
                INSERT INTO ratings
                (name, course, score, total, percent, xp, penalty, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, course, score, total, percent, xp, int(penalty), now))
        conn.commit()
    finally:
        conn.close()

    telegram_sent = False
    if penalty:
        telegram_sent = send_telegram_penalty(name, course, score, percent)

    return jsonify({
        "ok": True,
        "penalty": penalty,
        "telegram_sent": telegram_sent,
    })


# =========================
# ADMIN
# =========================

@app.get("/admin")
def admin_page():
    if not session.get("admin_logged_in"):
        return render_template("admin_login.html")
    return render_template("admin.html")


@app.post("/admin/login")
def admin_login():
    password = request.form.get("password", "")
    if not ADMIN_PASSWORD:
        return "ADMIN_PASSWORD sozlanmagan. Render Environment Variables ga qo‘shing.", 500
    if password == ADMIN_PASSWORD:
        session["admin_logged_in"] = True
        return redirect(url_for("admin_page"))
    return render_template("admin_login.html", error="Parol noto‘g‘ri."), 401


@app.post("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_page"))


@app.get("/api/admin/ratings")
def admin_ratings():
    if not session.get("admin_logged_in"):
        return jsonify({"ok": False, "error": "Ruxsat yo‘q."}), 401

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT name, course, score, total, percent, xp, penalty, created_at
            FROM ratings
            ORDER BY created_at DESC
            LIMIT 500
        """)
        rows = cur.fetchall()
        result = []
        for row in rows:
            if is_postgres():
                name, course, score, total, percent, xp, penalty, created_at = row
                date_text = created_at.isoformat() if created_at else ""
            else:
                name = row["name"]
                course = row["course"]
                score = row["score"]
                total = row["total"]
                percent = row["percent"]
                xp = row["xp"]
                penalty = bool(row["penalty"])
                date_text = row["created_at"]
            result.append({
                "name": name,
                "course": COURSE_NAMES.get(course, course),
                "score": score,
                "total": total,
                "percent": percent,
                "xp": xp,
                "penalty": penalty,
                "date": date_text,
            })
        return jsonify(result)
    finally:
        conn.close()


with app.app_context():
    init_db()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

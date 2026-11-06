"""Savol-javob kalitini (quiz_key.json) sahifadan qayta chiqaradi.
Savollarni templates/index.html da o'zgartirgandan keyin ishga tushiring:
    1) python app.py  (boshqa terminalda)      2) pip install playwright && playwright install chromium
    3) python tools/export_quiz_key.py
"""
import json, os
from playwright.sync_api import sync_playwright

URL = os.getenv("SITE", "http://127.0.0.1:5000/")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto(URL); pg.wait_for_timeout(1500)
    data = pg.evaluate("Object.fromEntries(Object.keys(courses).map(id=>[id,getCourseTestItems(id).map(q=>[q[0],q[1]])]))")
    b.close()
key = {c: {q: a for q, a in items} for c, items in data.items()}
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "quiz_key.json")
json.dump(key, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print("Yozildi:", out, {c: len(v) for c, v in key.items()})

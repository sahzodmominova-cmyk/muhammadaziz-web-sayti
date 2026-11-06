"""tools/kurikulum.txt (matn) -> static/kurikulum.js (sayt ma'lumoti).  Ishga tushirish:  python tools/build_kurikulum.py"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
fanlar = json.load(open(os.path.join(HERE, "fanlar.json"), encoding="utf-8"))
ids = {f["id"] for f in fanlar}


def fix(t):
    # ASCII apostroflarni chiroyli o'zbek belgilariga almashtiradi: o' -> o‘, g' -> g‘, qolganlari -> ’
    t = re.sub(r"([oOgG])'", lambda m: m.group(1) + "‘", t)
    return t.replace("'", "’")


kur, g, errors = {}, None, []
for n, line in enumerate(open(os.path.join(HERE, "kurikulum.txt"), encoding="utf-8"), 1):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    if line.startswith("@"):
        g = line[1:].strip(); kur[g] = {}; continue
    fan, _, rest = line.partition(":")
    fan = fan.strip(); topics = [fix(x.strip()) for x in rest.split(";") if x.strip()]
    if fan not in ids: errors.append(f"{n}-qator: noma'lum fan '{fan}'")
    if len(topics) != len(set(topics)): errors.append(f"{n}-qator ({g}-sinf {fan}): takroriy mavzu")
    if len(topics) < 4: errors.append(f"{n}-qator ({g}-sinf {fan}): kamida 4 ta mavzu kerak (choraklar uchun)")
    kur[g][fan] = topics
if errors:
    print("XATOLAR:\n  " + "\n  ".join(errors)); sys.exit(1)

js = "/* O‘quv dasturi: 1–11-sinf. Umumiy o‘quv dasturi asosida tuzilgan reja; maktab darsligiga qarab farq qilishi mumkin. */\n"
js += "const fanlar=" + json.dumps(fanlar, ensure_ascii=False, indent=0) + ";\n"
js += "const KURIKULUM=" + json.dumps(kur, ensure_ascii=False, indent=0) + ";\n"
open(os.path.join(ROOT, "static", "kurikulum.js"), "w", encoding="utf-8").write(js)
tot = {k: sum(len(t) for t in d.values()) for k, d in kur.items()}
print("Yozildi: static/kurikulum.js | jami mavzu:", sum(tot.values()), "|", tot)

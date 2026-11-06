"""1-11-sinf o'quv dasturi (static/kurikulum.js) tuzilmasini tekshiradi."""
import json, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = open(os.path.join(ROOT, "static", "kurikulum.js"), encoding="utf-8").read()
FANLAR = json.loads(re.search(r"const fanlar=(\[.*?\]);\nconst KURIKULUM", JS, re.S).group(1))
KUR = json.loads(re.search(r"const KURIKULUM=(\{.*\});", JS, re.S).group(1))


class KurikulumTests(unittest.TestCase):
    def test_all_eleven_grades_present(self):
        self.assertEqual(sorted(KUR, key=int), [str(i) for i in range(1, 12)])

    def test_every_subject_is_known_and_has_enough_unique_topics(self):
        ids = {f["id"] for f in FANLAR}
        for g, d in KUR.items():
            self.assertGreaterEqual(len(d), 5, f"{g}-sinf: fanlar kam")
            for fan, topics in d.items():
                self.assertIn(fan, ids, f"{g}-sinf: noma'lum fan {fan}")
                self.assertGreaterEqual(len(topics), 5, f"{g}-sinf {fan}: mavzu kam")
                self.assertEqual(len(topics), len(set(topics)), f"{g}-sinf {fan}: takroriy mavzu")

    def test_quarters_are_never_empty(self):
        for g, d in KUR.items():
            for fan, topics in d.items():
                n = len(topics); qs = {i * 4 // n + 1 for i in range(n)}
                self.assertEqual(qs, {1, 2, 3, 4}, f"{g}-sinf {fan}: chorak bo'sh qoladi")

    def test_ready_lessons_are_attached_to_their_grade(self):
        js = open(os.path.join(ROOT, "static", "edustar.js"), encoding="utf-8").read()
        norm = lambda s: re.sub(r"[‘’'`ʻʼ]", "", s.lower())
        ready = [("matematika", "5", "Geometriya asoslari"), ("matematika", "6", "Foizlar"), ("matematika", "6", "Tenglamalar"),
                 ("informatika", "5", "Algoritm tushunchasi"), ("informatika", "9", "Python asoslari"), ("informatika", "9", "O‘zgaruvchilar"),
                 ("ingliz", "5", "To be fe’li"), ("ingliz", "5", "Oddiy so‘zlar"), ("fizika", "7", "Tezlik"), ("jahon-tarixi", "5", "Tarixni o‘rganish")]
        for fan, g, nom in ready:
            self.assertIn(norm(nom), [norm(t) for t in KUR[g][fan]], f"{g}-sinf {fan}: {nom}")
            self.assertIn(norm(nom).split()[0], norm(js))

if __name__ == "__main__":
    unittest.main()

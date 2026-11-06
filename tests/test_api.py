"""V2 xavfsizlik va reyting testlari (haqiqiy Flask test klienti, vaqtinchalik bazalar bilan)."""
import base64, os, tempfile, unittest

TMP = tempfile.mkdtemp()
os.environ["ADMIN_PASSWORD"] = "test-parol"
os.environ["EDUSTAR_DB_PATH"] = os.path.join(TMP, "edu.db")
os.environ["TEST_MIN_SECONDS"] = "0"

import app as site  # noqa: E402

site.SQLITE_PATH = os.path.join(TMP, "rating.db")
site.init_db(); site.edu_init(); site.edu_migrate()
ADMIN = {"Authorization": "Basic " + base64.b64encode(b"admin:test-parol").decode()}


def answers(course, wrong=False):
    return [{"q": q, "a": "xato" if wrong else a} for q, a in list(site.QUIZ_KEY[course].items())[:25]]


class RatingTests(unittest.TestCase):
    def setUp(self):
        self.c = site.app.test_client(); site.RATE.clear(); site.TEST_MIN_SECONDS = 0

    def start(self, name="Ali", course="ctrl"):
        return self.c.post("/api/test/start", json={"name": name, "course": course}).get_json()["token"]

    def send(self, token, ans):
        return self.c.post("/api/rating", json={"token": token, "answers": ans})

    def test_honest_result_is_graded_by_server(self):
        r = self.send(self.start(), answers("ctrl")); self.assertEqual(r.status_code, 200); self.assertEqual(r.get_json()["score"], 25)

    def test_forged_score_without_token_rejected(self):
        r = self.c.post("/api/rating", json={"name": "Sinfdosh", "course": "ctrl", "score": 25, "violation": True})
        self.assertEqual(r.status_code, 400)

    def test_tampered_token_rejected(self):
        t = self.start(); self.assertEqual(self.send(t[:-3] + "abc", answers("ctrl")).status_code, 400)

    def test_token_cannot_be_reused(self):
        t = self.start(); self.assertEqual(self.send(t, answers("ctrl")).status_code, 200); self.assertEqual(self.send(t, answers("ctrl")).status_code, 409)

    def test_too_fast_rejected(self):
        site.TEST_MIN_SECONDS = 999; self.assertEqual(self.send(self.start(), answers("ctrl")).status_code, 400)

    def test_wrong_answer_count_or_unknown_question_rejected(self):
        self.assertEqual(self.send(self.start(), answers("ctrl")[:10]).status_code, 400)
        bad = answers("ctrl"); bad[0] = {"q": "uydirma savol", "a": "x"}; self.assertEqual(self.send(self.start(), bad).status_code, 400)

    def test_wrong_answers_get_low_score_and_penalty(self):
        j = self.send(self.start("Vali"), answers("ctrl", wrong=True)).get_json(); self.assertEqual(j["score"], 0); self.assertTrue(j["penalty_label"])

    def test_overall_counts_best_attempt_per_course_only(self):
        for _ in range(3): self.send(self.start("Sardor", "ctrl"), answers("ctrl"))
        row = [r for r in self.c.get("/api/rating/overall").get_json() if r["name"] == "Sardor"][0]
        self.assertEqual((row["score"], row["total"], row["attempts"]), (25, 25, 3))

    def test_old_unauthenticated_violation_endpoint_is_gone(self):
        self.assertEqual(self.c.post("/test-violation", json={"name": "x"}).status_code, 404)

    def test_rate_limit(self):
        codes = [self.c.post("/api/test/start", json={"name": "A", "course": "ctrl"}).status_code for _ in range(25)]
        self.assertIn(429, codes)

    def test_admin_can_delete_record(self):
        self.send(self.start("Soxta"), answers("ctrl", wrong=True))
        rid = [r for r in self.c.get("/api/admin/results", headers=ADMIN).get_json()["results"] if r["name"] == "Soxta"][0]["id"]
        self.assertEqual(self.c.post(f"/api/admin/results/{rid}/delete").status_code, 401)
        self.assertTrue(self.c.post(f"/api/admin/results/{rid}/delete", headers=ADMIN).get_json()["ok"])

    def test_security_headers(self):
        h = self.c.get("/health").headers; self.assertEqual(h["X-Content-Type-Options"], "nosniff")


class BattleTests(unittest.TestCase):
    def test_group_code_protects_answers_and_bad_input_is_400(self):
        c = site.app.test_client()
        qs = [{"prompt": f"S{i}", "answer": "a", "options": ["a", "b"], "is_bonus": i < 6, "category": "Umumiy bilim"} for i in range(30)]
        r = c.post("/api/admin/edustar/battle", json={"title": "T", "groups": ["Alfa", "Beta"], "questions": qs}, headers=ADMIN)
        self.assertEqual(r.status_code, 201); j = r.get_json(); bid, codes = j["battle_id"], {g["name"]: g["code"] for g in j["groups"]}
        self.assertEqual(c.post(f"/api/admin/edustar/battle/{bid}/start", headers=ADMIN).status_code, 200)
        st = c.get(f"/api/edustar/battle/{bid}").get_json(); gid = st["groups"][0]["id"]; qid = st["questions"][0]["id"]
        self.assertNotIn("join_code", st["groups"][0])
        body = {"question_id": qid, "group_id": gid, "answer": "a", "event_key": "k1"}
        self.assertEqual(c.post(f"/api/edustar/battle/{bid}/answer", json=body).status_code, 403)
        self.assertEqual(c.post(f"/api/edustar/battle/{bid}/answer", json={**body, "group_code": "000000"}).status_code, 403)
        gname = st["groups"][0]["name"]
        self.assertEqual(c.post(f"/api/edustar/battle/{bid}/answer", json={**body, "group_code": codes[gname]}).status_code, 200)
        bad = c.post("/api/admin/edustar/battle", json={"title": "T", "groups": ["A"], "questions": [None] * 30}, headers=ADMIN)
        self.assertIn(bad.status_code, (400,))


if __name__ == "__main__":
    unittest.main()

"""Barcha API marshrutlariga axlat ma'lumot yuborib, server 500 xato bermasligini tekshiradi."""
import base64, os, re, tempfile, unittest

TMP = tempfile.mkdtemp()
os.environ.update(ADMIN_PASSWORD="p", EDUSTAR_DB_PATH=TMP + "/e.db", TEST_MIN_SECONDS="0")
import app as site  # noqa: E402

site.SQLITE_PATH = TMP + "/r.db"
site.init_db(); site.edu_init(); site.edu_migrate()
ADMIN = {"Authorization": "Basic " + base64.b64encode(b"a:p").decode()}
BODIES = [None, [], "x", 123, {}, {"name": None, "course": [], "answers": "x", "token": 5},
          {"questions": [None] * 30, "groups": [1, 2], "title": {}},
          {"student": "A" * 500, "lesson_id": "x", "score": "y"}, {"question_id": "a", "group_id": [], "answer": {}}]


class FuzzTests(unittest.TestCase):
    def test_no_server_errors_on_garbage(self):
        c = site.app.test_client(); bad = []
        for rule in site.app.url_map.iter_rules():
            if rule.endpoint == "static":
                continue
            path = re.sub(r"<[^>]+>", "1", rule.rule)
            for m in rule.methods - {"HEAD", "OPTIONS"}:
                for hdr in ({}, ADMIN):
                    for body in ([None] if m == "GET" else BODIES):
                        for qs in ("", "?student=%00&x=" + "A" * 3000, "?limit=-1&course=<script>"):
                            kw = {"headers": hdr}
                            if m != "GET":
                                kw["json"] = body
                            r = c.open(path + qs, method=m, **kw)
                            if r.status_code >= 500:
                                bad.append((m, path, r.status_code))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()

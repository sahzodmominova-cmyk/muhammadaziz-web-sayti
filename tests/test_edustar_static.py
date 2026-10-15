"""EduStar integratsiyasi uchun yengil statik tekshiruvlar: python -m unittest discover -s tests"""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class EduStarStaticTests(unittest.TestCase):
    def test_app_parses(self):
        ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))

    def test_required_routes_exist(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        for route in (
            "/api/edustar/lessons", "/api/edustar/progress",
            "/api/edustar/profile", "/api/admin/edustar/battle",
            "/api/edustar/battle/<int:bid>/answer",
        ):
            self.assertIn(route, source)

    def test_battle_question_guard_exists(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("len(questions)!=30", source)
        self.assertIn("!=6", source)
        self.assertIn("Correct answers are intentionally never sent", source)

if __name__ == "__main__":
    unittest.main()

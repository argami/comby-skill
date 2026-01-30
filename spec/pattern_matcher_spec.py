"""Specs for PatternMatcher class using Ivoire BDD"""

from ivoire import describe

with describe("PatternMatcher") as it:
    with it("detect_sql_injection - can detect SQL concatenation vulnerability") as test:
        from comby_skill.pattern_matcher import PatternMatcher

        code = 'query = "SELECT * FROM users WHERE id = \'" + user_id + "\'"'

        matcher = PatternMatcher()
        matches = matcher.detect_sql_injection(code)

        test.assertGreater(len(matches), 0)
        test.assertIn("SELECT", matches[0]["code"])
        test.assertEqual(matches[0]["pattern"], "SQL_INJECTION")
        test.assertEqual(matches[0]["severity"], "CRITICAL")

    with it("detect_missing_type_hints - can detect function without type hints") as test:
        from comby_skill.pattern_matcher import PatternMatcher

        code = """def get_user(user_id):
    return db.query(user_id)"""

        matcher = PatternMatcher()
        matches = matcher.detect_missing_type_hints(code)

        test.assertGreater(len(matches), 0)
        test.assertIn("def get_user", matches[0]["code"])
        test.assertEqual(matches[0]["pattern"], "MISSING_TYPE_HINTS")
        test.assertEqual(matches[0]["severity"], "MEDIUM")

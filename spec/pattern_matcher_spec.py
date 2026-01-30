"""Specs for PatternMatcher class using Ivoire BDD"""

from ivoire import describe, context, it
from ivoire.assertions import expect

describe("PatternMatcher"):
    context("detect_sql_injection"):
        it("can detect SQL concatenation vulnerability"):
            from comby_skill.pattern_matcher import PatternMatcher

            code = 'query = "SELECT * FROM users WHERE id = \'" + user_id + "\'"'

            matcher = PatternMatcher()
            matches = matcher.detect_sql_injection(code)

            expect(len(matches)).to(be_above(0))
            expect(matches[0]["code"]).to(contain("SELECT"))
            expect(matches[0]["pattern"]).to(equal("SQL_INJECTION"))
            expect(matches[0]["severity"]).to(equal("CRITICAL"))

    context("detect_missing_type_hints"):
        it("can detect function without type hints"):
            from comby_skill.pattern_matcher import PatternMatcher

            code = """def get_user(user_id):
    return db.query(user_id)"""

            matcher = PatternMatcher()
            matches = matcher.detect_missing_type_hints(code)

            expect(len(matches)).to(be_above(0))
            expect(matches[0]["code"]).to(contain("def get_user"))
            expect(matches[0]["pattern"]).to(equal("MISSING_TYPE_HINTS"))
            expect(matches[0]["severity"]).to(equal("MEDIUM"))

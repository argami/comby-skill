"""Pattern matching engine for detecting code vulnerabilities and patterns."""

import re
from typing import List, Dict, Any


class PatternMatcher:
    """Detects security vulnerabilities and code patterns using regex matching."""

    def detect_sql_injection(self, code: str) -> List[Dict[str, Any]]:
        """Detect SQL injection vulnerabilities from string concatenation.

        Args:
            code: Python source code to analyze

        Returns:
            List of detected SQL injection matches with code, line number, pattern, and severity
        """
        matches = []

        # Pattern 1: SELECT with string concatenation
        # Matches: query = "SELECT * FROM users WHERE id = '" + user_id + "'"
        pattern1 = r'["\']SELECT\s+.*?["\']?\s*\+\s*'

        # Pattern 2: SELECT with f-string
        # Matches: f"SELECT * FROM users WHERE id = '{user_id}'"
        pattern2 = r'f["\']SELECT\s+.*?\{.*?\}.*?["\']'

        # Pattern 3: Generic SQL concatenation
        # Matches: "UPDATE users SET role = '" + role + "'"
        pattern3 = r'["\'](?:SELECT|INSERT|UPDATE|DELETE|DROP)\s+.*?["\']?\s*\+\s*'

        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            if re.search(pattern1, line) or re.search(pattern2, line) or re.search(pattern3, line):
                matches.append({
                    'code': line.strip(),
                    'line_number': line_num,
                    'pattern': 'SQL_INJECTION',
                    'severity': 'CRITICAL'
                })

        return matches

    def detect_missing_type_hints(self, code: str) -> List[Dict[str, Any]]:
        """Detect functions missing type hints.

        Args:
            code: Python source code to analyze

        Returns:
            List of detected functions without type hints
        """
        matches = []

        # Pattern: def function_name(args): without type hints
        # Matches: def get_user(user_id):
        # Does not match: def get_user(user_id: int) -> Optional[Dict]:
        pattern = r'^\s*def\s+\w+\([^)]*\):\s*$'

        lines = code.split('\n')

        for line_num, line in enumerate(lines, 1):
            if re.match(pattern, line):
                # Check if the function definition itself has type hints
                if '->' not in line and ':' in line:
                    matches.append({
                        'code': line.strip(),
                        'line_number': line_num,
                        'pattern': 'MISSING_TYPE_HINTS',
                        'severity': 'MEDIUM'
                    })

        return matches

"""Pattern matching engine for detecting code vulnerabilities and patterns."""

import re
from typing import List, Dict, Any, Callable, Optional


# Pattern family registry
_PATTERN_FAMILIES: Dict[str, Callable] = {}


def register_pattern(family_name: str):
    """Decorator to register a pattern family.

    Args:
        family_name: Name of the pattern family

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        _PATTERN_FAMILIES[family_name] = func
        return func
    return decorator


class PatternMatcher:
    """Detects security vulnerabilities and code patterns using regex matching."""

    def __init__(self):
        """Initialize PatternMatcher with pattern families."""
        self._families: Dict[str, Callable] = {}
        self._load_builtin_families()

    def _load_builtin_families(self):
        """Load built-in pattern families."""
        # Import and register pattern families
        try:
            from .patterns import (
                detect_database_access,
                detect_http_endpoints,
                detect_auth_boundaries,
                detect_external_dependencies,
                analyze_complexity,
                detect_error_handling,
            )

            self.register_pattern("database_access", detect_database_access)
            self.register_pattern("http_endpoints", detect_http_endpoints)
            self.register_pattern("auth_boundaries", detect_auth_boundaries)
            self.register_pattern("external_deps", detect_external_dependencies)
            self.register_pattern("complexity", analyze_complexity)
            self.register_pattern("error_handling", detect_error_handling)
        except ImportError:
            pass  # Patterns not available yet

    def register_pattern(self, family_name: str, detector_func: Callable):
        """Register a pattern family.

        Args:
            family_name: Name of the pattern family
            detector_func: Function that detects the pattern
        """
        self._families[family_name] = detector_func

    def get_patterns_by_category(self, category: str) -> List[str]:
        """Get all patterns in a category.

        Args:
            category: Category to filter by (security, code, quality, api, database)

        Returns:
            List of pattern family names
        """
        category_map = {
            "security": ["database_access", "auth_boundaries"],
            "api": ["http_endpoints"],
            "database": ["database_access"],
            "quality": ["complexity", "error_handling"],
            "external": ["external_deps"],
        }
        return category_map.get(category, list(self._families.keys()))

    def run_family(self, family_name: str, path: str, **kwargs) -> List[Dict[str, Any]]:
        """Run a specific pattern family.

        Args:
            family_name: Name of the pattern family to run
            path: Path to analyze
            **kwargs: Additional arguments for the detector

        Returns:
            List of findings
        """
        if family_name not in self._families:
            return []

        detector = self._families[family_name]

        # Read file content
        try:
            with open(path, 'r') as f:
                code_content = f.read()
        except (IOError, OSError):
            return []

        # Detect language from extension
        language = self._detect_language(path)

        # Run detector
        try:
            results = detector(path, language, code_content, **kwargs)
            # Convert to dict format if needed
            if hasattr(results, '__iter__') and not isinstance(results, dict):
                return [self._convert_result(r) for r in results]
            return results
        except Exception:
            return []

    def _detect_language(self, path: str) -> str:
        """Detect programming language from file extension.

        Args:
            path: File path

        Returns:
            Language name
        """
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".go": "go",
            ".rb": "ruby",
            ".rs": "rust",
            ".php": "php",
        }
        import os
        _, ext = os.path.splitext(path)
        return ext_map.get(ext.lower(), "python")

    def _convert_result(self, result) -> Dict[str, Any]:
        """Convert result object to dictionary.

        Args:
            result: Result object

        Returns:
            Dictionary representation
        """
        if isinstance(result, dict):
            return result

        # Convert dataclass to dict
        if hasattr(result, '__dataclassfields__'):
            return {f: getattr(result, f) for f in result.__dataclassfields__}

        return {"result": str(result)}

    def list_available_families(self) -> List[str]:
        """List all available pattern families.

        Returns:
            List of family names
        """
        return list(self._families.keys())

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

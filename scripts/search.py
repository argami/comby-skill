"""Search functions for Comby Skill plugin."""

import subprocess
from typing import List, Dict, Any, Optional
from .utils import (
    run_comby_command,
    parse_json_output,
    validate_pattern,
    get_language_from_extension,
)


LANGUAGE_PATTERNS = {
    "python": {
        "function": r"def\s+(\w+)\s*\(",
        "class": r"class\s+(\w+)(?:\(.*?\))?:",
        "import": r"^(?:from\s+(\S+)\s+import|import\s+(\S+))",
    },
    "javascript": {
        "function": r"function\s+(\w+)\s*\(",
        "class": r"class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{",
        "import": r"import\s+(?:(?:\{[^}]*\}|\*\s+as\s+\w+|\w+)\s+from\s+)?['\"]([^'\"]+)['\"]",
    },
    "go": {
        "function": r"func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(",
        "struct": r"type\s+(\w+)\s+struct\s*\{",
        "import": r"import\s+(?:\(\s*)?(?:\s*[\'\"]([^\'\"]+)[\'\"]\s*)?",
    },
    "ruby": {
        "function": r"def\s+(\w+)",
        "class": r"class\s+(\w+)(?:\s*<\s*\w+)?",
        "import": r"require(?:_relative)?\s+['\"]([^'\"]+)['\"]",
    },
    "rust": {
        "function": r"fn\s+(\w+)\s*(?:<[^>]*>)?s*\(",
        "struct": r"struct\s+(\w+)(?:\s*<[^>]*>)?\s*\{?",
        "enum": r"enum\s+(\w+)\s*\{?",
        "import": r"use\s+(\w+(?:::\w+)*)",
    },
    "php": {
        "function": r"function\s+(\w+)\s*\(",
        "class": r"class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w,\s]+)?",
        "import": r"use\s+(\w+(?:\\\\\w+)*)",
    },
}


def search_pattern(
    pattern: str,
    path: str = ".",
    format: str = "json",
    include: Optional[str] = None,
    exclude: Optional[str] = None,
    context: int = 0,
    case_insensitive: bool = False,
) -> List[Dict[str, Any]]:
    """Search for a pattern in files.

    Args:
        pattern: Regex pattern to search for
        path: Root path to search
        format: Output format (default, json, csv, lines, count)
        include: File patterns to include
        exclude: File patterns to exclude
        context: Number of context lines
        case_insensitive: Case insensitive search

    Returns:
        List of search results
    """
    validation = validate_pattern(pattern)
    if not validation["valid"]:
        raise ValueError(f"Invalid pattern: {validation['error']}")

    result = run_comby_command(
        pattern=pattern,
        path=path,
        format=format,
        include=include,
        exclude=exclude,
        context=context,
        case_insensitive=case_insensitive,
    )

    if format == "json":
        return parse_json_output(result.stdout)

    # For non-JSON formats, return as raw text
    return [{"raw": result.stdout}]


def search_functions(
    lang: str,
    path: str = ".",
    format: str = "json",
    **kwargs
) -> List[Dict[str, Any]]:
    """Find function definitions.

    Args:
        lang: Programming language (python, javascript, go, ruby, rust, php)
        path: Root path to search
        format: Output format
        **kwargs: Additional arguments for search_pattern

    Returns:
        List of function definitions
    """
    lang = lang.lower()
    if lang not in LANGUAGE_PATTERNS:
        raise ValueError(f"Unsupported language: {lang}")

    pattern = LANGUAGE_PATTERNS[lang].get("function")
    if not pattern:
        raise ValueError(f"No function pattern for language: {lang}")

    return search_pattern(pattern, path, format, **kwargs)


def search_classes(
    lang: str,
    path: str = ".",
    format: str = "json",
    **kwargs
) -> List[Dict[str, Any]]:
    """Find class definitions.

    Args:
        lang: Programming language
        path: Root path to search
        format: Output format
        **kwargs: Additional arguments for search_pattern

    Returns:
        List of class definitions
    """
    lang = lang.lower()
    if lang not in LANGUAGE_PATTERNS:
        raise ValueError(f"Unsupported language: {lang}")

    pattern = LANGUAGE_PATTERNS[lang].get("class")
    if not pattern:
        raise ValueError(f"No class pattern for language: {lang}")

    return search_pattern(pattern, path, format, **kwargs)


def search_imports(
    lang: str,
    path: str = ".",
    format: str = "json",
    **kwargs
) -> List[Dict[str, Any]]:
    """Find import statements.

    Args:
        lang: Programming language
        path: Root path to search
        format: Output format
        **kwargs: Additional arguments for search_pattern

    Returns:
        List of import statements
    """
    lang = lang.lower()
    if lang not in LANGUAGE_PATTERNS:
        raise ValueError(f"Unsupported language: {lang}")

    pattern = LANGUAGE_PATTERNS[lang].get("import")
    if not pattern:
        raise ValueError(f"No import pattern for language: {lang}")

    return search_pattern(pattern, path, format, **kwargs)


SECURITY_PATTERNS = {
    "sql_injection": r"execute\s*\(\s*['\"]|\.execute\(|\.exec\(|\.query\(|cursor\.execute",
    "xss": r"innerHTML|outerHTML|document\.write|\.html\(|v-html",
    "hardcoded_secrets": r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|pwd|private[_-]?key)",
    "command_injection": r"os\.system\(|os\.popen\(|subprocess\.call\(|subprocess\.run\(|subprocess\.Popen\(|shell=True",
    "unsafe_deserialization": r"pickle\.loads\(|pickle\.load\(|yaml\.load\(|yaml\.unsafe_load|marshal\.loads\(|eval\(|exec\(",
}


def search_security_patterns(
    path: str = ".",
    pattern_type: Optional[str] = None,
    format: str = "json",
    **kwargs
) -> List[Dict[str, Any]]:
    """Search for security-related patterns.

    Args:
        path: Root path to search
        pattern_type: Specific security pattern type (sql_injection, xss, etc.)
                   If None, searches all security patterns
        format: Output format
        **kwargs: Additional arguments for search_pattern

    Returns:
        List of security findings
    """
    results = []

    if pattern_type:
        if pattern_type not in SECURITY_PATTERNS:
            raise ValueError(f"Unknown security pattern: {pattern_type}")
        pattern = SECURITY_PATTERNS[pattern_type]
        return search_pattern(pattern, path, format, **kwargs)

    # Search all security patterns
    for name, pattern in SECURITY_PATTERNS.items():
        findings = search_pattern(pattern, path, format, **kwargs)
        for finding in findings:
            finding["security_type"] = name
        results.extend(findings)

    return results

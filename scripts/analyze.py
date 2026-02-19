"""Analysis functions for Comby Skill plugin."""

import json
from typing import Dict, List, Any, Optional
from .utils import run_comby_command, parse_json_output
from .search import search_security_patterns


FOCUS_PATTERNS = {
    "security": {
        "sql_injection": r"execute\s*\(\s*['\"]|\.execute\(|\.exec\(|\.query\(|cursor\.execute",
        "xss": r"innerHTML|outerHTML|document\.write|\.html\(|v-html",
        "hardcoded_secrets": r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|pwd|private[_-]?key)",
        "command_injection": r"os\.system\(|os\.popen\(|subprocess\.call\(|subprocess\.run\(|subprocess\.Popen\(|shell=True",
        "unsafe_deserialization": r"pickle\.loads\(|pickle\.load\(|yaml\.load\(|yaml\.unsafe_load|marshal\.loads\(|eval\(|exec\(",
    },
    "database": {
        "db_calls": r"execute\s*\(|cursor\.execute|\.query\(|db\.execute",
        "orm": r"\.filter\(|\.get\(|\.create\(|\.update\(|Model\.objects",
        "transactions": r"begin\(|commit\(|rollback\(|transaction",
    },
    "http": {
        "flask_routes": r"@app\.route\(|@router\.(get|post|put|delete|patch)",
        "django_urls": r"path\(|re_path\(|url\(",
        "express_routes": r"app\.(get|post|put|delete|patch|all)\(",
        "fastapi": r"@(app|router)\.(get|post|put|delete|patch)",
    },
    "auth": {
        "auth_decorators": r"@login_required|@auth_required|@requires_auth|@authenticated",
        "jwt": r"jwt\.decode|jwt\.encode|JWT|jwt_required",
        "password_handling": r"bcrypt|hashpw|check_password|generate_password",
        "middleware": r"AuthenticationMiddleware|AuthorizationMiddleware",
    },
    "quality": {
        "long_functions": r"def\s+\w+.*:[\s\S]{100,}",
        "nested_loops": r"for\s+.*:\s*for\s+.*:\s*for\s+",
        "bare_except": r"except\s*:\s*(?:pass|#|$)",
    },
}


def analyze_file(
    filepath: str,
    focus: Optional[str] = None,
    severity: str = "all",
    format: str = "json",
) -> List[Dict[str, Any]]:
    """Analyze a single file for patterns.

    Args:
        filepath: Path to file
        focus: Analysis focus (security, database, http, auth, quality)
        severity: Minimum severity to report (critical, high, medium, low, all)
        format: Output format

    Returns:
        List of findings
    """
    results = []

    if focus and focus in FOCUS_PATTERNS:
        patterns = FOCUS_PATTERNS[focus]
        for pattern_name, pattern in patterns.items():
            findings = run_analysis(pattern, filepath, format)
            for finding in findings:
                finding["pattern_type"] = pattern_name
                finding["focus"] = focus
                results.append(finding)
    else:
        # Run all focuses
        for focus_name, patterns in FOCUS_PATTERNS.items():
            for pattern_name, pattern in patterns.items():
                findings = run_analysis(pattern, filepath, format)
                for finding in findings:
                    finding["pattern_type"] = pattern_name
                    finding["focus"] = focus_name
                    results.append(finding)

    # Filter by severity if needed
    if severity != "all":
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        min_severity = severity_order.get(severity, 0)
        results = [
            r for r in results
            if severity_order.get(r.get("severity", "low"), 0) >= min_severity
        ]

    return results


def analyze_directory(
    dirpath: str,
    focus: Optional[str] = None,
    severity: str = "all",
    format: str = "json",
    recursive: bool = True,
) -> List[Dict[str, Any]]:
    """Analyze all files in a directory.

    Args:
        dirpath: Path to directory
        focus: Analysis focus (security, database, http, auth, quality)
        severity: Minimum severity to report
        format: Output format
        recursive: Search recursively

    Returns:
        List of findings
    """
    results = []

    if focus and focus in FOCUS_PATTERNS:
        patterns = FOCUS_PATTERNS[focus]
        for pattern_name, pattern in patterns.items():
            cmd_result = run_comby_command(
                pattern=pattern,
                path=dirpath,
                format=format,
            )
            findings = parse_json_output(cmd_result.stdout) if format == "json" else []
            for finding in findings:
                finding["pattern_type"] = pattern_name
                finding["focus"] = focus
                results.append(finding)
    else:
        # Run all focuses
        for focus_name, patterns in FOCUS_PATTERNS.items():
            for pattern_name, pattern in patterns.items():
                cmd_result = run_comby_command(
                    pattern=pattern,
                    path=dirpath,
                    format=format,
                )
                findings = parse_json_output(cmd_result.stdout) if format == "json" else []
                for finding in findings:
                    finding["pattern_type"] = pattern_name
                    finding["focus"] = focus_name
                    results.append(finding)

    # Filter by severity
    if severity != "all":
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        min_severity = severity_order.get(severity, 0)
        results = [
            r for r in results
            if severity_order.get(r.get("severity", "low"), 0) >= min_severity
        ]

    return results


def run_analysis(pattern: str, path: str, format: str) -> List[Dict[str, Any]]:
    """Run analysis with a pattern.

    Args:
        pattern: Regex pattern
        path: Path to analyze
        format: Output format

    Returns:
        List of findings
    """
    cmd_result = run_comby_command(
        pattern=pattern,
        path=path,
        format=format,
    )

    if format == "json":
        return parse_json_output(cmd_result.stdout)

    return []


def check_security(
    path: str,
    severity: str = "all",
    format: str = "json",
) -> List[Dict[str, Any]]:
    """Run security analysis on path.

    Args:
        path: Path to analyze
        severity: Minimum severity
        format: Output format

    Returns:
        List of security findings
    """
    return analyze_directory(path, focus="security", severity=severity, format=format)


def check_quality(
    path: str,
    severity: str = "all",
    format: str = "json",
) -> List[Dict[str, Any]]:
    """Run quality analysis on path.

    Args:
        path: Path to analyze
        severity: Minimum severity
        format: Output format

    Returns:
        List of quality findings
    """
    return analyze_directory(path, focus="quality", severity=severity, format=format)


def generate_report(
    results: List[Dict[str, Any]],
    format: str = "json",
) -> str:
    """Generate analysis report.

    Args:
        results: List of findings
        format: Output format (json, default)

    Returns:
        Formatted report
    """
    if format == "json":
        return json.dumps(results, indent=2)

    if not results:
        return "No issues found."

    # Group by focus
    by_focus = {}
    for result in results:
        focus = result.get("focus", "unknown")
        if focus not in by_focus:
            by_focus[focus] = []
        by_focus[focus].append(result)

    lines = ["Analysis Report", "=" * 50]

    for focus, findings in by_focus.items():
        lines.append(f"\n{focus.upper()} ({len(findings)} issues)")
        lines.append("-" * 30)
        for finding in findings:
            file_path = finding.get("file", "unknown")
            line = finding.get("line", "?")
            pattern = finding.get("pattern_type", "?")
            lines.append(f"  {file_path}:{line} - {pattern}")

    return "\n".join(lines)

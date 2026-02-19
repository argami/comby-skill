"""Utility functions for Comby Skill plugin."""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


def run_comby_command(
    pattern: str,
    path: str = ".",
    format: str = "default",
    include: Optional[str] = None,
    exclude: Optional[str] = None,
    context: int = 0,
    case_insensitive: bool = False,
) -> subprocess.CompletedProcess:
    """Execute comby-skill CLI command.

    Args:
        pattern: Regex pattern to search for
        path: Root path to search in
        format: Output format (default, json, csv, lines, count)
        include: File patterns to include
        exclude: File patterns to exclude
        context: Number of context lines
        case_insensitive: Case insensitive search

    Returns:
        CompletedProcess with command output
    """
    cmd = ["comby-skill", "search", pattern, path, "--format", format]

    if include:
        cmd.extend(["--include", include])
    if exclude:
        cmd.extend(["--exclude", exclude])
    if context > 0:
        cmd.extend(["--context", str(context)])
    if case_insensitive:
        cmd.append("--case-insensitive")

    return subprocess.run(cmd, capture_output=True, text=True)


def parse_json_output(json_str: str) -> List[Dict[str, Any]]:
    """Parse JSON output from comby-skill.

    Args:
        json_str: JSON string from comby-skill CLI

    Returns:
        List of result dictionaries
    """
    try:
        data = json.loads(json_str)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "results" in data:
            return data["results"]
        return [data]
    except json.JSONDecodeError:
        return []


def format_results(
    results: List[Dict[str, Any]],
    format: str = "default"
) -> str:
    """Format search results for Claude display.

    Args:
        results: List of result dictionaries
        format: Output format (default, json, csv, lines)

    Returns:
        Formatted string
    """
    if format == "json":
        return json.dumps(results, indent=2)

    if not results:
        return "No results found."

    output_lines = []
    for result in results:
        if format == "default":
            file_path = result.get("file", "unknown")
            line = result.get("line", "?")
            text = result.get("text", "")
            output_lines.append(f"{file_path}:{line}: {text}")
        elif format == "lines":
            text = result.get("text", "")
            output_lines.append(text)
        elif format == "csv":
            file_path = result.get("file", "")
            line = result.get("line", "")
            text = result.get("text", "")
            output_lines.append(f"{file_path},{line},{text}")

    return "\n".join(output_lines)


def validate_pattern(pattern: str) -> Dict[str, Any]:
    """Validate a regex pattern.

    Args:
        pattern: Regex pattern to validate

    Returns:
        Dictionary with validation result
    """
    try:
        re.compile(pattern)
        return {
            "valid": True,
            "pattern": pattern,
            "error": None
        }
    except re.error as e:
        return {
            "valid": False,
            "pattern": pattern,
            "error": str(e)
        }


def get_file_info(path: str) -> Dict[str, Any]:
    """Get file metadata.

    Args:
        path: File path

    Returns:
        Dictionary with file metadata
    """
    p = Path(path)

    if not p.exists():
        return {
            "exists": False,
            "path": path
        }

    stat = p.stat()

    return {
        "exists": True,
        "path": str(p.absolute()),
        "name": p.name,
        "extension": p.suffix,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "is_file": p.is_file(),
        "is_dir": p.is_dir(),
    }


def get_language_from_extension(path: str) -> Optional[str]:
    """Detect programming language from file extension.

    Args:
        path: File path

    Returns:
        Language name or None
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
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
    }

    ext = Path(path).suffix.lower()
    return ext_map.get(ext)


def build_search_command(
    pattern: str,
    path: str = ".",
    **kwargs
) -> List[str]:
    """Build comby-skill search command arguments.

    Args:
        pattern: Regex pattern to search for
        path: Root path to search in
        **kwargs: Additional command options

    Returns:
        List of command arguments
    """
    cmd = ["comby-skill", "search", pattern, path]

    option_map = {
        "format": "--format",
        "include": "--include",
        "exclude": "--exclude",
        "context": "--context",
        "case_insensitive": "--case-insensitive",
    }

    for key, flag in option_map.items():
        if key in kwargs and kwargs[key]:
            value = kwargs[key]
            if key == "case_insensitive" and value:
                cmd.append(flag)
            elif value:
                cmd.extend([flag, str(value)])

    return cmd

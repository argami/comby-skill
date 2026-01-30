"""Command-line interface for Comby Skill."""

import argparse
import sys
from pathlib import Path
from typing import List

from comby_skill.pattern_matcher import PatternMatcher


def main(args: List[str] = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        prog='comby-skill',
        description='Detect code vulnerabilities and patterns using pattern matching'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Analyze subcommand
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze a file for vulnerabilities and patterns'
    )
    analyze_parser.add_argument(
        'filepath',
        type=str,
        help='Path to the Python file to analyze'
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.command == 'analyze':
        return analyze(parsed_args.filepath)
    else:
        parser.print_help()
        return 1


def analyze(filepath: str) -> int:
    """Analyze a file for vulnerabilities.

    Args:
        filepath: Path to the file to analyze

    Returns:
        Exit code (0 if successful, 1 if file not found or error)
    """
    file_path = Path(filepath)

    if not file_path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return 1

    if not file_path.is_file():
        print(f"Error: Not a file: {filepath}", file=sys.stderr)
        return 1

    # Read the file
    try:
        code = file_path.read_text()
    except Exception as e:
        print(f"Error: Could not read file: {e}", file=sys.stderr)
        return 1

    # Detect patterns
    matcher = PatternMatcher()
    sql_matches = matcher.detect_sql_injection(code)
    type_hints_matches = matcher.detect_missing_type_hints(code)

    all_matches = sql_matches + type_hints_matches

    if not all_matches:
        print(f"No vulnerabilities detected in {filepath}")
        return 0

    # Print results
    print(f"Found {len(all_matches)} issue(s) in {filepath}:\n")

    for match in all_matches:
        severity_symbol = '🔴' if match['severity'] == 'CRITICAL' else '🟡'
        print(f"{severity_symbol} {match['pattern']} ({match['severity']})")
        print(f"   Line {match['line_number']}: {match['code']}")
        print()

    return 0


if __name__ == '__main__':
    sys.exit(main())

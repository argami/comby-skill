"""Command-line interface for Comby Skill."""

import argparse
import sys
import time
from pathlib import Path
from typing import List

from comby_skill.pattern_matcher import PatternMatcher
from comby_skill.search_engine import SearchEngine, OutputFormatter


def main(args: List[str] = None) -> int:
    """Main entry point for the CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = argparse.ArgumentParser(
        prog='comby-skill',
        description='Comby Skill: Code search and pattern detection'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search subcommand (primary grep-like interface)
    search_parser = subparsers.add_parser(
        'search',
        help='Search for patterns in files (grep-like interface)'
    )
    search_parser.add_argument(
        'pattern',
        type=str,
        help='Regex pattern to search for'
    )
    search_parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Root path to search (default: current directory)'
    )
    search_parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        default=True,
        help='Recursively search subdirectories (default: true)'
    )
    search_parser.add_argument(
        '-i', '--case-insensitive',
        action='store_true',
        help='Case-insensitive search'
    )
    search_parser.add_argument(
        '--include',
        type=str,
        default='*',
        help='File glob pattern to include (default: *)'
    )
    search_parser.add_argument(
        '--exclude',
        type=str,
        help='File glob pattern to exclude'
    )
    search_parser.add_argument(
        '-f', '--format',
        choices=['default', 'json', 'csv', 'lines', 'count'],
        default='default',
        help='Output format (default: default)'
    )
    search_parser.add_argument(
        '-C', '--context',
        type=int,
        default=0,
        metavar='NUM',
        help='Lines of context before/after match (default: 0)'
    )
    search_parser.add_argument(
        '-m', '--max-results',
        type=int,
        default=100,
        metavar='NUM',
        help='Maximum results to return (default: 100)'
    )
    search_parser.add_argument(
        '-c', '--count',
        action='store_true',
        help='Count matches instead of listing them'
    )

    # Analyze subcommand (legacy pattern detection)
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze a file for vulnerabilities and patterns'
    )
    analyze_parser.add_argument(
        'filepath',
        type=str,
        help='Path to the Python file to analyze'
    )
    analyze_parser.add_argument(
        '--focus',
        type=str,
        choices=['security', 'database', 'http', 'auth', 'quality', 'all'],
        default='all',
        help='Focus area for analysis (default: all)'
    )
    analyze_parser.add_argument(
        '--severity',
        type=str,
        choices=['critical', 'high', 'medium', 'low', 'all'],
        default='all',
        help='Filter by severity level (default: all)'
    )
    analyze_parser.add_argument(
        '--category',
        type=str,
        help='Filter by category (e.g., sql_injection, xss)'
    )

    # List patterns subcommand
    list_parser = subparsers.add_parser(
        'list-patterns',
        help='List available pattern families'
    )
    list_parser.add_argument(
        '--category',
        type=str,
        help='Filter by category (security, code, quality, api, database)'
    )
    list_parser.add_argument(
        '--format',
        choices=['default', 'json'],
        default='default',
        help='Output format (default: default)'
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.command == 'search':
        return search(parsed_args)
    elif parsed_args.command == 'analyze':
        return analyze(parsed_args)
    elif parsed_args.command == 'list-patterns':
        return list_patterns(parsed_args)
    else:
        parser.print_help()
        return 1


def analyze(args) -> int:
    """Analyze a file for vulnerabilities.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 if successful, 1 if file not found or error)
    """
    filepath = args.filepath
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

    # Get focus and filters
    focus = getattr(args, 'focus', 'all')
    severity_filter = getattr(args, 'severity', 'all')
    category_filter = getattr(args, 'category', None)

    # Run pattern families based on focus
    all_matches = []

    if focus in ('all', 'security'):
        sql_matches = matcher.detect_sql_injection(code)
        all_matches.extend(sql_matches)

    if focus in ('all', 'quality'):
        type_hints_matches = matcher.detect_missing_type_hints(code)
        all_matches.extend(type_hints_matches)

    # Run additional pattern families if available
    if focus == 'all' or focus == 'database':
        db_results = matcher.run_family('database_access', filepath)
        if db_results:
            all_matches.extend(db_results)

    if focus == 'all' or focus == 'http':
        http_results = matcher.run_family('http_endpoints', filepath)
        if http_results:
            all_matches.extend(http_results)

    if focus == 'all' or focus == 'auth':
        auth_results = matcher.run_family('auth_boundaries', filepath)
        if auth_results:
            all_matches.extend(auth_results)

    if focus == 'all' or focus == 'security':
        ext_results = matcher.run_family('external_deps', filepath)
        if ext_results:
            all_matches.extend(ext_results)

    # Filter by severity
    if severity_filter != 'all':
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        min_level = severity_order.get(severity_filter, 0)
        all_matches = [
            m for m in all_matches
            if severity_order.get(m.get('severity', '').lower(), 0) >= min_level
        ]

    # Filter by category
    if category_filter:
        all_matches = [
            m for m in all_matches
            if category_filter in m.get('pattern', '').lower()
        ]

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


def search(args) -> int:
    """Search for patterns in files (grep-like interface).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for errors)
    """
    pattern = args.pattern
    path = args.path

    # Validate path exists
    search_path = Path(path)
    if not search_path.exists():
        print(f"Error: Path not found: {path}", file=sys.stderr)
        return 1

    # Create search engine
    try:
        engine = SearchEngine(pattern, case_insensitive=args.case_insensitive)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Execute search
    start_time = time.time()
    try:
        results = engine.search(
            root_path=path,
            recursive=args.recursive,
            include_pattern=args.include,
            exclude_pattern=args.exclude,
            context_lines=args.context,
            max_results=args.max_results,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    elapsed_time_ms = (time.time() - start_time) * 1000

    # Format output
    if args.count:
        output = str(len(results))
    else:
        if args.format == 'default':
            output = OutputFormatter.format_default(results, elapsed_time_ms)
        elif args.format == 'json':
            output = OutputFormatter.format_json(results, elapsed_time_ms)
        elif args.format == 'csv':
            output = OutputFormatter.format_csv(results)
        elif args.format == 'lines':
            output = OutputFormatter.format_lines(results)
        elif args.format == 'count':
            output = OutputFormatter.format_count(results)
        else:
            output = OutputFormatter.format_default(results, elapsed_time_ms)

    print(output)
    return 0


def list_patterns(args) -> int:
    """List available pattern families.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success)
    """
    matcher = PatternMatcher()

    families = matcher.list_available_families()

    if args.category:
        families = matcher.get_patterns_by_category(args.category)

    if args.format == 'json':
        import json
        print(json.dumps({"families": families, "count": len(families)}, indent=2))
    else:
        print("Available Pattern Families:")
        print("=" * 40)
        for family in families:
            print(f"  - {family}")
        print()
        print(f"Total: {len(families)} families")

    return 0


if __name__ == '__main__':
    sys.exit(main())

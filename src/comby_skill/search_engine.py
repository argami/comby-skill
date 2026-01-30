"""Search engine for grep-like pattern matching across files and directories."""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import csv
from io import StringIO


class SearchResult:
    """Represents a single search result match."""

    def __init__(
        self,
        file_path: Path,
        line_number: int,
        column_number: int,
        matched_text: str,
        context_before: Optional[List[str]] = None,
        context_after: Optional[List[str]] = None,
    ):
        """Initialize a search result."""
        self.file_path = file_path
        self.line_number = line_number
        self.column_number = column_number
        self.matched_text = matched_text
        self.context_before = context_before or []
        self.context_after = context_after or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'file': str(self.file_path),
            'line': self.line_number,
            'column': self.column_number,
            'text': self.matched_text,
            'context_before': self.context_before,
            'context_after': self.context_after,
        }


class SearchEngine:
    """Search engine for finding patterns in files and directories."""

    def __init__(self, pattern: str, case_insensitive: bool = False):
        """Initialize search engine with a regex pattern.

        Args:
            pattern: Regex pattern to search for
            case_insensitive: Whether to perform case-insensitive search

        Raises:
            ValueError: If the regex pattern is invalid
        """
        flags = re.IGNORECASE if case_insensitive else 0
        try:
            self.pattern = re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

        self.case_insensitive = case_insensitive

    def search(
        self,
        root_path: str = ".",
        recursive: bool = True,
        include_pattern: str = "*",
        exclude_pattern: Optional[str] = None,
        context_lines: int = 0,
        max_results: int = 100,
    ) -> List[SearchResult]:
        """Search for pattern in files.

        Args:
            root_path: Root directory to search (default: current directory)
            recursive: Whether to search recursively (default: True)
            include_pattern: File glob pattern to include (default: "*")
            exclude_pattern: File glob pattern to exclude (default: None)
            context_lines: Number of lines to include before/after match (default: 0)
            max_results: Maximum number of results to return (default: 100)

        Returns:
            List of SearchResult objects

        Raises:
            ValueError: If root_path doesn't exist
        """
        root = Path(root_path)
        if not root.exists():
            raise ValueError(f"Path does not exist: {root_path}")

        results = []
        results_count = 0

        # Determine search pattern
        if recursive:
            glob_pattern = f"**/{include_pattern}"
        else:
            glob_pattern = include_pattern

        # Search files
        for file_path in root.glob(glob_pattern):
            if results_count >= max_results:
                break

            if not file_path.is_file():
                continue

            # Check exclude pattern
            if exclude_pattern and file_path.match(exclude_pattern):
                continue

            # Search within file
            try:
                file_results = self._search_file(
                    file_path,
                    context_lines=context_lines,
                    max_results=max_results - results_count,
                )
                results.extend(file_results)
                results_count += len(file_results)
            except (UnicodeDecodeError, IOError):
                # Skip files that can't be read
                continue

        return results

    def _search_file(
        self,
        file_path: Path,
        context_lines: int = 0,
        max_results: int = 100,
    ) -> List[SearchResult]:
        """Search for pattern within a single file.

        Args:
            file_path: Path to the file to search
            context_lines: Number of lines to include before/after match
            max_results: Maximum number of results from this file

        Returns:
            List of SearchResult objects from this file
        """
        results = []

        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, IOError):
            return []

        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            if len(results) >= max_results:
                break

            # Find all matches in this line
            for match in self.pattern.finditer(line):
                if len(results) >= max_results:
                    break

                matched_text = match.group()
                column_number = match.start() + 1  # 1-indexed

                # Get context lines
                context_before = []
                context_after = []

                if context_lines > 0:
                    start_context = max(0, line_num - 1 - context_lines)
                    end_context = min(len(lines), line_num + context_lines)

                    context_before = [
                        lines[i].rstrip() for i in range(start_context, line_num - 1)
                    ]
                    context_after = [
                        lines[i].rstrip() for i in range(line_num, end_context)
                    ]

                result = SearchResult(
                    file_path=file_path,
                    line_number=line_num,
                    column_number=column_number,
                    matched_text=matched_text,
                    context_before=context_before,
                    context_after=context_after,
                )
                results.append(result)

        return results

    def count_matches(
        self,
        root_path: str = ".",
        recursive: bool = True,
        include_pattern: str = "*",
        exclude_pattern: Optional[str] = None,
    ) -> int:
        """Count total matches across all files.

        Args:
            root_path: Root directory to search
            recursive: Whether to search recursively
            include_pattern: File glob pattern to include
            exclude_pattern: File glob pattern to exclude

        Returns:
            Total number of matches
        """
        results = self.search(
            root_path=root_path,
            recursive=recursive,
            include_pattern=include_pattern,
            exclude_pattern=exclude_pattern,
            max_results=float('inf'),  # type: ignore
        )
        return len(results)


class OutputFormatter:
    """Formats search results in different output formats."""

    @staticmethod
    def format_default(results: List[SearchResult], total_time_ms: float = 0) -> str:
        """Format results in human-readable default format.

        Args:
            results: List of search results
            total_time_ms: Execution time in milliseconds

        Returns:
            Formatted output string
        """
        lines = []
        files_with_matches = len(set(r.file_path for r in results))

        for result in results:
            line = f"{result.file_path}:{result.line_number}: {result.matched_text}"
            lines.append(line)

        # Add summary
        if lines:
            lines.append("---")
            lines.append(
                f"Total: {len(results)} match{'es' if len(results) != 1 else ''} "
                f"in {files_with_matches} file{'s' if files_with_matches != 1 else ''}"
            )
            if total_time_ms > 0:
                lines.append(f"Time: {total_time_ms:.0f}ms")

        return "\n".join(lines)

    @staticmethod
    def format_json(results: List[SearchResult], total_time_ms: float = 0) -> str:
        """Format results as JSON.

        Args:
            results: List of search results
            total_time_ms: Execution time in milliseconds

        Returns:
            JSON formatted string
        """
        files_with_matches = len(set(r.file_path for r in results))

        output = {
            'matches': [r.to_dict() for r in results],
            'total_matches': len(results),
            'files_with_matches': files_with_matches,
            'execution_time_ms': int(total_time_ms),
        }

        return json.dumps(output, indent=2)

    @staticmethod
    def format_csv(results: List[SearchResult]) -> str:
        """Format results as CSV.

        Args:
            results: List of search results

        Returns:
            CSV formatted string
        """
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=['file', 'line', 'column', 'text'],
        )

        writer.writeheader()
        for result in results:
            writer.writerow({
                'file': str(result.file_path),
                'line': result.line_number,
                'column': result.column_number,
                'text': result.matched_text,
            })

        return output.getvalue().rstrip()

    @staticmethod
    def format_lines(results: List[SearchResult]) -> str:
        """Format results as lines (one result per line).

        Args:
            results: List of search results

        Returns:
            Line-formatted string
        """
        lines = [
            f"{result.file_path}:{result.line_number}: {result.matched_text}"
            for result in results
        ]
        return "\n".join(lines)

    @staticmethod
    def format_count(results: List[SearchResult]) -> str:
        """Format as count only.

        Args:
            results: List of search results

        Returns:
            Count as string
        """
        return str(len(results))

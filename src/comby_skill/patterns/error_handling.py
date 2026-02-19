"""
Error Handling Pattern Family

Analyzes error handling patterns including:
- Try/catch blocks
- Exception handling
- Error logging
- Fallback patterns
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ErrorHandlingPattern(Enum):
    """Types of error handling patterns."""
    TRY_CATCH = "try_catch"
    TRY_EXCEPT = "try_except"
    EXCEPTION_SWALLOW = "exception_swallow"
    BARE_EXCEPT = "bare_except"
    ERROR_LOGGING = "error_logging"
    FALLBACK = "fallback"
    RETRY = "retry"
    ERROR_DECORATOR = "error_decorator"


@dataclass
class ErrorHandler:
    """Represents an error handling block."""
    file_path: str
    line_number: int
    pattern: ErrorHandlingPattern
    error_type: Optional[str] = None
    has_logging: bool = False
    has_retry: bool = False
    is_swallowed: bool = False
    context: Optional[str] = None


class ErrorHandlingPatterns:
    """Pattern definitions for error handling detection."""

    # Try-catch patterns
    TRY_CATCH_PATTERNS = {
        "python": [
            r'try:',
            r'except\s+(\w+)\s*:',
            r'except\s+(\w+)\s+as\s+\w+:',
        ],
        "javascript": [
            r'try\s*\{',
            r'catch\s*\(',
            r'catch\s*\([^)]*\)\s*\{',
        ],
    }

    # Bare except (bad practice)
    BARE_EXCEPT_PATTERNS = {
        "python": [
            r'except\s*:',
            r'except\s+Exception\s*:',
            r'except\s+BaseException\s*:',
        ],
        "javascript": [
            r'catch\s*\(\s*\)\s*\{',  # catch() with no variable
        ],
    }

    # Logging patterns
    LOGGING_PATTERNS = {
        "python": [
            r'log\.(error|warning|exception|critical)',
            r'logging\.(error|warning|exception|critical)',
            r'logger\.(error|warning|exception|critical)',
            r'print\s*\(.*traceback',
            r'pprint\s*\(.*traceback',
        ],
        "javascript": [
            r'console\.(error|warn)',
            r'logger\.error\(',
            r'log\.error\(',
            r'winston\.error\(',
            r'pino\.error\(',
        ],
    }

    # Fallback patterns
    FALLBACK_PATTERNS = {
        "python": [
            r'if\s+.*:\s*return.*else\s+return',
            r'try:.*except:.*else:',
            r'except.*:\s*return.*finally:',
        ],
        "javascript": [
            r'try\s*{.*}\s*catch.*{\s*return',
            r'if\s*\(.*\)\s*\{.*\}\s*else\s*\{.*\}',
            r'if\s*\(.+\)\s*\?.*:.*',
        ],
    }

    # Retry patterns
    RETRY_PATTERNS = {
        "python": [
            r'retry',
            r'for\s+.*in\s+range\(.*attempts',
            r'@retry',
            r'tenacity',
            r'backoff',
        ],
        "javascript": [
            r'retry',
            r'for\s*\(\s*let\s+\w+\s*=\s*0.*attempts',
            r'\.retry\(',
            r'p-retry',
        ],
    }


def detect_error_handling(
    file_path: str,
    language: str,
    code_content: str,
) -> List[ErrorHandler]:
    """Detect error handling patterns in code.

    Args:
        file_path: Path to the file
        language: Programming language
        code_content: Source code

    Returns:
        List of detected error handlers
    """
    import re

    results = []

    # Find try blocks
    for pattern in ErrorHandlingPatterns.TRY_CATCH_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1

            # Extract error type if present
            error_type = None
            if match.groups():
                error_type = match.group(1)

            # Check for logging
            has_logging = check_for_logging(code_content, line_num, language)

            # Check for retry
            has_retry = check_for_retry(code_content, line_num, language)

            # Check if swallowed
            is_swallowed = check_if_swallowed(code_content, line_num, language)

            results.append(ErrorHandler(
                file_path=file_path,
                line_number=line_num,
                pattern=ErrorHandlingPattern.TRY_CATCH,
                error_type=error_type,
                has_logging=has_logging,
                has_retry=has_retry,
                is_swallowed=is_swallowed,
                context=match.group(0),
            ))

    # Find bare excepts (bad practice)
    for pattern in ErrorHandlingPatterns.BARE_EXCEPT_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1

            results.append(ErrorHandler(
                file_path=file_path,
                line_number=line_num,
                pattern=ErrorHandlingPattern.BARE_EXCEPT,
                is_swallowed=True,
                context=match.group(0),
            ))

    # Find error logging
    for pattern in ErrorHandlingPatterns.LOGGING_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1

            results.append(ErrorHandler(
                file_path=file_path,
                line_number=line_num,
                pattern=ErrorHandlingPattern.ERROR_LOGGING,
                has_logging=True,
                context=match.group(0),
            ))

    # Find retry patterns
    for pattern in ErrorHandlingPatterns.RETRY_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1

            results.append(ErrorHandler(
                file_path=file_path,
                line_number=line_num,
                pattern=ErrorHandlingPattern.RETRY,
                has_retry=True,
                context=match.group(0),
            ))

    # Find fallback patterns
    for pattern in ErrorHandlingPatterns.FALLBACK_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1

            results.append(ErrorHandler(
                file_path=file_path,
                line_number=line_num,
                pattern=ErrorHandlingPattern.FALLBACK,
                context=match.group(0)[:100],
            ))

    return results


def check_for_logging(
    code_content: str,
    line_num: int,
    language: str,
) -> bool:
    """Check if error handling has logging.

    Args:
        code_content: Source code
        line_num: Line number of error handler
        language: Programming language

    Returns:
        True if logging is present
    """
    import re

    lines = code_content.split('\n')
    context = '\n'.join(lines[max(0, line_num-1):min(len(lines), line_num+10)])

    patterns = ErrorHandlingPatterns.LOGGING_PATTERNS.get(language, [])

    return any(re.search(p, context, re.IGNORECASE) for p in patterns)


def check_for_retry(
    code_content: str,
    line_num: int,
    language: str,
) -> bool:
    """Check if error handling has retry logic.

    Args:
        code_content: Source code
        line_num: Line number of error handler
        language: Programming language

    Returns:
        True if retry is present
    """
    import re

    lines = code_content.split('\n')
    context = '\n'.join(lines[max(0, line_num-1):min(len(lines), line_num+10)])

    patterns = ErrorHandlingPatterns.RETRY_PATTERNS.get(language, [])

    return any(re.search(p, context, re.IGNORECASE) for p in patterns)


def check_if_swallowed(
    code_content: str,
    line_num: int,
    language: str,
) -> bool:
    """Check if exception is swallowed (no logging, no re-raise).

    Args:
        code_content: Source code
        line_num: Line number of exception
        language: Programming language

    Returns:
        True if exception is swallowed
    """
    lines = code_content.split('\n')
    context_lines = lines[max(0, line_num-1):min(len(lines), line_num+5)]
    context = '\n'.join(context_lines)

    # Check for bare except
    if 'except:' in context or 'catch()' in context:
        return True

    # Check for pass or empty handler
    if 'pass' in context or 'catch' in context:
        # Check if there's actual handling after
        handler_lines = [l.strip() for l in context_lines if l.strip() and not l.strip().startswith(('try', 'except', 'catch'))]
        return len(handler_lines) <= 1

    return False


def classify_error_handling(handlers: List[ErrorHandler]) -> Dict[str, Any]:
    """Classify error handling patterns.

    Args:
        handlers: List of detected error handlers

    Returns:
        Classification summary
    """
    classification = {
        "total_handlers": len(handlers),
        "by_pattern": {},
        "with_logging": 0,
        "with_retry": 0,
        "swallowed_count": 0,
        "issues": [],
    }

    for handler in handlers:
        # Count by pattern
        pattern = handler.pattern.value
        classification["by_pattern"][pattern] = \
            classification["by_pattern"].get(pattern, 0) + 1

        # Count with logging
        if handler.has_logging:
            classification["with_logging"] += 1

        # Count with retry
        if handler.has_retry:
            classification["with_retry"] += 1

        # Count swallowed
        if handler.is_swallowed:
            classification["swallowed_count"] += 1
            classification["issues"].append(
                f"Swallowed exception at {handler.file_path}:{handler.line_number}"
            )

    # Check for bare except
    bare_except_count = classification["by_pattern"].get("bare_except", 0)
    if bare_except_count > 0:
        classification["issues"].append(
            f"Found {bare_except_count} bare except clause(s) - should catch specific exceptions"
        )

    # Check logging coverage
    if len(handlers) > 0:
        logging_ratio = classification["with_logging"] / len(handlers)
        if logging_ratio < 0.5:
            classification["issues"].append(
                f"Only {logging_ratio:.0%} of exceptions are logged"
            )

    # Determine quality level
    if classification["swallowed_count"] > 0:
        classification["quality"] = "needs_improvement"
    elif logging_ratio < 0.5:
        classification["quality"] = "acceptable"
    else:
        classification["quality"] = "good"

    return classification

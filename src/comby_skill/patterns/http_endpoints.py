"""
HTTP Endpoints Pattern Family

Detects and classifies HTTP endpoint definitions including:
- Route decorators
- HTTP methods
- Request handlers
- API specifications
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"
    OPTIONS = "options"
    HEAD = "head"


@dataclass
class HTTPEndpoint:
    """Represents an HTTP endpoint definition."""
    file_path: str
    line_number: int
    method: HTTPMethod
    path: str
    framework: str
    handler_name: Optional[str] = None
    middleware: List[str] = None
    is_async: bool = False

    def __post_init__(self):
        if self.middleware is None:
            self.middleware = []


class HTTPEndpointPatterns:
    """Pattern definitions for HTTP endpoint detection."""

    # Framework-specific patterns
    FRAMEWORK_PATTERNS = {
        "flask": [
            (r"@app\.route\(['\"]([^'\"]+)['\"]", "GET"),
            (r"@app\.route\(['\"]([^'\"]+)['\"].*method\s*=\s*\[[^\]]*'GET'", "GET"),
            (r"@app\.route\(['\"]([^'\"]+)['\"].*method\s*=\s*\[[^\]]*'POST'", "POST"),
            (r"@app\.route\(['\"]([^'\"]+)['\"].*method\s*=\s*\[[^\]]*'PUT'", "PUT"),
            (r"@app\.route\(['\"]([^'\"]+)['\"].*method\s*=\s*\[[^\]]*'DELETE'", "DELETE"),
            (r"@app\.get\(['\"]([^'\"]+)['\"]\)", "GET"),
            (r"@app\.post\(['\"]([^'\"]+)['\"]\)", "POST"),
            (r"@app\.put\(['\"]([^'\"]+)['\"]\)", "PUT"),
            (r"@app\.delete\(['\"]([^'\"]+)['\"]\)", "DELETE"),
            (r"@app\.patch\(['\"]([^'\"]+)['\"]\)", "PATCH"),
        ],
        "fastapi": [
            (r"@(app|router)\.get\(['\"]([^'\"]+)['\"]\)", "GET"),
            (r"@(app|router)\.post\(['\"]([^'\"]+)['\"]\)", "POST"),
            (r"@(app|router)\.put\(['\"]([^'\"]+)['\"]\)", "PUT"),
            (r"@(app|router)\.delete\(['\"]([^'\"]+)['\"]\)", "DELETE"),
            (r"@(app|router)\.patch\(['\"]([^'\"]+)['\"]\)", "PATCH"),
            (r"@(app|router)\.options\(['\"]([^'\"]+)['\"]\)", "OPTIONS"),
        ],
        "django": [
            (r"path\(['\"]([^'\"]+)['\"].*,\s*(\w+)", "GET"),
            (r"re_path\(['\"]([^'\"]+)['\"].*,\s*(\w+)", "GET"),
            (r"@login_required.*def\s+(\w+)", None),
        ],
        "express": [
            (r"app\.(get|post|put|delete|patch|options)\s*\(\s*['\"]([^'\"]+)['\"]", None),
            (r"router\.(get|post|put|delete|patch|options)\s*\(\s*['\"]([^'\"]+)['\"]", None),
            (r"app\.all\s*\(\s*['\"]([^'\"]+)['\"]", None),
        ],
        "koa": [
            (r"router\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]", None),
            (r"app\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]", None),
        ],
        "go": [
            (r"http\.(Handle|HandleFunc)\s*\(['\"]([^'\"]+)['\"]", None),
            (r"router\.(GET|POST|PUT|DELETE|PATCH)\s*\(['\"]([^'\"]+)['\"]", None),
            (r"@router\.(get|post|put|delete|patch)\s*\(['\"]([^'\"]+)['\"]", None),
        ],
    }

    # Middleware patterns
    MIDDLEWARE_PATTERNS = {
        "python": [
            r"@middleware\.register",
            r"@app\.middleware",
            r"@router\.middleware",
            r"def\s+\w+\s*\([^)]*request[^)]*\):.*#.*middleware",
        ],
        "javascript": [
            r"app\.use\(",
            r"router\.use\(",
            r"\.use\s*\(",
        ],
    }


def detect_http_endpoints(
    file_path: str,
    language: str,
    code_content: str,
    framework: Optional[str] = None,
) -> List[HTTPEndpoint]:
    """Detect HTTP endpoint definitions in code.

    Args:
        file_path: Path to the file being analyzed
        language: Programming language
        code_content: Source code content
        framework: Optional framework hint

    Returns:
        List of detected HTTP endpoints
    """
    import re
    results = []

    # Determine framework
    if not framework:
        framework = detect_framework(code_content)

    if framework not in HTTPEndpointPatterns.FRAMEWORK_PATTERNS:
        return results

    # Find endpoints
    for pattern, default_method in HTTPEndpointPatterns.FRAMEWORK_PATTERNS[framework]:
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1

            # Extract path
            path = match.group(1) if len(match.groups()) >= 1 else "/"

            # Determine method
            method_str = default_method
            if method_str is None:
                # Try to extract from pattern match
                full_match = match.group(0).lower()
                for m in HTTPMethod:
                    if m.value in full_match:
                        method_str = m.value
                        break

            if method_str is None:
                method_str = "GET"

            # Check for async
            is_async = "async" in code_content[max(0, match.start()-50):match.start()]

            results.append(HTTPEndpoint(
                file_path=file_path,
                line_number=line_num,
                method=HTTPMethod(method_str.lower()),
                path=path,
                framework=framework,
                is_async=is_async,
            ))

    # Find middleware
    for endpoint in results:
        endpoint.middleware = detect_middleware(code_content, endpoint.line_number)

    return results


def detect_framework(code_content: str) -> Optional[str]:
    """Detect web framework from code content.

    Args:
        code_content: Source code content

    Returns:
        Framework name or None
    """
    import re

    # Check for framework indicators
    if re.search(r"from\s+flask\s+import|import\s+flask", code_content):
        return "flask"
    if re.search(r"from\s+fastapi\s+import|import\s+fastapi", code_content):
        return "fastapi"
    if re.search(r"from\s+express\s+import|const\s+express\s*=", code_content):
        return "express"
    if re.search(r"from\s+django|import\s+django", code_content):
        return "django"
    if re.search(r"from\s+koa|import\s+koa", code_content):
        return "koa"
    if re.search(r'"koa"|\'koa\'', code_content):
        return "koa"
    if re.search(r'import\s+"net/http"|import\s+\'net/http\'', code_content):
        return "go"

    return None


def detect_middleware(code_content: str, endpoint_line: int) -> List[str]:
    """Detect middleware for an endpoint.

    Args:
        code_content: Source code content
        endpoint_line: Line number of endpoint

    Returns:
        List of middleware names
    """
    import re
    middleware = []

    lines = code_content.split('\n')

    # Look for middleware before the endpoint
    for i, line in enumerate(lines):
        if i >= endpoint_line - 1:
            break

        # Check for middleware patterns
        if re.search(r'\.use\s*\(', line):
            match = re.search(r'\.use\s*\(\s*([^,\s)]+)', line)
            if match:
                middleware.append(match.group(1))

        if re.search(r'@app\.middleware|@router\.middleware', line):
            match = re.search(r'@app\.middleware|@router\.middleware', line)
            if match:
                middleware.append("app_middleware")

    return middleware


def classify_endpoints(endpoints: List[HTTPEndpoint]) -> Dict[str, Any]:
    """Classify HTTP endpoint patterns.

    Args:
        endpoints: List of detected endpoints

    Returns:
        Classification summary
    """
    classification = {
        "total_endpoints": len(endpoints),
        "endpoints_by_method": {},
        "endpoints_by_framework": {},
        "async_count": 0,
        "with_middleware": 0,
        "restfulness": {
            "compliant": 0,
            "issues": [],
        },
    }

    for endpoint in endpoints:
        # Count by method
        method = endpoint.method.value
        classification["endpoints_by_method"][method] = \
            classification["endpoints_by_method"].get(method, 0) + 1

        # Count by framework
        fw = endpoint.framework
        classification["endpoints_by_framework"][fw] = \
            classification["endpoints_by_framework"].get(fw, 0) + 1

        # Async count
        if endpoint.is_async:
            classification["async_count"] += 1

        # Middleware count
        if endpoint.middleware:
            classification["with_middleware"] += 1

        # REST compliance
        if classify_as_restful(endpoint):
            classification["restfulness"]["compliant"] += 1
        else:
            classification["restfulness"]["issues"].append(
                f"{endpoint.path} uses {endpoint.method.value}"
            )

    return classification


def classify_as_restful(endpoint: HTTPEndpoint) -> bool:
    """Check if endpoint follows RESTful conventions.

    Args:
        endpoint: HTTP endpoint

    Returns:
        True if RESTful
    """
    # Simple heuristic for REST compliance
    path = endpoint.path.lower()
    method = endpoint.method.value

    # Check for action-based (non-RESTful) patterns
    non_restful = ['/add', '/edit', '/delete', '/update', '/create']

    for pattern in non_restful:
        if pattern in path:
            return False

    return True

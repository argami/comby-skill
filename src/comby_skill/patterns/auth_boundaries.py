"""
Authentication and Authorization Boundaries Pattern Family

Detects and classifies:
- Authentication decorators
- Authorization checks
- Permission handling
- JWT/OAuth implementations
- Password handling
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class AuthType(Enum):
    """Types of authentication/authorization patterns."""
    DECORATOR = "decorator"
    MIDDLEWARE = "middleware"
    PERMISSION_CHECK = "permission_check"
    JWT_HANDLER = "jwt_handler"
    OAUTH_HANDLER = "oauth_handler"
    PASSWORD_HANDLER = "password_handler"
    SESSION_HANDLER = "session_handler"
    API_KEY_HANDLER = "api_key_handler"


@dataclass
class AuthBoundary:
    """Represents an authentication/authorization boundary."""
    file_path: str
    line_number: int
    auth_type: AuthType
    name: str
    context: str
    is_secure: bool = True
    issues: List[str] = None

    def __post_init__(self):
        if self.issues is None:
            self.issues = []


class AuthPatterns:
    """Pattern definitions for authentication/authorization detection."""

    # Authentication decorators
    AUTH_DECORATORS = {
        "python": [
            r"@login_required",
            r"@auth_required",
            r"@requires_auth",
            r"@authenticated",
            r"@jwt_required",
            r"@token_required",
            r"@api_key_required",
            r"@permission_required\(['\"]([^'\"]+)['\"]",
            r"@require_roles?\([^)]+\)",
        ],
        "javascript": [
            r"@login_required",
            r"@auth",
            r"@secured",
            r"@authorize\(",
            r"function\s+.*authenticate",
            r"const\s+.*auth.*=\s*.*requireAuth",
        ],
    }

    # Middleware patterns
    AUTH_MIDDLEWARE = {
        "python": [
            r"Middleware\s*\(\s*['\"]auth['\"]",
            r"@app\.middleware\(['\"]auth['\"]\)",
        ],
        "javascript": [
            r"express\.authentication\(",
            r"app\.use\([^)]*auth[^)]*\)",
            r"router\.use\([^)]*auth[^)]*\)",
        ],
    }

    # JWT patterns
    JWT_PATTERNS = {
        "python": [
            r"jwt\.decode\(",
            r"jwt\.encode\(",
            r"pyjwt\.decode\(",
            r"pyjwt\.encode\(",
            r"JWT\(\)",
            r"create_access_token\(",
            r"create_refresh_token\(",
        ],
        "javascript": [
            r"jwt\.verify\(",
            r"jwt\.sign\(",
            r"jsonwebtoken\.verify\(",
            r"jsonwebtoken\.sign\(",
            r"await\s+jwt\.",
        ],
    }

    # OAuth patterns
    OAUTH_PATTERNS = {
        "python": [
            r"@.*oauth\.",
            r"OAuth2\(",
            r"Auth2Session\(",
        ],
        "javascript": [
            r"passport\.",
            r"OAuth2Strategy",
            r"google\.oauth2",
            r"github\.auth",
        ],
    }

    # Password handling patterns
    PASSWORD_PATTERNS = {
        "python": [
            r"bcrypt\.hashpw\(",
            r"bcrypt\.gensalt\(",
            r"hashlib\.sha256.*password",
            r"generate_password_hash\(",
            r"check_password_hash\(",
            r"pwd_context\.hash\(",
            r"verify_password\(",
        ],
        "javascript": [
            r"bcrypt\.hash\(",
            r"bcrypt\.compare\(",
            r"bcryptjs\.hash\(",
            r"bcryptjs\.compare\(",
            r"argon2\.hash\(",
            r"argon2\.verify\(",
        ],
    }

    # Permission check patterns
    PERMISSION_PATTERNS = {
        "python": [
            r"is_admin\(",
            r"has_permission\(",
            r"check_permission\(",
            r"can_access\(",
            r"authorize\(",
            r"\.groups\.filter\(",
            r"user\.has_perm\(",
            r"@permission_required",
        ],
        "javascript": [
            r"isAdmin\(",
            r"hasPermission\(",
            r"checkPermission\(",
            r"canAccess\(",
            r"authorize\(",
        ],
    }

    # Insecure patterns (red flags)
    INSECURE_PATTERNS = {
        "python": [
            r"if\s+user\.is_authenticated\s*:.*pass",  # Weak auth check
            r"password\s*==\s*['\"][^'\"]+['\"]",  # Plaintext comparison
            r"eval\s*\(\s*request",  # Code injection
            r"exec\s*\(\s*request",  # Code injection
            r"\.authenticate\(.*password.*\)",  # In custom auth
        ],
        "javascript": [
            r"if\s*\(.*password.*===.*\)",  # Plaintext comparison
            r"localStorage\.setItem.*token",  # Storing tokens in localStorage
            r"document\.cookie\s*=.*token",  # Insecure cookie
        ],
    }


def detect_auth_boundaries(
    file_path: str,
    language: str,
    code_content: str,
) -> List[AuthBoundary]:
    """Detect authentication/authorization boundaries in code.

    Args:
        file_path: Path to the file being analyzed
        language: Programming language
        code_content: Source code content

    Returns:
        List of detected auth boundaries
    """
    import re
    results = []

    # Check decorators
    for pattern in AuthPatterns.AUTH_DECORATORS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1
            results.append(AuthBoundary(
                file_path=file_path,
                line_number=line_num,
                auth_type=AuthType.DECORATOR,
                name=match.group(0)[:50],
                context=match.group(0),
            ))

    # Check middleware
    for pattern in AuthPatterns.AUTH_MIDDLEWARE.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1
            results.append(AuthBoundary(
                file_path=file_path,
                line_number=line_num,
                auth_type=AuthType.MIDDLEWARE,
                name="auth_middleware",
                context=match.group(0),
            ))

    # Check JWT
    for pattern in AuthPatterns.JWT_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1
            results.append(AuthBoundary(
                file_path=file_path,
                line_number=line_num,
                auth_type=AuthType.JWT_HANDLER,
                name="jwt_handler",
                context=match.group(0),
            ))

    # Check OAuth
    for pattern in AuthPatterns.OAUTH_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1
            results.append(AuthBoundary(
                file_path=file_path,
                line_number=line_num,
                auth_type=AuthType.OAUTH_HANDLER,
                name="oauth_handler",
                context=match.group(0),
            ))

    # Check password handling
    for pattern in AuthPatterns.PASSWORD_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1

            # Check if secure (uses proper hashing)
            is_secure = 'bcrypt' in match.group(0).lower() or \
                       'argon2' in match.group(0).lower() or \
                       'hashpw' in match.group(0).lower()

            results.append(AuthBoundary(
                file_path=file_path,
                line_number=line_num,
                auth_type=AuthType.PASSWORD_HANDLER,
                name="password_handler",
                context=match.group(0),
                is_secure=is_secure,
            ))

    # Check permissions
    for pattern in AuthPatterns.PERMISSION_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1
            results.append(AuthBoundary(
                file_path=file_path,
                line_number=line_num,
                auth_type=AuthType.PERMISSION_CHECK,
                name=match.group(0)[:30],
                context=match.group(0),
            ))

    # Check for insecure patterns
    for boundary in results:
        boundary.issues = check_insecure_patterns(language, code_content, boundary.line_number)

    return results


def check_insecure_patterns(
    language: str,
    code_content: str,
    line_number: int,
) -> List[str]:
    """Check for insecure patterns near a line.

    Args:
        language: Programming language
        code_content: Source code content
        line_number: Line number to check

    Returns:
        List of security issues
    """
    import re
    issues = []

    lines = code_content.split('\n')

    if line_number > len(lines):
        return issues

    context = '\n'.join(lines[max(0, line_number-3):min(len(lines), line_number+2)])

    for pattern in AuthPatterns.INSECURE_PATTERNS.get(language, []):
        if re.search(pattern, context, re.IGNORECASE):
            issues.append(f"Potential security issue: {pattern}")

    return issues


def classify_auth_usage(results: List[AuthBoundary]) -> Dict[str, Any]:
    """Classify authentication/authorization patterns.

    Args:
        results: List of detected auth boundaries

    Returns:
        Classification summary
    """
    classification = {
        "total_auth_points": len(results),
        "by_type": {},
        "secure_count": 0,
        "insecure_count": 0,
        "security_issues": [],
    }

    for result in results:
        # Count by type
        auth_type = result.auth_type.value
        classification["by_type"][auth_type] = \
            classification["by_type"].get(auth_type, 0) + 1

        # Track security
        if result.is_secure:
            classification["secure_count"] += 1
        else:
            classification["insecure_count"] += 1

        # Collect issues
        if result.issues:
            classification["security_issues"].extend(result.issues)

    # Overall security assessment
    if classification["insecure_count"] > 0:
        classification["security_level"] = "needs_review"
    elif classification["secure_count"] > 0:
        classification["security_level"] = "good"
    else:
        classification["security_level"] = "no_auth"

    return classification

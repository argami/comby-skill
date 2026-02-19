"""
Pattern families for Comby Skill.
"""

from .database_access import (
    DatabaseAccess,
    DatabaseOperationType,
    DatabaseAccessPatterns,
    detect_database_access,
    classify_database_usage,
)

from .http_endpoints import (
    HTTPEndpoint,
    HTTPMethod,
    HTTPEndpointPatterns,
    detect_http_endpoints,
    classify_endpoints,
)

from .auth_boundaries import (
    AuthBoundary,
    AuthType,
    AuthPatterns,
    detect_auth_boundaries,
    classify_auth_usage,
)

from .external_deps import (
    ExternalDependency,
    ExternalServiceType,
    ExternalDependencyPatterns,
    detect_external_dependencies,
    classify_external_dependencies,
)

from .complexity import (
    ComplexityMetric,
    ComplexityThresholds,
    analyze_complexity,
    classify_complexity,
)

from .duplication import (
    DuplicateBlock,
    DuplicationReport,
    analyze_duplication,
    suggest_refactoring,
)

from .error_handling import (
    ErrorHandler,
    ErrorHandlingPattern,
    ErrorHandlingPatterns,
    detect_error_handling,
    classify_error_handling,
)

__all__ = [
    # Database
    "DatabaseAccess",
    "DatabaseOperationType",
    "detect_database_access",
    "classify_database_usage",

    # HTTP
    "HTTPEndpoint",
    "HTTPMethod",
    "detect_http_endpoints",
    "classify_endpoints",

    # Auth
    "AuthBoundary",
    "AuthType",
    "detect_auth_boundaries",
    "classify_auth_usage",

    # External
    "ExternalDependency",
    "ExternalServiceType",
    "detect_external_dependencies",
    "classify_external_dependencies",

    # Complexity
    "ComplexityMetric",
    "analyze_complexity",
    "classify_complexity",

    # Duplication
    "DuplicateBlock",
    "DuplicationReport",
    "analyze_duplication",
    "suggest_refactoring",

    # Error Handling
    "ErrorHandler",
    "ErrorHandlingPattern",
    "detect_error_handling",
    "classify_error_handling",
]

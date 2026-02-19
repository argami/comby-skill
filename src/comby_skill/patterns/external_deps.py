"""
External Dependencies Pattern Family

Detects and classifies external service calls including:
- HTTP client usage
- Third-party API calls
- Cloud service integrations
- External service patterns
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ExternalServiceType(Enum):
    """Types of external service integrations."""
    HTTP_CLIENT = "http_client"
    AWS_SERVICE = "aws_service"
    CLOUD_STORAGE = "cloud_storage"
    PAYMENT_GATEWAY = "payment_gateway"
    EMAIL_SERVICE = "email_service"
    ANALYTICS = "analytics"
    SOCIAL_API = "social_api"
    MAPS_API = "maps_api"
    AI_SERVICE = "ai_service"
    GENERIC_API = "generic_api"


@dataclass
class ExternalDependency:
    """Represents an external service dependency."""
    file_path: str
    line_number: int
    service_type: ExternalServiceType
    service_name: str
    call_type: str  # GET, POST, etc.
    endpoint: Optional[str] = None
    has_retry: bool = False
    has_error_handling: bool = False
    is_async: bool = False
    context: Optional[str] = None


class ExternalDependencyPatterns:
    """Pattern definitions for external dependency detection."""

    # HTTP client patterns
    HTTP_CLIENT_PATTERNS = {
        "python": [
            r"requests\.(get|post|put|delete|patch)\(",
            r"httpx\.(get|post|put|delete|patch)\(",
            r"aiohttp\.(ClientSession|request)\(",
            r"urllib\.(request|urlopen)",
            r"http\.client\.",
            r"urllib3\.(PoolManager|connectionpool)",
        ],
        "javascript": [
            r"fetch\(",
            r"axios\.(get|post|put|delete|patch)\(",
            r"http\.(get|post|put|delete)\(",
            r"node-fetch",
            r"superagent\.(get|post|put|delete)\(",
        ],
    }

    # AWS service patterns
    AWS_PATTERNS = [
        r"boto3\.",
        r"aws-sdk\.",
        r"@aws-sdk",
        r"import\s+{[^}]*(S3|DynamoDB|Lambda|SQS|SNS|EC2)[^}]*}",
        r"from\s+'@aws-sdk",
    ]

    # Cloud storage patterns
    CLOUD_STORAGE_PATTERNS = [
        r"gcloud\.storage",
        r"@google-cloud",
        r"azure\.storage",
        r"@azure/",
        r"cloudinary\.",
        r"uploadcare",
    ]

    # Payment gateway patterns
    PAYMENT_PATTERNS = [
        r"stripe\.",
        r"@stripe",
        r"paypal",
        r"braintree",
        r"square\.",
        r"adyen",
    ]

    # Email service patterns
    EMAIL_PATTERNS = [
        r"sendgrid",
        r"mailgun",
        r"ses\.",
        r"@sendgrid",
        r"@mailgun",
        r"nodemailer",
        r"postmark",
    ]

    # Analytics patterns
    ANALYTICS_PATTERNS = [
        r"mixpanel",
        r"segment\.",
        r"@segment",
        r"amplitude",
        r"google-analytics",
        r"ga\(",
        r"hotjar",
        r"intercom",
    ]

    # Social API patterns
    SOCIAL_PATTERNS = [
        r"twitter\.api",
        r"facebook\.api",
        r"instagram\.api",
        r"github\.com",
        r"slack\.com",
        r"discord\.com",
    ]

    # Maps API patterns
    MAPS_PATTERNS = [
        r"google\.maps",
        r"mapbox",
        r"leaflet",
        r"openlayers",
        r"@google-maps",
    ]

    # AI service patterns
    AI_PATTERNS = [
        r"openai\.",
        r"@openai",
        r"anthropic\.",
        r"@anthropic",
        r"cohere\.",
        r"huggingface",
        r"replicate",
        r"azure\.openai",
    ]

    # Retry patterns
    RETRY_PATTERNS = [
        r"retry",
        r"tenacity",
        r"backoff",
        r"@retry",
        r"max_attempts",
    ]

    # Error handling patterns
    ERROR_HANDLING_PATTERNS = [
        r"try:",
        r"except",
        r"catch\s*\(",
        r"\.catch\(",
        r"onerror",
    ]


def detect_external_dependencies(
    file_path: str,
    language: str,
    code_content: str,
) -> List[ExternalDependency]:
    """Detect external service dependencies in code.

    Args:
        file_path: Path to the file being analyzed
        language: Programming language
        code_content: Source code content

    Returns:
        List of detected external dependencies
    """
    import re
    results = []

    # Detect service type from imports/requires
    service_types = detect_service_types(code_content)

    # Find HTTP client calls
    for pattern in ExternalDependencyPatterns.HTTP_CLIENT_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1

            # Determine call type
            call_type = "UNKNOWN"
            call_match = re.search(r'\.(get|post|put|delete|patch|request)\(', match.group(0), re.IGNORECASE)
            if call_match:
                call_type = call_match.group(1).upper()

            # Check for retry
            has_retry = bool(re.search('|'.join(ExternalDependencyPatterns.RETRY_PATTERNS),
                                       code_content[max(0, match.start()-200):match.start()]))

            # Check for error handling
            has_error = bool(re.search('|'.join(ExternalDependencyPatterns.ERROR_HANDLING_PATTERNS),
                                       code_content[max(0, match.start()-100):match.start()]))

            # Check for async
            is_async = "async" in code_content[max(0, match.start()-50):match.start()]

            # Extract endpoint if possible
            endpoint = extract_endpoint(match.group(0))

            # Determine service type
            service_type = ExternalServiceType.HTTP_CLIENT
            service_name = "HTTP"

            if service_types:
                for st, name in service_types.items():
                    service_type = st
                    service_name = name
                    break

            results.append(ExternalDependency(
                file_path=file_path,
                line_number=line_num,
                service_type=service_type,
                service_name=service_name,
                call_type=call_type,
                endpoint=endpoint,
                has_retry=has_retry,
                has_error_handling=has_error,
                is_async=is_async,
                context=match.group(0)[:100],
            ))

    return results


def detect_service_types(code_content: str) -> Dict[ExternalServiceType, str]:
    """Detect which external services are used.

    Args:
        code_content: Source code content

    Returns:
        Dictionary of service types found
    """
    import re
    services = {}

    # AWS
    if any(re.search(p, code_content, re.IGNORECASE) for p in ExternalDependencyPatterns.AWS_PATTERNS):
        services[ExternalServiceType.AWS_SERVICE] = "AWS"

    # Cloud Storage
    if any(re.search(p, code_content, re.IGNORECASE) for p in ExternalDependencyPatterns.CLOUD_STORAGE_PATTERNS):
        services[ExternalServiceType.CLOUD_STORAGE] = "Cloud Storage"

    # Payment
    if any(re.search(p, code_content, re.IGNORECASE) for p in ExternalDependencyPatterns.PAYMENT_PATTERNS):
        services[ExternalServiceType.PAYMENT_GATEWAY] = "Payment"

    # Email
    if any(re.search(p, code_content, re.IGNORECASE) for p in ExternalDependencyPatterns.EMAIL_PATTERNS):
        services[ExternalServiceType.EMAIL_SERVICE] = "Email"

    # Analytics
    if any(re.search(p, code_content, re.IGNORECASE) for p in ExternalDependencyPatterns.ANALYTICS_PATTERNS):
        services[ExternalServiceType.ANALYTICS] = "Analytics"

    # Social
    if any(re.search(p, code_content, re.IGNORECASE) for p in ExternalDependencyPatterns.SOCIAL_PATTERNS):
        services[ExternalServiceType.SOCIAL_API] = "Social"

    # Maps
    if any(re.search(p, code_content, re.IGNORECASE) for p in ExternalDependencyPatterns.MAPS_PATTERNS):
        services[ExternalServiceType.MAPS_API] = "Maps"

    # AI
    if any(re.search(p, code_content, re.IGNORECASE) for p in ExternalDependencyPatterns.AI_PATTERNS):
        services[ExternalServiceType.AI_SERVICE] = "AI"

    return services


def extract_endpoint(call: str) -> Optional[str]:
    """Extract endpoint from HTTP call.

    Args:
        call: HTTP call string

    Returns:
        Extracted endpoint or None
    """
    import re
    # Try to find URL in quotes
    match = re.search(r'["\']([^"\']+)["\']', call)
    if match:
        url = match.group(1)
        if url.startswith('http'):
            # Extract path from URL
            path_match = re.search(r'https?://[^/]+(/.*)', url)
            if path_match:
                return path_match.group(1)
        return url[:50]
    return None


def classify_external_dependencies(deps: List[ExternalDependency]) -> Dict[str, Any]:
    """Classify external dependency patterns.

    Args:
        deps: List of detected dependencies

    Returns:
        Classification summary
    """
    classification = {
        "total_calls": len(deps),
        "calls_by_service": {},
        "calls_by_type": {},
        "async_count": 0,
        "with_retry": 0,
        "with_error_handling": 0,
        "missing_retry": [],
        "missing_error_handling": [],
    }

    for dep in deps:
        # Count by service
        service = dep.service_name
        classification["calls_by_service"][service] = \
            classification["calls_by_service"].get(service, 0) + 1

        # Count by type
        call_type = dep.call_type
        classification["calls_by_type"][call_type] = \
            classification["calls_by_type"].get(call_type, 0) + 1

        # Async count
        if dep.is_async:
            classification["async_count"] += 1

        # Retry handling
        if dep.has_retry:
            classification["with_retry"] += 1
        else:
            classification["missing_retry"].append(f"{dep.file_path}:{dep.line_number}")

        # Error handling
        if dep.has_error_handling:
            classification["with_error_handling"] += 1
        else:
            classification["missing_error_handling"].append(f"{dep.file_path}:{dep.line_number}")

    return classification

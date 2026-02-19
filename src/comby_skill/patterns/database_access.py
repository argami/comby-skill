"""
Database Access Pattern Family

Detects and classifies database operations including:
- Raw SQL execution
- ORM calls
- Migrations
- Transactions
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class DatabaseOperationType(Enum):
    """Types of database operations."""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    TRANSACTION = "transaction"
    RAW_SQL = "raw_sql"
    ORM_QUERY = "orm_query"


@dataclass
class DatabaseAccess:
    """Represents a database access pattern found in code."""
    file_path: str
    line_number: int
    operation_type: DatabaseOperationType
    table_name: Optional[str] = None
    query_text: Optional[str] = None
    is_orm: bool = False
    orm_framework: Optional[str] = None
    context: Optional[str] = None


class DatabaseAccessPatterns:
    """Pattern definitions for database access detection."""

    # Raw SQL patterns
    RAW_SQL_PATTERNS = {
        "python": [
            r"cursor\.execute\(['\"](SELECT|INSERT|UPDATE|DELETE).*?['\"]",
            r"\.execute\s*\(\s*['\"].*?(SELECT|insert|update|delete).*?['\"]",
            r"\.exec\(['\"].*?['\"]",
            r"\.query\(['\"].*?['\"]",
        ],
        "javascript": [
            r"await\s+.*\.execute\(['\"].*?(SELECT|INSERT|UPDATE|DELETE)",
            r"db\.query\(['\"].*?(SELECT|INSERT|UPDATE|DELETE)",
            r"pool\.query\(",
        ],
    }

    # ORM patterns by framework
    ORM_PATTERNS = {
        "django": [
            r"\.objects\.(filter|get|create|update|delete)",
            r"Model\.objects",
            r"\.save\(\)",
            r"\.filter\(",
        ],
        "sqlalchemy": [
            r"session\.query\(",
            r"\.filter\(",
            r"\.add\(",
            r"\.commit\(\)",
        ],
        "sqlmodel": [
            r"session\.select\(",
            r"\.filter\(",
        ],
        "prisma": [
            r"prisma\.\w+\.(findMany|findUnique|create|update|delete)",
        ],
        "typeorm": [
            r"repository\.(find|save|remove|delete)",
            r"manager\.(find|save|remove)",
        ],
    }

    # Transaction patterns
    TRANSACTION_PATTERNS = {
        "python": [
            r"begin\(\)",
            r"\.begin\(\)",
            r"connection\.begin\(\)",
            r"with\s+transaction",
        ],
        "javascript": [
            r"await\s+.*\.beginTransaction\(\)",
            r"pool\.begin\(",
        ],
    }


def detect_database_access(
    file_path: str,
    language: str,
    code_content: str,
) -> List[DatabaseAccess]:
    """Detect database access patterns in code.

    Args:
        file_path: Path to the file being analyzed
        language: Programming language
        code_content: Source code content

    Returns:
        List of detected database accesses
    """
    import re
    results = []

    # Check raw SQL patterns
    for pattern in DatabaseAccessPatterns.RAW_SQL_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1

            # Determine operation type
            op_type = DatabaseOperationType.RAW_SQL
            query = match.group(0).lower()
            if 'select' in query:
                op_type = DatabaseOperationType.SELECT
            elif 'insert' in query:
                op_type = DatabaseOperationType.INSERT
            elif 'update' in query:
                op_type = DatabaseOperationType.UPDATE
            elif 'delete' in query:
                op_type = DatabaseOperationType.DELETE

            results.append(DatabaseAccess(
                file_path=file_path,
                line_number=line_num,
                operation_type=op_type,
                query_text=match.group(0)[:100],
                is_orm=False,
            ))

    # Check ORM patterns
    for orm_framework, patterns in DatabaseAccessPatterns.ORM_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                line_num = code_content[:match.start()].count('\n') + 1

                # Determine operation type from context
                op_type = DatabaseOperationType.ORM_QUERY
                query = match.group(0).lower()
                if 'create' in query:
                    op_type = DatabaseOperationType.INSERT
                elif 'update' in query:
                    op_type = DatabaseOperationType.UPDATE
                elif 'delete' in query:
                    op_type = DatabaseOperationType.DELETE

                results.append(DatabaseAccess(
                    file_path=file_path,
                    line_number=line_num,
                    operation_type=op_type,
                    is_orm=True,
                    orm_framework=orm_framework,
                    context=match.group(0),
                ))

    # Check transaction patterns
    for pattern in DatabaseAccessPatterns.TRANSACTION_PATTERNS.get(language, []):
        matches = re.finditer(pattern, code_content, re.IGNORECASE)
        for match in matches:
            line_num = code_content[:match.start()].count('\n') + 1
            results.append(DatabaseAccess(
                file_path=file_path,
                line_number=line_num,
                operation_type=DatabaseOperationType.TRANSACTION,
                context=match.group(0),
            ))

    return results


def classify_database_usage(results: List[DatabaseAccess]) -> Dict[str, Any]:
    """Classify database usage patterns.

    Args:
        results: List of detected database accesses

    Returns:
        Classification summary
    """
    classification = {
        "total_operations": len(results),
        "operations_by_type": {},
        "orm_usage": {
            "uses_orm": False,
            "framework": None,
            "raw_sql_count": 0,
        },
        "transaction_count": 0,
        "risk_level": "low",
    }

    for result in results:
        # Count by type
        op_type = result.operation_type.value
        classification["operations_by_type"][op_type] = \
            classification["operations_by_type"].get(op_type, 0) + 1

        # Track ORM usage
        if result.is_orm:
            classification["orm_usage"]["uses_orm"] = True
            if result.orm_framework:
                classification["orm_usage"]["framework"] = result.orm_framework
        else:
            classification["orm_usage"]["raw_sql_count"] += 1

        # Count transactions
        if result.operation_type == DatabaseOperationType.TRANSACTION:
            classification["transaction_count"] += 1

    # Determine risk level
    if classification["orm_usage"]["raw_sql_count"] > 0:
        classification["risk_level"] = "medium"

    if classification["transaction_count"] == 0 and \
       classification["operations_by_type"].get("update", 0) > 0:
        classification["risk_level"] = "high"

    return classification

"""
Code Complexity Pattern Family

Analyzes code complexity metrics including:
- Cyclomatic complexity
- Function length
- Nesting depth
- Parameter count
- Cognitive complexity
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class ComplexityMetric:
    """Represents a complexity metric for a code element."""
    file_path: str
    line_number: int
    element_name: str
    element_type: str  # function, class, method
    cyclomatic_complexity: int
    lines_of_code: int
    nesting_depth: int
    parameter_count: int
    cognitive_complexity: int
    complexity_score: float


class ComplexityThresholds:
    """Thresholds for complexity ratings."""

    CYCLOMATIC = {
        "low": 10,
        "moderate": 20,
        "high": 30,
    }

    LINES_OF_CODE = {
        "function": {
            "low": 20,
            "moderate": 50,
            "high": 100,
        },
        "method": {
            "low": 20,
            "moderate": 40,
            "high": 80,
        },
    }

    NESTING_DEPTH = {
        "low": 3,
        "moderate": 4,
        "high": 5,
    }

    PARAMETER_COUNT = {
        "low": 3,
        "moderate": 5,
        "high": 7,
    }


def count_cyclomatic_complexity(code_block: str) -> int:
    """Calculate cyclomatic complexity.

    Args:
        code_block: Code to analyze

    Returns:
        Cyclomatic complexity value
    """
    import re

    # Base complexity
    complexity = 1

    # Count decision points
    decision_keywords = [
        r'\bif\b',
        r'\belif\b',
        r'\belse\b',
        r'\bfor\b',
        r'\bwhile\b',
        r'\bcatch\b',
        r'\band\b',
        r'\bor\b',
        r'\?.*:.*',  # Ternary operator
    ]

    for pattern in decision_keywords:
        complexity += len(re.findall(pattern, code_block, re.IGNORECASE))

    return complexity


def count_nesting_depth(code_block: str) -> int:
    """Calculate maximum nesting depth.

    Args:
        code_block: Code to analyze

    Returns:
        Maximum nesting depth
    """
    import re

    max_depth = 0
    current_depth = 0

    for char in code_block:
        if char == '{' or char == '(' or char == '[':
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif char == '}' or char == ')' or char == ']':
            current_depth = max(0, current_depth - 1)

    return max_depth


def count_parameters(func_def: str) -> int:
    """Count function parameters.

    Args:
        func_def: Function definition

    Returns:
        Number of parameters
    """
    import re

    # Find parameters in function definition
    # Python: def func(a, b, c)
    # JS: function func(a, b, c)
    # Go: func(a, b, c)
    # etc.

    patterns = [
        r'def\s+\w+\s*\(([^)]*)\)',
        r'function\s+\w+\s*\(([^)]*)\)',
        r'const\s+\w+\s*=\s*\(([^)]*)\)\s*=>',
        r'func\s+\w+\s*\(([^)]*)\)',
        r'fn\s+\w+\s*\(([^)]*)\)',
    ]

    for pattern in patterns:
        match = re.search(pattern, func_def)
        if match:
            params = match.group(1).strip()
            if not params:
                return 0
            # Split by comma, handling nested parentheses
            return len([p for p in params.split(',') if p.strip()])

    return 0


def calculate_cognitive_complexity(code_block: str) -> int:
    """Calculate cognitive complexity.

    Args:
        code_block: Code to analyze

    Returns:
        Cognitive complexity value
    """
    import re

    complexity = 0
    nesting_increment = 0

    lines = code_block.split('\n')

    for line in lines:
        stripped = line.strip()

        # Increment complexity for structures
        if any(kw in stripped for kw in ['if', 'elif', 'for', 'while', 'catch', 'case']):
            complexity += 1 + nesting_increment

        if stripped.startswith(('else', 'finally')):
            complexity += 1 + nesting_increment

        # Track nesting
        nesting_increment += line.count('{') - line.count('}')
        nesting_increment += line.count('(') - line.count(')')
        nesting_increment += line.count('[') - line.count(']')

        # Reset negative increments
        if nesting_increment < 0:
            nesting_increment = 0

    return complexity


def extract_function_blocks(code_content: str, language: str) -> List[tuple]:
    """Extract function/method blocks from code.

    Args:
        code_content: Source code
        language: Programming language

    Returns:
        List of (name, start_line, end_line, code_block) tuples
    """
    import re

    functions = []

    if language == "python":
        pattern = r'def\s+(\w+)\s*\(([^)]*)\):(.*?)(?=\ndef\s|\Z)'
    elif language in ("javascript", "typescript"):
        pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|(\w+)\s*\([^)]*\)\s*\{)(.*?)(?=\nfunction\s|\nconst\s|\n\w+\s*=\s*|\Z)'
    elif language == "go":
        pattern = r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(([^)]*)\)\s*\{(.*?)(?=\nfunc\s|\Z)'
    else:
        return functions

    matches = re.finditer(pattern, code_content, re.DOTALL)
    for match in matches:
        name = match.group(1) or match.group(2) or match.group(3)
        code_block = match.group(0)

        start_line = code_content[:match.start()].count('\n') + 1

        functions.append((name, start_line, code_block))

    return functions


def analyze_complexity(
    file_path: str,
    language: str,
    code_content: str,
) -> List[ComplexityMetric]:
    """Analyze code complexity.

    Args:
        file_path: Path to the file
        language: Programming language
        code_content: Source code

    Returns:
        List of complexity metrics
    """
    results = []

    functions = extract_function_blocks(code_content, language)

    for name, start_line, code_block in functions:
        cyclomatic = count_cyclomatic_complexity(code_block)
        nesting = count_nesting_depth(code_block)
        params = count_parameters(code_block)
        cognitive = calculate_cognitive_complexity(code_block)
        loc = len(code_block.split('\n'))

        # Calculate overall complexity score
        score = (cyclomatic * 1.0 + nesting * 2.0 +
                 (loc / 10) + cognitive * 0.5)

        results.append(ComplexityMetric(
            file_path=file_path,
            line_number=start_line,
            element_name=name,
            element_type="function",
            cyclomatic_complexity=cyclomatic,
            lines_of_code=loc,
            nesting_depth=nesting,
            parameter_count=params,
            cognitive_complexity=cognitive,
            complexity_score=round(score, 2),
        ))

    return results


def classify_complexity(metrics: List[ComplexityMetric]) -> Dict[str, Any]:
    """Classify complexity metrics.

    Args:
        metrics: List of complexity metrics

    Returns:
        Classification summary
    """
    classification = {
        "total_elements": len(metrics),
        "complexity_distribution": {
            "low": 0,
            "moderate": 0,
            "high": 0,
            "very_high": 0,
        },
        "average_complexity": 0,
        "max_complexity": 0,
        "max_complexity_element": None,
        "issues": [],
    }

    if not metrics:
        return classification

    total_score = 0

    for metric in metrics:
        score = metric.complexity_score
        total_score += score

        if score < 15:
            classification["complexity_distribution"]["low"] += 1
        elif score < 30:
            classification["complexity_distribution"]["moderate"] += 1
        elif score < 50:
            classification["complexity_distribution"]["high"] += 1
        else:
            classification["complexity_distribution"]["very_high"] += 1

        if score > classification["max_complexity"]:
            classification["max_complexity"] = score
            classification["max_complexity_element"] = {
                "name": metric.element_name,
                "file": metric.file_path,
                "line": metric.line_number,
            }

        # Collect specific issues
        if metric.nesting_depth > ComplexityThresholds.NESTING_DEPTH["high"]:
            classification["issues"].append(
                f"Deep nesting ({metric.nesting_depth}) in {metric.element_name}"
            )

        if metric.parameter_count > ComplexityThresholds.PARAMETER_COUNT["high"]:
            classification["issues"].append(
                f"Too many parameters ({metric.parameter_count}) in {metric.element_name}"
            )

    classification["average_complexity"] = round(total_score / len(metrics), 2)

    return classification

"""
Code Duplication Pattern Family

Detects and classifies code duplication including:
- Exact duplicates
- Similar blocks
- Copy-paste patterns
- Repeated logic
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Set
from collections import defaultdict


@dataclass
class DuplicateBlock:
    """Represents a duplicated code block."""
    file_path: str
    line_start: int
    line_end: int
    hash_value: str
    content: str
    clone_group: int  # Groups similar duplicates


@dataclass
class DuplicationReport:
    """Report of code duplication analysis."""
    total_duplicates: int
    duplicate_lines: int
    unique_blocks: int
    clone_groups: List[Dict[str, Any]]


def normalize_code(code: str) -> str:
    """Normalize code for comparison.

    Args:
        code: Code block

    Returns:
        Normalized code
    """
    import re

    # Remove comments
    lines = code.split('\n')
    normalized = []

    for line in lines:
        # Remove single-line comments
        line = re.sub(r'//.*$', '', line)
        line = re.sub(r'#.*$', '', line)

        # Remove strings (replace with placeholder)
        line = re.sub(r'"[^"]*"', '"__STR__"', line)
        line = re.sub(r"'[^']*'", "'__STR__'", line)

        # Normalize whitespace
        line = re.sub(r'\s+', ' ', line.strip())

        if line:
            normalized.append(line)

    return '\n'.join(normalized)


def calculate_hash(content: str, min_lines: int = 5) -> Optional[str]:
    """Calculate hash for code block.

    Args:
        content: Code content
        min_lines: Minimum lines to consider

    Returns:
        Hash string or None
    """
    import hashlib

    lines = content.strip().split('\n')

    if len(lines) < min_lines:
        return None

    normalized = normalize_code(content)
    return hashlib.md5(normalized.encode()).hexdigest()


def find_exact_duplicates(
    code_blocks: List[tuple],  # [(content, file_path, line_start, line_end)]
    min_lines: int = 5,
) -> List[DuplicateBlock]:
    """Find exact duplicate code blocks.

    Args:
        code_blocks: List of (content, file_path, line_start, line_end)
        min_lines: Minimum lines for detection

    Returns:
        List of duplicate blocks
    """
    import hashlib

    hash_map = defaultdict(list)
    duplicates = []

    for content, file_path, line_start, line_end in code_blocks:
        # Skip short blocks
        lines = content.strip().split('\n')
        if len(lines) < min_lines:
            continue

        # Calculate hash
        normalized = normalize_code(content)
        h = hashlib.md5(normalized.encode()).hexdigest()

        hash_map[h].append({
            'content': content,
            'file_path': file_path,
            'line_start': line_start,
            'line_end': line_end,
        })

    # Build duplicates
    group_id = 0
    for h, blocks in hash_map.items():
        if len(blocks) > 1:
            for block in blocks:
                duplicates.append(DuplicateBlock(
                    file_path=block['file_path'],
                    line_start=block['line_start'],
                    line_end=block['line_end'],
                    hash_value=h,
                    content=block['content'][:100],
                    clone_group=group_id,
                ))
            group_id += 1

    return duplicates


def extract_code_blocks(
    file_path: str,
    language: str,
    code_content: str,
    block_size: int = 10,
) -> List[tuple]:
    """Extract code blocks from file.

    Args:
        file_path: Path to file
        language: Programming language
        code_content: Source code
        block_size: Lines per block

    Returns:
        List of (content, file_path, line_start, line_end)
    """
    blocks = []

    lines = code_content.split('\n')
    total_lines = len(lines)

    for i in range(total_lines - block_size + 1):
        block = '\n'.join(lines[i:i + block_size])

        # Skip blocks that are mostly comments or strings
        normalized = normalize_code(block)
        if len(normalized) < block_size * 2:
            continue

        blocks.append((
            block,
            file_path,
            i + 1,  # 1-indexed
            i + block_size,
        ))

    return blocks


def find_similar_blocks(
    code_blocks: List[tuple],
    similarity_threshold: float = 0.8,
) -> List[tuple]:
    """Find similar (not identical) code blocks.

    Args:
        code_blocks: List of (content, file_path, line_start, line_end)
        similarity_threshold: Minimum similarity to consider

    Returns:
        List of similar block pairs
    """
    similar = []

    for i, (content1, path1, start1, end1) in enumerate(code_blocks):
        for j, (content2, path2, start2, end2) in enumerate(code_blocks[i+1:], i+1):
            # Calculate similarity
            similarity = calculate_similarity(content1, content2)

            if similarity >= similarity_threshold:
                similar.append((
                    (path1, start1, end1, similarity),
                    (path2, start2, end2, similarity),
                ))

    return similar


def calculate_similarity(code1: str, code2: str) -> float:
    """Calculate similarity between two code blocks.

    Args:
        code1: First code block
        code2: Second code block

    Returns:
        Similarity score (0-1)
    """
    # Simple token-based similarity
    tokens1 = set(normalize_code(code1).split())
    tokens2 = set(normalize_code(code2).split())

    if not tokens1 or not tokens2:
        return 0.0

    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)

    return intersection / union if union > 0 else 0.0


def analyze_duplication(
    files: Dict[str, tuple],  # {file_path: (language, content)}
    min_block_size: int = 5,
    similarity_threshold: float = 0.8,
) -> DuplicationReport:
    """Analyze code duplication across files.

    Args:
        files: Dictionary of file_path -> (language, content)
        min_block_size: Minimum lines per block
        similarity_threshold: Threshold for similar detection

    Returns:
        Duplication report
    """
    # Extract all code blocks
    all_blocks = []
    for file_path, (language, content) in files.items():
        blocks = extract_code_blocks(file_path, language, content, min_block_size)
        all_blocks.extend(blocks)

    # Find exact duplicates
    duplicates = find_exact_duplicates(all_blocks, min_block_size)

    # Calculate metrics
    unique_hashes = set(d.hash_value for d in duplicates)
    total_duplicate_lines = sum(d.line_end - d.line_start for d in duplicates)

    # Group duplicates
    clone_groups = defaultdict(list)
    for dup in duplicates:
        clone_groups[dup.clone_group].append({
            'file': dup.file_path,
            'lines': f"{dup.line_start}-{dup.line_end}",
        })

    return DuplicationReport(
        total_duplicates=len(duplicates),
        duplicate_lines=total_duplicate_lines,
        unique_blocks=len(unique_hashes),
        clone_groups=[
            {'group_id': gid, 'occurrences': blocks}
            for gid, blocks in clone_groups.items()
        ],
    )


def suggest_refactoring(duplicates: List[DuplicateBlock]) -> List[str]:
    """Suggest refactoring for duplicated code.

    Args:
        duplicates: List of duplicate blocks

    Returns:
        List of refactoring suggestions
    """
    suggestions = []

    # Group by clone group
    groups = defaultdict(list)
    for dup in duplicates:
        groups[dup.clone_group].append(dup)

    for group_id, blocks in groups.items():
        if len(blocks) < 2:
            continue

        files = list(set(b.file_path for b in blocks))
        lines = sum(b.line_end - b.line_start for b in blocks)

        if lines > 10:
            suggestions.append(
                f"Clone group {group_id}: {len(blocks)} occurrences across {len(files)} files. "
                f"Consider extracting to shared function ({lines} lines)"
            )

    return suggestions
